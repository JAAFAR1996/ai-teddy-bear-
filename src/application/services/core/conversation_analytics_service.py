"""Conversation analytics service."""

import logging
import sqlite3
from datetime import date, datetime, timedelta
from typing import Any, Dict, Optional


class ConversationAnalyticsService:
    """Service for conversation analytics and reporting."""

    def __init__(self, connection: sqlite3.Connection):
        """Initialize analytics service with database connection."""
        self.connection = connection
        self.logger = logging.getLogger(__name__)

    def _build_analytics_query(self, child_id: Optional[str]) -> tuple[str, list]:
        """Builds the SQL query and parameters for conversation analytics."""
        sql = """
            SELECT
                COUNT(*) as total_conversations,
                SUM(duration) as total_duration_seconds,
                AVG(duration) as avg_duration_seconds,
                SUM(total_messages) as total_messages,
                AVG(total_messages) as avg_messages_per_conversation,
                AVG(quality_score) as avg_quality_score,
                AVG(safety_score) as avg_safety_score,
                AVG(engagement_score) as avg_engagement_score,
                COUNT(CASE WHEN safety_score < 1.0 THEN 1 END) as flagged_conversations
            FROM conversations
            WHERE start_time BETWEEN ? AND ? AND archived = 0
        """
        params = []

        if child_id:
            sql += " AND child_id = ?"
            params.append(child_id)

        return sql, params

    def _format_analytics_result(self, result: tuple, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Formats the raw SQL result into a structured dictionary."""
        total_conversations = result[0] or 0
        flagged_conversations = result[8] or 0

        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
            "summary": {
                "total_conversations": total_conversations,
                "total_duration_hours": (result[1] or 0) / 3600,
                "average_duration_minutes": ((result[2] or 0) / 60) if result[2] else 0,
                "total_messages": result[3] or 0,
                "average_messages_per_conversation": result[4] or 0,
            },
            "quality_metrics": {
                "average_quality_score": result[5] or 0,
                "average_engagement_score": result[7] or 0,
                "average_safety_score": result[6] or 1.0,
            },
            "safety": {
                "flagged_conversations": flagged_conversations,
                "safety_percentage": (
                    ((total_conversations - flagged_conversations) /
                     total_conversations * 100)
                    if total_conversations > 0 else 100
                ),
            },
        }

    async def get_conversation_analytics(
        self,
        child_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Generate comprehensive conversation analytics."""
        start_date = start_date or datetime.now() - timedelta(days=30)
        end_date = end_date or datetime.now()

        try:
            cursor = self.connection.cursor()

            sql, params = self._build_analytics_query(child_id)

            # Prepend date params
            final_params = [
                start_date.isoformat(), end_date.isoformat()] + params

            cursor.execute(sql, final_params)
            result = cursor.fetchone()

            if not result:
                return {"message": "No data found for the specified period."}

            return self._format_analytics_result(result, start_date, end_date)

        except sqlite3.Error as e:
            self.logger.error(f"Error generating conversation analytics: {e}")
            raise

    async def get_conversation_statistics(self) -> Dict[str, Any]:
        """Get overall conversation statistics."""
        try:
            cursor = self.connection.cursor()

            # Basic counts
            cursor.execute(
                "SELECT COUNT(*) FROM conversations WHERE archived = 0")
            total_conversations = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COUNT(DISTINCT child_id) FROM conversations WHERE archived = 0"
            )
            unique_children = cursor.fetchone()[0]

            return {
                "total_conversations": total_conversations,
                "unique_children": unique_children,
            }

        except sqlite3.Error as e:
            self.logger.error(f"Error getting conversation statistics: {e}")
            raise

    async def generate_daily_summary(
        self, date: date, child_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate daily conversation summary."""
        start = datetime.combine(date, datetime.min.time())
        end = datetime.combine(date, datetime.max.time())

        try:
            cursor = self.connection.cursor()

            # Get conversations for the day
            sql = """
                SELECT * FROM conversations
                WHERE start_time BETWEEN ? AND ? AND archived = 0
            """
            params = [start.isoformat(), end.isoformat()]

            if child_id:
                sql += " AND child_id = ?"
                params.append(child_id)

            cursor.execute(sql, params)
            conversations = cursor.fetchall()

            if not conversations:
                return {"date": date.isoformat(), "no_activity": True}

            return {
                "date": date.isoformat(),
                "summary": {
                    "total_conversations": len(conversations),
                    "unique_children": len(set(c[2] for c in conversations)),
                },
            }

        except sqlite3.Error as e:
            self.logger.error(f"Error generating daily summary: {e}")
            raise
