"""
Mixin for performance monitoring in SQLAlchemy repositories.
"""
import logging
from typing import Dict

from .caching import CachingMixin

logger = logging.getLogger(__name__)


class PerformanceMixin(CachingMixin):
    """
    A mixin to add performance monitoring capabilities, including
    query counting and cache statistics.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._query_count = 0
        self.model_class = kwargs.get('model_class', 'UnknownModel')

    def get_performance_stats(self) -> Dict[str, any]:
        """
        Retrieves a dictionary of performance statistics, including query counts
        and cache hit/miss ratios.
        """
        cache_hit_ratio = 0.0
        if self.enable_caching and (self._cache_hits + self._cache_misses > 0):
            cache_hit_ratio = self._cache_hits / \
                (self._cache_hits + self._cache_misses)

        stats = {
            "model_class": self.model_class.__name__ if hasattr(self.model_class, '__name__') else str(self.model_class),
            "query_count": self._query_count,
            "caching_enabled": self.enable_caching,
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "cache_hit_ratio": f"{cache_hit_ratio:.2%}",
            "cache_size": len(self._cache) if self._cache is not None else 0,
        }
        logger.info(f"Performance stats for {stats['model_class']}: {stats}")
        return stats

    def reset_performance_stats(self) -> None:
        """Resets all performance counters to zero."""
        self._query_count = 0
        self._cache_hits = 0
        self._cache_misses = 0
        logger.info(
            f"Performance statistics have been reset for {self.model_class.__name__ if hasattr(self.model_class, '__name__') else str(self.model_class)}.")
