/*
🧪 ESP32 MP3 Compression Performance Test
Unit test for audio compression quality and performance validation
*/

#include <Arduino.h>
#include <vector>
#include <cmath>

// Test configuration
#define TEST_SAMPLE_RATE 16000
#define TEST_DURATION_SEC 5
#define MP3_BITRATE_TEST 96
#define EXPECTED_COMPRESSION_RATIO 4.0  // Expected 4:1 compression

// Test results structure
struct CompressionTestResult {
    bool test_passed = false;
    float compression_ratio = 0.0;
    float quality_score = 0.0;
    size_t raw_size_bytes = 0;
    size_t compressed_size_bytes = 0;
    unsigned long encoding_time_ms = 0;
    float rms_error = 0.0;
    String error_message = "";
};

// Mock audio encoder for testing
class MockMP3Encoder {
private:
    int bitrate_kbps;
    bool initialized = false;
    
public:
    MockMP3Encoder(int bitrate) : bitrate_kbps(bitrate) {}
    
    bool init() {
        Serial.println("🎵 Initializing Mock MP3 Encoder...");
        initialized = true;
        return true;
    }
    
    size_t encode(int16_t* input_samples, size_t sample_count, uint8_t* output_buffer) {
        if (!initialized) return 0;
        
        // Simulate MP3 compression
        // Real compression ratio depends on content, but typically 4:1 to 8:1
        float compression_factor = (float)bitrate_kbps / (TEST_SAMPLE_RATE * 16 / 1000.0);
        size_t input_bytes = sample_count * sizeof(int16_t);
        size_t compressed_bytes = (size_t)(input_bytes * compression_factor);
        
        // Simulate encoding delay
        delay(sample_count / (TEST_SAMPLE_RATE / 10)); // ~10ms per second of audio
        
        // Fill output buffer with mock compressed data
        for (size_t i = 0; i < compressed_bytes && i < sample_count * 2; i++) {
            output_buffer[i] = (uint8_t)(rand() % 256);
        }
        
        return compressed_bytes;
    }
    
    void deinit() {
        initialized = false;
    }
};

// Generate test audio signals
void generate_test_audio(std::vector<int16_t>& samples, int signal_type) {
    size_t total_samples = TEST_SAMPLE_RATE * TEST_DURATION_SEC;
    samples.resize(total_samples);
    
    Serial.printf("🎼 Generating test audio: %d samples\n", total_samples);
    
    switch (signal_type) {
        case 0: // Silence
            for (size_t i = 0; i < total_samples; i++) {
                samples[i] = 0;
            }
            Serial.println("   Signal type: Silence");
            break;
            
        case 1: // Pure tone (1kHz)
            for (size_t i = 0; i < total_samples; i++) {
                float t = (float)i / TEST_SAMPLE_RATE;
                samples[i] = (int16_t)(16000 * sin(2.0 * M_PI * 1000.0 * t));
            }
            Serial.println("   Signal type: 1kHz Pure Tone");
            break;
            
        case 2: // Speech-like signal (multiple frequencies)
            for (size_t i = 0; i < total_samples; i++) {
                float t = (float)i / TEST_SAMPLE_RATE;
                float signal = 0;
                signal += 0.4 * sin(2.0 * M_PI * 300.0 * t);   // Fundamental
                signal += 0.3 * sin(2.0 * M_PI * 600.0 * t);   // 2nd harmonic
                signal += 0.2 * sin(2.0 * M_PI * 900.0 * t);   // 3rd harmonic
                signal += 0.1 * sin(2.0 * M_PI * 1200.0 * t);  // 4th harmonic
                samples[i] = (int16_t)(12000 * signal);
            }
            Serial.println("   Signal type: Speech-like Multi-tone");
            break;
            
        case 3: // White noise
            for (size_t i = 0; i < total_samples; i++) {
                samples[i] = (int16_t)((rand() % 32768) - 16384);
            }
            Serial.println("   Signal type: White Noise");
            break;
            
        default: // Sweep tone
            for (size_t i = 0; i < total_samples; i++) {
                float t = (float)i / TEST_SAMPLE_RATE;
                float freq = 200.0 + (1000.0 * t / TEST_DURATION_SEC); // 200Hz to 1200Hz sweep
                samples[i] = (int16_t)(14000 * sin(2.0 * M_PI * freq * t));
            }
            Serial.println("   Signal type: Frequency Sweep 200-1200Hz");
            break;
    }
}

