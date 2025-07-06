"""
Rate limiting service for the security manager.
"""
import time
from typing import Any, Dict, Optional, Tuple

import redis.asyncio as redis


class RateLimitingService:
    """
    Provides advanced rate limiting capabilities using a sliding window algorithm,
    with support for both Redis and in-memory storage as backends.
    """

    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client
        self._memory_store: Dict[str, Dict[str, Any]] = {}
        self.limits = {
            "api_general": {"requests": 100, "window": 60},
            "api_auth": {"requests": 5, "window": 300},  # Stricter for auth
            "websocket": {"connections": 10, "window": 60},
            "audio_upload": {"requests": 20, "window": 60},
        }

    async def check_rate_limit(self, key: str, limit_type: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Checks if a request identified by a key is within the defined rate limit
        for a specific limit type.
        """
        if limit_type not in self.limits:
            return True, {}

        config = self.limits[limit_type]
        full_key = f"rate_limit:{limit_type}:{key}"

        if self.redis_client:
            return await self._check_redis_rate_limit(full_key, config)
        return self._check_memory_rate_limit(full_key, config)

    async def _check_redis_rate_limit(self, key: str, config: Dict[str, int]) -> Tuple[bool, Dict[str, Any]]:
        """Performs a rate limit check using Redis (sliding window)."""
        now = time.time()
        window_start = now - config["window"]

        async with self.redis_client.pipeline(transaction=True) as pipe:
            pipe.zremrangebyscore(key, -1, window_start)
            pipe.zcard(key)
            pipe.zadd(key, {str(now): now})
            pipe.expire(key, config["window"])
            results = await pipe.execute()

        current_count = results[1]

        if current_count > config["requests"]:
            # To get a more accurate retry_after, we need one more query
            oldest_timestamp = await self.redis_client.zrange(key, 0, 0, withscores=True)
            reset_time = oldest_timestamp[0][1] + \
                config["window"] if oldest_timestamp else now
            retry_after = max(0, reset_time - now)

            return False, self._build_limit_info(config, 0, reset_time, retry_after)

        remaining = config["requests"] - current_count
        return True, self._build_limit_info(config, remaining, now + config["window"])

    def _check_memory_rate_limit(self, key: str, config: Dict[str, int]) -> Tuple[bool, Dict[str, Any]]:
        """Performs a rate limit check using in-memory storage (sliding window)."""
        now = time.time()
        window_start = now - config["window"]

        timestamps = self._memory_store.setdefault(key, [])
        # Remove old timestamps
        timestamps = [ts for ts in timestamps if ts > window_start]
        self._memory_store[key] = timestamps

        if len(timestamps) >= config["requests"]:
            reset_time = timestamps[0] + config["window"]
            retry_after = max(0, reset_time - now)
            return False, self._build_limit_info(config, 0, reset_time, retry_after)

        timestamps.append(now)
        remaining = config["requests"] - len(timestamps)
        return True, self._build_limit_info(config, remaining, now + config["window"])

    def _build_limit_info(
        self, config, remaining, reset_time, retry_after=0
    ) -> Dict[str, Any]:
        """Helper to build the rate limit information dictionary."""
        return {
            "limit": config["requests"],
            "remaining": remaining,
            "reset_time": int(reset_time),
            "retry_after": int(retry_after),
        }
