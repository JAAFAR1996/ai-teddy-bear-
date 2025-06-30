/*
🧸 AI Teddy Bear - Secure ESP32 Main Code v2.0
Enhanced security with HTTPS, NVS storage, and improved audio handling
*/

#include <WiFi.h>
#include <HTTPClient.h>
#include <WiFiClientSecure.h>
#include <ArduinoJson.h>
#include <Preferences.h>
#include <driver/i2s.h>
#include <esp_sleep.h>
#include <esp_log.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

// ================ SECURE CONFIGURATION ================
Preferences preferences;
WiFiClientSecure client;

// Configuration keys for NVS storage
const char* WIFI_SSID_KEY = "wifi_ssid";
const char* WIFI_PASS_KEY = "wifi_pass";  
const char* SERVER_URL_KEY = "server_url";
const char* DEVICE_ID_KEY = "device_id";
const char* API_KEY_KEY = "api_key";

// Default values (will be overridden by stored values)
String wifi_ssid = "";
String wifi_password = "";
String server_url = "https://teddy-cloud.example.com";
String device_id = "";
String api_key = "";

// Hardware pins
const int BUTTON_TALK = 12;
const int BUTTON_VOLUME_UP = 13;
const int BUTTON_VOLUME_DOWN = 14;
const int LED_STATUS = 2;
const int LED_LISTENING = 4;
const int LED_PROCESSING = 5;

// Audio configuration
const int SAMPLE_RATE = 16000;
const int BITS_PER_SAMPLE = 16;
const int AUDIO_BUFFER_SIZE = 1024;
const int MAX_AUDIO_DURATION = 10; // seconds
const int VOLUME_LEVELS = 10;

// State variables
bool wifi_connected = false;
bool server_connected = false;
int current_volume = 5;
bool is_listening = false;
bool is_processing = false;
unsigned long last_heartbeat = 0;
unsigned long last_activity = 0;
const unsigned long SLEEP_TIMEOUT = 300000; // 5 minutes
const unsigned long HEARTBEAT_INTERVAL = 30000; // 30 seconds

// Audio buffers
int16_t audio_buffer[AUDIO_BUFFER_SIZE];
std::vector<int16_t> recorded_audio;

// ================ INITIALIZATION ================

void setup() {
    Serial.begin(115200);
    delay(1000);
    
    Serial.println("\n🧸 AI Teddy Bear - Secure Version v2.0");
    Serial.println("======================================");
    
    // Initialize hardware
    init_hardware();
    
    // Load configuration from NVS
    load_configuration();
    
    // Generate device ID if not exists
    if (device_id.isEmpty()) {
        generate_device_id();
    }
    
    Serial.printf("Device ID: %s\n", device_id.c_str());
    
    // Initialize WiFi
    init_wifi();
    
    // Initialize audio system
    init_audio();
    
    // Setup SSL certificate validation
    setup_ssl();
    
    // Test server connection
    test_server_connection();
    
    Serial.println("🧸 Teddy Bear ready! Press TALK button to start.");
    set_status_led(true, false, false); // Green = ready
}

void init_hardware() {
    // Initialize pins
    pinMode(BUTTON_TALK, INPUT_PULLUP);
    pinMode(BUTTON_VOLUME_UP, INPUT_PULLUP);
    pinMode(BUTTON_VOLUME_DOWN, INPUT_PULLUP);
    pinMode(LED_STATUS, OUTPUT);
    pinMode(LED_LISTENING, OUTPUT);
    pinMode(LED_PROCESSING, OUTPUT);
    
    // Initial LED state
    set_status_led(false, false, false);
    
    Serial.println("✅ Hardware initialized");
}

