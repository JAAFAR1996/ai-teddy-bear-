# src/infrastructure/caching/cache_service.py
from typing import Optional, Any, Callable
import aioredis
import pickle
import hashlib
from functools import wraps
import asyncio

class CacheService:
    """Multi-layer caching with Redis"""
    
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self._redis: Optional[aioredis.Redis] = None
        self._local_cache: Dict[str, Any] = {}
        self._cache_stats = {
            "hits": 0,
            "misses": 0,
            "errors": 0
        }
        
    async def connect(self):
        self._redis = await aioredis.from_url(
            self.redis_url,
            encoding="utf-8",
            decode_responses=False
        )
        
    async def get(self, key: str) -> Optional[Any]:
        """Get from cache with local cache fallback"""
        # Try local cache first
        if key in self._local_cache:
            self._cache_stats["hits"] += 1
            return self._local_cache[key]
            
        # Try Redis
        try:
            value = await self._redis.get(key)
            if value:
                self._cache_stats["hits"] += 1
                deserialized = pickle.loads(value)
                # Update local cache
                self._local_cache[key] = deserialized
                return deserialized
        except Exception as e:
            self._cache_stats["errors"] += 1
            
        self._cache_stats["misses"] += 1
        return None
        
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: int = 3600
    ) -> bool:
        """Set in cache with TTL"""
        try:
            serialized = pickle.dumps(value)
            await self._redis.setex(key, ttl, serialized)
            # Update local cache
            self._local_cache[key] = value
            # Schedule local cache cleanup
            asyncio.create_task(self._cleanup_local_cache(key, ttl))
            return True
        except Exception as e:
            self._cache_stats["errors"] += 1
            return False
            
    async def _cleanup_local_cache(self, key: str, ttl: int):
        """Remove from local cache after TTL"""
        await asyncio.sleep(ttl)
        self._local_cache.pop(key, None)
        
    def cached(self, ttl: int = 3600, key_prefix: str = ""):
        """Decorator for caching function results"""
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = self._generate_cache_key(
                    f"{key_prefix}:{func.__name__}", 
                    args, 
                    kwargs
                )
                
                # Try to get from cache
                cached_result = await self.get(cache_key)
                if cached_result is not None:
                    return cached_result
                    
                # Execute function
                result = await func(*args, **kwargs)
                
                # Cache result
                await self.set(cache_key, result, ttl)
                
                return result
            return wrapper
        return decorator
        
    def _generate_cache_key(
        self, 
        prefix: str, 
        args: tuple, 
        kwargs: dict
    ) -> str:
        """Generate unique cache key"""
        key_data = f"{prefix}:{str(args)}:{str(sorted(kwargs.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()