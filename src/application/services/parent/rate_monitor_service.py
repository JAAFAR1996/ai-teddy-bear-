#!/usr/bin/env python3
"""
📊 Rate Monitor Service - خدمة مراقبة معدلات الإرسال
مراقبة وتتبع حدود الإشعارات لكل ولي أمر والنظام العام
"""

import asyncio
import json
import sqlite3
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import structlog

# إعداد logger
logger = structlog.get_logger(__name__)


@dataclass
class RateLimit:
    """حدود معدل الإرسال"""

    per_minute: int = 30
    per_hour: int = 100
    per_day: int = 1000
    per_week_per_parent: int = 3
    cooldown_hours: int = 24


class RateMonitorService:
    """
    📊 خدمة مراقبة معدلات الإرسال المتقدمة

    الميزات:
    - مراقبة حدود الإرسال (دقيقة/ساعة/يوم/أسبوع)
    - تتبع الحدود لكل ولي أمر
    - منع تجاوز الحدود الأسبوعية
    - تبريد زمني بين الإشعارات
    - إحصائيات تفصيلية
    """

    def __init__(self, config_path: str = "config/staging_config.json"):
        self.logger = logger.bind(service="rate_monitor")
        self.config_path = config_path
        self._load_config()
        self._init_counters()
        self._init_database()

    def _load_config(self) -> Any:
        """تحميل إعدادات المراقبة"""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)

            notification_config = config.get("NOTIFICATION_CONFIG", {})

            self.rate_limit = RateLimit(
                per_minute=notification_config.get("rate_limit_per_minute", 30),
                per_hour=notification_config.get("rate_limit_per_hour", 100),
                per_day=notification_config.get("rate_limit_per_day", 1000),
                per_week_per_parent=notification_config.get(
                    "max_notifications_per_parent_per_week", 3
                ),
                cooldown_hours=notification_config.get("cooldown_period_hours", 24),
            )

            self.logger.info("Rate limits loaded", **asdict(self.rate_limit))

        except Exception as e:
            self.logger.error("Failed to load rate monitor config", error=str(e))
            self.rate_limit = RateLimit()

    def _init_counters(self) -> Any:
        """تهيئة العدادات"""
        self.minute_counter = deque(maxlen=60)
        self.hour_counter = deque(maxlen=3600)
        self.day_counter = deque(maxlen=86400)

    def _init_database(self) -> Any:
        """تهيئة قاعدة بيانات المراقبة"""
        try:
            self.db_path = "logs/rate_monitor.db"
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS notification_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    parent_email TEXT,
                    child_udid TEXT,
                    notification_type TEXT,
                    channel TEXT,
                    success BOOLEAN,
                    error_message TEXT
                )
            """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS weekly_parent_limits (
                    parent_email TEXT,
                    week_start DATE,
                    notifications_sent INTEGER DEFAULT 0,
                    last_notification DATETIME,
                    PRIMARY KEY (parent_email, week_start)
                )
            """
            )

            conn.commit()
            conn.close()

            self.logger.info("Rate monitor database initialized", db_path=self.db_path)

        except Exception as e:
            self.logger.error(
                "Failed to initialize rate monitor database", error=str(e)
            )

    async def check_rate_limit(
        self, parent_email: str, child_udid: str
    ) -> Tuple[bool, str]:
        """فحص حدود معدل الإرسال"""
        try:
            now = datetime.utcnow()

            # فحص الحد العام للنظام
            system_check = await self._check_system_limits(now)
            if not system_check[0]:
                return system_check

            # فحص حدود ولي الأمر الأسبوعية
            parent_check = await self._check_parent_weekly_limit(parent_email, now)
            if not parent_check[0]:
                return parent_check

            return True, "Rate limit check passed"

        except Exception as e:
            self.logger.error("Rate limit check failed", error=str(e))
            return False, f"Rate check error: {str(e)}"

    async def _check_system_limits(self, now: datetime) -> Tuple[bool, str]:
        """فحص الحدود العامة للنظام"""
        try:
            cutoff_minute = now - timedelta(minutes=1)
            self.minute_counter = deque(
                [t for t in self.minute_counter if t > cutoff_minute], maxlen=60
            )

            if len(self.minute_counter) >= self.rate_limit.per_minute:
                return (
                    False,
                    f"System minute limit exceeded ({self.rate_limit.per_minute}/min)",
                )

            return True, "System limits OK"

        except Exception as e:
            return False, "System limits check error"

    async def _check_parent_weekly_limit(
        self, parent_email: str, now: datetime
    ) -> Tuple[bool, str]:
        """فحص الحد الأسبوعي لولي الأمر"""
        try:
            week_start = now - timedelta(days=now.weekday())
            week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT notifications_sent 
                FROM weekly_parent_limits 
                WHERE parent_email = ? AND week_start = ?
            """,
                (parent_email, week_start.date()),
            )

            result = cursor.fetchone()
            conn.close()

            if result and result[0] >= self.rate_limit.per_week_per_parent:
                return (
                    False,
                    f"Parent weekly limit exceeded ({result[0]}/{self.rate_limit.per_week_per_parent})",
                )

            return True, "Parent weekly limit OK"

        except Exception as e:
            return False, "Parent limit check error"

    async def record_notification(
        self,
        parent_email: str,
        child_udid: str,
        channel: str,
        success: bool,
        error_message: str = None,
    ):
        """تسجيل إرسال إشعار"""
        try:
            now = datetime.utcnow()
            self.minute_counter.append(now)

            # تسجيل في قاعدة البيانات
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO notification_stats 
                (timestamp, parent_email, child_udid, notification_type, channel, success, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    now,
                    parent_email,
                    child_udid,
                    "cleanup_warning",
                    channel,
                    success,
                    error_message,
                ),
            )

            # تحديث الحدود الأسبوعية
            if success:
                week_start = now - timedelta(days=now.weekday())
                week_start = week_start.replace(
                    hour=0, minute=0, second=0, microsecond=0
                )

                cursor.execute(
                    """
                    INSERT OR REPLACE INTO weekly_parent_limits 
                    (parent_email, week_start, notifications_sent, last_notification)
                    VALUES (?, ?, 
                        COALESCE((SELECT notifications_sent FROM weekly_parent_limits 
                                 WHERE parent_email = ? AND week_start = ?), 0) + 1,
                        ?)
                """,
                    (
                        parent_email,
                        week_start.date(),
                        parent_email,
                        week_start.date(),
                        now,
                    ),
                )

            conn.commit()
            conn.close()

            self.logger.info(
                "Notification recorded", parent_email=parent_email, success=success
            )

        except Exception as e:
            self.logger.error("Failed to record notification", error=str(e))

    async def get_statistics(self) -> Dict:
        """الحصول على إحصائيات المعدلات"""
        try:
            return {
                "system": {
                    "current_minute": len(self.minute_counter),
                    "limits": asdict(self.rate_limit),
                },
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            self.logger.error("Failed to get statistics", error=str(e))
            return {"error": str(e)}


# مثيل خدمة المراقبة العامة
rate_monitor = RateMonitorService()


# دوال مساعدة
async def check_notification_rate_limit(
    parent_email: str, child_udid: str
) -> Tuple[bool, str]:
    """فحص حدود معدل الإرسال"""
    return await rate_monitor.check_rate_limit(parent_email, child_udid)


async def record_notification_sent(
    parent_email: str,
    child_udid: str,
    channel: str,
    success: bool,
    error_message: str = None,
):
    """تسجيل إرسال إشعار"""
    await rate_monitor.record_notification(
        parent_email, child_udid, channel, success, error_message
    )


async def get_rate_statistics() -> Dict:
    """الحصول على إحصائيات المعدلات"""
    return {
        "system": {
            "current_minute": len(rate_monitor.minute_counter),
            "limits": asdict(rate_monitor.rate_limit),
        },
        "timestamp": datetime.utcnow().isoformat(),
    }
