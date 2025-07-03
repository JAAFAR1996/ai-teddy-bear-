"""Enterprise-Grade Authentication Middleware
Child-safe authentication with comprehensive security measures
"""

from __future__ import annotations

import asyncio
import logging
from functools import wraps
from typing import Any, Callable, Dict, Optional

import jwt
from flask import jsonify, request
from pydantic import BaseModel, Field

from domain.exceptions import (
    AuthenticationException,
    TokenExpiredException,
    SecurityException,
)
from infrastructure.security.secrets_manager import (
    SecretsManager,
    SecretType,
    create_secrets_manager,
)

logger = logging.getLogger(__name__)


class AuthConfig(BaseModel):
    """Authentication configuration"""
    
    jwt_secret_name: str = Field(default="jwt_secret", description="JWT secret name in vault")
    api_key_name: str = Field(default="teddy_api_key", description="API key name in vault")
    token_expiry_hours: int = Field(default=24, description="Token expiry in hours")
    max_failed_attempts: int = Field(default=5, description="Max failed auth attempts")
    lockout_duration_minutes: int = Field(default=15, description="Account lockout duration")
    
    class Config:
        validate_assignment = True


class AuthManager:
    """Centralized authentication manager with security features"""
    
    def __init__(self, config: Optional[AuthConfig] = None):
        self.config = config or AuthConfig()
        self.secrets_manager: Optional[SecretsManager] = None
        self._failed_attempts: Dict[str, int] = {}
        self._lockout_times: Dict[str, float] = {}
    
    async def initialize(self):
        """Initialize secrets manager"""
        try:
            self.secrets_manager = create_secrets_manager("production")
            await self.secrets_manager.initialize()
            logger.info("🔐 Authentication manager initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize auth manager: {e}")
            raise SecurityException(f"Authentication initialization failed: {e}")
    
    async def get_jwt_secret(self) -> str:
        """Get JWT secret from vault"""
        if not self.secrets_manager:
            raise SecurityException("Secrets manager not initialized")
        
        secret = await self.secrets_manager.get_secret(self.config.jwt_secret_name)
        if not secret:
            raise SecurityException(f"JWT secret '{self.config.jwt_secret_name}' not found")
        
        return secret
    
    async def get_api_key(self) -> str:
        """Get API key from vault"""
        if not self.secrets_manager:
            raise SecurityException("Secrets manager not initialized")
        
        secret = await self.secrets_manager.get_secret(self.config.api_key_name)
        if not secret:
            raise SecurityException(f"API key '{self.config.api_key_name}' not found")
        
        return secret
    
    def check_rate_limit(self, identifier: str) -> bool:
        """Check if request is rate limited"""
        current_time = asyncio.get_event_loop().time()
        
        # Check if account is locked out
        if identifier in self._lockout_times:
            lockout_until = self._lockout_times[identifier]
            if current_time < lockout_until:
                return False  # Still locked out
            else:
                # Lockout expired, reset
                del self._lockout_times[identifier]
                self._failed_attempts[identifier] = 0
        
        return True
    
    def record_failed_attempt(self, identifier: str):
        """Record a failed authentication attempt"""
        self._failed_attempts[identifier] = self._failed_attempts.get(identifier, 0) + 1
        
        if self._failed_attempts[identifier] >= self.config.max_failed_attempts:
            # Lockout account
            lockout_duration = self.config.lockout_duration_minutes * 60
            self._lockout_times[identifier] = asyncio.get_event_loop().time() + lockout_duration
            logger.warning(f"🔒 Account {identifier} locked out for {self.config.lockout_duration_minutes} minutes")
    
    def record_successful_attempt(self, identifier: str):
        """Record a successful authentication attempt"""
        if identifier in self._failed_attempts:
            del self._failed_attempts[identifier]
        if identifier in self._lockout_times:
            del self._lockout_times[identifier]


# Global auth manager instance
auth_manager = AuthManager()


def require_api_key(f) -> Any:
    """Require API key for endpoint access with vault-based validation"""

    @wraps(f)
    async def decorated_function(*args, **kwargs) -> Any:
        try:
            # Initialize auth manager if needed
            if not auth_manager.secrets_manager:
                await auth_manager.initialize()
            
            api_key = request.headers.get("X-API-Key")
            if not api_key:
                logger.warning("🚨 API key missing in request")
                return jsonify({"error": "API key required"}), 401

            # Get client IP for rate limiting
            client_ip = request.remote_addr or "unknown"
            
            # Check rate limiting
            if not auth_manager.check_rate_limit(client_ip):
                logger.warning(f"🚨 Rate limit exceeded for IP: {client_ip}")
                return jsonify({"error": "Rate limit exceeded"}), 429

            # Get valid API key from vault
            try:
                valid_api_key = await auth_manager.get_api_key()
            except SecurityException as e:
                logger.error(f"❌ Failed to retrieve API key from vault: {e}")
                return jsonify({"error": "Authentication service unavailable"}), 503

            if api_key != valid_api_key:
                auth_manager.record_failed_attempt(client_ip)
                logger.warning(f"🚨 Invalid API key from IP: {client_ip}")
                return jsonify({"error": "Invalid API key"}), 401

            # Record successful authentication
            auth_manager.record_successful_attempt(client_ip)
            logger.info(f"✅ Valid API key from IP: {client_ip}")

            return await f(*args, **kwargs)

        except Exception as e:
            logger.error(f"❌ Authentication error: {e}")
            return jsonify({"error": "Authentication failed"}), 500

    return decorated_function


