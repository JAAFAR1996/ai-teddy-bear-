/*
🧸 AI Teddy Bear - Real-time Audio Streaming System v1.0
Advanced ESP32 microphone capture with WebSocket streaming
Features: I2S audio input, real-time streaming, automatic reconnection, noise gate
*/

#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <Preferences.h>
#include <driver/i2s.h>
#include <esp_sleep.h>
#include <esp_log.h>
#include <esp_heap_caps.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"
#include "freertos/semphr.h"

// Include our custom modules
#include "macros.h"
#include "ws_handler.ino"

// ================ GLOBAL VARIABLES ================
Preferences preferences;

// Device configuration
String wifi_ssid = "";
String wifi_password = "";
String server_url = "https://teddy-cloud.example.com";
String device_id = "";
String api_key = "";

// System state
volatile int system_status = STATUS_IDLE;
volatile bool recording_active = false;
volatile bool streaming_active = false;
unsigned long last_button_press = 0;
unsigned long last_activity = 0;

// Audio buffers and management
int16_t* i2s_read_buffer = nullptr;
uint8_t* stream_buffer = nullptr;
QueueHandle_t audio_queue = nullptr;
SemaphoreHandle_t buffer_mutex = nullptr;
TaskHandle_t audio_task_handle = nullptr;
TaskHandle_t stream_task_handle = nullptr;

// Audio processing state
struct AudioStream {
  int16_t* data;
  size_t samples;
  unsigned long timestamp;
  bool processed;
};

// Circular buffer for audio streaming
struct CircularAudioBuffer {
  AudioStream* buffers;
  int head;
  int tail;
  int count;
  int max_count;
  SemaphoreHandle_t mutex;
};

CircularAudioBuffer stream_buffer_queue;

// Performance monitoring
struct SystemPerformance {
  unsigned long audio_samples_captured = 0;
  unsigned long audio_bytes_streamed = 0;
  unsigned long buffer_overruns = 0;
  unsigned long stream_errors = 0;
  float cpu_usage_percent = 0.0;
  size_t free_heap = 0;
  size_t free_psram = 0;
  unsigned long uptime_seconds = 0;
};

SystemPerformance perf_stats;

// ================ SETUP AND INITIALIZATION ================

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  display_startup_banner();
  
  // Initialize hardware
  init_hardware_pins();
  
  // Check system capabilities
  check_system_capabilities();
  
  // Load configuration
  load_device_configuration();
  
  // Generate device ID if needed
  ensure_device_id();
  
  // Initialize audio system
  init_audio_system();
  
  // Initialize networking
  init_networking();
  
  // Initialize WebSocket
  init_websocket();
  
  // Create FreeRTOS tasks
  create_system_tasks();
  
  // Final system check
  perform_system_health_check();
  
  DEBUG_PRINTLN("🧸 Teddy Bear Audio Streaming System Ready!");
  DEBUG_PRINTLN("   Press TALK button to start streaming audio");
  
  set_system_status(STATUS_IDLE);
}

void display_startup_banner() {
  DEBUG_PRINTLN("\n" + String("=").substring(0, 50));
  DEBUG_PRINTLN("🧸 AI Teddy Bear - Audio Streaming v1.0");
  DEBUG_PRINTLN("   Real-time I2S → WebSocket Audio Pipeline");
  DEBUG_PRINTLN("   Built with ESP32 FreeRTOS");
  DEBUG_PRINTLN(String("=").substring(0, 50));
}

void init_hardware_pins() {
  DEBUG_PRINTLN("🔧 Initializing hardware pins...");
  
  // Configure input pins with pullup
  pinMode(BUTTON_TALK, INPUT_PULLUP);
  pinMode(BUTTON_VOLUME_UP, INPUT_PULLUP);
  pinMode(BUTTON_VOLUME_DOWN, INPUT_PULLUP);
  
  // Configure LED outputs
  pinMode(LED_STATUS, OUTPUT);
  pinMode(LED_LISTENING, OUTPUT);
  pinMode(LED_PROCESSING, OUTPUT);
  pinMode(LED_ERROR, OUTPUT);
  
  // Initial LED state - all off
  set_all_leds(false);
  
  DEBUG_PRINTLN("✅ Hardware pins configured");
}

