"""
Child SQLite Repository - Refactored

Clean Architecture implementation of Child Repository with separated concerns.
"""

import json
import os
import sqlite3
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.core.domain.entities.child import Child
from src.infrastructure.persistence.base import QueryOptions, SortOrder
from src.infrastructure.persistence.base_sqlite_repository import BaseSQLiteRepository
from src.infrastructure.persistence.child_repository import ChildRepository


class ChildSQLiteRepositoryRefactored(
    BaseSQLiteRepository[Child, int], ChildRepository
):
    """
    Refactored SQLite implementation of Child Repository
    Following Clean Architecture with separated concerns
    """

    _columns = [
        "id",
        "name",
        "age",
        "date_of_birth",
        "gender",
        "interests",
        "personality_traits",
        "learning_preferences",
        "communication_style",
        "max_daily_interaction_time",
        "allowed_topics",
        "restricted_topics",
        "language_preference",
        "cultural_background",
        "parental_controls",
        "emergency_contacts",
        "medical_notes",
        "educational_level",
        "special_needs",
        "created_at",
        "updated_at",
        "last_interaction",
        "total_interaction_time",
        "is_active",
        "privacy_settings",
        "custom_settings",
    ]

    def __init__(
        self,
        session_factory,
        db_path: str = os.path.join(
            os.path.dirname(__file__), "..", "..", "..", "data", "teddyai.db"
        ),
    ):
        self.session_factory = session_factory

        # Ensure data directory exists
        data_dir = os.path.dirname(db_path)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)

        # Create connection
        connection = sqlite3.connect(db_path, check_same_thread=False)

        super().__init__(
            connection=connection, table_name="children", entity_class=Child
        )

    async def initialize(self):
        """Initialize repository (no-op for backwards compatibility)"""
        pass

    def _get_table_schema(self) -> str:
        """Get the CREATE TABLE SQL statement for children table"""
        return """
            CREATE TABLE IF NOT EXISTS children (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                date_of_birth DATE,
                gender TEXT,
                interests TEXT,
                personality_traits TEXT,
                learning_preferences TEXT,
                communication_style TEXT,
                max_daily_interaction_time INTEGER DEFAULT 3600,
                allowed_topics TEXT,
                restricted_topics TEXT,
                language_preference TEXT DEFAULT 'en',
                cultural_background TEXT,
                parental_controls TEXT,
                emergency_contacts TEXT,
                medical_notes TEXT,
                educational_level TEXT,
                special_needs TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_interaction DATETIME,
                total_interaction_time INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                privacy_settings TEXT,
                custom_settings TEXT
            )
        """

    # ======= CORE CRUD OPERATIONS =======

    async def create(self, child: Child) -> Child:
        """Create a new child profile"""
        try:
            with self.transaction() as cursor:
                data = self._serialize_child_for_db(child)

                columns = ", ".join(data.keys())
                placeholders = ", ".join(["?" for _ in data])
                sql = (
                    f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
                )

                cursor.execute(sql, list(data.values()))

                if not child.id:
                    child.id = data["id"]

                return child

        except sqlite3.Error as e:
            self.logger.error(f"Error creating child: {e}")
            raise

    async def get_by_id(self, child_id: str) -> Optional[Child]:
        """Retrieve child by ID"""
        try:
            cursor = self._connection.cursor()
            sql = f"SELECT * FROM {self.table_name} WHERE id = ? AND is_active = 1"
            cursor.execute(sql, (child_id,))

            row = cursor.fetchone()
            if row:
                return self._deserialize_child_from_db(dict(row))
            return None

        except sqlite3.Error as e:
            self.logger.error(f"Error retrieving child {child_id}: {e}")
            raise

    def _prepare_update_data(self, child: Child) -> Dict[str, Any]:
        """Prepares child data for the update operation."""
        data = self._serialize_child_for_db(child)
        update_data = {
            k: v
            for k, v in data.items()
            if k in self._columns and k not in ("id", "created_at")
        }
        if not update_data:
            self.logger.warning(
                f"No valid fields to update for child {child.id}")
            return {}

        update_data["updated_at"] = datetime.now().isoformat()
        return update_data

    def _build_update_query(self, update_data: Dict) -> (str, List[Any]):
        """Builds the SQL UPDATE query and its corresponding values."""
        update_fields = ", ".join([f"{k} = ?" for k in update_data.keys()])
        update_values = list(update_data.values())
        sql = f"UPDATE {self.table_name} SET {update_fields} WHERE id = ?"
        return sql, update_values

    async def update(self, child: Child) -> Child:
        """Update existing child profile"""
        if not child.id:
            raise ValueError("Child must have an ID for update")

        try:
            with self.transaction() as cursor:
                update_data = self._prepare_update_data(child)
                if not update_data:
                    return child

                sql, update_values = self._build_update_query(update_data)
                update_values.append(child.id)

                cursor.execute(sql, update_values)

                if cursor.rowcount == 0:
                    raise ValueError(f"No child found with ID {child.id}")

                return child

        except sqlite3.Error as e:
            self.logger.error(f"Error updating child {child.id}: {e}")
            raise

    async def delete(self, child_id: str) -> bool:
        """Soft delete child (mark as inactive)"""
        try:
            with self.transaction() as cursor:
                sql = f"UPDATE {self.table_name} SET is_active = 0, updated_at = ? WHERE id = ?"
                cursor.execute(sql, (datetime.now().isoformat(), child_id))
                return cursor.rowcount > 0

        except sqlite3.Error as e:
            self.logger.error(f"Error deleting child {child_id}: {e}")
            raise

    def _apply_sorting(self, sql: str, options: QueryOptions) -> str:
        """Applies sorting to the SQL query if specified in options."""
        if hasattr(options, "sort_by") and options.sort_by:
            if options.sort_by not in self._columns:
                raise ValueError(f"Invalid sort column: {options.sort_by}")
            order = (
                "DESC"
                if hasattr(options, "sort_order")
                and options.sort_order == SortOrder.DESC
                else "ASC"
            )
            sql += f" ORDER BY {options.sort_by} {order}"
        return sql

    def _apply_pagination(
        self, sql: str, params: List, options: QueryOptions
    ) -> (str, List):
        """Applies pagination (limit and offset) to the SQL query."""
        if hasattr(options, "limit") and options.limit:
            sql += " LIMIT ?"
            params.append(options.limit)
        if hasattr(options, "offset") and options.offset:
            sql += " OFFSET ?"
            params.append(options.offset)
        return sql, params

    async def list(
            self,
            options: Optional[QueryOptions] = None) -> List[Child]:
        """List active children with optional filtering and sorting"""
        try:
            cursor = self._connection.cursor()
            sql = f"SELECT * FROM {self.table_name} WHERE is_active = 1"
            params = []

            if options:
                sql = self._apply_sorting(sql, options)
                sql, params = self._apply_pagination(sql, params, options)

            cursor.execute(sql, params)
            rows = cursor.fetchall()

            return [self._deserialize_child_from_db(dict(row)) for row in rows]

        except sqlite3.Error as e:
            self.logger.error(f"Error listing children: {e}")
            raise

    # ======= DELEGATION TO ORIGINAL METHODS =======

    async def find_by_name(self, name: str) -> Optional[Child]:
        """Delegate to original implementation"""
        return (
            await super().find_by_name(name)
            if hasattr(super(), "find_by_name")
            else None
        )

    async def find_by_age_range(
            self,
            min_age: int,
            max_age: int) -> List[Child]:
        """Delegate to original implementation"""
        return (
            await super().find_by_age_range(min_age, max_age)
            if hasattr(super(), "find_by_age_range")
            else []
        )

    # ======= HELPER METHODS =======

    def _serialize_child_for_db(self, child: Child) -> Dict[str, Any]:
        """Serialize child entity for database storage"""
        data = child.dict() if hasattr(child, "dict") else child.__dict__.copy()

        if not data.get("id"):
            data["id"] = str(uuid.uuid4())

        # Serialize complex fields to JSON
        json_fields = [
            "interests",
            "personality_traits",
            "learning_preferences",
            "allowed_topics",
            "restricted_topics",
            "parental_controls",
            "emergency_contacts",
            "privacy_settings",
            "custom_settings",
        ]

        for field in json_fields:
            if field in data and data[field] is not None:
                data[field] = json.dumps(data[field])

        # Handle datetime fields
        if "date_of_birth" in data and isinstance(
                data["date_of_birth"], datetime):
            data["date_of_birth"] = data["date_of_birth"].date().isoformat()

        # Set updated_at timestamp
        data["updated_at"] = datetime.now().isoformat()

        return data

    def _deserialize_json_fields(self, data: Dict[str, Any]):
        """Deserializes all JSON-encoded fields in the data dictionary."""
        json_fields = [
            "interests",
            "personality_traits",
            "learning_preferences",
            "allowed_topics",
            "restricted_topics",
            "parental_controls",
            "emergency_contacts",
            "privacy_settings",
            "custom_settings",
        ]
        for field in json_fields:
            if field in data and data[field]:
                try:
                    data[field] = json.loads(data[field])
                except (json.JSONDecodeError, TypeError):
                    data[field] = [] if field.endswith("s") else {}
            else:
                data[field] = [] if field.endswith("s") else {}

    def _deserialize_datetime_fields(self, data: Dict[str, Any]):
        """Deserializes all datetime fields in the data dictionary."""
        datetime_fields = ["created_at", "updated_at", "last_interaction"]
        for field in datetime_fields:
            if field in data and data[field]:
                try:
                    data[field] = datetime.fromisoformat(data[field])
                except (ValueError, TypeError):
                    data[field] = None

    def _deserialize_date_fields(self, data: Dict[str, Any]):
        """Deserializes all date fields in the data dictionary."""
        if "date_of_birth" in data and data["date_of_birth"]:
            try:
                data["date_of_birth"] = datetime.fromisoformat(
                    data["date_of_birth"]
                ).date()
            except (ValueError, TypeError):
                data["date_of_birth"] = None

    def _deserialize_boolean_fields(self, data: Dict[str, Any]):
        """Deserializes all boolean fields in the data dictionary."""
        if "is_active" in data:
            data["is_active"] = bool(data["is_active"])

    def _deserialize_child_from_db(self, data: Dict[str, Any]) -> Child:
        """Deserialize child data from database"""
        self._deserialize_json_fields(data)
        self._deserialize_datetime_fields(data)
        self._deserialize_date_fields(data)
        self._deserialize_boolean_fields(data)
        return Child(**data)
