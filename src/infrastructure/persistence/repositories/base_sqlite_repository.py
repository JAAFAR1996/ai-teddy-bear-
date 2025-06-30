import sqlite3
import logging
import json
from typing import TypeVar, Generic, Optional, List, Any, Type, Dict, Union, Tuple
from datetime import datetime
from contextlib import contextmanager
from abc import abstractmethod

from src.domain.repositories.base import (
    BaseRepository, QueryOptions, SearchCriteria,
    SortOrder, BulkOperationResult
)

T = TypeVar('T')
ID = TypeVar('ID')


class DatabaseError(Exception):
    """Custom database error"""
    pass


class BaseSQLiteRepository(BaseRepository[T, ID]):
    """
    Enhanced SQLite repository implementation

    Provides comprehensive CRUD operations, transactions, and advanced querying
    """

    def __init__(self, connection, table_name=None, entity_class=None):
        """
        Initialize SQLite repository

        Args:
            connection (sqlite3.Connection): SQLite database connection
            table_name (str): Name of the database table
            entity_class (Type[T]): Entity class for serialization/deserialization
        """
        self._connection = connection
        self._table_name = table_name or self.table_name
        self._entity_class = entity_class
        self.logger = logging.getLogger(self.__class__.__name__)

        # Configure connection for better performance and consistency
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA foreign_keys = ON")
        self._connection.execute("PRAGMA journal_mode = WAL")

        # Initialize table if needed
        self._ensure_table_exists()

    @property
    def table_name(self) -> str:
        """Get the table name for this repository."""
        if hasattr(self, '_table_name') and self._table_name:
            return self._table_name
        raise NotImplementedError(
            "Subclasses must define table_name property or provide it in constructor")

    @abstractmethod
    def _get_table_schema(self) -> str:
        """
        Get the CREATE TABLE SQL statement for this repository

        Returns:
            str: SQL CREATE TABLE statement
        """
        pass

    def _ensure_table_exists(self) -> Any:
        """Create table if it doesn't exist"""
        try:
            schema = self._get_table_schema()
            self._connection.execute(schema)
            self._connection.commit()
        except sqlite3.Error as e:
            self.logger.error(f"Error creating table {self.table_name}: {e}")
            raise DatabaseError(f"Failed to create table: {e}")

    @contextmanager
    def transaction(self) -> Any:
        """Context manager for database transactions"""
        cursor = self._connection.cursor()
        try:
            yield cursor
            self._connection.commit()
        except Exception as e:
            self._connection.rollback()
            self.logger.error(f"Transaction failed, rolling back: {e}")
            raise
        finally:
            cursor.close()

    def _entity_to_dict(self, entity: T) -> Dict[str, Any]:
        """Convert entity to dictionary for database storage"""
        if hasattr(entity, 'dict'):
            return entity.dict()
        elif hasattr(entity, 'to_dict'):
            return entity.to_dict()
        elif hasattr(entity, '__dict__'):
            return entity.__dict__.copy()
        else:
            raise ValueError(
                f"Cannot convert entity {type(entity)} to dictionary")

    def _dict_to_entity(self, data: Dict[str, Any]) -> T:
        """Convert dictionary from database to entity"""
        if not self._entity_class:
            raise ValueError("Entity class not specified")

        # Handle datetime fields
        processed_data = self._process_datetime_fields(data)

        # Handle JSON fields
        processed_data = self._process_json_fields(processed_data)

        try:
            return self._entity_class(**processed_data)
        except Exception as e:
            self.logger.error(f"Error creating entity from data {data}: {e}")
            raise ValueError(f"Cannot create entity: {e}")

    def _process_datetime_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process datetime fields from database"""
        processed = data.copy()

        # Common datetime field names
        datetime_fields = ['created_at', 'updated_at',
                           'start_time', 'end_time', 'timestamp']

        for field in datetime_fields:
            if field in processed and processed[field]:
                if isinstance(processed[field], str):
                    try:
                        processed[field] = datetime.fromisoformat(
                            processed[field])
                    except ValueError:
                        # Try alternative datetime format
                        try:
                            processed[field] = datetime.strptime(
                                processed[field], '%Y-%m-%d %H:%M:%S')
                        except ValueError:
                            self.logger.warning(
                                f"Could not parse datetime field {field}: {processed[field]}")

        return processed

    def _process_json_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process JSON fields from database"""
        processed = data.copy()

        # Common JSON field names
        json_fields = ['metadata', 'settings', 'config',
                       'data', 'topics', 'emotional_states']

        for field in json_fields:
            if field in processed and processed[field]:
                if isinstance(processed[field], str):
                    try:
                        processed[field] = json.loads(processed[field])
                    except json.JSONDecodeError:
                        self.logger.warning(
                            f"Could not parse JSON field {field}: {processed[field]}")

        return processed

    def _serialize_for_db(self, value: Any) -> Any:
        """Serialize complex values for database storage"""
        if isinstance(value, datetime):
            return value.isoformat()
        elif isinstance(value, (dict, list)):
            return json.dumps(value)
        elif isinstance(value, bool):
            return int(value)  # SQLite doesn't have native boolean
        return value

    # Core CRUD Operations

    async def create(self, entity: T) -> T:
        """
        Create a new entity

        Args:
            entity: Entity to create

        Returns:
            Created entity with assigned ID
        """
        try:
            with self.transaction() as cursor:
                entity_dict = self._entity_to_dict(entity)

                # Serialize complex fields
                serialized_dict = {
                    k: self._serialize_for_db(v) for k, v in entity_dict.items()
                }

                # Remove id if it's None or empty
                if 'id' in serialized_dict and not serialized_dict['id']:
                    del serialized_dict['id']

                # Prepare SQL
                columns = ', '.join(serialized_dict.keys())
                placeholders = ', '.join(['?' for _ in serialized_dict])
                sql = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"

                cursor.execute(sql, list(serialized_dict.values()))

                # Assign generated ID if applicable
                if hasattr(entity, 'id') and not entity.id:
                    entity.id = cursor.lastrowid

                return entity

        except sqlite3.Error as e:
            self.logger.error(f"Error creating entity: {e}")
            raise DatabaseError(f"Failed to create entity: {e}")

    async def get_by_id(self, entity_id: str) -> Optional[T]:
        """
        Retrieve entity by ID

        Args:
            entity_id: Unique identifier

        Returns:
            Entity or None if not found
        """
        try:
            cursor = self._connection.cursor()
            sql = f"SELECT * FROM {self.table_name} WHERE id = ?"
            cursor.execute(sql, (entity_id,))

            row = cursor.fetchone()
            if row:
                return self._dict_to_entity(dict(row))
            return None

        except sqlite3.Error as e:
            self.logger.error(f"Error retrieving entity {entity_id}: {e}")
            raise DatabaseError(f"Failed to retrieve entity: {e}")

    async def update(self, entity: T) -> T:
        """
        Update existing entity

        Args:
            entity: Entity to update

        Returns:
            Updated entity
        """
        try:
            with self.transaction() as cursor:
                entity_dict = self._entity_to_dict(entity)

                if 'id' not in entity_dict or not entity_dict['id']:
                    raise ValueError("Entity must have an ID for update")

                # Serialize complex fields
                serialized_dict = {
                    k: self._serialize_for_db(v) for k, v in entity_dict.items()
                }

                # Prepare update SQL
                update_fields = [
                    f"{k} = ?" for k in serialized_dict.keys() if k != 'id']
                update_values = [
                    v for k, v in serialized_dict.items() if k != 'id']
                update_values.append(serialized_dict['id'])

                sql = f"UPDATE {self.table_name} SET {', '.join(update_fields)} WHERE id = ?"

                cursor.execute(sql, update_values)

                if cursor.rowcount == 0:
                    raise ValueError(
                        f"No entity found with ID {entity_dict['id']}")

                return entity

        except sqlite3.Error as e:
            self.logger.error(f"Error updating entity: {e}")
            raise DatabaseError(f"Failed to update entity: {e}")

    async def delete(self, entity_id: str) -> bool:
        """
        Delete entity by ID

        Args:
            entity_id: Unique identifier

        Returns:
            True if deleted, False if not found
        """
        try:
            with self.transaction() as cursor:
                sql = f"DELETE FROM {self.table_name} WHERE id = ?"
                cursor.execute(sql, (entity_id,))
                return cursor.rowcount > 0

        except sqlite3.Error as e:
            self.logger.error(f"Error deleting entity {entity_id}: {e}")
            raise DatabaseError(f"Failed to delete entity: {e}")

    async def list(
        self,
        options: Optional[QueryOptions] = None
    ) -> List[T]:
        """
        List entities with optional filtering and sorting

        Args:
            options: Query options for filtering, sorting, pagination

        Returns:
            List of entities
        """
        try:
            cursor = self._connection.cursor()
            sql = f"SELECT * FROM {self.table_name}"
            params = []

            # Apply filtering if provided
            if options and options.filters:
                filter_conditions = []
                for key, value in options.filters.items():
                    filter_conditions.append(f"{key} = ?")
                    params.append(self._serialize_for_db(value))

                if filter_conditions:
                    sql += " WHERE " + " AND ".join(filter_conditions)

            # Apply sorting
            if options and options.sort_by:
                order = "DESC" if options.sort_order == SortOrder.DESC else "ASC"
                sql += f" ORDER BY {options.sort_by} {order}"

            # Apply pagination
            if options and options.limit:
                sql += f" LIMIT {options.limit}"

            if options and options.offset:
                sql += f" OFFSET {options.offset}"

            cursor.execute(sql, params)
            rows = cursor.fetchall()

            return [self._dict_to_entity(dict(row)) for row in rows]

        except sqlite3.Error as e:
            self.logger.error(f"Error listing entities: {e}")
            raise DatabaseError(f"Failed to list entities: {e}")

    async def search(
        self,
        criteria: List[SearchCriteria],
        options: Optional[QueryOptions] = None
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
            cursor = self._connection.cursor()
            sql = f"SELECT * FROM {self.table_name}"
            params = []

            if criteria:
                conditions = []
                for criterion in criteria:
                    condition, param = self._build_search_condition(criterion)
                    conditions.append(condition)
                    if param is not None:
                        params.append(param)

                if conditions:
                    sql += " WHERE " + " AND ".join(conditions)

            # Apply sorting
            if options and options.sort_by:
                order = "DESC" if options.sort_order == SortOrder.DESC else "ASC"
                sql += f" ORDER BY {options.sort_by} {order}"

            # Apply pagination
            if options and options.limit:
                sql += f" LIMIT {options.limit}"

            if options and options.offset:
                sql += f" OFFSET {options.offset}"

            cursor.execute(sql, params)
            rows = cursor.fetchall()

            return [self._dict_to_entity(dict(row)) for row in rows]

        except sqlite3.Error as e:
            self.logger.error(f"Error searching entities: {e}")
            raise DatabaseError(f"Failed to search entities: {e}")

    def _build_search_condition(self, criterion: SearchCriteria) -> Tuple[str, Any]:
        """Build SQL condition from search criteria"""
        field = criterion.field
        operator = criterion.operator
        value = self._serialize_for_db(criterion.value)

        if operator == 'eq':
            return f"{field} = ?", value
        elif operator == 'ne':
            return f"{field} != ?", value
        elif operator == 'gt':
            return f"{field} > ?", value
        elif operator == 'gte':
            return f"{field} >= ?", value
        elif operator == 'lt':
            return f"{field} < ?", value
        elif operator == 'lte':
            return f"{field} <= ?", value
        elif operator == 'like':
            return f"{field} LIKE ?", f"%{value}%"
        elif operator == 'ilike':
            return f"LOWER({field}) LIKE LOWER(?)", f"%{value}%"
        elif operator == 'in':
            if isinstance(value, (list, tuple)):
                placeholders = ', '.join(['?' for _ in value])
                # Handle separately
                return f"{field} IN ({placeholders})", None
            else:
                return f"{field} = ?", value
        elif operator == 'is_null':
            return f"{field} IS NULL", None
        elif operator == 'is_not_null':
            return f"{field} IS NOT NULL", None
        else:
            raise ValueError(f"Unsupported operator: {operator}")

    async def count(self, criteria: Optional[List[SearchCriteria]] = None) -> int:
        """
        Count entities matching criteria

        Args:
            criteria: Optional search criteria

        Returns:
            Number of matching entities
        """
        try:
            cursor = self._connection.cursor()
            sql = f"SELECT COUNT(*) FROM {self.table_name}"
            params = []

            if criteria:
                conditions = []
                for criterion in criteria:
                    condition, param = self._build_search_condition(criterion)
                    conditions.append(condition)
                    if param is not None:
                        params.append(param)

                if conditions:
                    sql += " WHERE " + " AND ".join(conditions)

            cursor.execute(sql, params)
            result = cursor.fetchone()

            return result[0] if result else 0

        except sqlite3.Error as e:
            self.logger.error(f"Error counting entities: {e}")
            raise DatabaseError(f"Failed to count entities: {e}")

    # Bulk Operations

    async def bulk_create(self, entities: List[T]) -> BulkOperationResult:
        """
        Create multiple entities in a single transaction

        Args:
            entities: List of entities to create

        Returns:
            Bulk operation result
        """
        success_count = 0
        failed_ids = []

        try:
            with self.transaction() as cursor:
                for entity in entities:
                    try:
                        entity_dict = self._entity_to_dict(entity)
                        serialized_dict = {
                            k: self._serialize_for_db(v) for k, v in entity_dict.items()
                        }

                        # Remove id if it's None or empty
                        if 'id' in serialized_dict and not serialized_dict['id']:
                            del serialized_dict['id']

                        columns = ', '.join(serialized_dict.keys())
                        placeholders = ', '.join(
                            ['?' for _ in serialized_dict])
                        sql = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"

                        cursor.execute(sql, list(serialized_dict.values()))

                        # Assign generated ID if applicable
                        if hasattr(entity, 'id') and not entity.id:
                            entity.id = cursor.lastrowid

                        success_count += 1

                    except Exception as e:
                        entity_id = getattr(entity, 'id', 'unknown')
                        failed_ids.append(entity_id)
                        self.logger.error(
                            f"Failed to create entity {entity_id}: {e}")

        except sqlite3.Error as e:
            self.logger.error(f"Bulk create failed: {e}")
            raise DatabaseError(f"Bulk create failed: {e}")

        return BulkOperationResult(
            success_count=success_count,
            failed_count=len(failed_ids),
            failed_ids=failed_ids
        )

    async def bulk_update(self, entities: List[T]) -> BulkOperationResult:
        """
        Update multiple entities in a single transaction

        Args:
            entities: List of entities to update

        Returns:
            Bulk operation result
        """
        success_count = 0
        failed_ids = []

        try:
            with self.transaction() as cursor:
                for entity in entities:
                    try:
                        entity_dict = self._entity_to_dict(entity)

                        if 'id' not in entity_dict or not entity_dict['id']:
                            failed_ids.append('unknown')
                            continue

                        serialized_dict = {
                            k: self._serialize_for_db(v) for k, v in entity_dict.items()
                        }

                        update_fields = [
                            f"{k} = ?" for k in serialized_dict.keys() if k != 'id']
                        update_values = [
                            v for k, v in serialized_dict.items() if k != 'id']
                        update_values.append(serialized_dict['id'])

                        sql = f"UPDATE {self.table_name} SET {', '.join(update_fields)} WHERE id = ?"

                        cursor.execute(sql, update_values)

                        if cursor.rowcount > 0:
                            success_count += 1
                        else:
                            failed_ids.append(entity_dict['id'])

                    except Exception as e:
                        entity_id = getattr(entity, 'id', 'unknown')
                        failed_ids.append(entity_id)
                        self.logger.error(
                            f"Failed to update entity {entity_id}: {e}")

        except sqlite3.Error as e:
            self.logger.error(f"Bulk update failed: {e}")
            raise DatabaseError(f"Bulk update failed: {e}")

        return BulkOperationResult(
            success_count=success_count,
            failed_count=len(failed_ids),
            failed_ids=failed_ids
        )

    async def bulk_delete(self, entity_ids: List[str]) -> BulkOperationResult:
        """
        Delete multiple entities in a single transaction

        Args:
            entity_ids: List of entity IDs to delete

        Returns:
            Bulk operation result
        """
        success_count = 0
        failed_ids = []

        try:
            with self.transaction() as cursor:
                for entity_id in entity_ids:
                    try:
                        sql = f"DELETE FROM {self.table_name} WHERE id = ?"
                        cursor.execute(sql, (entity_id,))

                        if cursor.rowcount > 0:
                            success_count += 1
                        else:
                            failed_ids.append(entity_id)

                    except Exception as e:
                        failed_ids.append(entity_id)
                        self.logger.error(
                            f"Failed to delete entity {entity_id}: {e}")

        except sqlite3.Error as e:
            self.logger.error(f"Bulk delete failed: {e}")
            raise DatabaseError(f"Bulk delete failed: {e}")

        return BulkOperationResult(
            success_count=success_count,
            failed_count=len(failed_ids),
            failed_ids=failed_ids
        )

    # Advanced Query Methods

    async def exists(self, entity_id: str) -> bool:
        """
        Check if entity exists

        Args:
            entity_id: Entity ID to check

        Returns:
            True if entity exists
        """
        try:
            cursor = self._connection.cursor()
            sql = f"SELECT 1 FROM {self.table_name} WHERE id = ? LIMIT 1"
            cursor.execute(sql, (entity_id,))
            return cursor.fetchone() is not None

        except sqlite3.Error as e:
            self.logger.error(f"Error checking entity existence: {e}")
            raise DatabaseError(f"Failed to check entity existence: {e}")

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
        Find entities by single field value

        Args:
            field: Field name
            value: Field value

        Returns:
            List of matching entities
        """
        criteria = [SearchCriteria(field, 'eq', value)]
        return await self.search(criteria)

    # Utility Methods

    def get_table_info(self) -> Dict[str, Any]:
        """Get table information and schema"""
        try:
            cursor = self._connection.cursor()

            # Get table info
            cursor.execute(f"PRAGMA table_info({self.table_name})")
            columns = cursor.fetchall()

            # Get indexes
            cursor.execute(f"PRAGMA index_list({self.table_name})")
            indexes = cursor.fetchall()

            # Get foreign keys
            cursor.execute(f"PRAGMA foreign_key_list({self.table_name})")
            foreign_keys = cursor.fetchall()

            return {
                'table_name': self.table_name,
                'columns': [dict(col) for col in columns],
                'indexes': [dict(idx) for idx in indexes],
                'foreign_keys': [dict(fk) for fk in foreign_keys]
            }

        except sqlite3.Error as e:
            self.logger.error(f"Error getting table info: {e}")
            raise DatabaseError(f"Failed to get table info: {e}")

    def vacuum(self) -> Any:
        """Vacuum database to reclaim space and optimize"""
        try:
            self._connection.execute("VACUUM")
            self._connection.commit()

        except sqlite3.Error as e:
            self.logger.error(f"Error vacuuming database: {e}")
            raise DatabaseError(f"Failed to vacuum database: {e}")

    def analyze(self) -> Any:
        """Analyze database to update query planner statistics"""
        try:
            self._connection.execute("ANALYZE")
            self._connection.commit()

        except sqlite3.Error as e:
            self.logger.error(f"Error analyzing database: {e}")
            raise DatabaseError(f"Failed to analyze database: {e}")

    def close(self) -> Any:
        """Close database connection"""
        if self._connection:
            self._connection.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    async def aggregate(self, field: str, operation: str, criteria: Optional[List[SearchCriteria]] = None) -> Any:
        """
        Perform aggregation operation

        Args:
            field: Field to aggregate
            operation: Aggregation operation (sum, avg, max, min, count)
            criteria: Optional search criteria

        Returns:
            Aggregation result
        """
        try:
            cursor = self._connection.cursor()

            # Build aggregation function
            if operation.lower() == 'count':
                agg_func = f"COUNT({field})"
            elif operation.lower() == 'sum':
                agg_func = f"SUM({field})"
            elif operation.lower() == 'avg':
                agg_func = f"AVG({field})"
            elif operation.lower() == 'max':
                agg_func = f"MAX({field})"
            elif operation.lower() == 'min':
                agg_func = f"MIN({field})"
            else:
                raise ValueError(
                    f"Unsupported aggregation operation: {operation}")

            sql = f"SELECT {agg_func} FROM {self.table_name}"
            params = []

            if criteria:
                conditions = []
                for criterion in criteria:
                    condition, param = self._build_search_condition(criterion)
                    conditions.append(condition)
                    if param is not None:
                        params.append(param)

                if conditions:
                    sql += " WHERE " + " AND ".join(conditions)

            cursor.execute(sql, params)
            result = cursor.fetchone()

            return result[0] if result else None

        except sqlite3.Error as e:
            self.logger.error(f"Error performing aggregation: {e}")
            raise DatabaseError(f"Failed to perform aggregation: {e}")

    async def execute_safe_query(self, sql: str, params: tuple = ()):
        """Execute parameterized query only, prevent SQL injection"""
        if not isinstance(sql, str) or not sql.strip():
            self.logger.error("Invalid SQL query")
            raise ValueError("Invalid SQL query")
        if not isinstance(params, (tuple, list)):
            self.logger.error("Query parameters must be tuple or list")
            raise ValueError("Query parameters must be tuple or list")
        try:
            cursor = self._connection.cursor()
            cursor.execute(sql, params)
            return cursor
        except Exception as e:
            self.logger.error(f"SQL execution error: {e}")
            raise


async def get(self, entity_id: str) -> Optional[T]:
    """
    Alias for get_by_id for compatibility

    Args:
        entity_id: Entity ID

    Returns:
        Entity or None
    """
    return await self.get_by_id(entity_id)


def get_table_schema(self) -> str:
    """
    Public method to get table schema

    Returns:
        CREATE TABLE SQL statement
    """
    return self._get_table_schema()