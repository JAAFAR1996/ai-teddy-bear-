# ⚡ ESP32 - الربط السريع

## 🎯 **الهدف:** ربط دمية ESP32 بالنظام الذي يعمل الآن

---

## 🛒 **اشتري هذه القطع (الأساسية فقط):**

### **للتجربة البسيطة:**
- ✅ **ESP32 DevKit** - $10
- ✅ **ميكروفون USB** (بدلاً من I2S) - $5  
- ✅ **زر ضغط واحد** - $1
- ✅ **LED** واحد - $0.50
- ✅ **أسلاك توصيل** - $3

**💰 التكلفة: ~$20 للتجربة**

### **للنسخة الكاملة:**
- ESP32-S3 مع PSRAM - $15
- ميكروفون I2S (INMP441) - $8
- مكبر صوت I2S (MAX98357A) - $12
- 3 أزرار + 4 LED - $5
- كابلات وقطع إضافية - $10

**💰 التكلفة: ~$50 للنسخة الكاملة**

---

## ⚡ **الإعداد السريع (10 دقائق):**

### **الخطوة 1: تحضير ESP32**
```bash
# 1. حمّل Arduino IDE من: https://arduino.cc
# 2. ثبّت ESP32 boards: 
#    File → Preferences → Additional URLs:
#    https://dl.espressif.com/dl/package_esp32_index.json
# 3. Tools → Board Manager → ابحث "ESP32" → Install
```

### **الخطوة 2: توصيل بسيط**
```
ESP32 Pin 12  →  زر Talk (إلى GND)
ESP32 Pin 2   →  LED Status (مع مقاومة 220Ω)
ESP32 USB    →  كمبيوتر (للبرمجة والطاقة)
```

### **الخطوة 3: رفع الكود**
```cpp
// 1. افتح Arduino IDE
// 2. انسخ هذا الكود البسيط:

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

const char* ssid = "اسم_الواي_فاي";          // عدّل هذا
const char* password = "كلمة_المرور";         // عدّل هذا  
const char* serverURL = "http://192.168.0.171:8000";  // عدّل IP حسب جهازك

const int BUTTON_PIN = 12;
const int LED_PIN = 2;

void setup() {
  Serial.begin(115200);
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  pinMode(LED_PIN, OUTPUT);
  
  // اتصال WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("WiFi Connected!");
  
  // تسجيل الجهاز
  registerDevice();
}

void loop() {
  if (digitalRead(BUTTON_PIN) == LOW) {
    digitalWrite(LED_PIN, HIGH);
    sendTestMessage();
    digitalWrite(LED_PIN, LOW);
    delay(1000);
  }
}

void registerDevice() {
  HTTPClient http;
  http.begin(serverURL + "/api/v1/devices/register");
  http.addHeader("Content-Type", "application/json");
  
  String payload = "{\"device_id\":\"ESP32_TEST_001\",\"firmware_version\":\"1.0.0\"}";
  int response = http.POST(payload);
  
  if (response == 201) {
    Serial.println("✅ Device registered!");
  } else {
    Serial.println("❌ Registration failed");
  }
  http.end();
}

void sendTestMessage() {
  HTTPClient http;
  http.begin(serverURL + "/api/v1/interact");
  http.addHeader("Content-Type", "application/json");
  
  String payload = "{\"message\":\"مرحبا من ESP32!\",\"child_id\":\"test_child\",\"device_id\":\"ESP32_TEST_001\"}";
  int response = http.POST(payload);
  
  if (response == 200) {
    String result = http.getString();
    Serial.println("Response: " + result);
  }
  http.end();
}

// 3. عدّل اسم الواي فاي و IP
// 4. Tools → Board → "ESP32 Dev Module"  
// 5. Tools → Port → اختر المنفذ
// 6. اضغط Upload
```

---

## 🧪 **اختبار سريع:**

### **بعد رفع الكود:**
```
1. افتح Serial Monitor (Ctrl+Shift+M)
2. يجب أن ترى: "WiFi Connected!" و "✅ Device registered!"
3. اضغط الزر → LED يضيء → رسالة تُرسل للـ Backend
4. تحقق من http://localhost:3000 → يجب أن ترى الجهاز في القائمة
```

### **في Dashboard:**
```
انتقل إلى: http://localhost:3000/devices
يجب أن ترى: "ESP32_TEST_001" مُسجّل ومتصل
```

---

## 🎮 **الاستخدام:**
1. **اضغط الزر** على ESP32
2. **LED يضيء** → رسالة تُرسل  
3. **Backend يعالج** الطلب
4. **الرد يظهر** في Serial Monitor

---

## 🚀 **للترقية للنسخة الكاملة:**

### **أضف الصوت:**
```cpp
// استخدم esp32/secure_teddy_main.ino من المشروع
// يتضمن:
- معالجة صوت I2S
- WebSocket للتواصل الفوري  
- ضغط صوت MP3
- نظام LED متقدم
- إعدادات أمان
```

### **أضف المميزات:**
- **ميكروفون حقيقي** بدلاً من رسائل نصية
- **مكبر صوت** للردود الصوتية
- **أزرار إضافية** للتحكم في الصوت
- **بطارية** للاستخدام المحمول

---

## 🔧 **حل المشاكل:**

### **ESP32 لا يتصل:**
```
1. تأكد من اسم الواي فاي صحيح
2. الشبكة 2.4GHz (ليست 5GHz)
3. تأكد من IP الـ Backend صحيح
4. اختبر: ping 192.168.1.100
```

### **لا يظهر في Dashboard:**
```
1. تأكد أن Backend يعمل على المنفذ 8000
2. تحقق من Firewall/Antivirus
3. اختبر: curl http://localhost:8000/health
```

### **الكود لا يُرفع:**
```
1. تأكد من اختيار Board الصحيح
2. تأكد من Port الصحيح  
3. اضغط زر BOOT أثناء الرفع
```

---

## 📋 **الخطوات التالية:**

✅ **مكتمل:** Backend + Frontend يعملان  
🔄 **الآن:** ESP32 متصل ويُرسل رسائل  
⏭️ **التالي:** إضافة الصوت والمميزات المتقدمة  

### **خطة التطوير:**
1. ✅ **اختبار الاتصال** (ESP32 ↔ Backend)
2. 🔄 **إضافة الميكروفون** (I2S)
3. ⏭️ **إضافة المكبر** (I2S)  
4. ⏭️ **تحسين التفاعل** (LED + Buttons)
5. ⏭️ **إضافة البطارية** (محمول)

---

## 💡 **نصائح:**
- **ابدأ بسيط** ثم أضف المميزات تدريجياً
- **اختبر كل خطوة** قبل الانتقال للتالية  
- **احفظ نسخ احتياطية** من الكود الذي يعمل
- **راجع Serial Monitor** دائماً للأخطاء

**🎯 الهدف: ESP32 يتكلم مع طفلك خلال ساعة!** 