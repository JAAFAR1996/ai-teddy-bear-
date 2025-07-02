from typing import Any, Dict

#!/usr/bin/env python3
"""
🐛 Issue Tracker Service - نظام تتبع الأخطاء والمشاكل
تسجيل وتتبع الأخطاء مع Stacktrace وسجلات تفصيلية
"""

import hashlib
import json
import sqlite3
import traceback
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

import structlog

# إعداد logger
logger = structlog.get_logger(__name__)


# =============================================================================
# PARAMETER OBJECTS (INTRODUCE PARAMETER OBJECT REFACTORING)
# =============================================================================

@dataclass
class IssueData:
    """
    Parameter object for issue creation and reporting.
    Encapsulates all data needed to create or report an issue.
    """
    title: str
    description: str
    severity: str = "medium"
    component: str = "unknown"
    error_type: str = "runtime_error"
    stacktrace: Optional[str] = None
    
    def __post_init__(self):
        """Validate issue data"""
        if not self.title or not isinstance(self.title, str):
            raise ValueError("title must be a non-empty string")
        if not self.description or not isinstance(self.description, str):
            raise ValueError("description must be a non-empty string")
            
        # Validate severity levels
        valid_severities = ["low", "medium", "high", "critical"]
        if self.severity not in valid_severities:
            raise ValueError(f"severity must be one of: {valid_severities}")
            
        # Clean and validate component name
        if not self.component or not isinstance(self.component, str):
            self.component = "unknown"
        else:
            self.component = self.component.strip().lower()
            
        # Clean and validate error_type
        if not self.error_type or not isinstance(self.error_type, str):
            self.error_type = "runtime_error"
        else:
            self.error_type = self.error_type.strip()
            
        # Clean stacktrace if provided
        if self.stacktrace and not isinstance(self.stacktrace, str):
            self.stacktrace = str(self.stacktrace)


