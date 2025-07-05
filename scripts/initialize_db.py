import logging
import os
import sqlite3
import sys
from datetime import datetime


def create_database(db_path: str = "data/child_memories.db"):
    """
    Initialize the SQLite database with required schemas

    :param db_path: Path to the SQLite database file
    """
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    try:
        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create child profiles table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS child_profiles (
            child_id TEXT PRIMARY KEY,
            name TEXT,
            age INTEGER,
            interests TEXT,
            personality TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
        )

        # Create conversation history table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS conversation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            child_id TEXT,
            timestamp DATETIME,
            conversation_context TEXT,
            sentiment TEXT,
            duration INTEGER,
            FOREIGN KEY(child_id) REFERENCES child_profiles(child_id)
        )
        """
        )

        # Create parent notifications table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS parent_notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            child_id TEXT,
            notification_type TEXT,
            details TEXT,
            timestamp DATETIME,
            is_read BOOLEAN DEFAULT 0,
            FOREIGN KEY(child_id) REFERENCES child_profiles(child_id)
        )
        """
        )

        # Create safety violation tracking table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS safety_violations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            child_id TEXT,
            timestamp DATETIME,
            violation_type TEXT,
            details TEXT,
            severity INTEGER,
            FOREIGN KEY(child_id) REFERENCES child_profiles(child_id)
        )
        """
        )

        # Create system configuration table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS system_config (
            key TEXT PRIMARY KEY,
            value TEXT,
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
        )

        # Commit changes
        conn.commit()
        logger.info(f"Database initialized successfully at {db_path}")

    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


def seed_initial_config(db_path: str = "data/child_memories.db"):
    """
    Seed initial system configuration

    :param db_path: Path to the SQLite database file
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Default configuration settings
        default_config = {
            "safety_level": "2",
            "coppa_compliance": "true",
            "gdpr_compliance": "true",
            "min_age": "4",
            "max_age": "12",
            "content_filter_enabled": "true",
            "analytics_enabled": "true",
        }

        # Insert or update configuration
        for key, value in default_config.items():
            cursor.execute(
                """
            INSERT OR REPLACE INTO system_config (key, value, last_updated)
            VALUES (?, ?, ?)
            """,
                (key, value, datetime.now()),
            )

        conn.commit()
        logging.info("Initial system configuration seeded successfully")

    except Exception as e:
        logging.error(f"Configuration seeding failed: {e}")
        raise
    finally:
        if conn:
            conn.close()


def main():
    """
    Main function to initialize database and seed configuration
    """
    logging.basicConfig(level=logging.INFO)

    try:
        db_path = "data/child_memories.db"
        create_database(db_path)
        seed_initial_config(db_path)
    except Exception as e:
        logging.error(f"Database initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
