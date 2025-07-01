# 🤖 دليل إعداد ESP32 - الدمية الذكية

## 🧸 **نظرة عامة**

الآن بعد تشغيل البرمجيات بنجاح، نحتاج لإعداد **الجزء الفيزيائي** - دمية ESP32 التي ستتفاعل مع الأطفال.

---

## 🛠️ **المتطلبات الأساسية**

### **1. قطع الـ Hardware:**
- **ESP32 DevKit** (يفضل ESP32-S3 مع PSRAM)
- **ميكروفون I2S** (مثل INMP441)
- **مكبر صوت** مع **DAC** (مثل MAX98357A)
- **3 أزرار ضغط** (Talk, Volume+, Volume-)
- **4 LED** (Status, Listening, Processing, Error)
- **بطارية ليثيوم** 3.7V (اختياري)
- **أسلاك توصيل** و **مقاومات**

### **2. برامج التطوير:**
- **Arduino IDE 2.x** أو **PlatformIO**
- **ESP32 Board Package**
- **مكتبات Arduino** المطلوبة

---

## ⚙️ **الخطوة 1: إعداد بيئة التطوير**

### **تثبيت Arduino IDE:**
1. حمّل من: https://www.arduino.cc/en/software
2. ثبّت ESP32 Board Package:
   - File → Preferences
   - Additional Board Manager URLs: 
     ```
     https://dl.espressif.com/dl/package_esp32_index.json
     ```
   - Tools → Board → Boards Manager → ابحث عن "ESP32" وثبّت

### **تثبيت المكتبات المطلوبة:**
```cpp
// افتح Arduino IDE → Tools → Manage Libraries
// ابحث وثبّت هذه المكتبات:

WiFi                    // مدمجة مع ESP32
HTTPClient              // مدمجة مع ESP32  
ArduinoJson             // by Benoit Blanchon
WebSockets              // by Markus Sattler
AsyncTCP                // by me-no-dev
ESPAsyncWebServer       // by me-no-dev
Preferences             // مدمجة مع ESP32
```

---

## 🔌 **الخطوة 2: التوصيلات الكهربائية**

### **مخطط التوصيل:**

```
ESP32 Pin    →    Component
=========================================
GPIO 12      →    زر Talk (مع مقاومة Pull-up)
GPIO 13      →    زر Volume+ (مع مقاومة Pull-up)  
GPIO 14      →    زر Volume- (مع مقاومة Pull-up)

GPIO 2       →    LED Status (أخضر)
GPIO 4       →    LED Listening (أزرق)
GPIO 5       →    LED Processing (أصفر)
GPIO 18      →    LED Error (أحمر)

// I2S Microphone (INMP441)
GPIO 26      →    I2S_BCLK (Bit Clock)
GPIO 25      →    I2S_LRCLK (Left/Right Clock)
GPIO 33      →    I2S_DIN (Data Input)
3.3V         →    VCC
GND          →    GND

// I2S Speaker (MAX98357A)
GPIO 22      →    I2S_BCLK
GPIO 23      →    I2S_LRCLK  
GPIO 21      →    I2S_DIN
5V           →    VCC
GND          →    GND
```

### **صورة توضيحية للتوصيل:**
```
     ┌─────────────────┐
     │     ESP32       │
     │                 │
 ┌───┤ GPIO12   GPIO2 ├───● LED Status
 │   │                 │
 ●   │ GPIO13   GPIO4 ├───● LED Listening  
Talk │                 │
     │ GPIO14   GPIO5 ├───● LED Processing
 ●   │                 │
Vol+ │         GPIO18 ├───● LED Error
     │                 │
 ●   │ GPIO26  GPIO22 ├───┐
Vol- │                 │   │ Speaker
     │ GPIO25  GPIO23 ├───┤ I2S
     │                 │   │
     │ GPIO33  GPIO21 ├───┘
     │                 │
     └─────────────────┘
           │      │
           ●      ●
        Mic I2S  Power
```

---

## 📝 **الخطوة 3: برمجة ESP32**

### **1. اختر الكود المناسب:**
```cpp
// للاستخدام العادي:
esp32/secure_teddy_main.ino

// للجودة العالية مع ضغط MP3:
esp32/secure_teddy_main_mp3_enhanced.ino

// للاختبار والتطوير:
esp32/audio_stream.ino
```

### **2. إعداد الكود:**
```cpp
// افتح esp32/secure_teddy_main.ino في Arduino IDE

// عدّل هذه الإعدادات:
String server_url = "http://192.168.1.100:8000";  // IP الخاص بك
String wifi_ssid = "اسم_الواي_فاي";
String wifi_password = "كلمة_مرور_الواي_فاي";

// تأكد من إعدادات الـ pins:
const int BUTTON_TALK = 12;
const int LED_STATUS = 2;
// ... إلخ
```

### **3. رفع الكود:**
```cpp
// 1. وصّل ESP32 بـ USB
// 2. اختر Board: "ESP32 Dev Module"
// 3. اختر Port المناسب
// 4. اضغط Upload
```

---

## 🔧 **الخطوة 4: التكوين الأولي**

### **عند التشغيل لأول مرة:**

1. **ESP32 سينشئ شبكة WiFi:**
   ```
   Network: "TeddyBear_Setup"
   Password: "teddy123"
   ```

2. **اتصل بالشبكة وادخل:**
   ```
   http://192.168.4.1
   ```

