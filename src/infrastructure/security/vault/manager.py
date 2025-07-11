"""
Core Vault Secrets Manager class.
"""
import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import hvac
import redis.asyncio as redis
import structlog
from hvac.exceptions import InvalidPath

from .models import SecretMetadata, SecretType, VaultEngine

logger = structlog.get_logger(__name__)


class VaultSecretsManager:
    """Enterprise-grade secrets management with HashiCorp Vault"""

    def __init__(
        self,
        vault_url: str = "http://localhost:8200",
        vault_token: Optional[str] = None,
        namespace: Optional[str] = None,
        role_id: Optional[str] = None,
        secret_id: Optional[str] = None,
    ):
        """
        Initialize Vault client with multiple authentication methods

        Args:
            vault_url: Vault server URL
            vault_token: Direct token authentication
            namespace: Vault namespace (for Enterprise)
            role_id: AppRole authentication role_id
            secret_id: AppRole authentication secret_id
        """
        self.vault_url = vault_url
        self.namespace = namespace
        self.client = hvac.AsyncClient(url=vault_url, namespace=namespace)

        # Redis for caching (optional)
        self.redis_client: Optional[redis.Redis] = None
        self.cache_ttl = 300  # 5 minutes

        # Secret metadata tracking
        self.secret_metadata: Dict[str, SecretMetadata] = {}

        # Background tasks
        self._rotation_tasks: Dict[str, asyncio.Task] = {}

        # Authentication
        self._authenticate(vault_token, role_id, secret_id)

        # Initialize engines
        self._initialize_engines()

    def _authenticate(
        self,
        vault_token: Optional[str],
        role_id: Optional[str],
        secret_id: Optional[str],
    ):
        """Authenticate with Vault using available methods"""
        try:
            if vault_token:
                self.client.token = vault_token
                logger.info("Vault authenticated with token")
            elif role_id and secret_id:
                auth_response = self.client.auth.approle.login(
                    role_id=role_id, secret_id=secret_id
                )
                self.client.token = auth_response["auth"]["client_token"]
                logger.info("Vault authenticated with AppRole")
            else:
                # Try to get token from environment
                env_token = os.getenv("VAULT_TOKEN")
                if env_token:
                    self.client.token = env_token
                    logger.info("Vault authenticated with environment token")
                else:
                    raise hvac.exceptions.VaultError(
                        "No authentication method provided")

            # Verify authentication
            if not self.client.is_authenticated():
                raise hvac.exceptions.VaultError("Vault authentication failed")

        except Exception as e:
            logger.error("Vault authentication error", error=str(e))
            raise

    def _initialize_engines(self) -> Any:
        """Initialize required secret engines"""
        try:
            # List existing engines
            engines = self.client.sys.list_mounted_secrets_engines()

            # Initialize KV v2 engine for general secrets
            if "teddy-secrets/" not in engines:
                self.client.sys.enable_secrets_engine(
                    backend_type="kv",
                    path="teddy-secrets",
                    options={
                        "version": "2"})
                logger.info("Initialized KV v2 engine: teddy-secrets")

            # Initialize transit engine for encryption
            if "transit/" not in engines:
                self.client.sys.enable_secrets_engine(
                    backend_type="transit", path="transit"
                )
                logger.info("Initialized transit engine")

            # Initialize database engine for dynamic credentials
            if "database/" not in engines:
                self.client.sys.enable_secrets_engine(
                    backend_type="database", path="database"
                )
                logger.info("Initialized database engine")

        except Exception as e:
            logger.warning("Engine initialization warning", error=str(e))

    def _create_secret_payload(
        self,
        secret_data: Dict[str, Any],
        secret_type: SecretType,
        ttl: Optional[int],
        metadata: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Prepare the secret payload with metadata."""
        return {
            "data": secret_data,
            "metadata": {
                "secret_type": secret_type.value,
                "created_at": datetime.utcnow().isoformat(),
                "created_by": self._get_current_user(),
                "ttl": ttl,
                "custom_metadata": metadata or {},
            },
        }

    def _store_local_metadata(
        self, path: str, secret_type: SecretType, ttl: Optional[int]
    ):
        """Store secret metadata locally."""
        self.secret_metadata[path] = SecretMetadata(
            secret_type=secret_type,
            path=path,
            engine=VaultEngine.KV_V2,
            ttl=ttl,
            created_at=datetime.utcnow(),
            created_by=self._get_current_user(),
        )

    def _write_secret_to_vault(self, path: str, secret_payload: Dict[str, Any]):
        """Writes the secret to vault."""
        self.client.secrets.kv.v2.create_or_update_secret(
            path=path, secret=secret_payload, mount_point="teddy-secrets"
        )

    async def store_secret(
        self,
        path: str,
        secret_data: Dict[str, Any],
        secret_type: SecretType = SecretType.API_KEY,
        ttl: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Store secret in Vault with metadata."""
        try:
            secret_payload = self._create_secret_payload(
                secret_data, secret_type, ttl, metadata
            )

            self._write_secret_to_vault(path, secret_payload)
            self._store_local_metadata(path, secret_type, ttl)

            if ttl and ttl > 0:
                await self._schedule_rotation(path, ttl)

            logger.info(
                "Secret stored successfully",
                path=path,
                secret_type=secret_type.value)
            return True

        except Exception as e:
            logger.error("Failed to store secret", path=path, error=str(e))
            return False

    async def _get_from_cache(
        self, path: str, version: Optional[int]
    ) -> Optional[Dict[str, Any]]:
        """Retrieve secret from Redis cache."""
        cache_key = f"vault_secret:{path}:{version or 'latest'}"
        cached_secret = await self.redis_client.get(cache_key)
        if cached_secret:
            logger.debug("Secret retrieved from cache", path=path)
            return json.loads(cached_secret)
        return None

    async def _retrieve_from_vault(
        self, path: str, version: Optional[int]
    ) -> Optional[Dict[str, Any]]:
        """Retrieve secret directly from Vault and update metadata."""
        response = self.client.secrets.kv.v2.read_secret_version(
            path=path, version=version, mount_point="teddy-secrets"
        )
        if not response:
            logger.warning("Secret not found", path=path)
            return None

        secret_data = response["data"]["data"]
        if path in self.secret_metadata:
            self.secret_metadata[path].last_accessed = datetime.utcnow()

        return secret_data

    async def _cache_secret(
        self, path: str, version: Optional[int], secret_data: Dict[str, Any]
    ):
        """Cache the secret in Redis."""
        cache_key = f"vault_secret:{path}:{version or 'latest'}"
        await self.redis_client.setex(
            cache_key, self.cache_ttl, json.dumps(secret_data)
        )

    async def get_secret(
        self, path: str, version: Optional[int] = None, use_cache: bool = True
    ) -> Optional[Dict[str, Any]]:
        """Retrieve secret from Vault with caching."""
        try:
            if use_cache and self.redis_client:
                secret = await self._get_secret_with_cache(path, version)
            else:
                secret = await self._retrieve_from_vault(path, version)

            if secret:
                logger.info("Secret retrieved successfully", path=path)

            return secret

        except Exception as e:
            logger.error("Failed to retrieve secret", path=path, error=str(e))
            return None

    async def _get_secret_with_cache(self, path: str, version: Optional[int]) -> Optional[Dict[str, Any]]:
        """Gets a secret, using the cache if available."""
        cached_secret = await self._get_from_cache(path, version)
        if cached_secret:
            return cached_secret

        secret_data = await self._retrieve_from_vault(path, version)
        if not secret_data:
            return None

        await self._cache_secret(path, version, secret_data)
        return secret_data

    async def rotate_secret(
            self, path: str, new_secret_data: Dict[str, Any]) -> bool:
        """
        Rotate secret with zero-downtime

        Args:
            path: Secret path
            new_secret_data: New secret data

        Returns:
            Success status
        """
        try:
            # Store new version
            success = await self.store_secret(
                path=path,
                secret_data=new_secret_data,
                secret_type=self.secret_metadata.get(
                    path,
                    SecretMetadata(
                        secret_type=SecretType.API_KEY,
                        path=path,
                        engine=VaultEngine.KV_V2,
                    ),
                ).secret_type,
            )

            if success:
                # Invalidate cache
                if self.redis_client:
                    cache_pattern = f"vault_secret:{path}:*"
                    async for key in self.redis_client.scan_iter(match=cache_pattern):
                        await self.redis_client.delete(key)

                logger.info("Secret rotated successfully", path=path)
                return True

            return False

        except Exception as e:
            logger.error("Failed to rotate secret", path=path, error=str(e))
            return False

    async def delete_secret(
        self, path: str, versions: Optional[List[int]] = None
    ) -> bool:
        """
        Delete secret versions

        Args:
            path: Secret path
            versions: Specific versions to delete (None for all)

        Returns:
            Success status
        """
        try:
            if versions:
                # Delete specific versions
                self.client.secrets.kv.v2.delete_secret_versions(
                    path=path, versions=versions, mount_point="teddy-secrets"
                )
            else:
                # Delete all versions (metadata deletion)
                self.client.secrets.kv.v2.delete_metadata_and_all_versions(
                    path=path, mount_point="teddy-secrets"
                )

            # Clean up local metadata
            if path in self.secret_metadata:
                del self.secret_metadata[path]

            # Clean up cache
            if self.redis_client:
                cache_pattern = f"vault_secret:{path}:*"
                async for key in self.redis_client.scan_iter(match=cache_pattern):
                    await self.redis_client.delete(key)

            # Cancel rotation task
            if path in self._rotation_tasks:
                self._rotation_tasks[path].cancel()
                del self._rotation_tasks[path]

            logger.info("Secret deleted successfully", path=path)
            return True

        except Exception as e:
            logger.error("Failed to delete secret", path=path, error=str(e))
            return False

    async def list_secrets(self, path_prefix: str = "") -> List[str]:
        """List all secrets with optional path prefix"""
        try:
            full_path = f"teddy-secrets/metadata/{path_prefix}"
            response = self.client.secrets.kv.v2.list_secrets(
                path=path_prefix, mount_point="teddy-secrets"
            )

            if response and "data" in response and "keys" in response["data"]:
                return response["data"]["keys"]

            return []

        except Exception as e:
            logger.error(
                "Failed to list secrets", path_prefix=path_prefix, error=str(e)
            )
            return []

    # Transit Engine Methods for Encryption

    async def encrypt_data(
        self,
        plaintext: Union[str, bytes],
        key_name: str = "teddy-master-key",
        context: Optional[str] = None,
    ) -> Optional[str]:
        """
        Encrypt data using Vault's transit engine

        Args:
            plaintext: Data to encrypt
            key_name: Encryption key name
            context: Additional context for encryption

        Returns:
            Encrypted data (base64 encoded) or None
        """
        try:
            # Ensure key exists
            await self._ensure_transit_key(key_name)

            # Prepare data
            if isinstance(plaintext, str):
                plaintext = plaintext.encode("utf-8")

            import base64

            plaintext_b64 = base64.b64encode(plaintext).decode("utf-8")

            # Encrypt
            response = self.client.secrets.transit.encrypt_data(
                name=key_name, plaintext=plaintext_b64, context=context
            )

            return response["data"]["ciphertext"]

        except Exception as e:
            logger.error(
                "Failed to encrypt data",
                key_name=key_name,
                error=str(e))
            return None

    async def decrypt_data(
        self,
        ciphertext: str,
        key_name: str = "teddy-master-key",
        context: Optional[str] = None,
    ) -> Optional[bytes]:
        """
        Decrypt data using Vault's transit engine

        Args:
            ciphertext: Encrypted data
            key_name: Encryption key name
            context: Additional context for decryption

        Returns:
            Decrypted data or None
        """
        try:
            response = self.client.secrets.transit.decrypt_data(
                name=key_name, ciphertext=ciphertext, context=context
            )

            import base64

            return base64.b64decode(response["data"]["plaintext"])

        except Exception as e:
            logger.error(
                "Failed to decrypt data",
                key_name=key_name,
                error=str(e))
            return None

    async def _ensure_transit_key(self, key_name: str):
        """Ensure transit encryption key exists"""
        try:
            # Try to read key info
            self.client.secrets.transit.read_key(name=key_name)
        except InvalidPath:
            # Key doesn't exist, create it
            self.client.secrets.transit.create_key(
                name=key_name, key_type="aes256-gcm96"
            )
            logger.info("Created transit encryption key", key_name=key_name)

    async def _schedule_rotation(self, path: str, ttl: int):
        """Schedule automatic secret rotation"""

        async def rotate_task():
            await asyncio.sleep(ttl - 300)  # Rotate 5 minutes before expiry

            # Generate new secret (this would depend on secret type)
            # For now, we'll just log the need for rotation
            logger.warning("Secret rotation needed", path=path)

            # In production, this would trigger the appropriate rotation logic
            # based on the secret type (API key renewal, password generation,
            # etc.)

        task = asyncio.create_task(rotate_task())
        self._rotation_tasks[path] = task

    def _get_current_user(self) -> str:
        """Get current user from token or default"""
        try:
            response = self.client.lookup_token()
            return response.get("data", {}).get("display_name", "system")
        except IndexError as e:
            return "system"

    async def get_database_credentials(
        self, role_name: str
    ) -> Optional[Dict[str, str]]:
        """Get dynamic database credentials"""
        try:
            response = self.client.secrets.database.generate_credentials(
                role=role_name)
            return {
                "username": response["data"]["username"],
                "password": response["data"]["password"],
                "lease_id": response["lease_id"],
                "lease_duration": response["lease_duration"],
            }
        except Exception as e:
            logger.error(
                "Failed to get database credentials",
                role=role_name,
                error=str(e))
            return None

    async def revoke_lease(self, lease_id: str) -> bool:
        """Revoke a dynamic secret lease"""
        try:
            self.client.sys.revoke_lease(lease_id=lease_id)
            logger.info("Lease revoked successfully", lease_id=lease_id)
            return True
        except Exception as e:
            logger.error(
                "Failed to revoke lease",
                lease_id=lease_id,
                error=str(e))
            return False

    def set_redis_client(self, redis_client: redis.Redis) -> None:
        """Set Redis client for caching"""
        self.redis_client = redis_client

    async def health_check(self) -> Dict[str, Any]:
        """Check Vault health and connectivity"""
        try:
            health = self.client.sys.read_health_status()
            return {
                "status": "healthy",
                "vault_version": health.get("version", "unknown"),
                "sealed": health.get("sealed", True),
                "initialized": health.get("initialized", False),
                "auth_status": self.client.is_authenticated(),
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "auth_status": False}
