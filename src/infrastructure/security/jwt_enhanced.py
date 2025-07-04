from typing import Any, Dict, List, Optional

"""
🔐 Enhanced JWT Authentication - Refresh Tokens & Advanced Security
===================================================================

Enhanced JWT system with:
- Access tokens and refresh tokens
- Token blacklisting
- Role-based claims
- Secure token rotation
- Device fingerprinting

Author: Jaafar Adeeb - Security Lead
"""

import hashlib
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Set

import jwt
import redis.asyncio as redis
import structlog
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

logger = structlog.get_logger(__name__)


class TokenType(Enum):
    """JWT token types"""

    ACCESS = "access"
    REFRESH = "refresh"
    DEVICE = "device"


@dataclass
class TokenPair:
    """Access and refresh token pair"""

    access_token: str
    refresh_token: str
    access_expires_at: datetime
    refresh_expires_at: datetime
    token_type: str = "Bearer"


@dataclass
class TokenClaims:
    """JWT token claims"""

    user_id: str
    username: str
    email: str
    role: str
    family_id: Optional[str] = None
    device_id: Optional[str] = None
    permissions: List[str] = None
    is_parent: bool = False
    is_child: bool = False

    def __post_init__(self):
        if self.permissions is None:
            self.permissions = []


class EnhancedJWTManager:
    """Enhanced JWT manager with security features"""

    def __init__(
        self,
        secret_key: Optional[str] = None,
        redis_client: Optional[redis.Redis] = None,
    ):

        self.secret_key = secret_key or self._generate_secret_key()
        self.redis_client = redis_client
        self.algorithm = "HS256"

        # Token expiration settings
        self.access_token_expire = timedelta(minutes=15)
        self.refresh_token_expire = timedelta(days=30)
        self.device_token_expire = timedelta(days=365)

        # Security settings
        self.max_refresh_attempts = 3
        self.blacklist_cleanup_interval = 3600  # 1 hour

        # In-memory fallback for blacklist
        self.blacklisted_tokens: Set[str] = set()
        self.refresh_attempts: Dict[str, int] = {}

        # Device fingerprinting
        self.device_fingerprints: Dict[str, Dict[str, Any]] = {}

    def _generate_secret_key(self) -> str:
        """Generate secure secret key"""
        return secrets.token_urlsafe(64)

    async def create_token_pair(
        self, claims: TokenClaims, device_fingerprint: Optional[str] = None
    ) -> TokenPair:
        """Create access and refresh token pair"""

        now = datetime.utcnow()
        access_expires_at = now + self.access_token_expire
        refresh_expires_at = now + self.refresh_token_expire

        # Access token claims
        access_claims = {
            "user_id": claims.user_id,
            "username": claims.username,
            "email": claims.email,
            "role": claims.role,
            "family_id": claims.family_id,
            "device_id": claims.device_id,
            "permissions": claims.permissions,
            "is_parent": claims.is_parent,
            "is_child": claims.is_child,
            "token_type": TokenType.ACCESS.value,
            "iat": now,
            "exp": access_expires_at,
            "iss": "ai-teddy-bear",
            "jti": secrets.token_hex(16),  # Unique token ID
        }

        # Refresh token claims (minimal)
        refresh_claims = {
            "user_id": claims.user_id,
            "token_type": TokenType.REFRESH.value,
            "device_fingerprint": device_fingerprint,
            "iat": now,
            "exp": refresh_expires_at,
            "iss": "ai-teddy-bear",
            "jti": secrets.token_hex(16),
        }

        # Generate tokens
        access_token = jwt.encode(
            access_claims, self.secret_key, algorithm=self.algorithm
        )
        refresh_token = jwt.encode(
            refresh_claims, self.secret_key, algorithm=self.algorithm
        )

        # Store refresh token info
        await self._store_refresh_token(
            refresh_token, claims.user_id, device_fingerprint
        )

        logger.info(
            "Token pair created",
            user_id=claims.user_id,
            role=claims.role,
            device_id=claims.device_id,
        )

        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            access_expires_at=access_expires_at,
            refresh_expires_at=refresh_expires_at,
        )

    async def verify_access_token(self, token: str) -> Optional[TokenClaims]:
        """Verify and decode access token"""

        try:
            # Check if token is blacklisted
            if await self._is_token_blacklisted(token):
                logger.warning("Blacklisted token used")
                return None

            # Decode token
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            # Verify token type
            if payload.get("token_type") != TokenType.ACCESS.value:
                logger.warning("Invalid token type for access token")
                return None

            # Create claims object
            claims = TokenClaims(
                user_id=payload["user_id"],
                username=payload["username"],
                email=payload["email"],
                role=payload["role"],
                family_id=payload.get("family_id"),
                device_id=payload.get("device_id"),
                permissions=payload.get("permissions", []),
                is_parent=payload.get("is_parent", False),
                is_child=payload.get("is_child", False),
            )

            return claims

        except ExpiredSignatureError:
            logger.debug("Access token expired")
            return None
        except InvalidTokenError as e:
            logger.warning("Invalid access token", error=str(e))
            return None
        except Exception as e:
            logger.error("Token verification error", error=str(e))
            return None

    async def refresh_access_token(
        self, refresh_token: str, device_fingerprint: Optional[str] = None
    ) -> Optional[TokenPair]:
        """Refresh access token using refresh token"""

        try:
            # Decode refresh token
            payload = jwt.decode(
                refresh_token, self.secret_key, algorithms=[self.algorithm]
            )

            # Verify token type
            if payload.get("token_type") != TokenType.REFRESH.value:
                logger.warning("Invalid token type for refresh token")
                return None

            user_id = payload["user_id"]
            stored_fingerprint = payload.get("device_fingerprint")

            # Verify device fingerprint
            if stored_fingerprint and device_fingerprint != stored_fingerprint:
                logger.warning("Device fingerprint mismatch", user_id=user_id)
                await self._blacklist_token(refresh_token)
                return None

            # Check refresh attempts
            if not await self._check_refresh_attempts(user_id):
                logger.warning("Too many refresh attempts", user_id=user_id)
                return None

            # Get user claims (this would typically come from database)
            claims = await self._get_user_claims(user_id)
            if not claims:
                logger.warning("User not found for refresh", user_id=user_id)
                return None

            # Blacklist old refresh token
            await self._blacklist_token(refresh_token)

            # Create new token pair
            new_token_pair = await self.create_token_pair(claims, device_fingerprint)

            # Reset refresh attempts
            await self._reset_refresh_attempts(user_id)

            logger.info("Access token refreshed", user_id=user_id)
            return new_token_pair

        except ExpiredSignatureError:
            logger.debug("Refresh token expired")
            return None
        except InvalidTokenError as e:
            logger.warning("Invalid refresh token", error=str(e))
            return None
        except Exception as e:
            logger.error("Token refresh error", error=str(e))
            return None

    async def revoke_token(self, token: str) -> bool:
        """Revoke (blacklist) a token"""

        try:
            # Decode to get expiration
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={"verify_exp": False},
            )

            # Add to blacklist
            await self._blacklist_token(token)

            logger.info(
                "Token revoked",
                user_id=payload.get("user_id"),
                token_type=payload.get("token_type"),
            )

            return True

        except Exception as e:
            logger.error("Token revocation error", error=str(e))
            return False

    async def revoke_all_user_tokens(self, user_id: str) -> bool:
        """Revoke all tokens for a user"""

        try:
            # In a real system, this would mark all user tokens as revoked
            # For now, we'll add user to a revoked users set
            if self.redis_client:
                await self.redis_client.sadd("revoked_users", user_id)
                await self.redis_client.expire("revoked_users", 86400 * 30)  # 30 days

            logger.info("All user tokens revoked", user_id=user_id)
            return True

        except Exception as e:
            logger.error("User token revocation error", error=str(e))
            return False

    async def create_device_token(
        self, user_id: str, device_id: str, device_info: Dict[str, Any]
    ) -> str:
        """Create long-lived device token"""

        now = datetime.utcnow()
        expires_at = now + self.device_token_expire

        claims = {
            "user_id": user_id,
            "device_id": device_id,
            "device_info": device_info,
            "token_type": TokenType.DEVICE.value,
            "iat": now,
            "exp": expires_at,
            "iss": "ai-teddy-bear",
            "jti": secrets.token_hex(16),
        }

        device_token = jwt.encode(claims, self.secret_key, algorithm=self.algorithm)

        # Store device token info
        await self._store_device_token(device_token, user_id, device_id, device_info)

        logger.info("Device token created", user_id=user_id, device_id=device_id)

        return device_token

    async def verify_device_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify device token"""

        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            if payload.get("token_type") != TokenType.DEVICE.value:
                return None

            return {
                "user_id": payload["user_id"],
                "device_id": payload["device_id"],
                "device_info": payload.get("device_info", {}),
            }

        except Exception as e:
            logger.warning("Device token verification failed", error=str(e))
            return None

    def generate_device_fingerprint(self, user_agent: str, ip_address: str) -> str:
        """Generate device fingerprint"""

        # Combine user agent and IP for fingerprinting
        fingerprint_data = f"{user_agent}:{ip_address}".encode()
        fingerprint = hashlib.sha256(fingerprint_data).hexdigest()

        return fingerprint[:32]  # First 32 characters

    async def _store_refresh_token(
        self, token: str, user_id: str, device_fingerprint: Optional[str]
    ):
        """Store refresh token information"""

        if self.redis_client:
            token_info = {
                "user_id": user_id,
                "device_fingerprint": device_fingerprint,
                "created_at": datetime.utcnow().isoformat(),
            }

            # Store with expiration
            await self.redis_client.hset(f"refresh_token:{token}", mapping=token_info)
            await self.redis_client.expire(
                f"refresh_token:{token}", int(self.refresh_token_expire.total_seconds())
            )

    async def _store_device_token(
        self, token: str, user_id: str, device_id: str, device_info: Dict[str, Any]
    ):
        """Store device token information"""

        if self.redis_client:
            token_info = {
                "user_id": user_id,
                "device_id": device_id,
                "device_info": str(device_info),
                "created_at": datetime.utcnow().isoformat(),
            }

            await self.redis_client.hset(f"device_token:{token}", mapping=token_info)
            await self.redis_client.expire(
                f"device_token:{token}", int(self.device_token_expire.total_seconds())
            )

    async def _is_token_blacklisted(self, token: str) -> bool:
        """Check if token is blacklisted"""

        if self.redis_client:
            return await self.redis_client.sismember("blacklisted_tokens", token)
        else:
            return token in self.blacklisted_tokens

    async def _blacklist_token(self, token: str):
        """Add token to blacklist"""

        if self.redis_client:
            await self.redis_client.sadd("blacklisted_tokens", token)
            # Set expiration to match token expiration
            await self.redis_client.expire("blacklisted_tokens", 86400 * 30)  # 30 days
        else:
            self.blacklisted_tokens.add(token)

    async def _check_refresh_attempts(self, user_id: str) -> bool:
        """Check if user has exceeded refresh attempts"""

        if self.redis_client:
            attempts = await self.redis_client.get(f"refresh_attempts:{user_id}")
            current_attempts = int(attempts) if attempts else 0
        else:
            current_attempts = self.refresh_attempts.get(user_id, 0)

        if current_attempts >= self.max_refresh_attempts:
            return False

        # Increment attempts
        if self.redis_client:
            await self.redis_client.incr(f"refresh_attempts:{user_id}")
            await self.redis_client.expire(
                f"refresh_attempts:{user_id}", 3600
            )  # 1 hour
        else:
            self.refresh_attempts[user_id] = current_attempts + 1

        return True

    async def _reset_refresh_attempts(self, user_id: str):
        """Reset refresh attempts for user"""

        if self.redis_client:
            await self.redis_client.delete(f"refresh_attempts:{user_id}")
        else:
            self.refresh_attempts.pop(user_id, None)

    async def _get_user_claims(self, user_id: str) -> Optional[TokenClaims]:
        """Get user claims (would typically come from database)"""

        # This is a placeholder - in production, fetch from database
        # For now, return a basic claims object
        return TokenClaims(
            user_id=user_id,
            username=f"user_{user_id}",
            email=f"user_{user_id}@example.com",
            role="parent",  # Default role
            permissions=["child:interact", "audio:record"],
            is_parent=True,
        )

    async def get_token_info(self, token: str) -> Optional[Dict[str, Any]]:
        """Get token information without verification"""

        try:
            # Decode without verification to get info
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={"verify_exp": False},
            )

            return {
                "user_id": payload.get("user_id"),
                "token_type": payload.get("token_type"),
                "issued_at": datetime.fromtimestamp(payload.get("iat", 0)),
                "expires_at": datetime.fromtimestamp(payload.get("exp", 0)),
                "is_expired": datetime.utcnow()
                > datetime.fromtimestamp(payload.get("exp", 0)),
            }

        except Exception as e:
            logger.error("Token info extraction error", error=str(e))
            return None


# Global JWT manager
_jwt_manager: Optional[EnhancedJWTManager] = None


def get_jwt_manager(
    secret_key: Optional[str] = None, redis_client: Optional[redis.Redis] = None
) -> EnhancedJWTManager:
    """Get global JWT manager instance"""
    global _jwt_manager
    if _jwt_manager is None:
        _jwt_manager = EnhancedJWTManager(secret_key, redis_client)
    return _jwt_manager


# Convenience functions


async def create_parent_tokens(
    user_id: str,
    username: str,
    email: str,
    family_id: str,
    device_fingerprint: Optional[str] = None,
) -> TokenPair:
    """Create tokens for parent user"""
    jwt_manager = get_jwt_manager()

    claims = TokenClaims(
        user_id=user_id,
        username=username,
        email=email,
        role="parent",
        family_id=family_id,
        permissions=["child:interact", "parental_controls", "reports:view"],
        is_parent=True,
    )

    return await jwt_manager.create_token_pair(claims, device_fingerprint)


async def create_child_tokens(
    user_id: str,
    username: str,
    email: str,
    family_id: str,
    parent_id: str,
    device_id: str,
) -> TokenPair:
    """Create tokens for child user"""
    jwt_manager = get_jwt_manager()

    claims = TokenClaims(
        user_id=user_id,
        username=username,
        email=email,
        role="child",
        family_id=family_id,
        device_id=device_id,
        permissions=["child:interact", "audio:record"],
        is_child=True,
    )

    return await jwt_manager.create_token_pair(claims)
