"""
Level 3 CDN cache implementation.
"""

import logging
import pickle
from typing import Any, Optional

from src.infrastructure.caching.mocks import MockCloudflareClient
from src.infrastructure.caching.models import CacheConfig


class L3CDNCache:
    """Level 3 CDN cache for static content."""

    def __init__(self, config: CacheConfig):
        self.config = config
        self.cdn_client = MockCloudflareClient(
            api_key=config.l3_api_key,
            endpoint=config.l3_cdn_endpoint
        )
        self.logger = logging.getLogger(
            f"{__name__}.{self.__class__.__name__}")

    async def get(self, key: str) -> Optional[Any]:
        """Get value from L3 CDN cache."""
        try:
            data = await self.cdn_client.get(key)
            if data:
                # Deserialize
                value = pickle.loads(data)
                self.logger.debug(f"L3 cache hit: {key[:16]}...")
                return value
        except Exception as e:
            self.logger.error(f"L3 cache get error: {e}")

        return None

    async def set(self, key: str, value: Any, ttl: int) -> bool:
        """Set value in L3 CDN cache."""
        try:
            # Only cache static content in CDN
            data = pickle.dumps(value)
            result = await self.cdn_client.set(key, data, ttl)

            if result:
                self.logger.debug(
                    f"L3 cache set: {key[:16]}... ({len(data)} bytes)")
            return result

        except Exception as e:
            self.logger.error(f"L3 cache set error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from L3 CDN cache."""
        try:
            result = await self.cdn_client.delete(key)
            if result:
                self.logger.debug(f"L3 cache deleted: {key[:16]}...")
            return result
        except Exception as e:
            self.logger.error(f"L3 cache delete error: {e}")
            return False

    async def purge_cache(self, pattern: str = "*") -> bool:
        """Purge CDN cache."""
        try:
            result = await self.cdn_client.purge_cache(pattern)
            self.logger.info(f"L3 cache purged (pattern: {pattern})")
            return result
        except Exception as e:
            self.logger.error(f"L3 cache purge error: {e}")
            return False