void check_system_capabilities() {
  DEBUG_PRINTLN("🔍 Checking system capabilities...");
  
  // Check PSRAM
  if (psramFound()) {
    size_t psram_size = ESP.getPsramSize();
    size_t free_psram = ESP.getFreePsram();
    DEBUG_PRINTF("✅ PSRAM: %d bytes total, %d bytes free\n", psram_size, free_psram);
  } else {
    DEBUG_PRINTLN("⚠️ No PSRAM found - using internal RAM only");
    DEBUG_PRINTLN("💡 Recommend ESP32-S3 with PSRAM for optimal performance");
  }
  
  // Check available heap
  size_t free_heap = ESP.getFreeHeap();
  DEBUG_PRINTF("🔋 Free heap: %d bytes\n", free_heap);
  
  // Check CPU frequency
  uint32_t cpu_freq = ESP.getCpuFreqMHz();
  DEBUG_PRINTF("⚡ CPU frequency: %d MHz\n", cpu_freq);
  
  if (cpu_freq < 240) {
    DEBUG_PRINTLN("⚠️ CPU frequency below 240MHz may impact performance");
  }
}

void load_device_configuration() {
  DEBUG_PRINTLN("📂 Loading device configuration...");
  
  preferences.begin("teddy_audio", false);
  
  wifi_ssid = preferences.getString(WIFI_SSID_KEY, "");
  wifi_password = preferences.getString(WIFI_PASS_KEY, "");
  server_url = preferences.getString(SERVER_URL_KEY, "https://teddy-cloud.example.com");
  device_id = preferences.getString(DEVICE_ID_KEY, "");
  api_key = preferences.getString(API_KEY_KEY, "");
  
  DEBUG_PRINTLN("✅ Configuration loaded");
  
  if (wifi_ssid.isEmpty()) {
    DEBUG_PRINTLN("⚠️ No WiFi credentials found");
    enter_configuration_mode();
  }
}

void ensure_device_id() {
  if (device_id.isEmpty()) {
    device_id = generate_unique_device_id();
    preferences.putString(DEVICE_ID_KEY, device_id);
    DEBUG_PRINTF("🆔 Generated new device ID: %s\n", device_id.c_str());
  } else {
    DEBUG_PRINTF("🆔 Using existing device ID: %s\n", device_id.c_str());
  }
}

// ================ AUDIO SYSTEM INITIALIZATION ================

void init_audio_system() {
  DEBUG_PRINTLN("🎤 Initializing advanced audio system...");
  
  // Allocate audio buffers
  allocate_audio_buffers();
  
  // Configure I2S
  configure_i2s_interface();
  
  // Initialize circular buffer
  init_circular_audio_buffer();
  
  // Create synchronization primitives
  create_audio_sync_objects();
  
  DEBUG_PRINTLN("✅ Audio system initialized");
}

void allocate_audio_buffers() {
  DEBUG_PRINTLN("📦 Allocating audio buffers...");
  
  // Allocate I2S read buffer (prefer PSRAM if available)
  if (psramFound()) {
    i2s_read_buffer = (int16_t*)heap_caps_malloc(
      AUDIO_BUFFER_SIZE * sizeof(int16_t), 
      MALLOC_CAP_SPIRAM
    );
    stream_buffer = (uint8_t*)heap_caps_malloc(
      STREAM_CHUNK_SIZE * STREAM_BUFFER_COUNT, 
      MALLOC_CAP_SPIRAM
    );
    DEBUG_PRINTLN("✅ Audio buffers allocated in PSRAM");
  } else {
    i2s_read_buffer = (int16_t*)malloc(AUDIO_BUFFER_SIZE * sizeof(int16_t));
    stream_buffer = (uint8_t*)malloc(STREAM_CHUNK_SIZE * STREAM_BUFFER_COUNT);
    DEBUG_PRINTLN("✅ Audio buffers allocated in internal RAM");
  }
  
  if (!i2s_read_buffer || !stream_buffer) {
    DEBUG_PRINTLN("❌ CRITICAL: Failed to allocate audio buffers!");
    handle_critical_error("Audio buffer allocation failed");
    return;
  }
  
  // Clear buffers
  memset(i2s_read_buffer, 0, AUDIO_BUFFER_SIZE * sizeof(int16_t));
  memset(stream_buffer, 0, STREAM_CHUNK_SIZE * STREAM_BUFFER_COUNT);
}

