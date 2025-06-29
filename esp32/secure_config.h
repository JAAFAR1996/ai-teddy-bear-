/*
🔐 Secure Configuration Header for AI Teddy Bear ESP32
Contains security definitions and safe configuration management
*/

#ifndef SECURE_CONFIG_H
#define SECURE_CONFIG_H

// ================ SECURITY SETTINGS ================

// Enable security features
#define ENABLE_HTTPS true
#define ENABLE_NVS_ENCRYPTION true
#define ENABLE_OTA_UPDATES true
#define ENABLE_SECURE_BOOT false  // Enable in production

// API Configuration
#define MAX_API_KEY_LENGTH 64
#define MAX_URL_LENGTH 256
#define MAX_SSID_LENGTH 32
#define MAX_PASSWORD_LENGTH 64

// Audio Security
#define ENABLE_AUDIO_ENCRYPTION false  // For future implementation
#define MAX_RECORDING_DURATION 30  // seconds
#define AUDIO_QUALITY_THRESHOLD 0.3  // Minimum quality to send

// Network Security
#define CONNECTION_TIMEOUT 10000  // ms
#define MAX_RETRY_ATTEMPTS 3
#define HEARTBEAT_INTERVAL 30000  // ms

// Device Security
#define ENABLE_TAMPER_DETECTION false  // For future hardware
#define MAX_FAILED_ATTEMPTS 5
#define LOCKOUT_DURATION 300000  // 5 minutes

// ================ DEFAULT ENDPOINTS ================

// Production server (replace with actual URL)
#define DEFAULT_SERVER_URL "https://teddy-cloud.secureai.com"

// API endpoints
#define ENDPOINT_HEALTH "/health"
#define ENDPOINT_AUDIO "/esp32/audio" 
#define ENDPOINT_HEARTBEAT "/esp32/heartbeat"
#define ENDPOINT_VOLUME "/esp32/volume"
#define ENDPOINT_CONFIG "/esp32/config"
#define ENDPOINT_OTA "/esp32/ota"

// ================ HARDWARE CONFIGURATION ================

// Audio pins (I2S)
#define I2S_BCK_PIN 26
#define I2S_WS_PIN 25
#define I2S_DATA_IN_PIN 33
#define I2S_DATA_OUT_PIN 22

// Control pins
#define BUTTON_TALK_PIN 12
#define BUTTON_VOLUME_UP_PIN 13
#define BUTTON_VOLUME_DOWN_PIN 14
#define BUTTON_POWER_PIN 15

// LED pins
#define LED_STATUS_PIN 2
#define LED_LISTENING_PIN 4
#define LED_PROCESSING_PIN 5
#define LED_ERROR_PIN 18

// Sensor pins (future expansion)
#define BATTERY_MONITOR_PIN 35
#define TEMPERATURE_SENSOR_PIN 34
#define TOUCH_SENSOR_PIN 27

// ================ AUDIO CONFIGURATION ================

#define AUDIO_SAMPLE_RATE 16000
#define AUDIO_BITS_PER_SAMPLE 16
#define AUDIO_CHANNELS 1
#define AUDIO_BUFFER_SIZE 1024
#define AUDIO_DMA_BUFFERS 4

// Voice activity detection
#define SILENCE_THRESHOLD 100
#define SILENCE_DURATION 2000  // ms
#define MIN_RECORDING_DURATION 500  // ms

// ================ POWER MANAGEMENT ================

#define SLEEP_TIMEOUT 300000  // 5 minutes
#define DEEP_SLEEP_DURATION 300  // 5 minutes
#define LOW_BATTERY_THRESHOLD 20  // percent
#define CRITICAL_BATTERY_THRESHOLD 10  // percent

// ================ DEVELOPMENT FLAGS ================

#ifdef DEBUG
  #define DEBUG_PRINT(x) Serial.print(x)
  #define DEBUG_PRINTLN(x) Serial.println(x)
  #define DEBUG_PRINTF(fmt, ...) Serial.printf(fmt, __VA_ARGS__)
#else
  #define DEBUG_PRINT(x)
  #define DEBUG_PRINTLN(x)
  #define DEBUG_PRINTF(fmt, ...)
#endif

// ================ SSL CERTIFICATE (for production) ================

// Root CA certificate for server verification
// TODO: Replace with actual production certificate
const char* ROOT_CA_CERT = \
"-----BEGIN CERTIFICATE-----\n" \
"MIIDrzCCApegAwIBAgIQCDvgVpBCRrGhdWrJWZHHSjANBgkqhkiG9w0BAQUFADBh\n" \
"MQswCQYDVQQGEwJVUzEVMBMGA1UEChMMRGlnaUNlcnQgSW5jMRkwFwYDVQQLExB3\n" \
"d3cuZGlnaWNlcnQuY29tMSAwHgYDVQQDExdEaWdpQ2VydCBHbG9iYWwgUm9vdCBD\n" \
"QTAeFw0wNjExMTAwMDAwMDBaFw0zMTExMTAwMDAwMDBaMGExCzAJBgNVBAYTAlVT\n" \
"... (truncated for security)\n" \
"-----END CERTIFICATE-----\n";

#endif // SECURE_CONFIG_H 