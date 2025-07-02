# 🧸 دليل نشر مشروع الدب الذكي - تقسيم الملفات

## 📋 نظرة عامة على التقسيم

مشروع الدب الذكي مقسم إلى **ثلاثة أجزاء رئيسية**:

1. **🖥️ السيرفر السحابي (Cloud Server)** - يعمل على الخوادم
2. **🎛️ جهاز ESP32** - يعمل على الدب نفسه  
3. **📱 تطبيق الويب** - للأهل والإدارة

---

## 🖥️ الجزء الأول: ملفات السيرفر السحابي

### 📂 الملفات التي تُنشر على السيرفر:

#### **ملفات Python الأساسية:**
```
src/
├── main.py                          # ← ملف السيرفر الرئيسي
├── domain/                          # ← منطق العمل
├── application/                     # ← خدمات التطبيق
├── infrastructure/                  # ← قواعد البيانات والخدمات الخارجية
└── presentation/                    # ← APIs وWebSocket

config/
├── config.json                      # ← إعدادات السيرفر
├── api_keys.json.example            # ← مفاتيح APIs
└── environments/                    # ← إعدادات البيئات المختلفة

api/
├── endpoints/                       # ← نقاط API للتطبيق
└── websocket/                       # ← اتصال WebSocket مع ESP32
```

#### **ملفات قواعد البيانات:**
```
database_migrations/
└── *.sql                           # ← ملفات إنشاء الجداول
```

#### **ملفات النشر:**
```
docker-compose.*.yml                 # ← ملفات Docker
Dockerfile_from_core                 # ← صورة Docker للسيرفر
requirements_from_core.txt           # ← مكتبات Python
```

#### **ملفات المراقبة:**
```
monitoring/
├── prometheus.yml                   # ← مراقبة الأداء
├── alertmanager.yml                 # ← تنبيهات النظام
└── alert_rules.yml                  # ← قواعد التنبيهات

observability/
├── grafana-dashboards.json          # ← لوحات المراقبة
└── sli-slo-definitions.yaml         # ← معايير الجودة
```

---

## 🎛️ الجزء الثاني: ملفات ESP32 (الدب نفسه)

### 📂 الملفات التي تُحمل على ESP32:

#### **الملفات الأساسية للبرمجة:**
```
esp32/
├── teddy_main.ino                   # ← الملف الرئيسي (أساسي)
├── secure_teddy_main.ino            # ← نسخة محسنة بالأمان
├── secure_teddy_main_mp3_enhanced.ino # ← نسخة متقدمة مع MP3
└── audio_streaming_main.ino         # ← نسخة البث المباشر
```

#### **ملفات معالجة الصوت:**
```
esp32/
├── audio_processor.h                # ← ملف الهيدر للصوت
├── audio_processor.cpp              # ← معالج الصوت المتقدم
├── audio_stream.ino                 # ← بث الصوت
└── mp3_compression_test.cpp         # ← ضغط MP3
```

#### **ملفات الشبكة والاتصال:**
```
esp32/
├── ws_handler.ino                   # ← معالج WebSocket
├── send_audio_example.ino           # ← مثال إرسال الصوت
└── secure_config.h                  # ← إعدادات الأمان
```

#### **ملفات الاختبار:**
```
esp32/
├── test_mp3_compression.ino         # ← اختبار ضغط MP3
└── example_enhanced_usage.ino       # ← مثال للاستخدام المتقدم
```

### 🔧 المكونات المطلوبة للـ ESP32:
- **مايكروكنترولر**: ESP32 DevKit
- **مايكروفون**: I2S MEMS microphone
- **سماعة**: I2S amplifier + speaker
- **أزرار**: 3 أزرار (تحدث، رفع صوت، خفض صوت)
- **LEDs**: WS2812B LED strip (8 LEDs)
- **الطاقة**: بطارية Li-Po 3.7V

---

## 📱 الجزء الثالث: تطبيق الويب (للأهل)

