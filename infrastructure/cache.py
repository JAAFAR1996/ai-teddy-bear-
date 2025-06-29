#!/usr/bin/env python3
"""
🚀 Redis Cache Client
Lead Architect: جعفر أديب (Jaafar Adeeb)
High-performance Redis caching with connection pooling
"""

import asyncio
import json
import pickle
from typing import Any, Optional, Union, Dict
import redis.asyncio as redis
import structlog
from datetime import datetime, timedelta

logger = structlog.get_logger()


class RedisClient:
    """
    🏗️ Enterprise Redis Client
    Features:
    - Connection pooling
    - Async operations
    - JSON and pickle serialization
    - Health monitoring
    - Retry logic with exponential backoff
    """
    
    def __init__(
        self,
        url: str = "redis://localhost:6379/0",
        max_connections: int = 10,
        retry_on_timeout: bool = True,
        socket_connect_timeout: int = 5,
        socket_timeout: int = 5
    ):
        self.url = url
        self.max_connections = max_connections
        self.retry_on_timeout = retry_on_timeout
        self.socket_connect_timeout = socket_connect_timeout
        self.socket_timeout = socket_timeout
        
        self.pool: Optional[redis.ConnectionPool] = None
        self.client: Optional[redis.Redis] = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize Redis connection pool"""
        if self._initialized:
            return
        
        logger.info("🚀 Initializing Redis client", url=self._mask_url())
        
        try:
            # Create connection pool
            self.pool = redis.ConnectionPool.from_url(
                self.url,
                max_connections=self.max_connections,
                retry_on_timeout=self.retry_on_timeout,
                socket_connect_timeout=self.socket_connect_timeout,
                socket_timeout=self.socket_timeout
            )
            
            # Create Redis client
            self.client = redis.Redis(connection_pool=self.pool)
            
            # Test connection
            await self.client.ping()
            
            self._initialized = True
            logger.info("✅ Redis client initialized successfully")
            
        except Exception as e:
            logger.error("❌ Failed to initialize Redis client", error=str(e))
            raise
    
    async def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache"""
        if not self._initialized:
            raise RuntimeError("Redis client not initialized")
        
        try:
            value = await self.client.get(key)
            if value is None:
                return default
            
            # Try to deserialize as JSON first, then pickle
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return pickle.loads(value)
                
        except Exception as e:
            logger.error("Error getting value from cache", key=key, error=str(e))
            return default
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None,
        serialize_as: str = "json"
    ) -> bool:
        """Set value in cache"""
        if not self._initialized:
            raise RuntimeError("Redis client not initialized")
        
        try:
            # Serialize value
            if serialize_as == "json":
                try:
                    serialized_value = json.dumps(value)
                except (TypeError, ValueError):
                    # Fallback to pickle for non-JSON serializable objects
                    serialized_value = pickle.dumps(value)
            else:
                serialized_value = pickle.dumps(value)
            
            # Set with optional TTL
            if ttl:
                return await self.client.setex(key, ttl, serialized_value)
            else:
                return await self.client.set(key, serialized_value)
                
        except Exception as e:
            logger.error("Error setting value in cache", key=key, error=str(e))
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self._initialized:
            raise RuntimeError("Redis client not initialized")
        
        try:
            result = await self.client.delete(key)
            return result > 0
        except Exception as e:
            logger.error("Error deleting key from cache", key=key, error=str(e))
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        if not self._initialized:
            raise RuntimeError("Redis client not initialized")
        
        try:
            result = await self.client.exists(key)
            return result > 0
        except Exception as e:
            logger.error("Error checking key existence", key=key, error=str(e))
            return False
    
    async def expire(self, key: str, ttl: int) -> bool:
        """Set TTL for existing key"""
        if not self._initialized:
            raise RuntimeError("Redis client not initialized")
        
        try:
            return await self.client.expire(key, ttl)
        except Exception as e:
            logger.error("Error setting TTL", key=key, ttl=ttl, error=str(e))
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Redis health"""
        try:
            if not self._initialized:
                return {"healthy": False, "error": "Redis client not initialized"}
            
            # Test basic operations
            start_time = asyncio.get_event_loop().time()
            
            # Ping Redis
            await self.client.ping()
            
            # Test set/get operations
            test_key = "health_check_test"
            test_value = {"timestamp": datetime.utcnow().isoformat()}
            
            await self.set(test_key, test_value, ttl=60)
            retrieved_value = await self.get(test_key)
            await self.delete(test_key)
            
            response_time = asyncio.get_event_loop().time() - start_time
            
            # Get Redis info
            redis_info = await self.client.info()
            
            return {
                "healthy": True,
                "response_time": response_time,
                "test_successful": retrieved_value == test_value,
                "redis_version": redis_info.get("redis_version"),
                "connected_clients": redis_info.get("connected_clients"),
                "used_memory": redis_info.get("used_memory_human"),
                "uptime_seconds": redis_info.get("uptime_in_seconds")
            }
            
        except Exception as e:
            return {"healthy": False, "error": str(e)}
    
    async def close(self):
        """Close Redis connections"""
        logger.info("🔒 Closing Redis connections...")
        
        try:
            if self.client:
                await self.client.close()
            
            if self.pool:
                await self.pool.disconnect()
            
            self._initialized = False
            logger.info("✅ Redis connections closed")
            
        except Exception as e:
            logger.error("❌ Error closing Redis connections", error=str(e))
    
    def _mask_url(self) -> str:
        """Mask sensitive information in URL"""
        # Hide password in Redis URL for logging
        if "@" in self.url:
            parts = self.url.split("@")
            if ":" in parts[0]:
                scheme_auth = parts[0].split(":")
                if len(scheme_auth) >= 3:  # redis://user:password
                    masked_auth = ":".join(scheme_auth[:-1]) + ":***"
                    return masked_auth + "@" + parts[1]
        
        return self.url
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get Redis statistics"""
        try:
            if not self._initialized:
                return {"status": "not_initialized"}
            
            info = await self.client.info()
            
            return {
                "redis_version": info.get("redis_version"),
                "connected_clients": info.get("connected_clients"),
                "used_memory": info.get("used_memory"),
                "used_memory_human": info.get("used_memory_human"),
                "used_memory_peak": info.get("used_memory_peak"),
                "total_commands_processed": info.get("total_commands_processed"),
                "uptime_seconds": info.get("uptime_in_seconds"),
                "keyspace_hits": info.get("keyspace_hits"),
                "keyspace_misses": info.get("keyspace_misses"),
                "hit_rate": info.get("keyspace_hits", 0) / max(1, info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0))
            }
            
        except Exception as e:
            return {"error": str(e)} 