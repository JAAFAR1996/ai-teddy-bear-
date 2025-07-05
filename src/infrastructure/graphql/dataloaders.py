#!/usr/bin/env python3
"""
🚀 Advanced GraphQL DataLoaders with Performance Optimization
Lead Architect: جعفر أديب (Jaafar Adeeb)
Enterprise-grade DataLoader pattern with intelligent caching and batching
"""

import hashlib
import json
import time
from abc import abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar

try:
    from aiodataloader import DataLoader
except ImportError:
    # Fallback implementation if aiodataloader is not available
    class DataLoader:
        def __init__(self, batch_load_fn, **kwargs):
            self.batch_load_fn = batch_load_fn
            self._batch_size = kwargs.get("max_batch_size", 100)
            self._cache = {}

        async def load(self, key):
            if key in self._cache:
                return self._cache[key]
            result = await self.batch_load_fn([key])
            self._cache[key] = result[0]
            return result[0]

        async def load_many(self, keys):
            missing_keys = [k for k in keys if k not in self._cache]
            if missing_keys:
                results = await self.batch_load_fn(missing_keys)
                for k, r in zip(missing_keys, results):
                    self._cache[k] = r
            return [self._cache[k] for k in keys]


import structlog
from redis.asyncio import Redis

logger = structlog.get_logger()

T = TypeVar("T")
K = TypeVar("K")


@dataclass
class CacheConfig:
    """Cache configuration for DataLoader"""

    ttl: int = 300  # 5 minutes default TTL
    prefix: str = "dataloader"
    serialize_fn: Callable[[Any], str] = json.dumps
    deserialize_fn: Callable[[str], Any] = json.loads
    max_batch_size: int = 100
    cache_miss_threshold: float = 0.1  # 10% cache miss triggers optimization


@dataclass
class LoaderMetrics:
    """DataLoader performance metrics"""

    cache_hits: int = 0
    cache_misses: int = 0
    batch_loads: int = 0
    total_items_loaded: int = 0
    average_batch_size: float = 0.0
    average_load_time: float = 0.0
    last_reset: datetime = field(default_factory=datetime.utcnow)

    @property
    def cache_hit_rate(self) -> float:
        total = self.cache_hits + self.cache_misses
        return self.cache_hits / total if total > 0 else 0.0

    @property
    def cache_miss_rate(self) -> float:
        return 1.0 - self.cache_hit_rate


