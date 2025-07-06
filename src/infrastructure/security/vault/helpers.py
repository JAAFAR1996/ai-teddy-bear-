"""
Helper functions and a global instance for the Vault integration.
"""
from typing import Optional

from .manager import VaultSecretsManager


# Global instance
_vault_manager: Optional[VaultSecretsManager] = None


def get_vault_manager() -> VaultSecretsManager:
    """Get global Vault manager instance"""
    global _vault_manager
    if _vault_manager is None:
        raise RuntimeError(
            "Vault manager not initialized. Call initialize_vault_manager() first."
        )
    return _vault_manager


def initialize_vault_manager(
    vault_url: str = "http://localhost:8200",
    vault_token: Optional[str] = None,
    namespace: Optional[str] = None,
    role_id: Optional[str] = None,
    secret_id: Optional[str] = None,
) -> VaultSecretsManager:
    """Initialize global Vault manager"""
    global _vault_manager
    _vault_manager = VaultSecretsManager(
        vault_url=vault_url,
        vault_token=vault_token,
        namespace=namespace,
        role_id=role_id,
        secret_id=secret_id,
    )
    return _vault_manager


# Convenience functions for common operations
async def get_api_key(service_name: str) -> Optional[str]:
    """Get API key for a service"""
    vault = get_vault_manager()
    secret = await vault.get_secret(f"api-keys/{service_name}")
    return secret.get("api_key") if secret else None


async def get_database_url(db_name: str) -> Optional[str]:
    """Get database connection URL"""
    vault = get_vault_manager()
    secret = await vault.get_secret(f"databases/{db_name}")
    return secret.get("connection_url") if secret else None


async def get_jwt_secret() -> Optional[str]:
    """Get JWT signing secret"""
    vault = get_vault_manager()
    secret = await vault.get_secret("auth/jwt")
    return secret.get("secret") if secret else None


async def get_encryption_key() -> Optional[str]:
    """Get application encryption key"""
    vault = get_vault_manager()
    secret = await vault.get_secret("encryption/master")
    return secret.get("key") if secret else None