void configure_i2s_interface() {
  DEBUG_PRINTLN("🔊 Configuring I2S interface...");
  
  // I2S configuration for microphone input
  i2s_config_t i2s_config = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
    .sample_rate = I2S_SAMPLE_RATE,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = I2S_COMM_FORMAT_I2S,
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = 8,
    .dma_buf_len = AUDIO_BUFFER_SIZE,
    .use_apll = true,                    // Use APLL for better precision
    .tx_desc_auto_clear = false,
    .fixed_mclk = 0
  };
  
  // I2S pin configuration
  i2s_pin_config_t pin_config = {
    .bck_io_num = I2S_BCK_PIN,
    .ws_io_num = I2S_WS_PIN,
    .data_out_num = I2S_DATA_OUT_PIN,
    .data_in_num = I2S_DATA_IN_PIN
  };
  
  // Install I2S driver
  esp_err_t err = i2s_driver_install(I2S_NUM, &i2s_config, 0, NULL);
  if (err != ESP_OK) {
    DEBUG_PRINTF("❌ I2S driver install failed: %s\n", esp_err_to_name(err));
    handle_critical_error("I2S driver installation failed");
    return;
  }
  
  // Set I2S pins
  err = i2s_set_pin(I2S_NUM, &pin_config);
  if (err != ESP_OK) {
    DEBUG_PRINTF("❌ I2S pin configuration failed: %s\n", esp_err_to_name(err));
    handle_critical_error("I2S pin configuration failed");
    return;
  }
  
  // Clear I2S DMA buffer
  i2s_zero_dma_buffer(I2S_NUM);
  
  DEBUG_PRINTF("✅ I2S configured: %d Hz, %d-bit, %s\n", 
               I2S_SAMPLE_RATE, I2S_BITS_PER_SAMPLE, 
               I2S_CHANNELS == 1 ? "Mono" : "Stereo");
}

void init_circular_audio_buffer() {
  stream_buffer_queue.max_count = STREAM_BUFFER_COUNT;
  stream_buffer_queue.buffers = (AudioStream*)malloc(
    sizeof(AudioStream) * STREAM_BUFFER_COUNT
  );
  
  if (!stream_buffer_queue.buffers) {
    handle_critical_error("Failed to allocate circular buffer");
    return;
  }
  
  // Initialize each buffer slot
  for (int i = 0; i < STREAM_BUFFER_COUNT; i++) {
    stream_buffer_queue.buffers[i].data = nullptr;
    stream_buffer_queue.buffers[i].samples = 0;
    stream_buffer_queue.buffers[i].timestamp = 0;
    stream_buffer_queue.buffers[i].processed = true;
  }
  
  stream_buffer_queue.head = 0;
  stream_buffer_queue.tail = 0;
  stream_buffer_queue.count = 0;
  
  DEBUG_PRINTLN("✅ Circular audio buffer initialized");
}

void create_audio_sync_objects() {
  // Create mutex for buffer access
  buffer_mutex = xSemaphoreCreateMutex();
  stream_buffer_queue.mutex = xSemaphoreCreateMutex();
  
  // Create queue for audio data transfer
  audio_queue = xQueueCreate(STREAM_BUFFER_COUNT, sizeof(AudioStream*));
  
  if (!buffer_mutex || !stream_buffer_queue.mutex || !audio_queue) {
    handle_critical_error("Failed to create synchronization objects");
    return;
  }
  
  DEBUG_PRINTLN("✅ Audio synchronization objects created");
}