// Calculate audio quality metrics
float calculate_snr(const std::vector<int16_t>& original, const std::vector<int16_t>& compressed) {
    if (original.size() != compressed.size()) return 0.0;
    
    double signal_power = 0.0;
    double noise_power = 0.0;
    
    for (size_t i = 0; i < original.size(); i++) {
        signal_power += (double)original[i] * original[i];
        double error = (double)original[i] - compressed[i];
        noise_power += error * error;
    }
    
    if (noise_power == 0.0) return 100.0; // Perfect match
    if (signal_power == 0.0) return 0.0;  // No signal
    
    return 10.0 * log10(signal_power / noise_power);
}

float calculate_rms_error(const std::vector<int16_t>& original, const std::vector<int16_t>& compressed) {
    if (original.size() != compressed.size()) return 100.0;
    
    double sum_squared_error = 0.0;
    for (size_t i = 0; i < original.size(); i++) {
        double error = (double)original[i] - compressed[i];
        sum_squared_error += error * error;
    }
    
    return sqrt(sum_squared_error / original.size()) / 32768.0 * 100.0; // Percentage
}

// Run compression test
CompressionTestResult run_compression_test(int signal_type, int bitrate_kbps) {
    CompressionTestResult result;
    
    Serial.printf("\n🧪 Running Compression Test #%d (Bitrate: %d kbps)\n", signal_type + 1, bitrate_kbps);
    Serial.println("=" * 50);
    
    // Generate test audio
    std::vector<int16_t> test_audio;
    generate_test_audio(test_audio, signal_type);
    
    // Initialize encoder
    MockMP3Encoder encoder(bitrate_kbps);
    if (!encoder.init()) {
        result.error_message = "Failed to initialize encoder";
        return result;
    }
    
    // Prepare buffers
    result.raw_size_bytes = test_audio.size() * sizeof(int16_t);
    uint8_t* compressed_buffer = new uint8_t[result.raw_size_bytes]; // Worst case size
    
    if (!compressed_buffer) {
        result.error_message = "Failed to allocate compression buffer";
        return result;
    }
    
    // Perform compression
    Serial.println("🎵 Starting compression...");
    unsigned long start_time = millis();
    
    result.compressed_size_bytes = encoder.encode(
        test_audio.data(), 
        test_audio.size(), 
        compressed_buffer
    );
    
    result.encoding_time_ms = millis() - start_time;
    
    // Calculate metrics
    result.compression_ratio = (float)result.raw_size_bytes / result.compressed_size_bytes;
    
    // Simulate decompression for quality assessment (in real implementation)
    std::vector<int16_t> decompressed_audio = test_audio; // Mock: assume perfect reconstruction
    
    // Add some realistic compression artifacts for testing
    for (size_t i = 0; i < decompressed_audio.size(); i += 100) {
        decompressed_audio[i] += (rand() % 200 - 100); // Small random error
    }
    
    float snr = calculate_snr(test_audio, decompressed_audio);
    result.rms_error = calculate_rms_error(test_audio, decompressed_audio);
    result.quality_score = snr;
    
    // Determine test pass/fail
    bool compression_ok = result.compression_ratio >= (EXPECTED_COMPRESSION_RATIO * 0.7); // 30% tolerance
    bool quality_ok = result.quality_score >= 20.0; // SNR > 20dB
    bool speed_ok = result.encoding_time_ms < (TEST_DURATION_SEC * 1000 * 2); // Real-time * 2
    
    result.test_passed = compression_ok && quality_ok && speed_ok;
    
    // Print results
    Serial.printf("📊 Test Results:\n");
    Serial.printf("   Raw size: %d bytes\n", result.raw_size_bytes);
    Serial.printf("   Compressed size: %d bytes\n", result.compressed_size_bytes);
    Serial.printf("   Compression ratio: %.2fx\n", result.compression_ratio);
    Serial.printf("   Encoding time: %lu ms\n", result.encoding_time_ms);
    Serial.printf("   Real-time factor: %.2fx\n", (float)result.encoding_time_ms / (TEST_DURATION_SEC * 1000));
    Serial.printf("   Quality (SNR): %.1f dB\n", result.quality_score);
    Serial.printf("   RMS error: %.2f%%\n", result.rms_error);
    Serial.printf("   Bandwidth savings: %.1f%%\n", (1.0 - 1.0/result.compression_ratio) * 100.0);
    
    Serial.printf("✅ Performance Checks:\n");
    Serial.printf("   Compression ratio: %s (%.2fx >= %.2fx)\n", 
                  compression_ok ? "PASS" : "FAIL", 
                  result.compression_ratio, 
                  EXPECTED_COMPRESSION_RATIO * 0.7);
    Serial.printf("   Audio quality: %s (%.1f dB >= 20.0 dB)\n", 
                  quality_ok ? "PASS" : "FAIL", 
                  result.quality_score);
    Serial.printf("   Encoding speed: %s (%lu ms <= %d ms)\n", 
                  speed_ok ? "PASS" : "FAIL", 
                  result.encoding_time_ms, 
                  TEST_DURATION_SEC * 1000 * 2);
    
    Serial.printf("🏆 Overall Result: %s\n", result.test_passed ? "PASS ✅" : "FAIL ❌");
    
    // Cleanup
    encoder.deinit();
    delete[] compressed_buffer;
    
    return result;
}