class IssueTrackerService:
    """
    🐛 نظام تتبع الأخطاء والمشاكل

    الميزات:
    - تسجيل تلقائي للأخطاء مع Stacktrace
    - تجميع الأخطاء المتشابهة
    - تتبع حالة المشاكل
    - إحصائيات تفصيلية
    """

    def __init__(self, config_path: str = "config/staging_config.json"):
        self.logger = logger.bind(service="issue_tracker")
        self.config_path = config_path
        self._load_config()
        self._init_database()

    def _load_config(self) -> Any:
        """تحميل إعدادات تتبع الأخطاء"""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)

            monitoring_config = config.get("MONITORING_CONFIG", {})

            self.config = {
                "enable_issue_tracking": monitoring_config.get(
                    "enable_issue_tracking", True
                ),
                "alert_email": monitoring_config.get(
                    "alert_email", "admin@aiteddybear.com"
                ),
                "log_retention_days": monitoring_config.get("log_retention_days", 30),
            }

        except Exception as e:
            self.logger.error("Failed to load issue tracker config", error=str(e))
            self.config = {"enable_issue_tracking": True}

    def _init_database(self) -> Any:
        """تهيئة قاعدة بيانات تتبع الأخطاء"""
        try:
            self.db_path = "logs/issues.db"
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS issues (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    severity TEXT DEFAULT 'medium',
                    status TEXT DEFAULT 'open',
                    component TEXT,
                    error_type TEXT,
                    stacktrace TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    occurrence_count INTEGER DEFAULT 1,
                    last_occurrence DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            conn.commit()
            conn.close()

            self.logger.info("Issue tracker database initialized")

        except Exception as e:
            self.logger.error(
                "Failed to initialize issue tracker database", error=str(e)
            )

    async def create_issue(self, issue_data: IssueData) -> str:
        """
        إنشاء تقرير مشكلة جديد.
        Refactored to use parameter object pattern.
        
        Args:
            issue_data: IssueData object containing all issue information
            
        Returns:
            str: Issue ID or None if failed
        """
        try:
            # إنشاء ID فريد للمشكلة
            issue_id = self._generate_issue_id(issue_data.title, issue_data.error_type)

            # حفظ في قاعدة البيانات
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # فحص إذا كانت المشكلة موجودة مسبقاً
            cursor.execute(
                "SELECT occurrence_count FROM issues WHERE id = ?", (issue_id,)
            )
            existing = cursor.fetchone()

            if existing:
                # تحديث عدد التكرارات
                cursor.execute(
                    """
                    UPDATE issues 
                    SET occurrence_count = occurrence_count + 1,
                        last_occurrence = ?
                    WHERE id = ?
                """,
                    (datetime.utcnow(), issue_id),
                )
            else:
                # إدراج مشكلة جديدة
                cursor.execute(
                    """
                    INSERT INTO issues 
                    (id, title, description, severity, status, component, error_type, stacktrace)
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

            self.logger.info(
                "Issue created",
                issue_id=issue_id,
                severity=issue_data.severity,
                component=issue_data.component,
            )

            return issue_id

        except Exception as e:
            self.logger.error("Failed to create issue", error=str(e))
            return None

    async def create_issue_legacy(
        self,
        title: str,
        description: str,
        severity: str = "medium",
        component: str = "unknown",
        error_type: str = "runtime_error",
        stacktrace: str = None,
    ) -> str:
        """
        Legacy method for backward compatibility.
        Creates IssueData and delegates to new method.
        """
        issue_data = IssueData(
            title=title,
            description=description,
            severity=severity,
            component=component,
            error_type=error_type,
            stacktrace=stacktrace
        )
        return await self.create_issue(issue_data)

    def _generate_issue_id(self, title: str, error_type: str) -> str:
        """إنشاء ID فريق للمشكلة"""
        try:
            content = f"{title}:{error_type}"
            hash_object = hashlib.md5(content.encode())
            return f"ISS-{hash_object.hexdigest()[:8].upper()}"
        except Exception:
            return f"ISS-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

    async def get_issue_statistics(self) -> Dict:
        """الحصول على إحصائيات المشاكل"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT 
                    COUNT(*) as total_issues,
                    SUM(CASE WHEN status = 'open' THEN 1 ELSE 0 END) as open_issues,
                    SUM(CASE WHEN severity = 'critical' THEN 1 ELSE 0 END) as critical_issues
                FROM issues
            """
            )

            stats = cursor.fetchone()

            cursor.execute(
                """
                SELECT component, COUNT(*) as count
                FROM issues 
                WHERE status = 'open'
                GROUP BY component
                ORDER BY count DESC
                LIMIT 5
            """
            )

            component_stats = cursor.fetchall()

            conn.close()

            return {
                "total_issues": stats[0] if stats else 0,
                "open_issues": stats[1] if stats else 0,
                "critical_issues": stats[2] if stats else 0,
                "by_component": [
                    {"component": comp, "count": count}
                    for comp, count in component_stats
                ],
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            self.logger.error("Failed to get issue statistics", error=str(e))
            return {"error": str(e)}


# مثيل نظام تتبع الأخطاء العام
issue_tracker = IssueTrackerService()


# دوال مساعدة
async def report_issue(issue_data: IssueData) -> str:
    """
    تسجيل مشكلة جديدة.
    Refactored to use parameter object pattern.
    
    Args:
        issue_data: IssueData object containing all issue information
        
    Returns:
        str: Issue ID or None if failed
    """
    return await issue_tracker.create_issue(issue_data)


async def report_issue_legacy(
    title: str,
    description: str,
    severity: str = "medium",
    component: str = "unknown",
    error_type: str = "runtime_error",
) -> str:
    """
    Legacy function for backward compatibility.
    Creates IssueData and delegates to new function.
    """
    issue_data = IssueData(
        title=title,
        description=description,
        severity=severity,
        component=component,
        error_type=error_type
    )
    return await report_issue(issue_data)


async def report_exception(
    component: str, exception: Exception, context: str = ""
) -> str:
    """تسجيل استثناء مع stacktrace"""
    stacktrace = traceback.format_exc()

    issue_data = IssueData(
        title=f"{component}: {type(exception).__name__}",
        description=f"{str(exception)}\n\nContext: {context}",
        severity="high",
        component=component,
        error_type=type(exception).__name__,
        stacktrace=stacktrace
    )
    
    return await issue_tracker.create_issue(issue_data)


async def get_system_health() -> Dict:
    """الحصول على حالة النظام"""
    return await issue_tracker.get_issue_statistics()
