#!/usr/bin/env python3
"""
⏰ Scheduler Service - خدمة جدولة المهام
ربط APScheduler مع FastAPI لتشغيل المهام الدورية
"""

import asyncio
from typing import Optional

import structlog
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from .data_cleanup_service import preview_cleanup, run_daily_cleanup
from .notification_service import notify_upcoming_cleanup

# إعداد logger
logger = structlog.get_logger(__name__)


class SchedulerService:
    """
    ⏰ خدمة جدولة المهام الشاملة

    الميزات:
    - جدولة تنظيف البيانات اليومي
    - جدولة التقارير الدورية
    - مراقبة حالة المهام
    - إعادة تشغيل المهام الفاشلة
    """

    def __init__(self):
        self.scheduler: Optional[AsyncIOScheduler] = None
        self.logger = logger.bind(service="scheduler")
        self._setup_scheduler()

    def _setup_scheduler(self) -> Any:
        """إعداد APScheduler"""
        try:
            # إعداد job stores و executors
            jobstores = {
                "default": MemoryJobStore(),
            }

            executors = {
                "default": AsyncIOExecutor(),
            }

            job_defaults = {
                "coalesce": False,
                "max_instances": 3,
                "misfire_grace_time": 30,
            }

            self.scheduler = AsyncIOScheduler(
                jobstores=jobstores,
                executors=executors,
                job_defaults=job_defaults,
                timezone="UTC",
            )

            # إضافة listener للمراقبة
            self.scheduler.add_listener(self._job_listener)

            self.logger.info("Scheduler configured successfully")

        except Exception as e:
            self.logger.error("Failed to setup scheduler", error=str(e))
            raise

    def _job_listener(self, event) -> Any:
        """مراقب الأحداث للمهام"""
        try:
            if event.exception:
                self.logger.error(
                    "Job failed",
                    job_id=event.job_id,
                    exception=str(
                        event.exception))
            else:
                self.logger.info(
                    "Job completed successfully",
                    job_id=event.job_id,
                    scheduled_run_time=event.scheduled_run_time,
                )
        except Exception as e:
            self.logger.error("Error in job listener", error=str(e))

    def start(self) -> Any:
        """بدء تشغيل المجدول"""
        try:
            if not self.scheduler:
                raise RuntimeError("Scheduler not configured")

            # إضافة المهام المحددة مسبقاً
            self._add_scheduled_jobs()

            # بدء التشغيل
            self.scheduler.start()

            self.logger.info("Scheduler started successfully")

        except Exception as e:
            self.logger.error("Failed to start scheduler", error=str(e))
            raise

    def shutdown(bool=True) -> None:
        """إيقاف المجدول"""
        try:
            if self.scheduler and self.scheduler.running:
                self.scheduler.shutdown(wait=wait)
                self.logger.info("Scheduler stopped")

        except Exception as e:
            self.logger.error("Failed to stop scheduler", error=str(e))

    def _add_scheduled_jobs(self) -> Any:
        """إضافة المهام المجدولة حسب المنطقة الزمنية"""
        try:
            # تحميل أوقات مناسبة للمنطقة الزمنية (السعودية UTC+3)
            # الأوقات محسوبة بتوقيت UTC للتشغيل المحلي

            # 1. تنظيف البيانات اليومي - 2 صباحاً بالتوقيت المحلي (23:00 UTC في
            # الشتاء)
            self.scheduler.add_job(
                self._run_data_cleanup,
                CronTrigger(hour=23, minute=0),  # 2 صباحاً بتوقيت الرياض
                id="daily_data_cleanup",
                name="Daily Data Cleanup",
                replace_existing=True,
            )

            # 1.5. إشعارات قبل الحذف - 9 مساءً بالتوقيت المحلي (18:00 UTC)
            # وقت مناسب للوالدين لرؤية الإشعار
            self.scheduler.add_job(
                self._run_notification_job,
                CronTrigger(hour=18, minute=0),  # 9 مساءً بتوقيت الرياض
                id="notification_cleanup_warning",
                name="Cleanup Warning Notifications",
                replace_existing=True,
            )

            # 2. معاينة البيانات - كل ساعة لأغراض المراقبة
            self.scheduler.add_job(
                self._monitor_data_status,
                CronTrigger(minute=0),  # كل ساعة عند الدقيقة 0
                id="hourly_data_monitor",
                name="Hourly Data Monitor",
                replace_existing=True,
            )

            # 3. تحسين قاعدة البيانات - أسبوعياً
            self.scheduler.add_job(
                self._weekly_database_optimization,
                CronTrigger(day_of_week="sun", hour=2, minute=0),
                # الأحد 2 صباحاً
                id="weekly_db_optimization",
                name="Weekly Database Optimization",
                replace_existing=True,
            )

            # 4. تقرير حالة النظام - يومياً
            self.scheduler.add_job(
                self._daily_system_report,
                CronTrigger(hour=6, minute=0),  # 6 صباحاً
                id="daily_system_report",
                name="Daily System Report",
                replace_existing=True,
            )

            self.logger.info(
                "Scheduled jobs added successfully",
                job_count=len(self.scheduler.get_jobs()),
            )

        except Exception as e:
            self.logger.error("Failed to add scheduled jobs", error=str(e))
            raise

    async def _run_data_cleanup(self):
        """تشغيل تنظيف البيانات اليومي"""
        try:
            self.logger.info("Starting daily data cleanup job")

            stats = await run_daily_cleanup()

            self.logger.info(
                "Daily data cleanup completed",
                sessions_deleted=stats.sessions_deleted,
                emotions_deleted=stats.emotions_deleted,
                children_notified=stats.children_notified,
                execution_time=stats.execution_time_seconds,
            )

        except Exception as e:
            self.logger.error("Daily data cleanup failed", error=str(e))
            raise

    async def _run_notification_job(self):
        """تشغيل مهمة إشعارات قبل الحذف"""
        try:
            self.logger.info("Starting cleanup notification job")

            stats = await notify_upcoming_cleanup()

            self.logger.info(
                "Cleanup notifications completed",
                children_notified=stats.children_notified,
                emails_sent=stats.emails_sent,
                push_sent=stats.push_sent,
                errors_count=stats.errors_count,
                execution_time=stats.execution_time_seconds,
            )

        except Exception as e:
            self.logger.error("Cleanup notification job failed", error=str(e))
            raise

    async def _monitor_data_status(self):
        """مراقبة حالة البيانات"""
        try:
            # معاينة البيانات المرشحة للحذف
            preview = await preview_cleanup()

            total_items = preview.get("items_to_delete", {}).get("total", 0)

            if total_items > 10000:  # تنبيه إذا كان هناك كمية كبيرة
                self.logger.warning(
                    "Large amount of data pending cleanup",
                    total_items=total_items)

            self.logger.debug(
                "Data status monitored", items_pending_cleanup=total_items
            )

        except Exception as e:
            self.logger.error("Data monitoring failed", error=str(e))

    async def _weekly_database_optimization(self):
        """تحسين قاعدة البيانات الأسبوعي"""
        try:
            self.logger.info("Starting weekly database optimization")

            from database import db_manager

            session = db_manager.Session()

            # تشغيل VACUUM و ANALYZE
            session.execute("VACUUM")
            session.execute("ANALYZE")
            session.commit()
            session.close()

            self.logger.info("Weekly database optimization completed")

        except Exception as e:
            self.logger.error("Database optimization failed", error=str(e))

    async def _daily_system_report(self):
        """تقرير حالة النظام اليومي"""
        try:
            self.logger.info("Generating daily system report")

            from database import db_manager

            session = db_manager.Session()

            # إحصائيات سريعة
            from database import ChildProfile, Emotion, SessionRecord

            total_sessions = session.query(SessionRecord).count()
            total_emotions = session.query(Emotion).count()
            total_children = session.query(ChildProfile).count()

            session.close()

            self.logger.info(
                "Daily system report generated",
                total_sessions=total_sessions,
                total_emotions=total_emotions,
                total_children=total_children,
            )

        except Exception as e:
            self.logger.error("System report generation failed", error=str(e))

    def add_custom_job(str, **kwargs) -> None:
        """إضافة مهمة مخصصة"""
        try:
            self.scheduler.add_job(
                func, trigger, id=job_id, replace_existing=True, **kwargs
            )

            self.logger.info("Custom job added", job_id=job_id)

        except Exception as e:
            self.logger.error(
                "Failed to add custom job",
                job_id=job_id,
                error=str(e))
            raise

    def remove_job(str) -> None:
        """إزالة مهمة"""
        try:
            self.scheduler.remove_job(job_id)
            self.logger.info("Job removed", job_id=job_id)

        except Exception as e:
            self.logger.error(
                "Failed to remove job",
                job_id=job_id,
                error=str(e))

    def get_jobs_status(self) -> dict:
        """الحصول على حالة جميع المهام"""
        try:
            jobs = self.scheduler.get_jobs()

            jobs_info = []
            for job in jobs:
                job_info = {
                    "id": job.id,
                    "name": job.name,
                    "next_run_time": (
                        job.next_run_time.isoformat() if job.next_run_time else None
                    ),
                    "trigger": str(job.trigger),
                    "func": (
                        job.func.__name__
                        if hasattr(job.func, "__name__")
                        else str(job.func)
                    ),
                }
                jobs_info.append(job_info)

            return {
                "scheduler_running": (
                    self.scheduler.running if self.scheduler else False
                ),
                "total_jobs": len(jobs),
                "jobs": jobs_info,
            }

        except Exception as e:
            self.logger.error("Failed to get jobs status", error=str(e))
            return {"error": str(e)}


