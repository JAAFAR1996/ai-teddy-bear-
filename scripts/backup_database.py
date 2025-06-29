import os
import shutil
import sqlite3
import logging
from datetime import datetime

def backup_database(source_db: str = 'data/child_memories.db', 
                    backup_dir: str = 'data/backups'):
    """
    Create a timestamped backup of the SQLite database
    
    :param source_db: Path to the source database
    :param backup_dir: Directory to store database backups
    """
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    try:
        # Ensure backup directory exists
        os.makedirs(backup_dir, exist_ok=True)

        # Generate timestamped backup filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"child_memories_backup_{timestamp}.db"
        backup_path = os.path.join(backup_dir, backup_filename)

        # Perform backup
        source_conn = sqlite3.connect(source_db)
        backup_conn = sqlite3.connect(backup_path)
        source_conn.backup(backup_conn)

        # Close connections
        backup_conn.close()
        source_conn.close()

        logger.info(f"Database backup created: {backup_path}")
        return backup_path

    except Exception as e:
        logger.error(f"Database backup failed: {e}")
        raise

def restore_database(backup_file: str, 
                     target_db: str = 'data/child_memories.db'):
    """
    Restore database from a backup file
    
    :param backup_file: Path to the backup database file
    :param target_db: Path to restore the database
    """
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    try:
        # Ensure target directory exists
        os.makedirs(os.path.dirname(target_db), exist_ok=True)

        # Copy backup file to target location
        shutil.copy2(backup_file, target_db)

        logger.info(f"Database restored from {backup_file} to {target_db}")

    except Exception as e:
        logger.error(f"Database restoration failed: {e}")
        raise

def list_backups(backup_dir: str = 'data/backups'):
    """
    List available database backups
    
    :param backup_dir: Directory containing backup files
    :return: List of backup files sorted by creation time
    """
    try:
        # Ensure backup directory exists
        os.makedirs(backup_dir, exist_ok=True)

        # Get list of backup files
        backup_files = [
            os.path.join(backup_dir, f) 
            for f in os.listdir(backup_dir) 
            if f.startswith('child_memories_backup_') and f.endswith('.db')
        ]

        # Sort backups by creation time (newest first)
        backup_files.sort(key=os.path.getctime, reverse=True)

        return backup_files

    except Exception as e:
        logging.error(f"Failed to list backups: {e}")
        return []

def main():
    """
    Main function to demonstrate backup and restore functionality
    """
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Create a backup
        backup_file = backup_database()
        
        # List available backups
        backups = list_backups()
        print("Available backups:", backups)
        
        # Optional: Restore from the most recent backup
        if backups:
            restore_database(backups[0])
    
    except Exception as e:
        logging.error(f"Backup/restore operation failed: {e}")
        exit(1)

if __name__ == "__main__":
    main()
