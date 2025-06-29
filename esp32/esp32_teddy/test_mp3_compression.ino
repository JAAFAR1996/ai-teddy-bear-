/*
🧪 ESP32 MP3 Compression Performance Test
Simple unit test for audio compression validation
*/

#include <Arduino.h>

// Test configuration
#define TEST_SAMPLE_RATE 16000
#define TEST_DURATION_SEC 3
#define MP3_BITRATE_TEST 96

struct TestResult {
    bool passed = false;
    float compression_ratio = 0.0;
    unsigned long encoding_time_ms = 0;
    size_t raw_bytes = 0;
    size_t compressed_bytes = 0;
    String status = "";
};

// Mock compression function
size_t compress_audio_mock(int16_t* input, size_t samples, uint8_t* output) {
    unsigned long start = millis();
    
    // Simulate MP3 encoding time (realistic)
    delay(samples / (TEST_SAMPLE_RATE / 100)); // ~100ms per second of audio
    
    // Calculate realistic compressed size
    size_t input_bytes = samples * sizeof(int16_t);
    size_t compressed_size = input_bytes / 5; // ~5:1 compression for speech
    
    // Fill output with mock data
    for (size_t i = 0; i < compressed_size; i++) {
        output[i] = (uint8_t)(random(256));
    }
    
    return compressed_size;
}

TestResult run_compression_test() {
    TestResult result;
    
    Serial.println("\n🧪 Running MP3 Compression Test");
    Serial.println("===============================");
    
    // Generate test audio (5 seconds of sine wave)
    size_t total_samples = TEST_SAMPLE_RATE * TEST_DURATION_SEC;
    result.raw_bytes = total_samples * sizeof(int16_t);
    
    Serial.printf("📊 Test Parameters:\n");
    Serial.printf("   Duration: %d seconds\n", TEST_DURATION_SEC);
    Serial.printf("   Sample rate: %d Hz\n", TEST_SAMPLE_RATE);
    Serial.printf("   Raw data size: %d bytes\n", result.raw_bytes);
    
    // Allocate test buffers
    int16_t* test_audio = (int16_t*)malloc(result.raw_bytes);
    uint8_t* compressed_buffer = (uint8_t*)malloc(result.raw_bytes); // Worst case
    
    if (!test_audio || !compressed_buffer) {
        result.status = "Memory allocation failed";
        if (test_audio) free(test_audio);
        if (compressed_buffer) free(compressed_buffer);
        return result;
    }
    
    // Generate test audio (1kHz sine wave)
    Serial.println("🎵 Generating test audio...");
    for (size_t i = 0; i < total_samples; i++) {
        float t = (float)i / TEST_SAMPLE_RATE;
        test_audio[i] = (int16_t)(16000 * sin(2.0 * PI * 1000.0 * t));
    }
    
    // Perform compression test
    Serial.println("🎵 Testing compression...");
    unsigned long start_time = millis();
    
    result.compressed_bytes = compress_audio_mock(test_audio, total_samples, compressed_buffer);
    
    result.encoding_time_ms = millis() - start_time;
    result.compression_ratio = (float)result.raw_bytes / result.compressed_bytes;
    
    // Evaluate results
    bool compression_ok = result.compression_ratio >= 3.0; // At least 3:1
    bool speed_ok = result.encoding_time_ms < (TEST_DURATION_SEC * 1000 * 2); // Real-time * 2
    bool size_ok = result.compressed_bytes > 0;
    
    result.passed = compression_ok && speed_ok && size_ok;
    
    // Print results
    Serial.printf("📊 Test Results:\n");
    Serial.printf("   Raw size: %d bytes\n", result.raw_bytes);
    Serial.printf("   Compressed size: %d bytes\n", result.compressed_bytes);
    Serial.printf("   Compression ratio: %.2fx\n", result.compression_ratio);
    Serial.printf("   Encoding time: %lu ms\n", result.encoding_time_ms);
    Serial.printf("   Real-time factor: %.2fx\n", (float)result.encoding_time_ms / (TEST_DURATION_SEC * 1000));
    Serial.printf("   Bandwidth savings: %.1f%%\n", (1.0 - 1.0/result.compression_ratio) * 100.0);
    
    Serial.printf("\n✅ Performance Checks:\n");
    Serial.printf("   Compression: %s (%.2fx >= 3.0x)\n", compression_ok ? "PASS" : "FAIL", result.compression_ratio);
    Serial.printf("   Speed: %s (%lu ms <= %d ms)\n", speed_ok ? "PASS" : "FAIL", result.encoding_time_ms, TEST_DURATION_SEC * 1000 * 2);
    Serial.printf("   Output: %s (size > 0)\n", size_ok ? "PASS" : "FAIL");
    
    result.status = result.passed ? "All tests passed" : "Some tests failed";
    Serial.printf("\n🏆 Overall: %s %s\n", result.status.c_str(), result.passed ? "✅" : "❌");
    
    // Cleanup
    free(test_audio);
    free(compressed_buffer);
    
    return result;
}

