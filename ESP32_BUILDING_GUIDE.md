# 🎛️ دليل بناء ESP32 للدب الذكي - خطوة بخطوة

## 📋 نظرة عامة على أجزاء ESP32

### 🔢 الترتيب المقترح للبناء:

1. **🏁 المستوى الأساسي** - اتصال WiFi واختبار LED
2. **🎤 المستوى الثاني** - تسجيل الصوت الأساسي  
3. **🌐 المستوى الثالث** - اتصال بالسيرفر
4. **🔊 المستوى الرابع** - تشغيل الصوت
5. **⚡ المستوى النهائي** - النظام الكامل المتقدم

---

## 🏁 المستوى الأول: الأساسيات

### 📁 الملفات المطلوبة:
```
esp32/
├── 01_basic_wifi_test.ino     # اختبار اتصال WiFi فقط
└── 02_led_control_test.ino    # اختبار الأضواء فقط
```

### 🔧 المكونات المطلوبة:
- **ESP32 DevKit** (أساسي)
- **LED Strip WS2812B** (8 LEDs)
- **3 أزرار** (Pull-up)
- **أسلاك توصيل**

### 📝 الكود الأساسي:

#### ملف: `01_basic_wifi_test.ino`
```cpp
#include <WiFi.h>

// إعدادات WiFi (غيّرها حسب شبكتك)
const char* ssid = "YOUR_WIFI_NAME";
const char* password = "YOUR_WIFI_PASSWORD";

void setup() {
    Serial.begin(115200);
    Serial.println("🧸 اختبار اتصال WiFi...");
    
    // بدء اتصال WiFi
    WiFi.begin(ssid, password);
    
    // انتظار الاتصال
    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.print(".");
    }
    
    // نجح الاتصال
    Serial.println("\n✅ WiFi متصل!");
    Serial.print("📍 عنوان IP: ");
    Serial.println(WiFi.localIP());
    Serial.print("📶 قوة الإشارة: ");
    Serial.println(WiFi.RSSI());
}

void loop() {
    // فحص الاتصال كل 10 ثوان
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("💚 الاتصال مازال قوي");
    } else {
        Serial.println("❌ انقطع الاتصال - محاولة إعادة الاتصال");
        WiFi.begin(ssid, password);
    }
    
    delay(10000);
}
```

