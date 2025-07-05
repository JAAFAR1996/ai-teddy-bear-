import hashlib
import json
import time
from functools import lru_cache
from typing import Dict, Optional

from src.application.services.ai.models.ai_response_models import AIResponseModel
from src.core.domain.entities.child import Child
from src.infrastructure.caching.simple_cache_service import CacheService
import logging

logger = logging.getLogger(__name__)


class CacheManager:
    """Manages caching for the AI service."""

    def __init__(self, cache_service: CacheService):
        self.cache = cache_service
        self.memory_cache: Dict[str, tuple] = {}
        self.cache_ttl = 3600  # 1 hour
        self.max_cache_size = 1000

    @lru_cache(maxsize=1000)
    def get_cache_key(self, text: str, context: str, child_profile: str) -> str:
        """Generate optimized cache key with LRU caching"""
        combined = f"{text}:{context}:{child_profile}"
        return hashlib.sha512(combined.encode()).hexdigest()

    def get_child_profile_key(self, child: Child) -> str:
        """Generate child profile key for caching"""
        return f"{child.name}:{child.age}:{getattr(child, 'learning_level', 'basic')}"

    def check_memory_cache(self, cache_key: str) -> Optional[AIResponseModel]:
        """Check memory cache with TTL validation"""
        if cache_key in self.memory_cache:
            response_dict, timestamp = self.memory_cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                logger.debug(f"🎯 Memory cache hit for key: {cache_key[:8]}...")
                response = AIResponseModel(**response_dict)
                response.cached = True
                return response
            else:
                # Remove expired entry
                del self.memory_cache[cache_key]
                logger.debug(
                    f"🧹 Expired cache entry removed: {cache_key[:8]}...")
        return None

    def store_in_memory_cache(self, cache_key: str, response: AIResponseModel) -> None:
        """Store response in memory cache with size management"""
        if len(self.memory_cache) >= self.max_cache_size:
            sorted_entries = sorted(
                self.memory_cache.items(), key=lambda x: x[1][1])
            entries_to_remove = int(self.max_cache_size * 0.1)
            for key, _ in sorted_entries[:entries_to_remove]:
                del self.memory_cache[key]
            logger.debug(f"🧹 Cleaned {entries_to_remove} old cache entries")

        response_dict = response.to_dict()
        response_dict["cached"] = False
        self.memory_cache[cache_key] = (response_dict, time.time())
        logger.debug(f"💾 Stored in memory cache: {cache_key[:8]}...")

    async def get_cached_response(self, cache_key: str) -> Optional[AIResponseModel]:
        """Gets a response from cache, checking memory first, then persistent."""
        # Check memory cache first (fastest)
        cached_response = self.check_memory_cache(cache_key)
        if cached_response:
            logger.info("🎯 Memory cache hit - response time: <1ms")
            return cached_response

        # Check persistent cache
        persistent_cached = await self.cache.get(f"ai_response_{cache_key}")
        if persistent_cached:
            logger.info("🎯 Persistent cache hit")
            response = AIResponseModel(**json.loads(persistent_cached))
            response.cached = True
            # Store in memory for next time
            self.store_in_memory_cache(cache_key, response)
            return response

        return None

    async def store_response(self, cache_key: str, response: AIResponseModel):
        """Stores a response in both memory and persistent cache."""
        self.store_in_memory_cache(cache_key, response)
        await self.cache.set(
            f"ai_response_{cache_key}",
            json.dumps(response.to_dict()),
            ttl=self.cache_ttl,
        )
