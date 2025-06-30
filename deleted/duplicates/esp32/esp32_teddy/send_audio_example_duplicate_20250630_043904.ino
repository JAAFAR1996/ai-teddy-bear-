/*
🎤 ESP32 Audio Send Example - لإرسال الصوت إلى سيرفر دبدوب AI
*/

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <base64.h>

// 📡 WiFi و Server Settings
const char* ssid = "Adeeb";          // اسم الواي فاي
const char* password = "19961996";  // كلمة مرور الواي فاي
const char* server_url = "http://192.168.0.171:8000";  // IP الخادم المحلي

// 🎤 Audio Settings
#define MIC_PIN A0                    // دبوس الميكروفون
#define BUTTON_PIN 4                  // زر التسجيل
#define LED_PIN 2                     // LED للحالة
#define SAMPLE_RATE 8000              // معدل العينة
#define RECORD_TIME_MS 3000           // مدة التسجيل (3 ثواني)

// متغيرات النظام
String device_id = "";
String session_id = "";
bool is_recording = false;

void setup() {
    Serial.begin(115200);
    Serial.println("🧸 بدء تشغيل دبدوب ESP32...");
    
    // إعداد الأجهزة
    pinMode(BUTTON_PIN, INPUT_PULLUP);
    pinMode(LED_PIN, OUTPUT);
    pinMode(MIC_PIN, INPUT);
    
    // الاتصال بالواي فاي
    connect_wifi();
    
    // إنشاء معرف الجهاز
    device_id = "ESP32_" + WiFi.macAddress();
    device_id.replace(":", "");
    
    // تسجيل الجهاز مع الخادم
    register_device();
    
    Serial.println("✅ دبدوب جاهز! اضغط الزر للحديث");
    digitalWrite(LED_PIN, HIGH); // LED أخضر = جاهز
}

void loop() {
    // فحص الزر
    if (digitalRead(BUTTON_PIN) == LOW && !is_recording) {
        start_recording();
    }
    
    delay(50);
}

// 📡 الاتصال بالواي فاي
void connect_wifi() {
    WiFi.begin(ssid, password);
    Serial.print("🔄 جاري الاتصال بالواي فاي");
    
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
        // وميض LED أثناء الاتصال
        digitalWrite(LED_PIN, !digitalRead(LED_PIN));
    }
    
    Serial.println();
    Serial.println("✅ متصل بالواي فاي!");
    Serial.println("📍 عنوان IP: " + WiFi.localIP().toString());
}

// 📝 تسجيل الجهاز مع الخادم
void register_device() {
    if (WiFi.status() != WL_CONNECTED) return;
    
    HTTPClient http;
    http.begin(String(server_url) + "/esp32/register");
    http.addHeader("Content-Type", "application/x-www-form-urlencoded");
    
    // إرسال بيانات التسجيل
    String postData = "device_id=" + device_id + "&child_id=ahmed_5_years";
    int httpResponseCode = http.POST(postData);
    
    if (httpResponseCode == 200) {
        String response = http.getString();
        Serial.println("✅ تم تسجيل الجهاز: " + response);
        
        // استخراج session_id من الرد
        DynamicJsonDocument doc(1024);
        deserializeJson(doc, response);
        session_id = doc["session_id"].as<String>();
        
    } else {
        Serial.println("❌ فشل التسجيل: " + String(httpResponseCode));
    }
    
    http.end();
}

// 🎤 بدء التسجيل
void start_recording() {
    Serial.println("🎤 بدء التسجيل...");
    is_recording = true;
    
    // LED أحمر = تسجيل
    for (int i = 0; i < 10; i++) {
        digitalWrite(LED_PIN, HIGH);
        delay(100);
        digitalWrite(LED_PIN, LOW);
        delay(100);
    }
    
    // تجميع بيانات الصوت (محاكاة)
    String audio_data = record_audio();
    
    // إرسال الصوت إلى الخادم
    send_audio_to_server(audio_data);
    
    is_recording = false;
    digitalWrite(LED_PIN, HIGH); // العودة إلى الأخضر
}

