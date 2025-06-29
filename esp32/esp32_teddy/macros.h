/*
🧸 AI Teddy Bear - ESP32 Audio Streaming Macros & Definitions v1.0
Enhanced definitions for real-time microphone capture and WebSocket streaming
*/

#ifndef TEDDY_MACROS_H
#define TEDDY_MACROS_H

// ================ HARDWARE PIN DEFINITIONS ================
#define MIC_PIN 34                    // ADC1 pin for analog microphone
#define BUTTON_TALK 12               // Talk/Record button
#define BUTTON_VOLUME_UP 13          // Volume up button  
#define BUTTON_VOLUME_DOWN 14        // Volume down button
#define LED_STATUS 2                 // Status LED (Green)
#define LED_LISTENING 4              // Listening LED (Blue)
#define LED_PROCESSING 5             // Processing LED (Orange)
#define LED_ERROR 15                 // Error LED (Red)

// ================ I2S AUDIO CONFIGURATION ================
#define I2S_SAMPLE_RATE 16000        // 16kHz optimal for speech
#define I2S_BITS_PER_SAMPLE 16       // 16-bit resolution
#define I2S_CHANNELS 1               // Mono audio
#define I2S_NUM I2S_NUM_0           // I2S port number

// I2S Pin Configuration
#define I2S_BCK_PIN 26              // Bit clock pin
#define I2S_WS_PIN 25               // Word select pin
#define I2S_DATA_IN_PIN 33          // Data input pin
#define I2S_DATA_OUT_PIN -1         // Not used for input

// ================ AUDIO BUFFER SETTINGS ================
#define AUDIO_BUFFER_SIZE 1024       // Samples per buffer
#define STREAM_BUFFER_COUNT 8        // Number of buffers for streaming
#define MAX_AUDIO_DURATION_MS 15000  // 15 seconds max recording
#define SILENCE_THRESHOLD 200        // Amplitude threshold for silence detection
#define SILENCE_DURATION_MS 2000     // 2 seconds of silence to stop recording

// ================ WEBSOCKET CONFIGURATION ================
#define WS_SERVER_HOST "teddy-cloud.example.com"
#define WS_SERVER_PORT 443          // HTTPS/WSS port
#define WS_USE_SSL true             // Enable SSL/TLS
#define WS_ENDPOINT_PREFIX "/ws/"   // WebSocket endpoint prefix
#define WS_RECONNECT_INTERVAL 5000  // 5 seconds between reconnect attempts
#define WS_MAX_RECONNECT_ATTEMPTS 10
#define WS_HEARTBEAT_INTERVAL 30000 // 30 seconds heartbeat

// ================ MEMORY MANAGEMENT ================
#define ENABLE_PSRAM true           // Use PSRAM if available
#define STREAM_CHUNK_SIZE 512       // Bytes per WebSocket message
#define MAX_MESSAGE_SIZE 2048       // Maximum WebSocket message size
#define BUFFER_SAFETY_MARGIN 0.8    // Use 80% of available buffer

// ================ AUDIO PROCESSING ================
#define ENABLE_NOISE_GATE true      // Enable noise gate
#define NOISE_GATE_THRESHOLD 150    // Noise gate threshold
#define ENABLE_AGC false            // Automatic Gain Control (disabled for now)
#define AGC_TARGET_LEVEL 8000       // Target audio level for AGC

// ================ TIMING DEFINITIONS ================
#define BUTTON_DEBOUNCE_MS 50       // Button debounce time
#define LED_BLINK_FAST_MS 200       // Fast LED blink interval
#define LED_BLINK_SLOW_MS 1000      // Slow LED blink interval
#define WATCHDOG_TIMEOUT_MS 30000   // Watchdog timeout
#define SLEEP_TIMEOUT_MS 300000     // Sleep after 5 minutes idle

// ================ SECURITY & AUTHENTICATION ================
#define MAX_DEVICE_ID_LENGTH 64     // Maximum device ID length
#define MAX_API_KEY_LENGTH 128      // Maximum API key length
#define ENABLE_ENCRYPTION true      // Enable data encryption
#define USE_DEVICE_CERTIFICATE false // Use device-specific certificates

