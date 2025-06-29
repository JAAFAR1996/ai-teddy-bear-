/*
🧸 AI Teddy Bear - Real-time Audio Streaming v1.0
ESP32 I2S Microphone + WebSocket Audio Streaming
*/

#include <WiFi.h>
#include <ArduinoJson.h>
#include <WebSocketsClient.h>
#include <driver/i2s.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

// ================ CONFIGURATION ================
#define WIFI_SSID "YourWiFiSSID"
#define WIFI_PASSWORD "YourWiFiPassword"
#define WS_SERVER "teddy-cloud.example.com"
#define WS_PORT 443
#define DEVICE_ID "teddy_esp32_001"

// Hardware pins
#define BUTTON_TALK 12
#define LED_STATUS 2
#define LED_LISTENING 4
#define LED_PROCESSING 5

// I2S Configuration
#define I2S_SAMPLE_RATE 16000
#define I2S_BCK_PIN 26
#define I2S_WS_PIN 25
#define I2S_DATA_PIN 33
#define AUDIO_BUFFER_SIZE 1024

// ================ GLOBALS ================
WebSocketsClient webSocket;
int16_t* audioBuffer;
bool recording = false;
bool wsConnected = false;
String sessionId = "";

// ================ SETUP ================
void setup() {
  Serial.begin(115200);
  Serial.println("🧸 AI Teddy Bear Starting...");
  
  initHardware();
  initAudio();
  connectWiFi();
  initWebSocket();
  
  Serial.println("✅ System Ready!");
}

void initHardware() {
  pinMode(BUTTON_TALK, INPUT_PULLUP);
  pinMode(LED_STATUS, OUTPUT);
  pinMode(LED_LISTENING, OUTPUT);
  pinMode(LED_PROCESSING, OUTPUT);
  
  digitalWrite(LED_STATUS, LOW);
  digitalWrite(LED_LISTENING, LOW);
  digitalWrite(LED_PROCESSING, LOW);
}

void initAudio() {
  // Allocate audio buffer
  audioBuffer = (int16_t*)malloc(AUDIO_BUFFER_SIZE * sizeof(int16_t));
  
  // I2S config
  i2s_config_t i2sConfig = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
    .sample_rate = I2S_SAMPLE_RATE,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = I2S_COMM_FORMAT_I2S,
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = 8,
    .dma_buf_len = AUDIO_BUFFER_SIZE,
    .use_apll = true
  };
  
  i2s_pin_config_t pinConfig = {
    .bck_io_num = I2S_BCK_PIN,
    .ws_io_num = I2S_WS_PIN,
    .data_out_num = I2S_PIN_NO_CHANGE,
    .data_in_num = I2S_DATA_PIN
  };
  
  i2s_driver_install(I2S_NUM_0, &i2sConfig, 0, NULL);
  i2s_set_pin(I2S_NUM_0, &pinConfig);
  i2s_zero_dma_buffer(I2S_NUM_0);
  
  Serial.println("✅ Audio system initialized");
}

void connectWiFi() {
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.printf("\n✅ WiFi connected: %s\n", WiFi.localIP().toString().c_str());
  digitalWrite(LED_STATUS, HIGH);
}

void initWebSocket() {
  webSocket.beginSSL(WS_SERVER, WS_PORT, "/ws/" + String(DEVICE_ID));
  webSocket.onEvent(webSocketEvent);
  webSocket.setReconnectInterval(5000);
  webSocket.enableHeartbeat(30000, 3000, 2);
  
  Serial.println("✅ WebSocket initialized");
}

// ================ MAIN LOOP ================
void loop() {
  webSocket.loop();
  handleButtons();
  
  if (recording && wsConnected) {
    captureAndStreamAudio();
  }
  
  delay(10);
}

void handleButtons() {
  static bool lastButtonState = false;
  bool currentButtonState = digitalRead(BUTTON_TALK) == LOW;
  
  if (currentButtonState && !lastButtonState) {
    startRecording();
  } else if (!currentButtonState && lastButtonState) {
    stopRecording();
  }
  
  lastButtonState = currentButtonState;
}

void captureAndStreamAudio() {
  size_t bytesRead = 0;
  
  esp_err_t result = i2s_read(I2S_NUM_0, audioBuffer, 
                             AUDIO_BUFFER_SIZE * sizeof(int16_t), 
                             &bytesRead, 100);
  
  if (result == ESP_OK && bytesRead > 0) {
    // Apply simple noise gate
    applyNoiseGate(audioBuffer, bytesRead / sizeof(int16_t));
    
    // Send audio via WebSocket
    webSocket.sendBIN((uint8_t*)audioBuffer, bytesRead);
    
    Serial.printf("📡 Streamed %d bytes\n", bytesRead);
  }
}

