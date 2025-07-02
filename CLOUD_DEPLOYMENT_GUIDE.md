# 🧸 AI Teddy Bear - دليل النشر السحابي

## 📋 نظرة عامة

هذا الدليل يوضح كيفية نشر مشروع AI Teddy Bear على الخدمات السحابية المختلفة مع أفضل الممارسات في الأمان والأداء.

## 🛠️ المتطلبات الأساسية

### Software Requirements
- Docker & Docker Compose
- Git
- Node.js 18+ (للـ Frontend)
- Python 3.11+
- SSL Certificate

### Cloud Provider Options
1. **AWS** (الموصى به للمؤسسات)
   - EC2 instances
   - RDS for PostgreSQL
   - ElastiCache for Redis
   - S3 for file storage
   - CloudFront CDN

2. **Digital Ocean** (أفضل للبداية)
   - Droplets
   - Managed Databases
   - Spaces (S3 compatible)

3. **Google Cloud Platform**
   - Compute Engine
   - Cloud SQL
   - Cloud Storage

## 🚀 خطوات النشر السريع (بدون دومين)

> ✨ **لا تحتاج دومين!** يمكنك استخدام IP الخادم مباشرة

## 🚀 خطوات النشر السريع

### 1. إعداد الخادم

```bash
# تحديث النظام
sudo apt update && sudo apt upgrade -y

# تثبيت Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# تثبيت Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# إعادة تسجيل الدخول لتفعيل صلاحيات Docker
logout
```

### 2. تنزيل المشروع

```bash
git clone https://github.com/your-repo/ai-teddy-bear.git
cd ai-teddy-bear
```

### 3. إعداد متغيرات البيئة

```bash
# إنشاء ملف البيئة
cp config/api_keys.json.example config/api_keys.json

# تعديل الإعدادات
nano config/api_keys.json
```

### 4. تصدير متغيرات البيئة

```bash
# إعدادات قاعدة البيانات
export POSTGRES_DB="teddy_bear_prod"
export POSTGRES_USER="teddy_user"
export POSTGRES_PASSWORD="your-strong-password-here"

# إعدادات Redis
export REDIS_PASSWORD="your-redis-password"

# مفاتيح الأمان
export JWT_SECRET_KEY="your-jwt-secret-32-chars-min"
export ENCRYPTION_KEY="your-encryption-key-exactly-32-chars"

# مفاتيح AI Services
export OPENAI_API_KEY="sk-your-openai-key"
export ELEVENLABS_API_KEY="your-elevenlabs-key"

# إعدادات Frontend (بدون دومين)
# احصل على IP الخادم: curl ifconfig.me
export FRONTEND_URL="http://YOUR_SERVER_IP:8000"  # مثال: http://165.22.123.45:8000

# إعدادات Grafana
export GRAFANA_ADMIN_PASSWORD="your-grafana-password"
```

### 5. تشغيل النشر

```bash
# تشغيل script النشر
chmod +x scripts/cloud-deployment.sh
./scripts/cloud-deployment.sh deploy
```

## 🔧 إعدادات متقدمة

### إعداد SSL Certificate

#### مع Let's Encrypt (مجاني)
```bash
# تثبيت Certbot
sudo apt install certbot

# الحصول على شهادة SSL
sudo certbot certonly --standalone -d your-domain.com

# نسخ الشهادات
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ./nginx/ssl/
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ./nginx/ssl/
```

#### مع Cloudflare
```bash
# تحديث nginx config لاستخدام Cloudflare certificates
# الملف: monitoring/emergency/nginx/nginx.conf
```

### إعداد النطاق (Domain)

1. **إعداد DNS Records:**
```
A     @           YOUR_SERVER_IP
A     api         YOUR_SERVER_IP
A     dashboard   YOUR_SERVER_IP
CNAME www         your-domain.com
```

2. **تحديث CORS Settings:**
```bash
export CORS_ORIGINS="https://your-domain.com,https://www.your-domain.com,https://api.your-domain.com"
```

