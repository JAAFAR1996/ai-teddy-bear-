import sqlite3
import structlog
from dataclasses import dataclass
from typing import Optional

# To avoid circular imports, we'd typically have these in a models file.
# from .models import IssueUpdateData


@dataclass
class IssueUpdateData:
    issue_id: str
    status: Optional[str] = None
    severity: Optional[str] = None
    notes: Optional[str] = None


logger = structlog.get_logger()


class IssueUpdater:
    """Handles updating existing issues."""

    def __init__(self, db_path: str):
        self.db_path = db_path

    async def update(self, update_data: "IssueUpdateData") -> bool:
        """Update an existing issue."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            update_fields = []
            update_values = []

            if update_data.status:
                update_fields.append("status = ?")
                update_values.append(update_data.status)
            if update_data.severity:
                update_fields.append("severity = ?")
                update_values.append(update_data.severity)
            if update_data.notes:
                update_fields.append("notes = ?")
                update_values.append(update_data.notes)

            if not update_fields:
                return False

            update_values.append(update_data.issue_id)
            query = "UPDATE issues SET " + \
                ", ".join(update_fields) + " WHERE id = ?"
            cursor.execute(query, tuple(update_values))
            conn.commit()
            updated = cursor.rowcount > 0
            conn.close()

            if updated:
                logger.info("Issue updated", issue_id=update_data.issue_id)
            return updated
        except Exception as e:
            logger.error("Failed to update issue", error=str(e))
            return False
