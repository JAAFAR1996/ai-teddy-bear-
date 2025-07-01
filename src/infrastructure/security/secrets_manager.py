"""
Enterprise-Grade Secrets Management System
Supports HashiCorp Vault, AWS Secrets Manager, and secure local storage
"""

import asyncio
import base64
import json
import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, Union

import aiofiles
import aioredis
import boto3
import hvac
from botocore.exceptions import ClientError
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from pydantic import BaseModel, Field, SecretStr, validator

logger = logging.getLogger(__name__)


class SecretProvider(Enum):
    """Supported secret providers"""

    HASHICORP_VAULT = auto()
    AWS_SECRETS_MANAGER = auto()
    AZURE_KEY_VAULT = auto()
    LOCAL_ENCRYPTED = auto()


class SecretType(Enum):
    """Types of secrets"""

    API_KEY = auto()
    PASSWORD = auto()
    TOKEN = auto()
    CERTIFICATE = auto()
    ENCRYPTION_KEY = auto()
    CONNECTION_STRING = auto()


@dataclass
class SecretMetadata:
    """Metadata for a secret"""

    name: str
    provider: SecretProvider
    secret_type: SecretType
    created_at: datetime
    updated_at: datetime
    rotation_interval_days: int = 90
    last_rotated_at: Optional[datetime] = None
    version: int = 1
    tags: Dict[str, str] = field(default_factory=dict)
    description: Optional[str] = None
    allowed_environments: List[str] = field(default_factory=lambda: ["production"])
    audit_trail: List[Dict[str, Any]] = field(default_factory=list)


class SecretConfig(BaseModel):
    """Configuration for secrets management"""

    default_provider: SecretProvider = SecretProvider.HASHICORP_VAULT
    auto_rotation_enabled: bool = True
    rotation_check_interval_hours: int = 24
    encryption_key_path: Optional[Path] = None
    vault_config: Optional[Dict[str, Any]] = None
    aws_config: Optional[Dict[str, Any]] = None
    azure_config: Optional[Dict[str, Any]] = None
    cache_ttl_seconds: int = 300
    audit_enabled: bool = True
    secure_delete_enabled: bool = True


class SecretValue(BaseModel):
    """Secure container for secret values"""

    value: SecretStr
    metadata: SecretMetadata
    encrypted: bool = False

    class Config:
        json_encoders = {SecretStr: lambda v: v.get_secret_value() if v else None}


class ISecretsProvider(ABC):
    """Interface for secret providers"""

    @abstractmethod
    async def get_secret(self, name: str, version: Optional[str] = None) -> Optional[SecretValue]:
        """Retrieve a secret"""
        pass

    @abstractmethod
    async def set_secret(self, name: str, value: str, metadata: SecretMetadata) -> bool:
        """Store a secret"""
        pass

    @abstractmethod
    async def delete_secret(self, name: str) -> bool:
        """Delete a secret"""
        pass

    @abstractmethod
    async def rotate_secret(self, name: str, new_value: str) -> bool:
        """Rotate a secret"""
        pass

    @abstractmethod
    async def list_secrets(self) -> List[SecretMetadata]:
        """List all secrets"""
        pass


