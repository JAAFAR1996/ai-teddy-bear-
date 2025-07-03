"""
Voice Cache Manager
Centralized cache operations for voice services
"""

import hashlib
import logging
from typing import Optional, Any

from core.infrastructure.caching.cache_service import CacheService

logger = logging.getLogger(__name__)


class VoiceCacheManager:
    """Manages caching for voice operations"""
    
    # Cache TTL configurations
    TRANSCRIPTION_TTL = 3600  # 1 hour
    SYNTHESIS_TTL = 86400  # 24 hours
    
    def __init__(self, cache_service: CacheService):
        self.cache_service = cache_service
    
    def generate_transcription_key(self, audio_data: str) -> str:
        """Generate cache key for transcription"""
        # Use first 100 chars for performance
        key_source = audio_data[:100] if len(audio_data) > 100 else audio_data
        return f"transcription_{self._hash_data(key_source)}"
    
    def generate_synthesis_key(
        self, text: str, emotion: str, language: str
    ) -> str:
        """Generate cache key for synthesis"""
        key_source = f"{text}_{emotion}_{language}"
        return f"tts_{self._hash_data(key_source)}"
    
    async def get(self, cache_key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            cached_value = await self.cache_service.get(cache_key)
            if cached_value:
                logger.debug(f"Cache hit for key: {cache_key}")
            return cached_value
        except Exception as e:
            logger.error(f"Cache get error: {str(e)}")
            return None
    
    async def set(
        self, cache_key: str, value: Any, ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache with optional TTL"""
        try:
            await self.cache_service.set(cache_key, value, ttl=ttl)
            logger.debug(f"Cached value for key: {cache_key}")
            return True
        except Exception as e:
            logger.error(f"Cache set error: {str(e)}")
            return False
    
    async def delete(self, cache_key: str) -> bool:
        """Delete value from cache"""
        try:
            await self.cache_service.delete(cache_key)
            logger.debug(f"Deleted cache key: {cache_key}")
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {str(e)}")
            return False
    
    def _hash_data(self, data: str) -> str:
        """Generate hash for cache key"""
        return hashlib.sha256(data.encode()).hexdigest()[:16] 