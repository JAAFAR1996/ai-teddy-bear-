"""
Data models for the multi-layer caching system.
"""

from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


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
