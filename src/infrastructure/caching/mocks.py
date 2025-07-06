"""
Mock clients for testing the caching system without real dependencies.
"""

import asyncio
import time
from typing import Optional


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
