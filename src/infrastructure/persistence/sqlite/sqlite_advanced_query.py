"""
Mixin for advanced querying in SQLite repositories.
"""
import logging
import sqlite3
from typing import Any, List, Optional, TypeVar

from src.infrastructure.persistence.base import QueryOptions, SearchCriteria
from src.infrastructure.persistence.repositories.base_sqlite_repository import DatabaseError

from .sqlite_query_builder import QueryBuilderMixin

T = TypeVar("T")
logger = logging.getLogger(__name__)


class SQLiteAdvancedQueryMixin(QueryBuilderMixin):
    """A mixin to add advanced querying capabilities like search, count, and aggregation."""

    async def search(
        self, criteria: List[SearchCriteria], options: Optional[QueryOptions] = None
    ) -> List[T]:
        """Searches for entities with advanced criteria, including validation and pagination."""
        try:
            cursor = self._connection.cursor()
            options = options or QueryOptions()
            sql, params = self._build_search_query(criteria, options)
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [self._dict_to_entity(dict(row)) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Error searching entities: {e}", exc_info=True)
            raise DatabaseError(f"Failed to search entities: {e}")

    async def count(self, criteria: Optional[List[SearchCriteria]] = None) -> int:
        """Counts entities that match the given search criteria."""
        try:
            cursor = self._connection.cursor()
            self._validate_table_and_column(self.table_name)
            sql = f"SELECT COUNT(*) FROM {self.table_name}"
            params: List[Any] = []

            if criteria:
                sql, params = self._apply_criteria_to_query(
                    sql, params, criteria)

            cursor.execute(sql, params)
            result = cursor.fetchone()
            return result[0] if result else 0
        except sqlite3.Error as e:
            logger.error(f"Error counting entities: {e}", exc_info=True)
            raise DatabaseError(f"Failed to count entities: {e}")

    async def exists(self, entity_id: str) -> bool:
        """Checks if an entity with the given ID exists."""
        try:
            cursor = self._connection.cursor()
            self._validate_table_and_column("id")
            sql = f"SELECT 1 FROM {self.table_name} WHERE id = ? LIMIT 1"
            cursor.execute(sql, (entity_id,))
            return cursor.fetchone() is not None
        except sqlite3.Error as e:
            logger.error(
                f"Error checking entity existence for ID {entity_id}: {e}", exc_info=True)
            raise DatabaseError(f"Failed to check entity existence: {e}")

    async def find_one(self, criteria: List[SearchCriteria]) -> Optional[T]:
        """Finds a single entity that matches the given criteria."""
        options = QueryOptions(limit=1)
        results = await self.search(criteria, options)
        return results[0] if results else None

    async def find_by_field(self, field: str, value: Any) -> List[T]:
        """Finds all entities that have a specific value in a given field."""
        self._validate_table_and_column(field)
        criteria = [SearchCriteria(field=field, operator="eq", value=value)]
        return await self.search(criteria)

    async def aggregate(
        self,
        field: str,
        operation: str,
        criteria: Optional[List[SearchCriteria]] = None,
    ) -> Any:
        """Performs an aggregation operation (e.g., COUNT, SUM, AVG) on a specific field."""
        try:
            cursor = self._connection.cursor()
            self._validate_table_and_column(self.table_name)
            agg_func = self._build_aggregation_function(operation, field)
            sql = f"SELECT {agg_func} FROM {self.table_name}"
            params: List[Any] = []

            if criteria:
                sql, params = self._apply_criteria_to_query(
                    sql, params, criteria)

            cursor.execute(sql, params)
            result = cursor.fetchone()
            return result[0] if result else None
        except sqlite3.Error as e:
            logger.error(
                f"Error performing aggregation on field {field}: {e}", exc_info=True)
            raise DatabaseError(f"Failed to perform aggregation: {e}")
