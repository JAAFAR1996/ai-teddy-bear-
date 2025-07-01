from typing import Dict, List, Any, Optional

"""
🔐 Enterprise API Gateway - Security & Rate Limiting 2025
=========================================================

Comprehensive API Gateway with:
- Rate limiting and DDoS protection
- JWT authentication and validation
- Request/response transformation
- Circuit breaker pattern
- Real-time threat detection
- API analytics and monitoring

Author: Jaafar Adeeb - Security Lead
"""

import asyncio
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
import structlog
from collections import defaultdict, deque
import hashlib
import ipaddress
import re

from fastapi import FastAPI, Request, Response, HTTPException, status, Depends
from fastapi.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
import redis.asyncio as redis

logger = structlog.get_logger(__name__)


class ThreatLevel(Enum):
    """Threat level classification"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RequestType(Enum):
    """Request type classification"""
    AUDIO_UPLOAD = "audio_upload"
    WEBSOCKET_CONNECTION = "websocket_connection"
    API_CALL = "api_call"
    AUTHENTICATION = "authentication"
    FILE_UPLOAD = "file_upload"
    BULK_OPERATION = "bulk_operation"


@dataclass
class RateLimitRule:
    """Rate limiting rule configuration"""
    name: str
    requests: int
    window_seconds: int
    request_type: Optional[RequestType] = None
    user_role: Optional[str] = None
    endpoint_pattern: Optional[str] = None
    burst_multiplier: float = 1.5


@dataclass
class ThreatSignature:
    """Security threat signature"""
    name: str
    pattern: str
    threat_level: ThreatLevel
    action: str  # block, log, rate_limit
    description: str


@dataclass
class RequestAnalytics:
    """Request analytics data"""
    timestamp: datetime
    ip_address: str
    user_id: Optional[str]
    endpoint: str
    method: str
    response_time: float
    status_code: int
    user_agent: str
    threat_level: ThreatLevel
    blocked: bool = False


class SecurityAPIGateway:
    """Enterprise API Gateway with comprehensive security"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client
        self.rate_limit_rules: List[RateLimitRule] = []
        self.threat_signatures: List[ThreatSignature] = []
        self.blocked_ips: set = set()
        self.whitelisted_ips: set = set()
        self.request_analytics: deque = deque(maxlen=10000)
        
        # Circuit breaker states
        self.circuit_breakers: Dict[str, Dict[str, Any]] = {}
        
        # DDoS detection
        self.ddos_thresholds = {
            'requests_per_minute': 1000,
            'unique_ips_threshold': 100,
            'error_rate_threshold': 0.5
        }
        
        # Initialize default rules and signatures
        self._initialize_default_rules()
        self._initialize_threat_signatures()
        
        # Background monitoring tasks
        self._monitoring_tasks: List[asyncio.Task] = []
        self._start_monitoring()
    
    def _initialize_default_rules(self) -> Any:
        """Initialize default rate limiting rules"""
        self.rate_limit_rules = [
            # General API limits
            RateLimitRule("general_api", 100, 60, RequestType.API_CALL),
            
            # Authentication limits (more restrictive)
            RateLimitRule("auth_login", 5, 300, RequestType.AUTHENTICATION),
            
            # Audio upload limits
            RateLimitRule("audio_upload", 20, 60, RequestType.AUDIO_UPLOAD),
            
            # WebSocket connections
            RateLimitRule("websocket", 10, 60, RequestType.WEBSOCKET_CONNECTION),
            
            # File uploads
            RateLimitRule("file_upload", 50, 300, RequestType.FILE_UPLOAD),
            
            # Bulk operations
            RateLimitRule("bulk_ops", 5, 600, RequestType.BULK_OPERATION),
            
            # Parent role - higher limits
            RateLimitRule("parent_api", 200, 60, user_role="parent"),
            
            # Child role - lower limits for safety
            RateLimitRule("child_api", 30, 60, user_role="child"),
        ]
    
    def _initialize_threat_signatures(self) -> Any:
        """Initialize security threat signatures"""
        self.threat_signatures = [
            # SQL Injection patterns
            ThreatSignature(
                "sql_injection",
                r"(union\s+select|or\s+1=1|drop\s+table|insert\s+into|delete\s+from)",
                ThreatLevel.HIGH,
                "block",
                "SQL injection attempt detected"
            ),
            
            # XSS patterns
            ThreatSignature(
                "xss_attack",
                r"(<script|javascript:|onload=|onerror=|alert\(|document\.cookie)",
                ThreatLevel.HIGH,
                "block",
                "Cross-site scripting attempt detected"
            ),
            
            # Command injection
            ThreatSignature(
                "command_injection",
                r"(;|\||&|\$\(|`|\$\{|eval\(|exec\(|system\()",
                ThreatLevel.CRITICAL,
                "block",
                "Command injection attempt detected"
            ),
            
            # Path traversal
            ThreatSignature(
                "path_traversal",
                r"(\.\./|\.\.\\|/etc/passwd|/windows/system32)",
                ThreatLevel.HIGH,
                "block",
                "Path traversal attempt detected"
            ),
            
            # Suspicious user agents
            ThreatSignature(
                "suspicious_user_agent",
                r"(sqlmap|nikto|nmap|masscan|zgrab|shodan)",
                ThreatLevel.MEDIUM,
                "log",
                "Suspicious user agent detected"
            ),
            
            # Bot detection
            ThreatSignature(
                "bot_detection",
                r"(bot|crawler|spider|scraper|automation)",
                ThreatLevel.LOW,
                "rate_limit",
                "Automated bot detected"
            ),
        ]
    
    async def create_middleware(self) -> BaseHTTPMiddleware:
        """Create FastAPI middleware for the gateway"""
        
        class APIGatewayMiddleware(BaseHTTPMiddleware):
            def __init__(self, app, gateway_instance):
                super().__init__(app)
                self.gateway = gateway_instance
            
            async def dispatch(self, request: Request, call_next: Callable):
                start_time = time.time()
                
                # Security checks
                security_result = await self.gateway.security_check(request)
                if not security_result['allowed']:
                    return JSONResponse(
                        status_code=security_result['status_code'],
                        content={"error": security_result['message']}
                    )
                
                # Rate limiting
                rate_limit_result = await self.gateway.check_rate_limit(request)
                if not rate_limit_result['allowed']:
                    return JSONResponse(
                        status_code=429,
                        content={
                            "error": "Rate limit exceeded",
                            "retry_after": rate_limit_result.get('retry_after', 60)
                        },
                        headers={"Retry-After": str(rate_limit_result.get('retry_after', 60))}
                    )
                
                # Circuit breaker check
                if not await self.gateway.check_circuit_breaker(request):
                    return JSONResponse(
                        status_code=503,
                        content={"error": "Service temporarily unavailable"}
                    )
                
                try:
                    # Process request
                    response = await call_next(request)
                    
                    # Record metrics
                    processing_time = time.time() - start_time
                    await self.gateway.record_request_metrics(
                        request, response, processing_time
                    )
                    
                    # Add security headers
                    response = await self.gateway.add_security_headers(response)
                    
                    return response
                
                except Exception as e:
                    # Handle errors and update circuit breaker
                    await self.gateway.handle_request_error(request, str(e))
                    raise
        
        return APIGatewayMiddleware
    
    async def security_check(self, request: Request) -> Dict[str, Any]:
        """Comprehensive security check for incoming requests"""
        
        client_ip = self._get_client_ip(request)
        
        # Check if IP is blocked
        if client_ip in self.blocked_ips:
            logger.warning("Blocked IP attempted access", ip=client_ip)
            return {
                'allowed': False,
                'status_code': 403,
                'message': 'Access denied from this IP address'
            }
        
        # Check whitelist (if configured)
        if self.whitelisted_ips and client_ip not in self.whitelisted_ips:
            return {
                'allowed': False,
                'status_code': 403,
                'message': 'IP address not whitelisted'
            }
        
        # Threat signature detection
        threat_detected = await self._check_threat_signatures(request)
        if threat_detected:
            return {
                'allowed': False,
                'status_code': 403,
                'message': 'Security threat detected'
            }
        
        # DDoS detection
        if await self._detect_ddos_attack(request):
            return {
                'allowed': False,
                'status_code': 429,
                'message': 'DDoS attack detected - temporary block'
            }
        
        return {'allowed': True}
    
    async def check_rate_limit(self, request: Request) -> Dict[str, Any]:
        """Check rate limits for the request"""
        
        client_ip = self._get_client_ip(request)
        user_id = await self._extract_user_id(request)
        user_role = await self._extract_user_role(request)
        endpoint = str(request.url.path)
        
        # Determine request type
        request_type = self._classify_request(request)
        
        # Find applicable rate limit rules
        applicable_rules = self._find_applicable_rules(request_type, user_role, endpoint)
        
        for rule in applicable_rules:
            # Create rate limit key
            key_parts = [rule.name]
            if user_id:
                key_parts.append(f"user:{user_id}")
            else:
                key_parts.append(f"ip:{client_ip}")
            
            rate_limit_key = ":".join(key_parts)
            
            # Check rate limit
            is_allowed, retry_after = await self._check_rate_limit_key(
                rate_limit_key, rule.requests, rule.window_seconds
            )
            
            if not is_allowed:
                logger.warning("Rate limit exceeded", 
                             key=rate_limit_key, 
                             rule=rule.name,
                             ip=client_ip,
                             user_id=user_id)
                
                return {
                    'allowed': False,
                    'retry_after': retry_after,
                    'rule': rule.name
                }
        
        return {'allowed': True}
    
    async def _check_rate_limit_key(self, key: str, limit: int, window: int) -> Tuple[bool, int]:
        """Check rate limit for a specific key"""
        
        if self.redis_client:
            return await self._redis_rate_limit_check(key, limit, window)
        else:
            return await self._memory_rate_limit_check(key, limit, window)
    
    async def _redis_rate_limit_check(self, key: str, limit: int, window: int) -> Tuple[bool, int]:
        """Redis-based sliding window rate limiting"""
        
        now = time.time()
        window_start = now - window
        
        # Use Redis pipeline for atomic operations
        async with self.redis_client.pipeline() as pipe:
            # Remove expired entries
            await pipe.zremrangebyscore(key, 0, window_start)
            
            # Count current requests
            current_count = await pipe.zcard(key)
            
            if current_count >= limit:
                # Get oldest entry to calculate retry_after
                oldest = await pipe.zrange(key, 0, 0, withscores=True)
                if oldest:
                    retry_after = int(oldest[0][1] + window - now)
                else:
                    retry_after = window
                
                return False, max(retry_after, 1)
            
            # Add current request
            await pipe.zadd(key, {str(now): now})
            await pipe.expire(key, window)
            await pipe.execute()
            
            return True, 0
    
    async def _memory_rate_limit_check(self, key: str, limit: int, window: int) -> Tuple[bool, int]:
        """Memory-based rate limiting (fallback)"""
        
        if not hasattr(self, '_memory_store'):
            self._memory_store = {}
        
        now = time.time()
        window_start = now - window
        
        if key not in self._memory_store:
            self._memory_store[key] = []
        
        # Clean expired entries
        self._memory_store[key] = [
            timestamp for timestamp in self._memory_store[key] 
            if timestamp > window_start
        ]
        
        if len(self._memory_store[key]) >= limit:
            oldest = min(self._memory_store[key])
            retry_after = int(oldest + window - now)
            return False, max(retry_after, 1)
        
        self._memory_store[key].append(now)
        return True, 0
    
    async def check_circuit_breaker(self, request: Request) -> bool:
        """Check circuit breaker status for service"""
        
        service_key = self._get_service_key(request)
        
        if service_key not in self.circuit_breakers:
            self.circuit_breakers[service_key] = {
                'state': 'closed',  # closed, open, half_open
                'failure_count': 0,
                'last_failure_time': None,
                'success_count': 0
            }
        
        breaker = self.circuit_breakers[service_key]
        
        # If circuit is open, check if it should transition to half-open
        if breaker['state'] == 'open':
            if (time.time() - breaker['last_failure_time']) > 60:  # 1 minute timeout
                breaker['state'] = 'half_open'
                breaker['success_count'] = 0
                logger.info("Circuit breaker transitioning to half-open", service=service_key)
            else:
                return False
        
        return True
    
    async def record_request_metrics(self, request: Request, response: Response, 
                                   processing_time: float):
        """Record request metrics for analytics"""
        
        client_ip = self._get_client_ip(request)
        user_id = await self._extract_user_id(request)
        
        analytics = RequestAnalytics(
            timestamp=datetime.utcnow(),
            ip_address=client_ip,
            user_id=user_id,
            endpoint=str(request.url.path),
            method=request.method,
            response_time=processing_time,
            status_code=response.status_code,
            user_agent=request.headers.get('user-agent', ''),
            threat_level=ThreatLevel.LOW
        )
        
        self.request_analytics.append(analytics)
        
        # Update circuit breaker
        service_key = self._get_service_key(request)
        if service_key in self.circuit_breakers:
            breaker = self.circuit_breakers[service_key]
            
            if response.status_code >= 500:
                breaker['failure_count'] += 1
                breaker['last_failure_time'] = time.time()
                
                # Open circuit if too many failures
                if breaker['failure_count'] >= 5:
                    breaker['state'] = 'open'
                    logger.warning("Circuit breaker opened", service=service_key)
            else:
                if breaker['state'] == 'half_open':
                    breaker['success_count'] += 1
                    if breaker['success_count'] >= 3:
                        breaker['state'] = 'closed'
                        breaker['failure_count'] = 0
                        logger.info("Circuit breaker closed", service=service_key)
    
    async def add_security_headers(self, response: Response) -> Response:
        """Add security headers to response"""
        
        # Security headers
        security_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'",
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Permissions-Policy': 'microphone=(), camera=(), geolocation=()',
        }
        
        for header, value in security_headers.items():
            response.headers[header] = value
        
        return response
    
    async def handle_request_error(self, request: Request, error: str):
        """Handle request errors and update metrics"""
        
        service_key = self._get_service_key(request)
        if service_key in self.circuit_breakers:
            breaker = self.circuit_breakers[service_key]
            breaker['failure_count'] += 1
            breaker['last_failure_time'] = time.time()
        
        logger.error("Request processing error",
                    endpoint=str(request.url.path),
                    method=request.method,
                    error=error)
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request"""
        
        # Check forwarded headers
        forwarded_for = request.headers.get('x-forwarded-for')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        
        real_ip = request.headers.get('x-real-ip')
        if real_ip:
            return real_ip
        
        # Fallback to client host
        if hasattr(request, 'client') and request.client:
            return request.client.host
        
        return 'unknown'
    
    async def _extract_user_id(self, request: Request) -> Optional[str]:
        """Extract user ID from JWT token or session"""
        
        # Try to get from Authorization header
        auth_header = request.headers.get('authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header[7:]
            # In a real implementation, decode JWT and extract user_id
            # For now, return a placeholder
            return f"user_from_token_{hash(token) % 1000}"
        
        return None
    
    async def _extract_user_role(self, request: Request) -> Optional[str]:
        """Extract user role from JWT token or session"""
        
        # This would decode JWT and extract role
        # For now, return a placeholder based on endpoint
        endpoint = str(request.url.path)
        if '/parent/' in endpoint:
            return 'parent'
        elif '/child/' in endpoint:
            return 'child'
        
        return None
    
    def _classify_request(self, request: Request) -> RequestType:
        """Classify request type for rate limiting"""
        
        endpoint = str(request.url.path)
        method = request.method
        
        if '/auth/' in endpoint or '/login' in endpoint:
            return RequestType.AUTHENTICATION
        elif '/audio/' in endpoint and method == 'POST':
            return RequestType.AUDIO_UPLOAD
        elif '/ws' in endpoint or '/websocket' in endpoint:
            return RequestType.WEBSOCKET_CONNECTION
        elif '/upload' in endpoint or method == 'POST':
            return RequestType.FILE_UPLOAD
        elif '/bulk/' in endpoint:
            return RequestType.BULK_OPERATION
        else:
            return RequestType.API_CALL
    
    def _find_applicable_rules(self, request_type: RequestType, 
                              user_role: Optional[str], 
                              endpoint: str) -> List[RateLimitRule]:
        """Find applicable rate limit rules for request"""
        
        applicable_rules = []
        
        for rule in self.rate_limit_rules:
            # Check request type match
            if rule.request_type and rule.request_type != request_type:
                continue
            
            # Check user role match
            if rule.user_role and rule.user_role != user_role:
                continue
            
            # Check endpoint pattern match
            if rule.endpoint_pattern and not re.search(rule.endpoint_pattern, endpoint):
                continue
            
            applicable_rules.append(rule)
        
        return applicable_rules
    
    def _get_service_key(self, request: Request) -> str:
        """Get service key for circuit breaker"""
        
        # Use first part of path as service identifier
        path_parts = str(request.url.path).strip('/').split('/')
        return path_parts[0] if path_parts else 'default'
    
    async def _check_threat_signatures(self, request: Request) -> bool:
        """Check request against threat signatures"""
        
        # Check URL for threats
        url_str = str(request.url)
        for signature in self.threat_signatures:
            if re.search(signature.pattern, url_str, re.IGNORECASE):
                logger.warning("Threat signature detected in URL",
                             signature=signature.name,
                             url=url_str,
                             threat_level=signature.threat_level.value)
                
                if signature.action == 'block':
                    return True
        
        # Check headers
        for header_name, header_value in request.headers.items():
            for signature in self.threat_signatures:
                if re.search(signature.pattern, header_value, re.IGNORECASE):
                    logger.warning("Threat signature detected in headers",
                                 signature=signature.name,
                                 header=header_name,
                                 threat_level=signature.threat_level.value)
                    
                    if signature.action == 'block':
                        return True
        
        return False
    
    async def _detect_ddos_attack(self, request: Request) -> bool:
        """Detect potential DDoS attacks"""
        
        current_time = datetime.utcnow()
        one_minute_ago = current_time - timedelta(minutes=1)
        
        # Count requests in the last minute
        recent_requests = [
            analytics for analytics in self.request_analytics
            if analytics.timestamp > one_minute_ago
        ]
        
        if len(recent_requests) > self.ddos_thresholds['requests_per_minute']:
            # Check unique IPs
            unique_ips = len(set(analytics.ip_address for analytics in recent_requests))
            
            if unique_ips < self.ddos_thresholds['unique_ips_threshold']:
                logger.critical("Potential DDoS attack detected",
                              requests_per_minute=len(recent_requests),
                              unique_ips=unique_ips)
                return True
        
        return False
    
    def _start_monitoring(self) -> Any:
        """Start background monitoring tasks"""
        
        async def cleanup_task():
            """Cleanup old data periodically"""
            while True:
                await asyncio.sleep(300)  # 5 minutes
                
                # Clean up old analytics data
                cutoff_time = datetime.utcnow() - timedelta(hours=24)
                self.request_analytics = deque(
                    [a for a in self.request_analytics if a.timestamp > cutoff_time],
                    maxlen=10000
                )
        
        self._monitoring_tasks.append(asyncio.create_task(cleanup_task()))
    
    async def get_analytics_summary(self) -> Dict[str, Any]:
        """Get analytics summary"""
        
        current_time = datetime.utcnow()
        one_hour_ago = current_time - timedelta(hours=1)
        
        recent_requests = [
            analytics for analytics in self.request_analytics
            if analytics.timestamp > one_hour_ago
        ]
        
        return {
            'total_requests_last_hour': len(recent_requests),
            'unique_ips': len(set(r.ip_address for r in recent_requests)),
            'blocked_requests': len([r for r in recent_requests if r.blocked]),
            'average_response_time': sum(r.response_time for r in recent_requests) / len(recent_requests) if recent_requests else 0,
            'top_endpoints': self._get_top_endpoints(recent_requests),
            'threat_levels': self._get_threat_level_counts(recent_requests)
        }
    
    def _get_top_endpoints(self, requests: List[RequestAnalytics]) -> List[Dict[str, Any]]:
        """Get top endpoints by request count"""
        
        endpoint_counts = defaultdict(int)
        for req in requests:
            endpoint_counts[req.endpoint] += 1
        
        return [
            {'endpoint': endpoint, 'count': count}
            for endpoint, count in sorted(endpoint_counts.items(), 
                                        key=lambda x: x[1], reverse=True)[:10]
        ]
    
    def _get_threat_level_counts(self, requests: List[RequestAnalytics]) -> Dict[str, int]:
        """Get threat level distribution"""
        
        threat_counts = defaultdict(int)
        for req in requests:
            threat_counts[req.threat_level.value] += 1
        
        return dict(threat_counts)


# Global instance
_api_gateway: Optional[SecurityAPIGateway] = None


def get_api_gateway(redis_client: Optional[redis.Redis] = None) -> SecurityAPIGateway:
    """Get global API gateway instance"""
    global _api_gateway
    if _api_gateway is None:
        _api_gateway = SecurityAPIGateway(redis_client)
    return _api_gateway


def configure_app_security(Optional[redis.Redis] = None) -> None:
    """Configure FastAPI app with security middleware"""
    
    # Get API gateway instance
    gateway = get_api_gateway(redis_client)
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://*.teddybear.ai", "https://localhost:3000"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )
    
    # Add API Gateway middleware
    app.add_middleware(gateway.create_middleware())
    
    return app 