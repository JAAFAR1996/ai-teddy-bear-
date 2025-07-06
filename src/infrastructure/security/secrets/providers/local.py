"""
Local encrypted secrets provider for development.
"""
from ..models import SecretProvider, SecretType
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiofiles
from cryptography.fernet import Fernet
from pydantic import SecretStr

from ..models import SecretMetadata, SecretValue
from .base import ISecretsProvider

logger = logging.getLogger(__name__)


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

    async def get_secret(
        self, name: str, version: Optional[str] = None
    ) -> Optional[SecretValue]:
        """Get secret from encrypted local storage"""
        try:
            secret_file = self.secrets_dir / f"{name}.secret"

            if not secret_file.exists():
                return None

            async with aiofiles.open(secret_file, "rb") as f:
                encrypted_data = await f.read()

            decrypted_data = self.fernet.decrypt(encrypted_data)
            secret_data = json.loads(decrypted_data.decode())

            # The metadata in the file is a dict, so we need to recreate the object
            metadata_dict = secret_data["metadata"]
            metadata_dict["provider"] = SecretProvider[metadata_dict["provider"]]
            metadata_dict["secret_type"] = SecretType[metadata_dict["secret_type"]]
            metadata_dict["created_at"] = datetime.fromisoformat(
                metadata_dict["created_at"])
            metadata_dict["updated_at"] = datetime.fromisoformat(
                metadata_dict["updated_at"])
            if metadata_dict.get("last_rotated_at"):
                metadata_dict["last_rotated_at"] = datetime.fromisoformat(
                    metadata_dict["last_rotated_at"])

            return SecretValue(
                value=SecretStr(secret_data["value"]),
                metadata=SecretMetadata(**metadata_dict),
                encrypted=True,
            )

        except Exception as e:
            logger.error(f"Failed to get local secret: {e}")
            return None

    async def set_secret(
            self,
            name: str,
            value: str,
            metadata: SecretMetadata) -> bool:
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
                    "last_rotated_at": (
                        metadata.last_rotated_at.isoformat()
                        if metadata.last_rotated_at
                        else None
                    ),
                    "version": metadata.version,
                    "tags": metadata.tags,
                    "description": metadata.description,
                    "allowed_environments": metadata.allowed_environments,
                    "audit_trail": metadata.audit_trail,
                },
            }

            encrypted_data = self.fernet.encrypt(
                json.dumps(secret_data).encode())

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

    async def _audit_log(
            self,
            action: str,
            secret_name: str,
            metadata: Optional[SecretMetadata] = None):
        """Log audit entry"""
        audit_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "secret_name": secret_name,
            "provider": "Local Encrypted",
            "metadata": metadata.__dict__ if metadata else None,
        }
        logger.info(f"Audit: {json.dumps(audit_entry)}")