class BaseDataLoader(DataLoader, Generic[K, T]):
    """
    🏗️ Enterprise Base DataLoader
    Advanced caching, batching, and performance monitoring
    """

    def __init__(
        self,
        repository: Any,
        cache_client: Redis,
        config: CacheConfig = None,
        name: str = "base_loader",
    ):
        self.repository = repository
        self.cache_client = cache_client
        self.config = config or CacheConfig()
        self.name = name
        self.metrics = LoaderMetrics()

        # Initialize parent DataLoader
        super().__init__(
            batch_load_fn=self._batch_load_with_cache,
            max_batch_size=self.config.max_batch_size,
        )

        logger.info(
            "🚀 DataLoader initialized",
            name=self.name,
            max_batch_size=self.config.max_batch_size,
        )

    async def _batch_load_with_cache(self, keys: List[K]) -> List[Optional[T]]:
        """Enhanced batch loading with multi-level caching"""
        start_time = time.time()

        try:
            # Step 1: Check cache for all keys
            cached_results = await self._get_from_cache_batch(keys)
            missing_keys = [
                key for key, result in zip(keys, cached_results) if result is None
            ]

            # Update metrics
            self.metrics.cache_hits += len(keys) - len(missing_keys)
            self.metrics.cache_misses += len(missing_keys)

            # Step 2: Fetch missing data from repository
            db_results = {}
            if missing_keys:
                logger.debug(
                    "📊 Fetching from database",
                    loader=self.name,
                    missing_count=len(missing_keys),
                )

                db_data = await self._fetch_from_repository(missing_keys)
                db_results = {key: data for key, data in zip(missing_keys, db_data)}

                # Step 3: Cache the fetched results
                await self._cache_results_batch(db_results)

            # Step 4: Merge cached and database results
            final_results = []
            for key, cached_result in zip(keys, cached_results):
                if cached_result is not None:
                    final_results.append(cached_result)
                else:
                    final_results.append(db_results.get(key))

            # Update metrics
            self.metrics.batch_loads += 1
            self.metrics.total_items_loaded += len(keys)
            load_time = time.time() - start_time
            self.metrics.average_load_time = (
                self.metrics.average_load_time * (self.metrics.batch_loads - 1)
                + load_time
            ) / self.metrics.batch_loads
            self.metrics.average_batch_size = (
                self.metrics.total_items_loaded / self.metrics.batch_loads
            )

            logger.debug(
                "✅ Batch load completed",
                loader=self.name,
                keys_count=len(keys),
                cache_hits=len(keys) - len(missing_keys),
                db_fetches=len(missing_keys),
                load_time=load_time,
            )

            return final_results

        except Exception as e:
            logger.error(
                "❌ Batch load failed",
                loader=self.name,
                error=str(e),
                keys_count=len(keys),
            )
            # Return None for all keys on error
            return [None] * len(keys)

    async def _get_from_cache_batch(self, keys: List[K]) -> List[Optional[T]]:
        """Get multiple items from cache efficiently"""
        try:
            cache_keys = [self._generate_cache_key(key) for key in keys]
            cached_values = await self.cache_client.mget(cache_keys)

            results = []
            for cached_value in cached_values:
                if cached_value:
                    try:
                        results.append(self.config.deserialize_fn(cached_value))
                    except Exception as e:
                        logger.warning("Cache deserialization failed", error=str(e))
                        results.append(None)
                else:
                    results.append(None)

            return results

        except Exception as e:
            logger.warning("Cache batch get failed", error=str(e))
            return [None] * len(keys)

    async def _cache_results_batch(self, results: Dict[K, T]) -> None:
        """Cache multiple results efficiently"""
        try:
            if not results:
                return

            # Prepare batch cache operation
            cache_data = {}
            for key, data in results.items():
                if data is not None:
                    cache_key = self._generate_cache_key(key)
                    cache_data[cache_key] = self.config.serialize_fn(data)

            if cache_data:
                # Use Redis pipeline for efficient batch operations
                async with self.cache_client.pipeline() as pipe:
                    for cache_key, cache_value in cache_data.items():
                        pipe.setex(cache_key, self.config.ttl, cache_value)
                    await pipe.execute()

                logger.debug(
                    "📋 Cached batch results",
                    loader=self.name,
                    cached_count=len(cache_data),
                )

        except Exception as e:
            logger.warning("Batch cache failed", error=str(e))

    @abstractmethod
    async def _fetch_from_repository(self, keys: List[K]) -> List[Optional[T]]:
        """Fetch data from repository - must be implemented by subclass"""
        pass

    def _generate_cache_key(self, key: K) -> str:
        """Generate cache key for a given key"""
        key_str = str(key)
        key_hash = hashlib.md5(key_str.encode()).hexdigest()[:8]
        return f"{self.config.prefix}:{self.name}:{key_hash}:{key_str}"

    async def get_metrics(self) -> Dict[str, Any]:
        """Get loader performance metrics"""
        return {
            "name": self.name,
            "cache_hit_rate": self.metrics.cache_hit_rate,
            "cache_miss_rate": self.metrics.cache_miss_rate,
            "total_loads": self.metrics.batch_loads,
            "total_items": self.metrics.total_items_loaded,
            "average_batch_size": self.metrics.average_batch_size,
            "average_load_time": self.metrics.average_load_time,
            "cache_hits": self.metrics.cache_hits,
            "cache_misses": self.metrics.cache_misses,
            "last_reset": self.metrics.last_reset.isoformat(),
        }

    def reset_metrics(self) -> Any:
        """Reset performance metrics"""
        self.metrics = LoaderMetrics()
        logger.info("📊 Metrics reset", loader=self.name)


