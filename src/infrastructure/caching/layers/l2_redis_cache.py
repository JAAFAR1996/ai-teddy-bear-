"""
Level 2 Redis cache implementation.
"""

import gzip
import logging
import pickle
from typing import Any, Dict, Optional

# Caching libraries
try:
    import redis.asyncio as redis
    CACHING_LIBS_AVAILABLE = True
except ImportError:
    CACHING_LIBS_AVAILABLE = False
    redis = None

# Compression
try:
    import lz4.frame
    LZ4_AVAILABLE = True
except ImportError:
    LZ4_AVAILABLE = False

from src.infrastructure.caching.models import CacheConfig
from src.infrastructure.caching.mocks import MockRedisClient


class L2RedisCache:
    """Level 2 Redis cache with clustering support."""

    def __init__(self, config: CacheConfig):
        self.config = config
        self.redis_client: Optional[redis.Redis] = None
        self.logger = logging.getLogger(
            f"{__name__}.{self.__class__.__name__}")

    async def initialize(self):
        """Initialize Redis connection."""
        try:
            if not CACHING_LIBS_AVAILABLE:
                self.logger.warning(
                    "Redis libraries not available, using mock")
                self.redis_client = MockRedisClient()
                return

            if self.config.l2_cluster_mode:
                # Redis Cluster mode
                from redis.asyncio import RedisCluster
                self.redis_client = RedisCluster.from_url(
                    self.config.l2_redis_url,
                    max_connections=self.config.l2_max_connections,
                    decode_responses=False
                )
            else:
                # Single Redis instance
                self.redis_client = redis.from_url(
                    self.config.l2_redis_url,
                    max_connections=self.config.l2_max_connections,
                    decode_responses=False
                )

            # Test connection
            await self.redis_client.ping()
            self.logger.info("L2 Redis cache initialized successfully")

        except Exception as e:
            self.logger.error(f"L2 Redis initialization failed: {e}")
            self.redis_client = MockRedisClient()

    async def get(self, key: str) -> Optional[Any]:
        """Get value from L2 Redis cache."""
        try:
            data = await self.redis_client.get(key)
            if data:
                # Decompress if needed
                if data.startswith(b'COMPRESSED:'):
                    data = self._decompress(data[11:])  # Remove prefix

                # Deserialize
                value = pickle.loads(data)
                self.logger.debug(f"L2 cache hit: {key[:16]}...")
                return value

        except Exception as e:
            self.logger.error(f"L2 cache get error: {e}")

        return None

    async def set(self, key: str, value: Any, ttl: int) -> bool:
        """Set value in L2 Redis cache."""
        try:
            # Serialize
            data = pickle.dumps(value)

            # Compress if enabled and beneficial
            if (self.config.compression_enabled and
                    len(data) > self.config.compression_threshold_bytes):
                compressed_data = self._compress(data)
                if len(compressed_data) < len(data):
                    data = b'COMPRESSED:' + compressed_data

            # Store with TTL
            await self.redis_client.setex(key, ttl, data)
            self.logger.debug(
                f"L2 cache set: {key[:16]}... ({len(data)} bytes)")
            return True

        except Exception as e:
            self.logger.error(f"L2 cache set error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from L2 Redis cache."""
        try:
            result = await self.redis_client.delete(key)
            if result:
                self.logger.debug(f"L2 cache deleted: {key[:16]}...")
            return bool(result)
        except Exception as e:
            self.logger.error(f"L2 cache delete error: {e}")
            return False

    async def clear(self, pattern: str = "*") -> bool:
        """Clear L2 cache with optional pattern."""
        try:
            if pattern == "*":
                await self.redis_client.flushdb()
            else:
                # Delete by pattern
                keys = await self.redis_client.keys(pattern)
                if keys:
                    await self.redis_client.delete(*keys)

            self.logger.info(f"L2 cache cleared (pattern: {pattern})")
            return True
        except Exception as e:
            self.logger.error(f"L2 cache clear error: {e}")
            return False

    def _compress(self, data: bytes) -> bytes:
        """Compress data using available compression."""
        if LZ4_AVAILABLE:
            return lz4.frame.compress(data)
        else:
            return gzip.compress(data)

    def _decompress(self, data: bytes) -> bytes:
        """Decompress data using available compression."""
        try:
            return lz4.frame.decompress(data)
        except Exception:
            try:
                return gzip.decompress(data)
            except Exception:
                return data  # Return as-is if decompression fails

    async def get_stats(self) -> Dict[str, Any]:
        """Get L2 cache statistics."""
        try:
            info = await self.redis_client.info()
            return {
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory", 0),
                "used_memory_human": info.get("used_memory_human", "0B"),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "expired_keys": info.get("expired_keys", 0),
                "evicted_keys": info.get("evicted_keys", 0)
            }
        except Exception:
            return {"status": "error"}
