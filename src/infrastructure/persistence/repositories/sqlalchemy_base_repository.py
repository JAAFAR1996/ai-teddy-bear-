#!/usr/bin/env python3
"""
Enhanced SQLAlchemy Base Repository
Provides comprehensive CRUD operations, advanced querying, and enterprise features
"""

import logging
from abc import ABC
from contextlib import contextmanager
from datetime import datetime
from typing import (Any, Dict, List, Optional, Type, TypeVar)

from sqlalchemy import and_, asc, desc, func, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.orm.query import Query

from src.infrastructure.persistence.base import (BaseRepository,
                                                 BulkOperationResult,
                                                 QueryOptions, SearchCriteria,
                                                 SortOrder)

T = TypeVar("T")  # Entity type
ID = TypeVar("ID")  # ID type

logger = logging.getLogger(__name__)


class RepositoryError(Exception):
    """Base repository error"""

    pass


class EntityNotFoundError(RepositoryError):
    """Entity not found error"""

    pass


class ValidationError(RepositoryError):
    """Validation error"""

    pass


class SQLAlchemyBaseRepository(BaseRepository[T, ID], ABC):
    """
    Enhanced SQLAlchemy base repository with comprehensive functionality

    Features:
    - Full CRUD operations with validation
    - Advanced querying with filters and pagination
    - Bulk operations with performance optimization
    - Transaction management
    - Entity caching and performance monitoring
    - Type-safe operations with comprehensive error handling
    """

    def __init__(
        self,
        session_factory: sessionmaker,
        model_class: Type[T],
        auto_commit: bool = True,
        enable_caching: bool = False,
    ):
        """
        Initialize repository

        Args:
            session_factory: SQLAlchemy session factory
            model_class: SQLAlchemy model class
            auto_commit: Whether to auto-commit transactions
            enable_caching: Enable entity caching (for read-heavy workloads)
        """
        self.session_factory = session_factory
        self.model_class = model_class
        self.auto_commit = auto_commit
        self.enable_caching = enable_caching

        # Performance monitoring
        self._query_count = 0
        self._cache_hits = 0
        self._cache_misses = 0

        # Simple in-memory cache (production should use Redis)
        self._cache: Dict[str, T] = {} if enable_caching else None

        logger.info(
            f"Initialized {self.__class__.__name__} for {model_class.__name__}",
            extra={
                "model_class": model_class.__name__,
                "auto_commit": auto_commit,
                "caching_enabled": enable_caching,
            },
        )

    @contextmanager
    def get_session(self) -> Session:
        """Context manager for database sessions"""
        session = self.session_factory()
        try:
            yield session
            if self.auto_commit:
                session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}", exc_info=True)
            raise RepositoryError(f"Database operation failed: {e}") from e
        finally:
            session.close()

    def _build_query(
        self,
        session: Session,
        criteria: Optional[List[SearchCriteria]] = None,
        options: Optional[QueryOptions] = None,
    ) -> Query:
        """
        Build SQLAlchemy query with filters, sorting, and pagination

        Args:
            session: Database session
            criteria: Search criteria list
            options: Query options (sorting, pagination, etc.)

        Returns:
            Configured SQLAlchemy query
        """
        query = session.query(self.model_class)
        self._query_count += 1

        # Apply search criteria
        if criteria:
            conditions = []
            for criterion in criteria:
                condition = self._build_condition(criterion)
                if condition is not None:
                    conditions.append(condition)

            if conditions:
                query = query.filter(and_(*conditions))

        # Apply additional filters from options
        if options and options.filters:
            for field, value in options.filters.items():
                if hasattr(self.model_class, field):
                    query = query.filter(getattr(self.model_class, field) == value)

        # Apply sorting
        if options and options.sort_by:
            sort_column = getattr(self.model_class, options.sort_by, None)
            if sort_column is not None:
                if options.sort_order == SortOrder.DESC:
                    query = query.order_by(desc(sort_column))
                else:
                    query = query.order_by(asc(sort_column))

        # Apply pagination
        if options:
            if options.offset:
                query = query.offset(options.offset)
            if options.limit:
                query = query.limit(options.limit)

        return query

    def _build_condition(SearchCriteria) -> None:
        """Build SQLAlchemy condition from search criteria"""
        field_attr = getattr(self.model_class, criterion.field, None)
        if field_attr is None:
            logger.warning(
                f"Field {criterion.field} not found in {self.model_class.__name__}"
            )
            return None

        value = criterion.value
        operator = criterion.operator.lower()

        if operator == "eq":
            return field_attr == value
        elif operator == "ne":
            return field_attr != value
        elif operator == "gt":
            return field_attr > value
        elif operator == "gte":
            return field_attr >= value
        elif operator == "lt":
            return field_attr < value
        elif operator == "lte":
            return field_attr <= value
        elif operator == "like":
            return field_attr.like(f"%{value}%")
        elif operator == "ilike":
            return field_attr.ilike(f"%{value}%")
        elif operator == "in":
            if isinstance(value, (list, tuple)):
                return field_attr.in_(value)
            else:
                return field_attr == value
        elif operator == "not_in":
            if isinstance(value, (list, tuple)):
                return ~field_attr.in_(value)
            else:
                return field_attr != value
        elif operator == "is_null":
            return field_attr.is_(None)
        elif operator == "is_not_null":
            return field_attr.isnot(None)
        elif operator == "between":
            if isinstance(value, (list, tuple)) and len(value) == 2:
                return field_attr.between(value[0], value[1])
        elif operator == "starts_with":
            return field_attr.like(f"{value}%")
        elif operator == "ends_with":
            return field_attr.like(f"%{value}")
        else:
            logger.warning(f"Unsupported operator: {operator}")
            return None

    def _validate_entity(self, entity: T) -> None:
        """
        Validate entity before database operations

        Args:
            entity: Entity to validate

        Raises:
            ValidationError: If entity is invalid
        """
        if entity is None:
            raise ValidationError("Entity cannot be None")

        # Additional validation can be implemented in subclasses
        pass

    def _cache_get(self, key: str) -> Optional[T]:
        """Get entity from cache"""
        if not self.enable_caching or not self._cache:
            return None

        entity = self._cache.get(key)
        if entity:
            self._cache_hits += 1
            return entity

        self._cache_misses += 1
        return None

    def _cache_put(self, key: str, entity: T) -> None:
        """Put entity in cache"""
        if self.enable_caching and self._cache is not None:
            self._cache[key] = entity

    def _cache_remove(self, key: str) -> None:
        """Remove entity from cache"""
        if self.enable_caching and self._cache is not None:
            self._cache.pop(key, None)

    # Core CRUD Operations

    async def create(self, entity: T) -> T:
        """
        Create a new entity

        Args:
            entity: Entity to create

        Returns:
            Created entity with assigned ID

        Raises:
            ValidationError: If entity is invalid
            RepositoryError: If database operation fails
        """
        self._validate_entity(entity)

        try:
            with self.get_session() as session:
                session.add(entity)
                session.flush()  # Get ID without committing

                # Cache the entity
                if hasattr(entity, "id") and entity.id:
                    self._cache_put(str(entity.id), entity)

                logger.info(
                    f"Created {self.model_class.__name__}",
                    extra={"entity_id": getattr(entity, "id", None)},
                )

                return entity

        except IntegrityError as e:
            logger.error(f"Integrity constraint violation: {e}")
            raise ValidationError(
                f"Entity creation failed due to constraint violation: {e}"
            ) from e
        except SQLAlchemyError as e:
            logger.error(f"Database error during create: {e}")
            raise RepositoryError(f"Failed to create entity: {e}") from e

    async def get_by_id(self, entity_id: ID) -> Optional[T]:
        """
        Retrieve entity by ID

        Args:
            entity_id: Unique identifier

        Returns:
            Entity if found, None otherwise
        """
        if entity_id is None:
            return None

        # Check cache first
        cached_entity = self._cache_get(str(entity_id))
        if cached_entity:
            return cached_entity

        try:
            with self.get_session() as session:
                entity = (
                    session.query(self.model_class)
                    .filter(self.model_class.id == entity_id)
                    .first()
                )

                # Cache the result
                if entity:
                    self._cache_put(str(entity_id), entity)

                return entity

        except SQLAlchemyError as e:
            logger.error(f"Database error during get_by_id: {e}")
            raise RepositoryError(f"Failed to retrieve entity: {e}") from e

    async def update(self, entity: T) -> T:
        """
        Update existing entity

        Args:
            entity: Entity to update

        Returns:
            Updated entity

        Raises:
            EntityNotFoundError: If entity doesn't exist
            ValidationError: If entity is invalid
        """
        self._validate_entity(entity)

        if not hasattr(entity, "id") or not entity.id:
            raise ValidationError("Entity must have an ID for update")

        try:
            with self.get_session() as session:
                # Check if entity exists
                existing = (
                    session.query(self.model_class)
                    .filter(self.model_class.id == entity.id)
                    .first()
                )

                if not existing:
                    raise EntityNotFoundError(f"Entity with ID {entity.id} not found")

                # Update fields
                for key, value in entity.__dict__.items():
                    if not key.startswith("_") and hasattr(existing, key):
                        setattr(existing, key, value)

                # Update timestamp if available
                if hasattr(existing, "updated_at"):
                    existing.updated_at = datetime.utcnow()

                session.flush()

                # Update cache
                self._cache_put(str(entity.id), existing)

                logger.info(
                    f"Updated {self.model_class.__name__}",
                    extra={"entity_id": entity.id},
                )

                return existing

        except SQLAlchemyError as e:
            logger.error(f"Database error during update: {e}")
            raise RepositoryError(f"Failed to update entity: {e}") from e

    async def delete(self, entity_id: ID) -> bool:
        """
        Delete entity by ID

        Args:
            entity_id: Unique identifier

        Returns:
            True if deleted, False if not found
        """
        if entity_id is None:
            return False

        try:
            with self.get_session() as session:
                entity = (
                    session.query(self.model_class)
                    .filter(self.model_class.id == entity_id)
                    .first()
                )

                if not entity:
                    return False

                session.delete(entity)
                session.flush()

                # Remove from cache
                self._cache_remove(str(entity_id))

                logger.info(
                    f"Deleted {self.model_class.__name__}",
                    extra={"entity_id": entity_id},
                )

                return True

        except SQLAlchemyError as e:
            logger.error(f"Database error during delete: {e}")
            raise RepositoryError(f"Failed to delete entity: {e}") from e

    async def list(self, options: Optional[QueryOptions] = None) -> List[T]:
        """
        List entities with optional filtering and sorting

        Args:
            options: Query options for filtering, sorting, pagination

        Returns:
            List of entities
        """
        try:
            with self.get_session() as session:
                query = self._build_query(session, options=options)
                entities = query.all()

                # Cache entities
                for entity in entities:
                    if hasattr(entity, "id") and entity.id:
                        self._cache_put(str(entity.id), entity)

                return entities

        except SQLAlchemyError as e:
            logger.error(f"Database error during list: {e}")
            raise RepositoryError(f"Failed to list entities: {e}") from e

    async def search(
        self, criteria: List[SearchCriteria], options: Optional[QueryOptions] = None
    ) -> List[T]:
        """
        Search entities with advanced criteria

        Args:
            criteria: List of search criteria
            options: Query options

        Returns:
            List of matching entities
        """
        try:
            with self.get_session() as session:
                query = self._build_query(session, criteria=criteria, options=options)
                entities = query.all()

                return entities

        except SQLAlchemyError as e:
            logger.error(f"Database error during search: {e}")
            raise RepositoryError(f"Failed to search entities: {e}") from e

    async def count(self, criteria: Optional[List[SearchCriteria]] = None) -> int:
        """
        Count entities matching criteria

        Args:
            criteria: Optional search criteria

        Returns:
            Number of matching entities
        """
        try:
            with self.get_session() as session:
                query = self._build_query(session, criteria=criteria)
                # Use count() for better performance
                count = query.count()
                return count

        except SQLAlchemyError as e:
            logger.error(f"Database error during count: {e}")
            raise RepositoryError(f"Failed to count entities: {e}") from e

    async def exists(self, entity_id: ID) -> bool:
        """
        Check if entity exists

        Args:
            entity_id: Unique identifier

        Returns:
            True if entity exists
        """
        if entity_id is None:
            return False

        # Check cache first
        if self._cache_get(str(entity_id)):
            return True

        try:
            with self.get_session() as session:
                exists = session.query(
                    session.query(self.model_class)
                    .filter(self.model_class.id == entity_id)
                    .exists()
                ).scalar()

                return exists

        except SQLAlchemyError as e:
            logger.error(f"Database error during exists check: {e}")
            raise RepositoryError(f"Failed to check entity existence: {e}") from e

    # Bulk Operations

    async def bulk_create(self, entities: List[T]) -> BulkOperationResult:
        """
        Create multiple entities in a single transaction

        Args:
            entities: List of entities to create

        Returns:
            Bulk operation result with success/failure counts
        """
        if not entities:
            return BulkOperationResult(success_count=0, failed_count=0, failed_ids=[])

        success_count = 0
        failed_count = 0
        failed_ids = []

        try:
            with self.get_session() as session:
                for entity in entities:
                    try:
                        self._validate_entity(entity)
                        session.add(entity)
                        success_count += 1
                    except Exception as e:
                        failed_count += 1
                        entity_id = getattr(entity, "id", "unknown")
                        failed_ids.append(str(entity_id))
                        logger.warning(f"Failed to add entity {entity_id}: {e}")

                session.flush()

                logger.info(
                    f"Bulk created {success_count} {self.model_class.__name__} entities",
                    extra={
                        "success_count": success_count,
                        "failed_count": failed_count,
                    },
                )

        except SQLAlchemyError as e:
            logger.error(f"Database error during bulk create: {e}")
            raise RepositoryError(f"Bulk create operation failed: {e}") from e

        return BulkOperationResult(
            success_count=success_count,
            failed_count=failed_count,
            failed_ids=failed_ids,
        )

    async def bulk_update(self, entities: List[T]) -> BulkOperationResult:
        """
        Update multiple entities

        Args:
            entities: List of entities to update

        Returns:
            Bulk operation result
        """
        if not entities:
            return BulkOperationResult(success_count=0, failed_count=0, failed_ids=[])

        success_count = 0
        failed_count = 0
        failed_ids = []

        try:
            with self.get_session() as session:
                for entity in entities:
                    try:
                        if not hasattr(entity, "id") or not entity.id:
                            raise ValidationError("Entity must have ID for update")

                        existing = (
                            session.query(self.model_class)
                            .filter(self.model_class.id == entity.id)
                            .first()
                        )

                        if existing:
                            # Update fields
                            for key, value in entity.__dict__.items():
                                if not key.startswith("_") and hasattr(existing, key):
                                    setattr(existing, key, value)

                            success_count += 1
                            self._cache_put(str(entity.id), existing)
                        else:
                            failed_count += 1
                            failed_ids.append(str(entity.id))

                    except Exception as e:
                        failed_count += 1
                        entity_id = getattr(entity, "id", "unknown")
                        failed_ids.append(str(entity_id))
                        logger.warning(f"Failed to update entity {entity_id}: {e}")

                session.flush()

        except SQLAlchemyError as e:
            logger.error(f"Database error during bulk update: {e}")
            raise RepositoryError(f"Bulk update operation failed: {e}") from e

        return BulkOperationResult(
            success_count=success_count,
            failed_count=failed_count,
            failed_ids=failed_ids,
        )

    async def bulk_delete(self, entity_ids: List[ID]) -> BulkOperationResult:
        """
        Delete multiple entities

        Args:
            entity_ids: List of entity IDs to delete

        Returns:
            Bulk operation result
        """
        if not entity_ids:
            return BulkOperationResult(success_count=0, failed_count=0, failed_ids=[])

        success_count = 0
        failed_count = 0
        failed_ids = []

        try:
            with self.get_session() as session:
                # Use bulk delete for better performance
                deleted_count = (
                    session.query(self.model_class)
                    .filter(self.model_class.id.in_(entity_ids))
                    .delete(synchronize_session=False)
                )

                success_count = deleted_count
                failed_count = len(entity_ids) - deleted_count

                # Clear cache for deleted entities
                for entity_id in entity_ids:
                    self._cache_remove(str(entity_id))

                if failed_count > 0:
                    # Find which IDs failed (simplified approach)
                    failed_ids = [str(id_) for id_ in entity_ids[-failed_count:]]

        except SQLAlchemyError as e:
            logger.error(f"Database error during bulk delete: {e}")
            raise RepositoryError(f"Bulk delete operation failed: {e}") from e

        return BulkOperationResult(
            success_count=success_count,
            failed_count=failed_count,
            failed_ids=failed_ids,
        )

    # Advanced Operations

    async def find_one(self, criteria: List[SearchCriteria]) -> Optional[T]:
        """
        Find single entity matching criteria

        Args:
            criteria: Search criteria

        Returns:
            First matching entity or None
        """
        options = QueryOptions(limit=1)
        results = await self.search(criteria, options)
        return results[0] if results else None

    async def find_by_field(self, field: str, value: Any) -> List[T]:
        """
        Find entities by specific field value

        Args:
            field: Field name
            value: Field value

        Returns:
            List of matching entities
        """
        criteria = [SearchCriteria(field=field, operator="eq", value=value)]
        return await self.search(criteria)

    async def aggregate(
        self,
        field: str,
        operation: str,
        criteria: Optional[List[SearchCriteria]] = None,
    ) -> Any:
        """
        Perform aggregation operation

        Args:
            field: Field to aggregate
            operation: Aggregation operation (count, sum, avg, min, max)
            criteria: Optional search criteria

        Returns:
            Aggregation result
        """
        try:
            with self.get_session() as session:
                query = self._build_query(session, criteria=criteria)

                field_attr = getattr(self.model_class, field, None)
                if field_attr is None:
                    raise ValueError(
                        f"Field {field} not found in {self.model_class.__name__}"
                    )

                if operation.lower() == "count":
                    result = query.count()
                elif operation.lower() == "sum":
                    result = query.with_entities(func.sum(field_attr)).scalar()
                elif operation.lower() == "avg":
                    result = query.with_entities(func.avg(field_attr)).scalar()
                elif operation.lower() == "min":
                    result = query.with_entities(func.min(field_attr)).scalar()
                elif operation.lower() == "max":
                    result = query.with_entities(func.max(field_attr)).scalar()
                else:
                    raise ValueError(f"Unsupported aggregation operation: {operation}")

                return result

        except SQLAlchemyError as e:
            logger.error(f"Database error during aggregation: {e}")
            raise RepositoryError(f"Aggregation operation failed: {e}") from e

    async def execute_raw_query(
        self, query: str, params: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute raw SQL query (use with caution)

        Args:
            query: Raw SQL query
            params: Query parameters

        Returns:
            Query results as list of dictionaries
        """
        try:
            with self.get_session() as session:
                result = session.execute(text(query), params or {})
                return [dict(row) for row in result]

        except SQLAlchemyError as e:
            logger.error(f"Database error during raw query execution: {e}")
            raise RepositoryError(f"Raw query execution failed: {e}") from e

    # Performance and Monitoring

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get repository performance statistics"""
        cache_hit_ratio = 0.0
        if self._cache_hits + self._cache_misses > 0:
            cache_hit_ratio = self._cache_hits / (self._cache_hits + self._cache_misses)

        return {
            "model_class": self.model_class.__name__,
            "query_count": self._query_count,
            "cache_enabled": self.enable_caching,
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "cache_hit_ratio": cache_hit_ratio,
            "cache_size": len(self._cache) if self._cache else 0,
        }

    def clear_cache(self) -> None:
        """Clear entity cache"""
        if self._cache:
            self._cache.clear()
            logger.info(f"Cleared cache for {self.model_class.__name__}")

    def reset_performance_stats(self) -> None:
        """Reset performance statistics"""
        self._query_count = 0
        self._cache_hits = 0
        self._cache_misses = 0
