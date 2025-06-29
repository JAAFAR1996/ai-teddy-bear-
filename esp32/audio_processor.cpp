/*
🧸 AI Teddy Bear - Production Audio Processor v3.0 (2025)
Enterprise-grade ESP32 audio processing with real base64, compression, and secure SSL
Fixes: Stubbed encoding, missing compression, insecure SSL
*/

#include "audio_processor.h"
#include <base64.h>
#include <ArduinoJson.h>
#include <WiFiClientSecure.h>
#include <esp_log.h>
#include <esp_heap_caps.h>

// ================ PRODUCTION TLS CERTIFICATES ================
// Replace with your actual production certificates
const char* root_ca = R"EOF(
-----BEGIN CERTIFICATE-----
MIIDQTCCAimgAwIBAgITBmyfz5m/jAo54vB4ikPmljZbyjANBgkqhkiG9w0BAQsF
ADA5MQswCQYDVQQGEwJVUzEPMA0GA1UEChMGQW1hem9uMRkwFwYDVQQDExBBbWF6
b24gUm9vdCBDQSAxMB4XDTE1MDUyNjAwMDAwMFoXDTM4MDExNzAwMDAwMFowOTEL
MAkGA1UEBhMCVVMxDzANBgNVBAoTBkFtYXpvbjEZMBcGA1UEAxMQQW1hem9uIFJv
b3QgQ0EgMTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBALJ4gHHKeNXj
ca9HgFB0fW7Y14h29Jlo91ghYPl0hAEvrAIthtOgQ3pOsqTQNroBvo3bSMgHFzZM
9O6II8c+6zf1tRn4SWiw3te5djgdYZ6k/oI2peVKVuRF4fn9tBb6dNqcmzU5L/qw
IFAGbHrQgLKm+a/sRxmPUDgH3KKHOVj4utWp+UhnMJbulHheb4mjUcAwhmahRWa6
VOujw5H5SNz/0egwLX0tdHA114gk957EWW67c4cX8jJGKLhD+rcdqsq08p8kDi1L
93FcXmn/6pUCyziKrlA4b9v7LWIbxcceVOF34GfID5yHI9Y/QCB/IIDEgEw+OyQm
jgSubJrIqg0CAwEAAaNCMEAwDwYDVR0TAQH/BAUwAwEB/zAOBgNVHQ8BAf8EBAMC
AYYwHQYDVR0OBBYEFIQYzIU07LwMlJQuCFmcx7IQTgoIMA0GCSqGSIb3DQEBCwUA
A4IBAQCY8jdaQZChGsV2USggNiMOruYou6r4lK5IpDB/G/wkjUu0yKGX9rbxenDI
U5PMCCjjmCXPI6T53iHTfIuJruydjsw2hUwsHlwjKhK5iNhKQQhQ9W2HH8ASBDCj
MQKPuJ6J+WKxnVlCLWcSAqLnp5lLTM8mCKjg4LKmN6BkFcPBJTK+0Fk0q8cYnNE2
5XUdGN9Uj3qPPPLxlODV3ZlhpPdKjfznRYXiGEaJpCkPpO5I6wMvqpQ8YE8dQw9c
Qp2+MKjpXR6KEJPOKRv2i2vXhD7vNQY6N2QWFlZkqjZ2Dg0EUc1aXQjB+fGZ4TfU
cQ8H2vEiZ3lk0mVWGhR4t/QP12nC6N+vR4hDl0Jy7k8L
-----END CERTIFICATE-----
)EOF";

// ================ AUDIO PROCESSOR CLASS IMPLEMENTATION ================

AudioProcessor::AudioProcessor() {
    // Allocate compression buffer in PSRAM if available
    if (psramFound()) {
        compressed_buffer = (uint8_t*)heap_caps_malloc(COMPRESSION_BUFFER_SIZE, MALLOC_CAP_SPIRAM);
        ESP_LOGI(TAG, "Compression buffer allocated in PSRAM");
    } else {
        compressed_buffer = (uint8_t*)malloc(COMPRESSION_BUFFER_SIZE);
        ESP_LOGI(TAG, "Compression buffer allocated in internal RAM");
    }
    
    if (!compressed_buffer) {
        ESP_LOGE(TAG, "Failed to allocate compression buffer");
        return;
    }
    
    // Initialize statistics
    memset(&stats, 0, sizeof(CompressionStats));
    stats.total_processed = 0;
    stats.total_compressed = 0;
    stats.average_compression_ratio = 1.0f;
    
    ESP_LOGI(TAG, "AudioProcessor initialized successfully");
}

