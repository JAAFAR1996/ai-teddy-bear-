# 🛎️ Notification Service Guide - دليل خدمة الإشعارات

## 📋 نظرة عامة

خدمة الإشعارات الشاملة لمشروع AI Teddy Bear تقوم بإرسال تنبيهات للوالدين قبل حذف بيانات أطفالهم بـ 48 ساعة. تدعم الخدمة قنوات متعددة للإشعارات مع قوالب HTML جميلة ومخصصة.

## 🚀 الميزات الرئيسية

### 📧 البريد الإلكتروني
- **قوالب HTML جميلة**: تصميم متجاوب مع ألوان جذابة
- **محتوى مخصص**: يتضمن اسم الطفل وتفاصيل البيانات
- **روابط مباشرة**: للوصول لتصدير البيانات
- **دعم المرفقات**: إمكانية إرفاق ملفات إضافية

### 📱 الإشعارات المحمولة
- **دعم متعدد المنصات**: Android (FCM) و iOS (APNs)
- **إشعارات فورية**: تسليم سريع مع أولوية عالية
- **بيانات مخصصة**: معلومات إضافية مع الإشعار
- **اكتشاف تلقائي**: للمنصة بناءً على معرف الجهاز

### 📲 الرسائل النصية (SMS)
- **دعم Twilio**: إرسال رسائل نصية دولية
- **رسائل مخصصة**: نص قصير ومفهوم
- **تتبع التسليم**: حالة إرسال الرسائل

### 🔔 الإشعارات داخل التطبيق
- **تخزين محلي**: في قاعدة البيانات للعرض المباشر
- **مهلة انتهاء**: للإشعارات المؤقتة
- **أولوية وتصنيف**: حسب نوع الإشعار

## 📁 هيكل الملفات

```
src/application/services/
├── notification_service.py      # الخدمة الرئيسية
├── email_service.py            # خدمة البريد الإلكتروني
├── push_service.py             # خدمة الإشعارات المحمولة
├── sms_service.py              # خدمة الرسائل النصية
└── scheduler_service.py        # تحديث: مهمة الإشعارات

test_notification_service.py     # ملف الاختبار الشامل
RUN_NOTIFICATION_TEST.bat       # ملف تشغيل الاختبار
notification_test_results.json   # نتائج الاختبار
```

## ⚙️ التكوين والإعداد

### 1. إعدادات البريد الإلكتروني

في `config/config.json`:

```json
{
  "EMAIL_CONFIG": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "from_email": "noreply@aiteddybear.com",
    "password": "your_app_password",
    "use_tls": true,
    "timeout": 30
  }
}
```

### 2. إعدادات الإشعارات المحمولة

```json
{
  "PUSH_CONFIG": {
    "fcm_server_key": "your_fcm_server_key",
    "fcm_sender_id": "your_sender_id",
    "apns_key_id": "your_apns_key_id",
    "apns_team_id": "your_team_id",
    "apns_bundle_id": "com.aiteddybear.app",
    "timeout": 30,
    "max_retries": 3
  }
}
```

### 3. إعدادات الرسائل النصية

```json
{
  "SMS_CONFIG": {
    "twilio_account_sid": "your_twilio_sid",
    "twilio_auth_token": "your_twilio_token",
    "from_number": "+1234567890"
  }
}
```

### 4. إعدادات الإشعارات العامة

```json
{
  "NOTIFICATION_CONFIG": {
    "default_language": "ar",
    "retry_attempts": 3,
    "retry_delay_seconds": 30,
    "batch_size": 100,
    "rate_limit_per_minute": 60,
    "enable_email": true,
    "enable_push": true,
    "enable_sms": false,
    "enable_in_app": true
  }
}
```

## 🔧 الاستخدام والتشغيل

### 1. تشغيل الخدمة تلقائياً

الخدمة تعمل تلقائياً مع جدولة يومية في 11 مساءً UTC:

```python
# في scheduler_service.py
scheduler.add_job(
    func=notify_upcoming_cleanup,
    trigger=CronTrigger(hour=23, minute=0),
    id="notification_cleanup_warning"
)
```

### 2. تشغيل يدوي عبر API

```bash
# تشغيل الإشعارات فوراً
curl -X POST http://localhost:8000/admin/notifications/trigger
```

