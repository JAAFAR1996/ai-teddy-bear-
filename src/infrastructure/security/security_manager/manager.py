"""
The main EnterpriseSecurityManager class.
"""
import logging
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union

import jwt
import redis.asyncio as redis
from fastapi import HTTPException, Request, status

from .audit_logger import SecurityAuditLogger
from .encryption import AdvancedEncryption
from .models import SecurityEvent, SecurityEventType, ThreatLevel
from .password import PasswordSecurity
from .rate_limiter import RateLimitingService
from .threat_detector import ThreatDetectionEngine

logger = logging.getLogger(__name__)


class EnterpriseSecurityManager:
    """
    The central coordinator for all security components, providing a unified
    interface for encryption, password management, threat detection, and more.
    """

    def __init__(self, settings: Optional[Any] = None):
        redis_client = redis.from_url(settings.redis_url) if settings and hasattr(
            settings, "redis_url") else None

        self.encryption = AdvancedEncryption()
        self.password_security = PasswordSecurity()
        self.audit_logger = SecurityAuditLogger()
        self.threat_detector = ThreatDetectionEngine()
        self.rate_limiter = RateLimitingService(redis_client=redis_client)

        self.jwt_secret = getattr(
            settings, "jwt_secret", secrets.token_urlsafe(32))
        self.jwt_algorithm = "HS256"
        self.jwt_expire_minutes = 30

    async def authenticate_request(self, request: Request) -> Dict[str, Any]:
        """Performs a full authentication and security check on an incoming request."""
        client_ip = request.client.host if request.client else "unknown"

        # 1. Threat Detection
        threat_level, threats = await self.threat_detector.analyze_request(request)
        if threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
            await self.audit_logger.log_event(self._create_security_event(
                SecurityEventType.SUSPICIOUS_ACTIVITY, request, threat_level, {
                    "threats": threats}
            ))
            raise HTTPException(status.HTTP_403_FORBIDDEN,
                                "Request blocked due to security policy.")

        # 2. Rate Limiting
        is_allowed, rate_info = await self.rate_limiter.check_rate_limit(client_ip, "api_general")
        if not is_allowed:
            await self.audit_logger.log_event(self._create_security_event(
                SecurityEventType.RATE_LIMIT_EXCEEDED, request, ThreatLevel.MEDIUM, rate_info
            ))
            raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "Rate limit exceeded.",
                                headers={"Retry-After": str(int(rate_info.get("retry_after", 60)))})

        # 3. JWT Validation
        token = self._extract_token(request)
        if not token:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED,
                                "Authentication token required.")

        try:
            payload = jwt.decode(token, self.jwt_secret,
                                 algorithms=[self.jwt_algorithm])
            user_id = payload.get("user_id")
            await self.audit_logger.log_event(self._create_security_event(
                SecurityEventType.LOGIN_SUCCESS, request, ThreatLevel.LOW, {
                    "user_id": user_id}
            ))
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, "Token has expired.")
        except jwt.InvalidTokenError:
            await self.audit_logger.log_event(self._create_security_event(
                SecurityEventType.LOGIN_FAILURE, request, ThreatLevel.MEDIUM, {
                    "reason": "invalid_token"}
            ))
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token.")

    def _extract_token(self, request: Request) -> Optional[str]:
        """Extracts a JWT from the 'Authorization: Bearer' header or a cookie."""
        if auth_header := request.headers.get("authorization"):
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == "bearer":
                return parts[1]
        return request.cookies.get("access_token")

    def generate_jwt(self, user_id: str, claims: Optional[Dict[str, Any]] = None) -> str:
        """Generates a new JWT for a given user ID and optional claims."""
        now = datetime.utcnow()
        payload = {
            "user_id": user_id,
            "iat": now,
            "exp": now + timedelta(minutes=self.jwt_expire_minutes),
            "iss": "ai-teddy-bear-security",
        }
        if claims:
            payload.update(claims)
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)

    async def encrypt_data(self, data: Union[str, bytes], context: str) -> bytes:
        """Encrypts sensitive data and logs the operation."""
        encrypted = self.encryption.encrypt_symmetric(data)
        await self.audit_logger.log_event(self._create_security_event(
            SecurityEventType.ENCRYPTION_OPERATION, details={
                "context": context}
        ))
        return encrypted

    async def decrypt_data(self, encrypted_data: bytes, context: str) -> bytes:
        """Decrypts sensitive data and logs the operation."""
        decrypted = self.encryption.decrypt_symmetric(encrypted_data)
        await self.audit_logger.log_event(self._create_security_event(
            SecurityEventType.DECRYPTION_OPERATION, details={
                "context": context}
        ))
        return decrypted

    def _create_security_event(
        self, event_type: SecurityEventType, request: Optional[Request] = None,
        threat_level: ThreatLevel = ThreatLevel.LOW, details: Optional[Dict] = None
    ) -> SecurityEvent:
        """A helper to create a SecurityEvent object with context from a request."""
        return SecurityEvent(
            event_type=event_type,
            timestamp=datetime.utcnow(),
            ip_address=request.client.host if request and request.client else None,
            user_agent=request.headers.get("user-agent") if request else None,
            resource=str(request.url.path) if request else None,
            threat_level=threat_level,
            details=details or {},
        )
