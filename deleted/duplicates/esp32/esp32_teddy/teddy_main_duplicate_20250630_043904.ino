#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <driver/i2s.h>
#include <FastLED.h>
#include <ESPAsyncWebServer.h>
#include <SPIFFS.h>

// ===============================
// 🧸 AI Teddy Bear ESP32 Code - 2025
// ===============================

// 📡 WiFi Configuration
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const char* server_url = "http://your-cloud-server.com:8000";

// 🎵 Audio Configuration
#define I2S_WS 25
#define I2S_SD 33
#define I2S_SCK 32
#define SAMPLE_RATE 16000
#define SAMPLE_BITS 16

// 💡 LED Configuration
#define LED_PIN 2
#define NUM_LEDS 8
CRGB leds[NUM_LEDS];

// 🔘 Button Configuration
#define TALK_BUTTON 4
#define VOLUME_UP 5
#define VOLUME_DOWN 18

// 🎚️ System Variables
bool is_recording = false;
bool is_playing = false;
int volume_level = 50;
String session_id = "";

// 🎤 Audio Buffer
const int buffer_size = 1024;
int16_t audio_buffer[buffer_size];

// 🌐 Web Server
AsyncWebServer server(80);

void setup() {
    Serial.begin(115200);
    Serial.println("🧸 Starting AI Teddy Bear...");
    
    // Initialize components
    init_pins();
    init_leds();
    init_wifi();
    init_audio();
    init_web_server();
    
    Serial.println("✅ Teddy Bear Ready!");
    show_status_led(CRGB::Green);
}

void loop() {
    handle_buttons();
    handle_audio();
    
    // Heartbeat to server every 30 seconds
    static unsigned long last_heartbeat = 0;
    if (millis() - last_heartbeat > 30000) {
        send_heartbeat();
        last_heartbeat = millis();
    }
    
    delay(10);
}

// 📌 Initialize Hardware Pins
void init_pins() {
    pinMode(TALK_BUTTON, INPUT_PULLUP);
    pinMode(VOLUME_UP, INPUT_PULLUP);
    pinMode(VOLUME_DOWN, INPUT_PULLUP);
}

// 💡 Initialize LEDs
void init_leds() {
    FastLED.addLeds<WS2812B, LED_PIN, GRB>(leds, NUM_LEDS);
    FastLED.setBrightness(100);
    
    // Startup animation
    for(int i = 0; i < NUM_LEDS; i++) {
        leds[i] = CRGB::Blue;
        FastLED.show();
        delay(100);
    }
}

// 📡 Initialize WiFi
void init_wifi() {
    WiFi.begin(ssid, password);
    show_status_led(CRGB::Yellow); // Connecting
    
    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.println("🔄 Connecting to WiFi...");
    }
    
    Serial.println("✅ WiFi Connected!");
    Serial.println("📍 IP Address: " + WiFi.localIP().toString());
    show_status_led(CRGB::Green);
}

// 🎵 Initialize Audio System
void init_audio() {
    i2s_config_t i2s_config = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX | I2S_MODE_TX),
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
        .data_out_num = I2S_SD,
        .data_in_num = I2S_SD
    };
    
    i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL);
    i2s_set_pin(I2S_NUM_0, &pin_config);
}

// 🌐 Initialize Web Server for Remote Control
void init_web_server() {
    server.on("/", HTTP_GET, [](AsyncWebServerRequest *request){
        request->send(200, "text/html", 
            "<!DOCTYPE html><html><head><title>🧸 Teddy Control</title></head>"
            "<body style='font-family: Arial; text-align: center; padding: 50px;'>"
            "<h1>🧸 AI Teddy Bear Control</h1>"
            "<p>Status: <span style='color: green;'>Online</span></p>"
            "<button onclick=\"fetch('/talk')\">🎤 Start Talking</button><br><br>"
            "<button onclick=\"fetch('/volume/up')\">🔊 Volume Up</button><br><br>"
            "<button onclick=\"fetch('/volume/down')\">🔉 Volume Down</button><br><br>"
            "<p>Volume: " + String(volume_level) + "%</p>"
            "</body></html>");
    });
    
    server.on("/talk", HTTP_GET, [](AsyncWebServerRequest *request){
        start_conversation();
        request->send(200, "text/plain", "Started conversation");
    });
    
    server.on("/volume/up", HTTP_GET, [](AsyncWebServerRequest *request){
        volume_level = min(100, volume_level + 10);
        request->send(200, "text/plain", "Volume: " + String(volume_level));
    });
    
    server.on("/volume/down", HTTP_GET, [](AsyncWebServerRequest *request){
        volume_level = max(0, volume_level - 10);
        request->send(200, "text/plain", "Volume: " + String(volume_level));
    });
    
    server.begin();
}