### 3. استخدام برمجي

```python
from src.application.services.notification_service import notify_upcoming_cleanup

# تشغيل الإشعارات
stats = await notify_upcoming_cleanup()
print(f"أرسلت إشعارات لـ {stats.children_notified} طفل")
```

## 🧪 تشغيل الاختبارات

### تشغيل سريع

```bash
# Windows
RUN_NOTIFICATION_TEST.bat

# Linux/Mac
python test_notification_service.py
```

### مراحل الاختبار

1. **📦 Phase 1**: اختبار الاستيراد الأساسي
2. **🔧 Phase 2**: اختبار تهيئة الخدمات  
3. **🛎️ Phase 3**: اختبار الوظائف الأساسية
4. **🔗 Phase 4**: اختبار التكامل
5. **🛡️ Phase 5**: اختبار معالجة الأخطاء

### نتائج الاختبار

```
🏆 FINAL TEST REPORT
============================================================
📊 Total Tests: 10
✅ Passed: 10
❌ Failed: 0
📈 Success Rate: 100.0%
⏱️  Total Time: 2.45s
```

## 📊 API Endpoints

### GET `/admin/scheduler/status`
عرض حالة جميع المهام المجدولة

```json
{
  "scheduler_running": true,
  "total_jobs": 5,
  "jobs": [
    {
      "id": "notification_cleanup_warning",
      "name": "Cleanup Warning Notifications",
      "next_run_time": "2025-06-28T23:00:00",
      "trigger": "cron[hour=23,minute=0]"
    }
  ]
}
```

### POST `/admin/notifications/trigger`
تشغيل الإشعارات يدوياً

```json
{
  "message": "Cleanup notifications triggered successfully",
  "stats": {
    "children_notified": 5,
    "emails_sent": 5,
    "push_sent": 4,
    "sms_sent": 0,
    "in_app_sent": 5,
    "errors_count": 0,
    "execution_time_seconds": 1.23
  }
}
```

## 🎨 قوالب الإشعارات

### قالب البريد الإلكتروني

```html
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <title>تنبيه AI Teddy Bear</title>
    <style>
        body { font-family: 'Arial', sans-serif; background-color: #f0f8ff; }
        .container { max-width: 600px; margin: 0 auto; background: white; 
                    border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                 color: white; padding: 30px; text-align: center; }
        .teddy-icon { font-size: 48px; margin-bottom: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="teddy-icon">🧸</div>
            <h1>AI Teddy Bear</h1>
            <h2>تنبيه مهم حول بيانات طفلك</h2>
        </div>
        <!-- محتوى الرسالة -->
    </div>
</body>
</html>
```

### قالب الإشعار المحمول

```json
{
  "title": "🧸 تنبيه AI Teddy Bear",
  "body": "بيانات {{ child_name }} ستحذف خلال {{ days_until_deletion }} أيام",
  "data": {
    "type": "data_cleanup_warning",
    "child_udid": "12345",
    "action_url": "/data-export"
  }
}
```

### قالب الرسالة النصية

```
🧸 تنبيه AI Teddy: بيانات {{ child_name }} ستحذف خلال {{ days_until_deletion }} أيام. 
صدّر البيانات من التطبيق للاحتفاظ بها.
```

## 🔒 الأمان والخصوصية

### تشفير الاتصالات
- **TLS/SSL**: جميع الاتصالات مشفرة
- **API Keys**: حماية مفاتيح الخدمات الخارجية
- **Rate Limiting**: حد أقصى 60 إشعار/دقيقة

### حماية البيانات
- **تجزئة البيانات**: عدم تسرب معلومات حساسة
- **سجلات مجهولة**: عدم تسجيل بيانات شخصية
- **انتهاء الصلاحية**: حذف الإشعارات المؤقتة

### GDPR و COPPA
- **حذف تلقائي**: للبيانات القديمة
- **موافقة الوالدين**: قبل معالجة بيانات الأطفال
- **حق الوصول**: للبيانات المخزنة

## 🐛 استكشاف الأخطاء

### مشاكل شائعة

#### 1. فشل إرسال البريد الإلكتروني
```
❌ SMTP authentication failed
```

