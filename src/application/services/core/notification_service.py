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
from typing import Dict, List, Optional, Tuple

import structlog
from jinja2 import Template

# استيراد النماذج من قاعدة البيانات
try:
    from database import (ChildProfile, Emotion, EmotionSummary, SessionRecord,
                          db_manager)
except ImportError:
    # Fallback للبنية البديلة
    from ...database import (ChildProfile, Emotion, EmotionSummary,
                             SessionRecord, db_manager)

# إعداد logger مهيكل
logger = structlog.get_logger(__name__)

class NotificationChannel(Enum):
    """قنوات الإشعارات المدعومة"""
    EMAIL = "email"
    PUSH = "push"
    SMS = "sms"
    IN_APP = "in_app"

class NotificationPriority(Enum):
    """مستويات أولوية الإشعارات"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

@dataclass
class NotificationData:
    """بيانات الإشعار"""
    child_udid: str
    child_name: str
    parent_email: str
    parent_device_id: Optional[str] = None
    parent_phone: Optional[str] = None
    sessions_count: int = 0
    oldest_date: Optional[datetime] = None
    newest_date: Optional[datetime] = None
    days_until_deletion: int = 2

@dataclass
class NotificationStats:
    """إحصائيات الإشعارات"""
    emails_sent: int = 0
    push_sent: int = 0
    sms_sent: int = 0
    in_app_sent: int = 0
    errors_count: int = 0
    children_notified: int = 0
    execution_time_seconds: float = 0.0

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
            
            self.email_service = EmailService()
            self.push_service = PushService()
            self.sms_service = SMSService()
        except ImportError as e:
            self.logger.warning("Some notification services not available", error=str(e))
            self.email_service = None
            self.push_service = None
            self.sms_service = None
    
    def _load_config(self) -> Any:
        """تحميل إعدادات الإشعارات"""
        try:
            config_path = Path(__file__).parent.parent.parent / "config" / "config.json"
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
            self.logger.warning("Failed to load notification config", error=str(e))
            self.config = {"default_language": "ar", "enable_email": True}
    
    def _load_templates(self) -> Any:
        """تحميل قوالب الإشعارات"""
        try:
            templates_dir = Path(__file__).parent.parent.parent / "templates" / "notifications"
            templates_dir.mkdir(parents=True, exist_ok=True)
            
            # قالب HTML للبريد الإلكتروني
            self.email_template_html = """
            <!DOCTYPE html>
            <html dir="rtl" lang="ar">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>تنبيه AI Teddy Bear</title>
                <style>
                    body { font-family: 'Arial', sans-serif; background-color: #f0f8ff; margin: 0; padding: 20px; }
                    .container { max-width: 600px; margin: 0 auto; background: white; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); overflow: hidden; }
                    .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }
                    .teddy-icon { font-size: 48px; margin-bottom: 10px; }
                    .content { padding: 30px; line-height: 1.6; }
                    .alert-box { background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; padding: 15px; margin: 20px 0; }
                    .data-summary { background: #f8f9fa; border-radius: 8px; padding: 20px; margin: 20px 0; }
                    .button { display: inline-block; background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 8px; margin: 10px 0; }
                    .footer { background: #f8f9fa; padding: 20px; text-align: center; font-size: 14px; color: #666; }
                    .countdown { font-size: 24px; font-weight: bold; color: #e74c3c; text-align: center; margin: 20px 0; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <div class="teddy-icon">🧸</div>
                        <h1>AI Teddy Bear</h1>
                        <h2>تنبيه مهم حول بيانات طفلك</h2>
                    </div>
                    
                    <div class="content">
                        <p>عزيزي ولي الأمر،</p>
                        
                        <div class="alert-box">
                            <h3>⚠️ تنبيه: سيتم حذف البيانات قريباً</h3>
                            <p>نود إعلامكم أن بيانات طفلكم <strong>{{ child_name }}</strong> القديمة ستحذف تلقائياً.</p>
                        </div>
                        
                        <div class="countdown">
                            ⏰ {{ days_until_deletion }} أيام متبقية
                        </div>
                        
                        <div class="data-summary">
                            <h3>📊 ملخص البيانات المتأثرة:</h3>
                            <ul>
                                <li><strong>عدد الجلسات:</strong> {{ sessions_count }}</li>
                                <li><strong>أقدم تسجيل:</strong> {{ oldest_date.strftime('%Y-%m-%d') if oldest_date }}</li>
                                <li><strong>أحدث تسجيل:</strong> {{ newest_date.strftime('%Y-%m-%d') if newest_date }}</li>
                            </ul>
                        </div>
                        
                        <h3>💾 للاحتفاظ بالبيانات:</h3>
                        <ol>
                            <li>سجلوا دخولكم إلى تطبيق AI Teddy</li>
                            <li>اذهبوا إلى قسم "إعدادات البيانات"</li>
                            <li>اختاروا "تصدير البيانات" لحفظها محلياً</li>
                        </ol>
                        
                        <div style="text-align: center;">
                            <a href="https://app.aiteddybear.com/data-export" class="button">تصدير البيانات الآن</a>
                        </div>
                        
                        <p><strong>لماذا نحذف البيانات؟</strong></p>
                        <p>نحن ملتزمون بحماية خصوصية طفلكم وفقاً للقوانين الدولية (GDPR, COPPA). يساعد الحذف الدوري في الحفاظ على أمان البيانات وأداء النظام.</p>
                    </div>
                    
                    <div class="footer">
                        <p>مع أطيب التحيات،<br><strong>فريق AI Teddy Bear</strong></p>
                        <p>📧 support@aiteddybear.com | 📱 تطبيق AI Teddy</p>
                        <p><small>هذا إشعار تلقائي. لا ترد على هذا البريد.</small></p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # قالب نصي للرسائل القصيرة
            self.sms_template = "🧸 تنبيه AI Teddy: بيانات {{ child_name }} ستحذف خلال {{ days_until_deletion }} أيام. صدّر البيانات من التطبيق للاحتفاظ بها."
            
            # قالب الإشعار المحمول
            self.push_template = {
                "title": "🧸 تنبيه AI Teddy Bear",
                "body": "بيانات {{ child_name }} ستحذف خلال {{ days_until_deletion }} أيام. اضغط للتفاصيل.",
                "data": {
                    "type": "data_cleanup_warning",
                    "child_name": "{{ child_name }}",
                    "days_until_deletion": "{{ days_until_deletion }}"
                }
            }
            
        except Exception as e:
            self.logger.error("Failed to load notification templates", error=str(e))
    
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
            stats.execution_time_seconds = (datetime.utcnow() - start_time).total_seconds()
            
            self.logger.info("Cleanup notifications completed", 
                           children_notified=stats.children_notified,
                           emails_sent=stats.emails_sent,
                           execution_time=stats.execution_time_seconds)
            
        except Exception as e:
            stats.errors_count += 1
            self.logger.error("Cleanup notification failed", error=str(e), exc_info=True)
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
                child_profile = session.query(ChildProfile).filter_by(udid=udid).first()
                
                notification = NotificationData(
                    child_udid=udid,
                    child_name=data['child_name'],
                    parent_email=f"parent_{udid}@example.com",  # في الإنتاج: child_profile.parent_email
                    parent_device_id=f"device_{udid}",  # في الإنتاج: child_profile.parent_device_id
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
            self.logger.error("Failed to collect notifications data", error=str(e))
            raise
    
    async def _send_multi_channel_notification(self, notification: NotificationData, stats: NotificationStats):
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
    logger.error(f"Error in operation: {e}", exc_info=True)Exception as e:
    logger.error(f"Error in operation: {e}", exc_info=True)xception as e:
    logger.warning(f"Ignoring error: {e}")
                    return
            except ImportError:
                # إذا لم تكن خدمة المراقبة متاحة، استمر بالإرسال
                pass
            
            # 1. إرسال بريد إلكتروني
            if self.config.get("enable_email", True) and self.email_service:
                success = await self._send_email_notification(notification)
                if success:
                    stats.emails_sent += 1
                    await self._record_notification_success(notification, "email")
                else:
                    stats.errors_count += 1
                    await self._record_notification_error(notification, "email", "Email sending failed")
            
            # 2. إرسال إشعار محمول
            if self.config.get("enable_push", True) and self.push_service:
                success = await self._send_push_notification(notification)
                if success:
                    stats.push_sent += 1
                    await self._record_notification_success(notification, "push")
                else:
                    stats.errors_count += 1
                    await self._record_notification_error(notification, "push", "Push notification failed")
            
            # 3. إرسال رسالة نصية (اختياري)
            if self.config.get("enable_sms", False) and self.sms_service:
                success = await self._send_sms_notification(notification)
                if success:
                    stats.sms_sent += 1
                    await self._record_notification_success(notification, "sms")
                else:
                    stats.errors_count += 1
                    await self._record_notification_error(notification, "sms", "SMS sending failed")
            
            # 4. إشعار داخل التطبيق
            if self.config.get("enable_in_app", True):
                success = await self._send_in_app_notification(notification)
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
                aexcept ImportError as e:
    logger.error(f"Error in operation: {e}", exc_info=True)port_exception("notification_service", e, f"Child UDID: {notificatiexcept ImportError as e:
    logger.error(f"Error in operation: {e}", exc_info=True)_udid}")
            except ImportError as e:
    logger.warning(f"Ignoring error: {e}")
    
    async def _record_notification_success(self, notification: NotificationData, channel: str):
        """تسجيل نجاح إرسال الإشعار"""
        try:
            from .rate_monitor_service import Exception as e:
            from .rate_monitor_service import recexcept
    logger.error(f"Error in operation: {e}", exc_info=True)ification_sent
            await record_notification_sent(
                notification.parent_email,
                notification.child_udid,
except Exception as e:
    logger.error(f"Error in operation: {e}", exc_info=True)        channel,
                True
            )
        except Exception as e:
    logger.warning(f"Ignoring error: {e}")
    
    async def _record_notification_error(self, notification: NotificationData, channel: str, error_message: str):
        """تسجيل except Exception as e:
    logger.error(f"Error in operation: {e}", exc_info=True)ال الإشعار"""
        try:
            from .rate_monitor_service import record_notification_sent
            await record_notification_sent(
                notification.parent_email,
                notification.chiexcept Exception as e:
    logger.error(f"Error in operation: {e}", exc_info=True)
                channel,
                False,
                error_message
            )
        except Exception as e:
    logger.warning(f"Ignoring error: {e}")
    
    async def _send_email_notification(self, notification: NotificationData) -> bool:
        """إرسال إشعار بالبريد الإلكتروني"""
        try:
            # تحضير القالب
            template = Template(self.email_template_html)
            html_content = template.render(
                child_name=notification.child_name,
                sessions_count=notification.sessions_count,
                oldest_date=notification.oldest_date,
                newest_date=notification.newest_date,
                days_until_deletion=notification.days_until_deletion
            )
            
            subject = f"🧸 تنبيه مهم: بيانات {notification.child_name} ستحذف خلال {notification.days_until_deletion} أيام"
            
            # إرسال البريد (محاكاة في بيئة التطوير)
            if self.email_service:
                success = await self.email_service.send_html_email(
                    to_email=notification.parent_email,
                    subject=subject,
                    html_content=html_content
                )
            else:
                # محاكاة الإرسال
                success = True
                self.logger.info("Email notification simulated", 
                               to=notification.parent_email,
                               child=notification.child_name)
            
            return success
            
        except Exception as e:
            self.logger.error("Failed to send email notification", 
                            child_udid=notification.child_udid, error=str(e))
            return False
    
    async def _send_push_notification(self, notification: NotificationData) -> bool:
        """إرسال إشعار محمول"""
        try:
            # تحضير القالب
            template = Template(self.push_template["body"])
            body = template.render(
                child_name=notification.child_name,
                days_until_deletion=notification.days_until_deletion
            )
            
            push_data = {
                "title": self.push_template["title"],
                "body": body,
                "data": {
                    "type": "data_cleanup_warning",
                    "child_udid": notification.child_udid,
                    "child_name": notification.child_name,
                    "days_until_deletion": str(notification.days_until_deletion)
                }
            }
            
            # إرسال الإشعار (محاكاة في بيئة التطوير)
            if self.push_service and notification.parent_device_id:
                success = await self.push_service.send_notification(
                    device_id=notification.parent_device_id,
                    notification=push_data
                )
            else:
                # محاكاة الإرسال
                success = True
                self.logger.info("Push notification simulated",
                               device_id=notification.parent_device_id,
                               child=notification.child_name)
            
            return success
            
        except Exception as e:
            self.logger.error("Failed to send push notification",
                            child_udid=notification.child_udid, error=str(e))
            return False
    
    async def _send_sms_notification(self, notification: NotificationData) -> bool:
        """إرسال رسالة نصية"""
        try:
            # تحضير القالب
            template = Template(self.sms_template)
            message = template.render(
                child_name=notification.child_name,
                days_until_deletion=notification.days_until_deletion
            )
            
            # إرسال الرسالة (محاكاة في بيئة التطوير)
            if self.sms_service and notification.parent_phone:
                success = await self.sms_service.send_sms(
                    phone_number=notification.parent_phone,
                    message=message
                )
            else:
                # محاكاة الإرسال
                success = True
                self.logger.info("SMS notification simulated",
                               phone=notification.parent_phone,
                               child=notification.child_name)
            
            return success
            
        except Exception as e:
            self.logger.error("Failed to send SMS notification",
                            child_udid=notification.child_udid, error=str(e))
            return False
    
    async def _send_in_app_notification(self, notification: NotificationData) -> bool:
        """إرسال إشعار داخل التطبيق"""
        try:
            # حفظ الإشعار في قاعدة البيانات للعرض في التطبيق
            in_app_data = {
                "type": "data_cleanup_warning",
                "title": "🧸 تنبيه مهم من AI Teddy",
                "message": f"بيانات {notification.child_name} ستحذف خلال {notification.days_until_deletion} أيام",
                "child_udid": notification.child_udid,
                "created_at": datetime.utcnow().isoformat(),
                "is_read": False,
                "priority": "high",
                "action_url": "/data-export",
                "expires_at": (datetime.utcnow() + timedelta(days=3)).isoformat()
            }
            
            # في بيئة الإنتاج، سيحفظ في جدول notifications
            self.logger.info("In-app notification created",
                           child_udid=notification.child_udid,
                           notification_data=in_app_data)
            
            return True
            
        except Exception as e:
            self.logger.error("Failed to create in-app notification",
                            child_udid=notification.child_udid, error=str(e))
            return False

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
        logger.info(f"   - Execution time: {stats.execution_time_seconds:.2f}s")
        
    asyncio.run(test_notifications())