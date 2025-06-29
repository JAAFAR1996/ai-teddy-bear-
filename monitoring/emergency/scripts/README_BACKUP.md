# 💾 نظام النسخ الاحتياطي الكامل - AI Teddy Bear

## Emergency Backup System v2025.1.0 - DevOps Team

**نظام نسخ احتياطي متقدم مع تشفير AES-256 وحفظ سحابي آمن على AWS S3**

---

## 🎯 نظرة عامة

تم تطوير نظام النسخ الاحتياطي الكامل كجزء من استراتيجية الأمان الشاملة لمشروع AI Teddy Bear. النظام يوفر:

✅ **نسخ احتياطي كامل مشفر** لجميع مكونات النظام  
✅ **حفظ سحابي آمن** على AWS S3 مع Glacier storage  
✅ **جدولة تلقائية** للنسخ الاحتياطية المتعددة  
✅ **استعادة سريعة** مع التحقق من السلامة  
✅ **مراقبة وتقارير** شاملة لحالة النسخ  

---

## 📋 السكريبتات المتوفرة

| السكريبت | الوصف | التشغيل | التكرار |
|-----------|--------|---------|----------|
| **full_backup.sh** | نسخة احتياطية كاملة | يدوي/مجدول | يومياً 2:00 ص |
| **restore_backup.sh** | استعادة النسخ الاحتياطية | يدوي | عند الحاجة |
| **backup_scheduler.sh** | جدولة النسخ التلقائية | يدوي | مرة واحدة |
| **config_backup.sh** | نسخ التكوينات فقط | تلقائي | كل 6 ساعات |
| **archive_backup.sh** | نسخة أرشيفية | تلقائي | أسبوعياً |
| **cleanup_old_backups.sh** | تنظيف النسخ القديمة | تلقائي | شهرياً |
| **verify_backups.sh** | فحص سلامة النسخ | تلقائي | أسبوعياً |

---

## ⚡ البدء السريع

### 1. إعداد متغيرات البيئة

```bash
# إعداد مفاتيح AWS (مطلوب)
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"

# إعداد النسخ الاحتياطية
export BACKUP_S3_BUCKET="ai-teddy-emergency-backups"
export BACKUP_ENCRYPTION_KEY="$(openssl rand -base64 32)"

# حفظ متغيرات البيئة
echo "export BACKUP_ENCRYPTION_KEY=\"${BACKUP_ENCRYPTION_KEY}\"" >> ~/.bashrc
```

### 2. تشغيل نسخة احتياطية فورية

```bash
cd monitoring/emergency/scripts

# نسخة احتياطية كاملة
./full_backup.sh

# نسخة احتياطية للتكوينات فقط (سريعة)
./config_backup.sh
```

### 3. تثبيت الجدولة التلقائية

```bash
# تثبيت الجدولة (يحتاج صلاحيات root)
sudo ./backup_scheduler.sh install

# عرض حالة الجدولة
./backup_scheduler.sh status
```

---

## 🔐 نظام التشفير المتقدم

### طبقات الحماية المتعددة:

1. **AES-256-CBC** - تشفير قوي للملفات
2. **PBKDF2** - تقوية المفاتيح (100,000 تكرار)
3. **AWS KMS** - إدارة مفاتيح السحابة
4. **SHA-256** - التحقق من سلامة البيانات
5. **TLS 1.3** - تشفير النقل

### مثال على عملية التشفير:
```bash
# ضغط البيانات
tar -czf backup.tar.gz /data

# تشفير بـ AES-256
openssl enc -aes-256-cbc -salt -pbkdf2 -iter 100000 \
  -in backup.tar.gz -out backup.tar.gz.enc -k "$ENCRYPTION_KEY"

# حساب checksum
sha256sum backup.tar.gz.enc > backup.tar.gz.enc.sha256

# رفع مع تشفير KMS إضافي
aws s3 cp backup.tar.gz.enc s3://bucket/ \
  --sse aws:kms --sse-kms-key-id alias/teddy-backup-key
```

---

## ☁️ تكوين AWS S3

### إعداد S3 Bucket

```bash
# إنشاء bucket للنسخ الاحتياطية
aws s3 mb s3://ai-teddy-emergency-backups

# تفعيل versioning
aws s3api put-bucket-versioning \
  --bucket ai-teddy-emergency-backups \
  --versioning-configuration Status=Enabled

# تطبيق lifecycle policy
aws s3api put-bucket-lifecycle-configuration \
  --bucket ai-teddy-emergency-backups \
  --lifecycle-configuration file://lifecycle.json
```

### Lifecycle Policy Example (lifecycle.json):
```json
{
  "Rules": [
    {
      "ID": "TeddyBackupLifecycle",
      "Status": "Enabled",
      "Filter": {"Prefix": "emergency-monitoring/"},
      "Transitions": [
        {
          "Days": 30,
          "StorageClass": "STANDARD_IA"
        },
        {
          "Days": 90,
          "StorageClass": "GLACIER"
        },
        {
          "Days": 2555,
          "StorageClass": "DEEP_ARCHIVE"
        }
      ],
      "Expiration": {
        "Days": 2555
      }
    }
  ]
}
```