// 🎵 تسجيل الصوت (محاكاة بسيطة)
String record_audio() {
    Serial.println("🎵 جاري تسجيل الصوت لمدة 3 ثواني...");
    
    // في التطبيق الحقيقي، نقرأ من الميكروفون
    // هنا سنرسل بيانات وهمية للاختبار
    
    String fake_audio = "";
    for (int i = 0; i < 100; i++) {
        int sample = analogRead(MIC_PIN); // قراءة من الميكروفون
        fake_audio += String(sample) + ",";
        delay(30); // حوالي 3 ثواني إجمالي
    }
    
    // تحويل إلى base64 (محاكاة)
    String encoded = base64::encode((uint8_t*)fake_audio.c_str(), fake_audio.length());
    
    Serial.println("✅ تم الانتهاء من التسجيل");
    return encoded;
}

// 📤 إرسال الصوت إلى الخادم
void send_audio_to_server(String audio_data) {
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("❌ لا يوجد اتصال واي فاي!");
        return;
    }
    
    Serial.println("📤 إرسال الصوت إلى الخادم...");
    
    HTTPClient http;
    http.begin(String(server_url) + "/esp32/audio");
    http.addHeader("Content-Type", "application/json");
    
    // إنشاء JSON payload
    DynamicJsonDocument doc(2048);
    doc["device_id"] = device_id;
    doc["child_id"] = "ahmed_5_years";
    doc["audio_data"] = audio_data;
    doc["session_id"] = session_id;
    doc["timestamp"] = String(millis());
    doc["duration_ms"] = RECORD_TIME_MS;
    doc["sample_rate"] = SAMPLE_RATE;
    
    String payload;
    serializeJson(doc, payload);
    
    // إرسال الطلب
    int httpResponseCode = http.POST(payload);
    
    if (httpResponseCode == 200) {
        String response = http.getString();
        Serial.println("✅ رد الخادم: " + response);
        
        // معالجة رد AI
        handle_ai_response(response);
        
    } else {
        Serial.println("❌ خطأ HTTP: " + String(httpResponseCode));
    }
    
    http.end();
}

// 🤖 معالجة رد الذكاء الاصطناعي
void handle_ai_response(String response) {
    DynamicJsonDocument doc(1024);
    deserializeJson(doc, response);
    
    if (doc["success"].as<bool>()) {
        String ai_message = doc["message"].as<String>();
        String audio_response = doc["audio_data"].as<String>();
        
        Serial.println("🐻 دبدوب يقول: " + ai_message);
        
        if (audio_response != "") {
            Serial.println("🔊 تم استلام صوت الرد من AI");
            // هنا يمكن تشغيل الصوت من base64
            play_ai_audio(audio_response);
        }
        
        // وميض LED للإشارة للنجاح
        for (int i = 0; i < 3; i++) {
            digitalWrite(LED_PIN, LOW);
            delay(200);
            digitalWrite(LED_PIN, HIGH);
            delay(200);
        }
        
    } else {
        Serial.println("❌ خطأ من AI: " + doc["message"].as<String>());
    }
}

// 🔊 تشغيل صوت AI (محاكاة)
void play_ai_audio(String base64_audio) {
    Serial.println("🔊 تشغيل رد صوتي من دبدوب AI...");
    
    // في التطبيق الحقيقي:
    // 1. فك تشفير base64
    // 2. تشغيل الصوت عبر DAC أو I2S
    
    // محاكاة تشغيل لمدة 3 ثواني
    for (int i = 0; i < 30; i++) {
        digitalWrite(LED_PIN, i % 2); // وميض أثناء التشغيل
        delay(100);
    }
    
    digitalWrite(LED_PIN, HIGH); // انتهاء التشغيل
    Serial.println("✅ انتهى تشغيل الصوت");
}

// 💓 إرسال نبضة حياة (اختياري)
void send_heartbeat() {
    HTTPClient http;
    http.begin(String(server_url) + "/esp32/heartbeat");
    http.addHeader("Content-Type", "application/json");
    
    DynamicJsonDocument doc(512);
    doc["device_id"] = device_id;
    doc["status"] = "online";
    doc["battery_level"] = 85;      // إذا كان يعمل بالبطارية
    doc["uptime_seconds"] = millis() / 1000;
    doc["volume_level"] = 50;
    doc["timestamp"] = String(millis());
    
    String payload;
    serializeJson(doc, payload);
    
    int httpResponseCode = http.POST(payload);
    
    if (httpResponseCode == 200) {
        Serial.println("💓 نبضة حياة مُرسلة");
    }
    
    http.end();
} 