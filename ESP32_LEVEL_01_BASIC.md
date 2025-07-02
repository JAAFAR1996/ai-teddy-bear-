# 🏁 ESP32 المستوى الأول: الأساسيات

## 🎯 الهدف من هذا المستوى
- اختبار ESP32 أساسي
- اتصال WiFi
- تحكم في LEDs
- قراءة الأزرار

## 🔧 المكونات المطلوبة

### الأساسي:
- **ESP32 DevKit** (أي نوع)
- **3 أزرار** (Push buttons)
- **مقاومات 10kΩ** (للأزرار)
- **أسلاك توصيل**

### الإضافي (للأضواء):
- **LED Strip WS2812B** (8 LEDs)
- **مكثف 1000µF** (للحماية)
- **مقاومة 330Ω** (للحماية)

## 📐 المخطط الكهربائي

```
ESP32 DevKit:
├── GPIO 4  → Button 1 (Talk)
├── GPIO 5  → Button 2 (Volume Up)  
├── GPIO 18 → Button 3 (Volume Down)
├── GPIO 2  → LED Strip (Data In)
├── 3.3V    → LED Strip (VCC)
└── GND     → LED Strip (GND) + Buttons (GND)
```

## 📁 الملفات المطلوبة

### ملف 1: `01_basic_wifi_test.ino`
```cpp
#include <WiFi.h>

// ⚙️ إعدادات WiFi (غيّرها حسب شبكتك)
const char* ssid = "YOUR_WIFI_NAME";
const char* password = "YOUR_WIFI_PASSWORD";

void setup() {
    Serial.begin(115200);
    delay(1000);
    
    Serial.println("🧸 اختبار ESP32 الأساسي");
    Serial.println("========================");
    
    // عرض معلومات ESP32
    Serial.println("📱 معلومات الجهاز:");
    Serial.println("   - Chip Model: " + String(ESP.getChipModel()));
    Serial.println("   - Chip Cores: " + String(ESP.getChipCores()));
    Serial.println("   - Chip Revision: " + String(ESP.getChipRevision()));
    Serial.println("   - Flash Size: " + String(ESP.getFlashChipSize()/1024/1024) + " MB");
    Serial.println("   - Free Heap: " + String(ESP.getFreeHeap()) + " bytes");
    
    // اختبار اتصال WiFi
    test_wifi_connection();
}

void loop() {
    // مراقبة حالة الاتصال
    monitor_wifi_status();
    delay(5000);
}

void test_wifi_connection() {
    Serial.println("\n🌐 اختبار اتصال WiFi...");
    Serial.println("   - الشبكة: " + String(ssid));
    
    WiFi.begin(ssid, password);
    
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 20) {
        delay(500);
        Serial.print(".");
        attempts++;
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\n✅ WiFi متصل بنجاح!");
        Serial.println("   - عنوان IP: " + WiFi.localIP().toString());
        Serial.println("   - قوة الإشارة: " + String(WiFi.RSSI()) + " dBm");
        Serial.println("   - MAC Address: " + WiFi.macAddress());
    } else {
        Serial.println("\n❌ فشل الاتصال بـ WiFi");
        Serial.println("   - تأكد من اسم الشبكة وكلمة المرور");
    }
}

void monitor_wifi_status() {
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("💚 الاتصال نشط - IP: " + WiFi.localIP().toString());
    } else {
        Serial.println("❌ انقطع الاتصال - محاولة إعادة الاتصال...");
        WiFi.begin(ssid, password);
    }
}
```