# 🔧 مثيل خدمة الجدولة العامة
scheduler_service = SchedulerService()


# 🚀 دوال مساعدة
def start_scheduler() -> Any:
    """بدء تشغيل المجدول"""
    scheduler_service.start()


def stop_scheduler(bool=True) -> None:
    """إيقاف المجدول"""
    scheduler_service.shutdown(wait=wait)


def get_scheduler_status() -> dict:
    """الحصول على حالة المجدول"""
    return scheduler_service.get_jobs_status()


async def trigger_cleanup_now():
    """تشغيل تنظيف البيانات فوراً"""
    return await scheduler_service._run_data_cleanup()


async def trigger_notifications_now():
    """تشغيل الإشعارات فوراً"""
    return await scheduler_service._run_notification_job()


if __name__ == "__main__":
    # اختبار الخدمة

    async def test_scheduler():
        logger.info("🧪 Testing Scheduler Service...")

        # بدء المجدول
        start_scheduler()

        # عرض حالة المهام
        status = get_scheduler_status()
        logger.info("📋 Scheduler Status:")
        logger.info(json.dumps(status, indent=2, ensure_ascii=False))

        # انتظار قليل ثم إيقاف
        await asyncio.sleep(5)
        stop_scheduler()

        logger.info("✅ Scheduler test completed")

    import json

    asyncio.run(test_scheduler())