---

## 🔄 استعادة النسخ الاحتياطية

### استعادة بسيطة

```bash
# عرض النسخ المتوفرة
./restore_backup.sh --list

# استعادة نسخة محددة
./restore_backup.sh 20241231_120000

# استعادة آخر نسخة
./restore_backup.sh latest
```

### استعادة متقدمة

```bash
# مع تحديد مفتاح التشفير
BACKUP_ENCRYPTION_KEY="your-key" ./restore_backup.sh 20241231_120000

# استعادة إلى موقع مختلف
RESTORE_PATH="/tmp/restore" ./restore_backup.sh 20241231_120000

# استعادة مع فحص شامل
./restore_backup.sh 20241231_120000 --verify-integrity
```

---

## ⏰ نظام الجدولة التلقائية

### الجدولة الافتراضية:

| النوع | التوقيت | التكرار | الحفظ |
|-------|---------|----------|-------|
| **كاملة** | 2:00 ص | يومياً | 30 يوم |
| **تكوينات** | كل 6 ساعات | يومياً | 7 أيام |
| **أرشيفية** | 1:00 ص الأحد | أسبوعياً | 7 سنوات |
| **تنظيف** | 3:00 ص اليوم 1 | شهرياً | - |
| **فحص** | 4:00 ص الإثنين | أسبوعياً | - |

### إدارة الجدولة:

```bash
# تثبيت الجدولة
sudo ./backup_scheduler.sh install

# عرض الحالة
./backup_scheduler.sh status

# تشغيل نسخة فورية
./backup_scheduler.sh run-now

# إلغاء الجدولة
sudo ./backup_scheduler.sh uninstall
```

---

## 📊 مراقبة النسخ الاحتياطية

### السجلات والتقارير:

```bash
# عرض سجلات النسخ الاحتياطية
tail -f /var/log/teddy/backup-*.log

# عرض تقرير آخر نسخة
cat /tmp/backup_report_*.json | jq .

# فحص سلامة النسخ
./verify_backups.sh

# إحصائيات S3
aws s3 ls s3://ai-teddy-emergency-backups/ --recursive --human-readable
```

### تكامل مع CloudWatch:

```bash
# إرسال metrics لـ CloudWatch
aws cloudwatch put-metric-data \
  --namespace "TeddyBear/Backup" \
  --metric-data MetricName=BackupSize,Value=$(du -s /backup),Unit=Bytes

# إنشاء alarm
aws cloudwatch put-metric-alarm \
  --alarm-name "TeddyBackupFailure" \
  --alarm-description "Backup failure detected" \
  --metric-name BackupStatus \
  --namespace TeddyBear/Backup \
  --statistic Maximum \
  --period 86400 \
  --threshold 1 \
  --comparison-operator GreaterThanThreshold
```

---

## 🛠️ استكشاف الأخطاء

### مشاكل شائعة وحلولها:

#### 1. فشل في التشفير
```bash
# التحقق من مفتاح التشفير
echo $BACKUP_ENCRYPTION_KEY

# إعادة إنشاء المفتاح
export BACKUP_ENCRYPTION_KEY="$(openssl rand -base64 32)"

# اختبار التشفير
echo "test" | openssl enc -aes-256-cbc -salt -k "$BACKUP_ENCRYPTION_KEY" | \
  openssl enc -aes-256-cbc -d -k "$BACKUP_ENCRYPTION_KEY"
```

#### 2. مشاكل AWS credentials
```bash
# فحص الهوية
aws sts get-caller-identity

# اختبار الوصول لـ S3
aws s3 ls s3://ai-teddy-emergency-backups/

# إعادة تكوين AWS
aws configure reconfigure
```

#### 3. مساحة قرص ممتلئة
```bash
# فحص المساحة
df -h /tmp

# تنظيف الملفات المؤقتة
rm -f /tmp/teddy_emergency_backup_*
rm -f /tmp/backup_test_*

# تشغيل تنظيف النسخ القديمة
./cleanup_old_backups.sh
```

#### 4. فشل في النقل لـ S3
```bash
# فحص اتصال الشبكة
curl -I https://s3.amazonaws.com

# فحص صلاحيات S3
aws s3api get-bucket-location --bucket ai-teddy-emergency-backups

# إعادة المحاولة مع verbose
aws s3 cp file.enc s3://bucket/ --debug
```

---

## 📋 قائمة التحقق اليومية

### للمشغل (DevOps):

- [ ] فحص سجلات النسخ الاحتياطية اليومية
- [ ] التحقق من حالة الجدولة التلقائية  
- [ ] مراجعة تقارير CloudWatch
- [ ] فحص مساحة S3 والتكاليف
- [ ] اختبار استعادة عشوائية (أسبوعياً)

### للمطور:
- [ ] التأكد من حفظ مفاتيح التشفير
- [ ] مراجعة التكوينات الجديدة
- [ ] اختبار النسخ الاحتياطية بعد التحديثات

