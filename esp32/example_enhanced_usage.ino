/*
🧸 AI Teddy Bear - Production Audio Processor Usage Example v3.0 (2025)
Complete example showing real base64, compression, and secure SSL in action
*/

#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <WebSocketsClient.h>
#include <driver/i2s.h>
#include "audio_processor.h"

// ================ CONFIGURATION ================
const char* wifi_ssid = "YOUR_WIFI_SSID";
const char* wifi_password = "YOUR_WIFI_PASSWORD";
const char* websocket_host = "your-teddy-server.com";
const int websocket_port = 443;
const char* websocket_path = "/ws/teddy";

// ================ HARDWARE PINS ================
#define BUTTON_TALK         12
#define LED_STATUS          2
#define LED_RECORDING       4
#define I2S_BCK_PIN         26
#define I2S_WS_PIN          25
#define I2S_DATA_PIN        33

// ================ AUDIO CONFIGURATION ================
#define SAMPLE_RATE         16000
#define BUFFER_SIZE         1024
#define RECORDING_DURATION  5000  // 5 seconds max

// ================ GLOBAL OBJECTS ================
AudioProcessor audioProcessor;
SecureConnectionManager sslManager;
WebSocketsClient webSocket;
WiFiClientSecure wifiClient;

// Audio recording
int16_t* audio_buffer;
std::vector<int16_t> recorded_audio;
bool is_recording = false;
unsigned long recording_start = 0;

// ================ SETUP ================
void setup() {
    Serial.begin(115200);
    delay(1000);
    
    Serial.println("🧸 AI Teddy Bear - Production Audio Example v3.0");
    Serial.println("   Features: Real Base64, Compression, Secure SSL");
    
    // Initialize hardware
    setup_hardware();
    
    // Initialize audio system
    setup_audio_system();
    
    // Test audio processor
    test_audio_processor();
    
    // Connect to WiFi
    connect_wifi();
    
    // Setup secure connection
    setup_secure_connection();
    
    // Initialize WebSocket
    setup_websocket();
    
    Serial.println("✅ System ready! Press TALK button to record audio.");
}

void setup_hardware() {
    Serial.println("🔧 Initializing hardware...");
    
    pinMode(BUTTON_TALK, INPUT_PULLUP);
    pinMode(LED_STATUS, OUTPUT);
    pinMode(LED_RECORDING, OUTPUT);
    
    digitalWrite(LED_STATUS, LOW);
    digitalWrite(LED_RECORDING, LOW);
    
    Serial.println("✅ Hardware initialized");
}

void setup_audio_system() {
    Serial.println("🎤 Initializing production audio system...");
    
    // Allocate audio buffer
    audio_buffer = (int16_t*)malloc(BUFFER_SIZE * sizeof(int16_t));
    if (!audio_buffer) {
        Serial.println("❌ Failed to allocate audio buffer");
        while(1);
    }
    
    // Configure I2S
    i2s_config_t i2s_config = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
        .sample_rate = SAMPLE_RATE,
        .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
        .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
        .communication_format = I2S_COMM_FORMAT_I2S,
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count = 4,
        .dma_buf_len = BUFFER_SIZE,
        .use_apll = true
    };
    
    i2s_pin_config_t pin_config = {
        .bck_io_num = I2S_BCK_PIN,
        .ws_io_num = I2S_WS_PIN,
        .data_out_num = I2S_PIN_NO_CHANGE,
        .data_in_num = I2S_DATA_PIN
    };
    
    // Install I2S driver
    esp_err_t err = i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL);
    if (err != ESP_OK) {
        Serial.printf("❌ I2S driver install failed: %s\n", esp_err_to_name(err));
        while(1);
    }
    
    err = i2s_set_pin(I2S_NUM_0, &pin_config);
    if (err != ESP_OK) {
        Serial.printf("❌ I2S pin setup failed: %s\n", esp_err_to_name(err));
        while(1);
    }
    
    Serial.println("✅ Audio system initialized");
}

void test_audio_processor() {
    Serial.println("🧪 Testing production audio processor...");
    
    // Run self-test
    if (!audioProcessor.selfTest()) {
        Serial.println("❌ CRITICAL: Audio processor self-test failed!");
        while(1);
    }
    
    // Run benchmark
    Serial.println("📊 Running performance benchmark...");
    audioProcessor.runBenchmark();
    
    Serial.println("✅ Audio processor ready for production use");
}