// ================ NETWORKING INITIALIZATION ================

void init_networking() {
  DEBUG_PRINTLN("📡 Initializing networking...");
  
  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(true);
  
  connect_wifi();
  
  if (WiFi.status() == WL_CONNECTED) {
    DEBUG_PRINTF("✅ WiFi connected: %s\n", WiFi.localIP().toString().c_str());
    DEBUG_PRINTF("   Signal strength: %d dBm\n", WiFi.RSSI());
  } else {
    DEBUG_PRINTLN("❌ WiFi connection failed");
    handle_critical_error("WiFi connection failed");
  }
}

void connect_wifi() {
  DEBUG_PRINTF("🔗 Connecting to WiFi: %s\n", wifi_ssid.c_str());
  
  WiFi.begin(wifi_ssid.c_str(), wifi_password.c_str());
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < MAX_WIFI_RECONNECT_ATTEMPTS) {
    delay(500);
    attempts++;
    
    if (attempts % 4 == 0) {
      DEBUG_PRINTF("⏳ WiFi connecting... (%d/%d)\n", attempts, MAX_WIFI_RECONNECT_ATTEMPTS);
    }
    
    // Blink status LED while connecting
    digitalWrite(LED_STATUS, !digitalRead(LED_STATUS));
  }
  
  if (WiFi.status() != WL_CONNECTED) {
    DEBUG_PRINTLN("❌ WiFi connection timeout");
    return;
  }
  
  digitalWrite(LED_STATUS, HIGH); // Solid green when connected
}

// ================ FREERTOS TASK CREATION ================

void create_system_tasks() {
  DEBUG_PRINTLN("⚙️ Creating FreeRTOS tasks...");
  
  // Create high-priority audio capture task
  xTaskCreatePinnedToCore(
    audio_capture_task,     // Task function
    "AudioCapture",         // Task name
    8192,                   // Stack size
    NULL,                   // Parameters
    configMAX_PRIORITIES - 1, // High priority
    &audio_task_handle,     // Task handle
    1                       // Pin to core 1
  );
  
  // Create medium-priority streaming task
  xTaskCreatePinnedToCore(
    audio_stream_task,      // Task function
    "AudioStream",          // Task name
    8192,                   // Stack size
    NULL,                   // Parameters
    configMAX_PRIORITIES - 2, // Medium-high priority
    &stream_task_handle,    // Task handle
    0                       // Pin to core 0
  );
  
  DEBUG_PRINTLN("✅ FreeRTOS tasks created");
}

// ================ MAIN LOOP ================

void loop() {
  // Handle WebSocket events
  websocket_loop();
  
  // Check button presses
  handle_button_input();
  
  // Update system status
  update_system_status();
  
  // Monitor performance
  update_performance_stats();
  
  // Handle auto-sleep
  check_auto_sleep();
  
  // Small delay to prevent watchdog triggers
  delay(10);
}

// ================ AUDIO CAPTURE TASK ================

void audio_capture_task(void* parameters) {
  DEBUG_PRINTLN("🎤 Audio capture task started");
  
  size_t bytes_read = 0;
  unsigned long last_stats_print = 0;
  
  while (true) {
    if (recording_active) {
      // Read audio data from I2S
      esp_err_t result = i2s_read(
        I2S_NUM,
        i2s_read_buffer,
        AUDIO_BUFFER_SIZE * sizeof(int16_t),
        &bytes_read,
        portMAX_DELAY
      );
      
      if (result == ESP_OK && bytes_read > 0) {
        size_t samples_read = bytes_read / sizeof(int16_t);
        
        // Apply audio processing
        process_audio_samples(i2s_read_buffer, samples_read);
        
        // Add to streaming queue if WebSocket is ready
        if (streaming_active && is_websocket_ready()) {
          add_to_stream_queue(i2s_read_buffer, samples_read);
        }
        
        // Update statistics
        perf_stats.audio_samples_captured += samples_read;
        
        // Debug output every 5 seconds
        if (millis() - last_stats_print > 5000) {
          DEBUG_PRINTF_DETAILED("🎤 Captured: %lu samples, Level: %d\n", 
                               samples_read, get_audio_level(i2s_read_buffer, samples_read));
          last_stats_print = millis();
        }
      } else {
        DEBUG_PRINTF("⚠️ I2S read error: %s\n", esp_err_to_name(result));
        vTaskDelay(pdMS_TO_TICKS(10));
      }
    } else {
      // Not recording - sleep to save CPU
      vTaskDelay(pdMS_TO_TICKS(100));
    }
  }
}