#### ملف: `02_led_control_test.ino`
```cpp
#include <FastLED.h>

// إعدادات LEDs
#define LED_PIN 2
#define NUM_LEDS 8
CRGB leds[NUM_LEDS];

// إعدادات الأزرار
#define BUTTON_1 4   // زر تغيير اللون
#define BUTTON_2 5   // زر السطوع
#define BUTTON_3 18  // زر إيقاف/تشغيل

// متغيرات التحكم
int current_color = 0;
int brightness = 100;
bool lights_on = true;

void setup() {
    Serial.begin(115200);
    Serial.println("🧸 اختبار أضواء LED...");
    
    // إعداد الأزرار
    pinMode(BUTTON_1, INPUT_PULLUP);
    pinMode(BUTTON_2, INPUT_PULLUP);
    pinMode(BUTTON_3, INPUT_PULLUP);
    
    // إعداد LEDs
    FastLED.addLeds<WS2812B, LED_PIN, GRB>(leds, NUM_LEDS);
    FastLED.setBrightness(brightness);
    
    // عرض ترحيبي
    startup_animation();
}

void loop() {
    // فحص الأزرار
    handle_buttons();
    
    // تحديث الأضواء
    update_lights();
    
    delay(50);
}

void startup_animation() {
    Serial.println("🌈 عرض ترحيبي...");
    
    // إضاءة تدريجية
    for(int i = 0; i < NUM_LEDS; i++) {
        leds[i] = CRGB::Blue;
        FastLED.show();
        delay(200);
    }
    
    delay(500);
    
    // إطفاء تدريجي
    for(int i = NUM_LEDS-1; i >= 0; i--) {
        leds[i] = CRGB::Black;
        FastLED.show();
        delay(200);
    }
    
    Serial.println("✅ اختبار LEDs مكتمل");
}

void handle_buttons() {
    static bool last_btn1 = HIGH, last_btn2 = HIGH, last_btn3 = HIGH;
    
    bool btn1 = digitalRead(BUTTON_1);
    bool btn2 = digitalRead(BUTTON_2);
    bool btn3 = digitalRead(BUTTON_3);
    
    // زر تغيير اللون
    if (last_btn1 == HIGH && btn1 == LOW) {
        current_color = (current_color + 1) % 7;
        Serial.println("🎨 تغيير اللون: " + String(current_color));
    }
    
    // زر السطوع
    if (last_btn2 == HIGH && btn2 == LOW) {
        brightness += 50;
        if (brightness > 255) brightness = 50;
        FastLED.setBrightness(brightness);
        Serial.println("💡 السطوع: " + String(brightness));
    }
    
    // زر إيقاف/تشغيل
    if (last_btn3 == HIGH && btn3 == LOW) {
        lights_on = !lights_on;
        Serial.println(lights_on ? "🟢 تشغيل الأضواء" : "🔴 إطفاء الأضواء");
    }
    
    last_btn1 = btn1;
    last_btn2 = btn2;
    last_btn3 = btn3;
}

void update_lights() {
    if (!lights_on) {
        fill_solid(leds, NUM_LEDS, CRGB::Black);
        FastLED.show();
        return;
    }
    
    CRGB colors[] = {
        CRGB::Red, CRGB::Green, CRGB::Blue, 
        CRGB::Yellow, CRGB::Purple, CRGB::Cyan, CRGB::White
    };
    
    fill_solid(leds, NUM_LEDS, colors[current_color]);
    FastLED.show();
}

### ✅ اختبار المستوى الأول:
1. رفع `01_basic_wifi_test.ino` - تأكد من اتصال WiFi
2. رفع `02_led_control_test.ino` - تأكد من عمل الأضواء والأزرار

---

## 🎤 المستوى الثاني: تسجيل الصوت

### 📁 الملفات المطلوبة:
```
esp32/
├── 03_microphone_test.ino     # اختبار المايكروفون
└── audio_processor_basic.h    # معالج صوت مبسط
```

### 🔧 المكونات الإضافية:
- **I2S MEMS Microphone** (مثل INMP441)
- **أسلاك I2S** (3 أسلاك: SCK, WS, SD)

### 📝 الكود:

#### ملف: `audio_processor_basic.h`
```cpp
#ifndef AUDIO_PROCESSOR_BASIC_H
#define AUDIO_PROCESSOR_BASIC_H

#include <driver/i2s.h>

// إعدادات I2S للمايكروفون
#define I2S_WS 25
#define I2S_SD 33
#define I2S_SCK 32
#define SAMPLE_RATE 16000
#define SAMPLE_BITS 16

class BasicAudioProcessor {
private:
    static const int buffer_size = 1024;
    int16_t audio_buffer[buffer_size];
    
public:
    bool initialize() {
        // إعداد I2S
        i2s_config_t i2s_config = {
            .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
            .sample_rate = SAMPLE_RATE,
            .bits_per_sample = (i2s_bits_per_sample_t)SAMPLE_BITS,
            .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
            .communication_format = I2S_COMM_FORMAT_STAND_I2S,
            .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
            .dma_buf_count = 4,
            .dma_buf_len = buffer_size
        };
        
        i2s_pin_config_t pin_config = {
            .bck_io_num = I2S_SCK,
            .ws_io_num = I2S_WS,
            .data_out_num = I2S_PIN_NO_CHANGE,
            .data_in_num = I2S_SD
        };
        
        if (i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL) != ESP_OK) {
            return false;
        }
        
        if (i2s_set_pin(I2S_NUM_0, &pin_config) != ESP_OK) {
            return false;
        }
        