AudioProcessor::~AudioProcessor() {
    if (compressed_buffer) {
        free(compressed_buffer);
        compressed_buffer = nullptr;
    }
    ESP_LOGI(TAG, "AudioProcessor destroyed");
}

String AudioProcessor::encodeAudioBase64(int16_t* samples, size_t count) {
    if (!samples || count == 0) {
        ESP_LOGW(TAG, "Invalid input for base64 encoding");
        return "";
    }
    
    unsigned long start_time = millis();
    
    // Convert to bytes
    size_t byte_count = count * sizeof(int16_t);
    uint8_t* byte_data = (uint8_t*)samples;
    
    // Compress audio first
    size_t compressed_size = compressAudio(byte_data, byte_count, compressed_buffer);
    
    // Real base64 encoding using ESP32 library
    String encoded = base64::encode(compressed_buffer, compressed_size);
    
    // Update statistics
    stats.encoding_time_ms = millis() - start_time;
    stats.total_processed += byte_count;
    stats.total_compressed += compressed_size;
    stats.last_compression_ratio = (float)byte_count / compressed_size;
    stats.average_compression_ratio = (stats.average_compression_ratio + stats.last_compression_ratio) / 2.0f;
    
    ESP_LOGI(TAG, "Audio encoded: %d samples -> %d bytes -> %d compressed -> %d base64", 
             count, byte_count, compressed_size, encoded.length());
    ESP_LOGI(TAG, "Compression ratio: %.2fx, Encoding time: %lu ms", 
             stats.last_compression_ratio, stats.encoding_time_ms);
    
    return encoded;
}

size_t AudioProcessor::compressAudio(uint8_t* input, size_t input_size, uint8_t* output) {
    if (!input || !output || input_size == 0) {
        ESP_LOGW(TAG, "Invalid input for compression");
        return 0;
    }
    
    size_t out_idx = 0;
    size_t i = 0;
    int16_t* samples = (int16_t*)input;
    size_t sample_count = input_size / sizeof(int16_t);
    
    ESP_LOGD(TAG, "Starting compression of %d samples", sample_count);
    
    while (i < sample_count) {
        // Check if we have enough space in output buffer
        if (out_idx >= COMPRESSION_BUFFER_SIZE - 4) {
            ESP_LOGW(TAG, "Compression buffer full, truncating");
            break;
        }
        
        // Check for silence region
        if (isSilence(samples + i, sample_count - i)) {
            size_t silence_count = countSilence(samples + i, sample_count - i);
            
            // Encode silence as: [SILENCE_MARKER][LOW_BYTE][HIGH_BYTE]
            output[out_idx++] = SILENCE_MARKER;
            output[out_idx++] = silence_count & 0xFF;
            output[out_idx++] = (silence_count >> 8) & 0xFF;
            
            i += silence_count;
            stats.silence_regions_compressed++;
            
            ESP_LOGV(TAG, "Compressed silence: %d samples at position %d", silence_count, i);
        } else {
            // Copy non-silent audio data directly (little-endian)
            output[out_idx++] = input[i * 2];     // Low byte
            output[out_idx++] = input[i * 2 + 1]; // High byte
            i++;
        }
    }
    
    ESP_LOGI(TAG, "Compression complete: %d bytes -> %d bytes (%.2fx reduction)", 
             input_size, out_idx, (float)input_size / out_idx);
    
    return out_idx;
}

bool AudioProcessor::isSilence(int16_t* samples, size_t available_count) {
    if (!samples || available_count < MIN_SILENCE_SAMPLES) {
        return false;
    }
    
    // Check first few samples for silence
    size_t check_count = min(MIN_SILENCE_SAMPLES, available_count);
    
    for (size_t i = 0; i < check_count; i++) {
        if (abs(samples[i]) > SILENCE_THRESHOLD) {
            return false;
        }
    }
    
    return true;
}

size_t AudioProcessor::countSilence(int16_t* samples, size_t available_count) {
    if (!samples || available_count == 0) {
        return 0;
    }
    
    size_t silence_count = 0;
    size_t max_silence = min(MAX_SILENCE_RUN, available_count);
    
    for (size_t i = 0; i < max_silence; i++) {
        if (abs(samples[i]) <= SILENCE_THRESHOLD) {
            silence_count++;
        } else {
            break; // End of silence region
        }
    }
    
    return silence_count;
}

