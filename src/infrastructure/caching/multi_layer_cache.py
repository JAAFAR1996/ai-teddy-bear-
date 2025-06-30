from typing import Dict, List, Any, Optional

"""
Enterprise-Grade Multi-Layer Caching System for AI Teddy Bear Project.

This module provides advanced multi-layer caching with L1 (memory), L2 (Redis),
and L3 (CDN) layers for optimal performance across different content types
and access patterns.

Performance Team Implementation - Task 12
Author: Performance Team Lead
"""

import asyncio
import logging
import time
import json
import hashlib
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
import pickle
import gzip
import base64
from pathlib import Path

# Caching libraries
try:
    import redis.asyncio as redis
    import aiocache
    from aiocache.serializers import JsonSerializer, PickleSerializer
    CACHING_LIBS_AVAILABLE = True
except ImportError:
    CACHING_LIBS_AVAILABLE = False
    redis = None
    aiocache = None

# HTTP client for CDN
try:
    import aiohttp
    import httpx
    HTTP_CLIENTS_AVAILABLE = True
except ImportError:
    HTTP_CLIENTS_AVAILABLE = False

# Compression
try:
    import lz4.frame
    LZ4_AVAILABLE = True
except ImportError:
    LZ4_AVAILABLE = False

logger = logging.getLogger(__name__)


class CacheLayer(Enum):
    """Cache layer types for multi-layer caching."""
    L1_MEMORY = "l1_memory"       # In-memory, fastest access
    L2_REDIS = "l2_redis"         # Redis cluster, fast network access
    L3_CDN = "l3_cdn"             # CDN/Edge cache, geographic distribution
    L4_DISK = "l4_disk"           # Local disk cache, fallback storage


class CachePolicy(Enum):
    """Cache policies for different content types."""
    WRITE_THROUGH = "write_through"     # Write to all layers immediately
    WRITE_BACK = "write_back"           # Write to L1, async to others
    READ_THROUGH = "read_through"       # Fill lower layers on miss
    CACHE_ASIDE = "cache_aside"         # Manual cache management


class ContentType(Enum):
    """Content types with different caching strategies."""
    AUDIO_TRANSCRIPTION = "audio_transcription"
    AI_RESPONSE = "ai_response"
    EMOTION_ANALYSIS = "emotion_analysis"
    VOICE_SYNTHESIS = "voice_synthesis"
    STATIC_ASSETS = "static_assets"
    USER_SESSION = "user_session"
    MODEL_WEIGHTS = "model_weights"
    CONFIGURATION = "configuration"


@dataclass
class CacheConfig:
    """Configuration for multi-layer cache system."""
    # L1 Memory Cache
    l1_enabled: bool = True
    l1_max_size_mb: int = 256
    l1_ttl_seconds: int = 300
    l1_max_items: int = 10000
    
    # L2 Redis Cache
    l2_enabled: bool = True
    l2_redis_url: str = "redis://localhost:6379"
    l2_ttl_seconds: int = 3600
    l2_max_connections: int = 100
    l2_cluster_mode: bool = False
    
    # L3 CDN Cache
    l3_enabled: bool = True
    l3_cdn_endpoint: str = "https://cdn.teddy-bear.ai"
    l3_ttl_seconds: int = 86400
    l3_api_key: str = ""
    
    # L4 Disk Cache
    l4_enabled: bool = False
    l4_cache_dir: str = "/tmp/teddy_cache"
    l4_max_size_gb: int = 10
    l4_ttl_seconds: int = 604800
    
    # Performance settings
    compression_enabled: bool = True
    compression_threshold_bytes: int = 1024
    async_write_enabled: bool = True
    cache_warming_enabled: bool = True
    metrics_enabled: bool = True