class HashiCorpVaultProvider(ISecretsProvider):
    """HashiCorp Vault provider implementation"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client = hvac.Client(url=config.get("url", "http://localhost:8200"), token=config.get("token"))
        self.mount_point = config.get("mount_point", "secret")
        self.path_prefix = config.get("path_prefix", "ai-teddy")

    async def get_secret(self, name: str, version: Optional[str] = None) -> Optional[SecretValue]:
        """Retrieve secret from Vault"""
        try:
            path = f"{self.path_prefix}/{name}"

            # Get specific version if requested
            if version:
                response = self.client.secrets.kv.read_secret_version(
                    path=path, version=int(version), mount_point=self.mount_point
                )
            else:
                response = self.client.secrets.kv.read_secret_version(path=path, mount_point=self.mount_point)

            if response and "data" in response and "data" in response["data"]:
                data = response["data"]["data"]
                metadata = response["data"]["metadata"]

                return SecretValue(
                    value=SecretStr(data.get("value")),
                    metadata=SecretMetadata(
                        name=name,
                        provider=SecretProvider.HASHICORP_VAULT,
                        secret_type=SecretType[data.get("type", "API_KEY")],
                        created_at=datetime.fromisoformat(metadata.get("created_time")),
                        updated_at=datetime.fromisoformat(metadata.get("updated_time")),
                        version=metadata.get("version", 1),
                        tags=data.get("tags", {}),
                        description=data.get("description"),
                    ),
                )
            return None

        except Exception as e:
            logger.error(f"Failed to get secret from Vault: {e}")
            return None

    async def set_secret(self, name: str, value: str, metadata: SecretMetadata) -> bool:
        """Store secret in Vault"""
        try:
            path = f"{self.path_prefix}/{name}"

            self.client.secrets.kv.create_or_update_secret(
                path=path,
                secret=dict(
                    value=value,
                    type=metadata.secret_type.name,
                    tags=metadata.tags,
                    description=metadata.description,
                    rotation_interval_days=metadata.rotation_interval_days,
                    allowed_environments=metadata.allowed_environments,
                ),
                mount_point=self.mount_point,
            )

            # Add audit entry
            await self._audit_log("set_secret", name, metadata)
            return True

        except Exception as e:
            logger.error(f"Failed to set secret in Vault: {e}")
            return False

    async def delete_secret(self, name: str) -> bool:
        """Delete secret from Vault"""
        try:
            path = f"{self.path_prefix}/{name}"
            self.client.secrets.kv.delete_metadata_and_all_versions(path=path, mount_point=self.mount_point)
            await self._audit_log("delete_secret", name)
            return True
        except Exception as e:
            logger.error(f"Failed to delete secret from Vault: {e}")
            return False

    async def rotate_secret(self, name: str, new_value: str) -> bool:
        """Rotate a secret in Vault"""
        try:
            # Get current secret metadata
            current = await self.get_secret(name)
            if not current:
                return False

            # Update with new value
            current.metadata.last_rotated_at = datetime.now(timezone.utc)
            current.metadata.version += 1

            return await self.set_secret(name, new_value, current.metadata)

        except Exception as e:
            logger.error(f"Failed to rotate secret in Vault: {e}")
            return False

    async def list_secrets(self) -> List[SecretMetadata]:
        """List all secrets in Vault"""
        try:
            response = self.client.secrets.kv.list_secrets(path=self.path_prefix, mount_point=self.mount_point)

            secrets = []
            if response and "data" in response and "keys" in response["data"]:
                for key in response["data"]["keys"]:
                    secret = await self.get_secret(key.rstrip("/"))
                    if secret:
                        secrets.append(secret.metadata)

            return secrets
        except Exception as e:
            logger.error(f"Failed to list secrets from Vault: {e}")
            return []

    async def _audit_log(self, action: str, secret_name: str, metadata: Optional[SecretMetadata] = None):
        """Log audit entry"""
        audit_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "secret_name": secret_name,
            "provider": "HashiCorp Vault",
            "metadata": metadata.__dict__ if metadata else None,
        }
        logger.info(f"Audit: {json.dumps(audit_entry)}")


class AWSSecretsManagerProvider(ISecretsProvider):
    """AWS Secrets Manager provider implementation"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client = boto3.client(
            "secretsmanager",
            region_name=config.get("region", "us-east-1"),
            aws_access_key_id=config.get("access_key_id"),
            aws_secret_access_key=config.get("secret_access_key"),
        )
        self.prefix = config.get("prefix", "ai-teddy")

    async def get_secret(self, name: str, version: Optional[str] = None) -> Optional[SecretValue]:
        """Retrieve secret from AWS Secrets Manager"""
        try:
            secret_id = f"{self.prefix}/{name}"

            params = {"SecretId": secret_id}
            if version:
                params["VersionId"] = version

            response = self.client.get_secret_value(**params)

            if "SecretString" in response:
                secret_data = json.loads(response["SecretString"])

                return SecretValue(
                    value=SecretStr(secret_data.get("value")),
                    metadata=SecretMetadata(
                        name=name,
                        provider=SecretProvider.AWS_SECRETS_MANAGER,
                        secret_type=SecretType[secret_data.get("type", "API_KEY")],
                        created_at=response.get("CreatedDate", datetime.now(timezone.utc)),
                        updated_at=datetime.now(timezone.utc),
                        version=1,
                        tags=secret_data.get("tags", {}),
                        description=response.get("Description"),
                    ),
                )
            return None

        except ClientError as e:
            if e.response["Error"]["Code"] != "ResourceNotFoundException":
                logger.error(f"Failed to get secret from AWS: {e}")
            return None

    async def set_secret(self, name: str, value: str, metadata: SecretMetadata) -> bool:
        """Store secret in AWS Secrets Manager"""
        try:
            secret_id = f"{self.prefix}/{name}"

            secret_data = {
                "value": value,
                "type": metadata.secret_type.name,
                "tags": metadata.tags,
                "rotation_interval_days": metadata.rotation_interval_days,
                "allowed_environments": metadata.allowed_environments,
            }

            try:
                # Try to create new secret
                self.client.create_secret(
                    Name=secret_id,
                    Description=metadata.description or f"AI Teddy Bear secret: {name}",
                    SecretString=json.dumps(secret_data),
                    Tags=[{"Key": k, "Value": v} for k, v in metadata.tags.items()],
                )
            except ClientError as e:
                if e.response["Error"]["Code"] == "ResourceExistsException":
                    # Update existing secret
                    self.client.put_secret_value(SecretId=secret_id, SecretString=json.dumps(secret_data))
                else:
                    raise

            await self._audit_log("set_secret", name, metadata)
            return True

        except Exception as e:
            logger.error(f"Failed to set secret in AWS: {e}")
            return False

    async def delete_secret(self, name: str) -> bool:
        """Delete secret from AWS Secrets Manager"""
        try:
            secret_id = f"{self.prefix}/{name}"
            self.client.delete_secret(
                SecretId=secret_id, ForceDeleteWithoutRecovery=self.config.get("force_delete", False)
            )
            await self._audit_log("delete_secret", name)
            return True
        except Exception as e:
            logger.error(f"Failed to delete secret from AWS: {e}")
            return False

    async def rotate_secret(self, name: str, new_value: str) -> bool:
        """Rotate a secret in AWS Secrets Manager"""
        try:
            current = await self.get_secret(name)
            if not current:
                return False

            current.metadata.last_rotated_at = datetime.now(timezone.utc)
            return await self.set_secret(name, new_value, current.metadata)

        except Exception as e:
            logger.error(f"Failed to rotate secret in AWS: {e}")
            return False

    async def list_secrets(self) -> List[SecretMetadata]:
        """List all secrets in AWS Secrets Manager"""
        try:
            secrets = []
            paginator = self.client.get_paginator("list_secrets")

            for page in paginator.paginate():
                for secret in page["SecretList"]:
                    if secret["Name"].startswith(self.prefix):
                        name = secret["Name"].replace(f"{self.prefix}/", "")
                        secret_value = await self.get_secret(name)
                        if secret_value:
                            secrets.append(secret_value.metadata)

            return secrets
        except Exception as e:
            logger.error(f"Failed to list secrets from AWS: {e}")
            return []

    async def _audit_log(self, action: str, secret_name: str, metadata: Optional[SecretMetadata] = None):
        """Log audit entry"""
        audit_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "secret_name": secret_name,
            "provider": "AWS Secrets Manager",
            "metadata": metadata.__dict__ if metadata else None,
        }
        logger.info(f"Audit: {json.dumps(audit_entry)}")


