from typing import Optional

"""
🔐 Enhanced JWT Authentication with Refresh Tokens
===================================================

Author: Jaafar Adeeb - Security Lead
"""

import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, Set

import jwt
import redis.asyncio as redis
import structlog
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

logger = structlog.get_logger(__name__)


@dataclass
class TokenPair:
    """Access and refresh token pair"""

    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "Bearer"


@dataclass
class UserClaims:
    """User claims for JWT tokens"""

    user_id: str
    username: str
    email: str
    role: str
    family_id: Optional[str] = None
    device_id: Optional[str] = None
    is_parent: bool = False
    is_child: bool = False


class JWTManager:
    """Enhanced JWT manager with refresh tokens"""

    def __init__(
        self,
        secret_key: Optional[str] = None,
        redis_client: Optional[redis.Redis] = None,
    ):
        self.secret_key = secret_key or secrets.token_urlsafe(64)
        self.redis_client = redis_client
        self.algorithm = "HS256"

        # Token expiration
        self.access_token_expire = timedelta(minutes=15)
        self.refresh_token_expire = timedelta(days=30)

        # Blacklisted tokens (fallback to memory)
        self.blacklisted_tokens: Set[str] = set()

    async def create_token_pair(self, claims: UserClaims) -> TokenPair:
        """Create access and refresh token pair"""

        now = datetime.utcnow()
        access_exp = now + self.access_token_expire
        refresh_exp = now + self.refresh_token_expire

        # Access token payload
        access_payload = {
            "user_id": claims.user_id,
            "username": claims.username,
            "email": claims.email,
            "role": claims.role,
            "family_id": claims.family_id,
            "device_id": claims.device_id,
            "is_parent": claims.is_parent,
            "is_child": claims.is_child,
            "token_type": "access",
            "iat": now,
            "exp": access_exp,
            "iss": "ai-teddy-bear",
        }

        # Refresh token payload (minimal)
        refresh_payload = {
            "user_id": claims.user_id,
            "token_type": "refresh",
            "iat": now,
            "exp": refresh_exp,
            "iss": "ai-teddy-bear",
        }

        # Generate tokens
        access_token = jwt.encode(
            access_payload, self.secret_key, algorithm=self.algorithm
        )
        refresh_token = jwt.encode(
            refresh_payload, self.secret_key, algorithm=self.algorithm
        )

        # Store refresh token
        await self._store_refresh_token(refresh_token, claims.user_id)

        logger.info(
            "Token pair created",
            user_id=claims.user_id,
            role=claims.role)

        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=int(self.access_token_expire.total_seconds()),
        )

    async def verify_access_token(self, token: str) -> Optional[UserClaims]:
        """Verify access token and return claims"""

        try:
            # Check blacklist
            if await self._is_blacklisted(token):
                return None

            # Decode token
            payload = jwt.decode(
                token, self.secret_key, algorithms=[
                    self.algorithm])

            # Verify token type
            if payload.get("token_type") != "access":
                return None

            # Create claims
            return UserClaims(
                user_id=payload["user_id"],
                username=payload["username"],
                email=payload["email"],
                role=payload["role"],
                family_id=payload.get("family_id"),
                device_id=payload.get("device_id"),
                is_parent=payload.get("is_parent", False),
                is_child=payload.get("is_child", False),
            )

        except ExpiredSignatureError:
            logger.debug("Access token expired")
            return None
        except InvalidTokenError:
            logger.warning("Invalid access token")
            return None
        except Exception as e:
            logger.error("Token verification error", error=str(e))
            return None

    async def refresh_access_token(
            self, refresh_token: str) -> Optional[TokenPair]:
        """Refresh access token"""

        try:
            # Decode refresh token
            payload = jwt.decode(
                refresh_token, self.secret_key, algorithms=[self.algorithm]
            )

            # Verify token type
            if payload.get("token_type") != "refresh":
                return None

            user_id = payload["user_id"]

            # Verify refresh token is stored
            if not await self._is_refresh_token_valid(refresh_token, user_id):
                return None

            # Get user claims (in production, from database)
            claims = await self._get_user_claims(user_id)
            if not claims:
                return None

            # Blacklist old refresh token
            await self._blacklist_token(refresh_token)

            # Create new token pair
            return await self.create_token_pair(claims)

        except ExpiredSignatureError:
            logger.debug("Refresh token expired")
            return None
        except InvalidTokenError:
            logger.warning("Invalid refresh token")
            return None
        except Exception as e:
            logger.error("Token refresh error", error=str(e))
            return None

    async def revoke_token(self, token: str) -> bool:
        """Revoke a token (add to blacklist)"""

        try:
            await self._blacklist_token(token)
            logger.info("Token revoked")
            return True
        except Exception as e:
            logger.error("Token revocation error", error=str(e))
            return False

    async def _store_refresh_token(self, token: str, user_id: str):
        """Store refresh token"""

        if self.redis_client:
            # Store in Redis with expiration
            await self.redis_client.setex(
                f"refresh_token:{user_id}",
                int(self.refresh_token_expire.total_seconds()),
                token,
            )

    async def _is_refresh_token_valid(self, token: str, user_id: str) -> bool:
        """Check if refresh token is valid"""

        if self.redis_client:
            stored_token = await self.redis_client.get(f"refresh_token:{user_id}")
            return stored_token and stored_token.decode() == token

        return True  # Fallback - accept any valid token

    async def _is_blacklisted(self, token: str) -> bool:
        """Check if token is blacklisted"""

        if self.redis_client:
            return await self.redis_client.sismember("blacklisted_tokens", token)
        else:
            return token in self.blacklisted_tokens

    async def _blacklist_token(self, token: str):
        """Add token to blacklist"""

        if self.redis_client:
            await self.redis_client.sadd("blacklisted_tokens", token)
            # Expire blacklist after 30 days
            await self.redis_client.expire("blacklisted_tokens", 86400 * 30)
        else:
            self.blacklisted_tokens.add(token)

    async def _get_user_claims(self, user_id: str) -> Optional[UserClaims]:
        """Get user claims (placeholder - would come from database)"""

        # Placeholder implementation
        return UserClaims(
            user_id=user_id,
            username=f"user_{user_id}",
            email=f"user_{user_id}@example.com",
            role="parent",
            is_parent=True,
        )


# Global JWT manager
_jwt_manager: Optional[JWTManager] = None


def get_jwt_manager(
    secret_key: Optional[str] = None, redis_client: Optional[redis.Redis] = None
) -> JWTManager:
    """Get global JWT manager"""
    global _jwt_manager
    if _jwt_manager is None:
        _jwt_manager = JWTManager(secret_key, redis_client)
    return _jwt_manager


# Convenience functions


async def authenticate_parent(
    user_id: str, username: str, email: str, family_id: str
) -> TokenPair:
    """Create tokens for parent"""
    jwt_manager = get_jwt_manager()

    claims = UserClaims(
        user_id=user_id,
        username=username,
        email=email,
        role="parent",
        family_id=family_id,
        is_parent=True,
    )

    return await jwt_manager.create_token_pair(claims)


async def authenticate_child(
    user_id: str, username: str, email: str, family_id: str, device_id: str
) -> TokenPair:
    """Create tokens for child"""
    jwt_manager = get_jwt_manager()

    claims = UserClaims(
        user_id=user_id,
        username=username,
        email=email,
        role="child",
        family_id=family_id,
        device_id=device_id,
        is_child=True,
    )

    return await jwt_manager.create_token_pair(claims)
