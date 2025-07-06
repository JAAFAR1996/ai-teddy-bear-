"""
Mixin for caching logic in SQLAlchemy repositories.
"""
import logging
from typing import Dict, Optional, TypeVar

T = TypeVar("T")
logger = logging.getLogger(__name__)


class CachingMixin:
    """A mixin to add in-memory caching capabilities to a repository."""

    def __init__(self, enable_caching: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enable_caching = enable_caching
        self._cache: Dict[str, T] = {} if enable_caching else None

        # Performance monitoring for cache
        self._cache_hits = 0
        self._cache_misses = 0

        if enable_caching:
            logger.info(
                "In-memory cache enabled for this repository instance.")

    def _cache_get(self, key: str) -> Optional[T]:
        """Gets an entity from the cache if caching is enabled."""
        if not self.enable_caching or self._cache is None:
            return None

        entity = self._cache.get(key)
        if entity:
            self._cache_hits += 1
            logger.debug(f"Cache HIT for key: {key}")
            return entity

        self._cache_misses += 1
        logger.debug(f"Cache MISS for key: {key}")
        return None

    def _cache_put(self, key: str, entity: T) -> None:
        """Puts an entity into the cache if caching is enabled."""
        if self.enable_caching and self._cache is not None:
            self._cache[key] = entity
            logger.debug(f"Cached entity with key: {key}")

    def _cache_remove(self, key: str) -> None:
        """Removes an entity from the cache if caching is enabled."""
        if self.enable_caching and self._cache is not None and key in self._cache:
            del self._cache[key]
            logger.debug(f"Removed entity with key: {key} from cache")

    def clear_cache(self) -> None:
        """Clears the entire in-memory cache for the repository."""
        if self.enable_caching and self._cache is not None:
            self._cache.clear()
            logger.info("Repository cache has been cleared.")