## 📊 المراقبة والصيانة

### الوصول لـ Dashboards

- **Application:** `https://your-domain.com`
- **API Docs:** `https://your-domain.com/docs`
- **Grafana:** `https://your-domain.com:3000`
- **Prometheus:** `https://your-domain.com:9090`

### أوامر مفيدة

```bash
# عرض حالة الخدمات
./scripts/cloud-deployment.sh status

# عرض السجلات
./scripts/cloud-deployment.sh logs

# إنشاء نسخة احتياطية
./scripts/cloud-deployment.sh backup

# إيقاف الخدمات
./scripts/cloud-deployment.sh stop
```

## 🔒 إعدادات الأمان

### Firewall Settings

```bash
# إعداد UFW Firewall
sudo ufw enable
sudo ufw default deny incoming
sudo ufw default allow outgoing

# السماح بالمنافذ المطلوبة
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw allow 8000  # API (اختياري للاختبار)
```

### Security Hardening

1. **تأمين SSH:**
```bash
# تعطيل root login
sudo sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config

# تغيير منفذ SSH
sudo sed -i 's/#Port 22/Port 2222/' /etc/ssh/sshd_config

sudo systemctl restart ssh
```

2. **تحديث كلمات المرور بانتظام:**
```bash
# تغيير كلمة مرور قاعدة البيانات
export POSTGRES_PASSWORD="new-secure-password"
./scripts/cloud-deployment.sh deploy
```

## 🌐 إعدادات ESP32 (بدون دومين)

### WebSocket Connection (HTTP - بدون SSL)

```cpp
// في ESP32 code - استخدم IP الخادم مباشرة
const char* websocket_server = "ws://165.22.123.45:8000/ws";  // ضع IP خادمك هنا
const char* api_endpoint = "http://165.22.123.45:8000/api";
const char* device_id = "teddy_001";

// إعدادات WiFi
const char* ssid = "your_wifi_name";
const char* password = "your_wifi_password";
```

### MQTT Configuration (اختياري)

```json
{
  "mqtt": {
    "broker": "165.22.123.45",  // IP الخادم
    "port": 1883,
    "username": "teddy_esp32",
    "password": "your-mqtt-password",
    "topics": {
      "audio": "teddy/audio",
      "commands": "teddy/commands",
      "status": "teddy/status"
    }
  }
}
```

### كود ESP32 مثال:

```cpp
#include <WiFi.h>
#include <WebSocketsClient.h>
#include <ArduinoJson.h>

// إعدادات الاتصال
const char* ssid = "your_wifi";
const char* password = "your_password";
const char* server_ip = "165.22.123.45";  // ضع IP خادمك
const int server_port = 8000;

WebSocketsClient webSocket;

void setup() {
    Serial.begin(115200);
    
    // الاتصال بالواي فاي
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.println("Connecting to WiFi...");
    }
    
    Serial.println("WiFi connected!");
    Serial.print("IP: ");
    Serial.println(WiFi.localIP());
    
    // الاتصال بالخادم
    webSocket.begin(server_ip, server_port, "/ws");
    webSocket.onEvent(webSocketEvent);
    webSocket.setReconnectInterval(5000);
}

void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
    switch(type) {
        case WStype_CONNECTED:
            Serial.printf("Connected to server: %s\n", payload);
            break;
        case WStype_TEXT:
            Serial.printf("Received: %s\n", payload);
            break;
        case WStype_DISCONNECTED:
            Serial.println("Disconnected from server");
            break;
    }
}

void loop() {
    webSocket.loop();
    // باقي كود التطبيق
}
```

## 🔄 النشر المستمر (CI/CD)

### GitHub Actions

إنشاء `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to server
      uses: appleboy/ssh-action@v0.1.5
      with:
        host: ${{ secrets.HOST }}
        username: ${{ secrets.USERNAME }}
        key: ${{ secrets.SSH_KEY }}
        script: |
          cd /path/to/ai-teddy-bear
          git pull origin main
          ./scripts/cloud-deployment.sh deploy
```

