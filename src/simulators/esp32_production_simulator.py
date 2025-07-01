from typing import Any, Dict, List, Optional, Union

"""
🧸 ESP32 Production Simulator - Enterprise Grade
Modern UI using PySide6/PyQt6 with proper async handling
"""

import asyncio
import base64
import json
import logging
import sys
from dataclasses import dataclass
from datetime import datetime

try:
    from PySide6 import QtCore, QtGui, QtWidgets
    from PySide6.QtCore import QPropertyAnimation, QThread, QTimer, Signal, Slot
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QTextEdit, QLabel, QGroupBox, QStatusBar,
        QProgressBar, QMessageBox, QInputDialog, QSplitter
    )
    from PySide6.QtGui import QColor, QFont, QIcon, QPalette
except Exception as e:
    logger.error(f"Error: {e}")"❌ PySide6 not installed. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PySide6"])
    from PySide6.QtCore import Signal, Slot, QThread, QTimer, QPropertyAnimation
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
        QPushButton, QLabel, QTextEdit, QProgressBar, QGroupBox, QSlider,
        QSpinBox, QCheckBox, QTabWidget, QGridLayout, QSplitter, QFrame
    )

import numpy as np
import sounddevice as sd

logger = logging.getLogger(__name__)

# ================== DATA MODELS ==================

@dataclass
class SimulatorConfig:
    """Simulator configuration"""
    api_url: str = "http://localhost:8000"
    ws_url: str = "ws://localhost:8000/ws"
    device_id: str = "ESP32_DEMO_001"
    firmware_version: str = "3.0.0"
    sample_rate: int = 16000
    chunk_size: int = 1024
    audio_channels: int = 1

@dataclass
class DeviceState:
    """Device state information"""
    connected: bool = False
    registered: bool = False
    child_name: Optional[str] = None
    child_age: Optional[int] = None
    is_recording: bool = False
    is_playing: bool = False
    volume: int = 50
    battery_level: int = 85

# ================== ASYNC WORKER THREAD ==================