class ChildDataLoader(BaseDataLoader[str, Dict[str, Any]]):
    """
    🧸 Child Data Loader
    Optimized loading of child entities with advanced caching
    """

    def __init__(self, child_repository, cache_client: Redis):
        super().__init__(
            repository=child_repository,
            cache_client=cache_client,
            config=CacheConfig(
                ttl=600, prefix="child_loader", max_batch_size=50
            ),  # 10 minutes for child data
            name="child_loader",
        )

    async def _fetch_from_repository(
        self, child_ids: List[str]
    ) -> List[Optional[Dict[str, Any]]]:
        """Fetch children from repository efficiently"""
        try:
            # Use repository's batch get method
            children = await self.repository.get_by_ids(child_ids)

            # Convert to dictionary format expected by GraphQL
            result_map = {
                str(child.id): self._serialize_child(child)
                for child in children
                if child
            }

            # Return results in the same order as requested IDs
            return [result_map.get(child_id) for child_id in child_ids]

        except Exception as e:
            logger.error("Failed to fetch children from repository", error=str(e))
            return [None] * len(child_ids)

    def _serialize_child(self, child) -> Dict[str, Any]:
        """Serialize child entity for caching"""
        return {
            "id": str(child.id),
            "name": child.name,
            "age": child.age,
            "language": child.language,
            "parent_id": str(child.parent_id),
            "created_at": child.created_at.isoformat() if child.created_at else None,
            "updated_at": child.updated_at.isoformat() if child.updated_at else None,
            "profile_picture": child.profile_picture,
            "is_active": child.is_active,
        }


class ConversationDataLoader(BaseDataLoader[str, Dict[str, Any]]):
    """
    💬 Conversation Data Loader
    Optimized loading of conversations with relationship data
    """

    def __init__(self, conversation_repository, cache_client: Redis):
        super().__init__(
            repository=conversation_repository,
            cache_client=cache_client,
            config=CacheConfig(
                ttl=300,
                prefix="conversation_loader",
                max_batch_size=100,  # 5 minutes for conversation data
            ),
            name="conversation_loader",
        )

    async def _fetch_from_repository(
        self, conversation_ids: List[str]
    ) -> List[Optional[Dict[str, Any]]]:
        """Fetch conversations from repository efficiently"""
        try:
            conversations = await self.repository.get_by_ids(conversation_ids)
            result_map = {
                str(conv.id): self._serialize_conversation(conv)
                for conv in conversations
                if conv
            }

            return [result_map.get(conv_id) for conv_id in conversation_ids]

        except Exception as e:
            logger.error("Failed to fetch conversations from repository", error=str(e))
            return [None] * len(conversation_ids)

    def _serialize_conversation(self, conversation) -> Dict[str, Any]:
        """Serialize conversation entity for caching"""
        return {
            "id": str(conversation.id),
            "child_id": str(conversation.child_id),
            "title": conversation.title,
            "started_at": (
                conversation.started_at.isoformat() if conversation.started_at else None
            ),
            "ended_at": (
                conversation.ended_at.isoformat() if conversation.ended_at else None
            ),
            "message_count": conversation.message_count,
            "topics": conversation.topics or [],
            "is_active": conversation.is_active,
        }