class LocalEncryptedProvider(ISecretsProvider):
    """Local encrypted secrets provider for development"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.secrets_dir = Path(config.get("secrets_dir", "./secrets"))
        self.secrets_dir.mkdir(parents=True, exist_ok=True)
        self.encryption_key = self._get_or_create_key()
        self.fernet = Fernet(self.encryption_key)

    def _get_or_create_key(self) -> bytes:
        """Get or create encryption key"""
        key_file = self.secrets_dir / ".encryption_key"

        if key_file.exists():
            with open(key_file, "rb") as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, "wb") as f:
                f.write(key)
            # Set restrictive permissions
            os.chmod(key_file, 0o600)
            return key

    async def get_secret(self, name: str, version: Optional[str] = None) -> Optional[SecretValue]:
        """Get secret from encrypted local storage"""
        try:
            secret_file = self.secrets_dir / f"{name}.secret"

            if not secret_file.exists():
                return None

            async with aiofiles.open(secret_file, "rb") as f:
                encrypted_data = await f.read()

            decrypted_data = self.fernet.decrypt(encrypted_data)
            secret_data = json.loads(decrypted_data.decode())

            return SecretValue(
                value=SecretStr(secret_data["value"]),
                metadata=SecretMetadata(**secret_data["metadata"]),
                encrypted=True,
            )

        except Exception as e:
            logger.error(f"Failed to get local secret: {e}")
            return None

    async def set_secret(self, name: str, value: str, metadata: SecretMetadata) -> bool:
        """Store secret in encrypted local storage"""
        try:
            secret_data = {
                "value": value,
                "metadata": {
                    "name": metadata.name,
                    "provider": metadata.provider.name,
                    "secret_type": metadata.secret_type.name,
                    "created_at": metadata.created_at.isoformat(),
                    "updated_at": metadata.updated_at.isoformat(),
                    "rotation_interval_days": metadata.rotation_interval_days,
                    "last_rotated_at": metadata.last_rotated_at.isoformat() if metadata.last_rotated_at else None,
                    "version": metadata.version,
                    "tags": metadata.tags,
                    "description": metadata.description,
                    "allowed_environments": metadata.allowed_environments,
                    "audit_trail": metadata.audit_trail,
                },
            }

            encrypted_data = self.fernet.encrypt(json.dumps(secret_data).encode())

            secret_file = self.secrets_dir / f"{name}.secret"
            async with aiofiles.open(secret_file, "wb") as f:
                await f.write(encrypted_data)

            # Set restrictive permissions
            os.chmod(secret_file, 0o600)

            await self._audit_log("set_secret", name, metadata)
            return True

        except Exception as e:
            logger.error(f"Failed to set local secret: {e}")
            return False

    async def delete_secret(self, name: str) -> bool:
        """Delete secret from local storage with secure deletion"""
        try:
            secret_file = self.secrets_dir / f"{name}.secret"

            if secret_file.exists():
                # Overwrite with random data before deletion
                if self.config.get("secure_delete", True):
                    file_size = secret_file.stat().st_size
                    async with aiofiles.open(secret_file, "wb") as f:
                        for _ in range(3):  # Triple overwrite
                            await f.write(os.urandom(file_size))
                            await f.flush()
                            os.fsync(f.fileno())

                secret_file.unlink()

            await self._audit_log("delete_secret", name)
            return True

        except Exception as e:
            logger.error(f"Failed to delete local secret: {e}")
            return False

    async def rotate_secret(self, name: str, new_value: str) -> bool:
        """Rotate a local secret"""
        try:
            current = await self.get_secret(name)
            if not current:
                return False

            current.metadata.last_rotated_at = datetime.now(timezone.utc)
            current.metadata.version += 1

            return await self.set_secret(name, new_value, current.metadata)

        except Exception as e:
            logger.error(f"Failed to rotate local secret: {e}")
            return False

    async def list_secrets(self) -> List[SecretMetadata]:
        """List all local secrets"""
        try:
            secrets = []

            for secret_file in self.secrets_dir.glob("*.secret"):
                name = secret_file.stem
                secret = await self.get_secret(name)
                if secret:
                    secrets.append(secret.metadata)

            return secrets
        except Exception as e:
            logger.error(f"Failed to list local secrets: {e}")
            return []

    async def _audit_log(self, action: str, secret_name: str, metadata: Optional[SecretMetadata] = None):
        """Log audit entry"""
        audit_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "secret_name": secret_name,
            "provider": "Local Encrypted",
            "metadata": metadata.__dict__ if metadata else None,
        }
        logger.info(f"Audit: {json.dumps(audit_entry)}")


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
            self.providers[SecretProvider.HASHICORP_VAULT] = HashiCorpVaultProvider(self.config.vault_config)

        if self.config.aws_config:
            self.providers[SecretProvider.AWS_SECRETS_MANAGER] = AWSSecretsManagerProvider(self.config.aws_config)

        # Always have local provider as fallback
        self.providers[SecretProvider.LOCAL_ENCRYPTED] = LocalEncryptedProvider(
            {"secrets_dir": "./secrets", "secure_delete": self.config.secure_delete_enabled}
        )

    async def get_secret(
        self, name: str, provider: Optional[SecretProvider] = None, use_cache: bool = True
    ) -> Optional[str]:
        """Get secret value"""
        try:
            # Check cache first
            if use_cache and name in self.cache:
                cached = self.cache[name]
                # Check if cache is still valid
                cache_age = (datetime.now(timezone.utc) - cached.metadata.updated_at).total_seconds()
                if cache_age < self.config.cache_ttl_seconds:
                    return cached.value.get_secret_value()

            # Get from provider
            provider = provider or self.config.default_provider
            if provider not in self.providers:
                logger.error(f"Provider {provider} not available")
                return None

            secret = await self.providers[provider].get_secret(name)
            if secret:
                # Update cache
                self.cache[name] = secret

                # Check if rotation needed
                if self.config.auto_rotation_enabled:
                    await self._check_rotation_needed(secret)

                return secret.value.get_secret_value()

            return None

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
        self, name: str, new_value: Optional[str] = None, provider: Optional[SecretProvider] = None
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

    async def delete_secret(self, name: str, provider: Optional[SecretProvider] = None) -> bool:
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

    async def list_secrets(self, provider: Optional[SecretProvider] = None) -> List[SecretMetadata]:
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
            logger.warning(f"Secret {metadata.name} needs rotation (last rotated {days_since_rotation} days ago)")

            # Schedule immediate rotation
            if metadata.name not in self.rotation_tasks:
                task = asyncio.create_task(self._rotate_secret_task(metadata.name))
                self.rotation_tasks[metadata.name] = task

    async def _setup_rotation(self, name: str, metadata: SecretMetadata):
        """Setup automatic rotation for a secret"""
        if name in self.rotation_tasks:
            self.rotation_tasks[name].cancel()

        # Schedule rotation
        rotation_delay = metadata.rotation_interval_days * 24 * 3600  # Convert to seconds
        task = asyncio.create_task(self._rotation_scheduler(name, rotation_delay))
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
                logger.info(f"✅ Successfully connected to {provider_type.name}")
            except Exception as e:
                logger.error(f"❌ Failed to connect to {provider_type.name}: {e}")

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


# Factory function
def create_secrets_manager(
    environment: str = "development",
    vault_url: Optional[str] = None,
    vault_token: Optional[str] = None,
    aws_region: Optional[str] = None,
) -> SecretsManager:
    """Create a configured secrets manager instance"""

    config = SecretConfig(
        default_provider=SecretProvider.HASHICORP_VAULT if vault_url else SecretProvider.LOCAL_ENCRYPTED,
        auto_rotation_enabled=environment == "production",
        rotation_check_interval_hours=24 if environment == "production" else 168,  # Weekly in dev
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
        config.aws_config = {"region": aws_region, "prefix": f"ai-teddy/{environment}"}

    return SecretsManager(config)