void connect_wifi() {
    Serial.printf("📡 Connecting to WiFi: %s\n", wifi_ssid);
    
    WiFi.mode(WIFI_STA);
    WiFi.begin(wifi_ssid, wifi_password);
    
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 20) {
        delay(500);
        Serial.print(".");
        attempts++;
        
        // Blink LED while connecting
        digitalWrite(LED_STATUS, attempts % 2);
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        Serial.printf("\n✅ WiFi connected! IP: %s\n", WiFi.localIP().toString().c_str());
        Serial.printf("📶 Signal strength: %d dBm\n", WiFi.RSSI());
        digitalWrite(LED_STATUS, HIGH);
    } else {
        Serial.println("\n❌ WiFi connection failed!");
        digitalWrite(LED_STATUS, LOW);
        while(1);
    }
}

void setup_secure_connection() {
    Serial.println("🔒 Setting up secure SSL connection...");
    
    // Setup secure connection (production mode by default)
    bool development_mode = false;
    
    #ifdef DEVELOPMENT
        development_mode = true;
        Serial.println("⚠️ DEVELOPMENT MODE: SSL validation may be disabled");
    #endif
    
    sslManager.setupSecureConnection(wifiClient, development_mode);
    
    // Verify SSL connection works
    if (sslManager.verifyConnection(wifiClient, websocket_host)) {
        Serial.println("✅ SSL connection verified successfully");
    } else {
        Serial.println("⚠️ SSL connection test failed - may still work during operation");
    }
    
    // Print SSL information
    String ssl_info = sslManager.getSSLInfo(wifiClient);
    Serial.printf("🔐 SSL Info: %s\n", ssl_info.c_str());
}

void setup_websocket() {
    Serial.println("🌐 Initializing WebSocket connection...");
    
    // Set WebSocket event handler
    webSocket.onEvent(webSocketEvent);
    
    // Configure heartbeat
    webSocket.enableHeartbeat(15000, 3000, 2);
    
    // Begin SSL WebSocket connection
    webSocket.beginSSL(websocket_host, websocket_port, websocket_path);
    
    Serial.println("✅ WebSocket initialized");
}

// ================ WEBSOCKET EVENT HANDLER ================
void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
    switch(type) {
        case WStype_DISCONNECTED:
            Serial.println("🔌 WebSocket disconnected");
            digitalWrite(LED_STATUS, LOW);
            break;
            
        case WStype_CONNECTED:
            Serial.printf("✅ WebSocket connected to: %s\n", payload);
            digitalWrite(LED_STATUS, HIGH);
            
            // Send initial metadata
            send_device_metadata();
            break;
            
        case WStype_TEXT:
            Serial.printf("📥 Received message: %.*s\n", length, payload);
            handle_server_response((char*)payload, length);
            break;
            
        case WStype_BIN:
            Serial.printf("📦 Received binary data: %d bytes\n", length);
            // Handle binary response (e.g., TTS audio)
            break;
            
        case WStype_ERROR:
            Serial.printf("❌ WebSocket error: %.*s\n", length, payload);
            break;
            
        default:
            break;
    }
}

void send_device_metadata() {
    StaticJsonDocument<512> doc;
    doc["type"] = "device_metadata";
    doc["device_id"] = WiFi.macAddress();
    doc["firmware_version"] = AUDIO_PROCESSOR_VERSION;
    doc["build_date"] = AUDIO_PROCESSOR_BUILD_DATE;
    doc["sample_rate"] = SAMPLE_RATE;
    doc["buffer_size"] = BUFFER_SIZE;
    
    // Add compression capabilities
    JsonObject compression = doc.createNestedObject("compression");
    compression["enabled"] = true;
    compression["algorithm"] = "RLE_silence";
    
    // Add system info
    JsonObject system = doc.createNestedObject("system");
    system["free_heap"] = ESP.getFreeHeap();
    system["psram_available"] = psramFound();
    if (psramFound()) {
        system["free_psram"] = ESP.getFreePsram();
    }
    
    String message;
    serializeJson(doc, message);
    
    webSocket.sendTXT(message);
    Serial.println("📤 Device metadata sent");
}

