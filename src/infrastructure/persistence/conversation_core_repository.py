"""Core conversation repository with CRUD operations."""

import json
import logging
import sqlite3
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from src.core.domain.entities.conversation import Conversation
from src.infrastructure.persistence.base_sqlite_repository import BaseSQLiteRepository


class ConversationCoreRepository:
    """Core repository for conversation CRUD operations."""

    def __init__(self, connection: sqlite3.Connection):
        """Initialize core repository with database connection."""
        self.connection = connection
        self.table_name = "conversations"
        self.logger = logging.getLogger(__name__)

    async def create(self, conversation: Conversation) -> Conversation:
        """Create a new conversation."""
        try:
            cursor = self.connection.cursor()
            data = self._serialize_conversation_for_db(conversation)

            columns = ", ".join(data.keys())
            placeholders = ", ".join(["?" for _ in data])
            sql = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"

            cursor.execute(sql, list(data.values()))
            self.connection.commit()

            # Assign ID if not already present
            if not conversation.id:
                conversation.id = data["id"]

            return conversation

        except sqlite3.Error as e:
            self.logger.error(f"Error creating conversation: {e}")
            raise

    async def get_by_id(self, conversation_id: str) -> Optional[Conversation]:
        """Retrieve conversation by ID."""
        try:
            cursor = self.connection.cursor()
            sql = f"SELECT * FROM {self.table_name} WHERE id = ? AND archived = 0"
            cursor.execute(sql, (conversation_id,))

            row = cursor.fetchone()
            if row:
                return self._deserialize_conversation_from_db(dict(row))
            return None

        except sqlite3.Error as e:
            self.logger.error(f"Error retrieving conversation {conversation_id}: {e}")
            raise

    async def get_by_session_id(self, session_id: str) -> Optional[Conversation]:
        """Get conversation by session ID."""
        try:
            cursor = self.connection.cursor()
            sql = f"SELECT * FROM {self.table_name} WHERE session_id = ? AND archived = 0"
            cursor.execute(sql, (session_id,))

            row = cursor.fetchone()
            if row:
                return self._deserialize_conversation_from_db(dict(row))
            return None

        except sqlite3.Error as e:
            self.logger.error(f"Error retrieving conversation by session {session_id}: {e}")
            raise

    async def update(self, conversation: Conversation) -> Conversation:
        """Update existing conversation."""
        try:
            cursor = self.connection.cursor()
            data = self._serialize_conversation_for_db(conversation)

            if "id" not in data or not data["id"]:
                raise ValueError("Conversation must have an ID for update")

            # Prepare update SQL
            update_fields = [f"{k} = ?" for k in data.keys() if k != "id"]
            update_values = [v for k, v in data.items() if k != "id"]
            update_values.append(data["id"])

            sql = f"UPDATE {self.table_name} SET {', '.join(update_fields)} WHERE id = ?"

            cursor.execute(sql, update_values)
            self.connection.commit()

            if cursor.rowcount == 0:
                raise ValueError(f"No conversation found with ID {data['id']}")

            return conversation

        except sqlite3.Error as e:
            self.logger.error(f"Error updating conversation: {e}")
            raise

    async def delete(self, conversation_id: str) -> bool:
        """Soft delete conversation (mark as archived)."""
        try:
            cursor = self.connection.cursor()
            sql = f"UPDATE {self.table_name} SET archived = 1, updated_at = ? WHERE id = ?"
            cursor.execute(sql, (datetime.now().isoformat(), conversation_id))
            self.connection.commit()
            return cursor.rowcount > 0

        except sqlite3.Error as e:
            self.logger.error(f"Error deleting conversation {conversation_id}: {e}")
            raise

    async def get_conversations_by_child(
        self,
        child_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> List[Conversation]:
        """Retrieve conversations for a specific child."""
        try:
            cursor = self.connection.cursor()
            sql = f"SELECT * FROM {self.table_name} WHERE child_id = ? AND archived = 0"
            params = [child_id]

            if start_date:
                sql += " AND start_time >= ?"
                params.append(start_date.isoformat())

            if end_date:
                sql += " AND start_time <= ?"
                params.append(end_date.isoformat())

            sql += " ORDER BY start_time DESC"

            if limit:
                sql += f" LIMIT {limit}"

            cursor.execute(sql, params)
            rows = cursor.fetchall()

            return [self._deserialize_conversation_from_db(dict(row)) for row in rows]

        except sqlite3.Error as e:
            self.logger.error(f"Error retrieving conversations for child {child_id}: {e}")
            raise

    def _serialize_conversation_for_db(self, conversation: Conversation) -> Dict[str, Any]:
        """Serialize conversation entity for database storage."""
        data = conversation.__dict__.copy() if hasattr(conversation, "__dict__") else {}

        # Generate ID if not present
        if not data.get("id"):
            data["id"] = str(uuid.uuid4())

        # Serialize complex fields to JSON
        json_fields = ["topics", "metadata"]
        for field in json_fields:
            if field in data and data[field] is not None:
                data[field] = json.dumps(data[field])

        # Handle datetime fields
        datetime_fields = ["start_time", "end_time", "created_at", "updated_at"]
        for field in datetime_fields:
            if field in data and data[field] and isinstance(data[field], datetime):
                data[field] = data[field].isoformat()

        # Handle duration (timedelta to seconds)
        if "duration" in data and data["duration"]:
            if hasattr(data["duration"], "total_seconds"):
                data["duration"] = int(data["duration"].total_seconds())

        # Set updated timestamp
        data["updated_at"] = datetime.now().isoformat()

        return data

    def _deserialize_conversation_from_db(self, data: Dict[str, Any]) -> Conversation:
        """Deserialize conversation data from database."""
        # Parse JSON fields
        json_fields = ["topics", "metadata"]
        for field in json_fields:
            if field in data and data[field]:
                try:
                    data[field] = json.loads(data[field])
                except (json.JSONDecodeError, TypeError):
                    data[field] = [] if field == "topics" else {}
            else:
                data[field] = [] if field == "topics" else {}

        # Parse datetime fields
        datetime_fields = ["start_time", "end_time", "created_at", "updated_at"]
        for field in datetime_fields:
            if field in data and data[field]:
                try:
                    data[field] = datetime.fromisoformat(data[field])
                except (ValueError, TypeError):
                    data[field] = None

        # Convert duration from seconds to timedelta
        if "duration" in data and data["duration"]:
            try:
                data["duration"] = timedelta(seconds=int(data["duration"]))
            except (ValueError, TypeError):
                data["duration"] = None

        # Convert boolean fields
        bool_fields = ["parent_visible", "archived"]
        for field in bool_fields:
            if field in data:
                data[field] = bool(data[field])

        # Create and return conversation (simplified for this case)
        return Conversation(**data)

    def transaction(self):
        """Create a transaction context manager."""
        return TransactionContext(self.connection)


class TransactionContext:
    """Simple transaction context manager."""

    def __init__(self, connection):
        self.connection = connection

    def __enter__(self):
        return self.connection.cursor()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.connection.commit()
        else:
            self.connection.rollback()
