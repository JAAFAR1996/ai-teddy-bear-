/*
🧸 AI Teddy Bear - WebSocket Handler v1.0
Advanced WebSocket client with reconnection, heartbeat, and audio streaming
*/

#include <WebSocketsClient.h>
#include <WiFiClientSecure.h>
#include <ArduinoJson.h>
#include "macros.h"

// ================ WEBSOCKET GLOBALS ================
WebSocketsClient webSocket;
WiFiClientSecure wsClient;

// Connection state
bool ws_connected = false;
bool ws_connecting = false;
unsigned long last_heartbeat = 0;
unsigned long last_reconnect_attempt = 0;
int reconnect_attempts = 0;

// Session management
String session_id = "";
unsigned long session_start_time = 0;
bool session_active = false;

// Audio streaming state
bool audio_streaming = false;
size_t bytes_sent_this_session = 0;
size_t total_bytes_sent = 0;
unsigned long stream_start_time = 0;

// Performance statistics
struct WSPerformanceStats {
  unsigned long total_messages_sent = 0;
  unsigned long total_messages_received = 0;
  unsigned long total_bytes_sent = 0;
  unsigned long total_bytes_received = 0;
  unsigned long connection_count = 0;
  unsigned long last_ping_ms = 0;
  float average_latency_ms = 0.0;
  bool connection_stable = false;
};

WSPerformanceStats ws_stats;

// ================ WEBSOCKET INITIALIZATION ================

void init_websocket() {
  DEBUG_PRINTLN("🌐 Initializing WebSocket client...");
  
  // Configure SSL if enabled
  if (WS_USE_SSL) {
    wsClient.setInsecure(); // For development - use proper certificates in production
    // wsClient.setCACert(root_ca); // Use proper CA certificate
    DEBUG_PRINTLN("✅ SSL/TLS configured for WebSocket");
  }
  
  // Set WebSocket event handler
  webSocket.onEvent(websocket_event);
  
  // Configure connection parameters
  webSocket.setReconnectInterval(WS_RECONNECT_INTERVAL);
  
  // Enable heartbeat
  webSocket.enableHeartbeat(WS_HEARTBEAT_INTERVAL, 3000, 2);
  
  DEBUG_PRINTLN("✅ WebSocket client initialized");
}

void connect_websocket() {
  if (ws_connecting || ws_connected) {
    return;
  }
  
  if (WiFi.status() != WL_CONNECTED) {
    DEBUG_PRINTLN("❌ Cannot connect WebSocket - No WiFi");
    return;
  }
  
  ws_connecting = true;
  reconnect_attempts++;
  
  String endpoint = String(WS_ENDPOINT_PREFIX) + device_id;
  
  DEBUG_PRINTF("🔗 Connecting to WebSocket: %s:%d%s\n", 
               WS_SERVER_HOST, WS_SERVER_PORT, endpoint.c_str());
  
  if (WS_USE_SSL) {
    webSocket.beginSSL(WS_SERVER_HOST, WS_SERVER_PORT, endpoint);
  } else {
    webSocket.begin(WS_SERVER_HOST, WS_SERVER_PORT, endpoint);
  }
  
  // Add authentication headers
  if (!api_key.isEmpty()) {
    webSocket.setAuthorization("Bearer", api_key.c_str());
  }
  
  last_reconnect_attempt = millis();
}

void disconnect_websocket() {
  if (ws_connected || ws_connecting) {
    DEBUG_PRINTLN("🔌 Disconnecting WebSocket...");
    webSocket.disconnect();
    ws_connected = false;
    ws_connecting = false;
    session_active = false;
    audio_streaming = false;
  }
}

// ================ WEBSOCKET EVENT HANDLER ================

void websocket_event(WStype_t type, uint8_t * payload, size_t length) {
  switch(type) {
    case WStype_DISCONNECTED:
      handle_ws_disconnected();
      break;
      
    case WStype_CONNECTED:
      handle_ws_connected(payload, length);
      break;
      
    case WStype_TEXT:
      handle_ws_text_message((char*)payload, length);
      break;
      
    case WStype_BIN:
      handle_ws_binary_message(payload, length);
      break;
      
    case WStype_PING:
      handle_ws_ping();
      break;
      
    case WStype_PONG:
      handle_ws_pong();
      break;
      
    case WStype_ERROR:
      handle_ws_error(payload, length);
      break;
      
    default:
      DEBUG_PRINTF("⚠️ Unknown WebSocket event: %d\n", type);
      break;
  }
}