void handle_server_response(char* message, size_t length) {
    StaticJsonDocument<1024> doc;
    DeserializationError error = deserializeJson(doc, message, length);
    
    if (error) {
        Serial.printf("❌ JSON parse error: %s\n", error.c_str());
        return;
    }
    
    String type = doc["type"] | "";
    
    if (type == "ai_response") {
        String text = doc["text"] | "";
        String emotion = doc["emotion"] | "neutral";
        
        Serial.printf("🤖 AI Response: %s (emotion: %s)\n", text.c_str(), emotion.c_str());
        
        // Visual feedback based on emotion
        if (emotion == "happy") {
            flash_led(LED_STATUS, 3, 200);
        } else if (emotion == "sad") {
            flash_led(LED_STATUS, 1, 1000);
        }
    } else if (type == "error") {
        String error_msg = doc["message"] | "Unknown error";
        Serial.printf("🚨 Server error: %s\n", error_msg.c_str());
        flash_led(LED_STATUS, 5, 100); // Fast error blink
    }
}

// ================ MAIN LOOP ================
void loop() {
    // Handle WebSocket events
    webSocket.loop();
    
    // Handle button presses
    handle_button_input();
    
    // Process audio recording
    if (is_recording) {
        process_audio_recording();
    }
    
    // Print diagnostics periodically
    static unsigned long last_diag = 0;
    if (millis() - last_diag > 30000) { // Every 30 seconds
        print_system_diagnostics();
        last_diag = millis();
    }
    
    delay(10);
}

void handle_button_input() {
    static bool button_pressed = false;
    static unsigned long last_press = 0;
    
    bool current_state = digitalRead(BUTTON_TALK) == LOW;
    
    // Button press (with debounce)
    if (current_state && !button_pressed && (millis() - last_press > 100)) {
        start_recording();
        button_pressed = true;
        last_press = millis();
    }
    
    // Button release
    if (!current_state && button_pressed) {
        stop_recording();
        button_pressed = false;
    }
}

// ================ AUDIO RECORDING ================
void start_recording() {
    if (is_recording) return;
    
    Serial.println("🎤 Starting enhanced audio recording...");
    
    // Clear previous recording
    recorded_audio.clear();
    recorded_audio.reserve(SAMPLE_RATE * (RECORDING_DURATION / 1000)); // Pre-allocate
    
    is_recording = true;
    recording_start = millis();
    
    digitalWrite(LED_RECORDING, HIGH);
    
    // Reset audio processor stats for this session
    audioProcessor.resetStats();
}

void process_audio_recording() {
    if (!is_recording) return;
    
    // Check for timeout
    if (millis() - recording_start > RECORDING_DURATION) {
        Serial.println("⏰ Recording timeout - stopping");
        stop_recording();
        return;
    }
    
    // Read audio data from I2S
    size_t bytes_read = 0;
    esp_err_t err = i2s_read(I2S_NUM_0, audio_buffer, 
                            BUFFER_SIZE * sizeof(int16_t), &bytes_read, 100);
    
    if (err == ESP_OK && bytes_read > 0) {
        size_t samples_read = bytes_read / sizeof(int16_t);
        
        // Add to recorded audio
        for (size_t i = 0; i < samples_read; i++) {
            recorded_audio.push_back(audio_buffer[i]);
        }
        
        // Check for silence (simple voice activity detection)
        if (recorded_audio.size() > SAMPLE_RATE && is_silence_detected()) {
            Serial.println("🔇 Silence detected - stopping recording");
            stop_recording();
        }
    }
}

bool is_silence_detected() {
    if (recorded_audio.size() < SAMPLE_RATE) return false;
    
    // Check last 0.5 seconds for silence
    size_t samples_to_check = SAMPLE_RATE / 2;
    size_t start_idx = recorded_audio.size() - samples_to_check;
    
    float avg_amplitude = 0;
    for (size_t i = start_idx; i < recorded_audio.size(); i++) {
        avg_amplitude += abs(recorded_audio[i]);
    }
    avg_amplitude /= samples_to_check;
    
    return avg_amplitude < 50; // Adjust threshold as needed
}