// ================ AUDIO STREAMING TASK ================

void audio_stream_task(void* parameters) {
  DEBUG_PRINTLN("📡 Audio streaming task started");
  
  AudioStream* stream_data;
  
  while (true) {
    if (streaming_active && is_websocket_ready()) {
      // Wait for audio data from capture task
      if (xQueueReceive(audio_queue, &stream_data, pdMS_TO_TICKS(100)) == pdTRUE) {
        
        if (stream_data && stream_data->data && stream_data->samples > 0) {
          // Convert to bytes and send via WebSocket
          size_t data_size = stream_data->samples * sizeof(int16_t);
          
          if (websocket_send_audio_stream((uint8_t*)stream_data->data, data_size)) {
            perf_stats.audio_bytes_streamed += data_size;
            DEBUG_PRINTF_VERBOSE("📡 Streamed %d bytes\n", data_size);
          } else {
            perf_stats.stream_errors++;
            DEBUG_PRINTLN("❌ Failed to stream audio chunk");
          }
          
          // Mark buffer as processed
          stream_data->processed = true;
        }
      }
    } else {
      // Not streaming - sleep
      vTaskDelay(pdMS_TO_TICKS(100));
    }
  }
}

// ================ AUDIO PROCESSING FUNCTIONS ================

void process_audio_samples(int16_t* samples, size_t count) {
  if (!samples || count == 0) return;
  
  // Apply noise gate if enabled
  if (ENABLE_NOISE_GATE) {
    apply_noise_gate(samples, count);
  }
  
  // Apply automatic gain control if enabled
  if (ENABLE_AGC) {
    apply_automatic_gain_control(samples, count);
  }
}

void apply_noise_gate(int16_t* samples, size_t count) {
  for (size_t i = 0; i < count; i++) {
    if (abs(samples[i]) < NOISE_GATE_THRESHOLD) {
      samples[i] = 0;
    }
  }
}

void apply_automatic_gain_control(int16_t* samples, size_t count) {
  // Simple AGC implementation
  int32_t peak = 0;
  
  // Find peak level
  for (size_t i = 0; i < count; i++) {
    int32_t abs_sample = abs(samples[i]);
    if (abs_sample > peak) {
      peak = abs_sample;
    }
  }
  
  // Apply gain if needed
  if (peak > 0 && peak < AGC_TARGET_LEVEL) {
    float gain = (float)AGC_TARGET_LEVEL / peak;
    if (gain > 4.0) gain = 4.0; // Limit maximum gain
    
    for (size_t i = 0; i < count; i++) {
      int32_t amplified = (int32_t)(samples[i] * gain);
      samples[i] = CLAMP(amplified, -32768, 32767);
    }
  }
}

int16_t get_audio_level(int16_t* samples, size_t count) {
  int32_t sum = 0;
  for (size_t i = 0; i < count; i++) {
    sum += abs(samples[i]);
  }
  return (sum / count);
}

