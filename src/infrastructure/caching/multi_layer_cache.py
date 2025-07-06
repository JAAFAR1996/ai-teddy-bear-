"""
Enterprise-Grade Multi-Layer Caching System for AI Teddy Bear Project.

This module provides advanced multi-layer caching with L1 (memory), L2 (Redis),
and L3 (CDN) layers for optimal performance across different content types
and access patterns.

Integrated with performance_optimizer.py for comprehensive cache management.

Performance Team Implementation - Task 12
Author: Performance Team Lead
"""

import asyncio
import hashlib
import logging
import time
from dataclasses import asdict
from typing import Any, Callable, Dict, List, Optional, Tuple

from src.infrastructure.caching.layers.l1_memory_cache import L1MemoryCache
from src.infrastructure.caching.layers.l2_redis_cache import L2RedisCache
from src.infrastructure.caching.layers.l3_cdn_cache import L3CDNCache
from src.infrastructure.caching.models import (
    CacheConfig,
    CacheLayer,
    CacheMetrics,
    ContentType,
)


class MultiLayerCache:
    """Enterprise-grade multi-layer caching system."""

    def __init__(self, config: Optional[CacheConfig] = None):
        self.config = config or CacheConfig()

        # Initialize cache layers
        self.l1_cache = L1MemoryCache(
            self.config) if self.config.l1_enabled else None
        self.l2_cache = L2RedisCache(
            self.config) if self.config.l2_enabled else None
        self.l3_cache = L3CDNCache(
            self.config) if self.config.l3_enabled else None

        # Performance metrics
        self.metrics = CacheMetrics()

        # Content type configurations
        self.content_configs = self._setup_content_configs()

        # Background tasks
        self.background_tasks = set()

        self.logger = logging.getLogger(
            f"{__name__}.{self.__class__.__name__}")

    async def initialize(self):
        """Initialize all cache layers."""
        try:
            if self.l2_cache:
                await self.l2_cache.initialize()

            # Start background tasks
            if self.config.cache_warming_enabled:
                task = asyncio.create_task(self._cache_warming_task())
                self.background_tasks.add(task)
                task.add_done_callback(self.background_tasks.discard)

            if self.config.metrics_enabled:
                task = asyncio.create_task(self._metrics_collection_task())
                self.background_tasks.add(task)
                task.add_done_callback(self.background_tasks.discard)

            self.logger.info(
                "Multi-layer cache system initialized successfully")

        except Exception as e:
            self.logger.error(f"Cache system initialization failed: {e}")
            raise

    async def get_with_fallback(
        self,
        key: str,
        content_type: ContentType = ContentType.AI_RESPONSE,
        compute_fn: Optional[Callable] = None
    ) -> Optional[Any]:
        """Get value with multi-layer fallback."""
        start_time = time.time()
        self.metrics.total_requests += 1

        try:
            # L1 Memory Cache
            if self.l1_cache:
                l1_start = time.time()
                value = await self.l1_cache.get(key)
                l1_time = (time.time() - l1_start) * 1000
                self.metrics.l1_latency_ms += l1_time

                if value is not None:
                    self.metrics.l1_hits += 1
                    self.metrics.total_latency_ms += (
                        time.time() - start_time) * 1000
                    self.logger.debug(f"Cache hit L1: {key[:16]}...")
                    return value
                else:
                    self.metrics.l1_misses += 1

            # L2 Redis Cache
            if self.l2_cache:
                l2_start = time.time()
                value = await self.l2_cache.get(key)
                l2_time = (time.time() - l2_start) * 1000
                self.metrics.l2_latency_ms += l2_time

                if value is not None:
                    self.metrics.l2_hits += 1

                    # Populate L1 cache
                    if self.l1_cache:
                        config = self.content_configs[content_type]
                        await self.l1_cache.set(
                            key, value, content_type, config['l1_ttl']
                        )

                    self.metrics.total_latency_ms += (
                        time.time() - start_time) * 1000
                    self.logger.debug(f"Cache hit L2: {key[:16]}...")
                    return value
                else:
                    self.metrics.l2_misses += 1

            # L3 CDN Cache (for static content only)
            if (self.l3_cache and
                    content_type in [ContentType.STATIC_ASSETS, ContentType.MODEL_WEIGHTS]):
                l3_start = time.time()
                value = await self.l3_cache.get(key)
                l3_time = (time.time() - l3_start) * 1000
                self.metrics.l3_latency_ms += l3_time

                if value is not None:
                    self.metrics.l3_hits += 1

                    # Populate lower layers
                    await self._populate_lower_layers(key, value, content_type)

                    self.metrics.total_latency_ms += (
                        time.time() - start_time) * 1000
                    self.logger.debug(f"Cache hit L3: {key[:16]}...")
                    return value
                else:
                    self.metrics.l3_misses += 1

            # Compute value if function provided
            if compute_fn:
                self.logger.debug(f"Cache miss, computing: {key[:16]}...")
                value = await compute_fn()

                if value is not None:
                    await self.set_multi_layer(key, value, content_type)

                self.metrics.total_latency_ms += (
                    time.time() - start_time) * 1000
                return value

            # Complete miss
            self.metrics.total_latency_ms += (time.time() - start_time) * 1000
            return None

        except Exception as e:
            self.logger.error(f"Cache get error: {e}")
            self.metrics.errors += 1
            return None

    async def set_multi_layer(
        self,
        key: str,
        value: Any,
        content_type: ContentType = ContentType.AI_RESPONSE
    ) -> bool:
        """Set value across appropriate cache layers."""
        try:
            config = self.content_configs[content_type]
            self.metrics.write_operations += 1

            success = True

            # L1 Memory Cache
            if self.l1_cache and config['use_l1']:
                result = await self.l1_cache.set(
                    key, value, content_type, config['l1_ttl']
                )
                success = success and result

            # L2 Redis Cache
            if self.l2_cache and config['use_l2']:
                if self.config.async_write_enabled:
                    # Async write to L2
                    task = asyncio.create_task(
                        self.l2_cache.set(key, value, config['l2_ttl'])
                    )
                    self.background_tasks.add(task)
                    task.add_done_callback(self.background_tasks.discard)
                else:
                    result = await self.l2_cache.set(key, value, config['l2_ttl'])
                    success = success and result

            # L3 CDN Cache (for static content only)
            if (self.l3_cache and config['use_l3'] and
                    content_type in [ContentType.STATIC_ASSETS, ContentType.MODEL_WEIGHTS]):
                if self.config.async_write_enabled:
                    # Async write to L3
                    task = asyncio.create_task(
                        self.l3_cache.set(key, value, config['l3_ttl'])
                    )
                    self.background_tasks.add(task)
                    task.add_done_callback(self.background_tasks.discard)
                else:
                    result = await self.l3_cache.set(key, value, config['l3_ttl'])
                    success = success and result

            if success:
                self.logger.debug(f"Cache set multi-layer: {key[:16]}...")

            return success

        except Exception as e:
            self.logger.error(f"Cache set error: {e}")
            self.metrics.errors += 1
            return False

    async def invalidate(
        self,
        key: str,
        layers: Optional[List[CacheLayer]] = None
    ) -> bool:
        """Invalidate cache entry across specified layers."""
        if layers is None:
            layers = [CacheLayer.L1_MEMORY,
                      CacheLayer.L2_REDIS, CacheLayer.L3_CDN]

        success = True

        try:
            for layer in layers:
                if layer == CacheLayer.L1_MEMORY and self.l1_cache:
                    result = await self.l1_cache.delete(key)
                    success = success and result

                elif layer == CacheLayer.L2_REDIS and self.l2_cache:
                    result = await self.l2_cache.delete(key)
                    success = success and result

                elif layer == CacheLayer.L3_CDN and self.l3_cache:
                    result = await self.l3_cache.delete(key)
                    success = success and result

            if success:
                self.logger.debug(f"Cache invalidated: {key[:16]}...")

            return success

        except Exception as e:
            self.logger.error(f"Cache invalidation error: {e}")
            return False

    async def warm_cache(
        self,
        keys_and_values: List[Tuple[str, Any, ContentType]]
    ) -> int:
        """Warm cache with predefined key-value pairs."""
        success_count = 0

        self.logger.info(
            f"Warming cache with {len(keys_and_values)} entries...")

        for key, value, content_type in keys_and_values:
            try:
                result = await self.set_multi_layer(key, value, content_type)
                if result:
                    success_count += 1
            except Exception as e:
                self.logger.error(f"Cache warming error for {key}: {e}")

        self.logger.info(
            f"Cache warming completed: {success_count}/{len(keys_and_values)} successful")
        return success_count

    async def _populate_lower_layers(
        self,
        key: str,
        value: Any,
        content_type: ContentType
    ):
        """Populate lower cache layers with value from higher layer."""
        config = self.content_configs[content_type]

        # Populate L2 from L3
        if self.l2_cache and config['use_l2']:
            await self.l2_cache.set(key, value, config['l2_ttl'])

        # Populate L1 from L2/L3
        if self.l1_cache and config['use_l1']:
            await self.l1_cache.set(key, value, content_type, config['l1_ttl'])

    def _setup_content_configs(self) -> Dict[ContentType, Dict[str, Any]]:
        """Setup cache configurations for different content types."""
        return {
            ContentType.AUDIO_TRANSCRIPTION: {
                'use_l1': True, 'l1_ttl': 300,
                'use_l2': True, 'l2_ttl': 3600,
                'use_l3': False, 'l3_ttl': 0
            },
            ContentType.AI_RESPONSE: {
                'use_l1': True, 'l1_ttl': 600,
                'use_l2': True, 'l2_ttl': 3600,
                'use_l3': False, 'l3_ttl': 0
            },
            ContentType.EMOTION_ANALYSIS: {
                'use_l1': True, 'l1_ttl': 300,
                'use_l2': True, 'l2_ttl': 1800,
                'use_l3': False, 'l3_ttl': 0
            },
            ContentType.VOICE_SYNTHESIS: {
                'use_l1': True, 'l1_ttl': 1800,
                'use_l2': True, 'l2_ttl': 86400,
                'use_l3': True, 'l3_ttl': 604800
            },
            ContentType.STATIC_ASSETS: {
                'use_l1': True, 'l1_ttl': 3600,
                'use_l2': True, 'l2_ttl': 86400,
                'use_l3': True, 'l3_ttl': 2592000  # 30 days
            },
            ContentType.USER_SESSION: {
                'use_l1': True, 'l1_ttl': 300,
                'use_l2': True, 'l2_ttl': 1800,
                'use_l3': False, 'l3_ttl': 0
            },
            ContentType.MODEL_WEIGHTS: {
                'use_l1': False, 'l1_ttl': 0,
                'use_l2': True, 'l2_ttl': 86400,
                'use_l3': True, 'l3_ttl': 604800
            },
            ContentType.CONFIGURATION: {
                'use_l1': True, 'l1_ttl': 3600,
                'use_l2': True, 'l2_ttl': 86400,
                'use_l3': True, 'l3_ttl': 604800
            }
        }

    async def _cache_warming_task(self):
        """Background task for cache warming."""
        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes

                # Example: Warm frequently accessed configurations
                config_keys = [
                    ("system_config", {"version": "1.0", "features": [
                     "ai", "voice"]}, ContentType.CONFIGURATION),
                    ("model_info", {"whisper": "base",
                     "emotion": "v1.0"}, ContentType.CONFIGURATION)
                ]

                await self.warm_cache(config_keys)

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Cache warming task error: {e}")

    async def _metrics_collection_task(self):
        """Background task for metrics collection."""
        while True:
            try:
                await asyncio.sleep(60)  # Collect every minute

                # Update memory usage
                if self.l1_cache:
                    stats = self.l1_cache.get_stats()
                    self.metrics.memory_usage_mb = stats['size_bytes'] / (
                        1024 * 1024)

                # Update timestamp
                self.metrics.last_updated = datetime.now()

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Metrics collection error: {e}")

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive cache performance metrics."""
        metrics_dict = asdict(self.metrics)

        # Add derived metrics
        metrics_dict.update({
            "hit_rate_by_layer": {
                "l1": self.metrics.l1_hits / max(1, self.metrics.l1_hits + self.metrics.l1_misses),
                "l2": self.metrics.l2_hits / max(1, self.metrics.l2_hits + self.metrics.l2_misses),
                "l3": self.metrics.l3_hits / max(1, self.metrics.l3_hits + self.metrics.l3_misses)
            },
            "latency_by_layer": {
                "l1_avg_ms": self.metrics.l1_latency_ms / max(1, self.metrics.l1_hits + self.metrics.l1_misses),
                "l2_avg_ms": self.metrics.l2_latency_ms / max(1, self.metrics.l2_hits + self.metrics.l2_misses),
                "l3_avg_ms": self.metrics.l3_latency_ms / max(1, self.metrics.l3_hits + self.metrics.l3_misses)
            },
            "cache_efficiency": {
                "total_hit_rate": self.metrics.hit_rate,
                "write_success_rate": (self.metrics.write_operations - self.metrics.errors) / max(1, self.metrics.write_operations),
                "error_rate": self.metrics.errors / max(1, self.metrics.total_requests)
            }
        })

        # Add layer statistics
        if self.l1_cache:
            metrics_dict["l1_stats"] = self.l1_cache.get_stats()

        return metrics_dict

    def cached(
        self,
        content_type: ContentType = ContentType.AI_RESPONSE,
        ttl_override: Optional[int] = None,
        key_prefix: str = ""
    ):
        """Decorator for caching function results."""
        def decorator(func):
            async def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = self._generate_cache_key(
                    f"{key_prefix}:{func.__name__}",
                    args,
                    kwargs
                )

                # Try to get from cache
                cached_result = await self.get_with_fallback(
                    cache_key,
                    content_type
                )

                if cached_result is not None:
                    return cached_result

                # Execute function
                result = await func(*args, **kwargs)

                # Cache result
                await self.set_multi_layer(cache_key, result, content_type)

                return result

            return wrapper
        return decorator

    def _generate_cache_key(
        self,
        prefix: str,
        args: tuple,
        kwargs: dict
    ) -> str:
        """Generate unique cache key."""
        key_data = f"{prefix}:{str(args)}:{str(sorted(kwargs.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()

    async def cleanup(self):
        """Cleanup cache system resources."""
        try:
            # Cancel background tasks
            for task in self.background_tasks:
                task.cancel()

            if self.background_tasks:
                await asyncio.gather(*self.background_tasks, return_exceptions=True)

            # Close Redis connections
            if self.l2_cache and self.l2_cache.redis_client and hasattr(self.l2_cache.redis_client, 'close'):
                await self.l2_cache.redis_client.close()

            self.logger.info("Multi-layer cache cleanup completed")

        except Exception as e:
            self.logger.error(f"Cache cleanup error: {e}")
            raise