        return true;
    }
    
    bool record_sample() {
        size_t bytes_read;
        esp_err_t result = i2s_read(I2S_NUM_0, audio_buffer, 
                                   buffer_size * sizeof(int16_t), 
                                   &bytes_read, portMAX_DELAY);
        
        if (result == ESP_OK && bytes_read > 0) {
            // حساب مستوى الصوت (Volume Level)
            int32_t sum = 0;
            int samples = bytes_read / sizeof(int16_t);
            
            for (int i = 0; i < samples; i++) {
                sum += abs(audio_buffer[i]);
            }
            
            int volume_level = sum / samples;
            Serial.println("🎤 مستوى الصوت: " + String(volume_level));
            
            return volume_level > 1000; // إذا كان هناك صوت قوي
        }
        
        return false;
    }
    
    void cleanup() {
        i2s_driver_uninstall(I2S_NUM_0);
    }
};

#endif
```

#### ملف: `03_microphone_test.ino`
```cpp
#include "audio_processor_basic.h"
#include <FastLED.h>

// LEDs للمؤشرات
#define LED_PIN 2
#define NUM_LEDS 8
CRGB leds[NUM_LEDS];

// الصوت
BasicAudioProcessor audio;

// أزرار
#define RECORD_BUTTON 4

void setup() {
    Serial.begin(115200);
    Serial.println("🧸 اختبار المايكروفون...");
    
    // إعداد الأزرار
    pinMode(RECORD_BUTTON, INPUT_PULLUP);
    
    // إعداد LEDs
    FastLED.addLeds<WS2812B, LED_PIN, GRB>(leds, NUM_LEDS);
    FastLED.setBrightness(100);
    
    // إعداد الصوت
    if (audio.initialize()) {
        Serial.println("✅ المايكروفون جاهز");
        show_status(CRGB::Green);
    } else {
        Serial.println("❌ خطأ في إعداد المايكروفون");
        show_status(CRGB::Red);
        while(1); // توقف هنا
    }
}

void loop() {
    static bool recording = false;
    static bool last_button = HIGH;
    
    bool button = digitalRead(RECORD_BUTTON);
    
    // بدء/إيقاف التسجيل عند الضغط
    if (last_button == HIGH && button == LOW) {
        recording = !recording;
        
        if (recording) {
            Serial.println("🎤 بدء التسجيل...");
            show_status(CRGB::Red);
        } else {
            Serial.println("🛑 إيقاف التسجيل");
            show_status(CRGB::Green);
        }
    }
    
    last_button = button;
    
    // التسجيل المستمر إذا كان مفعلاً
    if (recording) {
        bool voice_detected = audio.record_sample();
        
        if (voice_detected) {
            // وميض أزرق عند اكتشاف صوت
            show_voice_activity();
        }
    }
    
    delay(10);
}

void show_status(CRGB color) {
    fill_solid(leds, NUM_LEDS, color);
    FastLED.show();
}

void show_voice_activity() {
    // وميض سريع أزرق
    fill_solid(leds, NUM_LEDS, CRGB::Blue);
    FastLED.show();
    delay(50);
    fill_solid(leds, NUM_LEDS, CRGB::Red); // العودة للأحمر (تسجيل)
    FastLED.show();
}

### ✅ اختبار المستوى الثاني:
1. تأكد من توصيل المايكروفون صحيحاً
2. رفع الكود واختبر بالضغط على الزر
3. تحدث وشاهد مستوى الصوت في Serial Monitor

---

## 🌐 المستوى الثالث: اتصال بالسيرفر

### 📁 الملفات المطلوبة:
```
esp32/
├── 04_server_connection_test.ino  # اختبار اتصال السيرفر
└── network_manager.h               # مدير الشبكة
```

### 📝 الكود:

