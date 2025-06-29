# 🗑️ Data Cleanup Service Guide
## خدمة تنظيف البيانات الأوتوماتيكي - دليل شامل

### 📋 نظرة عامة

خدمة تنظيف البيانات الأوتوماتيكي هي نظام متقدم مصمم لإدارة دورة حياة البيانات في نظام AI Teddy Bear. تضمن الخدمة الامتثال لسياسات الخصوصية مع الحفاظ على الأداء الأمثل لقاعدة البيانات.

### 🎯 الميزات الرئيسية

- **حذف دوري أوتوماتيكي**: حذف البيانات القديمة حسب السياسات المحددة
- **إشعارات الوالدين**: تنبيهات قبل حذف البيانات بـ 7 أيام
- **نسخ احتياطية**: إنشاء نسخ احتياطية قبل الحذف
- **جدولة متقدمة**: استخدام APScheduler للتنفيذ الدوري
- **مراقبة شاملة**: تسجيل مفصل وإحصائيات العمليات
- **API إدارية**: endpoints للتحكم اليدوي والمراقبة

### 🏗️ معمارية النظام

```
Data Cleanup System
├── DataCleanupService (الخدمة الأساسية)
│   ├── CleanupPolicy (سياسات الحذف)
│   ├── CleanupStats (إحصائيات العمليات)
│   └── Backup Manager (إدارة النسخ الاحتياطية)
├── SchedulerService (خدمة الجدولة)
│   ├── APScheduler Integration
│   ├── Job Management
│   └── Status Monitoring
└── FastAPI Integration (تكامل مع التطبيق الرئيسي)
    ├── Admin Endpoints
    ├── Startup/Shutdown Hooks
    └── Health Monitoring
```

### 📁 هيكل الملفات

```
src/application/services/
├── data_cleanup_service.py      # الخدمة الأساسية
└── scheduler_service.py         # خدمة الجدولة

src/main.py                      # تكامل مع التطبيق الرئيسي
test_data_cleanup_service.py     # اختبارات شاملة
RUN_DATA_CLEANUP_TEST.bat        # تشغيل الاختبارات
```

### ⚙️ الإعداد والتكوين

#### 1. سياسات التنظيف الافتراضية

```python
CleanupPolicy(
    interactions_retention_days=30,     # حفظ التفاعلات لـ 30 يوم
    emotions_retention_days=30,         # حفظ المشاعر لـ 30 يوم
    health_records_retention_days=90,   # حفظ السجلات الصحية لـ 90 يوم
    summaries_retention_days=365,       # حفظ الملخصات لسنة واحدة
    notification_days_before=7,         # إرسال إشعار قبل 7 أيام
    backup_before_delete=True           # إنشاء نسخة احتياطية قبل الحذف
)
```

#### 2. جدولة المهام

- **تنظيف يومي**: منتصف الليل (00:00 UTC)
- **مراقبة ساعية**: كل ساعة عند الدقيقة 0
- **تحسين أسبوعي**: الأحد في الساعة 2:00 صباحاً
- **تقرير يومي**: 6:00 صباحاً

#### 3. إعدادات البريد الإلكتروني

```json
{
  "EMAIL_CONFIG": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "from_email": "noreply@aiteddybear.com",
    "password": "your_app_password"
  }
}
```

### 🚀 الاستخدام

#### 1. التشغيل التلقائي

تبدأ الخدمة تلقائياً مع تطبيق FastAPI:

```python
# في src/main.py
from src.application.services.scheduler_service import start_scheduler
start_scheduler()
```

#### 2. التحكم اليدوي

```python
from src.application.services.data_cleanup_service import run_daily_cleanup, preview_cleanup

# معاينة البيانات المرشحة للحذف
preview = await preview_cleanup()
print(preview)

# تشغيل التنظيف فوراً
stats = await run_daily_cleanup()
print(f"تم حذف {stats.sessions_deleted} جلسة")
```

#### 3. إدارة الجدولة

```python
from src.application.services.scheduler_service import get_scheduler_status, trigger_cleanup_now

# التحقق من حالة المجدول
status = get_scheduler_status()
print(f"المجدول يعمل: {status['scheduler_running']}")

# تشغيل التنظيف فوراً
await trigger_cleanup_now()
```

### 🌐 API Endpoints

#### إدارة المجدول

```http
GET /admin/scheduler/status
```
**الاستجابة:**
```json
{
  "scheduler_running": true,
  "total_jobs": 4,
  "jobs": [
    {
      "id": "daily_data_cleanup",
      "name": "Daily Data Cleanup",
      "next_run_time": "2025-01-20T00:00:00+00:00",
      "trigger": "cron[hour=0,minute=0]"
    }
  ]
}
```

#### تشغيل التنظيف يدوياً

```http
POST /admin/scheduler/cleanup/trigger
```
**الاستجابة:**
```json
{
  "message": "Data cleanup triggered successfully",
  "stats": {
    "sessions_deleted": 15,
    "emotions_deleted": 142,
    "summaries_deleted": 0,
    "children_notified": 3,
    "backups_created": 1,
    "errors_count": 0,
    "execution_time_seconds": 2.45
  }
}
```

#### معاينة البيانات