### 📂 ملفات تطبيق الويب:

#### **ملفات React الأساسية:**
```
frontend/
├── package.json                     # ← مكتبات JavaScript
├── public/
│   ├── index.html                   # ← الصفحة الرئيسية
│   └── manifest.json                # ← إعدادات PWA
└── src/
    ├── App.tsx                      # ← التطبيق الرئيسي
    ├── components/                  # ← مكونات الواجهة
    ├── services/                    # ← خدمات API
    └── styles/                      # ← تصميم CSS
```

#### **ملفات Dashboard الإدارة:**
```
src/dashboards/
├── executive-dashboard.tsx          # ← لوحة إدارية
├── dashboard-demo.tsx               # ← عرض توضيحي
└── components/                      # ← مكونات اللوحات
```

---

## 🚀 خطوات النشر

### 1️⃣ نشر السيرفر السحابي:

```bash
# 1. تحضير البيئة
cd src/
pip install -r requirements_from_core.txt

# 2. إعداد قاعدة البيانات
python database_migrations/setup.py

# 3. تشغيل السيرفر
python main.py
```

### 2️⃣ برمجة ESP32:

```cpp
// 1. افتح Arduino IDE
// 2. اختر ملف: esp32/teddy_main.ino
// 3. غيّر إعدادات WiFi:
const char* ssid = "YOUR_WIFI_NAME";
const char* password = "YOUR_WIFI_PASSWORD";
const char* server_url = "http://your-server.com:8000";

// 4. ارفع الكود للـ ESP32
```

### 3️⃣ نشر تطبيق الويب:

```bash
# 1. تحضير التطبيق
cd frontend/
npm install

# 2. بناء التطبيق
npm run build

# 3. نشر التطبيق
# رفع مجلد build/ إلى خدمة الاستضافة
```

---

## 🔗 كيفية الاتصال بين الأجزاء

### 🔄 تدفق البيانات:

```
1. الطفل يضغط زر ← ESP32 يسجل الصوت
2. ESP32 يرسل للسيرفر ← معالجة AI
3. السيرفر يرد بالإجابة ← ESP32 يشغل الصوت
4. الأهل يراقبون ← تطبيق الويب
```

### 🌐 بروتوكولات الاتصال:

- **ESP32 ↔ Server**: WebSocket / HTTP
- **Web App ↔ Server**: REST API / WebSocket  
- **قاعدة البيانات**: SQLite/PostgreSQL
- **التشفير**: TLS 1.3

---

## 📊 ملخص سريع للملفات

| الجزء | الملفات الرئيسية | المكان |
|-------|-----------------|--------|
| 🖥️ **السيرفر** | `src/main.py`, `config/`, `api/` | الخادم السحابي |
| 🎛️ **ESP32** | `esp32/*.ino`, `esp32/*.h` | جهاز الدب |
| 📱 **الويب** | `frontend/src/`, `frontend/build/` | متصفح الأهل |

---

## ⚡ البدء السريع

### للمطورين المبتدئين:
1. ابدأ بـ `esp32/teddy_main.ino` (نسخة بسيطة)
2. شغّل `src/main.py` (السيرفر الأساسي)
3. افتح `frontend/` في المتصفح

### للمطورين المتقدمين:
1. استخدم `esp32/secure_teddy_main_mp3_enhanced.ino`
2. فعّل جميع خدمات `src/infrastructure/`
3. استخدم `docker-compose` للنشر الكامل

---

## 🛡️ ملاحظات الأمان

- **لا تضع API Keys** في ملفات ESP32
- **استخدم HTTPS** في الإنتاج
- **فعّل التشفير** لجميع الاتصالات
- **راجع إعدادات الخصوصية** للأطفال

---

## 📞 الدعم الفني

للأسئلة والمساعدة:
- **المطور الرئيسي**: جعفر أديب
- **الوثائق التقنية**: `/docs/`
- **الاختبارات**: `/tests/` 