"""Conversation maintenance service."""

import logging
import sqlite3
from datetime import datetime, timedelta
from typing import Any, Dict


class ConversationMaintenanceService:
    """Service for conversation maintenance and cleanup operations."""

    def __init__(self, connection: sqlite3.Connection):
        """Initialize maintenance service with database connection."""
        self.connection = connection
        self.logger = logging.getLogger(__name__)

    async def delete_old_conversations(
        self, retention_days: int = 90, exclude_flagged: bool = True
    ) -> int:
        """Delete old conversations."""
        cutoff_date = datetime.now() - timedelta(days=retention_days)

        try:
            cursor = self.connection.cursor()

            sql = "DELETE FROM conversations WHERE start_time < ?"
            params = [cutoff_date.isoformat()]

            if exclude_flagged:
                sql += " AND safety_score >= 1.0"

            cursor.execute(sql, params)
            self.connection.commit()

            deleted_count = cursor.rowcount
            self.logger.info(f"Deleted {deleted_count} old conversations")

            return deleted_count

        except sqlite3.Error as e:
            self.logger.error(f"Error deleting old conversations: {e}")
            raise

    async def archive_conversations(
        self, days_old: int = 30, archive_path: str = "archives/"
    ) -> int:
        """Archive old conversations to storage."""
        cutoff_date = datetime.now() - timedelta(days=days_old)

        try:
            cursor = self.connection.cursor()

            # Mark conversations as archived
            sql = """
                UPDATE conversations 
                SET archived = 1, updated_at = ?
                WHERE start_time < ? AND archived = 0 AND parent_visible = 1
            """
            cursor.execute(sql, (datetime.now().isoformat(), cutoff_date.isoformat()))
            self.connection.commit()

            archived_count = cursor.rowcount
            self.logger.info(f"Archived {archived_count} conversations")

            return archived_count

        except sqlite3.Error as e:
            self.logger.error(f"Error archiving conversations: {e}")
            raise

    async def cleanup_orphaned_messages(self) -> int:
        """Remove messages that have no corresponding conversation."""
        try:
            cursor = self.connection.cursor()

            sql = """
                DELETE FROM messages 
                WHERE conversation_id NOT IN (SELECT id FROM conversations)
            """
            cursor.execute(sql)
            self.connection.commit()

            cleaned_count = cursor.rowcount
            self.logger.info(f"Cleaned {cleaned_count} orphaned messages")

            return cleaned_count

        except sqlite3.Error as e:
            self.logger.error(f"Error cleaning orphaned messages: {e}")
            raise

    async def cleanup_orphaned_emotional_states(self) -> int:
        """Remove emotional states that have no corresponding conversation."""
        try:
            cursor = self.connection.cursor()

            sql = """
                DELETE FROM emotional_states 
                WHERE conversation_id NOT IN (SELECT id FROM conversations)
            """
            cursor.execute(sql)
            self.connection.commit()

            cleaned_count = cursor.rowcount
            self.logger.info(f"Cleaned {cleaned_count} orphaned emotional states")

            return cleaned_count

        except sqlite3.Error as e:
            self.logger.error(f"Error cleaning orphaned emotional states: {e}")
            raise

    async def optimize_database(self) -> Dict[str, Any]:
        """Optimize database performance."""
        try:
            cursor = self.connection.cursor()

            # Analyze tables
            cursor.execute("ANALYZE")

            # Vacuum database
            cursor.execute("VACUUM")

            # Update statistics
            cursor.execute("PRAGMA optimize")

            self.connection.commit()

            # Get database size
            cursor.execute("PRAGMA page_count")
            page_count = cursor.fetchone()[0]

            cursor.execute("PRAGMA page_size")
            page_size = cursor.fetchone()[0]

            db_size_bytes = page_count * page_size

            self.logger.info("Database optimization completed")

            return {
                "status": "success",
                "db_size_bytes": db_size_bytes,
                "operations_performed": ["ANALYZE", "VACUUM", "PRAGMA optimize"],
                "timestamp": datetime.now().isoformat(),
            }

        except sqlite3.Error as e:
            self.logger.error(f"Error optimizing database: {e}")
            raise

    async def analyze_performance(self) -> Dict[str, Any]:
        """Analyze and suggest optimizations for conversation performance."""
        try:
            cursor = self.connection.cursor()

            # Analyze conversation patterns
            cursor.execute(
                """
                SELECT 
                    AVG(CASE WHEN end_time IS NOT NULL THEN 
                        (julianday(end_time) - julianday(start_time)) * 24 * 60 
                        ELSE NULL END) as avg_duration_minutes,
                    AVG(total_messages) as avg_messages,
                    COUNT(*) as total_conversations,
                    COUNT(CASE WHEN safety_score < 1.0 THEN 1 END) as flagged_conversations,
                    AVG(quality_score) as avg_quality
                FROM conversations 
                WHERE archived = 0 AND start_time >= datetime('now', '-30 days')
            """
            )

            stats = cursor.fetchone()

            optimizations = []
            performance_score = 100

            # Analyze performance bottlenecks
            if stats[0] and stats[0] > 15:  # Average duration > 15 minutes
                optimizations.append(
                    {
                        "area": "Duration Management",
                        "issue": "Conversations are running longer than optimal",
                        "suggestion": "Consider implementing time limits or conversation breaks",
                        "impact": "medium",
                    }
                )
                performance_score -= 10

            if stats[1] and stats[1] > 20:  # Too many messages per conversation
                optimizations.append(
                    {
                        "area": "Message Efficiency",
                        "issue": "High message count per conversation",
                        "suggestion": "Optimize AI responses to be more concise and effective",
                        "impact": "low",
                    }
                )
                performance_score -= 5

            if stats[3] and (stats[3] / stats[2]) > 0.05:  # More than 5% flagged
                optimizations.append(
                    {
                        "area": "Content Safety",
                        "issue": "High rate of flagged conversations",
                        "suggestion": "Review and improve content moderation rules",
                        "impact": "high",
                    }
                )
                performance_score -= 25

            if stats[4] and stats[4] < 0.7:  # Low quality score
                optimizations.append(
                    {
                        "area": "Conversation Quality",
                        "issue": "Below-average conversation quality scores",
                        "suggestion": "Review AI model performance and fine-tune responses",
                        "impact": "high",
                    }
                )
                performance_score -= 20

            return {
                "performance_score": max(0, performance_score),
                "performance_level": (
                    "excellent"
                    if performance_score >= 90
                    else "good" if performance_score >= 70 else "needs_improvement"
                ),
                "statistics": {
                    "avg_duration_minutes": stats[0] or 0,
                    "avg_messages_per_conversation": stats[1] or 0,
                    "total_recent_conversations": stats[2] or 0,
                    "flagged_rate_percentage": ((stats[3] or 0) / (stats[2] or 1))
                    * 100,
                    "avg_quality_score": stats[4] or 0,
                },
                "optimizations": optimizations,
                "analysis_date": datetime.now().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Error in performance analysis: {e}")
            return {"status": "error", "message": str(e)}
