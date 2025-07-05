from typing import Dict
import sqlite3
from datetime import datetime
import hashlib
from dataclasses import dataclass

import structlog

# To avoid circular imports, we'd typically have these in a models file.
# from .models import IssueData


@dataclass
class IssueData:
    title: str
    description: str
    severity: str
    component: str
    error_type: str
    stacktrace: str | None


logger = structlog.get_logger()


class IssueCreator:
    """Handles the creation of new issues."""

    def __init__(self, db_path: str):
        self.db_path = db_path

    async def create(self, issue_data: "IssueData") -> str:
        """Create a new issue or update the occurrence count of an existing one."""
        try:
            issue_id = self._generate_issue_id(
                issue_data.title, issue_data.error_type)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                "SELECT occurrence_count FROM issues WHERE id = ?", (issue_id,))
            existing = cursor.fetchone()

            if existing:
                cursor.execute(
                    "UPDATE issues SET occurrence_count = occurrence_count + 1, last_occurrence = ? WHERE id = ?",
                    (datetime.utcnow(), issue_id),
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO issues (id, title, description, severity, status, component, error_type, stacktrace)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        issue_id,
                        issue_data.title,
                        issue_data.description,
                        issue_data.severity,
                        "open",
                        issue_data.component,
                        issue_data.error_type,
                        issue_data.stacktrace or "",
                    ),
                )
            conn.commit()
            conn.close()
            logger.info("Issue created", issue_id=issue_id,
                        severity=issue_data.severity)
            return issue_id
        except Exception as e:
            logger.error("Failed to create issue", error=str(e))
            return None

    def _generate_issue_id(self, title: str, error_type: str) -> str:
        """Generate a unique ID for the issue."""
        try:
            content = f"{title}:{error_type}"
            hash_object = hashlib.md5(content.encode())
            return f"ISS-{hash_object.hexdigest()[:8].upper()}"
        except Exception:
            return f"ISS-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