## 📈 تحسين الأداء

### Database Optimization

```sql
-- إعداد PostgreSQL للإنتاج
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
SELECT pg_reload_conf();
```

### Redis Optimization

```bash
# في ملف redis.conf
maxmemory 512mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

## 🆘 استكشاف الأخطاء

### مشاكل شائعة وحلولها

1. **فشل في الاتصال بقاعدة البيانات:**
```bash
# فحص حالة قاعدة البيانات
docker-compose -f src/docker-compose.prod.yml logs postgres

# إعادة تشغيل قاعدة البيانات
docker-compose -f src/docker-compose.prod.yml restart postgres
```

2. **مشاكل في SSL:**
```bash
# فحص صحة الشهادة
openssl x509 -in nginx/ssl/teddyai.crt -text -noout

# تجديد Let's Encrypt
sudo certbot renew
```

3. **استهلاك عالي للذاكرة:**
```bash
# مراقبة استهلاك الموارد
docker stats

# تحسين إعدادات الذاكرة
export POSTGRES_SHARED_BUFFERS=256MB
```

## 📞 الدعم والمساعدة

### Logs Locations
- Application: `logs/app.log`
- Nginx: `logs/nginx/`
- Database: Docker logs
- Redis: Docker logs

### Health Checks
- Application: `https://your-domain.com/health`
- Database: `docker-compose exec postgres pg_isready`
- Redis: `docker-compose exec redis redis-cli ping`

### Contact
- Email: support@teddyai.com
- Documentation: https://docs.teddyai.com
- Issues: GitHub Issues

---

## 🎯 خطة النشر خطوة بخطوة

### المرحلة 1: الإعداد الأولي (30 دقيقة)
1. ✅ إعداد الخادم السحابي
2. ✅ تثبيت Docker & Dependencies
3. ✅ تنزيل المشروع

### المرحلة 2: التكوين (45 دقيقة)
1. ✅ إعداد متغيرات البيئة
2. ✅ تكوين قاعدة البيانات
3. ✅ إعداد النطاق وSSL

### المرحلة 3: النشر (30 دقيقة)
1. ✅ تشغيل script النشر
2. ✅ فحص الخدمات
3. ✅ إعداد المراقبة

### المرحلة 4: التحقق (15 دقيقة)
1. ✅ اختبار الاتصال
2. ✅ فحص ESP32 connectivity
3. ✅ تجربة Parent Dashboard

**المدة الإجمالية: ~2 ساعة**

---

## ⚡ التلخيص السريع (بدون دومين)

### خطوات سريعة للنشر:

1. **احصل على خادم سحابي** (Digital Ocean/AWS/GCP)
2. **تثبيت Docker:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh
```

3. **تحديد IP الخادم:**
```bash
curl ifconfig.me  # سيعطيك IP مثل: 165.22.123.45
```

4. **تعيين متغيرات البيئة:**
```bash
export POSTGRES_PASSWORD="StrongPass123!"
export REDIS_PASSWORD="RedisPass123!"
export JWT_SECRET_KEY="your-jwt-secret-min-32-characters"
export OPENAI_API_KEY="sk-your-openai-key"
export FRONTEND_URL="http://165.22.123.45:8000"  # ضع IP خادمك
```

5. **تشغيل النشر:**
```bash
git clone your-repo && cd ai-teddy-bear
./scripts/cloud-deployment.sh deploy
```

6. **إعداد ESP32:**
```cpp
const char* websocket_server = "ws://165.22.123.45:8000/ws";
```

### 🎯 النتيجة:
- **تطبيق يعمل على:** `http://YOUR_SERVER_IP:8000`
- **ESP32 متصل بالخادم مباشرة**
- **لا حاجة لدومين أو شهادات SSL معقدة**

---

*تم إنشاء هذا الدليل بواسطة AI Teddy Bear Team - إصدار 2025* 