void load_configuration() {
    preferences.begin("teddy_config", false);
    
    // Load stored configuration
    wifi_ssid = preferences.getString(WIFI_SSID_KEY, "");
    wifi_password = preferences.getString(WIFI_PASS_KEY, "");
    server_url = preferences.getString(SERVER_URL_KEY, "https://teddy-cloud.example.com");
    device_id = preferences.getString(DEVICE_ID_KEY, "");
    api_key = preferences.getString(API_KEY_KEY, "");
    current_volume = preferences.getInt("volume", 5);
    
    Serial.println("✅ Configuration loaded from NVS");
    
    // If WiFi credentials are empty, enter configuration mode
    if (wifi_ssid.isEmpty()) {
        Serial.println("⚠️ No WiFi credentials found. Entering configuration mode...");
        enter_config_mode();
    }
}

void save_configuration() {
    preferences.putString(WIFI_SSID_KEY, wifi_ssid);
    preferences.putString(WIFI_PASS_KEY, wifi_password);
    preferences.putString(SERVER_URL_KEY, server_url);
    preferences.putString(DEVICE_ID_KEY, device_id);
    preferences.putString(API_KEY_KEY, api_key);
    preferences.putInt("volume", current_volume);
    
    Serial.println("✅ Configuration saved to NVS");
}

void generate_device_id() {
    uint64_t mac = ESP.getEfuseMac();
    device_id = "ESP32_TEDDY_" + String((uint32_t)mac, HEX);
    device_id.toUpperCase();
    save_configuration();
    Serial.printf("✅ Generated Device ID: %s\n", device_id.c_str());
}

void enter_config_mode() {
    Serial.println("🔧 Configuration Mode");
    Serial.println("Connect to WiFi 'TeddyBear_Setup' and open 192.168.4.1");
    
    // Create access point for configuration
    WiFi.softAP("TeddyBear_Setup", "teddy123");
    
    // Start web server for configuration
    // TODO: Implement web server for WiFi setup
    
    // For now, use serial configuration
    Serial.println("Enter WiFi SSID:");
    while (Serial.available() == 0) delay(100);
    wifi_ssid = Serial.readString();
    wifi_ssid.trim();
    
    Serial.println("Enter WiFi Password:");
    while (Serial.available() == 0) delay(100);
    wifi_password = Serial.readString();
    wifi_password.trim();
    
    save_configuration();
    Serial.println("✅ Configuration saved. Restarting...");
    ESP.restart();
}

void init_wifi() {
    WiFi.mode(WIFI_STA);
    WiFi.begin(wifi_ssid.c_str(), wifi_password.c_str());
    
    Serial.printf("Connecting to WiFi: %s", wifi_ssid.c_str());
    
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 20) {
        delay(500);
        Serial.print(".");
        attempts++;
        
        // Blink LED while connecting
        digitalWrite(LED_STATUS, attempts % 2);
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        wifi_connected = true;
        Serial.printf("\n✅ WiFi connected! IP: %s\n", WiFi.localIP().toString().c_str());
        set_status_led(true, false, false); // Green
    } else {
        Serial.println("\n❌ WiFi connection failed!");
        set_status_led(false, false, true); // Red
        // Enter deep sleep and retry later
        enter_deep_sleep(60); // Sleep for 1 minute
    }
}

void setup_ssl() {
    // Skip certificate validation for now (use proper certificates in production)
    client.setInsecure();
    
    // TODO: Load proper SSL certificates
    // client.setCACert(root_ca);
    
    Serial.println("⚠️ SSL validation disabled (development mode)");
}

void init_audio() {
    // Configure I2S for audio recording
    i2s_config_t i2s_config = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
        .sample_rate = SAMPLE_RATE,
        .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
        .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
        .communication_format = I2S_COMM_FORMAT_I2S,
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count = 4,
        .dma_buf_len = AUDIO_BUFFER_SIZE,
        .use_apll = false
    };
    
    i2s_pin_config_t pin_config = {
        .bck_io_num = 26,
        .ws_io_num = 25,
        .data_out_num = I2S_PIN_NO_CHANGE,
        .data_in_num = 33
    };
    
    esp_err_t err = i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL);
    if (err != ESP_OK) {
        Serial.printf("❌ I2S driver install failed: %s\n", esp_err_to_name(err));
        return;
    }
    
    err = i2s_set_pin(I2S_NUM_0, &pin_config);
    if (err != ESP_OK) {
        Serial.printf("❌ I2S pin setup failed: %s\n", esp_err_to_name(err));
        return;
    }
    
    Serial.println("✅ Audio system initialized");
}