void handle_ws_disconnected() {
  DEBUG_PRINTLN("🔌 WebSocket disconnected");
  ws_connected = false;
  ws_connecting = false;
  session_active = false;
  audio_streaming = false;
  
  set_status_led(false, false, false, true); // Red LED for disconnection
  
  // Schedule reconnection if under attempt limit
  if (reconnect_attempts < WS_MAX_RECONNECT_ATTEMPTS) {
    last_reconnect_attempt = millis();
    DEBUG_PRINTF("⏳ Will attempt reconnection in %d seconds (attempt %d/%d)\n",
                 WS_RECONNECT_INTERVAL/1000, reconnect_attempts + 1, WS_MAX_RECONNECT_ATTEMPTS);
  } else {
    DEBUG_PRINTLN("❌ Max reconnection attempts reached");
    handle_critical_error("WebSocket connection failed permanently");
  }
}

void handle_ws_connected(uint8_t * payload, size_t length) {
  DEBUG_PRINTF("✅ WebSocket connected to: %s\n", payload);
  
  ws_connected = true;
  ws_connecting = false;
  reconnect_attempts = 0;
  ws_stats.connection_count++;
  ws_stats.connection_stable = true;
  
  set_status_led(true, false, false, false); // Green LED for connection
  
  // Send initial metadata
  send_session_metadata();
  
  // Start heartbeat timer
  last_heartbeat = millis();
  
  DEBUG_PRINTLN("🎯 WebSocket ready for audio streaming");
}

void handle_ws_text_message(char* message, size_t length) {
  DEBUG_PRINTF("📨 Received text message: %.*s\n", length, message);
  
  ws_stats.total_messages_received++;
  ws_stats.total_bytes_received += length;
  
  // Parse JSON message
  StaticJsonDocument<512> doc;
  DeserializationError error = deserializeJson(doc, message, length);
  
  if (error) {
    DEBUG_PRINTF("❌ JSON parse error: %s\n", error.c_str());
    return;
  }
  
  String msg_type = doc["type"] | "";
  
  if (msg_type == "ack") {
    handle_acknowledgment(doc);
  } else if (msg_type == "response") {
    handle_ai_response(doc);
  } else if (msg_type == "error") {
    handle_server_error(doc);
  } else if (msg_type == "ping") {
    send_pong_response();
  } else if (msg_type == "session_start") {
    handle_session_start(doc);
  } else if (msg_type == "session_end") {
    handle_session_end(doc);
  } else {
    DEBUG_PRINTF("⚠️ Unknown message type: %s\n", msg_type.c_str());
  }
}

void handle_ws_binary_message(uint8_t* data, size_t length) {
  DEBUG_PRINTF("📦 Received binary message: %d bytes\n", length);
  ws_stats.total_bytes_received += length;
  
  // Handle binary responses (e.g., TTS audio)
  if (length > 0) {
    play_received_audio(data, length);
  }
}

void handle_ws_ping() {
  DEBUG_PRINTLN_VERBOSE("🏓 Received ping");
  unsigned long ping_time = millis();
  ws_stats.last_ping_ms = ping_time;
}

void handle_ws_pong() {
  DEBUG_PRINTLN_VERBOSE("🏓 Received pong");
  unsigned long pong_time = millis();
  
  if (ws_stats.last_ping_ms > 0) {
    unsigned long latency = pong_time - ws_stats.last_ping_ms;
    ws_stats.average_latency_ms = (ws_stats.average_latency_ms + latency) / 2.0;
    DEBUG_PRINTF_VERBOSE("⚡ Latency: %lu ms (avg: %.1f ms)\n", 
                         latency, ws_stats.average_latency_ms);
  }
}

void handle_ws_error(uint8_t* payload, size_t length) {
  DEBUG_PRINTF("❌ WebSocket error: %.*s\n", length, payload);
  ws_stats.connection_stable = false;
}

// ================ MESSAGE HANDLERS ================

