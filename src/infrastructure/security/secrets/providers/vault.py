"""
HashiCorp Vault provider implementation.
"""
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import hvac
from pydantic import SecretStr

from ..models import (SecretMetadata, SecretProvider, SecretType,
                      SecretValue)
from .base import ISecretsProvider

logger = logging.getLogger(__name__)


class HashiCorpVaultProvider(ISecretsProvider):
    """HashiCorp Vault provider implementation"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client = hvac.AsyncClient(
            url=config.get("url", "http://localhost:8200"),
            token=config.get("token")
        )
        self.mount_point = config.get("mount_point", "secret")
        self.path_prefix = config.get("path_prefix", "ai-teddy")

    async def get_secret(
        self, name: str, version: Optional[str] = None
    ) -> Optional[SecretValue]:
        """Retrieve secret from Vault"""
        try:
            path = f"{self.path_prefix}/{name}"

            # Get specific version if requested
            if version:
                response = await self.client.secrets.kv.read_secret_version(
                    path=path, version=int(version), mount_point=self.mount_point
                )
            else:
                response = await self.client.secrets.kv.read_secret_version(
                    path=path, mount_point=self.mount_point
                )

            if response and "data" in response and "data" in response["data"]:
                data = response["data"]["data"]
                metadata = response["data"]["metadata"]

                return SecretValue(
                    value=SecretStr(data.get("value")),
                    metadata=SecretMetadata(
                        name=name,
                        provider=SecretProvider.HASHICORP_VAULT,
                        secret_type=SecretType[data.get("type", "API_KEY")],
                        created_at=datetime.fromisoformat(
                            metadata.get("created_time")),
                        updated_at=datetime.fromisoformat(
                            metadata.get("updated_time")),
                        version=metadata.get("version", 1),
                        tags=data.get("tags", {}),
                        description=data.get("description"),
                    ),
                )
            return None

        except Exception as e:
            logger.error(f"Failed to get secret from Vault: {e}")
            return None

    async def set_secret(
            self,
            name: str,
            value: str,
            metadata: SecretMetadata) -> bool:
        """Store secret in Vault"""
        try:
            path = f"{self.path_prefix}/{name}"

            await self.client.secrets.kv.create_or_update_secret(
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
            await self.client.secrets.kv.delete_metadata_and_all_versions(
                path=path, mount_point=self.mount_point
            )
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
            response = await self.client.secrets.kv.list_secrets(
                path=self.path_prefix, mount_point=self.mount_point
            )

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
            "provider": "HashiCorp Vault",
            "metadata": metadata.__dict__ if metadata else None,
        }
        logger.info(f"Audit: {json.dumps(audit_entry)}")