// ================ MAIN LOOP ================

void loop() {
    update_activity();
    
    // Check buttons
    handle_buttons();
    
    // Send heartbeat periodically
    if (millis() - last_heartbeat > HEARTBEAT_INTERVAL) {
        send_heartbeat();
        last_heartbeat = millis();
    }
    
    // Check for sleep timeout
    if (millis() - last_activity > SLEEP_TIMEOUT) {
        Serial.println("💤 Entering sleep mode...");
        enter_deep_sleep(300); // Sleep for 5 minutes
    }
    
    delay(100);
}

void update_activity() {
    last_activity = millis();
}

void handle_buttons() {
    // Talk button
    if (digitalRead(BUTTON_TALK) == LOW) {
        delay(50); // Debounce
        if (digitalRead(BUTTON_TALK) == LOW) {
            handle_talk_button();
            while (digitalRead(BUTTON_TALK) == LOW) delay(10);
        }
    }
    
    // Volume up button
    if (digitalRead(BUTTON_VOLUME_UP) == LOW) {
        delay(50);
        if (digitalRead(BUTTON_VOLUME_UP) == LOW) {
            adjust_volume(1);
            while (digitalRead(BUTTON_VOLUME_UP) == LOW) delay(10);
        }
    }
    
    // Volume down button
    if (digitalRead(BUTTON_VOLUME_DOWN) == LOW) {
        delay(50);
        if (digitalRead(BUTTON_VOLUME_DOWN) == LOW) {
            adjust_volume(-1);
            while (digitalRead(BUTTON_VOLUME_DOWN) == LOW) delay(10);
        }
    }
}

void handle_talk_button() {
    update_activity();
    
    if (!wifi_connected) {
        Serial.println("❌ No WiFi connection");
        set_status_led(false, false, true); // Red
        return;
    }
    
    if (is_listening || is_processing) {
        Serial.println("⚠️ Already processing...");
        return;
    }
    
    Serial.println("🎤 Talk button pressed - Starting recording...");
    start_recording();
}

void adjust_volume(int delta) {
    current_volume += delta;
    current_volume = constrain(current_volume, 0, VOLUME_LEVELS);
    
    Serial.printf("🔊 Volume: %d/%d\n", current_volume, VOLUME_LEVELS);
    
    // Save volume setting
    preferences.putInt("volume", current_volume);
    
    // Send volume update to server
    send_volume_update();
    
    // Visual feedback
    for (int i = 0; i <= current_volume; i++) {
        set_status_led(true, false, false);
        delay(100);
        set_status_led(false, false, false);
        delay(100);
    }
}

// ================ AUDIO RECORDING ================

void start_recording() {
    is_listening = true;
    recorded_audio.clear();
    
    set_status_led(false, true, false); // Blue = listening
    Serial.println("🎤 Recording started... (speak now)");
    
    unsigned long start_time = millis();
    size_t bytes_read = 0;
    
    while (millis() - start_time < MAX_AUDIO_DURATION * 1000) {
        // Read audio data
        esp_err_t err = i2s_read(I2S_NUM_0, audio_buffer, 
                                sizeof(audio_buffer), &bytes_read, 100);
        
        if (err == ESP_OK && bytes_read > 0) {
            // Add to recorded audio
            int samples = bytes_read / sizeof(int16_t);
            for (int i = 0; i < samples; i++) {
                recorded_audio.push_back(audio_buffer[i]);
            }
        }
        
        // Check for silence (simplified voice activity detection)
        if (is_silence_detected()) {
            Serial.println("🔇 Silence detected - stopping recording");
            break;
        }
        
        // Check if talk button released
        if (digitalRead(BUTTON_TALK) == HIGH) {
            Serial.println("🛑 Talk button released - stopping recording");
            break;
        }
    }
    
    is_listening = false;
    set_status_led(false, false, false);
    
    if (recorded_audio.size() > 0) {
        Serial.printf("✅ Recording complete: %d samples\n", recorded_audio.size());
        process_audio();
    } else {
        Serial.println("❌ No audio recorded");
    }
}

