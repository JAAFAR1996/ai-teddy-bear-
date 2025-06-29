/*
🧸 AI Teddy Bear - Enhanced ESP32 with MP3 Audio Compression v3.0
Advanced audio compression using ESP Audio Codec and Shine MP3 encoder
Optimized for bandwidth efficiency and audio quality
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

// ================ AUDIO COMPRESSION LIBRARIES ================
#include <esp_heap_caps.h>

// MP3 Encoding Options - Choose one:
#define USE_ESP_AUDIO_CODEC 1  // Official Espressif codec (recommended)
#define USE_SHINE_ENCODER 0    // Lightweight alternative

#if USE_ESP_AUDIO_CODEC
  // ESP Audio Codec includes (install via ESP-IDF Component Manager)
  // idf.py add-dependency "espressif/esp_audio_codec^1.0.0"
  #include "esp_audio_enc.h"
  #include "esp_audio_codec_lib.h"
  #include "audio_encoder.h"
#elif USE_SHINE_ENCODER
  // Shine MP3 encoder includes (lightweight alternative)
  // Download from: https://github.com/savonet/shine
  #include "shine_mp3_encoder.h"
#endif

// ================ ENHANCED CONFIGURATION ================
Preferences preferences;
WiFiClientSecure client;

// Configuration keys
const char* WIFI_SSID_KEY = "wifi_ssid";
const char* WIFI_PASS_KEY = "wifi_pass";  
const char* SERVER_URL_KEY = "server_url";
const char* DEVICE_ID_KEY = "device_id";
const char* API_KEY_KEY = "api_key";
const char* AUDIO_QUALITY_KEY = "audio_quality";
const char* COMPRESSION_LEVEL_KEY = "compression_level";

// Network settings
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

// ================ ENHANCED AUDIO CONFIGURATION ================
const int SAMPLE_RATE = 16000;           // Optimized for speech
const int BITS_PER_SAMPLE = 16;
const int AUDIO_BUFFER_SIZE = 2048;      // Increased for MP3 encoding
const int MAX_AUDIO_DURATION = 15;       // Extended recording time
const int VOLUME_LEVELS = 10;

// MP3 Encoding Settings
const int MP3_BITRATE = 96;              // kbps (64-128 range for good quality/size balance)
const int MP3_QUALITY = 5;               // 0=best quality, 9=worst quality
const int COMPRESSION_BUFFER_SIZE = 4096; // For encoded data

// Advanced Memory Management
const size_t PSRAM_AUDIO_BUFFER_SIZE = 32768;  // Use PSRAM if available
const size_t MAX_COMPRESSED_SIZE = 16384;       // Max compressed audio size

// State variables
bool wifi_connected = false;
bool server_connected = false;
int current_volume = 5;
bool is_listening = false;
bool is_processing = false;
bool is_encoding = false;
unsigned long last_heartbeat = 0;
unsigned long last_activity = 0;
const unsigned long SLEEP_TIMEOUT = 300000;     // 5 minutes
const unsigned long HEARTBEAT_INTERVAL = 30000; // 30 seconds

// Enhanced audio buffers
int16_t* audio_buffer;
uint8_t* compressed_buffer;
std::vector<int16_t> recorded_audio;
size_t compressed_size = 0;

// Audio encoder instance
#if USE_ESP_AUDIO_CODEC
  audio_encoder_handle_t encoder_handle = NULL;
#elif USE_SHINE_ENCODER
  shine_t shine_encoder = NULL;
#endif

// Performance monitoring structure
struct AudioStats {
  size_t raw_bytes = 0;
  size_t compressed_bytes = 0;
  float compression_ratio = 0.0;
  unsigned long encoding_time_ms = 0;
  unsigned long total_processing_time_ms = 0;
  bool encoding_success = false;
};

AudioStats current_stats;

// ================ INITIALIZATION ================

void setup() {
    Serial.begin(115200);
    delay(1000);
    
    Serial.println("\n🧸 AI Teddy Bear - Enhanced MP3 Version v3.0");
    Serial.println("============================================");
    
    // Check PSRAM availability
    check_psram_support();
    
    // Initialize hardware
    init_hardware();
    
    // Load configuration
    load_configuration();
    
    // Generate device ID if not exists
    if (device_id.isEmpty()) {
        generate_device_id();
    }
    
    Serial.printf("Device ID: %s\n", device_id.c_str());
    
    // Initialize enhanced audio system
    init_enhanced_audio();
    
    // Initialize MP3 encoder
    init_mp3_encoder();
    
    // Initialize WiFi
    init_wifi();
    
    // Setup SSL
    setup_ssl();
    
    // Test server connection
    test_server_connection();
    
    Serial.println("🧸 Enhanced Teddy Bear ready! Press TALK button to start MP3 recording.");
    set_status_led(true, false, false); // Green = ready
}

void check_psram_support() {
    if (psramFound()) {
        Serial.printf("✅ PSRAM found: %d bytes\n", ESP.getPsramSize());
        Serial.printf("✅ Free PSRAM: %d bytes\n", ESP.getFreePsram());
    } else {
        Serial.println("⚠️ No PSRAM found - using internal RAM only");
        Serial.println("💡 Consider using ESP32-S3 with PSRAM for better performance");
    }
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
    
    wifi_ssid = preferences.getString(WIFI_SSID_KEY, "");
    wifi_password = preferences.getString(WIFI_PASS_KEY, "");
    server_url = preferences.getString(SERVER_URL_KEY, "https://teddy-cloud.example.com");
    device_id = preferences.getString(DEVICE_ID_KEY, "");
    api_key = preferences.getString(API_KEY_KEY, "");
    current_volume = preferences.getInt("volume", 5);
    
    Serial.println("✅ Configuration loaded from NVS");
    
    if (wifi_ssid.isEmpty()) {
        Serial.println("⚠️ No WiFi credentials found. Entering configuration mode...");
        enter_config_mode();
    }
}

void init_enhanced_audio() {
    // Allocate audio buffers with PSRAM if available
    if (psramFound()) {
        audio_buffer = (int16_t*)heap_caps_malloc(PSRAM_AUDIO_BUFFER_SIZE, MALLOC_CAP_SPIRAM);
        compressed_buffer = (uint8_t*)heap_caps_malloc(MAX_COMPRESSED_SIZE, MALLOC_CAP_SPIRAM);
        Serial.println("✅ Audio buffers allocated in PSRAM");
    } else {
        audio_buffer = (int16_t*)malloc(AUDIO_BUFFER_SIZE * sizeof(int16_t));
        compressed_buffer = (uint8_t*)malloc(MAX_COMPRESSED_SIZE);
        Serial.println("✅ Audio buffers allocated in internal RAM");
    }
    
    if (!audio_buffer || !compressed_buffer) {
        Serial.println("❌ Failed to allocate audio buffers!");
        handle_critical_error("Audio buffer allocation failed");
        return;
    }
    
    // Configure I2S for enhanced audio recording
    i2s_config_t i2s_config = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
        .sample_rate = SAMPLE_RATE,
        .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
        .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
        .communication_format = I2S_COMM_FORMAT_I2S,
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count = 8,              // Increased for better performance
        .dma_buf_len = AUDIO_BUFFER_SIZE,
        .use_apll = true,                // Use APLL for better precision
        .tx_desc_auto_clear = false,
        .fixed_mclk = 0
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
    
    Serial.println("✅ Enhanced audio system initialized");
}

void init_mp3_encoder() {
    Serial.println("🎵 Initializing MP3 encoder...");
    
#if USE_ESP_AUDIO_CODEC
    // Initialize ESP Audio Codec
    audio_encoder_cfg_t enc_cfg = {
        .type = AUDIO_ENCODER_MP3,
        .sample_rate = SAMPLE_RATE,
        .channel = 1,                    // Mono
        .bit_rate = MP3_BITRATE * 1000,  // Convert to bps
        .quality = MP3_QUALITY,
        .complexity = 5                   // Encoding complexity
    };
    
    esp_err_t ret = audio_encoder_new(&enc_cfg, &encoder_handle);
    if (ret != ESP_OK) {
        Serial.printf("❌ ESP Audio Codec init failed: %s\n", esp_err_to_name(ret));
        Serial.println("⚠️ Falling back to uncompressed audio");
        encoder_handle = NULL;
    } else {
        Serial.println("✅ ESP Audio Codec MP3 encoder initialized");
        Serial.printf("   Bitrate: %d kbps\n", MP3_BITRATE);
        Serial.printf("   Quality: %d\n", MP3_QUALITY);
    }
    
#elif USE_SHINE_ENCODER
    // Initialize Shine MP3 encoder (lightweight alternative)
    shine_config_t config;
    shine_set_config_mpeg_defaults(&config.mpeg);
    
    config.mpeg.bitr = MP3_BITRATE;
    config.mpeg.mode = MONO;
    config.mpeg.emph = NONE;
    config.wave.samplerate = SAMPLE_RATE;
    config.wave.channels = 1;
    
    if (shine_check_config(config.wave.samplerate, config.mpeg.bitr) < 0) {
        Serial.println("❌ Shine encoder config invalid");
        shine_encoder = NULL;
    } else {
        shine_encoder = shine_initialise(&config);
        if (!shine_encoder) {
            Serial.println("❌ Shine encoder initialization failed");
        } else {
            Serial.println("✅ Shine MP3 encoder initialized");
            Serial.printf("   Bitrate: %d kbps\n", MP3_BITRATE);
        }
    }
#else
    Serial.println("⚠️ No MP3 encoder enabled - using uncompressed audio");
#endif

    // Test encoder with silence
    if (!test_encoder()) {
        Serial.println("⚠️ MP3 encoder test failed - using uncompressed audio");
    }
}

bool test_encoder() {
    Serial.println("🧪 Testing MP3 encoder...");
    
    // Create test audio (silence)
    int16_t test_samples[1024];
    memset(test_samples, 0, sizeof(test_samples));
    
    size_t encoded_size = 0;
    bool success = encode_audio_chunk(test_samples, 1024, compressed_buffer, &encoded_size);
    
    if (success && encoded_size > 0) {
        float test_ratio = (float)sizeof(test_samples) / encoded_size;
        Serial.printf("✅ Encoder test passed - Compression ratio: %.2fx\n", test_ratio);
        return true;
    } else {
        Serial.println("❌ Encoder test failed");
        return false;
    }
}

// ================ ENHANCED AUDIO RECORDING ================

void start_recording() {
    is_listening = true;
    is_encoding = false;
    recorded_audio.clear();
    compressed_size = 0;
    
    // Reset performance stats
    current_stats = AudioStats();
    
    set_status_led(false, true, false); // Blue = listening
    Serial.println("🎤 Enhanced MP3 recording started... (speak now)");
    
    unsigned long start_time = millis();
    size_t bytes_read = 0;
    
    while (millis() - start_time < MAX_AUDIO_DURATION * 1000) {
        // Read audio data with larger chunks
        esp_err_t err = i2s_read(I2S_NUM_0, audio_buffer, 
                                AUDIO_BUFFER_SIZE * sizeof(int16_t), 
                                &bytes_read, 100);
        
        if (err == ESP_OK && bytes_read > 0) {
            int samples = bytes_read / sizeof(int16_t);
            
            // Add to recorded audio
            for (int i = 0; i < samples; i++) {
                recorded_audio.push_back(audio_buffer[i]);
            }
            
            current_stats.raw_bytes += bytes_read;
            
            // Apply real-time audio enhancements
            apply_audio_enhancements(audio_buffer, samples);
        }
        
        // Advanced voice activity detection
        if (is_advanced_silence_detected()) {
            Serial.println("🔇 Advanced silence detected - stopping recording");
            break;
        }
        
        // Check button release
        if (digitalRead(BUTTON_TALK) == HIGH) {
            Serial.println("🛑 Talk button released - stopping recording");
            break;
        }
        
        // Memory usage check
        if (recorded_audio.size() > PSRAM_AUDIO_BUFFER_SIZE / sizeof(int16_t)) {
            Serial.println("⚠️ Audio buffer full - stopping recording");
            break;
        }
    }
    
    is_listening = false;
    set_status_led(false, false, false);
    
    Serial.printf("✅ Recording complete: %d samples (%.2f seconds)\n", 
                  recorded_audio.size(), 
                  (float)recorded_audio.size() / SAMPLE_RATE);
    
    if (recorded_audio.size() > 0) {
        process_enhanced_audio();
    } else {
        Serial.println("❌ No audio recorded");
    }
}

void apply_audio_enhancements(int16_t* samples, int count) {
    // Simple noise gate
    const int16_t noise_threshold = 100;
    
    for (int i = 0; i < count; i++) {
        if (abs(samples[i]) < noise_threshold) {
            samples[i] = 0; // Remove low-level noise
        }
    }
    
    // Additional enhancements can be added here:
    // - High-pass filter for speech
    // - Automatic gain control
    // - Dynamic range compression
}

bool is_advanced_silence_detected() {
    if (recorded_audio.size() < SAMPLE_RATE) return false;
    
    // Check last 1 second for silence
    int samples_to_check = SAMPLE_RATE;
    int start_idx = recorded_audio.size() - samples_to_check;
    
    float energy = 0;
    float zero_crossing_rate = 0;
    
    for (int i = start_idx; i < recorded_audio.size() - 1; i++) {
        energy += abs(recorded_audio[i]);
        
        // Zero crossing rate calculation
        if ((recorded_audio[i] >= 0) != (recorded_audio[i + 1] >= 0)) {
            zero_crossing_rate++;
        }
    }
    
    energy /= samples_to_check;
    zero_crossing_rate /= samples_to_check;
    
    // Advanced silence detection using energy and spectral features
    return (energy < 150 && zero_crossing_rate < 0.1);
}

// ================ MP3 ENCODING FUNCTIONS ================

bool encode_audio_chunk(int16_t* input_samples, size_t sample_count, 
                       uint8_t* output_buffer, size_t* output_size) {
    if (!output_buffer || !output_size) return false;
    
    *output_size = 0;
    
#if USE_ESP_AUDIO_CODEC
    if (!encoder_handle) return false;
    
    audio_encoder_input_t input_data = {
        .buffer = (uint8_t*)input_samples,
        .len = sample_count * sizeof(int16_t)
    };
    
    audio_encoder_output_t output_data = {
        .buffer = output_buffer,
        .len = MAX_COMPRESSED_SIZE
    };
    
    esp_err_t ret = audio_encoder_process(encoder_handle, &input_data, &output_data);
    if (ret == ESP_OK) {
        *output_size = output_data.len;
        return true;
    }
    
#elif USE_SHINE_ENCODER
    if (!shine_encoder) return false;
    
    int samples_per_pass = shine_samples_per_pass(shine_encoder);
    
    if (sample_count >= samples_per_pass) {
        long encoded_bytes = shine_encode_buffer_interleaved(
            shine_encoder, input_samples, (unsigned char*)output_buffer);
        
        if (encoded_bytes > 0) {
            *output_size = encoded_bytes;
            return true;
        }
    }
#endif

    return false;
}

void process_enhanced_audio() {
    if (!server_connected) {
        Serial.println("❌ No server connection");
        return;
    }
    
    is_processing = true;
    is_encoding = true;
    set_status_led(true, false, true); // Yellow = encoding
    
    unsigned long encoding_start = millis();
    
    Serial.println("🎵 Starting MP3 encoding...");
    
    // Convert recorded audio to compressed format
    String encoded_audio = "";
    bool encoding_success = false;
    
#if USE_ESP_AUDIO_CODEC || USE_SHINE_ENCODER
    // Compress audio in chunks
    size_t total_compressed = 0;
    const size_t chunk_size = 1152; // MP3 frame size
    
    for (size_t i = 0; i < recorded_audio.size(); i += chunk_size) {
        size_t samples_in_chunk = min(chunk_size, recorded_audio.size() - i);
        size_t chunk_encoded_size = 0;
        
        bool chunk_success = encode_audio_chunk(
            &recorded_audio[i], 
            samples_in_chunk,
            compressed_buffer + total_compressed,
            &chunk_encoded_size
        );
        
        if (chunk_success) {
            total_compressed += chunk_encoded_size;
            encoding_success = true;
        } else {
            Serial.printf("⚠️ Failed to encode chunk %d\n", i / chunk_size);
        }
        
        // Prevent buffer overflow
        if (total_compressed >= MAX_COMPRESSED_SIZE - 1000) {
            Serial.println("⚠️ Compressed buffer nearly full - stopping encoding");
            break;
        }
    }
    
    compressed_size = total_compressed;
    current_stats.compressed_bytes = compressed_size;
    current_stats.encoding_success = encoding_success;
    
    if (encoding_success && compressed_size > 0) {
        // Convert to base64
        encoded_audio = encode_mp3_base64(compressed_buffer, compressed_size);
        Serial.printf("✅ MP3 encoding complete: %d bytes -> %d bytes (%.1fx compression)\n", 
                     current_stats.raw_bytes, compressed_size,
                     (float)current_stats.raw_bytes / compressed_size);
    } else {
        Serial.println("❌ MP3 encoding failed - using uncompressed audio");
        encoded_audio = encode_pcm_base64();
    }
#else
    // Fallback to uncompressed audio
    encoded_audio = encode_pcm_base64();
    encoding_success = false;
#endif
    
    current_stats.encoding_time_ms = millis() - encoding_start;
    current_stats.compression_ratio = (float)current_stats.raw_bytes / 
                                     max(current_stats.compressed_bytes, 1UL);
    
    is_encoding = false;
    set_status_led(false, false, true); // Red = processing
    
    // Send to cloud
    send_compressed_audio_to_cloud(encoded_audio, encoding_success);
    
    is_processing = false;
    set_status_led(true, false, false); // Green = ready
}

String encode_mp3_base64(uint8_t* mp3_data, size_t size) {
    if (!mp3_data || size == 0) return "";
    
    // Base64 encoding for MP3 data
    const char* chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
    String result = "";
    result.reserve((size * 4) / 3 + 4);
    
    for (size_t i = 0; i < size; i += 3) {
        uint32_t val = mp3_data[i] << 16;
        if (i + 1 < size) val |= mp3_data[i + 1] << 8;
        if (i + 2 < size) val |= mp3_data[i + 2];
        
        result += chars[(val >> 18) & 0x3F];
        result += chars[(val >> 12) & 0x3F];
        result += chars[(val >> 6) & 0x3F];
        result += chars[val & 0x3F];
    }
    
    // Add padding
    while (result.length() % 4) {
        result += '=';
    }
    
    return result;
}

String encode_pcm_base64() {
    // Fallback PCM encoding (simplified for demo)
    return "pcm_fallback_audio_data";
}

void send_compressed_audio_to_cloud(String encoded_audio, bool is_compressed) {
    Serial.println("☁️ Sending enhanced audio to cloud...");
    
    unsigned long send_start = millis();
    
    // Create enhanced JSON payload
    DynamicJsonDocument doc(12288); // Larger buffer for metadata
    doc["device_id"] = device_id;
    doc["session_id"] = "session_" + String(millis());
    
    // Audio format information
    if (is_compressed) {
        doc["audio_format"] = "mp3_compressed";
        doc["bitrate"] = MP3_BITRATE;
        doc["compression_ratio"] = current_stats.compression_ratio;
    } else {
        doc["audio_format"] = "pcm_16000";
    }
    
    doc["audio_data"] = encoded_audio;
    doc["timestamp"] = millis();
    doc["volume_level"] = current_volume;
    
    // Performance metadata
    JsonObject perf = doc.createNestedObject("performance");
    perf["raw_bytes"] = current_stats.raw_bytes;
    perf["compressed_bytes"] = current_stats.compressed_bytes;
    perf["encoding_time_ms"] = current_stats.encoding_time_ms;
    perf["encoding_success"] = current_stats.encoding_success;
    perf["sample_rate"] = SAMPLE_RATE;
    perf["duration_seconds"] = (float)recorded_audio.size() / SAMPLE_RATE;
    
    // System information
    JsonObject system = doc.createNestedObject("system");
    system["free_heap"] = ESP.getFreeHeap();
    system["psram_available"] = psramFound();
    if (psramFound()) {
        system["free_psram"] = ESP.getFreePsram();
    }
    system["cpu_freq"] = ESP.getCpuFreqMHz();
    
    String json_payload;
    serializeJson(doc, json_payload);
    
    // Send to server
    HTTPClient http;
    http.begin(client, server_url + "/esp32/audio");
    http.addHeader("Content-Type", "application/json");
    http.addHeader("Authorization", "Bearer " + api_key);
    http.addHeader("X-Audio-Format", is_compressed ? "mp3" : "pcm");
    http.addHeader("X-Compression-Ratio", String(current_stats.compression_ratio, 2));
    http.setTimeout(30000); // Extended timeout for compressed audio
    
    int response_code = http.POST(json_payload);
    
    current_stats.total_processing_time_ms = millis() - send_start + current_stats.encoding_time_ms;
    
    if (response_code == 200) {
        String response = http.getString();
        handle_enhanced_cloud_response(response);
        
        Serial.printf("📊 Performance Summary:\n");
        Serial.printf("   Raw audio: %d bytes\n", current_stats.raw_bytes);
        Serial.printf("   Compressed: %d bytes\n", current_stats.compressed_bytes);
        Serial.printf("   Compression ratio: %.2fx\n", current_stats.compression_ratio);
        Serial.printf("   Encoding time: %lu ms\n", current_stats.encoding_time_ms);
        Serial.printf("   Total time: %lu ms\n", current_stats.total_processing_time_ms);
        Serial.printf("   Bandwidth savings: %.1f%%\n", 
                     (1.0 - (float)current_stats.compressed_bytes / current_stats.raw_bytes) * 100.0);
        
    } else {
        Serial.printf("❌ Server error: %d\n", response_code);
        set_status_led(true, false, true); // Yellow = error
        delay(2000);
    }
    
    http.end();
}

void handle_enhanced_cloud_response(String response) {
    Serial.println("📥 Received enhanced response from cloud:");
    
    DynamicJsonDocument doc(4096);
    deserializeJson(doc, response);
    
    String transcription = doc["transcription"];
    JsonObject ai_response = doc["ai_response"];
    String response_text = ai_response["text"];
    String emotion = ai_response["emotion"];
    
    // Enhanced response handling
    JsonObject performance = doc["performance"];
    if (!performance.isNull()) {
        Serial.printf("🚀 Server processing time: %d ms\n", 
                     performance["processing_time_ms"].as<int>());
    }
    
    Serial.printf("🎯 Transcription: %s\n", transcription.c_str());
    Serial.printf("🧸 AI Response: %s\n", response_text.c_str());
    Serial.printf("😊 Emotion: %s\n", emotion.c_str());
    
    play_enhanced_response(response_text, emotion);
}

void play_enhanced_response(String text, String emotion) {
    Serial.println("🔊 Playing enhanced response...");
    
    // Enhanced LED patterns based on emotion
    if (emotion == "happy") {
        animate_led_pattern(1); // Happy pattern
    } else if (emotion == "sad") {
        animate_led_pattern(2); // Sad pattern
    } else if (emotion == "excited") {
        animate_led_pattern(3); // Excited pattern
    } else {
        set_status_led(true, false, false); // Default green
    }
    
    // TODO: Implement enhanced TTS playback with emotion
    delay(3000);
    
    set_status_led(true, false, false); // Back to ready
    Serial.println("✅ Enhanced response played");
}

void animate_led_pattern(int pattern) {
    switch (pattern) {
        case 1: // Happy - quick green blinks
            for (int i = 0; i < 3; i++) {
                set_status_led(true, false, false);
                delay(200);
                set_status_led(false, false, false);
                delay(200);
            }
            break;
            
        case 2: // Sad - slow blue pulse
            for (int i = 0; i < 2; i++) {
                set_status_led(false, true, false);
                delay(800);
                set_status_led(false, false, false);
                delay(400);
            }
            break;
            
        case 3: // Excited - rainbow effect
            for (int i = 0; i < 2; i++) {
                set_status_led(true, false, false); delay(150);
                set_status_led(false, true, false); delay(150);
                set_status_led(false, false, true); delay(150);
                set_status_led(true, true, false); delay(150);
            }
            break;
    }
}

// ================ MAIN LOOP & BUTTON HANDLING ================

void loop() {
    update_activity();
    handle_buttons();
    
    // Performance monitoring
    if (millis() % 10000 == 0) { // Every 10 seconds
        print_system_status();
    }
    
    // Send heartbeat
    if (millis() - last_heartbeat > HEARTBEAT_INTERVAL) {
        send_enhanced_heartbeat();
        last_heartbeat = millis();
    }
    
    // Sleep timeout
    if (millis() - last_activity > SLEEP_TIMEOUT) {
        Serial.println("💤 Entering enhanced sleep mode...");
        cleanup_before_sleep();
        enter_deep_sleep(300);
    }
    
    delay(100);
}

void update_activity() {
    last_activity = millis();
}

void handle_buttons() {
    // Talk button with enhanced handling
    if (digitalRead(BUTTON_TALK) == LOW) {
        delay(50); // Debounce
        if (digitalRead(BUTTON_TALK) == LOW) {
            handle_enhanced_talk_button();
            while (digitalRead(BUTTON_TALK) == LOW) delay(10);
        }
    }
    
    // Volume buttons
    if (digitalRead(BUTTON_VOLUME_UP) == LOW) {
        delay(50);
        if (digitalRead(BUTTON_VOLUME_UP) == LOW) {
            adjust_volume(1);
            while (digitalRead(BUTTON_VOLUME_UP) == LOW) delay(10);
        }
    }
    
    if (digitalRead(BUTTON_VOLUME_DOWN) == LOW) {
        delay(50);
        if (digitalRead(BUTTON_VOLUME_DOWN) == LOW) {
            adjust_volume(-1);
            while (digitalRead(BUTTON_VOLUME_DOWN) == LOW) delay(10);
        }
    }
}

void handle_enhanced_talk_button() {
    update_activity();
    
    if (!wifi_connected) {
        Serial.println("❌ No WiFi connection");
        set_status_led(false, false, true);
        return;
    }
    
    if (is_listening || is_processing || is_encoding) {
        Serial.println("⚠️ System busy - please wait...");
        return;
    }
    
    Serial.println("🎤 Enhanced talk button pressed - Starting MP3 recording...");
    start_recording();
}

void adjust_volume(int delta) {
    current_volume += delta;
    current_volume = constrain(current_volume, 0, VOLUME_LEVELS);
    
    Serial.printf("🔊 Volume: %d/%d\n", current_volume, VOLUME_LEVELS);
    preferences.putInt("volume", current_volume);
    
    // Enhanced volume feedback
    for (int i = 0; i <= current_volume; i++) {
        set_status_led(true, false, false);
        delay(100);
        set_status_led(false, false, false);
        delay(100);
    }
}

// ================ UTILITY AND MAINTENANCE FUNCTIONS ================

void print_system_status() {
    Serial.println("📊 Enhanced System Status:");
    Serial.printf("   Free heap: %d bytes\n", ESP.getFreeHeap());
    Serial.printf("   WiFi RSSI: %d dBm\n", WiFi.RSSI());
    
    if (psramFound()) {
        Serial.printf("   Free PSRAM: %d bytes\n", ESP.getFreePsram());
    }
    
    Serial.printf("   Uptime: %lu seconds\n", millis() / 1000);
    Serial.printf("   CPU frequency: %d MHz\n", ESP.getCpuFreqMHz());
}

void send_enhanced_heartbeat() {
    if (!wifi_connected) return;
    
    HTTPClient http;
    http.begin(client, server_url + "/esp32/heartbeat");
    http.addHeader("Content-Type", "application/json");
    http.addHeader("Authorization", "Bearer " + api_key);
    
    DynamicJsonDocument doc(1024);
    doc["device_id"] = device_id;
    doc["status"] = "online";
    doc["battery_level"] = get_battery_level();
    doc["wifi_strength"] = WiFi.RSSI();
    doc["uptime"] = millis();
    doc["firmware_version"] = "3.0.0-mp3-enhanced";
    doc["volume"] = current_volume;
    doc["audio_format"] = "mp3_capable";
    doc["compression_available"] = true;
    
    // System health
    JsonObject health = doc.createNestedObject("health");
    health["free_heap"] = ESP.getFreeHeap();
    health["psram_available"] = psramFound();
    if (psramFound()) {
        health["free_psram"] = ESP.getFreePsram();
    }
    
    String payload;
    serializeJson(doc, payload);
    
    int response_code = http.POST(payload);
    if (response_code == 200) {
        server_connected = true;
    } else {
        server_connected = false;
        Serial.printf("❌ Enhanced heartbeat failed: %d\n", response_code);
    }
    
    http.end();
}

void generate_device_id() {
    uint64_t mac = ESP.getEfuseMac();
    device_id = "ESP32_TEDDY_MP3_" + String((uint32_t)mac, HEX);
    device_id.toUpperCase();
    preferences.putString(DEVICE_ID_KEY, device_id);
    Serial.printf("✅ Generated Device ID: %s\n", device_id.c_str());
}

void enter_config_mode() {
    Serial.println("🔧 Enhanced Configuration Mode");
    WiFi.softAP("TeddyBear_MP3_Setup", "teddy123");
    
    // Simple serial configuration for demo
    Serial.println("Enter WiFi SSID:");
    while (Serial.available() == 0) delay(100);
    wifi_ssid = Serial.readString();
    wifi_ssid.trim();
    
    Serial.println("Enter WiFi Password:");
    while (Serial.available() == 0) delay(100);
    wifi_password = Serial.readString();
    wifi_password.trim();
    
    preferences.putString(WIFI_SSID_KEY, wifi_ssid);
    preferences.putString(WIFI_PASS_KEY, wifi_password);
    
    Serial.println("✅ Enhanced configuration saved. Restarting...");
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
        digitalWrite(LED_STATUS, attempts % 2);
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        wifi_connected = true;
        Serial.printf("\n✅ WiFi connected! IP: %s\n", WiFi.localIP().toString().c_str());
        Serial.printf("📶 Signal strength: %d dBm\n", WiFi.RSSI());
        set_status_led(true, false, false);
    } else {
        Serial.println("\n❌ WiFi connection failed!");
        set_status_led(false, false, true);
        enter_deep_sleep(60);
    }
}

void setup_ssl() {
    client.setInsecure(); // Development mode
    Serial.println("⚠️ SSL validation disabled (development mode)");
}

void test_server_connection() {
    Serial.println("🔗 Testing enhanced server connection...");
    
    HTTPClient http;
    http.begin(client, server_url + "/health");
    http.setTimeout(5000);
    
    int response_code = http.GET();
    if (response_code == 200) {
        server_connected = true;
        Serial.println("✅ Enhanced server connection successful");
    } else {
        server_connected = false;
        Serial.printf("❌ Server connection failed: %d\n", response_code);
    }
    
    http.end();
}

void set_status_led(bool green, bool blue, bool red) {
    digitalWrite(LED_STATUS, green);
    digitalWrite(LED_LISTENING, blue);
    digitalWrite(LED_PROCESSING, red);
}

int get_battery_level() {
    // TODO: Implement actual battery monitoring
    return 85;
}

void cleanup_before_sleep() {
    // Cleanup encoder resources
#if USE_ESP_AUDIO_CODEC
    if (encoder_handle) {
        audio_encoder_destroy(encoder_handle);
        encoder_handle = NULL;
    }
#elif USE_SHINE_ENCODER
    if (shine_encoder) {
        shine_close(shine_encoder);
        shine_encoder = NULL;
    }
#endif
    
    // Free audio buffers
    if (audio_buffer) {
        free(audio_buffer);
        audio_buffer = NULL;
    }
    if (compressed_buffer) {
        free(compressed_buffer);
        compressed_buffer = NULL;
    }
    
    Serial.println("🧹 Cleanup completed before sleep");
}

void enter_deep_sleep(int seconds) {
    Serial.printf("💤 Entering enhanced deep sleep for %d seconds\n", seconds);
    
    cleanup_before_sleep();
    
    esp_sleep_enable_timer_wakeup(seconds * 1000000ULL);
    esp_sleep_enable_ext0_wakeup(GPIO_NUM_12, 0);
    
    set_status_led(false, false, false);
    preferences.end();
    
    esp_deep_sleep_start();
}

void handle_critical_error(String error) {
    Serial.printf("💥 CRITICAL ERROR: %s\n", error.c_str());
    
    cleanup_before_sleep();
    
    // Flash red LED
    for (int i = 0; i < 10; i++) {
        set_status_led(false, false, true);
        delay(200);
        set_status_led(false, false, false);
        delay(200);
    }
    
    ESP.restart();
}

/*
================ INSTALLATION NOTES ================

1. ESP Audio Codec Installation:
   - Add to your platformio.ini or Arduino IDE:
   - lib_deps = espressif/esp_audio_codec@^1.0.0
   - Or via ESP-IDF: idf.py add-dependency "espressif/esp_audio_codec^1.0.0"

2. Alternative Shine MP3 Encoder:
   - Download from: https://github.com/savonet/shine
   - Add shine files to your project directory
   - Enable USE_SHINE_ENCODER define

3. Hardware Requirements:
   - ESP32-S3 with PSRAM (recommended)
   - I2S microphone (INMP441 or similar)
   - 3 LEDs for status indication
   - 3 buttons for user interaction

4. Memory Optimization:
   - Use PSRAM when available
   - Adjust buffer sizes based on available memory
   - Monitor heap usage during operation

5. Performance Tuning:
   - Adjust MP3 bitrate (64-128 kbps)
   - Optimize buffer sizes for your use case
   - Use appropriate compression quality settings
*/ 