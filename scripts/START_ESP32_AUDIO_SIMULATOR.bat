@echo off
color 0A
title 🧸 ESP32 Audio Streaming Simulator - Task 5

echo.
echo ========================================================
echo 🧸 AI Teddy Bear - ESP32 Audio Streaming Simulator
echo ========================================================
echo.
echo 🎯 Task 5: Real-time Microphone Capture + WebSocket Streaming
echo.
echo 📡 Starting ESP32 Audio Streaming Simulator...
echo.

:: Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.8+
    echo 💡 Download from: https://python.org/downloads/
    pause
    exit /b 1
)

:: Check if required modules are installed
echo 🔍 Checking Python dependencies...
python -c "import websockets, asyncio, json" >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Installing required Python modules...
    pip install websockets asyncio
)

:: Create ESP32 simulator if it doesn't exist
if not exist "esp32_audio_simulator.py" (
    echo 📝 Creating ESP32 Audio Simulator...
    
    (
        echo # 🧸 ESP32 Audio Streaming Simulator
        echo import asyncio
        echo import websockets
        echo import json
        echo import time
        echo import random
        echo import struct
        echo.
        echo class ESP32AudioSimulator:
        echo     def __init__(self^):
        echo         self.device_id = "esp32_simulator_001"
        echo         self.session_id = None
        echo         self.connected = False
        echo         self.recording = False
        echo.
        echo     async def connect_websocket(self^):
        echo         uri = "ws://localhost:8000/ws/" + self.device_id
        echo         print(f"🔗 Connecting to {uri}..."^)
        echo.
        echo         try:
        echo             async with websockets.connect(uri^) as websocket:
        echo                 self.connected = True
        echo                 print("✅ WebSocket Connected!"^)
        echo.
        echo                 # Send metadata
        echo                 await self.send_metadata(websocket^)
        echo.
        echo                 # Handle messages
        echo                 await self.handle_connection(websocket^)
        echo.
        echo         except Exception as e:
        echo             print(f"❌ Connection failed: {e}"^)
        echo             print("💡 Make sure the server is running on localhost:8000"^)
        echo.
        echo     async def send_metadata(self, websocket^):
        echo         metadata = {
        echo             "type": "metadata",
        echo             "device_id": self.device_id,
        echo             "timestamp": int(time.time(^) * 1000^),
        echo             "sample_rate": 16000,
        echo             "channels": 1,
        echo             "bits_per_sample": 16,
        echo             "capabilities": {
        echo                 "audio_streaming": True,
        echo                 "noise_gate": True,
        echo                 "psram": True
        echo             }
        echo         }
        echo.
        echo         await websocket.send(json.dumps(metadata^)^)
        echo         print("📤 Metadata sent"^)
        echo.
        echo     async def handle_connection(self, websocket^):
        echo         try:
        echo             while True:
        echo                 # Simulate user input
        echo                 print("\n🎤 Press Enter to start recording (or 'q' to quit^)..."^)
        echo                 user_input = input(^)
        echo.
        echo                 if user_input.lower(^) == 'q':
        echo                     break
        echo.
        echo                 # Start recording simulation
        echo                 await self.simulate_recording(websocket^)
        echo.
        echo         except websockets.exceptions.ConnectionClosed:
        echo             print("🔌 Connection closed"^)
        echo         except KeyboardInterrupt:
        echo             print("\n👋 Shutting down simulator..."^)
        echo.
        echo     async def simulate_recording(self, websocket^):
        echo         print("🎤 Simulating audio recording..."^)
        echo.
        echo         # Send audio start notification
        echo         start_msg = {
        echo             "type": "audio_start",
        echo             "device_id": self.device_id,
        echo             "timestamp": int(time.time(^) * 1000^)
        echo         }
        echo         await websocket.send(json.dumps(start_msg^)^)
        echo.
        echo         # Simulate 3 seconds of audio data
        echo         for i in range(30^):  # 30 chunks of 100ms each
        echo             # Generate fake audio data (1024 samples of int16^)
        echo             audio_samples = []
        echo             for _ in range(1024^):
        echo                 # Simulate speech-like waveform
        echo                 sample = int(random.gauss(0, 1000^)^)
        echo                 sample = max(-32768, min(32767, sample^)^)
        echo                 audio_samples.append(sample^)
        echo.
        echo             # Pack as binary data
        echo             audio_data = struct.pack('1024h', *audio_samples^)
        echo             await websocket.send(audio_data^)
        echo.
        echo             print(f"📡 Sent audio chunk {i+1}/30"^)
        echo             await asyncio.sleep(0.1^)  # 100ms intervals
        echo.
        echo         # Send audio end notification
        echo         end_msg = {
        echo             "type": "audio_end",
        echo             "device_id": self.device_id,
        echo             "timestamp": int(time.time(^) * 1000^)
        echo         }
        echo         await websocket.send(json.dumps(end_msg^)^)
        echo         print("✅ Audio recording simulation complete!"^)
        echo.
        echo if __name__ == "__main__":
        echo     print("🧸 ESP32 Audio Streaming Simulator v1.0"^)
        echo     print("========================================"^)
        echo.
        echo     simulator = ESP32AudioSimulator(^)
        echo     asyncio.run(simulator.connect_websocket(^)^)
    ) > esp32_audio_simulator.py
)

echo ✅ ESP32 Audio Simulator ready!
echo.
echo 📋 Simulator Features:
echo    ✅ WebSocket connection to /ws/device_id
echo    ✅ Metadata exchange (device capabilities)
echo    ✅ Simulated I2S audio data streaming
echo    ✅ Audio start/end notifications
echo    ✅ Real-time binary data transmission
echo.
echo 🎯 Usage Instructions:
echo    1. Make sure your backend server is running on localhost:8000
echo    2. The simulator will connect to /ws/esp32_simulator_001
echo    3. Press Enter to simulate audio recording
echo    4. Type 'q' to quit the simulator
echo.
echo 🚀 Starting simulator...
echo.

python esp32_audio_simulator.py

echo.
echo 👋 ESP32 Audio Simulator finished.
pause 