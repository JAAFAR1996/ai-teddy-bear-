# Cache module exports for AI Teddy Bear project

try:
    from .simple_cache_service import SimpleCacheService

    SIMPLE_CACHE_AVAILABLE = True
except ImportError:
    SIMPLE_CACHE_AVAILABLE = False

try:
    from .cache_service import CacheService

    CACHE_SERVICE_AVAILABLE = True
except ImportError:
    CACHE_SERVICE_AVAILABLE = False

try:
    from .multi_layer_cache import (
        CacheConfig,
        CacheEntry,
        CacheLayer,
        CacheMetrics,
        CachePolicy,
        ContentType,
        L1MemoryCache,
        L2RedisCache,
        L3CDNCache,
        MultiLayerCache,
    )

    MULTI_LAYER_CACHE_AVAILABLE = True
except ImportError:
    MULTI_LAYER_CACHE_AVAILABLE = False

try:
    from .cache_integration_service import CacheIntegrationService, CacheStrategy, create_cache_integration_service

    CACHE_INTEGRATION_AVAILABLE = True
except ImportError:
    CACHE_INTEGRATION_AVAILABLE = False

__all__ = [
    # Simple cache
    "SimpleCacheService",
    # Basic cache service
    "CacheService",
    # Multi-layer cache system
    "MultiLayerCache",
    "CacheConfig",
    "CacheLayer",
    "CachePolicy",
    "ContentType",
    "CacheMetrics",
    "CacheEntry",
    "L1MemoryCache",
    "L2RedisCache",
    "L3CDNCache",
    # Integration service
    "CacheIntegrationService",
    "CacheStrategy",
    "create_cache_integration_service",
    # Availability flags
    "SIMPLE_CACHE_AVAILABLE",
    "CACHE_SERVICE_AVAILABLE",
    "MULTI_LAYER_CACHE_AVAILABLE",
    "CACHE_INTEGRATION_AVAILABLE",
]
