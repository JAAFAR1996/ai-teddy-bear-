# دليل نشر المشروع باستخدام Docker على VPS

## المتطلبات الأساسية
- Docker
- Docker Compose
- VPS أو خادم يدعم Docker
- اتصال بالإنترنت

## الخطوات التفصيلية للنشر

### 1. تحضير الخادم
```bash
# تحديث النظام
sudo apt update && sudo apt upgrade -y

# تثبيت Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# تثبيت Docker Compose
sudo apt install docker-compose -y

# إضافة المستخدم الحالي لمجموعة Docker
sudo usermod -aG docker $USER
```

### 2. استنساخ المشروع
```bash
# إنشاء مجلد للمشروع
mkdir -p ~/audio-assistant
cd ~/audio-assistant

# استنساخ المشروع
git clone https://github.com/your-repo/intelligent-audio-system.git
cd intelligent-audio-system
```

### 3. إعداد المتغيرات البيئية (اختياري)
إذا كنت تريد استخدام Azure Speech Services:
```bash
# إنشاء ملف .env
touch .env

# تحرير الملف وإضافة المفاتيح
nano .env

# محتوى الملف
AZURE_SPEECH_KEY=your_azure_cognitive_services_key
AZURE_SPEECH_REGION=your_azure_region
```

### 4. بناء وتشغيل المشروع
```bash
# بناء الصورة
docker-compose build

# تشغيل المشروع
docker-compose up -d
```

### 5. التحقق من التشغيل
```bash
# عرض الحاويات الجارية
docker ps

# عرض سجلات التشغيل
docker-compose logs app
```

## نصائح الأمان
- استخدم جدار حماية (Firewall)
- قم بتأمين المنافذ
- استخدم HTTPS
- حدّث المتغيرات البيئية بشكل آمن

## استكشاف الأخطاء
```bash
# في حالة وجود مشكلة
docker-compose logs app

# إعادة بناء الصورة
docker-compose down
docker-compose build
docker-compose up -d
```

## دعم اللغة العربية
- يدعم المشروع اللغة العربية في التحويل الصوتي
- يمكن تحديد اللغة في الكود أو عند الاستدعاء

## ملاحظات مهمة
- تأكد من وجود مساحة كافية على الخادم
- راقب استهلاك الموارد
- قم بعمل نسخ احتياطي بانتظام

## التكوين المتقدم
يمكنك تعديل `docker-compose.yml` لتخصيص:
- إعدادات الموارد
- متغيرات البيئة
- تخزين البيانات

## المساعدة
- راجع README.md
- تحقق من issues على GitHub
- تواصل مع فريق التطوير

---

**ملاحظة**: تأكد من استبدال `your-repo` و`your_azure_cognitive_services_key` بالقيم الفعلية.
