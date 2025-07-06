"""
AWS Secrets Manager provider implementation.
"""
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import aiobotocore
from pydantic import SecretStr

from ..models import (SecretMetadata, SecretProvider, SecretType,
                      SecretValue)
from .base import ISecretsProvider

logger = logging.getLogger(__name__)


class AWSSecretsManagerProvider(ISecretsProvider):
    """AWS Secrets Manager provider implementation"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.session = aiobotocore.get_session()
        self.prefix = config.get("prefix", "ai-teddy")

    async def _get_client(self):
        return self.session.create_client(
            "secretsmanager",
            region_name=self.config.get("region", "us-east-1"),
            aws_access_key_id=self.config.get("access_key_id"),
            aws_secret_access_key=self.config.get("secret_access_key"),
        )

    async def get_secret(
        self, name: str, version: Optional[str] = None
    ) -> Optional[SecretValue]:
        """Retrieve secret from AWS Secrets Manager"""
        try:
            secret_id = f"{self.prefix}/{name}"
            async with await self._get_client() as client:
                params = {"SecretId": secret_id}
                if version:
                    params["VersionId"] = version

                response = await client.get_secret_value(**params)

                if "SecretString" in response:
                    secret_data = json.loads(response["SecretString"])

                    return SecretValue(
                        value=SecretStr(secret_data.get("value")),
                        metadata=SecretMetadata(
                            name=name,
                            provider=SecretProvider.AWS_SECRETS_MANAGER,
                            secret_type=SecretType[secret_data.get(
                                "type", "API_KEY")],
                            created_at=response.get(
                                "CreatedDate", datetime.now(timezone.utc)
                            ),
                            updated_at=datetime.now(timezone.utc),
                            version=1,
                            tags=secret_data.get("tags", {}),
                            description=response.get("Description"),
                        ),
                    )
            return None

        except client.exceptions.ResourceNotFoundException:
            return None
        except Exception as e:
            logger.error(f"Failed to get secret from AWS: {e}")
            return None

    async def set_secret(
            self,
            name: str,
            value: str,
            metadata: SecretMetadata) -> bool:
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

            async with await self._get_client() as client:
                try:
                    # Try to create new secret
                    await client.create_secret(
                        Name=secret_id,
                        Description=metadata.description or f"AI Teddy Bear secret: {name}",
                        SecretString=json.dumps(secret_data),
                        Tags=[{"Key": k, "Value": v}
                              for k, v in metadata.tags.items()],
                    )
                except client.exceptions.ResourceExistsException:
                    # Update existing secret
                    await client.put_secret_value(
                        SecretId=secret_id, SecretString=json.dumps(secret_data))

                await self._audit_log("set_secret", name, metadata)
                return True

        except Exception as e:
            logger.error(f"Failed to set secret in AWS: {e}")
            return False

    async def delete_secret(self, name: str) -> bool:
        """Delete secret from AWS Secrets Manager"""
        try:
            secret_id = f"{self.prefix}/{name}"
            async with await self._get_client() as client:
                await client.delete_secret(
                    SecretId=secret_id,
                    ForceDeleteWithoutRecovery=self.config.get(
                        "force_delete",
                        False),
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
            async with await self._get_client() as client:
                paginator = client.get_paginator("list_secrets")

                async for page in paginator.paginate():
                    for secret in page["SecretList"]:
                        if secret["Name"].startswith(self.prefix):
                            name = secret["Name"].replace(
                                f"{self.prefix}/", "")
                            secret_value = await self.get_secret(name)
                            if secret_value:
                                secrets.append(secret_value.metadata)

            return secrets
        except Exception as e:
            logger.error(f"Failed to list secrets from AWS: {e}")
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
            "provider": "AWS Secrets Manager",
            "metadata": metadata.__dict__ if metadata else None,
        }
        logger.info(f"Audit: {json.dumps(audit_entry)}")