CompressionStats AudioProcessor::getStats() const {
    return stats;
}

void AudioProcessor::resetStats() {
    memset(&stats, 0, sizeof(CompressionStats));
    stats.average_compression_ratio = 1.0f;
    ESP_LOGI(TAG, "Statistics reset");
}

// ================ SECURE SSL CONFIGURATION ================

SecureConnectionManager::SecureConnectionManager() : client_configured(false) {
    ESP_LOGI(TAG, "SecureConnectionManager initialized");
}

void SecureConnectionManager::setupSecureConnection(WiFiClientSecure& client, bool development_mode) {
    ESP_LOGI(TAG, "Setting up secure HTTPS connection");
    
    if (development_mode) {
        ESP_LOGW(TAG, "⚠️ DEVELOPMENT MODE: SSL certificate validation disabled");
        ESP_LOGW(TAG, "⚠️ This should NEVER be used in production!");
        
        #ifdef DEVELOPMENT
        client.setInsecure();
        #else
        ESP_LOGE(TAG, "Development mode requested but DEVELOPMENT flag not set!");
        // Force secure mode in production builds
        client.setCACert(root_ca);
        #endif
    } else {
        ESP_LOGI(TAG, "✅ Production mode: Full SSL certificate validation enabled");
        client.setCACert(root_ca);
        
        // Additional security settings for production
        client.setTimeout(30000); // 30 second timeout
        // client.setClientRSACert(...); // Add client cert if needed
        // client.setClientRSAKey(...);  // Add client key if needed
    }
    
    client_configured = true;
    ESP_LOGI(TAG, "SSL configuration complete");
}

bool SecureConnectionManager::verifyConnection(WiFiClientSecure& client, const char* host) {
    if (!client_configured) {
        ESP_LOGE(TAG, "Client not configured - call setupSecureConnection first");
        return false;
    }
    
    ESP_LOGI(TAG, "Verifying SSL connection to %s", host);
    
    // Test connection
    if (!client.connect(host, 443)) {
        ESP_LOGE(TAG, "Failed to connect to %s:443", host);
        return false;
    }
    
    ESP_LOGI(TAG, "✅ SSL connection verified successfully");
    client.stop();
    return true;
}

String SecureConnectionManager::getSSLInfo(WiFiClientSecure& client) {
    if (!client.connected()) {
        return "Not connected";
    }
    
    // Get SSL cipher and protocol info
    StaticJsonDocument<256> doc;
    doc["connected"] = true;
    doc["cipher"] = "TLS_CIPHER_INFO"; // Would need specific SSL library calls
    doc["protocol"] = "TLSv1.2+";
    doc["verified"] = !client.getInsecure();
    
    String result;
    serializeJson(doc, result);
    return result;
}

// ================ AUDIO STREAMING INTEGRATION ================

bool AudioProcessor::streamAudioToWebSocket(WebSocketsClient& ws, int16_t* samples, size_t count) {
    if (!samples || count == 0) {
        ESP_LOGW(TAG, "Invalid audio data for streaming");
        return false;
    }
    
    unsigned long start_time = millis();
    
    // Encode audio with compression
    String encoded_audio = encodeAudioBase64(samples, count);
    
    if (encoded_audio.length() == 0) {
        ESP_LOGE(TAG, "Failed to encode audio for streaming");
        return false;
    }
    
    // Create metadata for the audio chunk
    StaticJsonDocument<512> doc;
    doc["type"] = "audio_chunk";
    doc["timestamp"] = millis();
    doc["sample_count"] = count;
    doc["compressed"] = true;
    doc["compression_ratio"] = stats.last_compression_ratio;
    doc["encoding_time_ms"] = stats.encoding_time_ms;
    doc["data"] = encoded_audio;
    
    // Performance metadata
    JsonObject perf = doc.createNestedObject("performance");
    perf["processing_time_ms"] = millis() - start_time;
    perf["data_size_bytes"] = encoded_audio.length();
    perf["raw_size_bytes"] = count * sizeof(int16_t);
    
    String message;
    serializeJson(doc, message);
    
    // Send via WebSocket
    bool sent = ws.sendTXT(message);
    
    if (sent) {
        stats.chunks_sent++;
        ESP_LOGI(TAG, "Audio chunk streamed successfully (%d bytes -> %d chars)", 
                 count * sizeof(int16_t), encoded_audio.length());
    } else {
        stats.chunks_failed++;
        ESP_LOGE(TAG, "Failed to stream audio chunk");
    }
    
    return sent;
}

