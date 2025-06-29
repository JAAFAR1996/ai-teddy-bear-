# 🚨 دليل نشر نظام المراقبة الطارئة

## AI Teddy Bear Emergency Monitoring System - Deployment Guide

---

## 📋 نظرة عامة

نظام المراقبة الطارئة هو نظام أمني متقدم مصمم للاستجابة الفورية للتهديدات الأمنية في مشروع AI Teddy Bear. يوفر النظام:

- **مراقبة مكثفة** كل 5 ثواني
- **تنبيهات فورية** للحوادث الحرجة  
- **استجابة تلقائية** للتهديدات
- **توثيق شامل** لجميع الأحداث

---

## ⚡ النشر السريع

### 1. النشر التلقائي (موصى به)

```bash
# الطريقة السريعة - نشر كامل في 5 دقائق
cd monitoring/emergency/scripts
chmod +x quick_deploy.sh
./quick_deploy.sh
```

### 2. النشر اليدوي

```bash
# نشر خطوة بخطوة للتحكم الكامل
cd monitoring/emergency/scripts  
chmod +x deploy_emergency_monitoring.sh
./deploy_emergency_monitoring.sh
```

---

## 🔧 المتطلبات الأساسية

### نظام التشغيل
- **Linux**: Ubuntu 20.04+ / CentOS 8+ / RHEL 8+
- **macOS**: 10.15+ مع Homebrew
- **Windows**: WSL2 أو Docker Desktop

### البرمجيات المطلوبة
```bash
# Docker & Docker Compose
docker --version          # >= 20.10.0
docker-compose --version  # >= 2.0.0

# أدوات إضافية
curl --version            # لاختبار APIs
openssl version           # لإنشاء الشهادات
```

### الموارد المطلوبة
- **المعالج**: 4 cores (8 cores موصى به)
- **الذاكرة**: 8GB RAM (16GB موصى به)
- **التخزين**: 50GB مساحة فارغة
- **الشبكة**: اتصال إنترنت مستقر

---

## 🏗️ هيكل المشروع

```
monitoring/emergency/
├── 📁 kubernetes/              # تكوينات Kubernetes
│   └── emergency-monitoring-configmap.yaml
├── 📁 scripts/                 # سكريبتات النشر
│   ├── quick_deploy.sh         # النشر السريع
│   └── deploy_emergency_monitoring.sh  # النشر الكامل
├── 📁 api/                     # API الاستجابة الطارئة
│   └── emergency_response.py
├── 📁 secrets/                 # الأسرار الآمنة (تُنشأ تلقائياً)
├── 📁 ssl/                     # الشهادات الأمنية (تُنشأ تلقائياً)
├── 📁 grafana/                 # تكوينات Grafana
├── 📁 prometheus/              # تكوينات Prometheus
├── 📁 alertmanager/           # تكوينات Alertmanager
├── docker-compose.emergency.yml # ملف Docker Compose
└── DEPLOYMENT_GUIDE.md        # هذا الملف
```

---

## 🚀 خطوات النشر التفصيلية

### الخطوة 1: التحضير

```bash
# التأكد من المتطلبات
./scripts/quick_deploy.sh --check-only

# إنشاء مجلدات البيانات
sudo mkdir -p /var/lib/teddy/monitoring/{prometheus,grafana}
sudo mkdir -p /var/log/teddy
```

### الخطوة 2: إعداد الأسرار

```bash
# إنشاء مجلد الأسرار
mkdir -p monitoring/emergency/secrets
chmod 700 monitoring/emergency/secrets

# إنشاء كلمات المرور (تلقائياً بواسطة السكريبت)
# أو يدوياً:
openssl rand -base64 32 > secrets/grafana-admin-password.txt
openssl rand -base64 64 > secrets/grafana-secret-key.txt
```

### الخطوة 3: النشر

```bash
# تشغيل النظام
docker-compose -f docker-compose.emergency.yml up -d

# التحقق من الحالة
docker-compose -f docker-compose.emergency.yml ps
```

### الخطوة 4: التحقق من التشغيل