def require_parent_auth(f) -> Any:
    """Require parent authentication for endpoint access with enhanced security"""

    @wraps(f)
    async def decorated_function(*args, **kwargs) -> Any:
        try:
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                logger.warning("🚨 Missing or invalid Authorization header")
                return jsonify({"error": "Authentication required"}), 401

            token = auth_header.split(" ")[1]
            client_ip = request.remote_addr or "unknown"

            # Check rate limiting
            if not auth_manager.check_rate_limit(client_ip):
                logger.warning(f"🚨 Rate limit exceeded for parent auth IP: {client_ip}")
                return jsonify({"error": "Rate limit exceeded"}), 429

            try:
                payload = await _decode_token(token)
                parent_id = payload.get("parent_id")
                
                if not parent_id:
                    auth_manager.record_failed_attempt(client_ip)
                    logger.warning(f"🚨 Missing parent_id in token from IP: {client_ip}")
                    return jsonify({"error": "Invalid token"}), 401
                
                request.parent_id = parent_id
                auth_manager.record_successful_attempt(client_ip)
                logger.info(f"✅ Valid parent authentication for ID: {parent_id} from IP: {client_ip}")
                
            except TokenExpiredException:
                auth_manager.record_failed_attempt(client_ip)
                logger.warning(f"🚨 Expired token from IP: {client_ip}")
                return jsonify({"error": "Token expired"}), 401
            except AuthenticationException as e:
                auth_manager.record_failed_attempt(client_ip)
                logger.warning(f"🚨 Invalid token from IP: {client_ip}: {e}")
                return jsonify({"error": "Invalid token"}), 401

            return await f(*args, **kwargs)

        except Exception as e:
            logger.error(f"❌ Parent authentication error: {e}")
            return jsonify({"error": "Authentication failed"}), 500

    return decorated_function


def require_child_auth(f) -> Any:
    """Require child authentication for endpoint access with enhanced security"""

    @wraps(f)
    async def decorated_function(*args, **kwargs) -> Any:
        try:
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                logger.warning("🚨 Missing or invalid Authorization header for child auth")
                return jsonify({"error": "Authentication required"}), 401

            token = auth_header.split(" ")[1]
            client_ip = request.remote_addr or "unknown"

            # Check rate limiting
            if not auth_manager.check_rate_limit(client_ip):
                logger.warning(f"🚨 Rate limit exceeded for child auth IP: {client_ip}")
                return jsonify({"error": "Rate limit exceeded"}), 429

            try:
                payload = await _decode_token(token)
                child_id = payload.get("child_id")
                
                if not child_id:
                    auth_manager.record_failed_attempt(client_ip)
                    logger.warning(f"🚨 Missing child_id in token from IP: {client_ip}")
                    return jsonify({"error": "Invalid token"}), 401
                
                request.child_id = child_id
                auth_manager.record_successful_attempt(client_ip)
                logger.info(f"✅ Valid child authentication for ID: {child_id} from IP: {client_ip}")
                
            except TokenExpiredException:
                auth_manager.record_failed_attempt(client_ip)
                logger.warning(f"🚨 Expired child token from IP: {client_ip}")
                return jsonify({"error": "Token expired"}), 401
            except AuthenticationException as e:
                auth_manager.record_failed_attempt(client_ip)
                logger.warning(f"🚨 Invalid child token from IP: {client_ip}: {e}")
                return jsonify({"error": "Invalid token"}), 401

            return await f(*args, **kwargs)

        except Exception as e:
            logger.error(f"❌ Child authentication error: {e}")
            return jsonify({"error": "Authentication failed"}), 500

    return decorated_function


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------


async def _decode_token(token: str) -> Dict[str, Any]:
    """Decode JWT with vault-based secret and return payload or raise specific exceptions."""

    try:
        # Initialize auth manager if needed
        if not auth_manager.secrets_manager:
            await auth_manager.initialize()
        
        # Get JWT secret from vault
        secret = await auth_manager.get_jwt_secret()
        algorithms = ["HS256"]

        try:
            return jwt.decode(token, secret, algorithms=algorithms)
        except jwt.ExpiredSignatureError as exc:
            logger.warning("🚨 JWT token expired")
            raise TokenExpiredException() from exc
        except jwt.InvalidTokenError as exc:
            logger.warning("🚨 Invalid JWT token")
            raise AuthenticationException(reason="invalid token") from exc
            
    except SecurityException as e:
        logger.error(f"❌ Failed to retrieve JWT secret from vault: {e}")
        raise AuthenticationException(reason="authentication service unavailable") from e
    except Exception as e:
        logger.error(f"❌ Token decoding error: {e}")
        raise AuthenticationException(reason="token processing failed") from e