// ================ DEBUG & MONITORING ================
#define DEBUG_LEVEL 2               // 0=None, 1=Basic, 2=Detailed, 3=Verbose
#define ENABLE_SERIAL_MONITOR true  // Enable serial output
#define ENABLE_PERFORMANCE_STATS true // Track performance metrics
#define STATS_REPORT_INTERVAL 10000   // Report stats every 10 seconds

// ================ SYSTEM LIMITS ================
#define MAX_WIFI_RECONNECT_ATTEMPTS 20
#define WIFI_CONNECT_TIMEOUT_MS 15000
#define SERVER_CONNECT_TIMEOUT_MS 10000
#define HTTP_TIMEOUT_MS 5000

// ================ FEATURE FLAGS ================
#define ENABLE_OTA_UPDATES true     // Over-the-air updates
#define ENABLE_CONFIG_AP false      // Configuration access point
#define ENABLE_WEB_INTERFACE false  // Web configuration interface
#define ENABLE_BLUETOOTH false      // Bluetooth connectivity

// ================ ERROR CODES ================
#define ERROR_NONE 0
#define ERROR_WIFI_FAILED 1
#define ERROR_SERVER_FAILED 2
#define ERROR_AUDIO_FAILED 3
#define ERROR_WEBSOCKET_FAILED 4
#define ERROR_MEMORY_FAILED 5
#define ERROR_HARDWARE_FAILED 6

// ================ STATUS CODES ================
#define STATUS_IDLE 0
#define STATUS_CONNECTING 1
#define STATUS_CONNECTED 2
#define STATUS_LISTENING 3
#define STATUS_PROCESSING 4
#define STATUS_STREAMING 5
#define STATUS_ERROR 6

// ================ UTILITY MACROS ================
#define ARRAY_SIZE(arr) (sizeof(arr) / sizeof(arr[0]))
#define MIN(a, b) ((a) < (b) ? (a) : (b))
#define MAX(a, b) ((a) > (b) ? (a) : (b))
#define CLAMP(x, min_val, max_val) MIN(MAX(x, min_val), max_val)

// Debug printing macros
#if ENABLE_SERIAL_MONITOR
  #if DEBUG_LEVEL >= 1
    #define DEBUG_PRINT(x) Serial.print(x)
    #define DEBUG_PRINTLN(x) Serial.println(x)
    #define DEBUG_PRINTF(...) Serial.printf(__VA_ARGS__)
  #else
    #define DEBUG_PRINT(x)
    #define DEBUG_PRINTLN(x)
    #define DEBUG_PRINTF(...)
  #endif
  
  #if DEBUG_LEVEL >= 2
    #define DEBUG_PRINT_DETAILED(x) Serial.print(x)
    #define DEBUG_PRINTLN_DETAILED(x) Serial.println(x)
    #define DEBUG_PRINTF_DETAILED(...) Serial.printf(__VA_ARGS__)
  #else
    #define DEBUG_PRINT_DETAILED(x)
    #define DEBUG_PRINTLN_DETAILED(x)
    #define DEBUG_PRINTF_DETAILED(...)
  #endif
  
  #if DEBUG_LEVEL >= 3
    #define DEBUG_PRINT_VERBOSE(x) Serial.print(x)
    #define DEBUG_PRINTLN_VERBOSE(x) Serial.println(x)
    #define DEBUG_PRINTF_VERBOSE(...) Serial.printf(__VA_ARGS__)
  #else
    #define DEBUG_PRINT_VERBOSE(x)
    #define DEBUG_PRINTLN_VERBOSE(x)
    #define DEBUG_PRINTF_VERBOSE(...)
  #endif
#else
  #define DEBUG_PRINT(x)
  #define DEBUG_PRINTLN(x)
  #define DEBUG_PRINTF(...)
  #define DEBUG_PRINT_DETAILED(x)
  #define DEBUG_PRINTLN_DETAILED(x)
  #define DEBUG_PRINTF_DETAILED(...)
  #define DEBUG_PRINT_VERBOSE(x)
  #define DEBUG_PRINTLN_VERBOSE(x)
  #define DEBUG_PRINTF_VERBOSE(...)
#endif

#endif // TEDDY_MACROS_H 