### ملف 2: `02_led_control_test.ino`
```cpp
#include <FastLED.h>

// ⚙️ إعدادات LEDs
#define LED_PIN 2
#define NUM_LEDS 8
#define LED_BRIGHTNESS 100

// ⚙️ إعدادات الأزرار
#define BUTTON_TALK 4
#define BUTTON_VOL_UP 5
#define BUTTON_VOL_DOWN 18

// 💡 متغيرات LEDs
CRGB leds[NUM_LEDS];
int current_pattern = 0;
int brightness = LED_BRIGHTNESS;

void setup() {
    Serial.begin(115200);
    delay(1000);
    
    Serial.println("🧸 اختبار الأضواء والأزرار");
    Serial.println("==========================");
    
    // إعداد الأزرار
    setup_buttons();
    
    // إعداد LEDs
    setup_leds();
    
    // عرض ترحيبي
    welcome_animation();
    
    Serial.println("✅ النظام جاهز!");
    Serial.println("📋 التحكم:");
    Serial.println("   - الزر 1: تغيير النمط");
    Serial.println("   - الزر 2: زيادة السطوع");
    Serial.println("   - الزر 3: تقليل السطوع");
}

void loop() {
    // فحص الأزرار
    handle_buttons();
    
    // تحديث الأضواء
    update_led_pattern();
    
    delay(50);
}

void setup_buttons() {
    pinMode(BUTTON_TALK, INPUT_PULLUP);
    pinMode(BUTTON_VOL_UP, INPUT_PULLUP);
    pinMode(BUTTON_VOL_DOWN, INPUT_PULLUP);
    Serial.println("✅ الأزرار جاهزة");
}

void setup_leds() {
    FastLED.addLeds<WS2812B, LED_PIN, GRB>(leds, NUM_LEDS);
    FastLED.setBrightness(brightness);
    FastLED.clear();
    FastLED.show();
    Serial.println("✅ LEDs جاهزة");
}

void welcome_animation() {
    Serial.println("🌈 عرض ترحيبي...");
    
    // إضاءة تدريجية
    for(int i = 0; i < NUM_LEDS; i++) {
        leds[i] = CRGB::Blue;
        FastLED.show();
        delay(150);
    }
    
    delay(500);
    
    // تأثير قوس قزح
    for(int hue = 0; hue < 255; hue += 5) {
        fill_rainbow(leds, NUM_LEDS, hue, 255/NUM_LEDS);
        FastLED.show();
        delay(30);
    }
    
    // إطفاء تدريجي
    for(int i = 0; i < NUM_LEDS; i++) {
        leds[i] = CRGB::Black;
        FastLED.show();
        delay(100);
    }
    
    Serial.println("✨ العرض مكتمل");
}

void handle_buttons() {
    static bool last_btn1 = HIGH, last_btn2 = HIGH, last_btn3 = HIGH;
    
    bool btn1 = digitalRead(BUTTON_TALK);
    bool btn2 = digitalRead(BUTTON_VOL_UP);
    bool btn3 = digitalRead(BUTTON_VOL_DOWN);
    
    // زر تغيير النمط
    if (last_btn1 == HIGH && btn1 == LOW) {
        current_pattern = (current_pattern + 1) % 6;
        Serial.println("🎨 النمط الجديد: " + String(current_pattern));
    }
    
    // زر زيادة السطوع
    if (last_btn2 == HIGH && btn2 == LOW) {
        brightness = min(255, brightness + 25);
        FastLED.setBrightness(brightness);
        Serial.println("🔆 السطوع: " + String(brightness));
    }
    
    // زر تقليل السطوع
    if (last_btn3 == HIGH && btn3 == LOW) {
        brightness = max(25, brightness - 25);
        FastLED.setBrightness(brightness);
        Serial.println("🔅 السطوع: " + String(brightness));
    }
    
    last_btn1 = btn1;
    last_btn2 = btn2;
    last_btn3 = btn3;
}

void update_led_pattern() {
    static unsigned long last_update = 0;
    static int animation_step = 0;
    
    if (millis() - last_update > 100) {
        switch(current_pattern) {
            case 0: // أحمر ثابت
                fill_solid(leds, NUM_LEDS, CRGB::Red);
                break;
                
            case 1: // أخضر ثابت
                fill_solid(leds, NUM_LEDS, CRGB::Green);
                break;
                
            case 2: // أزرق ثابت
                fill_solid(leds, NUM_LEDS, CRGB::Blue);
                break;
                
            case 3: // قوس قزح ثابت
                fill_rainbow(leds, NUM_LEDS, 0, 255/NUM_LEDS);
                break;
                
            case 4: // قوس قزح متحرك
                fill_rainbow(leds, NUM_LEDS, animation_step * 5, 255/NUM_LEDS);
                break;
                
            case 5: // وميض متدرج
                for(int i = 0; i < NUM_LEDS; i++) {
                    int brightness_wave = (sin((animation_step + i * 20) * 0.1) + 1) * 127;
                    leds[i] = CHSV(160, 255, brightness_wave); // بنفسجي متدرج
                }
                break;
        }
        
        FastLED.show();
        animation_step++;
        last_update = millis();
    }
}
```

