import ast

"""
Cache Service
============

Infrastructure service for caching operations.
Supports both in-memory and Redis implementations.
"""
import logging
from abc import ABC, abstractmethod
from typing import Any, Optional

import redis


class CacheInterface(ABC):
    """Interface for cache implementations"""

    @abstractmethod
    def get(self, key: str) -> Any:
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> Any:
        pass

    @abstractmethod
    def delete(self, key: str) -> Any:
        pass

    @abstractmethod
    def clear(self) -> Any:
        pass


class InMemoryCache(CacheInterface):
    """Simple in-memory cache implementation"""

    def __init__(self):
        self._cache = {}
        self.logger = logging.getLogger(self.__class__.__name__)

    def get(self, key: str) -> Any:
        """Get value from cache"""
        return self._cache.get(key)

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> Any:
        """Set value in cache (TTL ignored for in-memory)"""
        self._cache[key] = value
        self.logger.debug(f"Cached key: {key}")

    def delete(self, key: str) -> Any:
        """Delete key from cache"""
        self._cache.pop(key, None)
        self.logger.debug(f"Deleted key: {key}")

    def clear(self) -> Any:
        """Clear all cache"""
        self._cache.clear()
        self.logger.info("Cache cleared")


class RedisCache(CacheInterface):
    """Redis-based cache implementation"""

    def __init__(self, redis_url: str):
        self.logger = logging.getLogger(self.__class__.__name__)
        try:
            self._client = redis.from_url(redis_url)
            self._client.ping()
            self.logger.info("Redis cache initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Redis cache: {e}")
            raise

    def get(self, key: str) -> Any:
        """Get value from Redis"""
        try:
            value = self._client.get(key)
            return value.decode() if value else None
        except Exception as e:
            self.logger.error(f"Error getting key {key}: {e}")
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> Any:
        """Set value in Redis with optional TTL"""
        try:
            self._client.set(key, value, ex=ttl)
            self.logger.debug(f"Cached key: {key} (TTL: {ttl})")
        except Exception as e:
            self.logger.error(f"Error setting key {key}: {e}")

    def delete(self, key: str) -> Any:
        """Delete key from Redis"""
        try:
            self._client.delete(key)
            self.logger.debug(f"Deleted key: {key}")
        except Exception as e:
            self.logger.error(f"Error deleting key {key}: {e}")

    def clear(self) -> Any:
        """Clear Redis database (use with caution)"""
        try:
            self._client.flushdb()
            self.logger.warning("Redis database cleared")
        except Exception as e:
            self.logger.error(f"Error clearing Redis: {e}")


class CacheService:
    """Main cache service with fallback mechanism"""

    def __init__(self, redis_url: Optional[str] = None):
        self.logger = logging.getLogger(self.__class__.__name__)
        if redis_url:
            try:
                self.cache = RedisCache(redis_url)
                self.cache_type = "redis"
            except Exception as e:
                self.logger.warning(
                    f"Redis unavailable, falling back to in-memory cache: {e}"
                )
                self.cache = InMemoryCache()
                self.cache_type = "memory"
        else:
            self.cache = InMemoryCache()
            self.cache_type = "memory"
        self.logger.info(
            f"Cache service initialized with {self.cache_type} backend")

    def get_analytics_cache_key(self, child_id: str, period_days: int) -> str:
        """Generate cache key for analytics data"""
        return f"analytics:{child_id}:{period_days}"

    def get_dashboard_cache_key(self, parent_id: str) -> str:
        """Generate cache key for dashboard data"""
        return f"dashboard:{parent_id}"

    def cache_analytics(
            self,
            child_id: str,
            period_days: int,
            analytics_data: dict,
            ttl: int = 300) -> None:
        """Cache analytics data for 5 minutes by default"""
        key = self.get_analytics_cache_key(child_id, period_days)
        self.cache.set(key, str(analytics_data), ttl)

    def get_cached_analytics(
            self,
            child_id: str,
            period_days: int) -> Optional[dict]:
        """Get cached analytics data"""
        key = self.get_analytics_cache_key(child_id, period_days)
        cached = self.cache.get(key)
        if cached:
            try:
                return ast.literal_eval(cached)
            except Exception as e:
                self.logger.error(f"Error deserializing cached analytics: {e}")
        return None

    def invalidate_child_cache(self, child_id: str) -> None:
        """Invalidate all cache entries for a child"""
        for period in [7, 14, 30, 90]:
            key = self.get_analytics_cache_key(child_id, period)
            self.cache.delete(key)
        self.logger.info(f"Invalidated cache for child {child_id}")

    def get_cache_stats(self) -> dict:
        """Get cache statistics"""
        return {"cache_type": self.cache_type, "status": "healthy"}