void applyNoiseGate(int16_t* samples, size_t count) {
  const int16_t threshold = 150;
  
  for (size_t i = 0; i < count; i++) {
    if (abs(samples[i]) < threshold) {
      samples[i] = 0;
    }
  }
}

// ================ RECORDING CONTROL ================
void startRecording() {
  if (!wsConnected) {
    Serial.println("❌ WebSocket not connected");
    return;
  }
  
  Serial.println("🎤 Starting recording...");
  recording = true;
  
  // Send start notification
  StaticJsonDocument<256> doc;
  doc["type"] = "audio_start";
  doc["device_id"] = DEVICE_ID;
  doc["timestamp"] = millis();
  doc["sample_rate"] = I2S_SAMPLE_RATE;
  
  String message;
  serializeJson(doc, message);
  webSocket.sendTXT(message);
  
  digitalWrite(LED_LISTENING, HIGH);
  digitalWrite(LED_PROCESSING, HIGH);
}

void stopRecording() {
  if (!recording) return;
  
  Serial.println("🛑 Stopping recording...");
  recording = false;
  
  // Send end notification
  StaticJsonDocument<256> doc;
  doc["type"] = "audio_end";
  doc["device_id"] = DEVICE_ID;
  doc["timestamp"] = millis();
  
  String message;
  serializeJson(doc, message);
  webSocket.sendTXT(message);
  
  digitalWrite(LED_LISTENING, LOW);
  digitalWrite(LED_PROCESSING, LOW);
}

// ================ WEBSOCKET EVENTS ================
void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
  switch(type) {
    case WStype_DISCONNECTED:
      Serial.println("🔌 WebSocket Disconnected");
      wsConnected = false;
      digitalWrite(LED_STATUS, LOW);
      break;
      
    case WStype_CONNECTED:
      Serial.printf("✅ WebSocket Connected to: %s\n", payload);
      wsConnected = true;
      digitalWrite(LED_STATUS, HIGH);
      sendMetadata();
      break;
      
    case WStype_TEXT:
      handleTextMessage((char*)payload, length);
      break;
      
    case WStype_BIN:
      handleBinaryMessage(payload, length);
      break;
      
    case WStype_PING:
      Serial.println("🏓 Ping received");
      break;
      
    case WStype_PONG:
      Serial.println("🏓 Pong received");
      break;
      
    default:
      break;
  }
}

void sendMetadata() {
  StaticJsonDocument<384> doc;
  doc["type"] = "metadata";
  doc["device_id"] = DEVICE_ID;
  doc["timestamp"] = millis();
  doc["sample_rate"] = I2S_SAMPLE_RATE;
  doc["channels"] = 1;
  doc["bits_per_sample"] = 16;
  doc["version"] = "1.0";
  
  JsonObject capabilities = doc.createNestedObject("capabilities");
  capabilities["audio_streaming"] = true;
  capabilities["noise_gate"] = true;
  capabilities["psram"] = psramFound();
  
  String message;
  serializeJson(doc, message);
  webSocket.sendTXT(message);
  
  Serial.println("📤 Metadata sent");
}

void handleTextMessage(char* message, size_t length) {
  Serial.printf("📨 Text message: %.*s\n", length, message);
  
  StaticJsonDocument<512> doc;
  if (deserializeJson(doc, message, length) == DeserializationError::Ok) {
    String msgType = doc["type"] | "";
    
    if (msgType == "ack") {
      String ackType = doc["ack_type"] | "";
      if (ackType == "metadata") {
        sessionId = doc["session_id"] | "";
        Serial.printf("🎯 Session started: %s\n", sessionId.c_str());
      }
    } else if (msgType == "response") {
      String responseText = doc["text"] | "";
      Serial.printf("🤖 AI Response: %s\n", responseText.c_str());
    } else if (msgType == "error") {
      String errorMsg = doc["message"] | "";
      Serial.printf("🚨 Server error: %s\n", errorMsg.c_str());
    }
  }
}

void handleBinaryMessage(uint8_t* data, size_t length) {
  Serial.printf("📦 Binary message: %d bytes\n", length);
  // Handle TTS audio or other binary data
}

// ================ UTILITY FUNCTIONS ================
void blinkLED(int pin, int times, int delayMs) {
  for (int i = 0; i < times; i++) {
    digitalWrite(pin, HIGH);
    delay(delayMs);
    digitalWrite(pin, LOW);
    delay(delayMs);
  }
} 