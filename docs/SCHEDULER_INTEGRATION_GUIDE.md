# ⏰ دليل نظام الجدولة - APScheduler Integration Guide

## 🎯 نظرة عامة
تم تنفيذ نظام جدولة متطور في `src/main.py` باستخدام **APScheduler** لتشغيل:
- **تنظيف البيانات اليومي** (منتصف الليل)
- **إشعارات التحذير** (11 مساءً يومياً)

---

## 🔧 التغييرات المنجزة

### 1. الاستيرادات الجديدة في `src/main.py`:
```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from src.application.services.data_cleanup_service import run_daily_cleanup, preview_cleanup
from src.application.services.notification_service import notify_upcoming_cleanup
```

### 2. إضافة متغير scheduler في `EnterpriseApplication`:
```python
self.scheduler: Optional[AsyncIOScheduler] = None
```

### 3. دالة إعداد المجدول الجديدة `_setup_scheduler()`:
```python
async def _setup_scheduler(self) -> None:
    # إنشاء APScheduler
    self.scheduler = AsyncIOScheduler(timezone='UTC')
    
    # مهمة تنظيف البيانات - منتصف الليل
    self.scheduler.add_job(
        self._run_data_cleanup,
        CronTrigger(hour=0, minute=0),
        id='daily_data_cleanup'
    )
    
    # مهمة الإشعارات - 11 مساءً
    self.scheduler.add_job(
        self._run_cleanup_notifications,
        CronTrigger(hour=23, minute=0),
        id='cleanup_notifications'
    )
```

### 4. دوال تشغيل المهام:
```python
async def _run_data_cleanup(self):
    """تشغيل تنظيف البيانات المجدول"""
    
async def _run_cleanup_notifications(self):
    """تشغيل إشعارات التنظيف المجدولة"""
```

---

## 🚀 كيفية التشغيل

### التشغيل العادي:
```bash
python src/main.py
```

### التشغيل مع النظام الإنتاجي:
```bash
python production_teddy_system.py
```

---

## 📊 مراقبة النظام

### 1. فحص حالة المجدول:
```http
GET /admin/scheduler/status
```
**الرد:**
```json
{
  "scheduler_running": true,
  "total_jobs": 2,
  "jobs": [
    {
      "id": "daily_data_cleanup",
      "name": "Daily Data Cleanup - تنظيف البيانات اليومي",
      "next_run_time": "2024-12-20T00:00:00+00:00",
      "trigger": "cron[hour='0', minute='0']"
    },
    {
      "id": "cleanup_notifications", 
      "name": "Cleanup Warning Notifications - إشعارات تحذير التنظيف",
      "next_run_time": "2024-12-19T23:00:00+00:00",
      "trigger": "cron[hour='23', minute='0']"
    }
  ]
}
```

### 2. تشغيل تنظيف البيانات يدوياً:
```http
POST /admin/scheduler/cleanup/trigger
```

### 3. تشغيل الإشعارات يدوياً:
```http
POST /admin/notifications/trigger
```

### 4. معاينة البيانات المرشحة للحذف:
```http
GET /admin/data/preview
```

---

## 🧪 اختبار النظام

### تشغيل اختبار شامل:
```bash
python test_scheduler_integration.py
```

أو استخدام الملف batch:
```bash
TEST_SCHEDULER.bat
```

### اختبار سريع للدوال:
```python
import asyncio
from src.application.services.data_cleanup_service import run_daily_cleanup
from src.application.services.notification_service import notify_upcoming_cleanup

# اختبار تنظيف البيانات
stats = await run_daily_cleanup()
print(stats)

# اختبار الإشعارات
stats = await notify_upcoming_cleanup()
print(stats)
```

---

## ⏰ جدول التشغيل الافتراضي

| المهمة | التوقيت | الوصف |
|--------|---------|-------|
| **تنظيف البيانات** | `00:00` (منتصف الليل) | حذف البيانات الأقدم من 30 يوم |
| **إشعارات التحذير** | `23:00` (11 مساءً) | تنبيه الأهل قبل الحذف بيومين |

### تخصيص التوقيت:
```python
# تغيير توقيت تنظيف البيانات إلى 2 صباحاً
CronTrigger(hour=2, minute=0)

# تشغيل الإشعارات مرتين يومياً (9 صباحاً و 6 مساءً)
CronTrigger(hour="9,18", minute=0)

# تشغيل أسبوعي (الأحد منتصف الليل)
CronTrigger(day_of_week='sun', hour=0, minute=0)
```

---

## 🔍 مراقبة الأخطاء

### سجلات النظام:
```bash
tail -f logs/teddy_system.log
```

