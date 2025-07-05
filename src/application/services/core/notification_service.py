#!/usr/bin/env python3
"""
🛎️ Notification Service - خدمة الإشعارات الشاملة
إرسال تنبيهات للوالدين قبل حذف البيانات مع دعم متعدد القنوات
"""

import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

import structlog
from jinja2 import Template

from .notification_models import (
    NotificationChannel,
    NotificationPriority,
    NotificationData,
    NotificationStats,
)

# استيراد النماذج من قاعدة البيانات
try:
    from database import (ChildProfile, Emotion, EmotionSummary, SessionRecord,
                          db_manager)
except ImportError:
    # Fallback للبنية البديلة
    from ...database import (ChildProfile, Emotion, EmotionSummary,
                             SessionRecord, db_manager)

from .channels.in_app_notifier import InAppNotifier
from .channels.sms_sender import SmsSender
from .channels.push_sender import PushSender
from .channels.email_sender import EmailSender

# إعداد logger مهيكل
logger = structlog.get_logger(__name__)


class NotificationService:
    """
    🛎️ خدمة الإشعارات الشاملة

    الميزات:
    - إشعارات متعددة القنوات (Email, Push, SMS, In-App)
    - قوالب HTML جميلة ومخصصة
    - جدولة ذكية للإشعارات
    - تتبع حالة الإرسال
    - معالجة شاملة للأخطاء
    - دعم اللغات المتعددة
    """

    def __init__(self):
        self.logger = logger.bind(service="notifications")
        self._load_config()
        self._load_templates()

        # استيراد خدمات الإرسال
        try:
            from .email_service import EmailService
            from .push_service import PushService
            from .sms_service import SMSService

            self.email_sender = EmailSender(
                EmailService(), self.email_template_html)
            self.push_sender = PushSender(PushService(), self.push_template)
            self.sms_sender = SmsSender(SMSService(), self.sms_template)
            self.in_app_notifier = InAppNotifier()
        except ImportError as e:
            self.logger.warning(
                "Some notification services not available",
                error=str(e))
            self.email_sender = EmailSender(None, self.email_template_html)
            self.push_sender = PushSender(None, self.push_template)
            self.sms_sender = SmsSender(None, self.sms_template)
            self.in_app_notifier = InAppNotifier()

    def _load_config(self) -> Any:
        """تحميل إعدادات الإشعارات"""
        try:
            config_path = Path(__file__).parent.parent.parent / \
                "config" / "config.json"
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            self.config = config.get("NOTIFICATION_CONFIG", {
                "default_language": "ar",
                "retry_attempts": 3,
                "retry_delay_seconds": 30,
                "batch_size": 100,
                "rate_limit_per_minute": 60,
                "enable_email": True,
                "enable_push": True,
                "enable_sms": False,
                "enable_in_app": True
            })
        except Exception as e:
            self.logger.warning(
                "Failed to load notification config",
                error=str(e))
            self.config = {"default_language": "ar", "enable_email": True}

    def _load_templates(self) -> Any:
        """تحميل قوالب الإشعارات"""
        try:
            templates_dir = Path(__file__).parent.parent.parent / \
                "templates" / "notifications"

            with open(templates_dir / "data_cleanup_email.html", 'r', encoding='utf-8') as f:
                self.email_template_html = f.read()

            with open(templates_dir / "data_cleanup_sms.txt", 'r', encoding='utf-8') as f:
                self.sms_template = f.read()

            with open(templates_dir / "data_cleanup_push.json", 'r', encoding='utf-8') as f:
                self.push_template = json.load(f)

        except Exception as e:
            self.logger.error(
                "Failed to load notification templates", error=str(e))
            # Fallback to empty templates
            self.email_template_html = ""
            self.sms_template = ""
            self.push_template = {}

    async def notify_upcoming_cleanup(self) -> NotificationStats:
        """
        🚨 تنبيه الوالدين قبل حذف البيانات بيومين

        Returns:
            NotificationStats: إحصائيات عملية الإرسال
        """
        start_time = datetime.utcnow()
        stats = NotificationStats()

        self.logger.info("Starting cleanup notification process")

        try:
            # 1. جمع البيانات المتأثرة
            notifications_data = await self._collect_notifications_data()

            # 2. إرسال الإشعارات
            for notification in notifications_data:
                await self._send_multi_channel_notification(notification, stats)

            stats.children_notified = len(notifications_data)
            stats.execution_time_seconds = (
                datetime.utcnow() - start_time).total_seconds()

            self.logger.info("Cleanup notifications completed",
                             children_notified=stats.children_notified,
                             emails_sent=stats.emails_sent,
                             execution_time=stats.execution_time_seconds)

        except Exception as e:
            stats.errors_count += 1
            self.logger.error(
                "Cleanup notification failed",
                error=str(e),
                exc_info=True)
            raise

        return stats

    async def _collect_notifications_data(self) -> List[NotificationData]:
        """جمع بيانات الإشعارات المطلوبة"""
        try:
            # تاريخ التحذير: البيانات التي عمرها 28 يوم (ستحذف خلال يومين)
            warn_date = datetime.utcnow() - timedelta(days=28)

            session = db_manager.Session()

            # البحث عن الجلسات التي ستحذف قريباً
            sessions_to_warn = session.query(SessionRecord).filter(
                SessionRecord.timestamp <= warn_date
            ).all()

            # تجميع البيانات حسب UDID
            children_data = {}
            for session_record in sessions_to_warn:
                udid = session_record.udid
                if udid not in children_data:
                    children_data[udid] = {
                        'child_name': session_record.child_name,
                        'sessions': [],
                        'oldest_date': session_record.timestamp,
                        'newest_date': session_record.timestamp
                    }

                children_data[udid]['sessions'].append(session_record)

                # تحديث نطاق التواريخ
                if session_record.timestamp < children_data[udid]['oldest_date']:
                    children_data[udid]['oldest_date'] = session_record.timestamp
                if session_record.timestamp > children_data[udid]['newest_date']:
                    children_data[udid]['newest_date'] = session_record.timestamp

            # إنشاء قائمة الإشعارات
            notifications = []
            for udid, data in children_data.items():
                # البحث عن معلومات الوالدين من ChildProfile
                child_profile = session.query(
                    ChildProfile).filter_by(udid=udid).first()

                notification = NotificationData(
                    child_udid=udid,
                    child_name=data['child_name'],
                    # في الإنتاج: child_profile.parent_email
                    parent_email=f"parent_{udid}@example.com",
                    # في الإنتاج: child_profile.parent_device_id
                    parent_device_id=f"device_{udid}",
                    sessions_count=len(data['sessions']),
                    oldest_date=data['oldest_date'],
                    newest_date=data['newest_date'],
                    days_until_deletion=2
                )
                notifications.append(notification)

            session.close()

            self.logger.info("Collected notification data",
                             children_count=len(notifications),
                             total_sessions=sum(n.sessions_count for n in notifications))

            return notifications

        except Exception as e:
            self.logger.error(
                "Failed to collect notifications data",
                error=str(e))
            raise

    async def _send_multi_channel_notification(
            self,
            notification: NotificationData,
            stats: NotificationStats):
        """إرسال إشعار متعدد القنوات مع مراقبة المعدلات"""
        try:
            # فحص حدود معدل الإرسال
            try:
                from .rate_monitor_service import (
                    check_notification_rate_limit, record_notification_sent)

                can_send, reason = await check_notification_rate_limit(
                    notification.parent_email,
                    notification.child_udid
                )

                if not can_send:
                    self.logger.warning("Rate limit exceeded",
                                        parent_email=notification.parent_email,
                                        reason=reason)
                    # تسجيل في نظام تتبع الأخطاء
                    try:
                        from .issue_tracker_service import report_issue
                        await report_issue(
                            "Rate Limit Exceeded",
                            f"Parent: {notification.parent_email}, Reason: {reason}",
                            "medium",
                            "rate_monitor",
                            "rate_limit_exceeded"
                        )
                    except Exception as e:
                        self.logger.warning(
                            f"Could not report issue to tracker: {e}")
                    return
            except ImportError:
                # إذا لم تكن خدمة المراقبة متاحة، استمر بالإرسال
                self.logger.debug(
                    "Rate monitor service not available, skipping check.")
                pass

            # 1. إرسال بريد إلكتروني
            if self.config.get("enable_email", True) and self.email_sender:
                success = await self.email_sender.send(notification)
                if success:
                    stats.emails_sent += 1
                    await self._record_notification_success(notification, "email")
                else:
                    stats.errors_count += 1
                    await self._record_notification_error(notification, "email", "Email sending failed")

            # 2. إرسال إشعار محمول
            if self.config.get("enable_push", True) and self.push_sender:
                success = await self.push_sender.send(notification)
                if success:
                    stats.push_sent += 1
                    await self._record_notification_success(notification, "push")
                else:
                    stats.errors_count += 1
                    await self._record_notification_error(notification, "push", "Push notification failed")

            # 3. إرسال رسالة نصية (اختياري)
            if self.config.get("enable_sms", False) and self.sms_sender:
                success = await self.sms_sender.send(notification)
                if success:
                    stats.sms_sent += 1
                    await self._record_notification_success(notification, "sms")
                else:
                    stats.errors_count += 1
                    await self._record_notification_error(notification, "sms", "SMS sending failed")

            # 4. إشعار داخل التطبيق
            if self.config.get("enable_in_app", True) and self.in_app_notifier:
                success = await self.in_app_notifier.send(notification)
                if success:
                    stats.in_app_sent += 1
                    await self._record_notification_success(notification, "in_app")
                else:
                    stats.errors_count += 1
                    await self._record_notification_error(notification, "in_app", "In-app notification failed")

        except Exception as e:
            self.logger.error("Failed to send multi-channel notification",
                              child_udid=notification.child_udid, error=str(e))
            stats.errors_count += 1

            # تسجيل الخطأ في نظام تتبع الأخطاء
            try:
                from .issue_tracker_service import report_exception
                await report_exception(
                    "notification_service", e, f"Child UDID: {notification.child_udid}"
                )
            except ImportError:
                self.logger.warning(
                    "Issue tracker service not available, skipping.")
            except Exception as report_e:
                self.logger.error(f"Failed to report issue: {report_e}")

    async def _record_notification_success(self, notification: NotificationData, channel: str):
        """تسجيل نجاح إرسال الإشعار"""
        try:
            from .rate_monitor_service import record_notification_sent
            await record_notification_sent(
                notification.parent_email,
                notification.child_udid,
                channel,
                True
            )
        except ImportError:
            self.logger.debug("Rate monitor service not available, skipping.")
        except Exception as e:
            self.logger.warning(f"Failed to record notification success: {e}")

    async def _record_notification_error(self, notification: NotificationData, channel: str, error_message: str):
        """تسجيل خطأ ارسال الإشعار"""
        try:
            from .rate_monitor_service import record_notification_sent
            await record_notification_sent(
                notification.parent_email,
                notification.child_udid,
                channel,
                False,
                error_message
            )
        except ImportError:
            self.logger.debug("Rate monitor service not available, skipping.")
        except Exception as e:
            self.logger.warning(f"Failed to record notification error: {e}")


# 🔧 مثيل خدمة الإشعارات العامة
notification_service = NotificationService()

# 🚀 دوال مساعدة للاستخدام المباشر


async def notify_upcoming_cleanup() -> NotificationStats:
    """تنبيه الوالدين قبل حذف البيانات"""
    return await notification_service.notify_upcoming_cleanup()

# دالة متوافقة مع الكود الأصلي


def notify_upcoming_cleanup_sync() -> Any:
    """نسخة متزامنة للتوافق مع الكود القديم"""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(notify_upcoming_cleanup())


if __name__ == "__main__":
    # اختبار الخدمة
    async def test_notifications():
        logger.info("🧪 Testing Notification Service...")

        stats = await notify_upcoming_cleanup()
        logger.info("📊 Notification Stats:")
        logger.info(f"   - Children notified: {stats.children_notified}")
        logger.info(f"   - Emails sent: {stats.emails_sent}")
        logger.info(f"   - Push notifications sent: {stats.push_sent}")
        logger.info(
            f"   - Execution time: {stats.execution_time_seconds:.2f}s")

    asyncio.run(test_notifications())
