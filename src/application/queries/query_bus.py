"""
🔍 Query Bus Implementation
===========================

CQRS Query Bus for handling read operations with optimized read models.
Provides query dispatching, caching, and projection management.
"""

import logging
from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Protocol, Type, TypeVar

logger = logging.getLogger(__name__)

TQuery = TypeVar("TQuery", bound="Query")
TResult = TypeVar("TResult")


@dataclass(frozen=True)
class QueryResult:
    """Result of query execution"""

    data: Any
    total_count: Optional[int] = None
    page: Optional[int] = None
    page_size: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass(frozen=True)
class CacheEntry:
    """Cache entry for query results"""

    key: str
    data: Any
    created_at: datetime
    expires_at: datetime


class Query(Protocol):
    """Base protocol for all queries"""

    query_id: str
    timestamp: datetime
    user_id: Optional[str] = None


class QueryHandler(Protocol[TQuery, TResult]):
    """Protocol for query handlers"""

    @abstractmethod
    async def handle(self, query: TQuery) -> TResult:
        """Handle the query and return result"""
        pass

    @abstractmethod
    def get_cache_key(self, query: TQuery) -> str:
        """Generate cache key for query"""
        pass

    @abstractmethod
    def get_cache_duration(self) -> timedelta:
        """Get cache duration for this query type"""
        pass


class ReadModelDatabase(Protocol):
    """Protocol for read model database"""

    @abstractmethod
    async def execute_query(self, sql: str, params: Optional[Dict] = None) -> List[Dict]:
        """Execute raw SQL query"""
        pass

    @abstractmethod
    async def get_by_id(self, table: str, id: str) -> Optional[Dict]:
        """Get single record by ID"""
        pass

    @abstractmethod
    async def find_many(
        self, table: str, filters: Optional[Dict] = None, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> List[Dict]:
        """Find multiple records with filters"""
        pass


class QueryCache:
    """In-memory cache for query results"""

    def __init__(self, max_size: int = 1000):
        self._cache: Dict[str, CacheEntry] = {}
        self.max_size = max_size

    async def get(self, key: str) -> Optional[Any]:
        """Get cached result"""

        entry = self._cache.get(key)
        if not entry:
            return None

        # Check expiration
        if datetime.utcnow() > entry.expires_at:
            del self._cache[key]
            return None

        return entry.data

    async def set(self, key: str, data: Any, duration: timedelta = timedelta(minutes=15)) -> None:
        """Set cached result"""

        # Remove oldest entries if cache is full
        if len(self._cache) >= self.max_size:
            oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k].created_at)
            del self._cache[oldest_key]

        entry = CacheEntry(key=key, data=data, created_at=datetime.utcnow(), expires_at=datetime.utcnow() + duration)

        self._cache[key] = entry

    async def invalidate(self, pattern: str = None) -> None:
        """Invalidate cache entries"""

        if pattern:
            # Remove entries matching pattern
            keys_to_remove = [k for k in self._cache.keys() if pattern in k]
            for key in keys_to_remove:
                del self._cache[key]
        else:
            # Clear all cache
            self._cache.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""

        now = datetime.utcnow()
        expired_count = sum(1 for entry in self._cache.values() if entry.expires_at < now)

        return {
            "total_entries": len(self._cache),
            "expired_entries": expired_count,
            "max_size": self.max_size,
            "hit_rate": getattr(self, "_hit_count", 0) / max(getattr(self, "_total_requests", 1), 1),
        }


class QueryBus:
    """Central query bus for CQRS pattern"""

    def __init__(self, read_model_db: ReadModelDatabase):
        self._handlers: Dict[Type[Query], QueryHandler] = {}
        self._db = read_model_db
        self._cache = QueryCache()

    def register_handler(self, query_type: Type[TQuery], handler: QueryHandler[TQuery, TResult]) -> None:
        """Register query handler"""

        if query_type in self._handlers:
            logger.warning(f"Handler for {query_type.__name__} already registered")

        self._handlers[query_type] = handler
        logger.info(f"Registered query handler for {query_type.__name__}")

    async def execute(self, query: TQuery, use_cache: bool = True) -> TResult:
        """Execute query with optional caching"""

        query_type = type(query)
        handler = self._handlers.get(query_type)

        if not handler:
            raise ValueError(f"No handler registered for {query_type.__name__}")

        # Try cache first
        if use_cache:
            cache_key = handler.get_cache_key(query)
            cached_result = await self._cache.get(cache_key)

            if cached_result is not None:
                logger.debug(f"Cache hit for query: {query_type.__name__}")
                return cached_result

        # Execute query
        start_time = datetime.utcnow()
        result = await handler.handle(query)

        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.info(f"Query {query_type.__name__} executed in {duration:.3f}s")

        # Cache result
        if use_cache:
            cache_key = handler.get_cache_key(query)
            cache_duration = handler.get_cache_duration()
            await self._cache.set(cache_key, result, cache_duration)

        return result

    async def execute_raw_sql(self, sql: str, params: Optional[Dict] = None) -> List[Dict]:
        """Execute raw SQL query on read model"""

        return await self._db.execute_query(sql, params)

    async def invalidate_cache(self, pattern: str = None) -> None:
        """Invalidate query cache"""

        await self._cache.invalidate(pattern)
        logger.info(f"Cache invalidated with pattern: {pattern}")

    def get_registered_queries(self) -> List[Type[Query]]:
        """Get list of registered query types"""
        return list(self._handlers.keys())

    async def health_check(self) -> Dict[str, Any]:
        """Health check for query bus"""

        cache_stats = self._cache.get_stats()

        return {
            "status": "healthy",
            "handlers_count": len(self._handlers),
            "registered_queries": [q.__name__ for q in self._handlers.keys()],
            "cache_stats": cache_stats,
        }


# Simple in-memory read model for development
class InMemoryReadModelDB(ReadModelDatabase):
    """Simple in-memory read model database"""

    def __init__(self):
        self._tables: Dict[str, List[Dict]] = {}

    async def execute_query(self, sql: str, params: Optional[Dict] = None) -> List[Dict]:
        """Execute simple query (limited implementation)"""
        # This is a simple implementation - in production use proper SQL engine
        return []

    async def get_by_id(self, table: str, id: str) -> Optional[Dict]:
        """Get record by ID"""

        records = self._tables.get(table, [])
        for record in records:
            if record.get("id") == id:
                return record
        return None

    async def find_many(
        self, table: str, filters: Optional[Dict] = None, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> List[Dict]:
        """Find records with filters"""

        records = self._tables.get(table, [])

        # Apply filters
        if filters:
            filtered_records = []
            for record in records:
                match = True
                for key, value in filters.items():
                    if record.get(key) != value:
                        match = False
                        break
                if match:
                    filtered_records.append(record)
            records = filtered_records

        # Apply pagination
        if offset:
            records = records[offset:]
        if limit:
            records = records[:limit]

        return records

    def insert_record(self, table: str, record: Dict) -> None:
        """Insert record for testing"""
        if table not in self._tables:
            self._tables[table] = []
        self._tables[table].append(record)


# Global query bus instance
_query_bus: Optional[QueryBus] = None


def get_query_bus() -> QueryBus:
    """Get global query bus instance"""
    global _query_bus
    if not _query_bus:
        # Use in-memory DB for development
        read_model_db = InMemoryReadModelDB()
        _query_bus = QueryBus(read_model_db)
    return _query_bus
