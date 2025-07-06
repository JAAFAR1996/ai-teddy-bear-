"""
Mixin for advanced querying in SQLAlchemy repositories.
"""
import logging
from typing import Any, List, Optional, TypeVar

from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.infrastructure.persistence.base import QueryOptions, SearchCriteria

from .exceptions import RepositoryError
from .query_builder import QueryBuilderMixin

T = TypeVar("T")
logger = logging.getLogger(__name__)


class AdvancedQueryMixin(QueryBuilderMixin):
    """A mixin to add advanced querying capabilities like search, count, and aggregation."""

    def get_session(self) -> Session:
        """Placeholder for getting a session. To be implemented in the main class."""
        raise NotImplementedError

    async def search(
        self, criteria: List[SearchCriteria], options: Optional[QueryOptions] = None
    ) -> List[T]:
        """Searches for entities with advanced criteria, including filtering, sorting, and pagination."""
        try:
            with self.get_session() as session:
                query = self._build_query(
                    session, criteria=criteria, options=options)
                return query.all()
        except SQLAlchemyError as e:
            logger.error(f"Database error during search: {e}", exc_info=True)
            raise RepositoryError(f"Failed to search entities: {e}")

    async def count(self, criteria: Optional[List[SearchCriteria]] = None) -> int:
        """Counts entities that match the given search criteria."""
        try:
            with self.get_session() as session:
                query = self._build_query(session, criteria=criteria)
                # Use a more direct way to count for performance
                count_query = query.statement.with_only_columns(
                    [func.count()]).order_by(None)
                return session.execute(count_query).scalar_one()
        except SQLAlchemyError as e:
            logger.error(f"Database error during count: {e}", exc_info=True)
            raise RepositoryError(f"Failed to count entities: {e}")

    async def exists(self, entity_id: Any) -> bool:
        """Checks if an entity with the given ID exists in the database."""
        if entity_id is None:
            return False

        if hasattr(self, '_cache_get') and self._cache_get(str(entity_id)):
            return True

        try:
            with self.get_session() as session:
                query = session.query(self.model_class).filter(
                    self.model_class.id == entity_id)
                return session.query(query.exists()).scalar()
        except SQLAlchemyError as e:
            logger.error(
                f"Database error during existence check for ID {entity_id}: {e}", exc_info=True)
            raise RepositoryError(f"Failed to check entity existence: {e}")

    async def find_one(self, criteria: List[SearchCriteria]) -> Optional[T]:
        """Finds a single entity that matches the given criteria."""
        options = QueryOptions(limit=1)
        results = await self.search(criteria, options)
        return results[0] if results else None

    async def find_by_field(self, field: str, value: Any) -> List[T]:
        """Finds all entities that have a specific value in a given field."""
        self._validate_attribute_name(field)
        criteria = [SearchCriteria(field=field, operator="eq", value=value)]
        return await self.search(criteria)

    async def aggregate(
        self,
        field: str,
        operation: str,
        criteria: Optional[List[SearchCriteria]] = None,
    ) -> Any:
        """Performs an aggregation operation (e.g., COUNT, SUM, AVG) on a specific field."""
        self._validate_attribute_name(field)
        op = operation.lower()
        if op not in ["count", "sum", "avg", "max", "min"]:
            raise ValueError(f"Unsupported aggregation operation: {operation}")

        try:
            with self.get_session() as session:
                query = self._build_query(session, criteria=criteria)
                field_attr = getattr(self.model_class, field)
                agg_func = getattr(func, op)

                # with_entities is used to select specific columns/aggregates
                result = query.with_entities(agg_func(field_attr)).scalar()
                return result
        except SQLAlchemyError as e:
            logger.error(
                f"Database error during aggregation on {field}: {e}", exc_info=True)
            raise RepositoryError(f"Aggregation operation failed: {e}")