class AsyncWorker(QThread):
    """Worker thread for async operations"""
    
    # Signals
    message_received = Signal(dict)
    error_occurred = Signal(str)
    status_updated = Signal(str)
    
    def __init__(self, config: SimulatorConfig):
        super().__init__()
        self.config = config
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.session: Optional[aiohttp.ClientSession] = None
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.running = False
        
    def run(self) -> Any:
        """Run async event loop in thread"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        try:
            self.loop.run_until_complete(self._run_async())
        except Exception as e:
            logger.error(f"AsyncWorker error: {str(e)}")
            self.error_occurred.emit(str(e))
        finally:
            self.loop.close()
    
    async def _run_async(self):
        """Main async loop"""
        self.running = True
        
        # Create session
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(timeout=timeout)
        
        try:
            while self.running:
                await asyncio.sleep(0.1)
        finally:
            await self.session.close()
    
    async def connect_websocket(self) -> bool:
        """Connect to WebSocket"""
        try:
            ws_url = f"{self.config.ws_url}/{self.config.device_id}"
            self.websocket = await websockets.connect(ws_url)
            self.status_updated.emit("WebSocket connected")
            
            # Start listening
            asyncio.create_task(self._listen_websocket())
            return True
            
        except Exception as e:
            self.error_occurred.emit(f"WebSocket connection failed: {str(e)}")
            return False
    
    async def _listen_websocket(self):
        """Listen for WebSocket messages"""
        try:
            while self.websocket and not self.websocket.closed:
                message = await self.websocket.recv()
                data = json.loads(message)
                self.message_received.emit(data)
                
        except websockets.exceptions.ConnectionClosed:
            self.status_updated.emit("WebSocket disconnected")
        except Exception as e:
            self.error_occurred.emit(f"WebSocket error: {str(e)}")
    
    async def send_api_request(self, endpoint: str, method: str, data: Dict = None) -> Dict:
        """Send API request"""
        url = f"{self.config.api_url}{endpoint}"
        
        try:
            async with self.session.request(method, url, json=data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"API error {response.status}: {error_text}")
                    
        except Exception as e:
            self.error_occurred.emit(f"API request failed: {str(e)}")
            raise
    
    def _schedule_coroutine(self, coro) -> Any:
        """Schedule coroutine in worker loop"""
        if self.loop and self.running:
            asyncio.run_coroutine_threadsafe(coro, self.loop)
    
    def _stop(self) -> Any:
        """Stop worker thread"""
        self.running = False
        if self.websocket:
            asyncio.run_coroutine_threadsafe(self.websocket.close(), self.loop)

# ================== AUDIO HANDLER ==================

class AudioHandler(QThread):
    """Handle audio recording and playback"""
    
    # Signals
    audio_level = Signal(float)
    audio_recorded = Signal(bytes)
    error = Signal(str)
    
    def __init__(self, config: SimulatorConfig):
        super().__init__()
        self.config = config
        self.is_recording = False
        self.audio_buffer = []
        
    def start_recording(self) -> Any:
        """Start audio recording"""
        self.is_recording = True
        self.audio_buffer = []
        self.start()
    
    def stop_recording(self) -> bytes:
        """Stop recording and return audio data"""
        self.is_recording = False
        self.wait()
        
        # Convert buffer to WAV
        if self.audio_buffer:
            audio_data = np.concatenate(self.audio_buffer)
            return self._numpy_to_wav(audio_data)
        return b''
    
    def _run(self) -> Any:
        """Recording thread"""
        try:
            with sd.InputStream(
                samplerate=self.config.sample_rate,
                channels=self.config.audio_channels,
                callback=self._audio_callback,
                blocksize=self.config.chunk_size
            ):
                while self.is_recording:
                    self.msleep(100)
                    
        except Exception as e:
            self.error.emit(f"Recording error: {str(e)}")
    
    def _audio_callback(self, indata, frames, time, status) -> Any:
        """Audio stream callback"""
        if status:
            logger.warning(f"Audio status: {status}")
        
        if self.is_recording:
            self.audio_buffer.append(indata.copy())
            
            # Calculate and emit audio level
            level = np.abs(indata).mean()
            self.audio_level.emit(float(level))
    
    def _numpy_to_wav(self, audio_data: np.ndarray) -> bytes:
        """Convert numpy array to WAV bytes"""
        import io
        import wave
        
        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wav_file:
            wav_file.setnchannels(self.config.audio_channels)
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(self.config.sample_rate)
            
            # Convert float32 to int16
            audio_int16 = (audio_data * 32767).astype(np.int16)
            wav_file.writeframes(audio_int16.tobytes())
        
        return buffer.getvalue()
    
    def _play_audio(bytes) -> None:
        """Play audio data"""
        try:
            # Decode base64 if needed
            if isinstance(audio_data, str):
                audio_data = base64.b64decode(audio_data)
            
            # Play using sounddevice
            # This is simplified - in production, use proper audio decoding
            sd.play(audio_data, self.config.sample_rate)
            
        except Exception as e:
            self.error.emit(f"Playback error: {str(e)}")

# ================== MODERN UI COMPONENTS ==================

class ModernButton(QPushButton):
    """Modern styled button with animations"""
    
    def __init__(self, text: str, primary: bool = False):
        super().__init__(text)
        self.primary = primary
        self._setup_style()
        self._setup_animation()
    
    def _setup_style(self) -> Any:
        """Setup modern button style"""
        base_style = """
            QPushButton {
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 600;
                color: white;
                background-color: %s;
            }
            QPushButton:hover {
                background-color: %s;
            }
            QPushButton:pressed {
                background-color: %s;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """
        
        if self.primary:
            colors = ("#2196F3", "#1976D2", "#0D47A1")  # Blue
        else:
            colors = ("#757575", "#616161", "#424242")  # Gray
        
        self.setStyleSheet(base_style % colors)
    
    def _setup_animation(self) -> Any:
        """Setup hover animation"""
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(100)

class ConsoleWidget(QTextEdit):
    """Modern console with syntax highlighting"""
    
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #3c3c3c;
                border-radius: 8px;
                padding: 12px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 13px;
            }
        """)
    
    def _log(str = "info") -> None:
        """Add log message with color coding"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        colors = {
            "info": "#58a6ff",
            "success": "#56d364",
            "warning": "#f0883e",
            "error": "#f85149"
        }
        
        color = colors.get(level, "#d4d4d4")
        
        html = f'<span style="color: #8b949e">[{timestamp}]</span> '
        html += f'<span style="color: {color}">{message}</span>'
        
        self.append(html)
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

# ================== MAIN SIMULATOR WINDOW ==================

class ESP32ProductionSimulator(QMainWindow):
    """Modern ESP32 Simulator with PySide6"""
    
    def __init__(self):
        super().__init__()
        self.config = SimulatorConfig()
        self.state = DeviceState()
        self.async_worker = AsyncWorker(self.config)
        self.audio_handler = AudioHandler(self.config)
        
        self._setup_ui()
        self._setup_connections()
        self._apply_theme()
        
        # Start async worker
        self.async_worker.start()
        
    def _setup_ui(self) -> Any:
        """Setup modern UI"""
        self.setWindowTitle("🧸 AI Teddy Bear - ESP32 Simulator")
        self.setMinimumSize(1200, 800)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        # Main layout
        layout = QVBoxLayout(central)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = self._create_header()
        layout.addWidget(header)
        
        # Main content (splitter)
        splitter = QSplitter(QtCore.Qt.Horizontal)
        
        # Left panel - Controls
        left_panel = self._create_control_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Console
        right_panel = self._create_console_panel()
        splitter.addWidget(right_panel)
        
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        layout.addWidget(splitter)
        
        # Status bar
        self._create_status_bar()
    
    def _create_header(self) -> QWidget:
        """Create header with device info"""
        header = QGroupBox("Device Information")
        header.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #424242;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px 0 8px;
            }
        """)
        
        layout = QHBoxLayout()
        
        # Device ID
        self.device_label = QLabel(f"Device: {self.config.device_id}")
        self.device_label.setStyleSheet("font-size: 14px; color: #58a6ff;")
        layout.addWidget(self.device_label)
        
        # Connection status
        self.connection_status = QLabel("● Disconnected")
        self.connection_status.setStyleSheet("font-size: 14px; color: #f85149;")
        layout.addWidget(self.connection_status)
        
        layout.addStretch()
        
        # Battery level
        self.battery_label = QLabel(f"🔋 {self.state.battery_level}%")
        self.battery_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.battery_label)
        
        header.setLayout(layout)
        return header
    
    def _create_control_panel(self) -> QWidget:
        """Create control panel"""
        panel = QGroupBox("Controls")
        layout = QVBoxLayout()
        layout.setSpacing(12)
        
        # Connect button
        self.connect_btn = ModernButton("Connect to Server", primary=True)
        self.connect_btn.clicked.connect(self.connect_to_server)
        layout.addWidget(self.connect_btn)
        
        # Child setup
        child_group = QGroupBox("Child Profile")
        child_layout = QVBoxLayout()
        
        self.setup_child_btn = ModernButton("Setup Child Profile")
        self.setup_child_btn.clicked.connect(self.setup_child_profile)
        child_layout.addWidget(self.setup_child_btn)
        
        self.child_info_label = QLabel("No profile configured")
        self.child_info_label.setStyleSheet("color: #8b949e; padding: 8px;")
        child_layout.addWidget(self.child_info_label)
        
        child_group.setLayout(child_layout)
        layout.addWidget(child_group)
        
        # Voice interaction
        voice_group = QGroupBox("Voice Interaction")
        voice_layout = QVBoxLayout()
        
        self.record_btn = ModernButton("🎤 Hold to Talk", primary=True)
        self.record_btn.setEnabled(False)
        self.record_btn.pressed.connect(self.start_recording)
        self.record_btn.released.connect(self.stop_recording)
        voice_layout.addWidget(self.record_btn)
        
        # Audio level indicator
        self.audio_level_bar = QProgressBar()
        self.audio_level_bar.setRange(0, 100)
        self.audio_level_bar.setTextVisible(False)
        self.audio_level_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                background-color: #1e1e1e;
                height: 8px;
            }
            QProgressBar::chunk {
                background-color: #56d364;
                border-radius: 3px;
            }
        """)
        voice_layout.addWidget(self.audio_level_bar)
        
        voice_group.setLayout(voice_layout)
        layout.addWidget(voice_group)
        
        # Demo controls
        demo_group = QGroupBox("Demo Features")
        demo_layout = QVBoxLayout()
        
        self.auto_demo_btn = ModernButton("Run Auto Demo")
        self.auto_demo_btn.clicked.connect(self.run_auto_demo)
        demo_layout.addWidget(self.auto_demo_btn)
        
        demo_group.setLayout(demo_layout)
        layout.addWidget(demo_group)
        
        layout.addStretch()
        
        panel.setLayout(layout)
        return panel
    
    def _create_console_panel(self) -> QWidget:
        """Create console panel"""
        panel = QGroupBox("System Console")
        layout = QVBoxLayout()
        
        # Console output
        self.console = ConsoleWidget()
        layout.addWidget(self.console)
        
        # Input area
        input_layout = QHBoxLayout()
        
        self.message_input = QtWidgets.QLineEdit()
        self.message_input.setPlaceholderText("Type a message...")
        self.message_input.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                border: 1px solid #3c3c3c;
                border-radius: 6px;
                padding: 8px;
                font-size: 14px;
                color: #d4d4d4;
            }
        """)
        self.message_input.returnPressed.connect(self.send_text_message)
        input_layout.addWidget(self.message_input)
        
        self.send_btn = ModernButton("Send")
        self.send_btn.clicked.connect(self.send_text_message)
        self.send_btn.setEnabled(False)
        input_layout.addWidget(self.send_btn)
        
        layout.addLayout(input_layout)
        
        panel.setLayout(layout)
        return panel
    
    def _create_status_bar(self) -> Any:
        """Create status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Permanent widgets
        self.api_status = QLabel("API: Disconnected")
        self.ws_status = QLabel("WebSocket: Disconnected")
        
        self.status_bar.addPermanentWidget(self.api_status)
        self.status_bar.addPermanentWidget(self.ws_status)
    
    def _setup_connections(self) -> Any:
        """Setup signal connections"""
        # Async worker signals
        self.async_worker.message_received.connect(self.handle_ws_message)
        self.async_worker.error_occurred.connect(self.handle_error)
        self.async_worker.status_updated.connect(self.update_status)
        
        # Audio handler signals
        self.audio_handler.audio_level.connect(self.update_audio_level)
        self.audio_handler.error.connect(self.handle_error)
    
    def _apply_theme(self) -> Any:
        """Apply dark theme"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0d1117;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #30363d;
                border-radius: 8px;
                margin-top: 8px;
                padding-top: 8px;
                background-color: #161b22;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px 0 8px;
            }
            QLabel {
                color: #c9d1d9;
            }
        """)
    
    # ================== SLOTS ==================
    
    @Slot()
    def _connect_to_server(self) -> Any:
        """Connect to server"""
        self.console.log("Connecting to server...", "info")
        
        async def connect():
            try:
                # Register device
                response = await self.async_worker.send_api_request(
                    "/api/v1/devices/register",
                    "POST",
                    {
                        "device_id": self.config.device_id,
                        "firmware_version": self.config.firmware_version,
                        "hardware_info": {
                            "type": "ESP32",
                            "simulator": True
                        }
                    }
                )
                
                self.state.registered = True
                self.console.log("Device registered successfully", "success")
                
                # Connect WebSocket
                if await self.async_worker.connect_websocket():
                    self.state.connected = True
                    self.update_connection_status(True)
                    self.console.log("Connected to server", "success")
                    
                    # Enable controls
                    self.record_btn.setEnabled(True)
                    self.send_btn.setEnabled(True)
                
            except Exception as e:
                self.console.log(f"Connection failed: {str(e)}", "error")
        
        self.async_worker.schedule_coroutine(connect())
    
    @Slot()
    def setup_child_profile(self) -> Any:
        """Setup child profile"""
        name, ok = QInputDialog.getText(self, "Child Profile", "Enter child's name:")
        if not ok or not name:
            return
        
        age, ok = QInputDialog.getInt(self, "Child Profile", "Enter child's age:", 5, 2, 14)
        if not ok:
            return
        
        async def create_profile():
            try:
                response = await self.async_worker.send_api_request(
                    "/api/v1/children",
                    "POST",
                    {
                        "name": name,
                        "age": age,
                        "device_id": self.config.device_id,
                        "language": "Arabic"
                    }
                )
                
                self.state.child_name = name
                self.state.child_age = age
                
                self.child_info_label.setText(f"👦 {name}, {age} years old")
                self.console.log(f"Child profile created: {name}, {age} years", "success")
                
            except Exception as e:
                self.console.log(f"Profile creation failed: {str(e)}", "error")
        
        self.async_worker.schedule_coroutine(create_profile())
    
    @Slot()
    def _start_recording(self) -> Any:
        """Start voice recording"""
        self.console.log("🎤 Recording started...", "info")
        self.state.is_recording = True
        self.audio_handler.start_recording()
    
    @Slot()
    def _stop_recording(self) -> Any:
        """Stop recording and send audio"""
        if not self.state.is_recording:
            return
        
        self.state.is_recording = False
        audio_data = self.audio_handler.stop_recording()
        
        if audio_data:
            self.console.log("🎤 Recording stopped, sending to server...", "info")
            self.send_audio_data(audio_data)
        else:
            self.console.log("No audio recorded", "warning")
    
    def _send_audio_data(bytes) -> None:
        """Send audio data to server"""
        async def send():
            try:
                # Convert to base64
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                
                response = await self.async_worker.send_api_request(
                    "/api/v1/audio/process",
                    "POST",
                    {
                        "audio": audio_base64,
                        "device_id": self.config.device_id
                    }
                )
                
                # Display response
                self.console.log(f"🤖 AI: {response['text']}", "success")
                
                # Play response audio if available
                if 'metadata' in response and 'audio_response' in response['metadata']:
                    self.audio_handler.play_audio(response['metadata']['audio_response'])
                
            except Exception as e:
                self.console.log(f"Failed to process audio: {str(e)}", "error")
        
        self.async_worker.schedule_coroutine(send())
    
    @Slot()
    def _send_text_message(self) -> Any:
        """Send text message"""
        message = self.message_input.text().strip()
        if not message:
            return
        
        self.message_input.clear()
        self.console.log(f"👤 You: {message}", "info")
        
        # For text demo - convert to audio simulation
        self.console.log("Converting text to speech simulation...", "info")
        # In production, this would use actual TTS
    
    @Slot(dict)
    def _handle_ws_message(dict) -> None:
        """Handle WebSocket message"""
        msg_type = data.get("type", "unknown")
        
        if msg_type == "ai_response":
            response = data.get("data", {})
            self.console.log(f"🤖 AI: {response.get('text', '')}", "success")
        else:
            self.console.log(f"WebSocket message: {json.dumps(data)}", "info")
    
    @Slot(str)
    def _handle_error(str) -> None:
        """Handle error messages"""
        self.console.log(error, "error")
    
    @Slot(str)
    def _update_status(str) -> None:
        """Update status message"""
        self.status_bar.showMessage(status, 3000)
    
    @Slot(float)
    def _update_audio_level(float) -> None:
        """Update audio level indicator"""
        self.audio_level_bar.setValue(int(level * 100))
    
    def _update_connection_status(bool) -> None:
        """Update connection status display"""
        if connected:
            self.connection_status.setText("● Connected")
            self.connection_status.setStyleSheet("font-size: 14px; color: #56d364;")
            self.api_status.setText("API: Connected")
            self.ws_status.setText("WebSocket: Connected")
        else:
            self.connection_status.setText("● Disconnected")
            self.connection_status.setStyleSheet("font-size: 14px; color: #f85149;")
            self.api_status.setText("API: Disconnected")
            self.ws_status.setText("WebSocket: Disconnected")
    
    @Slot()
    def _run_auto_demo(self) -> Any:
        """Run automated demo"""
        self.console.log("Starting automated demo...", "info")
        
        demo_messages = [
            "مرحباً دبدوب",
            "كيف حالك اليوم؟",
            "هل يمكنك أن تحكي لي قصة؟",
            "أريد أن ألعب معك",
            "ما هو لونك المفضل؟"
        ]
        
        # Simulate sending messages
        for i, msg in enumerate(demo_messages):
            QTimer.singleShot(i * 5000, lambda m=msg: self.console.log(f"👤 Demo: {m}", "info"))
    
    def _closeEvent(self, event) -> Any:
        """Handle window close"""
        self.async_worker.stop()
        self.async_worker.wait()
        event.accept()

# ================== MAIN ENTRY POINT ==================

def main() -> Any:
    """Main entry point"""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("ESP32 Teddy Bear Simulator")
    app.setOrganizationName("AI Teddy Bear Corp")
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create and show simulator
    simulator = ESP32ProductionSimulator()
    simulator.show()
    
    # Run application
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 