void stop_recording() {
    if (!is_recording) return;
    
    is_recording = false;
    digitalWrite(LED_RECORDING, LOW);
    
    unsigned long duration = millis() - recording_start;
    Serial.printf("🛑 Recording stopped: %d samples in %lu ms\n", 
                  recorded_audio.size(), duration);
    
    if (recorded_audio.size() > 0) {
        send_audio_to_server();
    } else {
        Serial.println("❌ No audio recorded");
    }
}

// ================ AUDIO TRANSMISSION ================
void send_audio_to_server() {
    if (!webSocket.isConnected()) {
        Serial.println("❌ WebSocket not connected - cannot send audio");
        return;
    }
    
    Serial.println("☁️ Processing and sending audio to server...");
    
    unsigned long start_time = millis();
    
    // Use production audio processor to encode with compression
    String encoded_audio = audioProcessor.encodeAudioBase64(
        recorded_audio.data(), recorded_audio.size()
    );
    
    if (encoded_audio.length() == 0) {
        Serial.println("❌ Failed to encode audio");
        return;
    }
    
    // Get compression statistics
    CompressionStats stats = audioProcessor.getStats();
    
    // Create enhanced JSON payload
    StaticJsonDocument<2048> doc;
    doc["type"] = "audio_data";
    doc["device_id"] = WiFi.macAddress();
    doc["timestamp"] = millis();
    doc["sample_rate"] = SAMPLE_RATE;
    doc["sample_count"] = recorded_audio.size();
    doc["duration_ms"] = (recorded_audio.size() * 1000) / SAMPLE_RATE;
    doc["audio_data"] = encoded_audio;
    
    // Compression metadata
    JsonObject compression = doc.createNestedObject("compression");
    compression["enabled"] = true;
    compression["algorithm"] = "RLE_silence";
    compression["ratio"] = stats.last_compression_ratio;
    compression["encoding_time_ms"] = stats.encoding_time_ms;
    compression["silence_regions"] = stats.silence_regions_compressed;
    
    // Performance metrics
    JsonObject performance = doc.createNestedObject("performance");
    performance["total_processing_time_ms"] = millis() - start_time;
    performance["bandwidth_savings_percent"] = calculateBandwidthSavings(stats);
    
    String message;
    serializeJson(doc, message);
    
    // Send to server
    bool sent = webSocket.sendTXT(message);
    
    if (sent) {
        Serial.printf("✅ Audio sent successfully!\n");
        Serial.printf("📊 Stats: %.2fx compression, %lu ms encoding, %.1f%% bandwidth savings\n",
                     stats.last_compression_ratio, stats.encoding_time_ms, 
                     calculateBandwidthSavings(stats));
        
        // Success blink
        flash_led(LED_STATUS, 2, 300);
    } else {
        Serial.println("❌ Failed to send audio");
        flash_led(LED_STATUS, 5, 100); // Error blink
    }
}

// ================ UTILITY FUNCTIONS ================
void flash_led(int led_pin, int count, int delay_ms) {
    for (int i = 0; i < count; i++) {
        digitalWrite(led_pin, HIGH);
        delay(delay_ms);
        digitalWrite(led_pin, LOW);
        delay(delay_ms);
    }
}

void print_system_diagnostics() {
    Serial.println("\n📊 === System Diagnostics ===");
    
    // System info
    Serial.printf("💾 Free heap: %d bytes\n", ESP.getFreeHeap());
    if (psramFound()) {
        Serial.printf("💾 Free PSRAM: %d bytes\n", ESP.getFreePsram());
    }
    Serial.printf("📶 WiFi RSSI: %d dBm\n", WiFi.RSSI());
    Serial.printf("🔌 WebSocket connected: %s\n", webSocket.isConnected() ? "Yes" : "No");
    Serial.printf("⏱️ Uptime: %lu seconds\n", millis() / 1000);
    
    // Audio processor diagnostics
    audioProcessor.printDiagnostics();
    
    // Performance check
    CompressionStats stats = audioProcessor.getStats();
    if (stats.total_processed > 0) {
        if (isPerformanceAcceptable(stats)) {
            Serial.println("✅ Performance: ACCEPTABLE");
        } else {
            Serial.println("⚠️ Performance: DEGRADED - consider optimization");
        }
    }
    
    Serial.println("================================\n");
} 