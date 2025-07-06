"""
Core SQLite repository implementation.
"""
import logging
import sqlite3
from abc import abstractmethod
from contextlib import contextmanager
from typing import Any, List, Optional, Type, TypeVar

from src.infrastructure.persistence.base import BaseRepository, QueryOptions
from src.infrastructure.persistence.repositories.base_sqlite_repository import DatabaseError

from .sqlite_advanced_query import SQLiteAdvancedQueryMixin
from .sqlite_bulk_operations import SQLiteBulkOperationsMixin
from .sqlite_utils import SQLiteUtilityMixin

T = TypeVar("T")
ID = TypeVar("ID")

logger = logging.getLogger(__name__)


class BaseSQLiteRepository(
    SQLiteAdvancedQueryMixin,
    SQLiteBulkOperationsMixin,
    SQLiteUtilityMixin,
    BaseRepository[T, ID],
):
    """
    An enhanced and modular base repository for SQLite, providing comprehensive
    CRUD, bulk, and advanced query operations through mixins.
    """

    def __init__(self, connection: sqlite3.Connection, table_name: str, entity_class: Type[T]):
        self._connection = connection
        self._table_name = table_name
        self._entity_class = entity_class

        self._configure_connection()
        self._ensure_table_exists()

    def _configure_connection(self):
        """Configures the SQLite connection for better performance and consistency."""
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA foreign_keys = ON;")
        self._connection.execute("PRAGMA journal_mode = WAL;")

    @property
    def table_name(self) -> str:
        """Returns the safe, validated table name for this repository."""
        self._validate_table_and_column(self._table_name)
        return self._table_name

    @abstractmethod
    def _get_table_schema(self) -> str:
        """Returns the CREATE TABLE SQL statement for this repository's table."""
        pass

    def _ensure_table_exists(self) -> None:
        """Ensures the repository's table exists in the database, creating it if necessary."""
        try:
            schema = self._get_table_schema()
            self._connection.execute(schema)
            self._connection.commit()
        except sqlite3.Error as e:
            logger.error(
                f"Error creating table {self.table_name}: {e}", exc_info=True)
            raise DatabaseError(
                f"Failed to ensure table '{self.table_name}' exists: {e}")

    @contextmanager
    def transaction(self):
        """Provides a transactional context manager for database operations."""
        try:
            yield self._connection
            self._connection.commit()
        except Exception as e:
            logger.error(
                f"Transaction failed, rolling back changes for table {self.table_name}: {e}", exc_info=True)
            self._connection.rollback()
            raise DatabaseError(f"Transaction failed: {e}")

    async def create(self, entity: T) -> T:
        """Creates a new entity in the database."""
        try:
            with self.transaction() as conn:
                entity_dict = self._entity_to_dict(entity)
                sql, values = self._prepare_insert_sql(entity_dict)
                cursor = conn.cursor()
                cursor.execute(sql, values)
                if hasattr(entity, "id") and not getattr(entity, "id", None):
                    setattr(entity, "id", cursor.lastrowid)
                return entity
        except sqlite3.Error as e:
            logger.error(
                f"Error creating entity in {self.table_name}: {e}", exc_info=True)
            raise DatabaseError(f"Failed to create entity: {e}")

    async def get_by_id(self, entity_id: ID) -> Optional[T]:
        """Retrieves an entity by its unique identifier."""
        try:
            cursor = self._connection.cursor()
            self._validate_table_and_column("id")
            sql = f"SELECT * FROM {self.table_name} WHERE id = ?"
            cursor.execute(sql, (entity_id,))
            row = cursor.fetchone()
            return self._dict_to_entity(row) if row else None
        except sqlite3.Error as e:
            logger.error(
                f"Error retrieving entity {entity_id} from {self.table_name}: {e}", exc_info=True)
            raise DatabaseError(f"Failed to retrieve entity: {e}")

    async def update(self, entity: T) -> T:
        """Updates an existing entity in the database."""
        try:
            with self.transaction() as conn:
                entity_dict = self._entity_to_dict(entity)
                sql, values = self._prepare_update_sql(entity_dict)
                cursor = conn.cursor()
                cursor.execute(sql, values)
                if cursor.rowcount == 0:
                    raise ValueError(
                        f"No entity found with ID {entity_dict.get('id')} to update.")
                return entity
        except (sqlite3.Error, ValueError) as e:
            logger.error(
                f"Error updating entity in {self.table_name}: {e}", exc_info=True)
            raise DatabaseError(f"Failed to update entity: {e}")

    async def delete(self, entity_id: ID) -> bool:
        """Deletes an entity from the database by its ID."""
        try:
            with self.transaction() as conn:
                self._validate_table_and_column("id")
                sql = f"DELETE FROM {self.table_name} WHERE id = ?"
                cursor = conn.cursor()
                cursor.execute(sql, (entity_id,))
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(
                f"Error deleting entity {entity_id} from {self.table_name}: {e}", exc_info=True)
            raise DatabaseError(f"Failed to delete entity: {e}")

    async def list(self, options: Optional[QueryOptions] = None) -> List[T]:
        """Lists entities with optional filtering, sorting, and pagination."""
        try:
            cursor = self._connection.cursor()
            options = options or QueryOptions()
            sql, params = self._build_list_query(options)
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [self._dict_to_entity(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(
                f"Error listing entities from {self.table_name}: {e}", exc_info=True)
            raise DatabaseError(f"Failed to list entities: {e}")

    def close(self) -> None:
        """Closes the database connection."""
        if self._connection:
            self._connection.close()
            logger.info("Database connection closed.")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    async def get(self, entity_id: ID) -> Optional[T]:
        """Alias for get_by_id for convenience."""
        return await self.get_by_id(entity_id)

    def get_table_schema(self) -> str:
        """Public method to get the table's CREATE SQL statement."""
        return self._get_table_schema()