### للإدارة:
- [ ] مراجعة تقارير السلامة الشهرية
- [ ] مراجعة التكاليف السحابية
- [ ] التأكد من الامتثال للمعايير

---

## 🚨 إجراءات الطوارئ

### في حالة فقدان البيانات:

1. **تقييم فوري للضرر**
   ```bash
   # فحص ما هو متاح
   ls -la /var/lib/teddy/monitoring/
   docker ps -a | grep teddy
   ```

2. **العثور على أحدث نسخة احتياطية**
   ```bash
   ./restore_backup.sh --list | head -5
   ```

3. **استعادة طارئة**
   ```bash
   # إيقاف النظام الحالي
   docker-compose down
   
   # استعادة آخر نسخة
   ./restore_backup.sh latest
   ```

4. **التحقق من النظام المستعاد**
   ```bash
   # فحص الخدمات
   curl -f http://localhost:9090/-/healthy
   curl -f http://localhost:3000/api/health
   ```

### في حالة اختراق النظام:

1. **عزل فوري**
   ```bash
   # إيقاف جميع الخدمات
   docker-compose down
   
   # قطع الاتصال بالشبكة
   sudo iptables -P INPUT DROP
   sudo iptables -P OUTPUT DROP
   ```

2. **نسخة احتياطية للأدلة**
   ```bash
   # حفظ حالة النظام
   sudo tar -czf /tmp/incident_$(date +%s).tar.gz \
     /var/log/ /var/lib/teddy/ /tmp/
   ```

3. **استعادة من نسخة نظيفة**
   ```bash
   # استعادة من نسخة قبل الاختراق
   ./restore_backup.sh [clean_timestamp]
   ```

---

## 📚 المراجع والوثائق

### الوثائق التقنية:
- [AWS S3 Backup Best Practices](https://docs.aws.amazon.com/s3/latest/userguide/backup-best-practices.html)
- [OpenSSL Encryption Guide](https://www.openssl.org/docs/man1.1.1/man1/enc.html)
- [Docker Data Management](https://docs.docker.com/storage/)

### معايير الأمان:
- [NIST Backup Guidelines](https://csrc.nist.gov/glossary/term/backup)
- [ISO 27001 Backup Requirements](https://www.iso.org/standard/54534.html)
- [GDPR Data Protection](https://gdpr.eu/data-protection/)

### أدوات المراقبة:
- [CloudWatch Logs](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/)
- [Prometheus Monitoring](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Grafana Dashboards](https://grafana.com/docs/grafana/latest/dashboards/)

---

## 🔧 التخصيص والتطوير

### إضافة backup جديد:

```bash
# إنشاء سكريبت مخصص
cat > custom_backup.sh << 'EOF'
#!/bin/bash
set -euo pipefail

# إعدادات مخصصة
CUSTOM_DATA="/path/to/custom/data"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# نسخ البيانات المخصصة
tar -czf "/tmp/custom_${TIMESTAMP}.tar.gz" "${CUSTOM_DATA}"

# تشفير
openssl enc -aes-256-cbc -salt -pbkdf2 \
  -in "/tmp/custom_${TIMESTAMP}.tar.gz" \
  -out "/tmp/custom_${TIMESTAMP}.tar.gz.enc" \
  -k "$BACKUP_ENCRYPTION_KEY"

# رفع لـ S3
aws s3 cp "/tmp/custom_${TIMESTAMP}.tar.gz.enc" \
  "s3://$BACKUP_S3_BUCKET/custom/$TIMESTAMP/"

# تنظيف
rm -f "/tmp/custom_${TIMESTAMP}.tar.gz" "/tmp/custom_${TIMESTAMP}.tar.gz.enc"
EOF

chmod +x custom_backup.sh
```

### تخصيص الجدولة:

```bash
# إضافة مهمة جديدة لـ cron
echo "0 */2 * * * root /path/to/custom_backup.sh >> /var/log/teddy/custom-backup.log 2>&1" \
  >> /etc/cron.d/teddy-emergency-backup
```

---

## ⚠️ ملاحظات مهمة

🔒 **أمان المفاتيح:**
- احفظ مفتاح التشفير في مكان آمن منفصل
- استخدم AWS Secrets Manager للبيئات الإنتاجية
- قم بتدوير المفاتيح دورياً (كل 90 يوم)

💰 **التكاليف السحابية:**
- مراقبة تكاليف S3 شهرياً
- استخدام Glacier للنسخ طويلة المدى
- تنظيف النسخ القديمة تلقائياً

⚡ **الأداء:**
- تشغيل النسخ الاحتياطية في أوقات الازدحام المنخفض
- استخدام compression للملفات الكبيرة
- مراقبة bandwidth للنقل السحابي

🧪 **الاختبار:**
- اختبار استعادة شهرياً على الأقل
- فحص سلامة النسخ أسبوعياً
- مراجعة وتحديث الإجراءات ربع سنوياً

---

**💾 نظام النسخ الاحتياطي الكامل جاهز ويحمي بياناتك على مدار الساعة!**

*تم تطوير هذا النظام بواسطة فريق DevOps - AI Teddy Bear Project*  
*آخر تحديث: ديسمبر 2024* 