### ملف 3: `03_complete_basic_test.ino`
```cpp
#include <WiFi.h>
#include <FastLED.h>

// ⚙️ إعدادات WiFi
const char* ssid = "YOUR_WIFI_NAME";
const char* password = "YOUR_WIFI_PASSWORD";

// ⚙️ إعدادات الأجهزة
#define LED_PIN 2
#define NUM_LEDS 8
#define BUTTON_TALK 4
#define BUTTON_VOL_UP 5
#define BUTTON_VOL_DOWN 18

// 💡 متغيرات النظام
CRGB leds[NUM_LEDS];
bool wifi_connected = false;
bool system_ready = false;

void setup() {
    Serial.begin(115200);
    delay(1000);
    
    Serial.println("🧸 اختبار النظام الأساسي الكامل");
    Serial.println("===============================");
    
    // إعداد الأجهزة
    if (setup_hardware()) {
        Serial.println("✅ الأجهزة جاهزة");
    } else {
        Serial.println("❌ خطأ في إعداد الأجهزة");
        return;
    }
    
    // اتصال الشبكة
    if (connect_wifi()) {
        wifi_connected = true;
        Serial.println("✅ الشبكة جاهزة");
    } else {
        wifi_connected = false;
        Serial.println("⚠️ الشبكة غير متوفرة - العمل أوفلاين");
    }
    
    // عرض حالة النظام
    show_system_status();
    
    system_ready = true;
    Serial.println("🎉 النظام جاهز للاستخدام!");
}

void loop() {
    if (system_ready) {
        // فحص الأزرار
        handle_user_input();
        
        // مراقبة النظام
        monitor_system();
        
        // تحديث المؤشرات
        update_status_leds();
    }
    
    delay(100);
}

bool setup_hardware() {
    // إعداد الأزرار
    pinMode(BUTTON_TALK, INPUT_PULLUP);
    pinMode(BUTTON_VOL_UP, INPUT_PULLUP);
    pinMode(BUTTON_VOL_DOWN, INPUT_PULLUP);
    
    // إعداد LEDs
    FastLED.addLeds<WS2812B, LED_PIN, GRB>(leds, NUM_LEDS);
    FastLED.setBrightness(100);
    FastLED.clear();
    FastLED.show();
    
    // اختبار الأضواء
    test_leds();
    
    return true;
}

bool connect_wifi() {
    Serial.println("🌐 محاولة اتصال WiFi...");
    
    WiFi.begin(ssid, password);
    
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 15) {
        delay(500);
        Serial.print(".");
        attempts++;
        
        // مؤشر أضواء للانتظار
        leds[attempts % NUM_LEDS] = CRGB::Yellow;
        FastLED.show();
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\n✅ WiFi متصل!");
        Serial.println("📍 IP: " + WiFi.localIP().toString());
        return true;
    } else {
        Serial.println("\n❌ فشل الاتصال");
        return false;
    }
}

void test_leds() {
    Serial.println("🧪 اختبار LEDs...");
    
    // أحمر
    fill_solid(leds, NUM_LEDS, CRGB::Red);
    FastLED.show();
    delay(300);
    
    // أخضر
    fill_solid(leds, NUM_LEDS, CRGB::Green);
    FastLED.show();
    delay(300);
    
    // أزرق
    fill_solid(leds, NUM_LEDS, CRGB::Blue);
    FastLED.show();
    delay(300);
    
    // إطفاء
    FastLED.clear();
    FastLED.show();
}

void handle_user_input() {
    static bool last_talk = HIGH, last_up = HIGH, last_down = HIGH;
    
    bool talk = digitalRead(BUTTON_TALK);
    bool up = digitalRead(BUTTON_VOL_UP);
    bool down = digitalRead(BUTTON_VOL_DOWN);
    
    // زر المحادثة
    if (last_talk == HIGH && talk == LOW) {
        Serial.println("🎤 زر المحادثة مضغوط");
        show_button_feedback(CRGB::Red);
    }
    
    // زر الصوت أعلى
    if (last_up == HIGH && up == LOW) {
        Serial.println("🔊 زر رفع الصوت مضغوط");
        show_button_feedback(CRGB::Green);
    }
    
    // زر الصوت أقل
    if (last_down == HIGH && down == LOW) {
        Serial.println("🔉 زر خفض الصوت مضغوط");
        show_button_feedback(CRGB::Blue);
    }
    
    last_talk = talk;
    last_up = up;
    last_down = down;
}

void monitor_system() {
    static unsigned long last_check = 0;
    
    if (millis() - last_check > 10000) { // كل 10 ثوان
        Serial.println("📊 حالة النظام:");
        Serial.println("   - الذاكرة الحرة: " + String(ESP.getFreeHeap()) + " bytes");
        Serial.println("   - وقت التشغيل: " + String(millis()/1000) + " ثانية");
        
        if (wifi_connected) {
            Serial.println("   - WiFi: متصل (" + String(WiFi.RSSI()) + " dBm)");
        } else {
            Serial.println("   - WiFi: غير متصل");
        }
        
        last_check = millis();
    }
}

void update_status_leds() {
    static unsigned long last_blink = 0;
    static bool blink_state = false;
    
    if (millis() - last_blink > 1000) {
        blink_state = !blink_state;
        
        if (wifi_connected) {
            // أخضر ثابت إذا متصل
            leds[0] = CRGB::Green;
        } else {
            // أحمر وامض إذا غير متصل
            leds[0] = blink_state ? CRGB::Red : CRGB::Black;
        }
        
        FastLED.show();
        last_blink = millis();
    }
}

void show_system_status() {
    Serial.println("📋 حالة النظام:");
    Serial.println("   - WiFi: " + String(wifi_connected ? "متصل" : "غير متصل"));
    Serial.println("   - LEDs: جاهزة");
    Serial.println("   - الأزرار: جاهزة");
    Serial.println("   - الذاكرة: " + String(ESP.getFreeHeap()) + " bytes");
}

void show_button_feedback(CRGB color) {
    // وميض سريع للتأكيد
    fill_solid(leds, NUM_LEDS, color);
    FastLED.show();
    delay(100);
    FastLED.clear();
    FastLED.show();
}
```

