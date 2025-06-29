/*
🧸 AI Teddy Bear - Production Audio Processor Header v3.0 (2025)
Enterprise-grade ESP32 audio processing with real base64, compression, and secure SSL
Fixes: Stubbed encoding, missing compression, insecure SSL
*/

#ifndef AUDIO_PROCESSOR_H
#define AUDIO_PROCESSOR_H

#include <Arduino.h>
#include <WiFiClientSecure.h>
#include <WebSocketsClient.h>

// ================ COMPRESSION CONFIGURATION ================
#define COMPRESSION_BUFFER_SIZE     8192        // 8KB compression buffer
#define SILENCE_THRESHOLD          100          // Threshold for silence detection
#define SILENCE_MARKER             0xFF         // Marker byte for silence regions
#define MIN_SILENCE_SAMPLES        8            // Minimum samples to consider silence
#define MAX_SILENCE_RUN            2048         // Maximum silence run to compress
#define CHUNK_SIZE                 1024         // Audio chunk size for processing

// ================ PERFORMANCE TUNING ================
#define ENCODING_TIMEOUT_MS        50           // Max time for encoding per chunk
#define MAX_COMPRESSION_RATIO      10.0f        // Maximum expected compression ratio
#define BENCHMARK_ITERATIONS       5            // Number of benchmark runs

// ================ LOGGING ================
static const char* TAG = "AudioProcessor";

// ================ COMPRESSION STATISTICS ================
struct CompressionStats {
    unsigned long total_processed;              // Total bytes processed
    unsigned long total_compressed;             // Total bytes after compression
    unsigned long silence_regions_compressed;   // Number of silence regions found
    unsigned long chunks_sent;                  // Successfully sent chunks
    unsigned long chunks_failed;                // Failed chunks
    unsigned long encoding_time_ms;             // Last encoding time
    float last_compression_ratio;               // Last compression ratio achieved
    float average_compression_ratio;            // Running average compression ratio
};

// ================ AUDIO PROCESSOR CLASS ================
class AudioProcessor {
private:
    uint8_t* compressed_buffer;                 // Pre-allocated compression buffer
    CompressionStats stats;                     // Performance statistics
    
    // Internal compression methods
    size_t compressAudio(uint8_t* input, size_t input_size, uint8_t* output);
    bool isSilence(int16_t* samples, size_t available_count);
    size_t countSilence(int16_t* samples, size_t available_count);

public:
    // Constructor & Destructor
    AudioProcessor();
    ~AudioProcessor();
    
    // Core functionality
    String encodeAudioBase64(int16_t* samples, size_t count);
    bool streamAudioToWebSocket(WebSocketsClient& ws, int16_t* samples, size_t count);
    
    // Statistics and monitoring
    CompressionStats getStats() const;
    void resetStats();
    void printDiagnostics();
    
    // Testing and validation
    bool selfTest();
    void runBenchmark();
};

// ================ SECURE CONNECTION MANAGER ================
class SecureConnectionManager {
private:
    bool client_configured;

public:
    // Constructor
    SecureConnectionManager();
    
    // SSL Configuration
    void setupSecureConnection(WiFiClientSecure& client, bool development_mode = false);
    bool verifyConnection(WiFiClientSecure& client, const char* host);
    String getSSLInfo(WiFiClientSecure& client);
};

// ================ INTEGRATION MACROS ================
#define AUDIO_PROCESSOR_VERSION "3.0.0"
#define AUDIO_PROCESSOR_BUILD_DATE __DATE__ " " __TIME__

// Convenience macros for conditional compilation
#ifdef DEVELOPMENT
    #define ENABLE_SSL_INSECURE true
    #define ENABLE_VERBOSE_LOGGING true
#else
    #define ENABLE_SSL_INSECURE false
    #define ENABLE_VERBOSE_LOGGING false
#endif

// ================ UTILITY FUNCTIONS ================
inline bool isAudioProcessorReady(AudioProcessor& processor) {
    return processor.selfTest();
}

inline float calculateBandwidthSavings(const CompressionStats& stats) {
    if (stats.total_processed == 0) return 0.0f;
    return (1.0f - (float)stats.total_compressed / stats.total_processed) * 100.0f;
}

inline bool isPerformanceAcceptable(const CompressionStats& stats) {
    return stats.encoding_time_ms < ENCODING_TIMEOUT_MS && 
           stats.last_compression_ratio >= 1.2f; // At least 20% compression
}

#endif // AUDIO_PROCESSOR_H 