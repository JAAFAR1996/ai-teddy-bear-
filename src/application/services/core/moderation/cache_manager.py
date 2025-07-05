"""
🗂️ Moderation Cache Manager
Extracted cache management functionality for better cohesion
"""

import hashlib
import time
from typing import Dict, Any, Optional
import logging


class ModerationCache:
    """
    Dedicated cache management for moderation results.
    High cohesion: all methods work with cache data and operations.
    """
    
    def __init__(self, ttl: int = 3600, max_size: int = 1000):
        """Initialize cache with TTL and size limits"""
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = ttl
        self.max_cache_size = max_size
        self.logger = logging.getLogger(__name__)
        
        # Cache-specific stats
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "total_entries": 0
        }
    
    def generate_cache_key(self, content: str, age: int, language: str) -> str:
        """Generate unique cache key for content"""
        key_string = f"{content}_{age}_{language}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached result if valid"""
        if cache_key not in self.cache:
            self.stats["misses"] += 1
            return None
        
        entry = self.cache[cache_key]
        current_time = time.time()
        
        # Check if cache entry has expired
        if current_time - entry["timestamp"] > self.cache_ttl:
            del self.cache[cache_key]
            self.stats["misses"] += 1
            self.stats["evictions"] += 1
            return None
        
        self.stats["hits"] += 1
        self.logger.debug(f"Cache hit for key: {cache_key[:8]}...")
        return entry["result"]
    
    def set(self, cache_key: str, result: Dict[str, Any]) -> None:
        """Store result in cache with TTL"""
        # Cleanup old entries if cache is full
        if len(self.cache) >= self.max_cache_size:
            self._cleanup_expired_entries()
            
            # If still full, remove oldest entry
            if len(self.cache) >= self.max_cache_size:
                oldest_key = min(
                    self.cache.keys(),
                    key=lambda k: self.cache[k]["timestamp"]
                )
                del self.cache[oldest_key]
                self.stats["evictions"] += 1
        
        self.cache[cache_key] = {
            "result": result,
            "timestamp": time.time()
        }
        self.stats["total_entries"] += 1
        self.logger.debug(f"Cached result for key: {cache_key[:8]}...")
    
    def _cleanup_expired_entries(self) -> None:
        """Remove expired cache entries"""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self.cache.items()
            if current_time - entry["timestamp"] > self.cache_ttl
        ]
        
        for key in expired_keys:
            del self.cache[key]
            self.stats["evictions"] += 1
    
    def clear(self) -> None:
        """Clear all cache entries"""
        cleared_count = len(self.cache)
        self.cache.clear()
        self.stats["evictions"] += cleared_count
        self.logger.info(f"Cache cleared: {cleared_count} entries removed")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "cache_size": len(self.cache),
            "max_size": self.max_cache_size,
            "ttl_seconds": self.cache_ttl,
            "hit_rate_percent": round(hit_rate, 2),
            **self.stats
        }
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get detailed cache information"""
        current_time = time.time()
        valid_entries = sum(
            1 for entry in self.cache.values()
            if current_time - entry["timestamp"] <= self.cache_ttl
        )
        
        return {
            "total_entries": len(self.cache),
            "valid_entries": valid_entries,
            "expired_entries": len(self.cache) - valid_entries,
            "memory_usage_estimate": len(str(self.cache)),
            "stats": self.get_stats()
        } 