#### ملف: `network_manager.h`
```cpp
#ifndef NETWORK_MANAGER_H
#define NETWORK_MANAGER_H

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

class NetworkManager {
private:
    String server_url;
    String device_id;
    
public:
    NetworkManager(String url) : server_url(url) {
        device_id = WiFi.macAddress();
    }
    
    bool test_server_connection() {
        if (WiFi.status() != WL_CONNECTED) {
            Serial.println("❌ WiFi غير متصل");
            return false;
        }
        
        HTTPClient http;
        http.begin(server_url + "/health");
        http.setTimeout(5000);
        
        int httpCode = http.GET();
        
        if (httpCode == 200) {
            String response = http.getString();
            Serial.println("✅ السيرفر يعمل: " + response);
            http.end();
            return true;
        } else {
            Serial.println("❌ خطأ اتصال بالسيرفر: " + String(httpCode));
            http.end();
            return false;
        }
    }
    
    bool send_heartbeat() {
        HTTPClient http;
        http.begin(server_url + "/teddy/heartbeat");
        http.addHeader("Content-Type", "application/json");
        
        StaticJsonDocument<300> doc;
        doc["device_id"] = device_id;
        doc["status"] = "online";
        doc["wifi_strength"] = WiFi.RSSI();
        doc["uptime"] = millis();
        
        String payload;
        serializeJson(doc, payload);
        
        int httpCode = http.POST(payload);
        
        if (httpCode == 200) {
            Serial.println("💓 Heartbeat مرسل بنجاح");
            http.end();
            return true;
        } else {
            Serial.println("❌ فشل إرسال Heartbeat: " + String(httpCode));
            http.end();
            return false;
        }
    }
    
    bool send_test_message(String message) {
        HTTPClient http;
        http.begin(server_url + "/teddy/test-message");
        http.addHeader("Content-Type", "application/json");
        
        StaticJsonDocument<500> doc;
        doc["device_id"] = device_id;
        doc["message"] = message;
        doc["timestamp"] = millis();
        
        String payload;
        serializeJson(doc, payload);
        
        Serial.println("📤 إرسال رسالة: " + payload);
        
        int httpCode = http.POST(payload);
        
        if (httpCode == 200) {
            String response = http.getString();
            Serial.println("📥 رد السيرفر: " + response);
            http.end();
            return true;
        } else {
            Serial.println("❌ خطأ إرسال: " + String(httpCode));
            http.end();
            return false;
        }
    }
};

#endif
```

#### ملف: `04_server_connection_test.ino`
```cpp
#include <WiFi.h>
#include <FastLED.h>
#include "network_manager.h"

// WiFi
const char* ssid = "YOUR_WIFI_NAME";
const char* password = "YOUR_WIFI_PASSWORD";

// السيرفر (غيّر هذا لرابط سيرفرك)
const char* server_url = "http://your-server.com:8000";

// LEDs
#define LED_PIN 2
#define NUM_LEDS 8
CRGB leds[NUM_LEDS];

// الشبكة
NetworkManager network(server_url);

// أزرار
#define TEST_BUTTON 4

void setup() {
    Serial.begin(115200);
    Serial.println("🧸 اختبار اتصال السيرفر...");
    
    // إعداد LEDs
    FastLED.addLeds<WS2812B, LED_PIN, GRB>(leds, NUM_LEDS);
    FastLED.setBrightness(100);
    show_status(CRGB::Yellow); // اتصال...
    
    // إعداد الأزرار
    pinMode(TEST_BUTTON, INPUT_PULLUP);
    
    // اتصال WiFi
    connect_wifi();
    
    // اختبار السيرفر
    if (network.test_server_connection()) {
        show_status(CRGB::Green);
        Serial.println("✅ جاهز للاختبار - اضغط الزر لإرسال رسالة");
    } else {
        show_status(CRGB::Red);
        Serial.println("❌ تأكد من تشغيل السيرفر على: " + String(server_url));
    }
}

void loop() {
    static bool last_button = HIGH;
    static unsigned long last_heartbeat = 0;
    
    bool button = digitalRead(TEST_BUTTON);
    
    // إرسال رسالة اختبار عند الضغط
    if (last_button == HIGH && button == LOW) {
        Serial.println("🧪 إرسال رسالة اختبار...");
        show_status(CRGB::Blue);
        
        if (network.send_test_message("مرحباً من الدب الذكي!")) {
            show_status(CRGB::Green);
        } else {
            show_status(CRGB::Red);
        }
    }
    
    last_button = button;
    
    // إرسال heartbeat كل 30 ثانية
    if (millis() - last_heartbeat > 30000) {
        Serial.println("💓 إرسال heartbeat...");
        network.send_heartbeat();
        last_heartbeat = millis();
    }
    
    delay(100);
}

void connect_wifi() {
    WiFi.begin(ssid, password);
    Serial.print("🔄 اتصال WiFi");
    
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    
    Serial.println("\n✅ WiFi متصل!");
    Serial.println("📍 IP: " + WiFi.localIP().toString());
    Serial.println("📱 Device ID: " + WiFi.macAddress());
}

void show_status(CRGB color) {
    fill_solid(leds, NUM_LEDS, color);
    FastLED.show();
}

### ✅ اختبار المستوى الثالث:
1. تأكد من تشغيل السيرفر أولاً
2. حدّث رابط السيرفر في الكود
3. رفع الكود واختبر الاتصال

---

## 🔊 المستوى الرابع: تشغيل الصوت

### 📁 الملفات المطلوبة:
```
esp32/
├── 05_speaker_test.ino        # اختبار السماعة
└── audio_player_basic.h       # مشغل صوت أساسي
```

### 🔧 المكونات الإضافية:
- **I2S Amplifier** (مثل MAX98357A)
- **Speaker** 4-8 Ohm
- **أسلاك I2S إضافية** للسماعة

### 📝 الكود:

#### ملف: `audio_player_basic.h`
```cpp
#ifndef AUDIO_PLAYER_BASIC_H
#define AUDIO_PLAYER_BASIC_H

