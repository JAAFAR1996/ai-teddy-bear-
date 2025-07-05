"""
🗄️ Simple Cache Service
Memory-only cache service for testing without Redis dependency
"""

import hashlib
import logging
import time
from functools import wraps
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class SimpleCacheService:
    """Simple memory-only cache service for testing"""

    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: Dict[str, tuple] = {}  # key: (value, timestamp, ttl)
        self._stats = {"hits": 0, "misses": 0, "sets": 0, "evictions": 0}
        logger.info(
            f"✅ Simple cache service initialized (max_size: {max_size})")

    async def connect(self):
        """Mock connect method for compatibility"""
        logger.info("📡 Simple cache service connected (memory only)")
        return True

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key in self._cache:
            value, timestamp, ttl = self._cache[key]

            # Check if expired
            if time.time() - timestamp > ttl:
                del self._cache[key]
                self._stats["misses"] += 1
                logger.debug(f"🧹 Cache key expired: {key[:8]}...")
                return None

            self._stats["hits"] += 1
            logger.debug(f"🎯 Cache hit: {key[:8]}...")
            return value

        self._stats["misses"] += 1
        logger.debug(f"❌ Cache miss: {key[:8]}...")
        return None

    async def set(
            self,
            key: str,
            value: Any,
            ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        try:
            if ttl is None:
                ttl = self.default_ttl

            # Evict old entries if cache is full
            if len(self._cache) >= self.max_size:
                await self._evict_oldest()

            self._cache[key] = (value, time.time(), ttl)
            self._stats["sets"] += 1
            logger.debug(f"💾 Cache set: {key[:8]}... (ttl: {ttl}s)")
            return True

        except Exception as e:
            logger.error(f"❌ Cache set failed: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if key in self._cache:
            del self._cache[key]
            logger.debug(f"🗑️ Cache deleted: {key[:8]}...")
            return True
        return False

    async def clear(self) -> bool:
        """Clear all cache"""
        self._cache.clear()
        logger.info("🧹 Cache cleared")
        return True

    async def _evict_oldest(self):
        """Evict oldest cache entry"""
        if not self._cache:
            return

        # Find oldest entry
        oldest_key = min(
            self._cache.keys(), key=lambda k: self._cache[k][1]
        )  # Sort by timestamp

        del self._cache[oldest_key]
        self._stats["evictions"] += 1
        logger.debug(f"🧹 Evicted oldest cache entry: {oldest_key[:8]}...")

    def cached(self, key_prefix: str = "", ttl: Optional[int] = None):
        """Decorator for caching function results"""

        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = self._generate_cache_key(
                    f"{key_prefix}:{func.__name__}", args, kwargs
                )

                # Try to get from cache
                cached_result = await self.get(cache_key)
                if cached_result is not None:
                    return cached_result

                # Execute function
                result = await func(*args, **kwargs)

                # Cache result
                await self.set(cache_key, result, ttl)

                return result

            return wrapper

        return decorator

    def _generate_cache_key(
            self,
            prefix: str,
            args: tuple,
            kwargs: dict) -> str:
        """Generate unique cache key"""
        key_data = f"{prefix}:{str(args)}:{str(sorted(kwargs.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self._stats["hits"] + self._stats["misses"]
        hit_rate = self._stats["hits"] / \
            total_requests if total_requests > 0 else 0

        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "hits": self._stats["hits"],
            "misses": self._stats["misses"],
            "sets": self._stats["sets"],
            "evictions": self._stats["evictions"],
            "hit_rate": hit_rate,
            "total_requests": total_requests,
        }

    async def cleanup_expired(self):
        """Manual cleanup of expired entries"""
        current_time = time.time()
        expired_keys = []

        for key, (_, timestamp, ttl) in self._cache.items():
            if current_time - timestamp > ttl:
                expired_keys.append(key)

        for key in expired_keys:
            del self._cache[key]

        if expired_keys:
            logger.info(
                f"🧹 Cleaned up {len(expired_keys)} expired cache entries")

        return len(expired_keys)


# Alias for compatibility
CacheService = SimpleCacheService
