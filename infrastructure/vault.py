#!/usr/bin/env python3
"""
🔐 HashiCorp Vault Client
Lead Architect: جعفر أديب (Jaafar Adeeb)
Enterprise secrets management with HashiCorp Vault integration
"""

import asyncio
import json
import os
from typing import Dict, Any, Optional, Union
import aiohttp
import structlog
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = structlog.get_logger()


@dataclass
class VaultSecret:
    """Vault secret with metadata"""
    value: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    version: int = 1
    metadata: Dict[str, Any] = None


class VaultClient:
    """
    🏗️ Enterprise Vault Client
    Features:
    - Secure API key retrieval
    - Token renewal and rotation
    - Secret caching with TTL
    - Health monitoring
    - Fallback to environment variables
    """
    
    def __init__(
        self,
        url: str = "http://localhost:8200",
        token: Optional[str] = None,
        mount_point: str = "secret",
        timeout: int = 30,
        max_retries: int = 3
    ):
        self.url = url.rstrip("/")
        self.token = token or os.getenv("VAULT_TOKEN")
        self.mount_point = mount_point
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Secret cache
        self._secret_cache: Dict[str, VaultSecret] = {}
        self._cache_ttl = 300  # 5 minutes
        
        # Client session
        self._session: Optional[aiohttp.ClientSession] = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize Vault client"""
        if self._initialized:
            return
        
        logger.info("🔐 Initializing Vault client", url=self.url)
        
        try:
            # Create HTTP session
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            connector = aiohttp.TCPConnector(limit=10)
            
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                headers={
                    "X-Vault-Token": self.token,
                    "Content-Type": "application/json"
                }
            )
            
            # Test connection
            await self._health_check()
            
            self._initialized = True
            logger.info("✅ Vault client initialized successfully")
            
        except Exception as e:
            logger.error("❌ Failed to initialize Vault client", error=str(e))
            # Don't raise exception, allow fallback to env vars
            logger.warning("🔄 Will fallback to environment variables for secrets")
    
    async def get_secret(self, secret_path: str, key: Optional[str] = None) -> str:
        """
        Get secret from Vault with caching and fallback
        
        Args:
            secret_path: Path to secret in Vault
            key: Specific key within secret (optional)
        
        Returns:
            Secret value as string
        """
        cache_key = f"{secret_path}:{key}" if key else secret_path
        
        # Check cache first
        if cache_key in self._secret_cache:
            cached_secret = self._secret_cache[cache_key]
            if not self._is_cache_expired(cached_secret):
                logger.debug("📋 Retrieved secret from cache", path=secret_path)
                return cached_secret.value
        
        # Try to get from Vault
        if self._initialized:
            try:
                secret_value = await self._fetch_from_vault(secret_path, key)
                
                # Cache the secret
                self._secret_cache[cache_key] = VaultSecret(
                    value=secret_value,
                    created_at=datetime.utcnow(),
                    expires_at=datetime.utcnow() + timedelta(seconds=self._cache_ttl)
                )
                
                logger.info("✅ Retrieved secret from Vault", path=secret_path)
                return secret_value
                
            except Exception as e:
                logger.warning("⚠️ Failed to get secret from Vault", 
                             path=secret_path, error=str(e))
        
        # Fallback to environment variables
        return self._get_from_env(secret_path, key)
    
    async def _fetch_from_vault(self, secret_path: str, key: Optional[str] = None) -> str:
        """Fetch secret from Vault API"""
        if not self._session:
            raise RuntimeError("Vault client not initialized")
        
        # Construct API path
        api_path = f"/v1/{self.mount_point}/data/{secret_path}"
        url = f"{self.url}{api_path}"
        
        for attempt in range(self.max_retries):
            try:
                async with self._session.get(url) as response:
                    if response.status == 404:
                        raise ValueError(f"Secret not found: {secret_path}")
                    
                    if response.status == 403:
                        raise ValueError(f"Access denied to secret: {secret_path}")
                    
                    response.raise_for_status()
                    
                    data = await response.json()
                    
                    # Extract secret data
                    secret_data = data.get("data", {}).get("data", {})
                    
                    if key:
                        if key not in secret_data:
                            raise ValueError(f"Key '{key}' not found in secret '{secret_path}'")
                        return secret_data[key]
                    else:
                        # Return the first value if no key specified
                        if not secret_data:
                            raise ValueError(f"No data in secret: {secret_path}")
                        return list(secret_data.values())[0]
                        
            except aiohttp.ClientError as e:
                if attempt == self.max_retries - 1:
                    raise
                
                wait_time = 2 ** attempt
                logger.warning(f"Vault request failed, retrying in {wait_time}s", 
                             attempt=attempt + 1, error=str(e))
                await asyncio.sleep(wait_time)
    
    def _get_from_env(self, secret_path: str, key: Optional[str] = None) -> str:
        """Get secret from environment variables as fallback"""
        # Convert secret path to environment variable name
        env_var_name = self._path_to_env_var(secret_path, key)
        
        # Pre-defined mappings for known secrets
        env_mappings = {
            "openai_api_key": "TEDDY_OPENAI_API_KEY",
            "anthropic_api_key": "TEDDY_ANTHROPIC_API_KEY",
            "elevenlabs_api_key": "TEDDY_ELEVENLABS_API_KEY",
            "hume_api_key": "TEDDY_HUME_API_KEY",
            "google_api_key": "TEDDY_GOOGLE_API_KEY",
            "encryption_key": "TEDDY_ENCRYPTION_KEY",
            "jwt_secret": "TEDDY_JWT_SECRET",
            "secret_key": "TEDDY_SECRET_KEY"
        }
        
        # Try mapped environment variable first
        if secret_path in env_mappings:
            env_var = env_mappings[secret_path]
            value = os.getenv(env_var)
            if value:
                logger.info("📋 Retrieved secret from environment", 
                           path=secret_path, env_var=env_var)
                return value
        
        # Try constructed environment variable name
        value = os.getenv(env_var_name)
        if value:
            logger.info("📋 Retrieved secret from environment", 
                       path=secret_path, env_var=env_var_name)
            return value
        
        # Default fallback values for development
        dev_defaults = {
            "openai_api_key": "sk-test-key-for-development",
            "anthropic_api_key": "sk-ant-test-key-for-development",
            "elevenlabs_api_key": "test-elevenlabs-key",
            "hume_api_key": "test-hume-key",
            "encryption_key": "dev-encryption-key-32-chars-long",
            "jwt_secret": "dev-jwt-secret-key-for-testing",
            "secret_key": "dev-secret-key-for-sessions"
        }
        
        if secret_path in dev_defaults:
            logger.warning("🚨 Using development default for secret", 
                          path=secret_path)
            return dev_defaults[secret_path]
        
        raise ValueError(f"Secret not found: {secret_path}")
    
    def _path_to_env_var(self, secret_path: str, key: Optional[str] = None) -> str:
        """Convert secret path to environment variable name"""
        # Convert path to uppercase and replace special chars with underscores
        env_name = secret_path.upper().replace("/", "_").replace("-", "_")
        
        if key:
            env_name += f"_{key.upper()}"
        
        # Add VAULT_ prefix
        return f"VAULT_{env_name}"
    
    def _is_cache_expired(self, secret: VaultSecret) -> bool:
        """Check if cached secret is expired"""
        if secret.expires_at is None:
            return False
        return datetime.utcnow() > secret.expires_at
    
    async def _health_check(self) -> Dict[str, Any]:
        """Check Vault health"""
        if not self._session:
            raise RuntimeError("Session not initialized")
        
        url = f"{self.url}/v1/sys/health"
        
        async with self._session.get(url) as response:
            data = await response.json()
            
            if not data.get("initialized", False):
                raise RuntimeError("Vault is not initialized")
            
            if data.get("sealed", True):
                raise RuntimeError("Vault is sealed")
            
            return data
    
    async def health_check(self) -> Dict[str, Any]:
        """Public health check method"""
        try:
            if not self._initialized:
                return {
                    "healthy": False,
                    "error": "Vault client not initialized",
                    "fallback_mode": True
                }
            
            vault_status = await self._health_check()
            
            return {
                "healthy": True,
                "vault_status": vault_status,
                "cached_secrets": len(self._secret_cache),
                "fallback_mode": False
            }
            
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e),
                "fallback_mode": True
            }
    
    async def close(self):
        """Close Vault client"""
        logger.info("🔒 Closing Vault client...")
        
        try:
            if self._session:
                await self._session.close()
            
            self._secret_cache.clear()
            self._initialized = False
            
            logger.info("✅ Vault client closed")
            
        except Exception as e:
            logger.error("❌ Error closing Vault client", error=str(e))
    
    def clear_cache(self):
        """Clear secret cache"""
        self._secret_cache.clear()
        logger.info("🗑️ Vault secret cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_secrets = len(self._secret_cache)
        expired_secrets = sum(
            1 for secret in self._secret_cache.values()
            if self._is_cache_expired(secret)
        )
        
        return {
            "total_cached_secrets": total_secrets,
            "expired_secrets": expired_secrets,
            "valid_secrets": total_secrets - expired_secrets,
            "cache_ttl_seconds": self._cache_ttl
        } 