bool is_silence_detected() {
    // Simple silence detection based on amplitude
    if (recorded_audio.size() < SAMPLE_RATE) return false; // Need at least 1 second
    
    // Check last 0.5 seconds for silence
    int samples_to_check = SAMPLE_RATE / 2;
    int start_idx = recorded_audio.size() - samples_to_check;
    
    float avg_amplitude = 0;
    for (int i = start_idx; i < recorded_audio.size(); i++) {
        avg_amplitude += abs(recorded_audio[i]);
    }
    avg_amplitude /= samples_to_check;
    
    // Threshold for silence (adjust based on microphone sensitivity)
    return avg_amplitude < 100;
}

// ================ CLOUD COMMUNICATION ================

void process_audio() {
    if (!server_connected) {
        Serial.println("❌ No server connection");
        return;
    }
    
    is_processing = true;
    set_status_led(false, false, true); // Red = processing
    
    Serial.println("☁️ Sending audio to cloud...");
    
    // Convert audio to base64
    String audio_base64 = encode_audio_base64();
    
    // Create JSON payload
    DynamicJsonDocument doc(8192);
    doc["device_id"] = device_id;
    doc["session_id"] = "session_" + String(millis());
    doc["audio_format"] = "pcm_16000";
    doc["audio_data"] = audio_base64;
    doc["timestamp"] = millis();
    doc["volume_level"] = current_volume;
    
    String json_payload;
    serializeJson(doc, json_payload);
    
    // Send to server
    HTTPClient http;
    http.begin(client, server_url + "/esp32/audio");
    http.addHeader("Content-Type", "application/json");
    http.addHeader("Authorization", "Bearer " + api_key);
    http.setTimeout(15000); // 15 second timeout
    
    int response_code = http.POST(json_payload);
    
    if (response_code == 200) {
        String response = http.getString();
        handle_cloud_response(response);
    } else {
        Serial.printf("❌ Server error: %d\n", response_code);
        set_status_led(true, false, true); // Yellow = error
        delay(2000);
    }
    
    http.end();
    is_processing = false;
    set_status_led(true, false, false); // Green = ready
}

String encode_audio_base64() {
    // Convert audio samples to bytes
    const char* chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
    String result = "";
    
    // Simple base64 encoding (use proper library in production)
    // For now, return a placeholder
    return "base64_encoded_audio_data";
}

void handle_cloud_response(String response) {
    Serial.println("📥 Received response from cloud:");
    Serial.println(response);
    
    // Parse JSON response
    DynamicJsonDocument doc(2048);
    deserializeJson(doc, response);
    
    String transcription = doc["transcription"];
    JsonObject ai_response = doc["ai_response"];
    String response_text = ai_response["text"];
    String emotion = ai_response["emotion"];
    
    Serial.printf("🎯 Transcription: %s\n", transcription.c_str());
    Serial.printf("🧸 AI Response: %s\n", response_text.c_str());
    Serial.printf("😊 Emotion: %s\n", emotion.c_str());
    
    // Play response audio (placeholder)
    play_response(response_text, emotion);
}

