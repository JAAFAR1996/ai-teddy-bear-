"""Conversation search service."""

import json
import logging
import sqlite3
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple


class ConversationSearchService:
    """Service for searching and filtering conversations."""

    def __init__(self, connection: sqlite3.Connection):
        """Initialize search service with database connection."""
        self.connection = connection
        self.logger = logging.getLogger(__name__)

    async def search_conversation_content(
        self, query: str, child_id: Optional[str] = None, search_in: List[str] = None
    ) -> List[Tuple[Dict[str, Any], List[Dict[str, Any]]]]:
        """Full-text search in conversation messages."""
        if search_in is None:
            search_in = ["user", "assistant"]

        try:
            cursor = self.connection.cursor()

            # Build search query
            role_conditions = []
            for role in search_in:
                role_conditions.append("m.role = ?")

            sql = f"""
                SELECT DISTINCT c.*, m.id as message_id, m.content, m.role, m.timestamp as msg_timestamp
                FROM conversations c
                JOIN messages m ON c.id = m.conversation_id
                WHERE ({' OR '.join(role_conditions)}) 
                AND m.content LIKE ? 
                AND c.archived = 0
            """

            params = search_in.copy()
            params.append(f"%{query}%")

            if child_id:
                sql += " AND c.child_id = ?"
                params.append(child_id)

            sql += " ORDER BY c.start_time DESC"

            cursor.execute(sql, params)
            rows = cursor.fetchall()

            # Group results by conversation
            conversation_messages = defaultdict(list)
            conversations = {}

            for row in rows:
                row_dict = dict(row)
                conv_id = row_dict["id"]

                # Create conversation object if not exists
                if conv_id not in conversations:
                    conv_data = {
                        k: v
                        for k, v in row_dict.items()
                        if k not in ["message_id", "content", "role", "msg_timestamp"]
                    }
                    conversations[conv_id] = conv_data

                # Create message object
                message = {
                    "id": row_dict["message_id"],
                    "role": row_dict["role"],
                    "content": row_dict["content"],
                    "timestamp": row_dict["msg_timestamp"],
                }
                conversation_messages[conv_id].append(message)

            # Return list of (conversation, matching_messages) tuples
            results = []
            for conv_id, conv in conversations.items():
                results.append((conv, conversation_messages[conv_id]))

            return results

        except sqlite3.Error as e:
            self.logger.error(f"Error searching conversation content: {e}")
            raise

    async def get_conversations_by_topics(
        self, topics: List[str], match_all: bool = False, child_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get conversations that contain specific topics."""
        try:
            cursor = self.connection.cursor()

            sql = "SELECT * FROM conversations WHERE archived = 0"
            params = []

            if child_id:
                sql += " AND child_id = ?"
                params.append(child_id)

            # We'll filter topics in Python since SQLite JSON functions are limited
            cursor.execute(sql, params)
            all_conversations = cursor.fetchall()

            # Filter by topics
            matching_conversations = []
            for conv in all_conversations:
                conv_dict = dict(conv)
                if conv_dict["topics"]:
                    try:
                        conv_topics = json.loads(conv_dict["topics"])
                        if match_all:
                            # All requested topics must be present
                            if all(topic in conv_topics for topic in topics):
                                matching_conversations.append(conv_dict)
                        else:
                            # Any of the requested topics must be present
                            if any(topic in conv_topics for topic in topics):
                                matching_conversations.append(conv_dict)
                    except json.JSONDecodeError:
                        continue

            return matching_conversations

        except sqlite3.Error as e:
            self.logger.error(f"Error searching conversations by topics: {e}")
            raise

    async def get_conversations_by_emotional_tone(
        self, emotion: str, threshold: float = 0.5, child_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get conversations with specific emotional tone."""
        try:
            cursor = self.connection.cursor()

            # Join with emotional_states table
            sql = """
                SELECT DISTINCT c.* FROM conversations c
                JOIN emotional_states e ON c.id = e.conversation_id
                WHERE e.primary_emotion = ? 
                AND e.confidence >= ? 
                AND c.archived = 0
            """
            params = [emotion, threshold]

            if child_id:
                sql += " AND c.child_id = ?"
                params.append(child_id)

            sql += " ORDER BY c.start_time DESC"

            cursor.execute(sql, params)
            return [dict(row) for row in cursor.fetchall()]

        except sqlite3.Error as e:
            self.logger.error(f"Error searching conversations by emotion: {e}")
            raise

    async def get_conversations_by_time_range(
        self, start_date: datetime, end_date: datetime, child_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get conversations in a specific time range."""
        try:
            cursor = self.connection.cursor()

            sql = """
                SELECT * FROM conversations
                WHERE start_time BETWEEN ? AND ? AND archived = 0
            """
            params = [start_date.isoformat(), end_date.isoformat()]

            if child_id:
                sql += " AND child_id = ?"
                params.append(child_id)

            sql += " ORDER BY start_time DESC"

            cursor.execute(sql, params)
            return [dict(row) for row in cursor.fetchall()]

        except sqlite3.Error as e:
            self.logger.error(f"Error retrieving conversations in range: {e}")
            raise

    async def get_conversations_requiring_review(self) -> List[Dict[str, Any]]:
        """Find conversations that may require manual review."""
        try:
            cursor = self.connection.cursor()

            # Conversations with low safety scores or high moderation flags
            sql = """
                SELECT * FROM conversations 
                WHERE (
                    safety_score < 0.8 OR 
                    moderation_flags > 2 OR
                    (total_messages > 50 AND duration < 300)
                ) AND archived = 0
                ORDER BY safety_score ASC, moderation_flags DESC
            """

            cursor.execute(sql)
            return [dict(row) for row in cursor.fetchall()]

        except sqlite3.Error as e:
            self.logger.error(f"Error finding conversations requiring review: {e}")
            raise

    async def get_active_conversations(
        self, inactive_threshold_minutes: int = 30
    ) -> List[Dict[str, Any]]:
        """Get currently active conversations."""
        try:
            cursor = self.connection.cursor()

            threshold = datetime.now() - timedelta(minutes=inactive_threshold_minutes)

            sql = """
                SELECT * FROM conversations
                WHERE end_time IS NULL AND start_time >= ? AND archived = 0
                ORDER BY start_time DESC
            """
            cursor.execute(sql, (threshold.isoformat(),))

            return [dict(row) for row in cursor.fetchall()]

        except sqlite3.Error as e:
            self.logger.error(f"Error retrieving active conversations: {e}")
            raise
