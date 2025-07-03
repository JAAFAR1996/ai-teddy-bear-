import logging
import sqlite3
from datetime import datetime
import sys


class DataMigration:
    """
    Handles data migration between different versions of the database schema
    """

    def __init__(self, db_path: str = "data/child_memories.db"):
        """
        Initialize data migration

        :param db_path: Path to the SQLite database
        """
        self._db_path = db_path
        logging.basicConfig(level=logging.INFO)
        self._logger = logging.getLogger(__name__)

    def _connect_db(self):
        """
        Create a database connection

        :return: Database connection
        """
        return sqlite3.connect(self._db_path)

    def migrate_v1_to_v2(self):
        """
        Migrate database from version 1 to version 2
        Add new tables, modify existing schemas
        """
        try:
            conn = self._connect_db()
            cursor = conn.cursor()

            # Add new columns to existing tables
            cursor.execute(
                """
            ALTER TABLE child_profiles 
            ADD COLUMN language_preference TEXT DEFAULT 'en'
            """
            )

            cursor.execute(
                """
            ALTER TABLE child_profiles 
            ADD COLUMN learning_mode TEXT DEFAULT 'adaptive'
            """
            )

            # Create new tables
            cursor.execute(
                """
            CREATE TABLE IF NOT EXISTS learning_progress (
                child_id TEXT,
                skill_category TEXT,
                progress_level INTEGER,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(child_id) REFERENCES child_profiles(child_id)
            )
            """
            )

            # Update system version
            cursor.execute(
                """
            INSERT OR REPLACE INTO system_config (key, value, last_updated)
            VALUES ('database_version', '2', ?)
            """,
                (datetime.now(),),
            )

            conn.commit()
            self._logger.info("Database migrated to version 2 successfully")

        except sqlite3.OperationalError as e:
            # Handle cases where columns might already exist
            if "duplicate column" in str(e):
                self._logger.warning("Migration columns already exist")
            else:
                self._logger.error(f"Migration error: {e}")
                raise
        finally:
            conn.close()

    def migrate_v2_to_v3(self):
        """
        Migrate database from version 2 to version 3
        Add enhanced privacy and safety features
        """
        try:
            conn = self._connect_db()
            cursor = conn.cursor()

            # Add privacy consent tracking
            cursor.execute(
                """
            ALTER TABLE child_profiles 
            ADD COLUMN parental_consent_timestamp DATETIME
            """
            )

            cursor.execute(
                """
            ALTER TABLE child_profiles 
            ADD COLUMN consent_version TEXT
            """
            )

            # Create privacy audit log
            cursor.execute(
                """
            CREATE TABLE IF NOT EXISTS privacy_audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                child_id TEXT,
                event_type TEXT,
                details TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(child_id) REFERENCES child_profiles(child_id)
            )
            """
            )

            # Update system version
            cursor.execute(
                """
            INSERT OR REPLACE INTO system_config (key, value, last_updated)
            VALUES ('database_version', '3', ?)
            """,
                (datetime.now(),),
            )

            conn.commit()
            self._logger.info("Database migrated to version 3 successfully")

        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e):
                self._logger.warning("Migration columns already exist")
            else:
                self._logger.error(f"Migration error: {e}")
                raise
        finally:
            conn.close()

    def backup_before_migration(self):
        """
        Create a backup before performing migration
        """
        from .backup_database import backup_database

        backup_file = backup_database()
        self._logger.info(f"Backup created before migration: {backup_file}")
        return backup_file

    def run_migrations(self):
        """
        Run all necessary migrations in sequence
        """
        try:
            # Backup database before migration
            self.backup_before_migration()

            # Check current database version
            conn = self._connect_db()
            cursor = conn.cursor()

            cursor.execute(
                """
            SELECT value FROM system_config 
            WHERE key = 'database_version'
            """
            )

            result = cursor.fetchone()
            current_version = int(result[0]) if result else 1
            conn.close()

            # Run migrations in sequence
            if current_version < 2:
                self.migrate_v1_to_v2()

            if current_version < 3:
                self.migrate_v2_to_v3()

            self._logger.info("All migrations completed successfully")

        except Exception as e:
            self._logger.error(f"Migration process failed: {e}")
            raise


def main():
    """
    Main function to run database migrations
    """
    logging.basicConfig(level=logging.INFO)

    try:
        migrator = DataMigration()
        migrator.run_migrations()
    except Exception as e:
        logging.error(f"Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
