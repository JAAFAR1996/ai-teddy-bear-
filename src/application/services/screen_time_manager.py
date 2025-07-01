from typing import Any, Dict, List, Optional

#!/usr/bin/env python3
"""
⏰ مدير وقت الاستخدام والتحكم الأبوي
يتولى مراقبة وقت اللعب وإرسال تنبيهات للراحة
"""

import asyncio
import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class UsageSession:
    """جلسة استخدام واحدة"""

    child_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    activity_type: str = "general"
    duration_seconds: int = 0
    warnings_sent: List[str] = None

    def __post_init__(self):
        if self.warnings_sent is None:
            self.warnings_sent = []

    def get_duration(self) -> int:
        """الحصول على مدة الجلسة بالثواني"""
        if self.end_time:
            return int((self.end_time - self.start_time).total_seconds())
        return int((datetime.now() - self.start_time).total_seconds())


@dataclass
class ScreenTimeSettings:
    """إعدادات وقت الاستخدام"""

    child_id: str
    daily_limit_minutes: int = 60
    session_limit_minutes: int = 30
    warning_intervals: List[int] = None
    break_reminder_minutes: int = 15
    sleep_time_start: str = "21:00"
    sleep_time_end: str = "07:00"
    allowed_days: List[str] = None

    def __post_init__(self):
        if self.warning_intervals is None:
            self.warning_intervals = [10, 5, 2]
        if self.allowed_days is None:
            self.allowed_days = [
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
            ]


