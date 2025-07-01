"""Conversation export service."""

import csv
import io
import json
import logging
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional


class ConversationExportService:
    """Service for exporting conversation data in various formats."""

    def __init__(self, connection: sqlite3.Connection):
        """Initialize export service with database connection."""
        self.connection = connection
        self.logger = logging.getLogger(__name__)

    async def export_conversations(
        self,
        child_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        format: str = "json",
        include_transcripts: bool = True,
    ) -> bytes:
        """Export conversations to specified format."""
        # Get conversations
        conversations = await self._get_conversations_for_export(child_id, start_date, end_date)

        if format == "json":
            return self._export_json(conversations, include_transcripts)
        elif format == "csv":
            return self._export_csv(conversations)
        elif format == "txt":
            return self._export_text(conversations, include_transcripts)
        else:
            raise ValueError(f"Unsupported export format: {format}")

    async def _get_conversations_for_export(
        self, child_id: Optional[str], start_date: Optional[datetime], end_date: Optional[datetime]
    ) -> List[Dict[str, Any]]:
        """Get conversations for export."""
        try:
            cursor = self.connection.cursor()

            sql = "SELECT * FROM conversations WHERE archived = 0"
            params = []

            if child_id:
                sql += " AND child_id = ?"
                params.append(child_id)

            if start_date:
                sql += " AND start_time >= ?"
                params.append(start_date.isoformat())

            if end_date:
                sql += " AND start_time <= ?"
                params.append(end_date.isoformat())

            sql += " ORDER BY start_time DESC"

            cursor.execute(sql, params)
            return [dict(row) for row in cursor.fetchall()]

        except sqlite3.Error as e:
            self.logger.error(f"Error getting conversations for export: {e}")
            raise

    def _export_json(self, conversations: List[Dict[str, Any]], include_transcripts: bool) -> bytes:
        """Export as JSON."""
        data = []

        for conv in conversations:
            conv_data = {
                "id": conv["id"],
                "child_id": conv["child_id"],
                "start_time": conv["start_time"],
                "end_time": conv["end_time"],
                "duration_seconds": conv["duration"] or 0,
                "topics": json.loads(conv["topics"]) if conv["topics"] else [],
                "quality_score": conv["quality_score"],
                "safety_score": conv["safety_score"],
                "message_count": conv["total_messages"] or 0,
            }

            if include_transcripts:
                conv_data["messages"] = self._get_messages_for_conversation(conv["id"])

            data.append(conv_data)

        return json.dumps(data, indent=2).encode("utf-8")

    def _export_csv(self, conversations: List[Dict[str, Any]]) -> bytes:
        """Export as CSV."""
        output = io.StringIO()

        fieldnames = [
            "id",
            "child_id",
            "start_time",
            "end_time",
            "duration_minutes",
            "message_count",
            "topics",
            "quality_score",
            "safety_score",
            "engagement_score",
        ]

        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for conv in conversations:
            topics_str = ", ".join(json.loads(conv["topics"])) if conv["topics"] else ""
            duration_minutes = round((conv["duration"] or 0) / 60, 2)

            writer.writerow(
                {
                    "id": conv["id"],
                    "child_id": conv["child_id"],
                    "start_time": conv["start_time"] or "",
                    "end_time": conv["end_time"] or "",
                    "duration_minutes": duration_minutes,
                    "message_count": conv["total_messages"] or 0,
                    "topics": topics_str,
                    "quality_score": round(conv["quality_score"], 2) if conv["quality_score"] else "",
                    "safety_score": round(conv["safety_score"], 2) if conv["safety_score"] else "",
                    "engagement_score": round(conv["engagement_score"], 2) if conv["engagement_score"] else "",
                }
            )

        return output.getvalue().encode("utf-8")

    def _export_text(self, conversations: List[Dict[str, Any]], include_transcripts: bool) -> bytes:
        """Export as human-readable text."""
        lines = []

        for conv in conversations:
            lines.append(f"{'=' * 50}")
            lines.append(f"Conversation ID: {conv['id']}")
            lines.append(f"Child ID: {conv['child_id']}")

            if conv["start_time"]:
                start_time = datetime.fromisoformat(conv["start_time"])
                lines.append(f"Date: {start_time.strftime('%Y-%m-%d %H:%M')}")

            if conv["duration"]:
                duration_minutes = conv["duration"] / 60
                lines.append(f"Duration: {duration_minutes:.1f} minutes")

            if conv["topics"]:
                try:
                    topics = json.loads(conv["topics"])
                    lines.append(f"Topics: {', '.join(topics)}")
                except json.JSONDecodeError:
                    pass

            if conv["quality_score"]:
                lines.append(f"Quality Score: {conv['quality_score']:.2f}")

            if include_transcripts:
                messages = self._get_messages_for_conversation(conv["id"])
                if messages:
                    lines.append("\nTranscript:")
                    for msg in messages:
                        timestamp = msg.get("timestamp", "N/A")
                        role = msg.get("role", "unknown").upper()
                        content = msg.get("content", "")
                        lines.append(f"[{timestamp}] {role}: {content}")

            lines.append("")

        return "\n".join(lines).encode("utf-8")

    def _get_messages_for_conversation(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get messages for a conversation for export."""
        try:
            cursor = self.connection.cursor()
            sql = """
                SELECT role, content, timestamp FROM messages 
                WHERE conversation_id = ? 
                ORDER BY sequence_number, timestamp
            """
            cursor.execute(sql, (conversation_id,))

            return [{"role": row[0], "content": row[1], "timestamp": row[2]} for row in cursor.fetchall()]

        except sqlite3.Error as e:
            self.logger.error(f"Error getting messages for export: {e}")
            return []