void handle_acknowledgment(StaticJsonDocument<512>& doc) {
  String ack_type = doc["ack_type"] | "";
  DEBUG_PRINTF("✅ Received acknowledgment: %s\n", ack_type.c_str());
  
  if (ack_type == "metadata") {
    session_active = true;
    session_id = doc["session_id"] | "";
    session_start_time = millis();
    DEBUG_PRINTF("🎯 Session started: %s\n", session_id.c_str());
  } else if (ack_type == "audio_start") {
    audio_streaming = true;
    stream_start_time = millis();
    bytes_sent_this_session = 0;
    DEBUG_PRINTLN("🎤 Audio streaming confirmed");
  } else if (ack_type == "audio_end") {
    audio_streaming = false;
    DEBUG_PRINTLN("🎤 Audio streaming ended");
  }
}

void handle_ai_response(StaticJsonDocument<512>& doc) {
  String response_text = doc["text"] | "";
  String response_type = doc["response_type"] | "text";
  
  DEBUG_PRINTF("🤖 AI Response (%s): %s\n", response_type.c_str(), response_text.c_str());
  
  if (response_type == "tts") {
    // TTS audio will come as binary message
    DEBUG_PRINTLN("🔊 Waiting for TTS audio...");
  } else {
    // Display text response if needed
    display_text_response(response_text);
  }
}

void handle_server_error(StaticJsonDocument<512>& doc) {
  String error_message = doc["message"] | "Unknown error";
  String error_code = doc["code"] | "ERR_UNKNOWN";
  
  DEBUG_PRINTF("🚨 Server error [%s]: %s\n", error_code.c_str(), error_message.c_str());
  
  set_status_led(false, false, false, true); // Red LED for error
  
  // Handle specific error types
  if (error_code == "AUTH_FAILED") {
    DEBUG_PRINTLN("🔒 Authentication failed - check API key");
  } else if (error_code == "RATE_LIMIT") {
    DEBUG_PRINTLN("⏱️ Rate limit exceeded - please wait");
  } else if (error_code == "AUDIO_ERROR") {
    DEBUG_PRINTLN("🎤 Audio processing error");
  }
}

void handle_session_start(StaticJsonDocument<512>& doc) {
  session_id = doc["session_id"] | "";
  session_active = true;
  DEBUG_PRINTF("🎯 Server initiated session: %s\n", session_id.c_str());
}

void handle_session_end(StaticJsonDocument<512>& doc) {
  DEBUG_PRINTLN("🏁 Session ended by server");
  session_active = false;
  audio_streaming = false;
}

// ================ SENDING FUNCTIONS ================

void send_session_metadata() {
  if (!ws_connected) return;
  
  StaticJsonDocument<384> doc;
  doc["type"] = "metadata";
  doc["device_id"] = device_id;
  doc["session_id"] = generate_session_id();
  doc["timestamp"] = millis();
  doc["sample_rate"] = I2S_SAMPLE_RATE;
  doc["channels"] = I2S_CHANNELS;
  doc["bits_per_sample"] = I2S_BITS_PER_SAMPLE;
  doc["buffer_size"] = AUDIO_BUFFER_SIZE;
  doc["version"] = "1.0";
  
  // Add device capabilities
  JsonObject capabilities = doc.createNestedObject("capabilities");
  capabilities["audio_streaming"] = true;
  capabilities["noise_gate"] = ENABLE_NOISE_GATE;
  capabilities["agc"] = ENABLE_AGC;
  capabilities["psram"] = psramFound();
  
  String message;
  serializeJson(doc, message);
  
  bool sent = webSocket.sendTXT(message);
  if (sent) {
    DEBUG_PRINTLN("📤 Metadata sent successfully");
    ws_stats.total_messages_sent++;
    ws_stats.total_bytes_sent += message.length();
  } else {
    DEBUG_PRINTLN("❌ Failed to send metadata");
  }
}

bool send_audio_chunk(uint8_t* audio_data, size_t data_size) {
  if (!ws_connected || !session_active) {
    DEBUG_PRINTLN("❌ Cannot send audio - not connected or no active session");
    return false;
  }
  
  if (data_size == 0 || data_size > MAX_MESSAGE_SIZE) {
    DEBUG_PRINTF("❌ Invalid audio chunk size: %d bytes\n", data_size);
    return false;
  }
  
  bool sent = webSocket.sendBIN(audio_data, data_size);
  
  if (sent) {
    bytes_sent_this_session += data_size;
    total_bytes_sent += data_size;
    ws_stats.total_bytes_sent += data_size;
    
    DEBUG_PRINTF_VERBOSE("📤 Audio chunk sent: %d bytes (session total: %d)\n", 
                         data_size, bytes_sent_this_session);
    return true;
  } else {
    DEBUG_PRINTF("❌ Failed to send audio chunk: %d bytes\n", data_size);
    return false;
  }
}