void add_to_stream_queue(int16_t* samples, size_t count) {
  if (xSemaphoreTake(stream_buffer_queue.mutex, pdMS_TO_TICKS(10)) == pdTRUE) {
    if (stream_buffer_queue.count < stream_buffer_queue.max_count) {
      int index = stream_buffer_queue.head;
      
      // Allocate buffer for this chunk
      stream_buffer_queue.buffers[index].data = (int16_t*)malloc(count * sizeof(int16_t));
      if (stream_buffer_queue.buffers[index].data) {
        memcpy(stream_buffer_queue.buffers[index].data, samples, count * sizeof(int16_t));
        stream_buffer_queue.buffers[index].samples = count;
        stream_buffer_queue.buffers[index].timestamp = millis();
        stream_buffer_queue.buffers[index].processed = false;
        
        // Send to streaming task
        AudioStream* stream_ptr = &stream_buffer_queue.buffers[index];
        xQueueSend(audio_queue, &stream_ptr, 0);
        
        // Update circular buffer pointers
        stream_buffer_queue.head = (stream_buffer_queue.head + 1) % stream_buffer_queue.max_count;
        stream_buffer_queue.count++;
      }
    } else {
      perf_stats.buffer_overruns++;
      DEBUG_PRINTLN_DETAILED("⚠️ Stream buffer overflow");
    }
    
    xSemaphoreGive(stream_buffer_queue.mutex);
  }
}

// ================ BUTTON AND INPUT HANDLING ================

void handle_button_input() {
  static bool talk_button_pressed = false;
  
  // Handle talk button with debouncing
  bool current_talk_state = digitalRead(BUTTON_TALK) == LOW;
  
  if (current_talk_state && !talk_button_pressed) {
    // Button just pressed
    if (millis() - last_button_press > BUTTON_DEBOUNCE_MS) {
      start_audio_recording();
      talk_button_pressed = true;
      last_button_press = millis();
    }
  } else if (!current_talk_state && talk_button_pressed) {
    // Button just released
    stop_audio_recording();
    talk_button_pressed = false;
  }
  
  // Handle volume buttons
  handle_volume_buttons();
}

void handle_volume_buttons() {
  static unsigned long last_volume_press = 0;
  
  if (millis() - last_volume_press > BUTTON_DEBOUNCE_MS) {
    if (digitalRead(BUTTON_VOLUME_UP) == LOW) {
      // Volume up pressed
      DEBUG_PRINTLN("🔊 Volume up");
      last_volume_press = millis();
    } else if (digitalRead(BUTTON_VOLUME_DOWN) == LOW) {
      // Volume down pressed
      DEBUG_PRINTLN("🔉 Volume down");
      last_volume_press = millis();
    }
  }
}

// ================ AUDIO RECORDING CONTROL ================

void start_audio_recording() {
  if (recording_active) return;
  
  DEBUG_PRINTLN("🎤 Starting audio recording and streaming...");
  
  if (!is_websocket_ready()) {
    DEBUG_PRINTLN("❌ WebSocket not ready - cannot start recording");
    set_status_led(false, false, false, true); // Red error LED
    return;
  }
  
  // Clear any existing buffers
  clear_audio_buffers();
  
  // Reset performance counters
  perf_stats.audio_samples_captured = 0;
  perf_stats.audio_bytes_streamed = 0;
  
  // Start recording and streaming
  recording_active = true;
  streaming_active = true;
  
  // Notify WebSocket that audio session is starting
  websocket_start_audio_session();
  
  // Update LED status
  set_status_led(false, true, true, false); // Blue + Orange = recording + processing
  
  // Update system status
  set_system_status(STATUS_LISTENING);
  
  last_activity = millis();
  
  DEBUG_PRINTLN("✅ Audio recording and streaming started");
}

void stop_audio_recording() {
  if (!recording_active) return;
  
  DEBUG_PRINTLN("🛑 Stopping audio recording and streaming...");
  
  // Stop recording and streaming
  recording_active = false;
  streaming_active = false;
  
  // Notify WebSocket that audio session is ending
  websocket_end_audio_session();
  
  // Clear buffers
  clear_audio_buffers();
  
  // Update LED status
  set_status_led(true, false, false, false); // Green = connected and ready
  
  // Update system status
  set_system_status(STATUS_CONNECTED);
  
  last_activity = millis();
  
  DEBUG_PRINTF("✅ Recording stopped - captured %lu samples, streamed %lu bytes\n",
               perf_stats.audio_samples_captured, perf_stats.audio_bytes_streamed);
}

