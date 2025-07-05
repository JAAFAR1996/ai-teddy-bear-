import sqlite3
import structlog
from typing import List, Dict, Optional
from datetime import datetime
from dataclasses import dataclass

# To avoid circular imports, we'd typically have these in a models file.
# from .models import IssueQueryParams


@dataclass
class IssueQueryParams:
    status: Optional[str] = None
    severity: Optional[str] = None
    component: Optional[str] = None
    limit: int = 10
    offset: int = 0


logger = structlog.get_logger()


class IssueSearcher:
    """Handles searching for issues and calculating statistics."""

    def __init__(self, db_path: str):
        self.db_path = db_path

    async def search(self, query_params: "IssueQueryParams") -> List[Dict]:
        """Search for issues based on given criteria."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            where_conditions = []
            where_values = []
            if query_params.status:
                where_conditions.append("status = ?")
                where_values.append(query_params.status)
            if query_params.severity:
                where_conditions.append("severity = ?")
                where_values.append(query_params.severity)
            if query_params.component:
                where_conditions.append("component = ?")
                where_values.append(query_params.component)

            base_query = "SELECT id, title, description, severity, status, component, error_type, timestamp, occurrence_count FROM issues"
            if where_conditions:
                base_query += " WHERE " + " AND ".join(where_conditions)
            base_query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
            where_values.extend([query_params.limit, query_params.offset])

            cursor.execute(base_query, tuple(where_values))
            columns = [desc[0] for desc in cursor.description]
            issues = [dict(zip(columns, row)) for row in cursor.fetchall()]
            conn.close()
            return issues
        except Exception as e:
            logger.error("Failed to search issues", error=str(e))
            return []

    async def get_statistics(self) -> Dict:
        """Get statistics about the issues."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*), SUM(CASE WHEN status = 'open' THEN 1 ELSE 0 END), SUM(CASE WHEN severity = 'critical' THEN 1 ELSE 0 END) FROM issues")
            stats = cursor.fetchone()
            cursor.execute(
                "SELECT component, COUNT(*) as count FROM issues WHERE status = 'open' GROUP BY component ORDER BY count DESC LIMIT 5")
            component_stats = cursor.fetchall()
            conn.close()

            return {
                "total_issues": stats[0] if stats else 0,
                "open_issues": stats[1] if stats else 0,
                "critical_issues": stats[2] if stats else 0,
                "by_component": [{"component": comp, "count": count} for comp, count in component_stats],
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error("Failed to get issue statistics", error=str(e))
            return {"error": str(e)}
