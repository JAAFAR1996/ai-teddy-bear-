"""
💾 LLM Response Cache Service
خدمة التخزين المؤقت لاستجابات LLM - مستخرجة من الملف الأساسي

✅ Single Responsibility: Response caching only
✅ Redis + Local cache hybrid approach
✅ Automatic cache expiration and cleanup
✅ Easy to test and maintain
"""

import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import List, Optional
from enum import Enum

try:
    import redis.asyncio as aioredis
except ImportError:
    aioredis = None


# Mock classes for standalone operation
class LLMProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic" 
    GOOGLE = "google"


class ModelConfig:
    """Mock model config for caching"""
    def __init__(self, provider=None, model_name="", max_tokens=150, temperature=0.7, **kwargs):
        self.provider = provider
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        for k, v in kwargs.items():
            setattr(self, k, v)
    
    def __dict__(self):
        return {
            "provider": str(self.provider) if self.provider else None,
            "model_name": self.model_name,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature
        }


class Message:
    """Mock message class for caching"""
    def __init__(self, content="", role="user", **kwargs):
        self.content = content
        self.role = role
        for k, v in kwargs.items():
            setattr(self, k, v)
    
    def __dict__(self):
        return {"content": self.content, "role": self.role}


class LLMResponseCache:
    """
    مسؤولية واحدة: إدارة cache للـ LLM responses
    Extracted from main factory to achieve High Cohesion
    """

    def __init__(self, redis_url: Optional[str] = None, ttl: int = 3600, max_size: int = 1000):
        self.redis_url = redis_url
        self.redis_client = None
        self.local_cache = {}
        self.cache_ttl = ttl
        self.max_size = max_size
        self.logger = logging.getLogger(self.__class__.__name__)

    async def connect(self):
        """Connect to Redis if available"""
        if self.redis_url and aioredis:
            try:
                self.redis_client = await aioredis.create_redis_pool(self.redis_url)
                self.logger.info("Connected to Redis cache")
            except Exception as e:
                self.logger.warning(f"Failed to connect to Redis: {e}")

    async def get(self, key: str) -> Optional[str]:
        """Get cached response"""
        # Try Redis first
        redis_value = await self._try_redis_get(key)
        if redis_value:
            return redis_value
        
        # Fallback to local cache
        return self._try_local_get(key)
    
    async def _try_redis_get(self, key: str) -> Optional[str]:
        """Try to get value from Redis"""
        if not self.redis_client:
            return None
        
        try:
            value = await self.redis_client.get(key)
            return value.decode('utf-8') if value else None
        except Exception:
            return None
    
    def _try_local_get(self, key: str) -> Optional[str]:
        """Try to get value from local cache"""
        if key not in self.local_cache:
            return None
        
        value, expiry = self.local_cache[key]
        
        if self._is_cache_valid(expiry):
            return value
        else:
            self._remove_expired_cache(key)
            return None
    
    def _is_cache_valid(self, expiry: datetime) -> bool:
        """Check if cache entry is still valid"""
        return datetime.now() < expiry
    
    def _remove_expired_cache(self, key: str) -> None:
        """Remove expired cache entry"""
        self.local_cache.pop(key, None)

    async def set(self, key: str, value: str):
        """Set cached response"""
        if self.redis_client:
            try:
                await self.redis_client.setex(key, self.cache_ttl, value)
            except Exception:
                pass

        # Set in local cache
        self._set_local_cache(key, value)
    
    def _set_local_cache(self, key: str, value: str) -> None:
        """Set value in local cache with size management"""
        if len(self.local_cache) >= self.max_size:
            # Remove oldest entry
            oldest_key = next(iter(self.local_cache))
            del self.local_cache[oldest_key]
        
        expiry = datetime.now() + timedelta(seconds=self.cache_ttl)
        self.local_cache[key] = (value, expiry)

    def generate_key(self, messages: List[Message], model_config: ModelConfig) -> str:
        """Generate cache key for messages and config"""
        content = json.dumps([msg.__dict__() for msg in messages], sort_keys=True)
        config_hash = hashlib.md5(json.dumps(model_config.__dict__(), sort_keys=True).encode()).hexdigest()
        return f"llm:{hashlib.md5(content.encode()).hexdigest()}:{config_hash}"
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        return {
            "local_cache_size": len(self.local_cache),
            "redis_connected": self.redis_client is not None,
            "cache_ttl": self.cache_ttl,
            "max_size": self.max_size
        } 