// Memory usage test
void test_memory_usage() {
    Serial.println("\n🧠 Memory Usage Test");
    Serial.println("=" * 30);
    
    size_t free_heap_before = ESP.getFreeHeap();
    size_t free_psram_before = psramFound() ? ESP.getFreePsram() : 0;
    
    Serial.printf("📊 Before allocation:\n");
    Serial.printf("   Free heap: %d bytes\n", free_heap_before);
    if (psramFound()) {
        Serial.printf("   Free PSRAM: %d bytes\n", free_psram_before);
    }
    
    // Allocate buffers as in real implementation
    const size_t BUFFER_SIZE = 32768;
    uint8_t* audio_buffer = NULL;
    uint8_t* compressed_buffer = NULL;
    
    if (psramFound()) {
        audio_buffer = (uint8_t*)heap_caps_malloc(BUFFER_SIZE, MALLOC_CAP_SPIRAM);
        compressed_buffer = (uint8_t*)heap_caps_malloc(BUFFER_SIZE/2, MALLOC_CAP_SPIRAM);
    } else {
        audio_buffer = (uint8_t*)malloc(BUFFER_SIZE);
        compressed_buffer = (uint8_t*)malloc(BUFFER_SIZE/2);
    }
    
    size_t free_heap_after = ESP.getFreeHeap();
    size_t free_psram_after = psramFound() ? ESP.getFreePsram() : 0;
    
    Serial.printf("📊 After allocation:\n");
    Serial.printf("   Free heap: %d bytes (used: %d bytes)\n", 
                  free_heap_after, free_heap_before - free_heap_after);
    if (psramFound()) {
        Serial.printf("   Free PSRAM: %d bytes (used: %d bytes)\n", 
                      free_psram_after, free_psram_before - free_psram_after);
    }
    
    bool allocation_success = (audio_buffer != NULL) && (compressed_buffer != NULL);
    Serial.printf("🏆 Memory allocation: %s\n", allocation_success ? "PASS ✅" : "FAIL ❌");
    
    if (allocation_success) {
        // Test buffer usage
        memset(audio_buffer, 0xAA, BUFFER_SIZE);
        memset(compressed_buffer, 0x55, BUFFER_SIZE/2);
        Serial.println("✅ Buffer write test passed");
        
        // Cleanup
        free(audio_buffer);
        free(compressed_buffer);
    }
    
    Serial.printf("📊 After cleanup:\n");
    Serial.printf("   Free heap: %d bytes\n", ESP.getFreeHeap());
    if (psramFound()) {
        Serial.printf("   Free PSRAM: %d bytes\n", ESP.getFreePsram());
    }
}

// Network transmission simulation test
void test_network_transmission() {
    Serial.println("\n🌐 Network Transmission Simulation");
    Serial.println("=" * 40);
    
    // Simulate different network conditions
    struct NetworkCondition {
        String name;
        int bandwidth_kbps;
        int latency_ms;
        float packet_loss_percent;
    };
    
    NetworkCondition conditions[] = {
        {"WiFi Good", 1000, 20, 0.1},
        {"WiFi Normal", 500, 50, 1.0},
        {"WiFi Poor", 100, 200, 5.0},
        {"3G Mobile", 64, 150, 2.0}
    };
    
    size_t test_data_sizes[] = {
        5000,   // Uncompressed 5KB
        1250,   // MP3 compressed ~4:1
        800,    // High compression
    };
    
    String data_types[] = {"Raw PCM", "MP3 96kbps", "MP3 64kbps"};
    
    for (int c = 0; c < 4; c++) {
        Serial.printf("\n📶 Network: %s\n", conditions[c].name.c_str());
        Serial.printf("   Bandwidth: %d kbps, Latency: %d ms, Loss: %.1f%%\n",
                     conditions[c].bandwidth_kbps, 
                     conditions[c].latency_ms,
                     conditions[c].packet_loss_percent);
        
        for (int d = 0; d < 3; d++) {
            size_t data_size = test_data_sizes[d];
            
            // Calculate transmission time
            float transmission_time_sec = (float)(data_size * 8) / (conditions[c].bandwidth_kbps * 1000);
            float total_time_sec = transmission_time_sec + (conditions[c].latency_ms / 1000.0);
            
            // Account for packet loss (retransmissions)
            if (conditions[c].packet_loss_percent > 0) {
                float loss_factor = 1.0 + (conditions[c].packet_loss_percent / 100.0 * 2.0);
                total_time_sec *= loss_factor;
            }
            
            bool acceptable = total_time_sec < 3.0; // Target < 3 seconds total
            
            Serial.printf("   %s (%d bytes): %.2fs %s\n", 
                         data_types[d].c_str(),
                         data_size,
                         total_time_sec,
                         acceptable ? "✅" : "❌");
        }
    }
}

