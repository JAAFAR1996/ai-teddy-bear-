"""
Factory function for creating a configured SecretsManager instance.
"""
from typing import Optional

from .config import SecretConfig
from .manager import SecretsManager
from .models import SecretProvider


def create_secrets_manager(
    environment: str = "development",
    vault_url: Optional[str] = None,
    vault_token: Optional[str] = None,
    aws_region: Optional[str] = None,
) -> SecretsManager:
    """Create a configured secrets manager instance"""

    config = SecretConfig(
        default_provider=(
            SecretProvider.HASHICORP_VAULT
            if vault_url
            else SecretProvider.LOCAL_ENCRYPTED
        ),
        auto_rotation_enabled=environment == "production",
        rotation_check_interval_hours=(
            24 if environment == "production" else 168
        ),  # Weekly in dev
        cache_ttl_seconds=300 if environment == "production" else 3600,  # 1 hour in dev
        audit_enabled=True,
        secure_delete_enabled=True,
    )

    # Configure Vault if available
    if vault_url and vault_token:
        config.vault_config = {
            "url": vault_url,
            "token": vault_token,
            "mount_point": "secret",
            "path_prefix": f"ai-teddy/{environment}",
        }

    # Configure AWS if credentials available
    if aws_region:
        config.aws_config = {
            "region": aws_region,
            "prefix": f"ai-teddy/{environment}"}

    return SecretsManager(config)