void send_audio_start_notification() {
  if (!ws_connected) return;
  
  StaticJsonDocument<256> doc;
  doc["type"] = "audio_start";
  doc["session_id"] = session_id;
  doc["timestamp"] = millis();
  doc["expected_duration"] = MAX_AUDIO_DURATION_MS;
  
  String message;
  serializeJson(doc, message);
  
  webSocket.sendTXT(message);
  DEBUG_PRINTLN("📤 Audio start notification sent");
}

void send_audio_end_notification() {
  if (!ws_connected) return;
  
  StaticJsonDocument<256> doc;
  doc["type"] = "audio_end";
  doc["session_id"] = session_id;
  doc["timestamp"] = millis();
  doc["total_bytes"] = bytes_sent_this_session;
  doc["duration_ms"] = millis() - stream_start_time;
  
  String message;
  serializeJson(doc, message);
  
  webSocket.sendTXT(message);
  DEBUG_PRINTLN("📤 Audio end notification sent");
}

void send_heartbeat() {
  if (!ws_connected) return;
  
  unsigned long now = millis();
  if (now - last_heartbeat >= WS_HEARTBEAT_INTERVAL) {
    StaticJsonDocument<128> doc;
    doc["type"] = "heartbeat";
    doc["timestamp"] = now;
    doc["session_active"] = session_active;
    
    String message;
    serializeJson(doc, message);
    
    webSocket.sendTXT(message);
    last_heartbeat = now;
    
    DEBUG_PRINTLN_VERBOSE("💓 Heartbeat sent");
  }
}

void send_pong_response() {
  StaticJsonDocument<64> doc;
  doc["type"] = "pong";
  doc["timestamp"] = millis();
  
  String message;
  serializeJson(doc, message);
  
  webSocket.sendTXT(message);
  DEBUG_PRINTLN_VERBOSE("🏓 Pong sent");
}

// ================ UTILITY FUNCTIONS ================

void websocket_loop() {
  webSocket.loop();
  
  // Handle reconnection
  if (!ws_connected && !ws_connecting) {
    unsigned long now = millis();
    if (now - last_reconnect_attempt >= WS_RECONNECT_INTERVAL) {
      if (reconnect_attempts < WS_MAX_RECONNECT_ATTEMPTS) {
        connect_websocket();
      }
    }
  }
  
  // Send periodic heartbeat
  if (ws_connected) {
    send_heartbeat();
  }
  
  // Update performance statistics
  update_performance_stats();
}

String generate_session_id() {
  return device_id + "_" + String(millis()) + "_" + String(random(1000, 9999));
}

void update_performance_stats() {
  static unsigned long last_stats_update = 0;
  unsigned long now = millis();
  
  if (now - last_stats_update >= STATS_REPORT_INTERVAL) {
    if (ENABLE_PERFORMANCE_STATS && DEBUG_LEVEL >= 2) {
      DEBUG_PRINTLN("📊 WebSocket Performance Stats:");
      DEBUG_PRINTF("   Connected: %s | Attempts: %d\n", 
                   ws_connected ? "Yes" : "No", ws_stats.connection_count);
      DEBUG_PRINTF("   Messages: %lu sent, %lu received\n", 
                   ws_stats.total_messages_sent, ws_stats.total_messages_received);
      DEBUG_PRINTF("   Data: %lu bytes sent, %lu bytes received\n", 
                   ws_stats.total_bytes_sent, ws_stats.total_bytes_received);
      DEBUG_PRINTF("   Latency: %.1f ms avg\n", ws_stats.average_latency_ms);
      
      if (session_active) {
        unsigned long session_duration = (millis() - session_start_time) / 1000;
        DEBUG_PRINTF("   Session: %s (active %lu sec)\n", 
                     session_id.c_str(), session_duration);
      }
    }
    
    last_stats_update = now;
  }
}

bool is_websocket_ready() {
  return ws_connected && session_active;
}

// ================ EXTERNAL INTERFACE ================

bool websocket_send_audio_stream(uint8_t* audio_data, size_t data_size) {
  return send_audio_chunk(audio_data, data_size);
}

void websocket_start_audio_session() {
  send_audio_start_notification();
}

void websocket_end_audio_session() {
  send_audio_end_notification();
} 