@dataclass
class CacheMetrics:
    """Cache performance metrics."""
    total_requests: int = 0
    l1_hits: int = 0
    l1_misses: int = 0
    l2_hits: int = 0
    l2_misses: int = 0
    l3_hits: int = 0
    l3_misses: int = 0
    l4_hits: int = 0
    l4_misses: int = 0
    
    write_operations: int = 0
    evictions: int = 0
    errors: int = 0
    
    total_latency_ms: float = 0.0
    l1_latency_ms: float = 0.0
    l2_latency_ms: float = 0.0
    l3_latency_ms: float = 0.0
    
    memory_usage_mb: float = 0.0
    disk_usage_mb: float = 0.0
    
    last_updated: datetime = None
    
    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.now()
    
    @property
    def total_hits(self) -> int:
        return self.l1_hits + self.l2_hits + self.l3_hits + self.l4_hits
    
    @property
    def total_misses(self) -> int:
        return self.l1_misses + self.l2_misses + self.l3_misses + self.l4_misses
    
    @property
    def hit_rate(self) -> float:
        total = self.total_hits + self.total_misses
        return self.total_hits / total if total > 0 else 0.0
    
    @property
    def average_latency_ms(self) -> float:
        return self.total_latency_ms / max(1, self.total_requests)


@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    key: str
    value: Any
    content_type: ContentType
    created_at: datetime
    expires_at: datetime
    access_count: int = 0
    last_accessed: datetime = None
    size_bytes: int = 0
    compressed: bool = False
    
    def __post_init__(self):
        if self.last_accessed is None:
            self.last_accessed = self.created_at
    
    @property
    def is_expired(self) -> bool:
        return datetime.now() > self.expires_at
    
    @property
    def age_seconds(self) -> float:
        return (datetime.now() - self.created_at).total_seconds()


class MockCloudflareClient:
    """Mock Cloudflare CDN client for testing."""
    
    def __init__(self, api_key: str = "", endpoint: str = ""):
        self.api_key = api_key
        self.endpoint = endpoint
        self.mock_storage = {}
        
    async def get(self, key: str) -> Optional[bytes]:
        """Mock CDN get operation."""
        await asyncio.sleep(0.05)  # Simulate network latency
        return self.mock_storage.get(key)
    
    async def set(self, key: str, value: bytes, ttl: int = 86400) -> bool:
        """Mock CDN set operation."""
        await asyncio.sleep(0.02)  # Simulate upload latency
        self.mock_storage[key] = value
        return True
    
    async def delete(self, key: str) -> bool:
        """Mock CDN delete operation."""
        await asyncio.sleep(0.01)
        return self.mock_storage.pop(key, None) is not None
    
    async def purge_cache(self, pattern: str = "*") -> bool:
        """Mock cache purge operation."""
        if pattern == "*":
            self.mock_storage.clear()
        return True


class L1MemoryCache:
    """Level 1 in-memory cache with LRU eviction."""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.cache: Dict[str, CacheEntry] = {}
        self.access_order: List[str] = []  # For LRU tracking
        self.current_size_bytes = 0
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
    async def get(self, key: str) -> Optional[Any]:
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
    
    async def set(self, key: str, value: Any, content_type: ContentType, ttl: int) -> bool:
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
            
            self.logger.debug(f"L1 cache set: {key[:16]}... ({size_bytes} bytes)")
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
    logger.error(f"Error in operation: {e}", exc_info=True)json.JSONDecodeError as e:
    logger.error(f"Error in operation: {e}", exc_info=True)            return 1024  # Default estimate
    
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


