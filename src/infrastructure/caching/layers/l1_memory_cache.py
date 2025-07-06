"""
Level 1 in-memory cache implementation.
"""

import json
import logging
import pickle
from datetime import datetime, timedelta
from typing import Any, Dict, List

from src.infrastructure.caching.models import CacheConfig, CacheEntry, ContentType


class L1MemoryCache:
    """Level 1 in-memory cache with LRU eviction."""

    def __init__(self, config: CacheConfig):
        self.config = config
        self.cache: Dict[str, CacheEntry] = {}
        self.access_order: List[str] = []  # For LRU tracking
        self.current_size_bytes = 0
        self.logger = logging.getLogger(
            f"{__name__}.{self.__class__.__name__}")

    async def get(self, key: str) -> Any | None:
        """Get value from L1 cache."""
        if key not in self.cache:
            return None

        entry = self.cache[key]

        # Check expiration
        if entry.is_expired:
            await self.delete(key)
            return None

        # Update access statistics
        entry.access_count += 1
        entry.last_accessed = datetime.now()

        # Update LRU order
        if key in self.access_order:
            self.access_order.remove(key)
        self.access_order.append(key)

        self.logger.debug(f"L1 cache hit: {key[:16]}...")
        return entry.value

    async def set(
            self,
            key: str,
            value: Any,
            content_type: ContentType,
            ttl: int) -> bool:
        """Set value in L1 cache."""
        try:
            # Estimate size
            size_bytes = self._estimate_size(value)

            # Check if we need to evict entries
            await self._ensure_capacity(size_bytes)

            # Create cache entry
            expires_at = datetime.now() + timedelta(seconds=ttl)
            entry = CacheEntry(
                key=key,
                value=value,
                content_type=content_type,
                created_at=datetime.now(),
                expires_at=expires_at,
                size_bytes=size_bytes
            )

            # Store entry
            self.cache[key] = entry
            self.current_size_bytes += size_bytes

            # Update access order
            if key in self.access_order:
                self.access_order.remove(key)
            self.access_order.append(key)

            self.logger.debug(
                f"L1 cache set: {key[:16]}... ({size_bytes} bytes)")
            return True

        except Exception as e:
            self.logger.error(f"L1 cache set failed: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from L1 cache."""
        if key in self.cache:
            entry = self.cache.pop(key)
            self.current_size_bytes -= entry.size_bytes

            if key in self.access_order:
                self.access_order.remove(key)

            self.logger.debug(f"L1 cache deleted: {key[:16]}...")
            return True
        return False

    async def clear(self) -> bool:
        """Clear L1 cache."""
        self.cache.clear()
        self.access_order.clear()
        self.current_size_bytes = 0
        self.logger.info("L1 cache cleared")
        return True

    async def _ensure_capacity(self, required_bytes: int):
        """Ensure sufficient capacity by evicting LRU entries."""
        max_size_bytes = self.config.l1_max_size_mb * 1024 * 1024
        max_items = self.config.l1_max_items

        # Evict by size
        while (self.current_size_bytes + required_bytes > max_size_bytes and
               self.access_order):
            lru_key = self.access_order[0]
            await self.delete(lru_key)

        # Evict by count
        while len(self.cache) >= max_items and self.access_order:
            lru_key = self.access_order[0]
            await self.delete(lru_key)

    def _estimate_size(self, value: Any) -> int:
        """Estimate memory size of value."""
        try:
            if isinstance(value, (str, bytes)):
                return len(value)
            elif isinstance(value, (dict, list)):
                return len(json.dumps(value, default=str))
            else:
                return len(pickle.dumps(value))
        except json.JSONDecodeError as e:
            self.logger.error(f"Error in operation: {e}", exc_info=True)
            return 1024  # Default estimate

    def get_stats(self) -> Dict[str, Any]:
        """Get L1 cache statistics."""
        return {
            "size": len(self.cache),
            "max_items": self.config.l1_max_items,
            "size_bytes": self.current_size_bytes,
            "max_size_bytes": self.config.l1_max_size_mb * 1024 * 1024,
            "utilization": self.current_size_bytes / (self.config.l1_max_size_mb * 1024 * 1024),
            "oldest_entry": min((e.created_at for e in self.cache.values()), default=None),
            "newest_entry": max((e.created_at for e in self.cache.values()), default=None)
        }