3. **أدخل إعدادات WiFi:**
   - اسم الشبكة الخاصة بك
   - كلمة المرور
   - IP الخاص بالـ Backend (مثل: 192.168.1.100:8000)

4. **حفظ وإعادة التشغيل**

---

## 🧪 **الخطوة 5: اختبار النظام**

### **اختبار الاتصال:**
```bash
# في الـ terminal:
curl http://localhost:8000/api/v1/devices

# يجب أن ترى ESP32 مسجل كجهاز جديد
```

### **اختبار الصوت:**
1. **اضغط زر "Talk"** على ESP32
2. **LED الأزرق** يجب أن يضيء (Listening)
3. **تكلم** لمدة 3-5 ثوان
4. **LED الأصفر** يضيء (Processing)
5. **الرد** يأتي من المكبر

### **متابعة اللوجز:**
```cpp
// افتح Serial Monitor في Arduino IDE (Ctrl+Shift+M)
// يجب أن ترى:
🧸 AI Teddy Bear - Audio Streaming v1.0
✅ WiFi connected: 192.168.1.101
✅ WebSocket connected to server
🎤 Audio system ready
```

---

## 🎯 **التكامل مع النظام الكامل**

### **تدفق البيانات:**
```
ESP32 Mic → I2S → WiFi → WebSocket → Backend → AI → Response → ESP32 Speaker
```

### **تسجيل الجهاز:**
```json
// ESP32 يرسل تلقائياً:
{
  "device_id": "ESP32_UNIQUE_ID",
  "device_type": "teddy_bear",
  "status": "online",
  "capabilities": ["audio_input", "audio_output", "led_indicators"]
}
```

### **معرف الطفل:**
```cpp
// يتم ربط ESP32 بطفل معين عبر:
// 1. QR Code على الدمية
// 2. تطبيق الوالدين
// 3. إعداد أولي
```

---

## 🔧 **حل المشاكل الشائعة**

### **ESP32 لا يتصل بـ WiFi:**
```cpp
// تحقق من:
1. اسم الشبكة وكلمة المرور صحيحة
2. الشبكة 2.4GHz (ليست 5GHz)
3. قوة الإشارة كافية
4. إعادة ضبط المصنع: اضغط BOOT + EN معاً
```

### **لا يوجد صوت:**
```cpp
// تحقق من:
1. توصيل I2S صحيح
2. مصدر الطاقة كافي (5V للمكبر)
3. مستوى الصوت (أزرار Volume)
4. كابل الصوت سليم
```

### **ESP32 لا يظهر في Backend:**
```cpp
// تحقق من:
1. Backend يعمل على http://IP:8000
2. Firewall يسمح بالاتصال
3. WebSocket مفعّل
4. Device ID مُعرّف صحيح
```

### **جودة الصوت ضعيفة:**
```cpp
// حلول:
1. استخدم esp32/secure_teddy_main_mp3_enhanced.ino
2. تحقق من جودة الميكروفون
3. قرّب الميكروفون من المتكلم
4. قلل الضوضاء المحيطة
```

---

## 📊 **مراقبة الأداء**

### **في Arduino Serial Monitor:**
```cpp
🎤 Captured: 1024 samples, Level: 156
📡 WebSocket: Connected, Latency: 45ms
🔋 Battery: 87%, Free heap: 234KB
⚡ CPU: 45%, WiFi: -55dBm
```

### **في Backend Dashboard:**
```json
{
  "device_id": "ESP32_ABC123",
  "status": "online",
  "last_seen": "2025-01-01T12:00:00Z",
  "audio_quality": "good",
  "wifi_strength": -55,
  "battery_level": 87
}
```

---

## 🎯 **الاستخدام اليومي**

### **سيناريو الاستخدام:**
1. **طفل يضغط زر "Talk"**
2. **LED أزرق يضيء** → "يمكنك التحدث الآن"
3. **طفل يتكلم:** "مرحبا دبدوبي!"
4. **LED أصفر يضيء** → "أفكر في الرد..."
5. **الرد يأتي:** "مرحبا حبيبي! كيف حالك اليوم؟"
6. **LED أخضر ثابت** → "جاهز للحديث التالي"

### **مؤشرات LED:**
- 🟢 **أخضر ثابت:** متصل وجاهز
- 🔵 **أزرق يرمش:** يستمع للطفل  
- 🟡 **أصفر يرمش:** يعالج الطلب
- 🔴 **أحمر:** خطأ أو انقطاع الاتصال

---

## 🚀 **الخطوات التالية**

### **بعد إتمام ESP32:**
1. **اختبار التفاعل الكامل** 
2. **ربط تطبيق الوالدين**
3. **إعداد ملفات الأطفال**
4. **تخصيص الردود**
5. **مراقبة الاستخدام**

### **التحسينات المتقدمة:**
- **ضغط صوت MP3** للجودة العالية
- **وضع توفير الطاقة** للبطارية
- **تحديثات OTA** عبر الشبكة
- **مستشعرات إضافية** (حرارة، حركة)

---

## ✅ **قائمة التحقق النهائية**

- [ ] ESP32 متصل ومُعرّف
- [ ] الصوت يعمل (دخل وخرج)
- [ ] LED تعمل بشكل صحيح
- [ ] WebSocket متصل بـ Backend
- [ ] الجهاز يظهر في Dashboard
- [ ] التفاعل الصوتي يعمل
- [ ] بيانات الطفل محفوظة

**🎉 تهانينا! دميتك الذكية جاهزة للاستخدام!** 