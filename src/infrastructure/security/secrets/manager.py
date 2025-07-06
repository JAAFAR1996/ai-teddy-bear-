"""
Main secrets management system with caching and rotation.
"""
import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional

from .config import SecretConfig
from .models import SecretMetadata, SecretProvider, SecretType, SecretValue
from .providers.aws import AWSSecretsManagerProvider
from .providers.base import ISecretsProvider
from .providers.local import LocalEncryptedProvider
from .providers.vault import HashiCorpVaultProvider

logger = logging.getLogger(__name__)


class SecretsManager:
    """Main secrets management system with caching and rotation"""

    def __init__(self, config: SecretConfig):
        self.config = config
        self.providers: Dict[SecretProvider, ISecretsProvider] = {}
        self.cache: Dict[str, SecretValue] = {}
        self.rotation_tasks: Dict[str, asyncio.Task] = {}
        self._initialize_providers()

    def _initialize_providers(self):
        """Initialize configured providers"""
        if self.config.vault_config:
            self.providers[SecretProvider.HASHICORP_VAULT] = HashiCorpVaultProvider(
                self.config.vault_config)

        if self.config.aws_config:
            self.providers[SecretProvider.AWS_SECRETS_MANAGER] = (
                AWSSecretsManagerProvider(self.config.aws_config)
            )

        # Always have local provider as fallback
        self.providers[SecretProvider.LOCAL_ENCRYPTED] = LocalEncryptedProvider(
            {
                "secrets_dir": "./secrets",
                "secure_delete": self.config.secure_delete_enabled,
            }
        )

    async def _get_from_cache(self, name: str) -> Optional[SecretValue]:
        """Get secret from cache if valid."""
        if name in self.cache:
            cached = self.cache[name]
            cache_age = (
                datetime.now(timezone.utc) - cached.metadata.updated_at
            ).total_seconds()
            if cache_age < self.config.cache_ttl_seconds:
                return cached
        return None

    async def _get_from_provider(
        self, name: str, provider: SecretProvider
    ) -> Optional[SecretValue]:
        """Get secret from the specified provider."""
        if provider not in self.providers:
            logger.error(f"Provider {provider} not available")
            return None

        secret = await self.providers[provider].get_secret(name)
        if secret:
            self.cache[name] = secret  # Update cache
            if self.config.auto_rotation_enabled:
                await self._check_rotation_needed(secret)
        return secret

    async def get_secret(
        self,
        name: str,
        provider: Optional[SecretProvider] = None,
        use_cache: bool = True,
    ) -> Optional[str]:
        """Get secret value"""
        try:
            # Check cache first
            if use_cache:
                cached_secret = await self._get_from_cache(name)
                if cached_secret:
                    return cached_secret.value.get_secret_value()

            # Get from provider
            selected_provider = provider or self.config.default_provider
            secret = await self._get_from_provider(name, selected_provider)

            if not secret:
                return None

            return secret.value.get_secret_value()

        except Exception as e:
            logger.error(f"Failed to get secret {name}: {e}")
            return None

    async def set_secret(
        self,
        name: str,
        value: str,
        secret_type: SecretType = SecretType.API_KEY,
        provider: Optional[SecretProvider] = None,
        rotation_interval_days: int = 90,
        tags: Optional[Dict[str, str]] = None,
        description: Optional[str] = None,
    ) -> bool:
        """Store a secret"""
        try:
            provider = provider or self.config.default_provider
            if provider not in self.providers:
                logger.error(f"Provider {provider} not available")
                return False

            metadata = SecretMetadata(
                name=name,
                provider=provider,
                secret_type=secret_type,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
                rotation_interval_days=rotation_interval_days,
                tags=tags or {},
                description=description,
            )

            success = await self.providers[provider].set_secret(name, value, metadata)

            if success:
                # Clear cache
                self.cache.pop(name, None)

                # Setup rotation if enabled
                if self.config.auto_rotation_enabled:
                    await self._setup_rotation(name, metadata)

            return success

        except Exception as e:
            logger.error(f"Failed to set secret {name}: {e}")
            return False

    async def rotate_secret(
        self,
        name: str,
        new_value: Optional[str] = None,
        provider: Optional[SecretProvider] = None,
    ) -> bool:
        """Rotate a secret"""
        try:
            provider = provider or self.config.default_provider
            if provider not in self.providers:
                logger.error(f"Provider {provider} not available")
                return False

            # Generate new value if not provided
            if not new_value:
                new_value = self._generate_secret_value()

            success = await self.providers[provider].rotate_secret(name, new_value)

            if success:
                # Clear cache
                self.cache.pop(name, None)

                # Log rotation
                logger.info(f"Successfully rotated secret: {name}")

            return success

        except Exception as e:
            logger.error(f"Failed to rotate secret {name}: {e}")
            return False

    async def delete_secret(
        self, name: str, provider: Optional[SecretProvider] = None
    ) -> bool:
        """Delete a secret"""
        try:
            provider = provider or self.config.default_provider
            if provider not in self.providers:
                logger.error(f"Provider {provider} not available")
                return False

            success = await self.providers[provider].delete_secret(name)

            if success:
                # Clear cache
                self.cache.pop(name, None)

                # Cancel rotation task
                if name in self.rotation_tasks:
                    self.rotation_tasks[name].cancel()
                    del self.rotation_tasks[name]

            return success

        except Exception as e:
            logger.error(f"Failed to delete secret {name}: {e}")
            return False

    async def list_secrets(
        self, provider: Optional[SecretProvider] = None
    ) -> List[SecretMetadata]:
        """List all secrets"""
        try:
            provider = provider or self.config.default_provider
            if provider not in self.providers:
                logger.error(f"Provider {provider} not available")
                return []

            return await self.providers[provider].list_secrets()

        except Exception as e:
            logger.error(f"Failed to list secrets: {e}")
            return []

    async def _check_rotation_needed(self, secret: SecretValue):
        """Check if secret needs rotation"""
        metadata = secret.metadata

        # Calculate days since last rotation
        last_rotation = metadata.last_rotated_at or metadata.created_at
        days_since_rotation = (datetime.now(timezone.utc) - last_rotation).days

        if days_since_rotation >= metadata.rotation_interval_days:
            logger.warning(
                f"Secret {metadata.name} needs rotation (last rotated {days_since_rotation} days ago)"
            )

            # Schedule immediate rotation
            if metadata.name not in self.rotation_tasks:
                task = asyncio.create_task(
                    self._rotate_secret_task(metadata.name))
                self.rotation_tasks[metadata.name] = task

    async def _setup_rotation(self, name: str, metadata: SecretMetadata):
        """Setup automatic rotation for a secret"""
        if name in self.rotation_tasks:
            self.rotation_tasks[name].cancel()

        # Schedule rotation
        rotation_delay = (
            metadata.rotation_interval_days * 24 * 3600
        )  # Convert to seconds
        task = asyncio.create_task(
            self._rotation_scheduler(
                name, rotation_delay))
        self.rotation_tasks[name] = task

    async def _rotation_scheduler(self, name: str, delay_seconds: float):
        """Schedule secret rotation"""
        try:
            await asyncio.sleep(delay_seconds)
            await self._rotate_secret_task(name)
        except asyncio.CancelledError:
            logger.info(f"Rotation scheduler cancelled for {name}")

    async def _rotate_secret_task(self, name: str):
        """Task to rotate a secret"""
        try:
            logger.info(f"Starting automatic rotation for secret: {name}")
            success = await self.rotate_secret(name)

            if success:
                # Reschedule next rotation
                secret = await self.get_secret(name, use_cache=False)
                if secret:
                    metadata = self.cache[name].metadata
                    await self._setup_rotation(name, metadata)
            else:
                logger.error(f"Failed to rotate secret: {name}")

        except Exception as e:
            logger.error(f"Error in rotation task for {name}: {e}")

    def _generate_secret_value(self) -> str:
        """Generate a secure random secret value"""
        import secrets

        return secrets.token_urlsafe(32)

    async def initialize(self):
        """Initialize the secrets manager"""
        logger.info("Initializing Secrets Manager...")

        # Test provider connections
        for provider_type, provider in self.providers.items():
            try:
                # Try to list secrets to test connection
                await provider.list_secrets()
                logger.info(
                    f"✅ Successfully connected to {provider_type.name}")
            except Exception as e:
                logger.error(
                    f"❌ Failed to connect to {provider_type.name}: {e}")

        # Start rotation checker if enabled
        if self.config.auto_rotation_enabled:
            asyncio.create_task(self._rotation_checker())

    async def _rotation_checker(self):
        """Periodic task to check for secrets needing rotation"""
        while True:
            try:
                await asyncio.sleep(self.config.rotation_check_interval_hours * 3600)

                # Check all secrets
                for provider in self.providers.values():
                    secrets = await provider.list_secrets()
                    for metadata in secrets:
                        secret = await provider.get_secret(metadata.name)
                        if secret:
                            await self._check_rotation_needed(secret)

            except Exception as e:
                logger.error(f"Error in rotation checker: {e}")