```bash
# فحص صحة الخدمات
curl http://localhost:9090/-/healthy    # Prometheus
curl http://localhost:9093/-/healthy    # Alertmanager  
curl http://localhost:3000/api/health   # Grafana
```

---

## 🌐 الوصول للنظام

### URLs الوصول

| الخدمة | الرابط | الوصف |
|---------|---------|--------|
| **Prometheus** | http://localhost:9090 | مراقبة المقاييس |
| **Alertmanager** | http://localhost:9093 | إدارة التنبيهات |
| **Grafana** | http://localhost:3000 | لوحات القيادة |
| **Node Exporter** | http://localhost:9100 | مقاييس النظام |
| **cAdvisor** | http://localhost:8080 | مقاييس الحاويات |
| **Emergency API** | http://localhost:8080 | API الاستجابة |

### بيانات تسجيل الدخول

```bash
# Grafana
المستخدم: admin
كلمة المرور: (موجودة في secrets/grafana-admin-password.txt)

# عرض كلمة المرور
cat monitoring/emergency/secrets/grafana-admin-password.txt
```

---

## 🔧 إدارة النظام

### أوامر الإدارة الأساسية

```bash
# تشغيل النظام
docker-compose -f docker-compose.emergency.yml up -d

# إيقاف النظام
docker-compose -f docker-compose.emergency.yml stop

# إعادة تشغيل النظام
docker-compose -f docker-compose.emergency.yml restart

# عرض حالة الخدمات
docker-compose -f docker-compose.emergency.yml ps

# عرض السجلات
docker-compose -f docker-compose.emergency.yml logs -f

# عرض سجل خدمة معينة
docker-compose -f docker-compose.emergency.yml logs -f prometheus-emergency
```

### مراقبة الأداء

```bash
# استهلاك الموارد
docker stats

# مساحة القرص
df -h /var/lib/teddy/monitoring/

# السجلات
tail -f /var/log/teddy/emergency-deployment-*.log
```

---

## 🚨 التنبيهات المُعدة

### التنبيهات الحرجة (استجابة فورية)

1. **تسريب مفاتيح API**
   - الإجراء: تدوير تلقائي للمفاتيح
   - التنبيه: فوري عبر جميع القنوات

2. **هجوم DDoS**
   - الإجراء: تفعيل دفاعات WAF
   - التنبيه: فوري + تفعيل حماية السحابة

3. **تسريب بيانات الأطفال**
   - الإجراء: قفل فوري للبيانات
   - التنبيه: إشعار قانوني فوري

4. **اختراق النظام**
   - الإجراء: عزل فوري للنظام
   - التنبيه: إشعار جميع المسؤولين

### التنبيهات العامة

- استهلاك عالي للمعالج (>80%)
- استهلاك عالي للذاكرة (>85%)
- مساحة قرص منخفضة (<10%)
- بطء الاستجابة (>5 ثواني)

---

## 🔐 الأمان والحماية

### الشهادات الأمنية

```bash
# عرض الشهادات المثبتة
ls -la monitoring/emergency/ssl/certs/

# التحقق من صحة الشهادة
openssl x509 -in ssl/certs/prometheus.pem -text -noout
```

### إدارة الأسرار

```bash
# تغيير كلمة مرور Grafana
openssl rand -base64 32 > secrets/grafana-admin-password.txt
docker-compose restart grafana-emergency

# تدوير جميع الأسرار
./scripts/rotate_secrets.sh
```

### حماية الشبكة

- جميع الاتصالات مشفرة بـ TLS
- فصل الشبكات الداخلية والخارجية
- WAF متقدم لحماية APIs
- مراقبة مستمرة لمحاولات التسلل

---

## 📊 لوحات القيادة

### لوحات Grafana المتاحة

1. **Security Overview**
   - نظرة عامة على الأمان
   - التنبيهات النشطة
   - إحصائيات الهجمات

2. **System Health**
   - صحة النظام العامة
   - استهلاك الموارد
   - أداء الخدمات