// 🔘 Handle Physical Buttons
void handle_buttons() {
    static bool last_talk_state = HIGH;
    bool talk_state = digitalRead(TALK_BUTTON);
    
    // Talk button pressed
    if (last_talk_state == HIGH && talk_state == LOW) {
        start_conversation();
    }
    // Talk button released
    else if (last_talk_state == LOW && talk_state == HIGH) {
        stop_conversation();
    }
    
    last_talk_state = talk_state;
    
    // Volume buttons
    if (digitalRead(VOLUME_UP) == LOW) {
        volume_level = min(100, volume_level + 5);
        delay(200);
    }
    if (digitalRead(VOLUME_DOWN) == LOW) {
        volume_level = max(0, volume_level - 5);
        delay(200);
    }
}

// 🎤 Start Conversation
void start_conversation() {
    if (!is_recording) {
        Serial.println("🎤 Starting to listen...");
        is_recording = true;
        show_status_led(CRGB::Red); // Recording
        
        // Generate new session ID
        session_id = String(millis()) + "_" + String(random(1000, 9999));
    }
}

// 🛑 Stop Conversation
void stop_conversation() {
    if (is_recording) {
        Serial.println("🛑 Stopping recording...");
        is_recording = false;
        show_status_led(CRGB::Blue); // Processing
        
        // Send audio to cloud server
        send_audio_to_cloud();
    }
}

// 🎵 Handle Audio Processing
void handle_audio() {
    if (is_recording) {
        size_t bytes_read;
        i2s_read(I2S_NUM_0, audio_buffer, buffer_size * sizeof(int16_t), &bytes_read, portMAX_DELAY);
        
        // In a real implementation, you would buffer the audio data
        // and send it to the cloud when recording stops
    }
}

// ☁️ Send Audio to Cloud Server
void send_audio_to_cloud() {
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("❌ WiFi not connected!");
        show_status_led(CRGB::Red);
        return;
    }
    
    HTTPClient http;
    http.begin(String(server_url) + "/teddy/voice-message");
    http.addHeader("Content-Type", "application/json");
    
    // Create JSON payload
    StaticJsonDocument<500> doc;
    doc["session_id"] = session_id;
    doc["device_id"] = WiFi.macAddress();
    doc["audio_format"] = "pcm_16000";
    doc["timestamp"] = millis();
    doc["volume_level"] = volume_level;
    
    // In real implementation, encode audio as base64
    doc["audio_data"] = "base64_encoded_audio_data_here";
    
    String payload;
    serializeJson(doc, payload);
    
    Serial.println("📤 Sending to cloud: " + payload);
    
    int httpResponseCode = http.POST(payload);
    
    if (httpResponseCode == 200) {
        String response = http.getString();
        Serial.println("📥 Response: " + response);
        
        // Parse response and play audio
        handle_cloud_response(response);
    } else {
        Serial.println("❌ HTTP Error: " + String(httpResponseCode));
        show_status_led(CRGB::Red);
    }
    
    http.end();
}

// 🎧 Handle Cloud Response
void handle_cloud_response(String response) {
    StaticJsonDocument<1000> doc;
    deserializeJson(doc, response);
    
    if (doc["status"] == "success") {
        String audio_url = doc["audio_url"];
        String text_response = doc["text"];
        
        Serial.println("🗣️ Teddy says: " + text_response);
        
        // Play audio from URL
        play_audio_from_url(audio_url);
        
        show_status_led(CRGB::Purple); // Speaking
    } else {
        Serial.println("❌ Error from cloud: " + String(doc["error"].as<String>()));
        show_status_led(CRGB::Red);
    }
}

// 🔊 Play Audio from URL
void play_audio_from_url(String url) {
    // In a real implementation, you would:
    // 1. Download the audio file
    // 2. Decode it (MP3/WAV)
    // 3. Play it through I2S
    
    Serial.println("🔊 Playing audio from: " + url);
    is_playing = true;
    
    // Simulate playing for demo
    delay(3000);
    
    is_playing = false;
    show_status_led(CRGB::Green); // Ready
}

// 💓 Send Heartbeat to Server
void send_heartbeat() {
    HTTPClient http;
    http.begin(String(server_url) + "/teddy/heartbeat");
    http.addHeader("Content-Type", "application/json");
    
    StaticJsonDocument<300> doc;
    doc["device_id"] = WiFi.macAddress();
    doc["status"] = "online";
    doc["battery_level"] = 85; // If using battery
    doc["wifi_strength"] = WiFi.RSSI();
    doc["uptime"] = millis();
    
    String payload;
    serializeJson(doc, payload);
    
    int httpResponseCode = http.POST(payload);
    
    if (httpResponseCode == 200) {
        Serial.println("💓 Heartbeat sent successfully");
    }
    
    http.end();
}

// 💡 Show Status LED
void show_status_led(CRGB color) {
    fill_solid(leds, NUM_LEDS, color);
    FastLED.show();
}

// 🎨 LED Animation for Different States
void animate_thinking() {
    for(int i = 0; i < NUM_LEDS; i++) {
        leds[i] = CRGB::Blue;
        FastLED.show();
        delay(100);
        leds[i] = CRGB::Black;
    }
}

void animate_speaking() {
    for(int brightness = 0; brightness < 255; brightness += 5) {
        fill_solid(leds, NUM_LEDS, CRGB(brightness, 0, brightness));
        FastLED.show();
        delay(10);
    }
} 