#include <driver/i2s.h>

class BasicAudioPlayer {
private:
    static const int sample_rate = 16000;
    
public:
    bool initialize() {
        // إعداد I2S للسماعة
        i2s_config_t i2s_config = {
            .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_TX),
            .sample_rate = sample_rate,
            .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
            .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
            .communication_format = I2S_COMM_FORMAT_STAND_I2S,
            .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
            .dma_buf_count = 4,
            .dma_buf_len = 1024
        };
        
        i2s_pin_config_t pin_config = {
            .bck_io_num = 26,    // BCK
            .ws_io_num = 25,     // LRCK
            .data_out_num = 22,  // DIN
            .data_in_num = I2S_PIN_NO_CHANGE
        };
        
        if (i2s_driver_install(I2S_NUM_1, &i2s_config, 0, NULL) != ESP_OK) {
            return false;
        }
        
        if (i2s_set_pin(I2S_NUM_1, &pin_config) != ESP_OK) {
            return false;
        }
        
        return true;
    }
    
    void play_tone(int frequency, int duration_ms) {
        const int samples_per_cycle = sample_rate / frequency;
        const int total_samples = (sample_rate * duration_ms) / 1000;
        
        int16_t wave[samples_per_cycle];
        
        // توليد موجة صوتية بسيطة
        for (int i = 0; i < samples_per_cycle; i++) {
            wave[i] = (int16_t)(sin(2 * PI * i / samples_per_cycle) * 10000);
        }
        
        // تشغيل الصوت
        for (int i = 0; i < total_samples; i += samples_per_cycle) {
            size_t bytes_written;
            i2s_write(I2S_NUM_1, wave, samples_per_cycle * sizeof(int16_t), 
                     &bytes_written, portMAX_DELAY);
        }
    }
    
    void play_startup_sound() {
        Serial.println("🔊 تشغيل صوت البداية...");
        
        // نغمات ترحيبية
        play_tone(440, 200);  // La
        play_tone(523, 200);  // Do
        play_tone(659, 200);  // Mi
        play_tone(784, 400);  // Sol
        
        Serial.println("✅ انتهى صوت البداية");
    }
    
    void play_success_sound() {
        Serial.println("🔊 صوت نجاح...");
        play_tone(659, 150);  // Mi
        play_tone(784, 150);  // Sol
        play_tone(988, 300);  // Si
    }
    
    void play_error_sound() {
        Serial.println("🔊 صوت خطأ...");
        play_tone(200, 500);  // نغمة منخفضة
    }
    
    void cleanup() {
        i2s_driver_uninstall(I2S_NUM_1);
    }
};

#endif
```

#### ملف: `05_speaker_test.ino`
```cpp
#include <FastLED.h>
#include "audio_player_basic.h"

