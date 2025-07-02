/*
🧸 AI Teddy Bear - ESP32 Code for Render.com
تم تحسينه للعمل مع Render.com cloud server
*/

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// إعدادات WiFi
const char* ssid = "YOUR_WIFI_NAME";
const char* password = "YOUR_WIFI_PASSWORD";

// إعدادات Render.com server
const char* render_url = "https://ai-teddy-bear-abc123.onrender.com";  // ضع URL خادمك
const char* device_id = "teddy_001";

// GPIO pins
const int buttonPin = 0;    // زر للاختبار
const int ledPin = 2;       // LED للحالة

void setup() {
    Serial.begin(115200);
    
    // إعداد GPIO
    pinMode(buttonPin, INPUT_PULLUP);
    pinMode(ledPin, OUTPUT);
    
    // إشارة بداية التشغيل
    blinkLED(3);
    
    // الاتصال بـ WiFi
    connectToWiFi();
    
    // اختبار الاتصال بالخادم
    testServerConnection();
    
    Serial.println("🧸 AI Teddy Bear ready!");
}

void loop() {
    // قراءة حالة الزر
    if (digitalRead(buttonPin) == LOW) {
        Serial.println("🔘 Button pressed - testing connection...");
        testServerConnection();
        sendTestMessage();
        delay(1000); // منع الضغط المتكرر
    }
    
    // إرسال heartbeat كل 30 ثانية
    static unsigned long lastHeartbeat = 0;
    if (millis() - lastHeartbeat > 30000) {
        sendHeartbeat();
        lastHeartbeat = millis();
    }
    
    delay(100);
}

void connectToWiFi() {
    Serial.print("🌐 Connecting to WiFi: ");
    Serial.println(ssid);
    
    WiFi.begin(ssid, password);
    
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 20) {
        delay(1000);
        Serial.print(".");
        attempts++;
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\n✅ WiFi connected!");
        Serial.print("📱 ESP32 IP: ");
        Serial.println(WiFi.localIP());
        digitalWrite(ledPin, HIGH); // LED on when connected
    } else {
        Serial.println("\n❌ WiFi connection failed!");
    }
}

void testServerConnection() {
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("❌ No WiFi connection");
        return;
    }
    
    HTTPClient http;
    String url = String(render_url) + "/esp32/connect";
    
    Serial.println("🔗 Testing connection to: " + url);
    
    http.begin(url);
    http.setTimeout(10000); // 10 second timeout
    
    int httpCode = http.GET();
    
    if (httpCode == 200) {
        String response = http.getString();
        Serial.println("✅ Connection successful!");
        Serial.println("📥 Response: " + response);
        
        // Parse JSON response
        DynamicJsonDocument doc(1024);
        deserializeJson(doc, response);
        
        if (doc["message"]) {
            Serial.println("🧸 Server says: " + String((const char*)doc["message"]));
        }
        
        blinkLED(2); // Success blink
        
    } else if (httpCode == -1) {
        Serial.println("❌ Connection timeout - server might be sleeping");
        Serial.println("⏳ Render.com free plan sleeps after 15min inactivity");
        Serial.println("🔄 Trying again to wake up server...");
        
        // Try again to wake up the server
        delay(2000);
        int retryCode = http.GET();
        if (retryCode == 200) {
            Serial.println("✅ Server woke up successfully!");
        }
        
    } else {
        Serial.println("❌ HTTP Error: " + String(httpCode));
        Serial.println("📄 Response: " + http.getString());
    }
    
    http.end();
}

void sendTestMessage() {
    HTTPClient http;
    String url = String(render_url) + "/api/audio/upload";
    
    http.begin(url);
    http.addHeader("Content-Type", "application/x-www-form-urlencoded");
    
    // إرسال رسالة نصية للاختبار
    String postData = "device_id=" + String(device_id) + "&text_message=Hello from ESP32!";
    
    Serial.println("📤 Sending test message...");
    
    int httpCode = http.POST(postData);
    
    if (httpCode == 200) {
        String response = http.getString();
        Serial.println("✅ Message sent successfully!");
        
        // Parse AI response
        DynamicJsonDocument doc(2048);
        deserializeJson(doc, response);
        
        if (doc["ai_response"]["text"]) {
            Serial.println("🤖 AI Response: " + String((const char*)doc["ai_response"]["text"]));
        }
        
        blinkLED(5); // Success blink
        
    } else {
        Serial.println("❌ Failed to send message: " + String(httpCode));
    }
    
    http.end();
}

void sendHeartbeat() {
    HTTPClient http;
    String url = String(render_url) + "/esp32/status";
    
    http.begin(url);
    http.addHeader("Content-Type", "application/json");
    
    // إنشاء JSON للحالة
    DynamicJsonDocument doc(512);
    doc["device_id"] = device_id;
    doc["status"] = "active";
    doc["last_seen"] = "2025-01-01T12:00:00Z"; // في التطبيق الحقيقي، استخدم RTC
    doc["battery_level"] = 85;
    doc["wifi_strength"] = WiFi.RSSI();
    
    String jsonString;
    serializeJson(doc, jsonString);
    
    int httpCode = http.POST(jsonString);
    
    if (httpCode == 200) {
        Serial.println("💗 Heartbeat sent");
    } else {
        Serial.println("💔 Heartbeat failed: " + String(httpCode));
    }
    
    http.end();
}

void blinkLED(int times) {
    for (int i = 0; i < times; i++) {
        digitalWrite(ledPin, HIGH);
        delay(200);
        digitalWrite(ledPin, LOW);
        delay(200);
    }
}

// دالة للتعامل مع انقطاع الشبكة
void checkWiFiConnection() {
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("🔄 WiFi disconnected, reconnecting...");
        digitalWrite(ledPin, LOW);
        connectToWiFi();
    }
} 