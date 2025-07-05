# base.py - Enhanced base repository with advanced features

import asyncio
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import (
    Any,
    AsyncIterator,
    Callable,
    Dict,
    Generic,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
)

T = TypeVar("T")
ID = TypeVar("ID", bound=Union[str, int])


class SortOrder(Enum):
    """Sort order enumeration"""

    ASC = "ASC"
    DESC = "DESC"


class OperationType(Enum):
    """Database operation types for auditing"""

    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    BULK_CREATE = "BULK_CREATE"
    BULK_UPDATE = "BULK_UPDATE"
    BULK_DELETE = "BULK_DELETE"


@dataclass
class QueryOptions:
    """Options for querying entities"""

    limit: Optional[int] = None
    offset: Optional[int] = None
    sort_by: Optional[str] = None
    sort_order: SortOrder = SortOrder.ASC
    include_deleted: bool = False
    select_fields: Optional[List[str]] = None
    exclude_fields: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for query building"""
        return {
            "limit": self.limit,
            "offset": self.offset,
            "sort_by": self.sort_by,
            "sort_order": self.sort_order.value,
            "include_deleted": self.include_deleted,
        }


@dataclass
class BulkOperationResult:
    """Result of bulk operations"""

    total_count: int
    success_count: int
    failed_count: int
    failed_ids: List[ID] = field(default_factory=list)
    errors: Dict[ID, str] = field(default_factory=dict)

    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        if self.total_count == 0:
            return 0.0
        return self.success_count / self.total_count


@dataclass
class SearchCriteria:
    """Advanced search criteria"""

    field: str
    operator: str  # eq, ne, gt, gte, lt, lte, in, not_in, like, ilike
    value: Any

    def to_sql(self) -> str:
        """Convert to SQL condition"""
        operator_map = {
            "eq": "=",
            "ne": "!=",
            "gt": ">",
            "gte": ">=",
            "lt": "<",
            "lte": "<=",
            "like": "LIKE",
            "ilike": "ILIKE",
        }

        if self.operator in ["in", "not_in"]:
            op = "IN" if self.operator == "in" else "NOT IN"
            placeholders = ", ".join(["?" for _ in self.value])
            return f"{self.field} {op} ({placeholders})"

        sql_op = operator_map.get(self.operator, "=")
        return f"{self.field} {sql_op} ?"


class RepositoryError(Exception):
    """Base exception for repository errors"""

    pass


class EntityNotFoundError(RepositoryError):
    """Raised when entity is not found"""

    def __init__(self, entity_type: str, entity_id: Any):
        super().__init__(f"{entity_type} with id {entity_id} not found")
        self.entity_type = entity_type
        self.entity_id = entity_id


class DuplicateEntityError(RepositoryError):
    """Raised when trying to create duplicate entity"""

    def __init__(self, entity_type: str, field: str, value: Any):
        super().__init__(f"{entity_type} with {field}={value} already exists")
        self.entity_type = entity_type
        self.field = field
        self.value = value


class ValidationError(RepositoryError):
    """Raised when entity validation fails"""

    def __init__(self, errors: Dict[str, str]):
        super().__init__(f"Validation failed: {errors}")
        self.errors = errors


class BaseRepository(ABC, Generic[T, ID]):
    """
    Enhanced abstract base repository with advanced features
    """

    def __init__(self, entity_type: Type[T]):
        """Initialize repository with entity type"""
        self.entity_type = entity_type
        self.entity_name = entity_type.__name__
        self._cache: Dict[ID, T] = {}
        self._cache_ttl: int = 300  # 5 minutes default
        self._hooks: Dict[OperationType, List[Callable]] = {
            op: [] for op in OperationType
        }

    # Core CRUD Operations

    @abstractmethod
    async def add(self, entity: T) -> T:
        """Add a new entity to the repository"""
        pass

    @abstractmethod
    async def get(self, entity_id: ID) -> Optional[T]:
        """Retrieve an entity by its unique identifier"""
        pass

    @abstractmethod
    async def update(self, entity: T) -> T:
        """Update an existing entity"""
        pass

    @abstractmethod
    async def delete(self, entity_id: ID) -> bool:
        """Delete an entity by its unique identifier"""
        pass

    # Advanced Query Operations

    @abstractmethod
    async def list(
        self, options: Optional[QueryOptions] = None, **filters: Any
    ) -> List[T]:
        """List entities with advanced querying options"""
        pass

    @abstractmethod
    async def search(
            self,
            criteria: List[SearchCriteria],
            options: Optional[QueryOptions] = None) -> List[T]:
        """Search entities with multiple criteria"""
        pass

    @abstractmethod
    async def count(
        self, criteria: Optional[List[SearchCriteria]] = None, **filters: Any
    ) -> int:
        """Count entities matching criteria"""
        pass

    @abstractmethod
    async def exists(self, entity_id: ID) -> bool:
        """Check if an entity exists"""
        pass

    # Bulk Operations

    async def bulk_add(self, entities: List[T]) -> BulkOperationResult:
        """Add multiple entities in a single operation"""
        result = BulkOperationResult(
            total_count=len(entities), success_count=0, failed_count=0
        )

        for entity in entities:
            try:
                await self.add(entity)
                result.success_count += 1
            except Exception as e:
                result.failed_count += 1
                entity_id = getattr(entity, "id", None)
                if entity_id:
                    result.failed_ids.append(entity_id)
                    result.errors[entity_id] = str(e)

        return result

    async def bulk_update(self, entities: List[T]) -> BulkOperationResult:
        """Update multiple entities in a single operation"""
        result = BulkOperationResult(
            total_count=len(entities), success_count=0, failed_count=0
        )

        for entity in entities:
            try:
                await self.update(entity)
                result.success_count += 1
            except Exception as e:
                result.failed_count += 1
                entity_id = getattr(entity, "id", None)
                if entity_id:
                    result.failed_ids.append(entity_id)
                    result.errors[entity_id] = str(e)

        return result

    async def bulk_delete(self, entity_ids: List[ID]) -> BulkOperationResult:
        """Delete multiple entities in a single operation"""
        result = BulkOperationResult(
            total_count=len(entity_ids), success_count=0, failed_count=0
        )

        for entity_id in entity_ids:
            try:
                success = await self.delete(entity_id)
                if success:
                    result.success_count += 1
                else:
                    result.failed_count += 1
                    result.failed_ids.append(entity_id)
            except Exception as e:
                result.failed_count += 1
                result.failed_ids.append(entity_id)
                result.errors[entity_id] = str(e)

        return result

    # Pagination

    async def paginate(
        self, page: int = 1, page_size: int = 20, **filters: Any
    ) -> Dict[str, Any]:
        """Get paginated results"""
        offset = (page - 1) * page_size
        options = QueryOptions(limit=page_size, offset=offset)

        items = await self.list(options=options, **filters)
        total_count = await self.count(**filters)
        total_pages = (total_count + page_size - 1) // page_size

        return {
            "items": items,
            "page": page,
            "page_size": page_size,
            "total_count": total_count,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        }

    # Streaming

    async def stream(self, batch_size: int = 100, **
                     filters: Any) -> AsyncIterator[T]:
        """Stream entities in batches"""
        offset = 0

        while True:
            options = QueryOptions(limit=batch_size, offset=offset)
            batch = await self.list(options=options, **filters)

            if not batch:
                break

            for entity in batch:
                yield entity

            offset += batch_size

    # Aggregation

    @abstractmethod
    async def aggregate(
        self,
        group_by: Optional[List[str]] = None,
        aggregations: Optional[Dict[str, str]] = None,
        **filters: Any,
    ) -> List[Dict[str, Any]]:
        """Perform aggregation operations"""
        pass

    # Caching

    async def get_cached(self, entity_id: ID) -> Optional[T]:
        """Get entity with caching"""
        # Check cache first
        if entity_id in self._cache:
            return self._cache[entity_id]

        # Fetch from repository
        entity = await self.get(entity_id)
        if entity:
            self._cache[entity_id] = entity
            # Schedule cache cleanup
            asyncio.create_task(self._cleanup_cache_entry(entity_id))

        return entity

    async def _cleanup_cache_entry(self, entity_id: ID):
        """Remove cache entry after TTL"""
        await asyncio.sleep(self._cache_ttl)
        self._cache.pop(entity_id, None)

    def clear_cache(self) -> Any:
        """Clear all cached entries"""
        self._cache.clear()

    # Hooks and Events

    def add_hook(Callable) -> None:
        """Add a hook for an operation type"""
        self._hooks[operation].append(hook)

    def remove_hook(Callable) -> None:
        """Remove a hook"""
        if hook in self._hooks[operation]:
            self._hooks[operation].remove(hook)

    async def _execute_hooks(self, operation: OperationType, entity: T):
        """Execute all hooks for an operation"""
        for hook in self._hooks[operation]:
            if asyncio.iscoroutinefunction(hook):
                await hook(entity)
            else:
                hook(entity)

    # Validation

    async def validate(self, entity: T) -> Dict[str, str]:
        """Validate entity before saving"""
        errors = {}

        # Check required fields
        for field_name, field_type in entity.__annotations__.items():
            value = getattr(entity, field_name, None)

            # Check if field is required (not Optional)
            if not str(field_type).startswith("Optional") and value is None:
                errors[field_name] = f"{field_name} is required"

        return errors

    # Soft Delete Support

    async def soft_delete(self, entity_id: ID) -> bool:
        """Soft delete an entity (mark as deleted)"""
        entity = await self.get(entity_id)
        if not entity:
            return False

        # Set deleted_at timestamp if entity has this field
        if hasattr(entity, "deleted_at"):
            entity.deleted_at = datetime.now()
            await self.update(entity)
            return True

        # Otherwise, perform hard delete
        return await self.delete(entity_id)

    async def restore(self, entity_id: ID) -> bool:
        """Restore a soft-deleted entity"""
        entity = await self.get(entity_id)
        if not entity:
            return False

        if hasattr(entity, "deleted_at"):
            entity.deleted_at = None
            await self.update(entity)
            return True

        return False

    # Transaction Support

    @asynccontextmanager
    async def transaction(self):
        """Context manager for transactions"""
        # This would be implemented by concrete repositories
        # that support transactions
        yield self

    # Utility Methods

    async def find_one(self, **filters: Any) -> Optional[T]:
        """Find first entity matching filters"""
        options = QueryOptions(limit=1)
        results = await self.list(options=options, **filters)
        return results[0] if results else None

    async def find_or_create(
        self, defaults: Dict[str, Any], **filters: Any
    ) -> Tuple[T, bool]:
        """Find entity or create if not exists"""
        entity = await self.find_one(**filters)
        if entity:
            return entity, False

        # Create new entity
        entity_data = {**filters, **defaults}
        entity = self.entity_type(**entity_data)
        created_entity = await self.add(entity)
        return created_entity, True

    async def update_or_create(
        self, defaults: Dict[str, Any], **filters: Any
    ) -> Tuple[T, bool]:
        """Update entity or create if not exists"""
        entity = await self.find_one(**filters)

        if entity:
            # Update existing entity
            for key, value in defaults.items():
                setattr(entity, key, value)
            updated_entity = await self.update(entity)
            return updated_entity, False
        else:
            # Create new entity
            entity_data = {**filters, **defaults}
            entity = self.entity_type(**entity_data)
            created_entity = await self.add(entity)
            return created_entity, True

    # Query Builder Methods

    def query(self) -> "QueryBuilder[T]":
        """Start building a query"""
        return QueryBuilder(self)


class QueryBuilder(Generic[T]):
    """Fluent query builder for repositories"""

    def __init__(self, repository: BaseRepository[T, Any]):
        self.repository = repository
        self.criteria: List[SearchCriteria] = []
        self.options = QueryOptions()
        self._filters: Dict[str, Any] = {}

    def where(self, field: str, operator: str,
              value: Any) -> "QueryBuilder[T]":
        """Add where condition"""
        self.criteria.append(SearchCriteria(field, operator, value))
        return self

    def filter(self, **kwargs) -> "QueryBuilder[T]":
        """Add simple equality filters"""
        self._filters.update(kwargs)
        return self

    def order_by(
        self, field: str, order: SortOrder = SortOrder.ASC
    ) -> "QueryBuilder[T]":
        """Set ordering"""
        self.options.sort_by = field
        self.options.sort_order = order
        return self

    def limit(self, limit: int) -> "QueryBuilder[T]":
        """Set result limit"""
        self.options.limit = limit
        return self

    def offset(self, offset: int) -> "QueryBuilder[T]":
        """Set result offset"""
        self.options.offset = offset
        return self

    def include_deleted(self) -> "QueryBuilder[T]":
        """Include soft-deleted entities"""
        self.options.include_deleted = True
        return self

    async def get(self) -> List[T]:
        """Execute query and get results"""
        if self.criteria:
            return await self.repository.search(self.criteria, self.options)
        else:
            return await self.repository.list(self.options, **self._filters)

    async def first(self) -> Optional[T]:
        """Get first result"""
        self.limit(1)
        results = await self.get()
        return results[0] if results else None

    async def count(self) -> int:
        """Get count of matching entities"""
        if self.criteria:
            return await self.repository.count(criteria=self.criteria)
        else:
            return await self.repository.count(**self._filters)

    async def exists(self) -> bool:
        """Check if any matching entity exists"""
        count = await self.count()
        return count > 0


# Type aliases for common ID types
StringID = BaseRepository[T, str]
IntID = BaseRepository[T, int]