## 📋 خطوات الاختبار

### ✅ اختبار 1: WiFi الأساسي
1. افتح `01_basic_wifi_test.ino`
2. غيّر `ssid` و `password`
3. رفع الكود
4. افتح Serial Monitor
5. تأكد من رؤية IP address

### ✅ اختبار 2: LEDs والأزرار
1. وصّل LEDs والأزرار حسب المخطط
2. افتح `02_led_control_test.ino`
3. رفع الكود
4. اختبر كل زر والأضواء

### ✅ اختبار 3: النظام الكامل
1. افتح `03_complete_basic_test.ino`
2. تأكد من جميع التوصيلات
3. رفع الكود واختبر كل شيء

## 🆘 حل المشاكل

### ❌ ESP32 لا يعمل:
- تأكد من كابل USB جيد
- اضغط زر EN للإعادة تشغيل
- جرب port مختلف في Arduino IDE

### ❌ WiFi لا يتصل:
- تأكد من اسم الشبكة وكلمة المرور
- تأكد من أن الشبكة 2.4GHz (ليس 5GHz)
- جرب الاقتراب من الراوتر

### ❌ LEDs لا تعمل:
- تأكد من توصيل VCC, GND, Data
- تأكد من أن LED Strip هو WS2812B
- جرب GPIO مختلف

### ❌ الأزرار لا تعمل:
- تأكد من استخدام INPUT_PULLUP
- تأكد من توصيل GND
- اختبر الأزرار بمتعدد القياس

## 🎯 ما التالي؟

بعد نجاح هذا المستوى، ستكون جاهزاً للمستوى الثاني:
- **المستوى 2**: إضافة المايكروفون وتسجيل الصوت
- **المستوى 3**: الاتصال بالسيرفر
- **المستوى 4**: تشغيل الصوت
- **المستوى 5**: النظام الكامل

🎉 **تهانينا!** أنت الآن تملك أساس قوي لبناء الدب الذكي! 