class ScreenTimeManager:
    """مدير وقت الاستخدام"""

    def __init__(self, data_dir: str = "data/screen_time"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.active_sessions: Dict[str, UsageSession] = {}
        self.settings: Dict[str, ScreenTimeSettings] = {}
        self.daily_usage: Dict[str, Dict[str, int]] = {}

        self.warning_tasks: Dict[str, List[asyncio.Task]] = {}
        self.break_reminder_tasks: Dict[str, asyncio.Task] = {}

        self._load_data()
        self.monitoring_task = None
        self.start_monitoring()

    def _load_data(self) -> Any:
        """تحميل البيانات من الملفات"""
        try:
            settings_file = self.data_dir / "settings.json"
            if settings_file.exists():
                with open(settings_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for child_id, settings_data in data.items():
                        self.settings[child_id] = ScreenTimeSettings(**settings_data)

            usage_file = self.data_dir / "daily_usage.json"
            if usage_file.exists():
                with open(usage_file, "r", encoding="utf-8") as f:
                    self.daily_usage = json.load(f)

        except Exception as e:
            logger.error(f"خطأ في تحميل بيانات وقت الاستخدام: {e}")

    def _save_data(self) -> Any:
        """حفظ البيانات في الملفات"""
        try:
            settings_file = self.data_dir / "settings.json"
            settings_data = {
                child_id: asdict(settings)
                for child_id, settings in self.settings.items()
            }
            with open(settings_file, "w", encoding="utf-8") as f:
                json.dump(settings_data, f, ensure_ascii=False, indent=2)

            usage_file = self.data_dir / "daily_usage.json"
            with open(usage_file, "w", encoding="utf-8") as f:
                json.dump(self.daily_usage, f, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error(f"خطأ في حفظ بيانات وقت الاستخدام: {e}")

    def get_child_settings(self, child_id: str) -> ScreenTimeSettings:
        """الحصول على إعدادات طفل محدد"""
        if child_id not in self.settings:
            self.settings[child_id] = ScreenTimeSettings(child_id=child_id)
            self._save_data()
        return self.settings[child_id]

    async def start_session(
        self, child_id: str, activity_type: str = "general"
    ) -> bool:
        """بدء جلسة استخدام جديدة"""
        if child_id in self.active_sessions:
            logger.warning(f"جلسة نشطة موجودة للطفل: {child_id}")
            return False

        settings = self.get_child_settings(child_id)

        if not self._is_allowed_time(settings):
            logger.info("⛔ وقت غير مسموح للعب. تعال لنلعب في وقت آخر!")
            return False

        today = datetime.now().strftime("%Y-%m-%d")
        daily_used = self._get_daily_usage(child_id, today)

        if daily_used >= settings.daily_limit_minutes:
            logger.info("📅 انتهى وقت اللعب لليوم! سنلعب مرة أخرى غداً 🌙")
            return False

        session = UsageSession(
            child_id=child_id, start_time=datetime.now(), activity_type=activity_type
        )

        self.active_sessions[child_id] = session

        await self._setup_session_warnings(child_id, settings)
        await self._setup_break_reminders(child_id, settings)

        logger.info(f"بدأت جلسة جديدة للطفل {child_id}: {activity_type}")
        return True

    def _is_allowed_time(self, settings: ScreenTimeSettings) -> bool:
        """التحقق من أن الوقت الحالي مسموح للعب"""
        now = datetime.now()
        day_name = now.strftime("%A").lower()

        if day_name not in settings.allowed_days:
            return False

        current_time = now.strftime("%H:%M")
        if settings.sleep_time_start <= settings.sleep_time_end:
            if settings.sleep_time_start <= current_time <= settings.sleep_time_end:
                return False
        else:
            if (
                current_time >= settings.sleep_time_start
                or current_time <= settings.sleep_time_end
            ):
                return False

        return True

    def _get_daily_usage(self, child_id: str, date: str) -> int:
        """الحصول على الاستخدام اليومي بالدقائق"""
        return self.daily_usage.get(child_id, {}).get(date, 0)

    async def _setup_session_warnings(
        self, child_id: str, settings: ScreenTimeSettings
    ):
        """إعداد تنبيهات الجلسة"""
        if child_id not in self.warning_tasks:
            self.warning_tasks[child_id] = []

        session_limit_seconds = settings.session_limit_minutes * 60

        for warning_minutes in settings.warning_intervals:
            warning_seconds = session_limit_seconds - (warning_minutes * 60)

            if warning_seconds > 0:
                task = asyncio.create_task(
                    self._send_warning_after_delay(
                        child_id, warning_seconds, warning_minutes
                    )
                )
                self.warning_tasks[child_id].append(task)

    async def _send_warning_after_delay(
        self, child_id: str, delay_seconds: int, minutes_remaining: int
    ):
        """إرسال تنبيه بعد تأخير محدد"""
        await asyncio.sleep(delay_seconds)

        if child_id in self.active_sessions:
            logger.info(
                f"🕐 {child_id}: باقي {minutes_remaining} دقائق على انتهاء وقت اللعب!"
            )

    async def _setup_break_reminders(self, child_id: str, settings: ScreenTimeSettings):
        """إعداد تذكيرات الراحة"""
        break_seconds = settings.break_reminder_minutes * 60

        task = asyncio.create_task(
            self._send_break_reminder_loop(child_id, break_seconds)
        )
        self.break_reminder_tasks[child_id] = task

    async def _send_break_reminder_loop(self, child_id: str, interval_seconds: int):
        """حلقة إرسال تذكيرات الراحة"""
        while child_id in self.active_sessions:
            await asyncio.sleep(interval_seconds)

            if child_id in self.active_sessions:
                logger.info(
                    f"🤸‍♂️ {child_id}: هل تريد أخذ استراحة قصيرة؟ تحرك قليلاً أو اشرب الماء!"
                )

    def start_monitoring(self) -> Any:
        """بدء مراقبة الجلسات النشطة"""
        try:
            if self.monitoring_task is None or self.monitoring_task.done():
                loop = asyncio.get_running_loop()
                self.monitoring_task = loop.create_task(self._monitoring_loop())
        except RuntimeError:
            # لا توجد حلقة أحداث نشطة، سيتم بدء المراقبة عند الحاجة
            pass

    async def _monitoring_loop(self):
        """حلقة مراقبة الجلسات"""
        while True:
            try:
                await asyncio.sleep(60)  # فحص كل دقيقة
                # إضافة منطق المراقبة هنا
            except Exception as e:
                logger.error(f"خطأ في حلقة المراقبة: {e}")

    async def end_session(self, child_id: str):
        """إنهاء جلسة الاستخدام"""
        if child_id not in self.active_sessions:
            return

        session = self.active_sessions[child_id]
        session.end_time = datetime.now()
        session.duration_seconds = session.get_duration()

        # إلغاء المؤقتات
        await self._cancel_warnings(child_id)
        await self._cancel_break_reminders(child_id)

        # تحديث الاستخدام اليومي
        today = datetime.now().strftime("%Y-%m-%d")
        duration_minutes = session.duration_seconds // 60
        self._add_daily_usage(child_id, today, duration_minutes)

        del self.active_sessions[child_id]

        logger.info(f"انتهت جلسة الطفل {child_id}: {duration_minutes} دقيقة")

    def _add_daily_usage(int) -> None:
        """إضافة دقائق للاستخدام اليومي"""
        if child_id not in self.daily_usage:
            self.daily_usage[child_id] = {}

        if date not in self.daily_usage[child_id]:
            self.daily_usage[child_id][date] = 0

        self.daily_usage[child_id][date] += minutes
        self._save_data()

    async def _cancel_warnings(self, child_id: str):
        """إلغاء جميع تنبيهات الطفل"""
        if child_id in self.warning_tasks:
            for task in self.warning_tasks[child_id]:
                task.cancel()
            del self.warning_tasks[child_id]

    async def _cancel_break_reminders(self, child_id: str):
        """إلغاء تذكيرات الراحة"""
        if child_id in self.break_reminder_tasks:
            self.break_reminder_tasks[child_id].cancel()
            del self.break_reminder_tasks[child_id]

    def get_usage_statistics(self, child_id: str, days: int = 7) -> Dict:
        """الحصول على إحصائيات الاستخدام"""
        stats = {
            "daily_usage": {},
            "total_minutes": 0,
            "average_daily": 0,
            "current_session": None,
            "today_remaining": 0,
        }

        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            daily_minutes = self._get_daily_usage(child_id, date)
            stats["daily_usage"][date] = daily_minutes
            stats["total_minutes"] += daily_minutes

        if days > 0:
            stats["average_daily"] = stats["total_minutes"] / days

        if child_id in self.active_sessions:
            session = self.active_sessions[child_id]
            stats["current_session"] = {
                "duration_minutes": session.get_duration() // 60,
                "activity_type": session.activity_type,
                "start_time": session.start_time.isoformat(),
            }

        settings = self.get_child_settings(child_id)
        today = datetime.now().strftime("%Y-%m-%d")
        used_today = self._get_daily_usage(child_id, today)
        stats["today_remaining"] = max(0, settings.daily_limit_minutes - used_today)

        return stats