// ================ UTILITY FUNCTIONS ================

void clear_audio_buffers() {
  if (xSemaphoreTake(stream_buffer_queue.mutex, pdMS_TO_TICKS(100)) == pdTRUE) {
    for (int i = 0; i < stream_buffer_queue.max_count; i++) {
      if (stream_buffer_queue.buffers[i].data) {
        free(stream_buffer_queue.buffers[i].data);
        stream_buffer_queue.buffers[i].data = nullptr;
        stream_buffer_queue.buffers[i].samples = 0;
        stream_buffer_queue.buffers[i].processed = true;
      }
    }
    
    stream_buffer_queue.head = 0;
    stream_buffer_queue.tail = 0;
    stream_buffer_queue.count = 0;
    
    xSemaphoreGive(stream_buffer_queue.mutex);
  }
  
  // Clear I2S buffer
  if (i2s_read_buffer) {
    memset(i2s_read_buffer, 0, AUDIO_BUFFER_SIZE * sizeof(int16_t));
  }
}

void set_system_status(int new_status) {
  system_status = new_status;
  
  switch (new_status) {
    case STATUS_IDLE:
      set_status_led(false, false, false, false);
      break;
    case STATUS_CONNECTING:
      // Blink status LED
      break;
    case STATUS_CONNECTED:
      set_status_led(true, false, false, false);
      break;
    case STATUS_LISTENING:
      set_status_led(false, true, false, false);
      break;
    case STATUS_PROCESSING:
      set_status_led(false, false, true, false);
      break;
    case STATUS_STREAMING:
      set_status_led(false, true, true, false);
      break;
    case STATUS_ERROR:
      set_status_led(false, false, false, true);
      break;
  }
}

void set_status_led(bool green, bool blue, bool orange, bool red) {
  digitalWrite(LED_STATUS, green ? HIGH : LOW);
  digitalWrite(LED_LISTENING, blue ? HIGH : LOW);
  digitalWrite(LED_PROCESSING, orange ? HIGH : LOW);
  digitalWrite(LED_ERROR, red ? HIGH : LOW);
}

void set_all_leds(bool state) {
  digitalWrite(LED_STATUS, state ? HIGH : LOW);
  digitalWrite(LED_LISTENING, state ? HIGH : LOW);
  digitalWrite(LED_PROCESSING, state ? HIGH : LOW);
  digitalWrite(LED_ERROR, state ? HIGH : LOW);
}

void update_system_status() {
  // Update system status based on current state
  if (recording_active && streaming_active) {
    set_system_status(STATUS_STREAMING);
  } else if (is_websocket_ready()) {
    set_system_status(STATUS_CONNECTED);
  } else if (WiFi.status() == WL_CONNECTED) {
    set_system_status(STATUS_CONNECTING);
  } else {
    set_system_status(STATUS_ERROR);
  }
}

void update_performance_stats() {
  static unsigned long last_update = 0;
  
  if (millis() - last_update > STATS_REPORT_INTERVAL) {
    perf_stats.free_heap = ESP.getFreeHeap();
    perf_stats.free_psram = psramFound() ? ESP.getFreePsram() : 0;
    perf_stats.uptime_seconds = millis() / 1000;
    
    if (ENABLE_PERFORMANCE_STATS && DEBUG_LEVEL >= 2) {
      print_performance_stats();
    }
    
    last_update = millis();
  }
}