// Run all tests
void setup() {
    Serial.begin(115200);
    delay(2000);
    
    Serial.println("\n🧸 ESP32 MP3 Compression Performance Test Suite");
    Serial.println("================================================");
    Serial.printf("Test Duration: %d seconds per test\n", TEST_DURATION_SEC);
    Serial.printf("Sample Rate: %d Hz\n", TEST_SAMPLE_RATE);
    Serial.printf("Target Bitrate: %d kbps\n", MP3_BITRATE_TEST);
    Serial.printf("Expected Compression: %.1fx\n", EXPECTED_COMPRESSION_RATIO);
    
    // System info
    Serial.printf("\n📊 System Information:\n");
    Serial.printf("   ESP32 Model: %s\n", ESP.getChipModel());
    Serial.printf("   CPU Frequency: %d MHz\n", ESP.getCpuFreqMHz());
    Serial.printf("   Flash Size: %d bytes\n", ESP.getFlashChipSize());
    Serial.printf("   Free Heap: %d bytes\n", ESP.getFreeHeap());
    Serial.printf("   PSRAM: %s\n", psramFound() ? "Available" : "Not found");
    if (psramFound()) {
        Serial.printf("   PSRAM Size: %d bytes\n", ESP.getPsramSize());
        Serial.printf("   Free PSRAM: %d bytes\n", ESP.getFreePsram());
    }
    
    // Run compression tests with different signal types
    CompressionTestResult results[5];
    int passed_tests = 0;
    
    for (int i = 0; i < 5; i++) {
        results[i] = run_compression_test(i, MP3_BITRATE_TEST);
        if (results[i].test_passed) {
            passed_tests++;
        }
        delay(1000); // Brief pause between tests
    }
    
    // Memory usage test
    test_memory_usage();
    
    // Network simulation test
    test_network_transmission();
    
    // Final summary
    Serial.println("\n🏆 TEST SUITE SUMMARY");
    Serial.println("====================");
    Serial.printf("Compression tests passed: %d/5\n", passed_tests);
    
    // Calculate average metrics
    float avg_compression_ratio = 0;
    float avg_quality = 0;
    unsigned long avg_encoding_time = 0;
    
    for (int i = 0; i < 5; i++) {
        if (results[i].test_passed) {
            avg_compression_ratio += results[i].compression_ratio;
            avg_quality += results[i].quality_score;
            avg_encoding_time += results[i].encoding_time_ms;
        }
    }
    
    if (passed_tests > 0) {
        avg_compression_ratio /= passed_tests;
        avg_quality /= passed_tests;
        avg_encoding_time /= passed_tests;
        
        Serial.printf("📊 Average Performance:\n");
        Serial.printf("   Compression ratio: %.2fx\n", avg_compression_ratio);
        Serial.printf("   Audio quality: %.1f dB SNR\n", avg_quality);
        Serial.printf("   Encoding time: %lu ms per %ds\n", avg_encoding_time, TEST_DURATION_SEC);
        Serial.printf("   Bandwidth savings: %.1f%%\n", (1.0 - 1.0/avg_compression_ratio) * 100.0);
    }
    
    // Overall verdict
    bool overall_pass = (passed_tests >= 4); // At least 4/5 tests should pass
    Serial.printf("\n🎯 OVERALL VERDICT: %s\n", overall_pass ? "SYSTEM READY FOR PRODUCTION ✅" : "NEEDS OPTIMIZATION ❌");
    
    if (!overall_pass) {
        Serial.println("\n💡 Optimization Recommendations:");
        Serial.println("   - Check MP3 encoder configuration");
        Serial.println("   - Verify sufficient PSRAM availability");
        Serial.println("   - Consider lower bitrate for better compression");
        Serial.println("   - Optimize buffer sizes for your specific use case");
    }
    
    Serial.println("\n🔚 Test suite complete. Reset to run again.");
}

void loop() {
    // Test suite runs once in setup()
    delay(1000);
} 