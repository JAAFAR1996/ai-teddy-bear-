"""
Mixin for SQLite utility and maintenance operations.
"""
import logging
import sqlite3
from typing import Any, Dict

from src.infrastructure.persistence.repositories.base_sqlite_repository import DatabaseError

from .sqlite_query_builder import QueryBuilderMixin

logger = logging.getLogger(__name__)


class SQLiteUtilityMixin(QueryBuilderMixin):
    """A mixin to add database utility and maintenance functions."""

    def get_table_info(self) -> Dict[str, Any]:
        """Gets detailed information about the repository's table, including schema, indexes, and foreign keys."""
        try:
            cursor = self._connection.cursor()
            self._validate_table_and_column(self.table_name)

            cursor.execute(f"PRAGMA table_info({self.table_name})")
            columns = [dict(row) for row in cursor.fetchall()]

            cursor.execute(f"PRAGMA index_list({self.table_name})")
            indexes = [dict(row) for row in cursor.fetchall()]

            cursor.execute(f"PRAGMA foreign_key_list({self.table_name})")
            foreign_keys = [dict(row) for row in cursor.fetchall()]

            return {
                "table_name": self.table_name,
                "columns": columns,
                "indexes": indexes,
                "foreign_keys": foreign_keys,
            }
        except sqlite3.Error as e:
            logger.error(
                f"Error getting table info for {self.table_name}: {e}", exc_info=True)
            raise DatabaseError(f"Failed to get table info: {e}")

    def vacuum(self) -> None:
        """Vacuums the database to reclaim space and improve performance."""
        try:
            self._connection.execute("VACUUM")
            self._connection.commit()
            logger.info("Database vacuumed successfully.")
        except sqlite3.Error as e:
            logger.error(f"Error vacuuming database: {e}", exc_info=True)
            raise DatabaseError(f"Failed to vacuum database: {e}")

    def analyze(self) -> None:
        """Analyzes the database to update statistics for the query planner."""
        try:
            self._connection.execute("ANALYZE")
            self._connection.commit()
            logger.info("Database analyzed successfully.")
        except sqlite3.Error as e:
            logger.error(f"Error analyzing database: {e}", exc_info=True)
            raise DatabaseError(f"Failed to analyze database: {e}")

    async def execute_safe_query(self, sql: str, params: tuple = ()):
        """
        Executes a read-only, parameterized SQL query safely.
        WARNING: This should not be used for modification queries.
        """
        if not isinstance(sql, str) or not sql.strip().upper().startswith("SELECT"):
            raise ValueError(
                "Only SELECT queries are allowed for safe execution.")

        try:
            cursor = self._connection.cursor()
            cursor.execute(sql, params)
            return cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Error executing safe query: {e}", exc_info=True)
            raise DatabaseError(f"Failed to execute safe query: {e}")