// LEDs
#define LED_PIN 2
#define NUM_LEDS 8
CRGB leds[NUM_LEDS];

// الصوت
BasicAudioPlayer audio_player;

// أزرار
#define PLAY_BUTTON 4
#define TONE_BUTTON 5

void setup() {
    Serial.begin(115200);
    Serial.println("🧸 اختبار السماعة...");
    
    // إعداد LEDs
    FastLED.addLeds<WS2812B, LED_PIN, GRB>(leds, NUM_LEDS);
    FastLED.setBrightness(100);
    
    // إعداد الأزرار
    pinMode(PLAY_BUTTON, INPUT_PULLUP);
    pinMode(TONE_BUTTON, INPUT_PULLUP);
    
    // إعداد السماعة
    if (audio_player.initialize()) {
        Serial.println("✅ السماعة جاهزة");
        show_status(CRGB::Green);
        
        // تشغيل صوت ترحيبي
        audio_player.play_startup_sound();
    } else {
        Serial.println("❌ خطأ في إعداد السماعة");
        show_status(CRGB::Red);
        while(1);
    }
    
    Serial.println("🎵 اضغط الأزرار لاختبار الأصوات");
}

void loop() {
    static bool last_play_btn = HIGH, last_tone_btn = HIGH;
    
    bool play_btn = digitalRead(PLAY_BUTTON);
    bool tone_btn = digitalRead(TONE_BUTTON);
    
    // زر تشغيل نغمة ترحيبية
    if (last_play_btn == HIGH && play_btn == LOW) {
        Serial.println("🎵 تشغيل نغمة ترحيبية...");
        show_status(CRGB::Purple);
        audio_player.play_startup_sound();
        show_status(CRGB::Green);
    }
    
    // زر تشغيل نغمات متنوعة
    if (last_tone_btn == HIGH && tone_btn == LOW) {
        Serial.println("🎵 تشغيل نغمات متنوعة...");
        show_status(CRGB::Blue);
        
        // نغمات متنوعة
        int frequencies[] = {262, 294, 330, 349, 392, 440, 494, 523};
        for (int i = 0; i < 8; i++) {
            audio_player.play_tone(frequencies[i], 200);
            
            // إضاءة LED مطابقة
            fill_solid(leds, NUM_LEDS, CRGB::Black);
            leds[i] = CRGB::Red;
            FastLED.show();
        }
        
        show_status(CRGB::Green);
    }
    
    last_play_btn = play_btn;
    last_tone_btn = tone_btn;
    
    delay(50);
}

void show_status(CRGB color) {
    fill_solid(leds, NUM_LEDS, color);
    FastLED.show();
}

### ✅ اختبار المستوى الرابع:
1. تأكد من توصيل I2S amplifier والسماعة
2. رفع الكود واختبر النغمات
3. تأكد من سماع الأصوات بوضوح

---

## ⚡ المستوى النهائي: النظام الكامل

### 📁 الملف النهائي:
```
esp32/
└── teddy_complete_system.ino   # النظام الكامل المدمج
```

