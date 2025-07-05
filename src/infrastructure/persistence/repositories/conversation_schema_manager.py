"""Conversation database schema manager."""

import logging
import sqlite3
from datetime import datetime
from typing import Any, Dict


class ConversationSchemaManager:
    """Manages database schema for conversations and related tables."""

    def __init__(self, connection: sqlite3.Connection):
        """Initialize schema manager with database connection."""
        self.connection = connection
        self.logger = logging.getLogger(__name__)

    def create_all_tables(self):
        """Create all conversation-related tables."""
        self._create_conversations_table()
        self._create_messages_table()
        self._create_emotional_states_table()
        self._create_indexes()

    def _create_conversations_table(self):
        """Create the main conversations table."""
        schema = """
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                session_id TEXT,
                child_id TEXT NOT NULL,
                parent_id TEXT,
                start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                end_time DATETIME,
                duration INTEGER DEFAULT 0,
                interaction_type TEXT DEFAULT 'general',
                topics TEXT,
                primary_language TEXT DEFAULT 'en',
                quality_score REAL,
                safety_score REAL DEFAULT 1.0,
                educational_score REAL DEFAULT 0.0,
                engagement_score REAL DEFAULT 0.0,
                llm_provider TEXT,
                model_version TEXT,
                context_summary TEXT,
                metadata TEXT,
                total_messages INTEGER DEFAULT 0,
                child_messages INTEGER DEFAULT 0,
                assistant_messages INTEGER DEFAULT 0,
                questions_asked INTEGER DEFAULT 0,
                moderation_flags INTEGER DEFAULT 0,
                parent_visible BOOLEAN DEFAULT 1,
                archived BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(child_id) REFERENCES children(id)
            )
        """
        try:
            self.connection.execute(schema)
            self.connection.commit()
            self.logger.info("Conversations table created successfully")
        except sqlite3.Error as e:
            self.logger.error(f"Error creating conversations table: {e}")
            raise

    def _create_messages_table(self):
        """Create messages table for storing individual messages."""
        schema = """
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                content_type TEXT DEFAULT 'text',
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                sequence_number INTEGER,
                metadata TEXT,
                moderation_flags TEXT,
                embedding_vector BLOB,
                FOREIGN KEY(conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
            )
        """
        try:
            self.connection.execute(schema)
            self.connection.commit()
            self.logger.info("Messages table created successfully")
        except sqlite3.Error as e:
            self.logger.error(f"Error creating messages table: {e}")
            raise

    def _create_emotional_states_table(self):
        """Create emotional states table."""
        schema = """
            CREATE TABLE IF NOT EXISTS emotional_states (
                id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                primary_emotion TEXT NOT NULL,
                confidence REAL DEFAULT 0.0,
                secondary_emotions TEXT,
                arousal_level REAL DEFAULT 0.0,
                valence_level REAL DEFAULT 0.0,
                emotional_context TEXT,
                FOREIGN KEY(conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
            )
        """
        try:
            self.connection.execute(schema)
            self.connection.commit()
            self.logger.info("Emotional states table created successfully")
        except sqlite3.Error as e:
            self.logger.error(f"Error creating emotional_states table: {e}")
            raise

    def _create_indexes(self):
        """Create database indexes for performance."""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_conversations_child_id ON conversations (child_id)",
            "CREATE INDEX IF NOT EXISTS idx_conversations_start_time ON conversations (start_time)",
            "CREATE INDEX IF NOT EXISTS idx_conversations_session_id ON conversations (session_id)",
            "CREATE INDEX IF NOT EXISTS idx_conversations_archived ON conversations (archived)",
            "CREATE INDEX IF NOT EXISTS idx_conversations_safety_score ON conversations (safety_score)",
            "CREATE INDEX IF NOT EXISTS idx_conversations_quality_score ON conversations (quality_score)",
            "CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages (conversation_id)",
            "CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages (timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_messages_role ON messages (role)",
            "CREATE INDEX IF NOT EXISTS idx_messages_content_search ON messages (content)",
            "CREATE INDEX IF NOT EXISTS idx_emotional_states_conversation_id ON emotional_states (conversation_id)",
            "CREATE INDEX IF NOT EXISTS idx_emotional_states_primary_emotion ON emotional_states (primary_emotion)",
            "CREATE INDEX IF NOT EXISTS idx_emotional_states_timestamp ON emotional_states (timestamp)",
        ]

        try:
            for index_sql in indexes:
                self.connection.execute(index_sql)
            self.connection.commit()
            self.logger.info("Database indexes created successfully")
        except sqlite3.Error as e:
            self.logger.error(f"Error creating indexes: {e}")
            raise

    def validate_schema(self) -> Dict[str, Any]:
        """Validate database schema integrity."""
        try:
            cursor = self.connection.cursor()

            # Check if all required tables exist
            required_tables = ["conversations", "messages", "emotional_states"]
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = [row[0] for row in cursor.fetchall()]

            missing_tables = [
                table for table in required_tables if table not in existing_tables]

            # Check foreign key constraints
            cursor.execute("PRAGMA foreign_key_check")
            fk_violations = cursor.fetchall()

            # Check indexes
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
            existing_indexes = [row[0] for row in cursor.fetchall()]

            return {
                "status": (
                    "valid" if not missing_tables and not fk_violations else "invalid"),
                "missing_tables": missing_tables,
                "foreign_key_violations": len(fk_violations),
                "total_indexes": len(existing_indexes),
                "validation_timestamp": datetime.now().isoformat(),
            }

        except sqlite3.Error as e:
            self.logger.error(f"Error validating schema: {e}")
            return {"status": "error", "message": str(e)}
