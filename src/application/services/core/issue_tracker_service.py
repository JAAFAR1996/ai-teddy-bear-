from typing import Any, Dict, List, Optional

#!/usr/bin/env python3
"""
🐛 Issue Tracker Service - نظام تتبع الأخطاء والمشاكل
تسجيل وتتبع الأخطاء مع Stacktrace وسجلات تفصيلية
"""

import asyncio
import hashlib
import json
import sqlite3
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import structlog

# إعداد logger
logger = structlog.get_logger(__name__)


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

    async def create_issue(
        self,
        title: str,
        description: str,
        severity: str = "medium",
        component: str = "unknown",
        error_type: str = "runtime_error",
        stacktrace: str = None,
    ) -> str:
        """إنشاء تقرير مشكلة جديد"""
        try:
            # إنشاء ID فريد للمشكلة
            issue_id = self._generate_issue_id(title, error_type)

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
                        title,
                        description,
                        severity,
                        "open",
                        component,
                        error_type,
                        stacktrace or "",
                    ),
                )

            conn.commit()
            conn.close()

            self.logger.info(
                "Issue created",
                issue_id=issue_id,
                severity=severity,
                component=component,
            )

            return issue_id

        except Exception as e:
            self.logger.error("Failed to create issue", error=str(e))
            return None

    def _generate_issue_id(self, title: str, error_type: str) -> str:
        """إنشاء ID فريد للمشكلة"""
        try:
            content = f"{title}:{error_type}"
            hash_object = hashlib.md5(content.encode())
            return f"ISS-{hash_object.hexdigest()[:8].upper()}"
        except Exception as e:
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
async def report_issue(
    title: str,
    description: str,
    severity: str = "medium",
    component: str = "unknown",
    error_type: str = "runtime_error",
) -> str:
    """تسجيل مشكلة جديدة"""
    return await issue_tracker.create_issue(
        title, description, severity, component, error_type
    )


async def report_exception(
    component: str, exception: Exception, context: str = ""
) -> str:
    """تسجيل استثناء مع stacktrace"""
    stacktrace = traceback.format_exc()

    return await issue_tracker.create_issue(
        title=f"{component}: {type(exception).__name__}",
        description=f"{str(exception)}\n\nContext: {context}",
        severity="high",
        component=component,
        error_type=type(exception).__name__,
        stacktrace=stacktrace,
    )


async def get_system_health() -> Dict:
    """الحصول على حالة النظام"""
    return await issue_tracker.get_issue_statistics()
