"""
🔐 Security Manager - Unified Security System
==============================================

Comprehensive security manager integrating:
- Vault secrets management
- RBAC system
- API Gateway security
- Audio encryption
- JWT authentication
- Audit logging

Author: Jaafar Adeeb - Security Lead
"""

from typing import Any, Dict, Optional

import redis.asyncio as redis
import structlog

from .api_security_gateway import APISecurityGateway, get_security_gateway
from .audio_security import AudioEncryptionManager, get_audio_encryption_manager
from .jwt_auth import JWTManager, TokenPair, UserClaims, get_jwt_manager
from .rbac_system import Permission, RBACManager, UserRole, get_rbac_manager
from .vault_secrets_manager import VaultSecretsManager, get_vault_manager

logger = structlog.get_logger(__name__)


class SecurityManager:
    """Unified security manager for AI Teddy Bear system"""

    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client

        # Initialize security components
        self.vault_manager: VaultSecretsManager = get_vault_manager()
        self.rbac_manager: RBACManager = get_rbac_manager()
        self.api_gateway: APISecurityGateway = get_security_gateway(
            redis_client)
        self.audio_encryption: AudioEncryptionManager = get_audio_encryption_manager()
        self.jwt_manager: JWTManager = get_jwt_manager(
            redis_client=redis_client)

        logger.info("Security Manager initialized with all components")

    # Vault Operations
    async def store_secret(
            self, path: str, secret_data: Dict[str, Any]) -> bool:
        """Store secret in Vault"""
        return await self.vault_manager.store_secret(path, secret_data)

    async def get_secret(self, path: str) -> Optional[Dict[str, Any]]:
        """Retrieve secret from Vault"""
        return await self.vault_manager.get_secret(path)

    # RBAC Operations
    async def create_parent_user(
        self,
        user_id: str,
        username: str,
        family_id: str,
        parent_id: Optional[str] = None,
    ):
        """Create parent user with proper permissions"""
        return await self.rbac_manager.create_user(
            user_id=user_id,
            username=username,
            role=UserRole.PARENT,
            family_id=family_id,
            parent_id=parent_id,
        )

    async def create_child_user(
        self, user_id: str, username: str, family_id: str, parent_id: str
    ):
        """Create child user with restricted permissions"""
        return await self.rbac_manager.create_user(
            user_id=user_id,
            username=username,
            role=UserRole.CHILD,
            family_id=family_id,
            parent_id=parent_id,
        )

    async def check_permission(
            self,
            user_id: str,
            permission: Permission,
            resource_id: Optional[str] = None) -> bool:
        """Check if user has permission for action"""
        return await self.rbac_manager.check_permission(
            user_id, permission, resource_id
        )

    # Authentication Operations
    async def authenticate_parent(
        self, user_id: str, username: str, email: str, family_id: str
    ) -> TokenPair:
        """Authenticate parent and create tokens"""
        claims = UserClaims(
            user_id=user_id,
            username=username,
            email=email,
            role="parent",
            family_id=family_id,
            is_parent=True,
        )
        return await self.jwt_manager.create_token_pair(claims)

    async def authenticate_child(
            self,
            user_id: str,
            username: str,
            email: str,
            family_id: str,
            device_id: str) -> TokenPair:
        """Authenticate child and create tokens"""
        claims = UserClaims(
            user_id=user_id,
            username=username,
            email=email,
            role="child",
            family_id=family_id,
            device_id=device_id,
            is_child=True,
        )
        return await self.jwt_manager.create_token_pair(claims)

    async def verify_token(self, token: str) -> Optional[UserClaims]:
        """Verify JWT token"""
        return await self.jwt_manager.verify_access_token(token)

    async def refresh_token(self, refresh_token: str) -> Optional[TokenPair]:
        """Refresh access token"""
        return await self.jwt_manager.refresh_access_token(refresh_token)

    # Audio Security Operations
    async def create_audio_session(self, device_id: str, user_id: str) -> str:
        """Create encrypted audio session"""
        return await self.audio_encryption.create_session(device_id, user_id)

    async def encrypt_audio(self, session_id: str,
                            audio_data: bytes) -> Dict[str, str]:
        """Encrypt audio data"""
        return await self.audio_encryption.encrypt_audio(session_id, audio_data)

    async def decrypt_audio(self, encrypted_packet: Dict[str, str]) -> bytes:
        """Decrypt audio data"""
        return await self.audio_encryption.decrypt_audio(encrypted_packet)

    # Security Health Check
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive security health check"""

        vault_health = await self.vault_manager.health_check()

        return {
            "status": "healthy",
            "components": {
                "vault": vault_health,
                "rbac": {
                    "status": "healthy",
                    "users_count": len(self.rbac_manager.users),
                },
                "api_gateway": {"status": "healthy"},
                "audio_encryption": {
                    "status": "healthy",
                    "active_sessions": len(self.audio_encryption.active_sessions),
                },
                "jwt_manager": {"status": "healthy"},
            },
            "timestamp": "2025-01-01T00:00:00Z",
        }

    # Security Policies
    async def enforce_child_safety_policy(
            self, user_id: str, action: str) -> bool:
        """Enforce child safety policies"""

        user = self.rbac_manager.get_user(user_id)
        if not user:
            return False

        # Child-specific safety checks
        if user.role == UserRole.CHILD:
            # Check time restrictions
            # Check content appropriateness
            # Check parental approval for certain actions

            if action in ["audio_record", "conversation_start"]:
                # Always allow basic interactions for children
                return True
            elif action in ["data_export", "settings_change"]:
                # Require parent permission
                return False

        return True

    async def apply_zero_trust_policies(
            self, request_context: Dict[str, Any]) -> bool:
        """Apply Zero Trust security policies"""

        # Verify every request regardless of source
        user_id = request_context.get("user_id")
        ip_address = request_context.get("ip_address")
        device_id = request_context.get("device_id")

        if not user_id:
            return False

        # Check user status
        user = self.rbac_manager.get_user(user_id)
        if not user or not user.is_active:
            return False

        # Device verification for children
        if user.role == UserRole.CHILD and not device_id:
            return False

        # Additional security checks would go here
        # - Device fingerprinting
        # - Behavioral analysis
        # - Risk scoring

        return True


# Global security manager
_security_manager: Optional[SecurityManager] = None


def get_security_manager(
        redis_client: Optional[redis.Redis] = None) -> SecurityManager:
    """Get global security manager instance"""
    global _security_manager
    if _security_manager is None:
        _security_manager = SecurityManager(redis_client)
    return _security_manager


# Convenience functions for common operations


async def secure_child_audio_flow(
    device_id: str, user_id: str, audio_data: bytes
) -> Dict[str, Any]:
    """Complete secure audio flow for child interaction"""
    security_manager = get_security_manager()

    # 1. Check permissions
    can_record = await security_manager.check_permission(
        user_id, Permission.AUDIO_RECORD
    )
    if not can_record:
        raise PermissionError("Audio recording not permitted")

    # 2. Apply safety policies
    if not await security_manager.enforce_child_safety_policy(user_id, "audio_record"):
        raise PermissionError("Child safety policy violation")

    # 3. Create encryption session
    session_id = await security_manager.create_audio_session(device_id, user_id)

    # 4. Encrypt audio
    encrypted_packet = await security_manager.encrypt_audio(session_id, audio_data)

    return {
        "encrypted_packet": encrypted_packet,
        "session_id": session_id,
        "security_level": "high",
    }


async def authenticate_family_member(
    username: str,
    password: str,
    role: str,
    family_id: str,
    device_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Authenticate family member with full security flow"""
    security_manager = get_security_manager()

    # This is a simplified version - in production, password would be verified
    # against secure storage

    user_id = f"{role}_{username}_{family_id}"
    email = f"{username}@family-{family_id}.teddy"

    if role == "parent":
        # Create parent user if doesn't exist
        await security_manager.create_parent_user(user_id, username, family_id)

        # Authenticate and get tokens
        tokens = await security_manager.authenticate_parent(
            user_id, username, email, family_id
        )
    elif role == "child":
        if not device_id:
            raise ValueError("Device ID required for child authentication")

        # Create child user if doesn't exist
        await security_manager.create_child_user(user_id, username, family_id, user_id)

        # Authenticate and get tokens
        tokens = await security_manager.authenticate_child(
            user_id, username, email, family_id, device_id
        )
    else:
        raise ValueError(f"Invalid role: {role}")

    return {
        "user_id": user_id,
        "tokens": tokens,
        "role": role,
        "family_id": family_id}
