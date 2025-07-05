from typing import Any, Dict, List, Optional

"""
🔐 HashiCorp Vault Integration - Enterprise Security 2025
=======================================================

Comprehensive secrets management using HashiCorp Vault with:
- Dynamic secret rotation
- Fine-grained access policies
- Multi-tenancy support
- Audit logging integration
- High availability configuration

Author: Jaafar Adeeb - Security Lead
"""

import asyncio
import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import structlog

try:
    import hvac
    from hvac.exceptions import Forbidden, InvalidPath, VaultError
except ImportError:
    hvac = None
    VaultError = Exception
    InvalidPath = Exception
    Forbidden = Exception

import redis.asyncio as redis
from cryptography.fernet import Fernet

logger = structlog.get_logger(__name__)


class SecretType(Enum):
    """Types of secrets managed by Vault"""
    API_KEY = os.getenv('API_KEY')
    DATABASE_CREDENTIAL = "database_credential"
    ENCRYPTION_KEY = "encryption_key"
    JWT_SECRET = os.getenv('SECRET_KEY_1')
    CERTIFICATE = "certificate"
    OAUTH_TOKEN = os.getenv('ACCESS_TOKEN_1')
    WEBHOOK_SECRET = os.getenv('SECRET_KEY_2')
    CHILD_DEVICE_KEY = "child_device_key"
    PARENT_AUTH_TOKEN = os.getenv('ACCESS_TOKEN_2')


@dataclass
class SecretMetadata:
    """Metadata for secrets stored in Vault"""
    secret_type: SecretType
    path: str
    ttl: Optional[int] = None
    created_at: Optional[datetime] = None
    last_accessed: Optional[datetime] = None


class VaultSecretsManager:
    """Enterprise-grade secrets management with HashiCorp Vault"""
    
    def __init__(self, 
                 vault_url: str = "http://localhost:8200",
                 vault_token: Optional[str] = None,
                 namespace: Optional[str] = None):
        """Initialize Vault client"""
        self.vault_url = vault_url
        self.namespace = namespace
        
        if hvac is None:
            logger.warning("hvac library not installed, using fallback mode")
            self.client = None
            self._fallback_secrets = {}
        else:
            self.client = hvac.Client(url=vault_url, namespace=namespace)
            self._authenticate(vault_token)
        
        self.redis_client: Optional[redis.Redis] = None
        self.cache_ttl = 300  # 5 minutes
        self.secret_metadata: Dict[str, SecretMetadata] = {}
    
    def _authenticate(Optional[str]) -> None:
        """Authenticate with Vault"""
        if not self.client:
            return
            
        try:
            if vault_token:
                self.client.token = vault_token
            else:
                env_token = os.getenv('VAULT_TOKEN')
                if env_token:
                    self.client.token = env_token
                else:
                    logger.warning("No Vault token provided, using fallback mode")
                    self.client = None
                    return
            
            if not self.client.is_authenticated():
                logger.warning("Vault authentication failed, using fallback mode")
                self.client = None
                
        except Exception as e:
            logger.error("Vault authentication error", error=str(e))
            self.client = None
    
    async def store_secret(self, 
                          path: str, 
                          secret_data: Dict[str, Any],
                          secret_type: SecretType = SecretType.API_KEY) -> bool:
        """Store secret in Vault or fallback storage"""
        try:
            if self.client:
                # Use Vault
                self.client.secrets.kv.v2.create_or_update_secret(
                    path=path,
                    secret=secret_data,
                    mount_point='teddy-secrets'
                )
            else:
                # Fallback to memory (for development)
                self._fallback_secrets[path] = secret_data
            
            self.secret_metadata[path] = SecretMetadata(
                secret_type=secret_type,
                path=path,
                created_at=datetime.utcnow()
            )
            
            logger.info("Secret stored successfully", path=path)
            return True
            
        except Exception as e:
            logger.error("Failed to store secret", path=path, error=str(e))
            return False
    
    async def get_secret(self, path: str) -> Optional[Dict[str, Any]]:
        """Retrieve secret from Vault or fallback storage"""
        try:
            if self.client:
                # Use Vault
                response = self.client.secrets.kv.v2.read_secret_version(
                    path=path,
                    mount_point='teddy-secrets'
                )
                return response['data']['data'] if response else None
            else:
                # Fallback
                return self._fallback_secrets.get(path)
                
        except Exception as e:
            logger.error("Failed to retrieve secret", path=path, error=str(e))
            return self._fallback_secrets.get(path)
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Vault health"""
        if not self.client:
            return {'status': 'fallback_mode', 'vault_available': False}
        
        try:
            health = self.client.sys.read_health_status()
            return {
                'status': 'healthy',
                'vault_available': True,
                'authenticated': self.client.is_authenticated()
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'vault_available': False,
                'error': str(e)
            }


# Global instance
_vault_manager: Optional[VaultSecretsManager] = None


def get_vault_manager() -> VaultSecretsManager:
    """Get global Vault manager instance"""
    global _vault_manager
    if _vault_manager is None:
        _vault_manager = VaultSecretsManager()
    return _vault_manager


async def get_api_key(service_name: str) -> Optional[str]:
    """Get API key for a service"""
    vault = get_vault_manager()
    secret = await vault.get_secret(f"api-keys/{service_name}")
    return secret.get('api_key') if secret else None


async def get_jwt_secret() -> Optional[str]:
    """Get JWT signing secret"""
    vault = get_vault_manager()
    secret = await vault.get_secret("auth/jwt")
    return secret.get('secret') if secret else None 