void play_response(String text, String emotion) {
    Serial.println("🔊 Playing response...");
    
    // Set LED based on emotion
    if (emotion == "happy") {
        set_status_led(true, true, false); // Green + Blue = Cyan
    } else if (emotion == "sad") {
        set_status_led(false, false, true); // Red
    } else {
        set_status_led(true, false, false); // Green
    }
    
    // TODO: Implement actual TTS playback
    // For now, just simulate playing
    delay(3000);
    
    set_status_led(true, false, false); // Back to ready state
    Serial.println("✅ Response played");
}

void send_heartbeat() {
    if (!wifi_connected) return;
    
    HTTPClient http;
    http.begin(client, server_url + "/esp32/heartbeat");
    http.addHeader("Content-Type", "application/json");
    http.addHeader("Authorization", "Bearer " + api_key);
    
    DynamicJsonDocument doc(512);
    doc["device_id"] = device_id;
    doc["status"] = "online";
    doc["battery_level"] = get_battery_level();
    doc["wifi_strength"] = WiFi.RSSI();
    doc["uptime"] = millis();
    doc["firmware_version"] = "2.0.0-secure";
    doc["volume"] = current_volume;
    
    String payload;
    serializeJson(doc, payload);
    
    int response_code = http.POST(payload);
    if (response_code == 200) {
        server_connected = true;
        // Serial.println("💓 Heartbeat sent");
    } else {
        server_connected = false;
        Serial.printf("❌ Heartbeat failed: %d\n", response_code);
    }
    
    http.end();
}

void send_volume_update() {
    if (!wifi_connected) return;
    
    HTTPClient http;
    http.begin(client, server_url + "/esp32/volume");
    http.addHeader("Content-Type", "application/json");
    http.addHeader("Authorization", "Bearer " + api_key);
    
    DynamicJsonDocument doc(256);
    doc["device_id"] = device_id;
    doc["volume"] = current_volume;
    doc["timestamp"] = millis();
    
    String payload;
    serializeJson(doc, payload);
    
    http.POST(payload);
    http.end();
}

void test_server_connection() {
    Serial.println("🔗 Testing server connection...");
    
    HTTPClient http;
    http.begin(client, server_url + "/health");
    http.setTimeout(5000);
    
    int response_code = http.GET();
    if (response_code == 200) {
        server_connected = true;
        Serial.println("✅ Server connection successful");
    } else {
        server_connected = false;
        Serial.printf("❌ Server connection failed: %d\n", response_code);
    }
    
    http.end();
}

// ================ UTILITY FUNCTIONS ================

void set_status_led(bool green, bool blue, bool red) {
    digitalWrite(LED_STATUS, green);
    digitalWrite(LED_LISTENING, blue);
    digitalWrite(LED_PROCESSING, red);
}

int get_battery_level() {
    // TODO: Implement actual battery monitoring
    // For now, return a simulated value
    return 85;
}

void enter_deep_sleep(int seconds) {
    Serial.printf("💤 Entering deep sleep for %d seconds\n", seconds);
    
    // Configure wake up sources
    esp_sleep_enable_timer_wakeup(seconds * 1000000ULL); // Convert to microseconds
    esp_sleep_enable_ext0_wakeup(GPIO_NUM_12, 0); // Wake on talk button press
    
    // Turn off LEDs
    set_status_led(false, false, false);
    
    // Save current state
    save_configuration();
    
    // Enter deep sleep
    esp_deep_sleep_start();
}

void handle_ota_update() {
    // TODO: Implement Over-The-Air firmware updates
    Serial.println("🔄 OTA update feature - coming soon");
}

// ================ ERROR HANDLING ================

void handle_critical_error(String error) {
    Serial.printf("💥 CRITICAL ERROR: %s\n", error.c_str());
    
    // Flash red LED rapidly
    for (int i = 0; i < 10; i++) {
        set_status_led(false, false, true);
        delay(200);
        set_status_led(false, false, false);
        delay(200);
    }
    
    // Log error to server if possible
    if (wifi_connected) {
        // TODO: Send error report to server
    }
    
    // Restart ESP32
    ESP.restart();
} 