**الحل:**
- تأكد من صحة بيانات SMTP
- فعّل "App Passwords" لـ Gmail
- تحقق من إعدادات الحماية

#### 2. فشل الإشعارات المحمولة
```
❌ FCM/APNs connection timeout
```

**الحل:**
- تحقق من مفاتيح FCM/APNs
- تأكد من صحة Bundle ID
- فحص اتصال الإنترنت

#### 3. مشكلة في قاعدة البيانات
```
❌ Database connection error
```

**الحل:**
- تأكد من تشغيل قاعدة البيانات
- فحص إعدادات الاتصال
- تحقق من الصلاحيات

### تفعيل الـ Debug Mode

```python
# في notification_service.py
logger.setLevel(logging.DEBUG)

# أو في config.json
{
  "LOG_LEVEL": "DEBUG",
  "NOTIFICATION_CONFIG": {
    "debug_mode": true
  }
}
```

## 📈 المراقبة والمتابعة

### إحصائيات الأداء

```python
from src.application.services.notification_service import notification_service

# الحصول على إحصائيات
stats = await notification_service.notify_upcoming_cleanup()
print(f"""
📊 Notification Performance:
   - Children notified: {stats.children_notified}
   - Success rate: {(stats.emails_sent / stats.children_notified * 100):.1f}%
   - Avg. execution time: {stats.execution_time_seconds:.2f}s
""")
```

### سجلات النظام

```bash
# عرض سجلات الإشعارات
tail -f logs/notification_service.log

# البحث عن أخطاء
grep "ERROR" logs/notification_service.log
```

### Metrics مع Prometheus

```python
# في notification_service.py
from prometheus_client import Counter, Histogram

notification_counter = Counter('notifications_sent_total', 'Total notifications sent', ['channel'])
notification_duration = Histogram('notification_duration_seconds', 'Notification processing time')
```

## 🔄 التحديثات والصيانة

### تحديث القوالب

1. عدّل القوالب في `notification_service.py`
2. اختبر التغييرات محلياً
3. نشر في بيئة الإنتاج

### إضافة قنوات جديدة

```python
# مثال: إضافة Slack
class SlackService:
    async def send_message(self, channel: str, message: str):
        # تنفيذ إرسال رسالة Slack
        pass

# في NotificationService
async def _send_slack_notification(self, notification: NotificationData):
    # تنفيذ إرسال إشعار Slack
    pass
```

### النسخ الاحتياطي

```bash
# نسخ احتياطي من الإعدادات
cp config/config.json config/config_backup_$(date +%Y%m%d).json

# نسخ احتياطي من السجلات
tar -czf logs_backup_$(date +%Y%m%d).tar.gz logs/
```

## 📞 الدعم والمساعدة

### الاتصال
- 📧 البريد الإلكتروني: support@aiteddybear.com
- 🌐 الموقع: https://aiteddybear.com/support
- 📱 التطبيق: قسم "المساعدة"

### الموارد
- 📚 [التوثيق الفني](docs/api/)
- 🎥 [فيديوهات تعليمية](https://youtube.com/aiteddybear)
- 💬 [منتدى المطورين](https://forum.aiteddybear.com)

---

## 📝 ملاحظات الإصدار

### v2.3.0 - إطلاق خدمة الإشعارات
- ✅ إضافة خدمة إشعارات شاملة
- ✅ دعم قنوات متعددة (Email, Push, SMS, In-App)
- ✅ قوالب HTML جميلة ومخصصة
- ✅ تكامل مع نظام الجدولة
- ✅ اختبارات شاملة
- ✅ API endpoints للإدارة
- ✅ مراقبة والتسجيل المتقدم

### التحديثات القادمة
- 🔄 دعم اللغات المتعددة
- 🔄 تخصيص قوالب متقدم
- 🔄 تحليلات متفصلة
- 🔄 دعم Webhook
- 🔄 إشعارات الوقت الفعلي

---

> 🧸 **AI Teddy Bear Project** - Making childhood memories safer and smarter with enterprise-grade technology and comprehensive privacy protection.

**تاريخ آخر تحديث:** 2025-06-27  
**رقم الإصدار:** v2.3.0  
**حالة الوثيقة:** مكتملة ✅ 