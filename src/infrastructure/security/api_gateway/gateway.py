"""
Main Security API Gateway class.
"""
import logging
from typing import Optional

import redis.asyncio as redis

from .analytics import AnalyticsCollectorMixin
from .circuit_breaker import CircuitBreakerMixin
from .middleware import APIGatewayMiddleware
from .rate_limiter import RateLimiterMixin
from .threat_detector import ThreatDetectorMixin

logger = logging.getLogger(__name__)


class SecurityAPIGateway(
    RateLimiterMixin,
    ThreatDetectorMixin,
    CircuitBreakerMixin,
    AnalyticsCollectorMixin,
):
    """
    A comprehensive, modular API Gateway that combines rate limiting, threat
    detection, circuit breaking, and analytics through a mixin-based architecture.
    """

    def __init__(self, redis_client: Optional[redis.Redis] = None):
        super().__init__(redis_client=redis_client)
        logger.info("Security API Gateway initialized.")

    def create_middleware(self) -> APIGatewayMiddleware:
        """Creates a FastAPI middleware instance for this gateway."""
        return APIGatewayMiddleware(app=None, gateway_instance=self)

    def _get_client_ip(self, request) -> str:
        """Extracts the client's IP address from the request."""
        if x_forwarded_for := request.headers.get("x-forwarded-for"):
            return x_forwarded_for.split(",")[0].strip()
        if x_real_ip := request.headers.get("x-real-ip"):
            return x_real_ip
        return request.client.host if request.client else "unknown"

    async def _extract_user_id(self, request) -> Optional[str]:
        """
        Extracts the user ID from the request, typically from a JWT or session.
        Placeholder: A real implementation would decode a token.
        """
        if auth := request.headers.get("authorization", "").split(" "):
            if len(auth) == 2 and auth[0].lower() == "bearer":
                # In a real app, decode token here: return jwt.decode(auth[1])['sub']
                return f"user_from_token_{hash(auth[1]) % 1000}"
        return None

    async def _extract_user_role(self, request) -> Optional[str]:
        """
        Extracts the user role from the request.
        Placeholder: A real implementation would decode a token.
        """
        # This is a mock implementation.
        if "/admin/" in str(request.url.path):
            return "admin"
        if "/parent/" in str(request.url.path):
            return "parent"
        if "/child/" in str(request.url.path):
            return "child"
        return "guest"

    def _get_service_key(self, request) -> str:
        """
        Generates a key for identifying an upstream service based on the request path,
        used for circuit breaking.
        """
        path_parts = str(request.url.path).strip("/").split("/")
        return path_parts[0] if path_parts else "default_service"

    async def add_security_headers(self, response):
        """Adds a set of standard security headers to the outgoing response."""
        headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
        }
        for key, value in headers.items():
            response.headers[key] = value
        return response
