# 🚀 AI Teddy Bear - بدء سريع بدون دومين

## لا تحتاج دومين! استخدم IP الخادم مباشرة

### 1. اختيار خادم سحابي:
- **Digital Ocean** (5$ شهرياً - الأسهل)
- **AWS EC2** (t3.micro مجاني سنة واحدة)
- **Google Cloud** (300$ رصيد مجاني)
- **Vultr/Linode** (5$ شهرياً)

### 2. إعداد الخادم:
```bash
# تسجيل الدخول للخادم عبر SSH
ssh root@YOUR_SERVER_IP

# تثبيت Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# تثبيت Git
sudo apt update && sudo apt install git -y
```

### 3. تحديد IP الخادم:
```bash
# احصل على IP العام للخادم
curl ifconfig.me
# النتيجة مثلاً: 165.22.123.45
```

### 4. تحضير المشروع:
```bash
# تنزيل المشروع
git clone https://github.com/your-repo/ai-teddy-bear.git
cd ai-teddy-bear

# تحديد متغيرات البيئة
export POSTGRES_PASSWORD="TeddyDB2025!"
export REDIS_PASSWORD="TeddyRedis2025!"
export JWT_SECRET_KEY="TeddyJWT-Secret-Key-32-Characters"
export ENCRYPTION_KEY="TeddyEncryption-Key-32-Chars-Here"
export OPENAI_API_KEY="sk-your-openai-api-key-here"
export FRONTEND_URL="http://165.22.123.45:8000"  # ضع IP خادمك

# إعدادات اختيارية
export GRAFANA_ADMIN_PASSWORD="admin123"
```

### 5. بناء ونشر المشروع:
```bash
# تشغيل النشر التلقائي
chmod +x scripts/cloud-deployment.sh
./scripts/cloud-deployment.sh deploy
```

### 6. التحقق من النجاح:
```bash
# فحص الخدمات
docker-compose -f src/docker-compose.prod.yml ps

# اختبار API
curl http://YOUR_SERVER_IP:8000/health
```

## 🌐 URLs المهمة:
- **التطبيق:** `http://YOUR_SERVER_IP:8000`
- **API Docs:** `http://YOUR_SERVER_IP:8000/docs`
- **Grafana:** `http://YOUR_SERVER_IP:3000` (admin/your-password)
- **Health Check:** `http://YOUR_SERVER_IP:8000/health`

## 🔧 إعداد ESP32:

### Arduino IDE Code:
```cpp
#include <WiFi.h>
#include <WebSocketsClient.h>
#include <HTTPClient.h>

// إعدادات WiFi
const char* ssid = "your_wifi_name";
const char* password = "your_wifi_password";

// إعدادات الخادم
const char* server_ip = "165.22.123.45";  // ضع IP خادمك هنا
const int server_port = 8000;
const char* websocket_path = "/ws";
const char* api_endpoint = "http://165.22.123.45:8000/api";

WebSocketsClient webSocket;

void setup() {
    Serial.begin(115200);
    
    // الاتصال بالواي فاي
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.println("Connecting to WiFi...");
    }
    
    Serial.println("WiFi Connected!");
    Serial.print("ESP32 IP: ");
    Serial.println(WiFi.localIP());
    
    // الاتصال بالخادم
    webSocket.begin(server_ip, server_port, websocket_path);
    webSocket.onEvent(webSocketEvent);
    webSocket.setReconnectInterval(5000);
    
    Serial.println("ESP32 ready to connect to Teddy Server!");
}

void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
    switch(type) {
        case WStype_DISCONNECTED:
            Serial.println("Disconnected from Teddy Server");
            break;
        case WStype_CONNECTED:
            Serial.printf("Connected to Teddy Server: %s\n", payload);
            // إرسال رسالة تحية
            webSocket.sendTXT("{\"type\":\"hello\",\"device\":\"teddy_001\"}");
            break;
        case WStype_TEXT:
            Serial.printf("Received from server: %s\n", payload);
            // معالجة الرسائل من الخادم
            handleServerMessage((char*)payload);
            break;
    }
}

void handleServerMessage(String message) {
    // معالجة الأوامر من الخادم
    if (message.indexOf("play_audio") != -1) {
        // تشغيل الصوت
        Serial.println("Playing audio...");
    }
}

void sendAudioToServer(uint8_t* audioData, size_t length) {
    // إرسال البيانات الصوتية للخادم
    HTTPClient http;
    http.begin(String(api_endpoint) + "/audio/upload");
    http.addHeader("Content-Type", "audio/wav");
    
    int httpResponseCode = http.POST(audioData, length);
    
    if (httpResponseCode > 0) {
        String response = http.getString();
        Serial.println("Audio sent successfully: " + response);
    }
    
    http.end();
}

void loop() {
    webSocket.loop();
    
    // باقي منطق التطبيق
    // قراءة المايك، معالجة الأزرار، إلخ
    
    delay(100);
}
```

## 🔥 أوامر مفيدة:

```bash
# عرض حالة الخدمات
./scripts/cloud-deployment.sh status

# عرض السجلات
./scripts/cloud-deployment.sh logs

# إعادة تشغيل
./scripts/cloud-deployment.sh deploy

# إيقاف الخدمات
./scripts/cloud-deployment.sh stop

# نسخة احتياطية
./scripts/cloud-deployment.sh backup
```

## 🆘 استكشاف الأخطاء:

### إذا لم تعمل الخدمات:
```bash
# فحص Docker
docker --version
docker-compose --version

# فحص السجلات
docker-compose -f src/docker-compose.prod.yml logs
```

### إذا لم يتصل ESP32:
1. تأكد من أن IP الخادم صحيح
2. تأكد من أن المنافذ مفتوحة (8000)
3. فحص سجلات الخادم

### فتح المنافذ:
```bash
# إعداد Firewall
sudo ufw allow 22    # SSH
sudo ufw allow 8000  # API
sudo ufw allow 3000  # Grafana
sudo ufw enable
```

## 💰 تكلفة تقديرية:
- **Digital Ocean Droplet (2GB RAM):** $12/شهر
- **AWS EC2 t3.small:** $16/شهر (سنة أولى مجانية)
- **Google Cloud e2-small:** $13/شهر

## 🎯 خلاصة:
✅ **لا دومين مطلوب** - استخدم IP مباشرة  
✅ **لا SSL معقدة** - HTTP يكفي للتطوير  
✅ **نشر سريع** - 15 دقيقة للتشغيل  
✅ **ESP32 جاهز للاتصال**

---

**🧸 مشروعك جاهز للعمل! ESP32 يمكن أن يتصل بالخادم الآن!** 