// ================ UTILITY AND DIAGNOSTIC FUNCTIONS ================

void AudioProcessor::printDiagnostics() {
    ESP_LOGI(TAG, "=== Audio Processor Diagnostics ===");
    ESP_LOGI(TAG, "Total processed: %lu bytes", stats.total_processed);
    ESP_LOGI(TAG, "Total compressed: %lu bytes", stats.total_compressed);
    ESP_LOGI(TAG, "Average compression ratio: %.2fx", stats.average_compression_ratio);
    ESP_LOGI(TAG, "Last compression ratio: %.2fx", stats.last_compression_ratio);
    ESP_LOGI(TAG, "Silence regions compressed: %lu", stats.silence_regions_compressed);
    ESP_LOGI(TAG, "Chunks sent: %lu", stats.chunks_sent);
    ESP_LOGI(TAG, "Chunks failed: %lu", stats.chunks_failed);
    ESP_LOGI(TAG, "Last encoding time: %lu ms", stats.encoding_time_ms);
    
    // Memory diagnostics
    ESP_LOGI(TAG, "Free heap: %d bytes", ESP.getFreeHeap());
    if (psramFound()) {
        ESP_LOGI(TAG, "Free PSRAM: %d bytes", ESP.getFreePsram());
    }
    ESP_LOGI(TAG, "================================");
}

bool AudioProcessor::selfTest() {
    ESP_LOGI(TAG, "Running audio processor self-test...");
    
    // Test 1: Buffer allocation
    if (!compressed_buffer) {
        ESP_LOGE(TAG, "Self-test FAILED: Compression buffer not allocated");
        return false;
    }
    
    // Test 2: Base64 encoding with test data
    int16_t test_samples[16] = {1000, -1000, 500, -500, 0, 0, 0, 0, 2000, -2000, 0, 0, 0, 0, 100, -100};
    String encoded = encodeAudioBase64(test_samples, 16);
    
    if (encoded.length() == 0) {
        ESP_LOGE(TAG, "Self-test FAILED: Base64 encoding failed");
        return false;
    }
    
    // Test 3: Compression test
    uint8_t test_data[32];
    for (int i = 0; i < 32; i++) {
        test_data[i] = (i < 16) ? 0 : (i * 10); // Half silence, half data
    }
    
    size_t compressed_size = compressAudio(test_data, 32, compressed_buffer);
    if (compressed_size == 0 || compressed_size >= 32) {
        ESP_LOGE(TAG, "Self-test FAILED: Compression not working correctly");
        return false;
    }
    
    ESP_LOGI(TAG, "✅ Self-test PASSED - Audio processor ready");
    ESP_LOGI(TAG, "Test compression: 32 bytes -> %d bytes (%.2fx)", 
             compressed_size, (float)32 / compressed_size);
    
    return true;
}

// ================ BENCHMARK FUNCTIONS ================

void AudioProcessor::runBenchmark() {
    ESP_LOGI(TAG, "Running audio processor benchmark...");
    
    const size_t test_sizes[] = {128, 512, 1024, 2048, 4096};
    const size_t num_tests = sizeof(test_sizes) / sizeof(test_sizes[0]);
    
    for (size_t t = 0; t < num_tests; t++) {
        size_t sample_count = test_sizes[t];
        
        // Generate test audio with mixed content
        int16_t* test_audio = (int16_t*)malloc(sample_count * sizeof(int16_t));
        if (!test_audio) continue;
        
        for (size_t i = 0; i < sample_count; i++) {
            if (i < sample_count / 4) {
                test_audio[i] = 0; // Silence
            } else if (i < sample_count / 2) {
                test_audio[i] = sin(i * 0.1) * 1000; // Sine wave
            } else {
                test_audio[i] = (rand() % 2000) - 1000; // Noise
            }
        }
        
        // Benchmark encoding
        resetStats();
        unsigned long start = millis();
        String encoded = encodeAudioBase64(test_audio, sample_count);
        unsigned long duration = millis() - start;
        
        ESP_LOGI(TAG, "Benchmark %d samples: %lu ms, %.2fx compression, %d chars", 
                 sample_count, duration, stats.last_compression_ratio, encoded.length());
        
        free(test_audio);
        
        // Ensure we don't overwhelm the system
        delay(100);
    }
    
    ESP_LOGI(TAG, "Benchmark complete");
} 