### مؤشرات Prometheus:
- `teddy_application_errors_total{type="scheduled_cleanup"}`
- `teddy_application_errors_total{type="scheduled_notifications"}`

### تنبيهات في حالة الفشل:
```python
def job_listener(event):
    if event.exception:
        logger.error("Scheduled job failed", 
                   job_id=event.job_id,
                   exception=str(event.exception))
        # إرسال تنبيه للمطورين
        error_count.labels(type="scheduled_job").inc()
```

---

## 🛡️ الأمان والموثوقية

### 1. إعادة التشغيل التلقائي:
```python
job_defaults = {
    'coalesce': False,        # تجنب تراكم المهام
    'max_instances': 3,       # حد أقصى للتشغيل المتزامن
    'misfire_grace_time': 30  # هامش زمني للمهام المتأخرة
}
```

### 2. معالجة الأخطاء:
```python
async def _run_data_cleanup(self):
    try:
        stats = await run_daily_cleanup()
        logger.info("✅ Scheduled data cleanup completed")
    except Exception as e:
        logger.error("❌ Scheduled data cleanup failed", error=str(e))
        error_count.labels(type="scheduled_cleanup").inc()
```

### 3. الإيقاف الآمن:
```python
async def shutdown(self) -> None:
    if self.scheduler and self.scheduler.running:
        self.scheduler.shutdown(wait=True)  # انتظار إكمال المهام الجارية
```

---

## 🔧 استكشاف الأخطاء

### المشاكل الشائعة:

#### 1. خطأ `ModuleNotFoundError: No module named 'apscheduler'`
**الحل:**
```bash
pip install apscheduler==3.10.4
```

#### 2. خطأ `RuntimeError: This event loop is already running`
**الحل:**
```python
# تأكد من استخدام AsyncIOScheduler وليس BlockingScheduler
scheduler = AsyncIOScheduler(timezone='UTC')
```

#### 3. المهام لا تعمل
**التحقق:**
```python
# فحص حالة المجدول
print(f"Scheduler running: {scheduler.running}")
print(f"Jobs count: {len(scheduler.get_jobs())}")

# فحص المهام
for job in scheduler.get_jobs():
    print(f"Job: {job.id}, Next run: {job.next_run_time}")
```

#### 4. خطأ في قاعدة البيانات
**الحل:**
```bash
# تهيئة قاعدة البيانات
python scripts/initialize_db.py

# اختبار الاتصال
python -c "from database import db_manager; print('DB OK')"
```

---

## 📈 التحسينات المستقبلية

### 1. جدولة ديناميكية:
```python
# إضافة مهام بناءً على إعدادات المستخدم
scheduler.add_job(
    custom_task,
    CronTrigger.from_crontab(user_crontab_expression),
    id=f"user_{user_id}_task"
)
```

### 2. مجدول موزع:
```python
# استخدام Redis JobStore للبيئات المتعددة
from apscheduler.jobstores.redis import RedisJobStore

jobstores = {
    'default': RedisJobStore(host='localhost', port=6379, db=1)
}
```

### 3. تحليلات متقدمة:
```python
# تتبع أداء المهام
@scheduler.job_listener
def job_performance_tracker(event):
    if not event.exception:
        duration = (event.finished_at - event.started_at).total_seconds()
        job_duration_metric.labels(job_id=event.job_id).observe(duration)
```

---

## ✅ قائمة التحقق النهائية

- [x] ✅ APScheduler مثبت ومحدّث في requirements.txt
- [x] ✅ استيرادات جديدة في src/main.py
- [x] ✅ متغير scheduler في EnterpriseApplication
- [x] ✅ دالة _setup_scheduler() مكتملة
- [x] ✅ مهمة تنظيف البيانات (منتصف الليل)
- [x] ✅ مهمة الإشعارات (11 مساءً)
- [x] ✅ إيقاف آمن في shutdown()
- [x] ✅ endpoints للمراقبة محدّثة
- [x] ✅ اختبار شامل للنظام
- [x] ✅ معالجة الأخطاء والسجلات
- [x] ✅ مراقبة الأداء مع Prometheus

---

## 🎉 الخلاصة

تم تنفيذ **نظام جدولة متكامل وجاهز للإنتاج** يشمل:

1. **🧹 تنظيف تلقائي للبيانات** يومياً منتصف الليل
2. **📧 إشعارات تحذيرية** للأهل يومياً 11 مساءً  
3. **📊 مراقبة شاملة** عبر REST APIs
4. **🔧 تشغيل يدوي** للمهام عند الحاجة
5. **🛡️ معالجة أخطاء** متقدمة وسجلات مفصلة
6. **⏰ مرونة في الجدولة** مع CronTrigger

**النظام جاهز الآن للاستخدام في بيئة الإنتاج! 🚀** 