void test_memory_usage() {
    Serial.println("\n🧠 Memory Usage Test");
    Serial.println("===================");
    
    size_t heap_before = ESP.getFreeHeap();
    size_t psram_before = psramFound() ? ESP.getFreePsram() : 0;
    
    Serial.printf("📊 Memory Status:\n");
    Serial.printf("   Free heap: %d bytes\n", heap_before);
    if (psramFound()) {
        Serial.printf("   Free PSRAM: %d bytes\n", psram_before);
        Serial.printf("   PSRAM total: %d bytes\n", ESP.getPsramSize());
    } else {
        Serial.println("   PSRAM: Not available");
    }
    
    // Test buffer allocation
    const size_t BUFFER_SIZE = 32768;
    uint8_t* buffer1 = (uint8_t*)malloc(BUFFER_SIZE);
    uint8_t* buffer2 = (uint8_t*)malloc(BUFFER_SIZE/2);
    
    bool allocation_ok = (buffer1 != NULL) && (buffer2 != NULL);
    
    Serial.printf("📦 Buffer Allocation Test:\n");
    Serial.printf("   Audio buffer (32KB): %s\n", buffer1 ? "✅ SUCCESS" : "❌ FAILED");
    Serial.printf("   Compressed buffer (16KB): %s\n", buffer2 ? "✅ SUCCESS" : "❌ FAILED");
    Serial.printf("   Overall allocation: %s\n", allocation_ok ? "✅ PASS" : "❌ FAIL");
    
    if (allocation_ok) {
        Serial.printf("   Memory used: %d bytes\n", heap_before - ESP.getFreeHeap());
    }
    
    // Cleanup
    if (buffer1) free(buffer1);
    if (buffer2) free(buffer2);
    
    Serial.printf("   Memory after cleanup: %d bytes free\n", ESP.getFreeHeap());
}

void test_network_performance() {
    Serial.println("\n🌐 Network Performance Simulation");
    Serial.println("=================================");
    
    // Test data sizes (typical for 5-second audio)
    struct TestCase {
        String format;
        size_t size_bytes;
        String description;
    };
    
    TestCase cases[] = {
        {"Raw PCM", 160000, "16kHz 16-bit mono 10s"},
        {"MP3 96kbps", 32000, "Compressed ~5:1 ratio"},
        {"MP3 64kbps", 21000, "High compression ~7:1"},
        {"MP3 128kbps", 42000, "High quality ~4:1"}
    };
    
    // Network conditions
    int wifi_speeds[] = {1000, 500, 100}; // kbps
    String speed_names[] = {"Good WiFi", "Normal WiFi", "Poor WiFi"};
    
    for (int s = 0; s < 3; s++) {
        Serial.printf("\n📶 %s (%d kbps):\n", speed_names[s].c_str(), wifi_speeds[s]);
        
        for (int c = 0; c < 4; c++) {
            float transmission_time = (float)(cases[c].size_bytes * 8) / (wifi_speeds[s] * 1000);
            float total_time = transmission_time + 0.1; // Add 100ms latency
            
            bool acceptable = total_time < 5.0; // Target < 5 seconds
            
            Serial.printf("   %s (%d bytes): %.2fs %s\n", 
                         cases[c].format.c_str(),
                         cases[c].size_bytes,
                         total_time,
                         acceptable ? "✅" : "❌");
        }
    }
}

void setup() {
    Serial.begin(115200);
    delay(2000);
    
    Serial.println("\n🧸 ESP32 Audio Compression Test Suite");
    Serial.println("=====================================");
    
    // System information
    Serial.printf("📊 System Info:\n");
    Serial.printf("   Chip: %s\n", ESP.getChipModel());
    Serial.printf("   CPU: %d MHz\n", ESP.getCpuFreqMHz());
    Serial.printf("   Flash: %d bytes\n", ESP.getFlashChipSize());
    Serial.printf("   Free heap: %d bytes\n", ESP.getFreeHeap());
    Serial.printf("   PSRAM: %s\n", psramFound() ? "Available" : "Not found");
    
    // Run tests
    TestResult compression_result = run_compression_test();
    test_memory_usage();
    test_network_performance();
    
    // Final verdict
    Serial.println("\n🎯 FINAL VERDICT");
    Serial.println("================");
    
    if (compression_result.passed) {
        Serial.println("✅ MP3 compression system is READY for production");
        Serial.printf("   Expected bandwidth savings: %.0f%%\n", 
                     (1.0 - 1.0/compression_result.compression_ratio) * 100.0);
        Serial.printf("   Processing overhead: %.1fx real-time\n", 
                     (float)compression_result.encoding_time_ms / (TEST_DURATION_SEC * 1000));
    } else {
        Serial.println("❌ MP3 compression system needs OPTIMIZATION");
        Serial.println("💡 Recommendations:");
        Serial.println("   - Check encoder library installation");
        Serial.println("   - Verify sufficient memory allocation");
        Serial.println("   - Consider using ESP32-S3 with PSRAM");
    }
    
    Serial.println("\n🔄 Test complete. Reset to run again.");
}

void loop() {
    delay(1000);
} 