### 📝 الكود النهائي:
```cpp
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <FastLED.h>
#include "audio_processor_basic.h"
#include "audio_player_basic.h"
#include "network_manager.h"

// إعدادات الشبكة
const char* ssid = "YOUR_WIFI_NAME";
const char* password = "YOUR_WIFI_PASSWORD";
const char* server_url = "http://your-server.com:8000";

// إعدادات الأجهزة
#define LED_PIN 2
#define NUM_LEDS 8
CRGB leds[NUM_LEDS];

#define TALK_BUTTON 4
#define VOLUME_UP 5
#define VOLUME_DOWN 18

// الكائنات الرئيسية
BasicAudioProcessor microphone;
BasicAudioPlayer speaker;
NetworkManager network(server_url);

// متغيرات النظام
bool is_recording = false;
bool is_connected = false;
int volume_level = 70;

void setup() {
    Serial.begin(115200);
    Serial.println("🧸 بدء نظام الدب الذكي الكامل...");
    
    // إعداد الأجهزة
    setup_hardware();
    
    // اتصال الشبكة
    connect_to_network();
    
    // إعداد الصوت
    setup_audio();
    
    // اختبار النظام
    system_test();
    
    Serial.println("✅ النظام جاهز للاستخدام!");
    show_ready_status();
}

void loop() {
    // فحص الأزرار
    handle_buttons();
    
    // إدارة التسجيل
    handle_recording();
    
    // فحص الاتصال
    check_connection();
    
    delay(10);
}

void setup_hardware() {
    // إعداد الأزرار
    pinMode(TALK_BUTTON, INPUT_PULLUP);
    pinMode(VOLUME_UP, INPUT_PULLUP);
    pinMode(VOLUME_DOWN, INPUT_PULLUP);
    
    // إعداد LEDs
    FastLED.addLeds<WS2812B, LED_PIN, GRB>(leds, NUM_LEDS);
    FastLED.setBrightness(100);
    show_status(CRGB::Yellow);
    
    Serial.println("✅ الأجهزة جاهزة");
}

void connect_to_network() {
    WiFi.begin(ssid, password);
    show_status(CRGB::Blue);
    
    Serial.print("🔄 اتصال WiFi");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    
    Serial.println("\n✅ WiFi متصل!");
    
    if (network.test_server_connection()) {
        is_connected = true;
        Serial.println("✅ السيرفر متصل!");
    } else {
        Serial.println("⚠️ السيرفر غير متاح - العمل في وضع أوفلاين");
        is_connected = false;
    }
}

void setup_audio() {
    Serial.println("🎤 إعداد نظام الصوت...");
    
    if (!microphone.initialize()) {
        Serial.println("❌ خطأ في المايكروفون");
        show_status(CRGB::Red);
        return;
    }
    
    if (!speaker.initialize()) {
        Serial.println("❌ خطأ في السماعة");
        show_status(CRGB::Red);
        return;
    }
    
    Serial.println("✅ نظام الصوت جاهز");
}

void system_test() {
    Serial.println("🧪 اختبار النظام...");
    
    // صوت البداية
    speaker.play_startup_sound();
    
    // اختبار الأضواء
    for (int i = 0; i < NUM_LEDS; i++) {
        fill_solid(leds, NUM_LEDS, CRGB::Black);
        leds[i] = CRGB::Green;
        FastLED.show();
        delay(100);
    }
    
    Serial.println("✅ اختبار النظام مكتمل");
}

void handle_buttons() {
    static bool last_talk = HIGH, last_vol_up = HIGH, last_vol_down = HIGH;
    
    bool talk = digitalRead(TALK_BUTTON);
    bool vol_up = digitalRead(VOLUME_UP);
    bool vol_down = digitalRead(VOLUME_DOWN);
    
    // زر التحدث
    if (last_talk == HIGH && talk == LOW) {
        start_conversation();
    } else if (last_talk == LOW && talk == HIGH) {
        stop_conversation();
    }
    
    // أزرار الصوت
    if (last_vol_up == HIGH && vol_up == LOW) {
        volume_level = min(100, volume_level + 10);
        Serial.println("🔊 مستوى الصوت: " + String(volume_level));
        speaker.play_success_sound();
    }
    
    if (last_vol_down == HIGH && vol_down == LOW) {
        volume_level = max(10, volume_level - 10);
        Serial.println("🔉 مستوى الصوت: " + String(volume_level));
        speaker.play_success_sound();
    }
    
    last_talk = talk;
    last_vol_up = vol_up;
    last_vol_down = vol_down;
}

void start_conversation() {
    if (!is_recording) {
        Serial.println("🎤 بدء المحادثة...");
        is_recording = true;
        show_status(CRGB::Red);
    }
}

void stop_conversation() {
    if (is_recording) {
        Serial.println("🛑 إنهاء المحادثة...");
        is_recording = false;
        
        if (is_connected) {
            process_conversation();
        } else {
            offline_response();
        }
    }
}

void handle_recording() {
    if (is_recording) {
        bool voice_detected = microphone.record_sample();
        
        if (voice_detected) {
            // وميض عند اكتشاف صوت
            leds[0] = CRGB::Blue;
            FastLED.show();
            delay(50);
            leds[0] = CRGB::Red;
            FastLED.show();
        }
    }
}

void process_conversation() {
    Serial.println("☁️ معالجة المحادثة مع السيرفر...");
    show_status(CRGB::Purple);
    
    // في التطبيق الحقيقي، ستُرسل البيانات الصوتية هنا
    if (network.send_test_message("طلب معالجة صوت")) {
        Serial.println("🗣️ تشغيل رد الدب...");
        speaker.play_success_sound();
        show_status(CRGB::Green);
    } else {
        Serial.println("❌ خطأ في الاتصال");
        speaker.play_error_sound();
        show_status(CRGB::Red);
    }
}

void offline_response() {
    Serial.println("🤖 رد أوفلاين...");
    show_status(CRGB::Orange);
    
    // رد بسيط في حالة عدم الاتصال
    speaker.play_tone(440, 200);
    speaker.play_tone(523, 200);
    speaker.play_tone(659, 400);
    
    show_status(CRGB::Yellow);
}

void check_connection() {
    static unsigned long last_check = 0;
    
    if (millis() - last_check > 30000) { // كل 30 ثانية
        if (WiFi.status() == WL_CONNECTED) {
            if (network.send_heartbeat()) {
                is_connected = true;
            } else {
                is_connected = false;
            }
        } else {
            is_connected = false;
        }
        
        last_check = millis();
    }
}

void show_status(CRGB color) {
    fill_solid(leds, NUM_LEDS, color);
    FastLED.show();
}

void show_ready_status() {
    // عرض حالة الجاهزية
    for (int i = 0; i < 3; i++) {
        show_status(CRGB::Green);
        delay(200);
        show_status(CRGB::Black);
        delay(200);
    }
    show_status(CRGB::Green);
}

### ✅ اختبار النظام النهائي:
1. تأكد من جميع المكونات متصلة
2. حدّث إعدادات WiFi والسيرفر
3. رفع الكود الكامل
4. اختبر جميع الوظائف

---

## 📋 ملخص خطوات البناء

### ✅ Checklist كامل:

#### 🔧 الأجهزة:
- [ ] ESP32 DevKit
- [ ] WS2812B LED Strip (8 LEDs)
- [ ] 3 أزرار (Pull-up)
- [ ] I2S MEMS Microphone (INMP441)
- [ ] I2S Amplifier (MAX98357A)
- [ ] Speaker 4-8 Ohm
- [ ] أسلاك توصيل كافية

#### 💻 البرمجيات:
- [ ] Arduino IDE مثبت
- [ ] ESP32 board package مثبت
- [ ] مكتبات: WiFi, HTTPClient, ArduinoJson, FastLED

#### 🏗️ البناء:
- [ ] **المستوى 1**: WiFi + LEDs → ✅
- [ ] **المستوى 2**: Microphone → ✅
- [ ] **المستوى 3**: Server Connection → ✅
- [ ] **المستوى 4**: Speaker → ✅
- [ ] **المستوى 5**: Complete System → ✅

---

## 🆘 استكشاف الأخطاء

### ❌ المشاكل الشائعة:

**WiFi لا يتصل:**
- تأكد من SSID وكلمة المرور
- تأكد من قوة الإشارة
- جرب إعادة تشغيل ESP32

**المايكروفون لا يعمل:**
- تأكد من توصيل I2S صحيح (SCK, WS, SD)
- تأكد من power 3.3V
- اختبر مع كود بسيط أولاً

**السماعة لا تعمل:**
- تأكد من توصيل I2S Amplifier
- تأكد من توصيل السماعة للAmplifier
- اختبر بنغمات بسيطة

**السيرفر لا يرد:**
- تأكد من تشغيل السيرفر أولاً
- تأكد من الـ URL صحيح
- اختبر بمتصفح: `http://server:8000/health`

هذا الدليل يسمح لك ببناء ESP32 خطوة بخطوة بهدوء تام! 🎯