void print_performance_stats() {
  DEBUG_PRINTLN("📊 System Performance Stats:");
  DEBUG_PRINTF("   Status: %d | Recording: %s | Streaming: %s\n", 
               system_status, recording_active ? "Yes" : "No", streaming_active ? "Yes" : "No");
  DEBUG_PRINTF("   Audio: %lu samples captured, %lu bytes streamed\n", 
               perf_stats.audio_samples_captured, perf_stats.audio_bytes_streamed);
  DEBUG_PRINTF("   Errors: %lu buffer overruns, %lu stream errors\n", 
               perf_stats.buffer_overruns, perf_stats.stream_errors);
  DEBUG_PRINTF("   Memory: %d heap, %d PSRAM free\n", 
               perf_stats.free_heap, perf_stats.free_psram);
  DEBUG_PRINTF("   Uptime: %lu seconds\n", perf_stats.uptime_seconds);
}

void check_auto_sleep() {
  if (millis() - last_activity > SLEEP_TIMEOUT_MS) {
    if (!recording_active && !streaming_active) {
      DEBUG_PRINTLN("😴 Entering sleep mode due to inactivity");
      enter_sleep_mode();
    }
  }
}

// ================ ERROR HANDLING ================

void handle_critical_error(const char* error_message) {
  DEBUG_PRINTF("🚨 CRITICAL ERROR: %s\n", error_message);
  
  // Stop all activities
  recording_active = false;
  streaming_active = false;
  
  // Set error LED
  set_status_led(false, false, false, true);
  
  // Try to notify server if possible
  if (is_websocket_ready()) {
    StaticJsonDocument<256> doc;
    doc["type"] = "error";
    doc["device_id"] = device_id;
    doc["error"] = error_message;
    doc["timestamp"] = millis();
    
    String message;
    serializeJson(doc, message);
    webSocket.sendTXT(message);
  }
  
  // Enter error state and attempt recovery
  delay(5000);
  ESP.restart();
}

// ================ CONFIGURATION AND UTILITIES ================

void enter_configuration_mode() {
  DEBUG_PRINTLN("⚙️ Entering configuration mode...");
  DEBUG_PRINTLN("💡 Please configure WiFi settings via serial monitor");
  
  // Implementation for WiFi configuration
  // This could be expanded to include AP mode, web interface, etc.
}

String generate_unique_device_id() {
  uint64_t mac = ESP.getEfuseMac();
  return "teddy_" + String((uint32_t)(mac >> 32), HEX) + String((uint32_t)mac, HEX);
}

void enter_sleep_mode() {
  // Save current state
  preferences.putInt("last_status", system_status);
  
  // Configure wake up source (button press)
  esp_sleep_enable_ext0_wakeup(GPIO_NUM_12, 0); // BUTTON_TALK
  
  // Enter deep sleep
  esp_deep_sleep_start();
}

void perform_system_health_check() {
  DEBUG_PRINTLN("🔍 Performing system health check...");
  
  bool health_ok = true;
  
  // Check WiFi
  if (WiFi.status() != WL_CONNECTED) {
    DEBUG_PRINTLN("❌ Health check: WiFi not connected");
    health_ok = false;
  }
  
  // Check audio buffers
  if (!i2s_read_buffer || !stream_buffer) {
    DEBUG_PRINTLN("❌ Health check: Audio buffers not allocated");
    health_ok = false;
  }
  
  // Check WebSocket
  if (!is_websocket_ready()) {
    DEBUG_PRINTLN("⚠️ Health check: WebSocket not ready (will retry)");
  }
  
  if (health_ok) {
    DEBUG_PRINTLN("✅ System health check passed");
  } else {
    DEBUG_PRINTLN("❌ System health check failed");
    handle_critical_error("System health check failed");
  }
}

// ================ EXTERNAL INTERFACE FUNCTIONS ================

void display_text_response(String text) {
  DEBUG_PRINTF("📱 Display response: %s\n", text.c_str());
  // Implementation for displaying text (LED patterns, etc.)
}

void play_received_audio(uint8_t* audio_data, size_t length) {
  DEBUG_PRINTF("🔊 Playing received audio: %d bytes\n", length);
  // Implementation for playing TTS audio through speaker
  // This would require additional I2S configuration for output
} 