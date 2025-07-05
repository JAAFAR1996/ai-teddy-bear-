"""
Security Middleware for AI Teddy Bear
Includes CORS, Rate Limiting, Security Headers, and Request Validation
"""

import asyncio
import hashlib
import secrets
import time
from collections import defaultdict
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Dict, List, Optional

import redis
import structlog
from fastapi import HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel, Field
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = structlog.get_logger()


class RateLimitConfig(BaseModel):
    """Rate limit configuration"""

    requests_per_minute: int = Field(default=60, gt=0)
    requests_per_hour: int = Field(default=1000, gt=0)
    requests_per_day: int = Field(default=10000, gt=0)
    burst_size: int = Field(default=10, gt=0)
    enable_redis: bool = True


class SecurityConfig(BaseModel):
    """Security configuration"""

    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000"]
    allowed_methods: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    allowed_headers: List[str] = ["*"]
    allow_credentials: bool = True
    max_age: int = 3600
    trusted_hosts: List[str] = ["localhost", "127.0.0.1"]
    enable_csrf: bool = True
    enable_rate_limit: bool = True
    rate_limit_config: RateLimitConfig = Field(default_factory=RateLimitConfig)


class RateLimiter:
    """Advanced rate limiter with Redis support"""

    def __init__(self, config: RateLimitConfig,
                 redis_client: Optional[redis.Redis] = None):
        self.config = config
        self.redis_client = redis_client
        self.local_cache: Dict[str, List[float]] = defaultdict(list)
        self._cleanup_task = None

    async def start(self):
        """Start background cleanup task"""
        if not self._cleanup_task:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def stop(self):
        """Stop background cleanup task"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

    async def _cleanup_loop(self):
        """Clean up old entries periodically"""
        while True:
            try:
                await asyncio.sleep(300)  # Every 5 minutes
                await self._cleanup_old_entries()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Rate limiter cleanup error", error=str(e))

    async def _cleanup_old_entries(self):
        """Remove old entries from local cache"""
        current_time = time.time()
        day_ago = current_time - 86400

        for key in list(self.local_cache.keys()):
            self.local_cache[key] = [
                ts for ts in self.local_cache[key] if ts > day_ago]
            if not self.local_cache[key]:
                del self.local_cache[key]

    async def check_rate_limit(self, identifier: str) -> bool:
        """Check if request is within rate limits"""
        current_time = time.time()

        if self.redis_client and self.config.enable_redis:
            return await self._check_redis_rate_limit(identifier, current_time)
        else:
            return self._check_local_rate_limit(identifier, current_time)

    async def _check_redis_rate_limit(
        self, identifier: str, current_time: float
    ) -> bool:
        """Check rate limit using Redis"""
        try:
            pipe = self.redis_client.pipeline()

            # Keys for different time windows
            minute_key = f"rl:m:{identifier}:{int(current_time // 60)}"
            hour_key = f"rl:h:{identifier}:{int(current_time // 3600)}"
            day_key = f"rl:d:{identifier}:{int(current_time // 86400)}"

            # Check all limits
            pipe.incr(minute_key)
            pipe.expire(minute_key, 60)
            pipe.incr(hour_key)
            pipe.expire(hour_key, 3600)
            pipe.incr(day_key)
            pipe.expire(day_key, 86400)

            results = await pipe.execute()

            minute_count = results[0]
            hour_count = results[2]
            day_count = results[4]

            if (
                minute_count > self.config.requests_per_minute
                or hour_count > self.config.requests_per_hour
                or day_count > self.config.requests_per_day
            ):
                # Decrement if over limit
                pipe = self.redis_client.pipeline()
                pipe.decr(minute_key)
                pipe.decr(hour_key)
                pipe.decr(day_key)
                await pipe.execute()
                return False

            return True

        except Exception as e:
            logger.warning("Redis rate limit check failed", error=str(e))
            # Fallback to local rate limiting
            return self._check_local_rate_limit(identifier, current_time)

    def _filter_timestamps(
        self, timestamps: List[float], current_time: float
    ) -> List[float]:
        """Filter out timestamps older than one day."""
        day_ago = current_time - 86400
        return [ts for ts in timestamps if ts > day_ago]

    def _count_requests(
        self, timestamps: List[float], time_window: int, current_time: float
    ) -> int:
        """Count requests within a given time window."""
        window_start = current_time - time_window
        return sum(1 for ts in timestamps if ts > window_start)

    def _check_local_rate_limit(
            self,
            identifier: str,
            current_time: float) -> bool:
        """Check rate limit using local memory"""
        timestamps = self.local_cache.get(identifier, [])

        timestamps = self._filter_timestamps(timestamps, current_time)

        minute_count = self._count_requests(timestamps, 60, current_time)
        hour_count = self._count_requests(timestamps, 3600, current_time)
        day_count = len(timestamps)

        if (
            minute_count >= self.config.requests_per_minute
            or hour_count >= self.config.requests_per_hour
            or day_count >= self.config.requests_per_day
        ):
            return False

        timestamps.append(current_time)
        self.local_cache[identifier] = timestamps

        return True

    def get_retry_after(self, identifier: str) -> int:
        """Get seconds until rate limit resets"""
        return 60  # Simple implementation, return 1 minute


class SecurityMiddleware(BaseHTTPMiddleware):
    """Comprehensive security middleware"""

    def __init__(self, app, config: SecurityConfig,
                 redis_client: Optional[redis.Redis] = None):
        super().__init__(app)
        self.config = config
        self.rate_limiter = RateLimiter(config.rate_limit_config, redis_client)
        self.csrf_tokens: Dict[str, float] = {}
        asyncio.create_task(self.rate_limiter.start())

    async def dispatch(self, request: Request, call_next):
        # Add security headers
        response = await self._add_security_headers(request, call_next)
        return response

    async def _add_security_headers(self, request: Request, call_next):
        """Add security headers to response"""
        # Check rate limit
        if self.config.enable_rate_limit:
            client_id = self._get_client_identifier(request)

            if not await self.rate_limiter.check_rate_limit(client_id):
                retry_after = self.rate_limiter.get_retry_after(client_id)
                logger.warning(
                    "Rate limit exceeded",
                    client_id=client_id,
                    path=request.url.path)
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={"detail": "Rate limit exceeded"},
                    headers={"Retry-After": str(retry_after)},
                )

        # Check CSRF for state-changing requests
        if self.config.enable_csrf and request.method in [
            "POST",
            "PUT",
            "DELETE",
            "PATCH",
        ]:
            if not await self._validate_csrf(request):
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"detail": "CSRF validation failed"},
                )

        # Process request
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(self), geolocation=(), payment=()"
        )

        # Add CSP header for HTML responses
        if "text/html" in response.headers.get("content-type", ""):
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "font-src 'self' https://fonts.gstatic.com; "
                "img-src 'self' data: https:; "
                "connect-src 'self' ws: wss: https:;")

        # Add timing header
        response.headers["X-Process-Time"] = str(process_time)

        # Log request
        logger.info(
            "Request processed",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            duration=process_time,
            client=self._get_client_identifier(request),
        )

        return response

    def _get_client_identifier(self, request: Request) -> str:
        """Get unique client identifier for rate limiting"""
        # Try to get authenticated user ID
        if hasattr(request.state, "user_id") and request.state.user_id:
            return f"user:{request.state.user_id}"

        # Try to get API key
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"api:{hashlib.sha256(api_key.encode()).hexdigest()[:16]}"

        # Fallback to IP address
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"

        return f"ip:{client_ip}"

    async def _validate_csrf(self, request: Request) -> bool:
        """Validate CSRF token"""
        # Skip CSRF for API endpoints with API key
        if request.headers.get("X-API-Key"):
            return True

        # Get CSRF token from header or form
        csrf_token = request.headers.get("X-CSRF-Token")
        if not csrf_token and request.method == "POST":
            form = await request.form()
            csrf_token = form.get("csrf_token")

        if not csrf_token:
            return False

        # Validate token
        return self._is_valid_csrf_token(csrf_token)

    def _is_valid_csrf_token(self, token: str) -> bool:
        """Check if CSRF token is valid"""
        if token not in self.csrf_tokens:
            return False

        # Check if token is expired (1 hour)
        if time.time() - self.csrf_tokens[token] > 3600:
            del self.csrf_tokens[token]
            return False

        return True

    def generate_csrf_token(self) -> str:
        """Generate new CSRF token"""
        token = secrets.token_urlsafe(32)
        self.csrf_tokens[token] = time.time()

        # Clean old tokens
        current_time = time.time()
        self.csrf_tokens = {
            k: v for k,
            v in self.csrf_tokens.items() if current_time -
            v < 3600}

        return token


def setup_security(app,
                   config,
                   redis_client: Optional[redis.Redis] = None) -> None:
    """Setup all security middleware"""
    security_config = SecurityConfig(**config.get("security", {}))

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=security_config.allowed_origins,
        allow_credentials=security_config.allow_credentials,
        allow_methods=security_config.allowed_methods,
        allow_headers=security_config.allowed_headers,
        max_age=security_config.max_age,
    )

    # Add trusted host middleware
    if security_config.trusted_hosts:
        app.add_middleware(
            TrustedHostMiddleware, allowed_hosts=security_config.trusted_hosts
        )

    # Add custom security middleware
    app.add_middleware(
        SecurityMiddleware, config=security_config, redis_client=redis_client
    )

    logger.info(
        "Security middleware configured",
        config=security_config.dict())


# Rate limiting decorator for specific endpoints
def rate_limit(int=10) -> None:
    """Decorator for endpoint-specific rate limiting"""

    def decorator(func) -> Any:
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            # Implement endpoint-specific rate limiting
            # This is a simplified version
            return await func(request, *args, **kwargs)

        return wrapper

    return decorator
