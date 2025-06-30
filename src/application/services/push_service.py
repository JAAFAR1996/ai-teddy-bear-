#!/usr/bin/env python3
"""
📱 Push Notification Service - خدمة الإشعارات المحمولة
إرسال إشعارات push للهواتف الذكية عبر Firebase و APNs
"""

import asyncio
import logging
from typing import Dict, List, Optional
from pathlib import Path
import json

import structlog
import httpx

# إعداد logger
logger = structlog.get_logger(__name__)

class PushService:
    """
    📱 خدمة الإشعارات المحمولة المتقدمة
    
    الميزات:
    - دعم Firebase Cloud Messaging (FCM)
    - دعم Apple Push Notifications (APNs)
    - إرسال غير متزامن
    - تجميع الإشعارات
    - تتبع حالة التسليم
    """
    
    def __init__(self):
        self.logger = logger.bind(service="push")
        self._load_config()
        self._setup_clients()
    
    def _load_config(self) -> Any:
        """تحميل إعدادات الإشعارات المحمولة"""
        try:
            config_path = Path(__file__).parent.parent.parent / "config" / "config.json"
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            push_config = config.get("PUSH_CONFIG", {})
            
            # إعدادات Firebase
            self.fcm_server_key = push_config.get("fcm_server_key", "")
            self.fcm_sender_id = push_config.get("fcm_sender_id", "")
            
            # إعدادات APNs
            self.apns_key_id = push_config.get("apns_key_id", "")
            self.apns_team_id = push_config.get("apns_team_id", "")
            self.apns_bundle_id = push_config.get("apns_bundle_id", "com.aiteddybear.app")
            
            # إعدادات عامة
            self.timeout = push_config.get("timeout", 30)
            self.max_retries = push_config.get("max_retries", 3)
            
        except Exception as e:
            self.logger.warning("Failed to load push config", error=str(e))
            # إعدادات افتراضية
            self.fcm_server_key = ""
            self.fcm_sender_id = ""
            self.apns_key_id = ""
            self.apns_team_id = ""
            self.apns_bundle_id = "com.aiteddybear.app"
            self.timeout = 30
            self.max_retries = 3
    
    def _setup_clients(self) -> Any:
        """إعداد عملاء HTTP"""
        self.http_client = httpx.AsyncClient(timeout=self.timeout)
        
        # URLs للخدمات
        self.fcm_url = "https://fcm.googleapis.com/fcm/send"
        self.apns_url = "https://api.push.apple.com/3/device"
    
    async def send_notification(self, 
                              device_id: str, 
                              notification: Dict,
                              platform: str = "auto") -> bool:
        """
        إرسال إشعار لجهاز محدد
        
        Args:
            device_id: معرف الجهاز
            notification: بيانات الإشعار
            platform: النظام (android/ios/auto)
            
        Returns:
            bool: نجح الإرسال أم لا
        """
        try:
            # تحديد النظام تلقائياً إذا لم يحدد
            if platform == "auto":
                platform = self._detect_platform(device_id)
            
            # إرسال حسب النظام
            if platform == "android":
                success = await self._send_fcm_notification(device_id, notification)
            elif platform == "ios":
                success = await self._send_apns_notification(device_id, notification)
            else:
                # محاكاة للأنظمة غير المدعومة
                success = await self._simulate_notification(device_id, notification)
            
            if success:
                self.logger.info("Push notification sent successfully", 
                               device_id=device_id, platform=platform)
            else:
                self.logger.error("Failed to send push notification", 
                                device_id=device_id, platform=platform)
            
            return success
            
        except Exception as e:
            self.logger.error("Push notification sending failed", 
                            device_id=device_id, error=str(e), exc_info=True)
            return False
    
    async def send_batch_notifications(self, 
                                     notifications: List[Dict]) -> Dict[str, int]:
        """
        إرسال مجموعة إشعارات
        
        Args:
            notifications: قائمة الإشعارات [{"device_id": "", "notification": {}, "platform": ""}]
            
        Returns:
            Dict: إحصائيات الإرسال
        """
        stats = {"sent": 0, "failed": 0, "total": len(notifications)}
        
        try:
            # إرسال متوازي لتحسين الأداء
            tasks = []
            for notif in notifications:
                task = self.send_notification(
                    device_id=notif["device_id"],
                    notification=notif["notification"],
                    platform=notif.get("platform", "auto")
                )
                tasks.append(task)
            
            # انتظار جميع المهام
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # تجميع النتائج
            for result in results:
                if isinstance(result, bool) and result:
                    stats["sent"] += 1
                else:
                    stats["failed"] += 1
            
            self.logger.info("Batch notifications completed", stats=stats)
            
        except Exception as e:
            self.logger.error("Batch notifications failed", error=str(e))
            stats["failed"] = stats["total"]
        
        return stats
    
    async def _send_fcm_notification(self, device_id: str, notification: Dict) -> bool:
        """إرسال إشعار عبر Firebase Cloud Messaging"""
        try:
            # في بيئة التطوير، نحاكي الإرسال
            if not self.fcm_server_key or self.fcm_server_key == "your_fcm_key":
                self.logger.info("FCM notification simulated (no server key configured)",
                               device_id=device_id)
                return True
            
            # تحضير البيانات
            headers = {
                'Authorization': f'key={self.fcm_server_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'to': device_id,
                'notification': {
                    'title': notification.get('title', 'AI Teddy Bear'),
                    'body': notification.get('body', ''),
                    'icon': notification.get('icon', 'teddy_icon'),
                    'sound': notification.get('sound', 'default'),
                    'click_action': notification.get('click_action', 'FLUTTER_NOTIFICATION_CLICK')
                },
                'data': notification.get('data', {}),
                'priority': 'high',
                'time_to_live': 3600  # ساعة واحدة
            }
            
            # الإرسال
            response = await self.http_client.post(
                self.fcm_url,
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get('success', 0) > 0:
                    return True
                else:
                    self.logger.error("FCM sending failed", 
                                    response=response_data)
                    return False
            else:
                self.logger.error("FCM HTTP error", 
                                status_code=response.status_code,
                                response=response.text)
                return False
            
        except Exception as e:
            self.logger.error("FCM notification failed", error=str(e))
            return False
    
    async def _send_apns_notification(self, device_id: str, notification: Dict) -> bool:
        """إرسال إشعار عبر Apple Push Notifications"""
        try:
            # في بيئة التطوير، نحاكي الإرسال
            if not self.apns_key_id or self.apns_key_id == "your_apns_key":
                self.logger.info("APNs notification simulated (no key configured)",
                               device_id=device_id)
                return True
            
            # تحضير البيانات
            headers = {
                'authorization': f'bearer {self._generate_jwt_token()}',
                'apns-topic': self.apns_bundle_id,
                'apns-push-type': 'alert',
                'apns-priority': '10',
                'apns-expiration': '0'
            }
            
            payload = {
                'aps': {
                    'alert': {
                        'title': notification.get('title', 'AI Teddy Bear'),
                        'body': notification.get('body', '')
                    },
                    'sound': notification.get('sound', 'default'),
                    'badge': notification.get('badge', 1)
                },
                'data': notification.get('data', {})
            }
            
            url = f"{self.apns_url}/{device_id}"
            
            # الإرسال
            response = await self.http_client.post(
                url,
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                return True
            else:
                self.logger.error("APNs HTTP error", 
                                status_code=response.status_code,
                                response=response.text)
                return False
            
        except Exception as e:
            self.logger.error("APNs notification failed", error=str(e))
            return False
    
    async def _simulate_notification(self, device_id: str, notification: Dict) -> bool:
        """محاكاة إرسال الإشعار للتطوير والاختبار"""
        try:
            self.logger.info("Push notification simulated",
                           device_id=device_id,
                           title=notification.get('title', ''),
                           body=notification.get('body', ''))
            
            # محاكاة تأخير الشبكة
            await asyncio.sleep(0.1)
            
            return True
            
        except Exception as e:
            self.logger.error("Simulation failed", error=str(e))
            return False
    
    def _detect_platform(self, device_id: str) -> str:
        """اكتشاف نظام التشغيل من معرف الجهاز"""
        try:
            # قواعد بسيطة لاكتشاف النظام
            if device_id.startswith('f') and len(device_id) > 100:
                return "android"  # FCM tokens are usually longer
            elif len(device_id) == 64:
                return "ios"  # APNs tokens are 64 characters
            else:
                return "unknown"
                
        except Exception as e:
    logger.error(f"Error: {e}", exc_info=True)as e:
    logger.error(f"Error: {e}", exc_info=True)            return "unknown"
    
    def _generate_jwt_token(self) -> str:
        """إنشاء JWT token لـ APNs"""
        # في بيئة الإنتاج، ستنشئ JWT token حقيقي
        # هنا نعيد token وهمي للمحاكاة
        return "mock_jwt_token_for_apns"
    
    async def close(self):
        """إغلاق الاتصالات"""
        try:
            await self.http_client.aclose()
        except Exception as e:
            self.logger.error("Failed to close HTTP client", error=str(e))

# 🔧 مثيل خدمة الإشعارات العامة
push_service = PushService()

# 🚀 دوال مساعدة
async def send_push(device_id: str, message: str, title: str = "AI Teddy Bear") -> bool:
    """دالة بسيطة لإرسال إشعار محمول"""
    notification = {
        "title": title,
        "body": message
    }
    return await push_service.send_notification(device_id, notification)

async def send_push_with_data(device_id: str, title: str, message: str, data: Dict) -> bool:
    """إرسال إشعار مع بيانات إضافية"""
    notification = {
        "title": title,
        "body": message,
        "data": data
    }
    return await push_service.send_notification(device_id, notification)

if __name__ == "__main__":
    # اختبار الخدمة
    async def test_push():
        logger.info("📱 Testing Push Notification Service...")
        
        # اختبار إشعار بسيط
        success = await send_push(
            "test_device_123",
            "This is a test push notification from AI Teddy Bear!",
            "Test Notification"
        )
        logger.error(f"Simple push test: {'✅ Success' if success else '❌ Failed'}")
        
        # اختبار إشعار مع بيانات
        success = await send_push_with_data(
            "test_device_456",
            "Data Notification",
            "Check this notification with custom data",
            {"type": "test", "priority": "high"}
        )
        logger.error(f"Data push test: {'✅ Success' if success else '❌ Failed'}")
        
        # اختبار إرسال مجموعة
        notifications = [
            {
                "device_id": "device_1",
                "notification": {"title": "Batch 1", "body": "First notification"},
                "platform": "android"
            },
            {
                "device_id": "device_2",
                "notification": {"title": "Batch 2", "body": "Second notification"},
                "platform": "ios"
            }
        ]
        
        stats = await push_service.send_batch_notifications(notifications)
        logger.info(f"Batch push test: {stats['sent']}/{stats['total']} sent successfully")
        
        # إغلاق الخدمة
        await push_service.close()
    
    asyncio.run(test_push()) 