class L2RedisCache:
    """Level 2 Redis cache with clustering support."""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.redis_client: Optional[redis.Redis] = None
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
    async def initialize(self):
        """Initialize Redis connection."""
        try:
            if not CACHING_LIBS_AVAILABLE:
                self.logger.warning("Redis libraries not available, using mock")
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
            self.logger.debug(f"L2 cache set: {key[:16]}... ({len(data)} bytes)")
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
        if LZ4_AVAILexcept Exception as e:
    logger.error(f"Error in operation: {e}", exc_info=True)           try:
                return lz4.frame.decompress(data)
            except Exceptioexcept Exception as e:
    logger.error(f"Error in operation: {e}", exc_info=True)
    logger.error(f"Error in operation: {e}", exc_info=True)xception as e:
    logger.warning(f"Ignoring error: {e}")
        
        try:
            except Exception as e:
    logger.error(f"Error in operation: {e}", exc_info=True)zip.decompress(data)
        except Exception as e:
    logger.error(f"Error in operation: {e}", exc_info=True)Exception as e:
    logger.error(f"Error in operation: {e}", exc_info=True)            return data  # Return as-is if decompression fails
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get L2 cache statistics."""
        try:
            info = await self.redis_client.info()
            return {
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory", 0),
                "used_memory_human": info.get("used_memory_human", "0B"),
   except IndexError as e:
    logger.error(f"Error in operation: {e}", exc_info=True)      "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "expired_keys": info.get("expired_keys", 0),
                "evicted_keys": info.get("eviexcept IndexError as e:
    logger.errexcept IndexError as e:
    logger.error(f"Error in operation: {e}", exc_info=True)ror in operation: {e}", exc_info=True)s", 0)
            }
        except IndexError as e:
    logger.error(f"Error in operation: {e}", exc_info=True)            return {"status": "error"}


class MockRedisClient:
    """Mock Redis client for testing without Redis dependency."""
    
    def __init__(self):
        self.storage = {}
        self.expiry = {}
    
    async def ping(self):
        return True
    
    async def get(self, key: str) -> Optional[bytes]:
        # Check expiry
        if key in self.expiry and time.time() > self.expiry[key]:
            self.storage.pop(key, None)
            self.expiry.pop(key, None)
            return None
        
        return self.storage.get(key)
    
    async def setex(self, key: str, ttl: int, value: bytes):
        self.storage[key] = value
        self.expiry[key] = time.time() + ttl
        return True
    
    async def delete(self, *keys):
        count = 0
        for key in keys:
            if self.storage.pop(key, None) is not None:
                count += 1
            self.expiry.pop(key, None)
        return count
    
    async def flushdb(self):
        self.storage.clear()
        self.expiry.clear()
        return True
    
    async def keys(self, pattern: str):
        if pattern == "*":
            return list(self.storage.keys())
        # Simple pattern matching
        import fnmatch
        return [k for k in self.storage.keys() if fnmatch.fnmatch(k, pattern)]
    
    async def info(self):
        return {
            "connected_clients": 1,
            "used_memory": sum(len(v) for v in self.storage.values()),
            "used_memory_human": f"{sum(len(v) for v in self.storage.values())}B",
            "keyspace_hits": 0,
            "keyspace_misses": 0,
            "expired_keys": 0,
            "evicted_keys": 0
        }


class L3CDNCache:
    """Level 3 CDN cache for static content."""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.cdn_client = MockCloudflareClient(
            api_key=config.l3_api_key,
            endpoint=config.l3_cdn_endpoint
        )
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
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
                self.logger.debug(f"L3 cache set: {key[:16]}... ({len(data)} bytes)")
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


class MultiLayerCache:
    """Enterprise-grade multi-layer caching system."""
    
    def __init__(self, config: Optional[CacheConfig] = None):
        self.config = config or CacheConfig()
        
        # Initialize cache layers
        self.l1_cache = L1MemoryCache(self.config) if self.config.l1_enabled else None
        self.l2_cache = L2RedisCache(self.config) if self.config.l2_enabled else None
        self.l3_cache = L3CDNCache(self.config) if self.config.l3_enabled else None
        
        # Performance metrics
        self.metrics = CacheMetrics()
        
        # Content type configurations
        self.content_configs = self._setup_content_configs()
        
        # Background tasks
        self.background_tasks = set()
        
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
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
            
            self.logger.info("Multi-layer cache system initialized successfully")
            
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
                    self.metrics.total_latency_ms += (time.time() - start_time) * 1000
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
                    
                    self.metrics.total_latency_ms += (time.time() - start_time) * 1000
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
                    
                    self.metrics.total_latency_ms += (time.time() - start_time) * 1000
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
                
                self.metrics.total_latency_ms += (time.time() - start_time) * 1000
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
            layers = [CacheLayer.L1_MEMORY, CacheLayer.L2_REDIS, CacheLayer.L3_CDN]
        
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
        
        self.logger.info(f"Warming cache with {len(keys_and_values)} entries...")
        
        for key, value, content_type in keys_and_values:
            try:
                result = await self.set_multi_layer(key, value, content_type)
                if result:
                    success_count += 1
            except Exception as e:
                self.logger.error(f"Cache warming error for {key}: {e}")
        
        self.logger.info(f"Cache warming completed: {success_count}/{len(keys_and_values)} successful")
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
                    ("system_config", {"version": "1.0", "features": ["ai", "voice"]}, ContentType.CONFIGURATION),
                    ("model_info", {"whisper": "base", "emotion": "v1.0"}, ContentType.CONFIGURATION)
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
                    self.metrics.memory_usage_mb = stats['size_bytes'] / (1024 * 1024)
                
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
        def decorator(func -> Any: Callable) -> Any:
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