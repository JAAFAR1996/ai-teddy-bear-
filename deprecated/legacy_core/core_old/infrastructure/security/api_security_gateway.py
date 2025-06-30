"""
🔐 API Security Gateway - Rate Limiting & DDoS Protection
=========================================================

Author: Jaafar Adeeb - Security Lead
"""

import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import structlog

from fastapi import Request, HTTPException, status
from fastapi.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
import redis.asyncio as redis

logger = structlog.get_logger(__name__)


class ThreatLevel(Enum):
    """Threat level classification"""
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class RateLimitRule:
    """Rate limiting rule"""
    name: str
    requests: int
    window_seconds: int
    user_role: Optional[str] = None


class APISecurityGateway:
    """API Gateway with security features"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client
        self.blocked_ips: set = set()
        self.request_counts: Dict[str, deque] = defaultdict(lambda: deque())
        
        # Rate limit rules
        self.rate_limits = {
            'default': RateLimitRule("default", 100, 60),
            'parent': RateLimitRule("parent", 200, 60, "parent"),
            'child': RateLimitRule("child", 30, 60, "child"),
            'auth': RateLimitRule("auth", 5, 300),
            'audio': RateLimitRule("audio", 20, 60),
        }
        
        # DDoS thresholds
        self.ddos_threshold = 1000  # requests per minute
        self.ip_threshold = 100     # unique IPs per minute
    
    async def check_rate_limit(self, request: Request) -> Dict[str, Any]:
        """Check rate limits for request"""
        
        client_ip = self._get_client_ip(request)
        user_role = await self._get_user_role(request)
        endpoint = str(request.url.path)
        
        # Determine which rate limit rule to apply
        rule_key = self._get_rate_limit_rule(endpoint, user_role)
        rule = self.rate_limits[rule_key]
        
        # Create rate limit key
        limit_key = f"{rule_key}:{client_ip}"
        
        # Check rate limit
        is_allowed = await self._check_rate_limit_key(
            limit_key, rule.requests, rule.window_seconds
        )
        
        if not is_allowed:
            logger.warning("Rate limit exceeded", 
                         ip=client_ip, 
                         rule=rule.name,
                         endpoint=endpoint)
            
            return {
                'allowed': False,
                'retry_after': rule.window_seconds
            }
        
        return {'allowed': True}
    
    async def security_check(self, request: Request) -> Dict[str, Any]:
        """Comprehensive security check"""
        
        client_ip = self._get_client_ip(request)
        
        # Check blocked IPs
        if client_ip in self.blocked_ips:
            return {
                'allowed': False,
                'status_code': 403,
                'message': 'IP address blocked'
            }
        
        # DDoS detection
        if await self._detect_ddos():
            self.blocked_ips.add(client_ip)
            return {
                'allowed': False,
                'status_code': 429,
                'message': 'DDoS attack detected'
            }
        
        # Threat detection
        if await self._detect_threats(request):
            return {
                'allowed': False,
                'status_code': 403,
                'message': 'Security threat detected'
            }
        
        return {'allowed': True}
    
    async def _check_rate_limit_key(self, key: str, limit: int, window: int) -> bool:
        """Check rate limit for specific key"""
        
        if self.redis_client:
            return await self._redis_rate_limit(key, limit, window)
        else:
            return await self._memory_rate_limit(key, limit, window)
    
    async def _redis_rate_limit(self, key: str, limit: int, window: int) -> bool:
        """Redis-based rate limiting"""
        
        now = time.time()
        window_start = now - window
        
        # Remove expired entries
        await self.redis_client.zremrangebyscore(key, 0, window_start)
        
        # Count current requests
        current_count = await self.redis_client.zcard(key)
        
        if current_count >= limit:
            return False
        
        # Add current request
        await self.redis_client.zadd(key, {str(now): now})
        await self.redis_client.expire(key, window)
        
        return True
    
    async def _memory_rate_limit(self, key: str, limit: int, window: int) -> bool:
        """Memory-based rate limiting"""
        
        now = time.time()
        window_start = now - window
        
        # Clean expired requests
        while self.request_counts[key] and self.request_counts[key][0] < window_start:
            self.request_counts[key].popleft()
        
        if len(self.request_counts[key]) >= limit:
            return False
        
        self.request_counts[key].append(now)
        return True
    
    async def _detect_ddos(self) -> bool:
        """Simple DDoS detection"""
        
        # Count total requests in last minute
        now = time.time()
        total_requests = 0
        
        for ip_requests in self.request_counts.values():
            total_requests += len([r for r in ip_requests if r > now - 60])
        
        return total_requests > self.ddos_threshold
    
    async def _detect_threats(self, request: Request) -> bool:
        """Basic threat detection"""
        
        url_str = str(request.url).lower()
        user_agent = request.headers.get('user-agent', '').lower()
        
        # Simple patterns
        threat_patterns = [
            'union select', 'drop table', '<script', 'javascript:',
            'onload=', 'onerror=', '../', '/etc/passwd'
        ]
        
        for pattern in threat_patterns:
            if pattern in url_str or pattern in user_agent:
                logger.warning("Threat pattern detected", 
                             pattern=pattern,
                             url=url_str)
                return True
        
        return False
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        
        # Check forwarded headers
        forwarded = request.headers.get('x-forwarded-for')
        if forwarded:
            return forwarded.split(',')[0].strip()
        
        real_ip = request.headers.get('x-real-ip')
        if real_ip:
            return real_ip
        
        if hasattr(request, 'client') and request.client:
            return request.client.host
        
        return 'unknown'
    
    async def _get_user_role(self, request: Request) -> Optional[str]:
        """Extract user role from request"""
        
        # Simple role detection from path
        path = str(request.url.path)
        if '/parent/' in path:
            return 'parent'
        elif '/child/' in path:
            return 'child'
        
        return None
    
    def _get_rate_limit_rule(self, endpoint: str, user_role: Optional[str]) -> str:
        """Determine which rate limit rule to use"""
        
        if '/auth/' in endpoint or '/login' in endpoint:
            return 'auth'
        elif '/audio/' in endpoint:
            return 'audio'
        elif user_role in ['parent', 'child']:
            return user_role
        else:
            return 'default'
    
    def add_security_headers(self, response):
        """Add security headers to response"""
        
        headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000',
            'Content-Security-Policy': "default-src 'self'",
        }
        
        for header, value in headers.items():
            response.headers[header] = value
        
        return response


class SecurityMiddleware(BaseHTTPMiddleware):
    """FastAPI security middleware"""
    
    def __init__(self, app, gateway: APISecurityGateway):
        super().__init__(app)
        self.gateway = gateway
    
    async def dispatch(self, request: Request, call_next):
        """Process request through security gateway"""
        
        # Security check
        security_result = await self.gateway.security_check(request)
        if not security_result['allowed']:
            return JSONResponse(
                status_code=security_result.get('status_code', 403),
                content={'error': security_result.get('message', 'Access denied')}
            )
        
        # Rate limit check
        rate_limit_result = await self.gateway.check_rate_limit(request)
        if not rate_limit_result['allowed']:
            return JSONResponse(
                status_code=429,
                content={
                    'error': 'Rate limit exceeded',
                    'retry_after': rate_limit_result.get('retry_after', 60)
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Add security headers
        response = self.gateway.add_security_headers(response)
        
        return response


# Global instance
_security_gateway: Optional[APISecurityGateway] = None


def get_security_gateway(redis_client: Optional[redis.Redis] = None) -> APISecurityGateway:
    """Get global security gateway instance"""
    global _security_gateway
    if _security_gateway is None:
        _security_gateway = APISecurityGateway(redis_client)
    return _security_gateway 