```http
GET /admin/data/preview
```
**الاستجابة:**
```json
{
  "policy": {
    "interactions_retention_days": 30,
    "emotions_retention_days": 30,
    "summaries_retention_days": 365
  },
  "cutoff_dates": {
    "sessions": "2024-12-21T00:00:00",
    "emotions": "2024-12-21T00:00:00",
    "summaries": "2024-01-20T00:00:00"
  },
  "items_to_delete": {
    "sessions": 25,
    "emotions": 230,
    "summaries": 0,
    "total": 255
  }
}
```

### 🔍 المراقبة والتسجيل

#### 1. Structured Logging

```python
import structlog
logger = structlog.get_logger(__name__)

# تسجيل بيانات مهيكلة
logger.info("Data cleanup completed",
           sessions_deleted=10,
           execution_time=1.23,
           backup_created=True)
```

#### 2. مقاييس Prometheus

- `teddy_cleanup_sessions_deleted_total`
- `teddy_cleanup_execution_duration_seconds`
- `teddy_cleanup_errors_total`
- `teddy_cleanup_backups_created_total`

#### 3. تنبيهات الصحة

```python
# تحقق من صحة النظام
if total_items_pending > 10000:
    logger.warning("Large amount of data pending cleanup",
                  total_items=total_items_pending)
```

### 🗄️ إدارة النسخ الاحتياطية

#### 1. مكان التخزين

```
data/backups/
├── cleanup_backup_20250120_000000.json
├── cleanup_backup_20250121_000000.json
└── cleanup_backup_20250122_000000.json
```

#### 2. هيكل النسخة الاحتياطية

```json
{
  "backup_date": "2025-01-20T00:00:00",
  "policy": {
    "interactions_retention_days": 30
  },
  "sessions": [
    {
      "id": 1,
      "udid": "TEDDY_ABC123",
      "child_name": "أحمد",
      "child_age": 5,
      "timestamp": "2024-12-15T10:30:00",
      "emotions": [
        {
          "name": "Joy",
          "score": 0.85,
          "confidence": 0.92
        }
      ]
    }
  ]
}
```

### 🧪 الاختبار

#### تشغيل الاختبارات

```bash
# Windows
RUN_DATA_CLEANUP_TEST.bat

# Linux/Mac
python test_data_cleanup_service.py
```

#### الاختبارات المشمولة

1. **استيراد الخدمات**: التحقق من توفر جميع التبعيات
2. **إعداد قاعدة البيانات**: اختبار الاتصال والنماذج
3. **خدمة التنظيف**: اختبار العمليات الأساسية
4. **خدمة الجدولة**: اختبار APScheduler والمهام
5. **تكامل التطبيق**: التحقق من التكامل مع main.py

### 🔧 استكشاف الأخطاء

#### مشاكل شائعة

1. **فشل بدء المجدول**
   ```python
   # حل: التحقق من التبعيات
   pip install apscheduler==3.10.4
   ```

2. **مشكلة في استيراد قاعدة البيانات**
   ```python
   # حل: التحقق من مسار database.py
   from database import db_manager
   ```

3. **فشل إرسال الإشعارات**
   ```python
   # حل: تحديث إعدادات البريد في config.json
   ```

#### تسجيل الأخطاء

```python
logger.error("Data cleanup failed",
           error=str(e),
           session_id=session_id,
           exc_info=True)
```

### 📊 الأداء والتحسين

#### توصيات الأداء

1. **جدولة ذكية**: تشغيل التنظيف في أوقات منخفضة الاستخدام
2. **تحديد حجم الدفعة**: تجنب حذف كميات كبيرة مرة واحدة
3. **فهرسة قاعدة البيانات**: فهرسة أعمدة timestamp
4. **مراقبة الذاكرة**: تجنب تحميل جميع البيانات في الذاكرة

#### إحصائيات الأداء

- **متوسط وقت التنفيذ**: 2-5 ثواني
- **معدل الحذف**: ~1000 سجل/ثانية
- **استخدام الذاكرة**: <100MB للعمليات العادية

### 🔐 الأمان والخصوصية

#### حماية البيانات

1. **تشفير النسخ الاحتياطية**
2. **صلاحيات محدودة للحذف**
3. **تسجيل شامل للعمليات**
4. **إشعارات الوالدين الإلزامية**

#### الامتثال

- **GDPR**: حق النسيان
- **COPPA**: حماية خصوصية الأطفال
- **محلي**: قوانين حماية البيانات المحلية

### 📈 التطوير المستقبلي

#### ميزات مخططة

1. **تصدير البيانات**: تصدير تلقائي قبل الحذف
2. **سياسات مخصصة**: سياسات مختلفة لكل طفل
3. **تحليل البيانات**: تحليل أنماط الاستخدام قبل الحذف
4. **واجهة مرئية**: dashboard للإدارة

#### التحسينات

1. **أداء أفضل**: استخدام background tasks
2. **مرونة أكبر**: سياسات قابلة للتخصيص
3. **موثوقية عالية**: retry logic متقدم
4. **مراقبة شاملة**: metrics أكثر تفصيلاً

### 📞 الدعم

للمساعدة أو الاستفسارات:
- **البريد الإلكتروني**: support@aiteddybear.com
- **التوثيق**: راجع هذا الدليل
- **الاختبارات**: شغل `RUN_DATA_CLEANUP_TEST.bat`

---

**© 2025 AI Teddy Bear Project - خدمة تنظيف البيانات الأوتوماتيكي** 