class ConversationByChildLoader(BaseDataLoader[str, List[Dict[str, Any]]]):
    """
    📝 Conversation by Child Loader
    Optimized loading of conversations by child ID with pagination support
    """

    def __init__(self, conversation_repository, cache_client: Redis):
        super().__init__(
            repository=conversation_repository,
            cache_client=cache_client,
            config=CacheConfig(
                ttl=180,
                prefix="conversation_by_child",
                max_batch_size=20,  # 3 minutes for conversation lists
            ),
            name="conversation_by_child_loader",
        )

    async def _fetch_from_repository(
        self, child_ids: List[str]
    ) -> List[Optional[List[Dict[str, Any]]]]:
        """Fetch conversations by child IDs efficiently"""
        try:
            results = []

            # Batch fetch for all child IDs
            for child_id in child_ids:
                conversations = await self.repository.get_by_child_id(
                    child_id, limit=50
                )
                serialized_conversations = [
                    self._serialize_conversation(conv) for conv in conversations
                ]
                results.append(serialized_conversations)

            return results

        except Exception as e:
            logger.error("Failed to fetch conversations by child ID", error=str(e))
            return [None] * len(child_ids)

    def _serialize_conversation(self, conversation) -> Dict[str, Any]:
        """Serialize conversation for caching"""
        return {
            "id": str(conversation.id),
            "child_id": str(conversation.child_id),
            "title": conversation.title,
            "started_at": (
                conversation.started_at.isoformat() if conversation.started_at else None
            ),
            "message_count": conversation.message_count,
            "topics": conversation.topics or [],
        }


class DataLoaderRegistry:
    """
    🗂️ DataLoader Registry
    Centralized management of all DataLoaders with lifecycle management
    """

    def __init__(self, cache_client: Redis):
        self.cache_client = cache_client
        self.loaders: Dict[str, BaseDataLoader] = {}
        self._repositories = {}
        logger.info("🗂️ DataLoader Registry initialized")

    def register_repositories(self, **repositories) -> Any:
        """Register repositories for DataLoader creation"""
        self._repositories.update(repositories)
        logger.info("📚 Repositories registered", count=len(repositories))

    def get_loader(self, loader_name: str) -> Optional[BaseDataLoader]:
        """Get or create DataLoader by name"""
        if loader_name not in self.loaders:
            self._create_loader(loader_name)

        return self.loaders.get(loader_name)

    def _create_loader(self, loader_name: str) -> None:
        """Create DataLoader based on name"""
        if loader_name == "child" and "child_repository" in self._repositories:
            self.loaders[loader_name] = ChildDataLoader(
                self._repositories["child_repository"], self.cache_client
            )
        elif (
            loader_name == "conversation"
            and "conversation_repository" in self._repositories
        ):
            self.loaders[loader_name] = ConversationDataLoader(
                self._repositories["conversation_repository"], self.cache_client
            )
        elif (
            loader_name == "conversation_by_child"
            and "conversation_repository" in self._repositories
        ):
            self.loaders[loader_name] = ConversationByChildLoader(
                self._repositories["conversation_repository"], self.cache_client
            )
        else:
            logger.warning("⚠️ Unknown loader or missing repository", loader=loader_name)

    async def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get metrics for all registered DataLoaders"""
        metrics = {}
        for name, loader in self.loaders.items():
            metrics[name] = await loader.get_metrics()

        return metrics

    def reset_all_metrics(self) -> Any:
        """Reset metrics for all DataLoaders"""
        for loader in self.loaders.values():
            loader.reset_metrics()

        logger.info("📊 All DataLoader metrics reset")

    async def warm_cache(self, warmup_data: Dict[str, List[str]]):
        """Pre-warm caches with commonly accessed data"""
        logger.info("🔥 Starting cache warmup", loaders=list(warmup_data.keys()))

        for loader_name, keys in warmup_data.items():
            if loader := self.get_loader(loader_name):
                try:
                    await loader.load_many(keys)
                    logger.info(
                        "✅ Cache warmed", loader=loader_name, keys_count=len(keys)
                    )
                except Exception as e:
                    logger.error(
                        "❌ Cache warmup failed", loader=loader_name, error=str(e)
                    )


# Factory function for creating DataLoader registry
def create_dataloader_registry(
    cache_client: Redis, **repositories
) -> DataLoaderRegistry:
    """Create and configure DataLoader registry"""
    registry = DataLoaderRegistry(cache_client)
    registry.register_repositories(**repositories)

    logger.info(
        "🏭 DataLoader registry created", repositories=list(repositories.keys())
    )

    return registry