3. **API Security**
   - مراقبة أمان APIs
   - محاولات الوصول غير المصرح
   - معدل الطلبات

4. **Network Security**
   - مراقبة الشبكة
   - الترافيك المشبوه
   - جدار الحماية

---

## 🛠️ استكشاف الأخطاء

### مشاكل شائعة وحلولها

#### 1. فشل في بدء الخدمات

```bash
# فحص السجلات
docker-compose logs prometheus-emergency

# فحص الموارد
docker system df
docker system prune -f  # تنظيف الموارد غير المستخدمة
```

#### 2. مشاكل في الأذونات

```bash
# إصلاح أذونات مجلدات البيانات
sudo chown -R 65534:65534 /var/lib/teddy/monitoring/prometheus
sudo chown -R 472:472 /var/lib/teddy/monitoring/grafana
```

#### 3. مشاكل في الشبكة

```bash
# فحص الشبكات
docker network ls
docker network inspect emergency-monitoring

# إعادة إنشاء الشبكات
docker-compose down
docker network prune -f
docker-compose up -d
```

#### 4. مشاكل في التنبيهات

```bash
# فحص تكوين Alertmanager
docker exec -it teddy-alertmanager-emergency amtool config show

# اختبار قواعد التنبيه
docker exec -it teddy-prometheus-emergency promtool check rules /etc/prometheus/rules/*.yml
```

---

## 🔄 النسخ الاحتياطي والاستعادة

### إنشاء نسخة احتياطية

```bash
# نسخ احتياطي شامل
./scripts/backup_monitoring.sh

# نسخ احتياطي يدوي
sudo tar -czf backup-$(date +%Y%m%d).tar.gz \
  /var/lib/teddy/monitoring/ \
  monitoring/emergency/secrets/ \
  monitoring/emergency/ssl/
```

### استعادة النسخة الاحتياطية

```bash
# إيقاف النظام
docker-compose -f docker-compose.emergency.yml down

# استعادة البيانات
sudo tar -xzf backup-20241231.tar.gz -C /

# إعادة تشغيل النظام
docker-compose -f docker-compose.emergency.yml up -d
```

---

## 📈 التحسين والضبط

### تحسين الأداء

```bash
# زيادة مدة الاحتفاظ ببيانات Prometheus
# في docker-compose.emergency.yml:
# --storage.tsdb.retention.time=60d

# تحسين إعدادات Grafana
# في متغيرات البيئة:
# GF_DATABASE_MAX_OPEN_CONN=300
# GF_DATABASE_MAX_IDLE_CONN=300
```

### ضبط التنبيهات

```bash
# تعديل قواعد التنبيه
vim monitoring/emergency/prometheus/rules/security_alerts.yml

# إعادة تحميل التكوين
docker exec -it teddy-prometheus-emergency \
  curl -X POST http://localhost:9090/-/reload
```

---

## 📞 الدعم والمساعدة

### في حالة الطوارئ

1. **التحقق من حالة النظام**
   ```bash
   ./scripts/system_status.sh
   ```

2. **إعادة تشغيل سريع**
   ```bash
   docker-compose restart
   ```

3. **الاتصال بفريق الدعم**
   - Email: security@teddybear.ai
   - هاتف طوارئ: [رقم الطوارئ]

### المراجع والوثائق

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [Alertmanager Guide](https://prometheus.io/docs/alerting/latest/alertmanager/)

---

## 📝 ملاحظات مهمة

⚠️  **تحذيرات أمنية:**
- احتفظ بكلمات المرور في مكان آمن
- قم بتحديث الشهادات دورياً (كل سنة)
- راجع السجلات الأمنية يومياً
- اختبر إجراءات الطوارئ شهرياً

💡 **نصائح للأداء الأمثل:**
- راقب استهلاك الموارد دورياً
- قم بتنظيف البيانات القديمة
- حدث صور Docker شهرياً
- اختبر النسخ الاحتياطية دورياً

---

*آخر تحديث: ديسمبر 2024*  
*فريق الأمان - AI Teddy Bear Project* 