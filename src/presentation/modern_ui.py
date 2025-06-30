"""
Modern PySide6 UI for AI Teddy Bear - Enterprise Grade 2025
Replaces deprecated tkinter with modern, responsive interface
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from typing import Dict, Optional, Any, List
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QPushButton, QLabel, QTextEdit, QLineEdit, QComboBox,
    QProgressBar, QSplitter, QGroupBox, QGridLayout, QListWidget,
    QStatusBar, QMenuBar, QAction, QDialog, QMessageBox, QSystemTrayIcon,
    QStyle, QTableWidget, QTableWidgetItem, QHeaderView, QSpacerItem,
    QSizePolicy, QFrame, QScrollArea, QSlider, QCheckBox, QSpinBox
)
from PySide6.QtCore import (
    Qt, QTimer, QThread, Signal, QObject, QPropertyAnimation, QEasingCurve,
    QRect, QUrl, QSettings, QSize, QPoint, QDateTime, QRunnable, QThreadPool
)
from PySide6.QtGui import (
    QFont, QPixmap, QIcon, QPalette, QColor, QLinearGradient, QGradient,
    QPainter, QBrush, QPen, QAction as QGuiAction, QDesktopServices,
    QMovie, QTextCursor, QSyntaxHighlighter, QTextCharFormat
)
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QDateTimeAxis, QValueAxis
from PySide6.QtWebSockets import QWebSocket
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

# Audio processing imports
try:
    import sounddevice as sd
    import numpy as np
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    SOUNDDEVICE_AVAILABLE = False
    print("⚠️ sounddevice not available. Install with: pip install sounddevice")

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    print("⚠️ PyAudio not available. Install with: pip install pyaudio")

# Advanced audio processing imports
try:
    import librosa
    import librosa.display
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    print("⚠️ librosa not available. Install with: pip install librosa")

try:
    import noisereduce as nr
    NOISEREDUCE_AVAILABLE = True
except ImportError:
    NOISEREDUCE_AVAILABLE = False
    print("⚠️ noisereduce not available. Install with: pip install noisereduce")

try:
    from scipy import signal
    from scipy.signal import butter, filtfilt
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    print("⚠️ scipy not available. Install with: pip install scipy")

import tempfile
import base64
import wave
import io
import time
import platform
import psutil

import structlog

logger = structlog.get_logger()


class AudioProcessingEngine:
    """Professional audio processing engine with noise reduction and voice enhancement"""
    
    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        self.performance_mode = self._detect_system_performance()
        self.processing_stats = {}
        
        logger.info("Audio processing engine initialized", 
                   performance_mode=self.performance_mode,
                   librosa_available=LIBROSA_AVAILABLE,
                   noisereduce_available=NOISEREDUCE_AVAILABLE,
                   scipy_available=SCIPY_AVAILABLE)
    
    def _detect_system_performance(self) -> str:
        """Detect system performance level for optimization"""
        try:
            # Check CPU cores and memory
            cpu_count = psutil.cpu_count()
            memory_gb = psutil.virtual_memory().total / (1024**3)
            
            # Simple performance classification
            if cpu_count >= 8 and memory_gb >= 16:
                return "high"
            elif cpu_count >= 4 and memory_gb >= 8:
                return "medium"
            else:
                return "low"
                
        except Exception:
            logger.warning("Could not detect system performance, using medium mode")
            return "medium"
    
    def process_audio(self, audio_data: np.ndarray, processing_level: str = "auto") -> tuple:
        """
        Process audio with comprehensive enhancement
        
        Args:
            audio_data: Input audio as numpy array
            processing_level: "low", "medium", "high", or "auto"
            
        Returns:
            tuple: (processed_audio, processing_info)
        """
        start_time = time.time()
        
        if processing_level == "auto":
            processing_level = self.performance_mode
        
        processing_info = {
            "original_length": len(audio_data),
            "sample_rate": self.sample_rate,
            "processing_level": processing_level,
            "steps_applied": []
        }
        
        try:
            # Step 1: Normalize input
            processed_audio = self._normalize_audio(audio_data)
            processing_info["steps_applied"].append("normalization")
            
            # Step 2: Noise reduction (if available and needed)
            if processing_level in ["medium", "high"] and NOISEREDUCE_AVAILABLE:
                processed_audio = self._reduce_noise(processed_audio, processing_level)
                processing_info["steps_applied"].append("noise_reduction")
            
            # Step 3: Voice enhancement
            if processing_level in ["medium", "high"] and SCIPY_AVAILABLE:
                processed_audio = self._enhance_voice(processed_audio, processing_level)
                processing_info["steps_applied"].append("voice_enhancement")
            
            # Step 4: Advanced processing (high performance only)
            if processing_level == "high" and LIBROSA_AVAILABLE:
                processed_audio = self._advanced_processing(processed_audio)
                processing_info["steps_applied"].append("advanced_processing")
            
            # Step 5: Final normalization and clipping prevention
            processed_audio = self._final_normalization(processed_audio)
            processing_info["steps_applied"].append("final_normalization")
            
            # Calculate processing stats
            processing_time = time.time() - start_time
            processing_info.update({
                "processing_time": processing_time,
                "final_length": len(processed_audio),
                "quality_improvement": self._calculate_quality_improvement(audio_data, processed_audio)
            })
            
            logger.info("Audio processing completed", **processing_info)
            
            return processed_audio, processing_info
            
        except Exception as e:
            logger.error("Audio processing failed", error=str(e))
            # Return original audio if processing fails
            processing_info["error"] = str(e)
            return audio_data, processing_info
    
    def _normalize_audio(self, audio: np.ndarray) -> np.ndarray:
        """Basic audio normalization"""
        if np.max(np.abs(audio)) > 0:
            return audio / np.max(np.abs(audio)) * 0.8  # Prevent clipping
        return audio
    
    def _reduce_noise(self, audio: np.ndarray, level: str) -> np.ndarray:
        """Advanced noise reduction using noisereduce"""
        try:
            if level == "medium":
                # Medium quality, faster processing
                reduced_audio = nr.reduce_noise(
                    y=audio, 
                    sr=self.sample_rate,
                    prop_decrease=0.6,
                    stationary=True
                )
            else:  # high
                # High quality, more thorough processing
                reduced_audio = nr.reduce_noise(
                    y=audio, 
                    sr=self.sample_rate,
                    prop_decrease=0.8,
                    stationary=False,
                    use_torch=False  # CPU optimization
                )
            
            return reduced_audio
            
        except Exception as e:
            logger.warning("Noise reduction failed, using original", error=str(e))
            return audio
    
    def _enhance_voice(self, audio: np.ndarray, level: str) -> np.ndarray:
        """Voice enhancement using frequency filtering"""
        try:
            # Human voice frequency range enhancement (80 Hz - 8000 Hz)
            nyquist = self.sample_rate / 2
            
            if level == "medium":
                # Simple bandpass filter
                low_cutoff = 80 / nyquist
                high_cutoff = 4000 / nyquist
                b, a = butter(4, [low_cutoff, high_cutoff], btype='band')
                
            else:  # high
                # More sophisticated filtering
                low_cutoff = 60 / nyquist
                high_cutoff = 6000 / nyquist
                b, a = butter(6, [low_cutoff, high_cutoff], btype='band')
            
            # Apply filter
            filtered_audio = filtfilt(b, a, audio)
            
            # Enhance speech frequencies (1000-3000 Hz)
            speech_low = 1000 / nyquist
            speech_high = 3000 / nyquist
            b_speech, a_speech = butter(2, [speech_low, speech_high], btype='band')
            speech_enhanced = filtfilt(b_speech, a_speech, audio)
            
            # Combine filtered audio with enhanced speech (subtle boost)
            enhanced_audio = filtered_audio + (speech_enhanced * 0.3)
            
            return enhanced_audio
            
        except Exception as e:
            logger.warning("Voice enhancement failed, using original", error=str(e))
            return audio
    
    def _advanced_processing(self, audio: np.ndarray) -> np.ndarray:
        """Advanced processing using librosa"""
        try:
            # Harmonic-percussive separation to isolate voice
            harmonic, percussive = librosa.effects.hpss(audio)
            
            # Focus on harmonic content (voice)
            processed_audio = harmonic + (percussive * 0.1)
            
            # Spectral centroid enhancement for clarity
            spectral_centroids = librosa.feature.spectral_centroid(y=processed_audio, sr=self.sample_rate)
            
            # Apply dynamic range compression
            processed_audio = self._dynamic_range_compression(processed_audio)
            
            return processed_audio
            
        except Exception as e:
            logger.warning("Advanced processing failed, using original", error=str(e))
            return audio
    
    def _dynamic_range_compression(self, audio: np.ndarray, ratio: float = 4.0) -> np.ndarray:
        """Apply dynamic range compression"""
        try:
            # Simple compressor
            threshold = 0.1
            audio_abs = np.abs(audio)
            
            # Find samples above threshold
            above_threshold = audio_abs > threshold
            
            # Apply compression
            compressed = audio.copy()
            compressed[above_threshold] = np.sign(audio[above_threshold]) * (
                threshold + (audio_abs[above_threshold] - threshold) / ratio
            )
            
            return compressed
            
        except Exception as e:
            logger.warning("Dynamic range compression failed", error=str(e))
            return audio
    
    def _final_normalization(self, audio: np.ndarray) -> np.ndarray:
        """Final normalization with clipping prevention"""
        # RMS normalization for consistent volume
        rms = np.sqrt(np.mean(audio**2))
        if rms > 0:
            target_rms = 0.15  # Target RMS level
            audio = audio * (target_rms / rms)
        
        # Hard limiting to prevent clipping
        audio = np.clip(audio, -0.95, 0.95)
        
        return audio
    
    def _calculate_quality_improvement(self, original: np.ndarray, processed: np.ndarray) -> dict:
        """Calculate quality improvement metrics"""
        try:
            # SNR improvement estimation
            original_rms = np.sqrt(np.mean(original**2))
            processed_rms = np.sqrt(np.mean(processed**2))
            
            # Dynamic range
            original_dynamic_range = np.max(np.abs(original)) - np.min(np.abs(original))
            processed_dynamic_range = np.max(np.abs(processed)) - np.min(np.abs(processed))
            
            return {
                "rms_ratio": processed_rms / (original_rms + 1e-10),
                "dynamic_range_improvement": processed_dynamic_range / (original_dynamic_range + 1e-10),
                "peak_reduction": np.max(np.abs(original)) / (np.max(np.abs(processed)) + 1e-10)
            }
            
        except Exception:
            return {"error": "Could not calculate quality metrics"}
    
    def clean_audio(self, input_audio: np.ndarray, processing_level: str = "auto") -> tuple:
        """
        Main function for cleaning and enhancing audio
        Equivalent to the requested clean_audio function
        
        Args:
            input_audio: Input audio as numpy array
            processing_level: Processing intensity level
            
        Returns:
            tuple: (cleaned_audio, processing_info)
        """
        return self.process_audio(input_audio, processing_level)
    
    def get_processing_capabilities(self) -> dict:
        """Get available processing capabilities"""
        return {
            "performance_mode": self.performance_mode,
            "librosa_available": LIBROSA_AVAILABLE,
            "noisereduce_available": NOISEREDUCE_AVAILABLE,
            "scipy_available": SCIPY_AVAILABLE,
            "recommended_level": self.performance_mode,
            "max_processing_time": {
                "low": "< 1 second",
                "medium": "< 3 seconds", 
                "high": "< 10 seconds"
            }[self.performance_mode]
        }


class WebSocketClient(QObject):
    """Enterprise WebSocket client with auto-reconnection"""
    
    connected = Signal()
    disconnected = Signal()
    message_received = Signal(dict)
    error_occurred = Signal(str)
    connection_status_changed = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.websocket = QWebSocket()
        self.url = QUrl("ws://localhost:8000/ws/ui_session")
        self.reconnect_timer = QTimer()
        self.heartbeat_timer = QTimer()
        self.is_connected = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 10
        
        # Setup timers
        self.reconnect_timer.timeout.connect(self._attempt_reconnect)
        self.heartbeat_timer.timeout.connect(self._send_heartbeat)
        self.heartbeat_timer.start(30000)  # 30 seconds
        
        # Setup WebSocket signals
        self.websocket.connected.connect(self._on_connected)
        self.websocket.disconnected.connect(self._on_disconnected)
        self.websocket.textMessageReceived.connect(self._on_message_received)
        self.websocket.errorOccurred.connect(self._on_error)
    
    def connect_to_server(self):
        """Connect to WebSocket server"""
        logger.info("Attempting WebSocket connection", url=str(self.url))
        self.connection_status_changed.emit("Connecting...")
        self.websocket.open(self.url)
    
    def disconnect_from_server(self):
        """Disconnect from WebSocket server"""
        self.websocket.close()
        self.reconnect_timer.stop()
    
    def send_message(self, message: Dict[str, Any]):
        """Send message to server"""
        if self.is_connected:
            json_message = json.dumps(message)
            self.websocket.sendTextMessage(json_message)
            logger.debug("Sent WebSocket message", message_type=message.get("type"))
    
    def _on_connected(self):
        """Handle successful connection"""
        self.is_connected = True
        self.reconnect_attempts = 0
        self.reconnect_timer.stop()
        self.connection_status_changed.emit("Connected")
        self.connected.emit()
        logger.info("WebSocket connected successfully")
    
    def _on_disconnected(self):
        """Handle disconnection"""
        self.is_connected = False
        self.connection_status_changed.emit("Disconnected")
        self.disconnected.emit()
        logger.warning("WebSocket disconnected")
        
        if self.reconnect_attempts < self.max_reconnect_attempts:
            self.reconnect_timer.start(5000)  # Retry in 5 seconds
    
    def _on_message_received(self, message: str):
        """Handle received message"""
        try:
            data = json.loads(message)
            self.message_received.emit(data)
            logger.debug("Received WebSocket message", message_type=data.get("type"))
        except json.JSONDecodeError as e:
            logger.error("Failed to parse WebSocket message", error=str(e))
            self.error_occurred.emit(f"Invalid message format: {e}")
    
    def _on_error(self, error):
        """Handle WebSocket error"""
        error_msg = f"WebSocket error: {error}"
        logger.error(error_msg)
        self.error_occurred.emit(error_msg)
        self.connection_status_changed.emit("Error")
    
    def _attempt_reconnect(self):
        """Attempt to reconnect"""
        self.reconnect_attempts += 1
        if self.reconnect_attempts <= self.max_reconnect_attempts:
            logger.info("Attempting reconnection", attempt=self.reconnect_attempts)
            self.connect_to_server()
        else:
            self.reconnect_timer.stop()
            self.connection_status_changed.emit("Failed")
            logger.error("Max reconnection attempts reached")
    
    def _send_heartbeat(self):
        """Send heartbeat to keep connection alive"""
        if self.is_connected:
            self.send_message({"type": "ping", "timestamp": datetime.now().isoformat()})


class EnterpriseMessageSender(QObject):
    """Advanced message sender with retry logic and metadata support"""
    
    message_sent = Signal(str)  # message_id
    message_delivered = Signal(str, dict)  # message_id, response
    message_failed = Signal(str, str)  # message_id, error
    sending_progress = Signal(str, int)  # message_id, progress_percent
    connection_restored = Signal()
    
    def __init__(self, websocket_client: 'WebSocketClient', parent=None):
        super().__init__(parent)
        self.websocket_client = websocket_client
        self.pending_messages = {}  # message_id -> message_data
        self.retry_queue = []  # Failed messages for retry
        self.max_retry_attempts = 3
        self.retry_delay = 2.0  # seconds
        self.setup_retry_system()
        
    def setup_retry_system(self):
        """Setup automatic retry system"""
        self.retry_timer = QTimer()
        self.retry_timer.timeout.connect(self._process_retry_queue)
        self.retry_timer.start(5000)  # Check every 5 seconds
        
        # Monitor connection status
        self.websocket_client.connected.connect(self._on_connection_restored)
        self.websocket_client.message_received.connect(self._handle_server_response)
    
    async def send_audio_message(self, audio_file: bytes, metadata: dict) -> str:
        """
        Send audio message with comprehensive metadata
        
        Args:
            audio_file: Audio data in bytes
            metadata: Message metadata (session_id, timestamp, etc.)
            
        Returns:
            message_id: Unique identifier for tracking
        """
        try:
            message_id = self._generate_message_id()
            
            # Prepare comprehensive message
            message_data = {
                "id": message_id,
                "type": "audio_message",
                "timestamp": datetime.now().isoformat(),
                "payload": {
                    "audio_data": base64.b64encode(audio_file).decode('utf-8'),
                    "audio_format": "wav",
                    "audio_size": len(audio_file),
                    "encoding": "base64"
                },
                "metadata": {
                    **metadata,
                    "client_version": "2.0.0",
                    "platform": platform.system(),
                    "processing_info": metadata.get("processing_info", {}),
                    "device_info": self._get_device_info(),
                    "session_context": self._get_session_context()
                },
                "delivery_options": {
                    "priority": metadata.get("priority", "normal"),
                    "retry_count": 0,
                    "max_retries": self.max_retry_attempts,
                    "timeout": 30.0
                }
            }
            
            return await self._send_message_with_retry(message_id, message_data)
            
        except Exception as e:
            logger.error("Failed to prepare audio message", error=str(e), metadata=metadata)
            self.message_failed.emit("", f"Preparation failed: {e}")
            return ""
    
    async def send_text_message(self, text: str, metadata: dict) -> str:
        """
        Send text message with metadata
        
        Args:
            text: Text content
            metadata: Message metadata
            
        Returns:
            message_id: Unique identifier for tracking
        """
        try:
            message_id = self._generate_message_id()
            
            message_data = {
                "id": message_id,
                "type": "text_message",
                "timestamp": datetime.now().isoformat(),
                "payload": {
                    "text": text,
                    "length": len(text),
                    "language": metadata.get("language", "auto")
                },
                "metadata": {
                    **metadata,
                    "client_version": "2.0.0",
                    "platform": platform.system(),
                    "device_info": self._get_device_info(),
                    "session_context": self._get_session_context()
                },
                "delivery_options": {
                    "priority": metadata.get("priority", "normal"),
                    "retry_count": 0,
                    "max_retries": self.max_retry_attempts,
                    "timeout": 15.0
                }
            }
            
            return await self._send_message_with_retry(message_id, message_data)
            
        except Exception as e:
            logger.error("Failed to prepare text message", error=str(e), text=text[:50])
            self.message_failed.emit("", f"Preparation failed: {e}")
            return ""
    
    async def _send_message_with_retry(self, message_id: str, message_data: dict) -> str:
        """Send message with automatic retry logic"""
        try:
            # Store for potential retry
            self.pending_messages[message_id] = message_data.copy()
            
            # Check connection
            if not self.websocket_client.is_connected:
                logger.warning("No connection - queuing message for retry", message_id=message_id)
                self._queue_for_retry(message_data)
                return message_id
            
            # Emit progress
            self.sending_progress.emit(message_id, 0)
            
            # Add compression for large messages
            if self._should_compress_message(message_data):
                message_data = await self._compress_message(message_data)
                self.sending_progress.emit(message_id, 25)
            
            # Send chunked for very large messages
            if self._should_chunk_message(message_data):
                await self._send_chunked_message(message_id, message_data)
            else:
                # Send normally
                self.sending_progress.emit(message_id, 50)
                success = self.websocket_client.send_message(message_data)
                
                if success:
                    self.sending_progress.emit(message_id, 100)
                    self.message_sent.emit(message_id)
                    logger.info("Message sent successfully", message_id=message_id, 
                              type=message_data["type"])
                else:
                    raise Exception("WebSocket send failed")
            
            return message_id
            
        except Exception as e:
            logger.error("Failed to send message", error=str(e), message_id=message_id)
            self._queue_for_retry(message_data)
            self.message_failed.emit(message_id, str(e))
            return message_id
    
    async def _send_chunked_message(self, message_id: str, message_data: dict):
        """Send large message in chunks"""
        chunk_size = 64 * 1024  # 64KB chunks
        
        # Extract large payload
        payload = message_data["payload"]
        if "audio_data" in payload:
            large_data = payload["audio_data"]
            data_type = "audio_data"
        else:
            large_data = json.dumps(payload)
            data_type = "json_data"
        
        total_chunks = (len(large_data) + chunk_size - 1) // chunk_size
        
        # Send initial chunk message
        init_message = {
            **message_data,
            "chunked": True,
            "chunk_info": {
                "total_chunks": total_chunks,
                "chunk_size": chunk_size,
                "data_type": data_type,
                "total_size": len(large_data)
            },
            "payload": {"chunk_id": 0, "is_init": True}
        }
        
        self.websocket_client.send_message(init_message)
        
        # Send data chunks
        for i in range(total_chunks):
            start_idx = i * chunk_size
            end_idx = min(start_idx + chunk_size, len(large_data))
            chunk_data = large_data[start_idx:end_idx]
            
            chunk_message = {
                "id": f"{message_id}_chunk_{i}",
                "type": "message_chunk",
                "parent_id": message_id,
                "chunk_id": i,
                "total_chunks": total_chunks,
                "payload": chunk_data
            }
            
            self.websocket_client.send_message(chunk_message)
            
            # Update progress
            progress = int((i + 1) / total_chunks * 100)
            self.sending_progress.emit(message_id, progress)
            
            # Small delay to prevent overwhelming
            await asyncio.sleep(0.01)
        
        logger.info("Chunked message sent", message_id=message_id, chunks=total_chunks)
    
    def _should_compress_message(self, message_data: dict) -> bool:
        """Check if message should be compressed"""
        message_size = len(json.dumps(message_data))
        return message_size > 10 * 1024  # 10KB threshold
    
    def _should_chunk_message(self, message_data: dict) -> bool:
        """Check if message should be sent in chunks"""
        message_size = len(json.dumps(message_data))
        return message_size > 100 * 1024  # 100KB threshold
    
    async def _compress_message(self, message_data: dict) -> dict:
        """Compress message payload"""
        try:
            import gzip
            
            # Compress audio data if present
            if "audio_data" in message_data.get("payload", {}):
                audio_data = message_data["payload"]["audio_data"]
                compressed = gzip.compress(audio_data.encode('utf-8'))
                compressed_b64 = base64.b64encode(compressed).decode('utf-8')
                
                message_data["payload"]["audio_data"] = compressed_b64
                message_data["payload"]["compressed"] = True
                message_data["payload"]["compression_ratio"] = len(compressed) / len(audio_data)
                
                logger.info("Message compressed", 
                          original_size=len(audio_data),
                          compressed_size=len(compressed),
                          ratio=message_data["payload"]["compression_ratio"])
            
            return message_data
            
        except Exception as e:
            logger.warning("Compression failed, sending uncompressed", error=str(e))
            return message_data
    
    def _queue_for_retry(self, message_data: dict):
        """Queue message for retry"""
        retry_count = message_data["delivery_options"]["retry_count"]
        max_retries = message_data["delivery_options"]["max_retries"]
        
        if retry_count < max_retries:
            message_data["delivery_options"]["retry_count"] += 1
            message_data["delivery_options"]["retry_timestamp"] = time.time() + self.retry_delay
            self.retry_queue.append(message_data)
            
            logger.info("Message queued for retry", 
                       message_id=message_data["id"],
                       attempt=retry_count + 1,
                       max_attempts=max_retries)
        else:
            logger.error("Message exceeded max retries", 
                        message_id=message_data["id"],
                        attempts=retry_count)
            self.message_failed.emit(message_data["id"], "Max retries exceeded")
    
    def _process_retry_queue(self):
        """Process queued retry messages"""
        if not self.retry_queue:
            return
        
        current_time = time.time()
        ready_messages = []
        
        # Find messages ready for retry
        for message in self.retry_queue[:]:
            if current_time >= message["delivery_options"]["retry_timestamp"]:
                ready_messages.append(message)
                self.retry_queue.remove(message)
        
        # Retry ready messages
        for message in ready_messages:
            if self.websocket_client.is_connected:
                asyncio.create_task(self._send_message_with_retry(message["id"], message))
            else:
                # Put back in queue
                message["delivery_options"]["retry_timestamp"] = current_time + self.retry_delay
                self.retry_queue.append(message)
    
    def _on_connection_restored(self):
        """Handle connection restoration"""
        if self.retry_queue:
            logger.info("Connection restored - processing retry queue", 
                       pending_messages=len(self.retry_queue))
            self.connection_restored.emit()
            
            # Reset retry timestamps for immediate processing
            current_time = time.time()
            for message in self.retry_queue:
                message["delivery_options"]["retry_timestamp"] = current_time
    
    def _handle_server_response(self, response: dict):
        """Handle server response to messages"""
        try:
            if response.get("type") == "message_ack":
                message_id = response.get("message_id")
                if message_id and message_id in self.pending_messages:
                    del self.pending_messages[message_id]
                    self.message_delivered.emit(message_id, response)
                    logger.info("Message acknowledged", message_id=message_id)
            
            elif response.get("type") == "message_response":
                message_id = response.get("reply_to")
                if message_id:
                    self.message_delivered.emit(message_id, response)
                    logger.info("Message response received", message_id=message_id)
            
        except Exception as e:
            logger.error("Failed to handle server response", error=str(e), response=response)
    
    def _generate_message_id(self) -> str:
        """Generate unique message ID"""
        import uuid
        timestamp = int(time.time() * 1000)
        unique_id = str(uuid.uuid4())[:8]
        return f"msg_{timestamp}_{unique_id}"
    
    def _get_device_info(self) -> dict:
        """Get device information"""
        try:
            import psutil
            return {
                "cpu_count": psutil.cpu_count(),
                "memory_gb": round(psutil.virtual_memory().total / (1024**3), 2),
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "timestamp": datetime.now().isoformat()
            }
        except:
            return {
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "timestamp": datetime.now().isoformat()
            }
    
    def _get_session_context(self) -> dict:
        """Get current session context"""
        return {
            "session_start": getattr(self, 'session_start_time', datetime.now().isoformat()),
            "messages_sent": len(self.pending_messages),
            "retry_queue_size": len(self.retry_queue),
            "connection_stable": self.websocket_client.is_connected,
            "client_id": getattr(self.websocket_client, 'client_id', 'unknown')
        }
    
    def get_pending_messages_count(self) -> int:
        """Get count of pending messages"""
        return len(self.pending_messages) + len(self.retry_queue)
    
    def clear_pending_messages(self):
        """Clear all pending messages"""
        cleared_count = len(self.pending_messages) + len(self.retry_queue)
        self.pending_messages.clear()
        self.retry_queue.clear()
        logger.info("Pending messages cleared", count=cleared_count)


class EnterpriseDashboardWidget(QWidget):
    """Enterprise dashboard with advanced real-time analytics and emotion tracking"""
    
    # Signals for parent communication
    alert_triggered = Signal(str, str, dict)  # alert_type, message, data
    emotion_detected = Signal(list, float)     # emotions, confidence
    analytics_updated = Signal(dict)           # analytics_data
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_data_stores()
        self.setup_plotly_integration()
        self.setup_ui()
        self.setup_timers()
        self.setup_alert_system()
        
        logger.info("Enterprise dashboard initialized with advanced analytics")
        
    def setup_data_stores(self):
        """Initialize data storage for analytics"""
        self.emotion_history = []
        self.performance_data = []
        self.session_analytics = {}
        self.alerts_log = []
        self.real_time_buffer = {
            "emotions": [],
            "responses": [],
            "interactions": [],
            "timestamps": []
        }
        
        # Child profiles and learning analytics
        self.child_profiles = {}
        self.learning_progress = {}
        self.behavioral_patterns = {}
        
    def setup_plotly_integration(self):
        """Setup Plotly for advanced interactive charts"""
        try:
            import plotly.graph_objects as go
            import plotly.express as px
            from plotly.offline import plot
            import plotly.figure_factory as ff
            
            self.plotly_available = True
            self.go = go
            self.px = px
            self.plot = plot
            self.ff = ff
            
            logger.info("Plotly integration successful - advanced charts available")
            
        except ImportError:
            self.plotly_available = False
            logger.warning("Plotly not available - using fallback charts")
            print("⚠️ Install Plotly for advanced charts: pip install plotly")
    
    def setup_ui(self):
        """Setup comprehensive dashboard UI"""
        layout = QVBoxLayout(self)
        
        # Create responsive layout with splitters
        main_splitter = QSplitter(Qt.Horizontal)
        left_panel = self.create_left_panel()
        right_panel = self.create_right_panel()
        
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(right_panel)
        main_splitter.setSizes([400, 600])  # Left smaller, right larger for charts
        
        layout.addWidget(main_splitter)
        
    def create_left_panel(self) -> QWidget:
        """Create left panel with metrics and controls"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Real-time status metrics
        status_group = self.create_status_metrics()
        layout.addWidget(status_group)
        
        # Emotion summary
        emotion_group = self.create_emotion_summary()
        layout.addWidget(emotion_group)
        
        # Smart alerts panel
        alerts_group = self.create_alerts_panel()
        layout.addWidget(alerts_group)
        
        # Child profiles overview
        profiles_group = self.create_profiles_overview()
        layout.addWidget(profiles_group)
        
        layout.addStretch()
        return panel
    
    def create_right_panel(self) -> QWidget:
        """Create right panel with interactive charts"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Chart tabs for different visualizations
        self.chart_tabs = QTabWidget()
        
        # Emotion Analytics Tab
        emotion_tab = self.create_emotion_charts_tab()
        self.chart_tabs.addTab(emotion_tab, "😊 Emotion Analytics")
        
        # Performance Monitoring Tab  
        performance_tab = self.create_performance_charts_tab()
        self.chart_tabs.addTab(performance_tab, "📊 Performance")
        
        # Learning Progress Tab
        learning_tab = self.create_learning_charts_tab()
        self.chart_tabs.addTab(learning_tab, "🎓 Learning Progress")
        
        # Behavioral Patterns Tab
        behavior_tab = self.create_behavior_charts_tab()
        self.chart_tabs.addTab(behavior_tab, "🧠 Behavioral Patterns")
        
        layout.addWidget(self.chart_tabs)
        return panel
    
    def create_status_metrics(self) -> QGroupBox:
        """Create real-time status metrics"""
        group = QGroupBox("🚀 Real-Time System Status")
        layout = QGridLayout(group)
        
        # Connection status with visual indicator
        layout.addWidget(QLabel("Connection:"), 0, 0)
        self.connection_indicator = QLabel("●")
        self.connection_indicator.setStyleSheet("QLabel { color: red; font-size: 20px; }")
        self.connection_label = QLabel("Disconnected")
        connection_layout = QHBoxLayout()
        connection_layout.addWidget(self.connection_indicator)
        connection_layout.addWidget(self.connection_label)
        connection_layout.addStretch()
        connection_widget = QWidget()
        connection_widget.setLayout(connection_layout)
        layout.addWidget(connection_widget, 0, 1)
        
        # Active children
        layout.addWidget(QLabel("Active Children:"), 1, 0)
        self.active_children_label = QLabel("0")
        self.active_children_label.setStyleSheet("QLabel { font-weight: bold; color: #2196F3; }")
        layout.addWidget(self.active_children_label, 1, 1)
        
        # Total interactions today
        layout.addWidget(QLabel("Interactions Today:"), 2, 0)
        self.interactions_label = QLabel("0")
        self.interactions_label.setStyleSheet("QLabel { font-weight: bold; color: #4CAF50; }")
        layout.addWidget(self.interactions_label, 2, 1)
        
        # Average response time
        layout.addWidget(QLabel("Avg Response Time:"), 3, 0)
        self.response_time_label = QLabel("0ms")
        self.response_time_label.setStyleSheet("QLabel { font-weight: bold; color: #FF9800; }")
        layout.addWidget(self.response_time_label, 3, 1)
        
        # System health with progress bar
        layout.addWidget(QLabel("System Health:"), 4, 0)
        self.health_progress = QProgressBar()
        self.health_progress.setRange(0, 100)
        self.health_progress.setValue(100)
        self.health_progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ddd;
                border-radius: 5px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4CAF50, stop:0.7 #FFC107, stop:1 #F44336);
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.health_progress, 4, 1)
        
        return group
    
    def create_emotion_summary(self) -> QGroupBox:
        """Create emotion summary with current mood"""
        group = QGroupBox("😊 Current Emotion Summary")
        layout = QVBoxLayout(group)
        
        # Dominant emotion display
        self.dominant_emotion_label = QLabel("😐 Neutral")
        self.dominant_emotion_label.setAlignment(Qt.AlignCenter)
        self.dominant_emotion_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                background-color: #f0f0f0;
                border: 2px solid #ddd;
                border-radius: 8px;
                padding: 10px;
                margin: 5px;
            }
        """)
        layout.addWidget(self.dominant_emotion_label)
        
        # Emotion confidence
        layout.addWidget(QLabel("Confidence:"))
        self.emotion_confidence = QProgressBar()
        self.emotion_confidence.setRange(0, 100)
        self.emotion_confidence.setValue(0)
        self.emotion_confidence.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ddd;
                border-radius: 5px;
                text-align: center;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4CAF50, stop:0.5 #2196F3, stop:1 #9C27B0);
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.emotion_confidence)
        
        # Recent emotions list
        layout.addWidget(QLabel("Recent Emotions:"))
        self.recent_emotions_list = QListWidget()
        self.recent_emotions_list.setMaximumHeight(100)
        self.recent_emotions_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                font-size: 12px;
            }
            QListWidget::item {
                padding: 4px;
                border-bottom: 1px solid #eee;
            }
        """)
        layout.addWidget(self.recent_emotions_list)
        
        return group
    
    def create_alerts_panel(self) -> QGroupBox:
        """Create smart alerts panel for parents"""
        group = QGroupBox("🚨 Smart Parental Alerts")
        layout = QVBoxLayout(group)
        
        # Alert settings
        settings_layout = QHBoxLayout()
        
        self.alerts_enabled = QCheckBox("Enable Smart Alerts")
        self.alerts_enabled.setChecked(True)
        self.alerts_enabled.toggled.connect(self.toggle_alerts)
        settings_layout.addWidget(self.alerts_enabled)
        
        self.alert_sensitivity = QSlider(Qt.Horizontal)
        self.alert_sensitivity.setRange(1, 5)
        self.alert_sensitivity.setValue(3)
        self.alert_sensitivity.valueChanged.connect(self.update_alert_sensitivity)
        settings_layout.addWidget(QLabel("Sensitivity:"))
        settings_layout.addWidget(self.alert_sensitivity)
        
        layout.addLayout(settings_layout)
        
        # Active alerts display
        self.alerts_display = QTextEdit()
        self.alerts_display.setMaximumHeight(150)
        self.alerts_display.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: #fafafa;
                font-size: 11px;
            }
        """)
        self.alerts_display.setPlaceholderText("Smart alerts will appear here...")
        layout.addWidget(self.alerts_display)
        
        # Alert statistics
        stats_layout = QGridLayout()
        stats_layout.addWidget(QLabel("Today's Alerts:"), 0, 0)
        self.alerts_today_label = QLabel("0")
        stats_layout.addWidget(self.alerts_today_label, 0, 1)
        
        stats_layout.addWidget(QLabel("Priority Alerts:"), 1, 0)
        self.priority_alerts_label = QLabel("0")
        stats_layout.addWidget(self.priority_alerts_label, 1, 1)
        
        layout.addLayout(stats_layout)
        
        return group
    
    def create_profiles_overview(self) -> QGroupBox:
        """Create child profiles overview"""
        group = QGroupBox("👶 Children Profiles")
        layout = QVBoxLayout(group)
        
        # Profiles list
        self.profiles_list = QListWidget()
        self.profiles_list.setMaximumHeight(120)
        self.profiles_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                font-size: 12px;
            }
            QListWidget::item {
                padding: 6px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
            }
        """)
        layout.addWidget(self.profiles_list)
        
        # Quick stats
        stats_layout = QGridLayout()
        stats_layout.addWidget(QLabel("Total Children:"), 0, 0)
        self.total_children_label = QLabel("0")
        stats_layout.addWidget(self.total_children_label, 0, 1)
        
        stats_layout.addWidget(QLabel("Active Sessions:"), 1, 0)
        self.active_sessions_label = QLabel("0")
        stats_layout.addWidget(self.active_sessions_label, 1, 1)
        
        layout.addLayout(stats_layout)
        
        return group
    
    def create_emotion_charts_tab(self) -> QWidget:
        """Create emotion analytics charts tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Chart controls
        controls_layout = QHBoxLayout()
        
        # Time range selector
        controls_layout.addWidget(QLabel("Time Range:"))
        self.time_range_combo = QComboBox()
        self.time_range_combo.addItems(["Last Hour", "Last 6 Hours", "Last 24 Hours", "Last Week"])
        self.time_range_combo.setCurrentText("Last 6 Hours")
        self.time_range_combo.currentTextChanged.connect(self.update_emotion_charts)
        controls_layout.addWidget(self.time_range_combo)
        
        # Chart type selector
        controls_layout.addWidget(QLabel("Chart Type:"))
        self.emotion_chart_type = QComboBox()
        self.emotion_chart_type.addItems(["Line Chart", "Bar Chart", "Pie Chart", "Heatmap"])
        self.emotion_chart_type.currentTextChanged.connect(self.update_emotion_charts)
        controls_layout.addWidget(self.emotion_chart_type)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.refresh_emotion_data)
        controls_layout.addWidget(refresh_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Charts container
        self.emotion_charts_widget = QWidget()
        self.emotion_charts_layout = QVBoxLayout(self.emotion_charts_widget)
        
        # Initialize with placeholder
        placeholder_label = QLabel("📊 Emotion charts will appear here after first interaction")
        placeholder_label.setAlignment(Qt.AlignCenter)
        placeholder_label.setStyleSheet("QLabel { color: #666; font-size: 14px; }")
        self.emotion_charts_layout.addWidget(placeholder_label)
        
        layout.addWidget(self.emotion_charts_widget)
        
        return tab
    
    def create_performance_charts_tab(self) -> QWidget:
        """Create performance monitoring charts tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Performance metrics grid
        metrics_grid = QGridLayout()
        
        # Response time chart placeholder
        response_time_group = QGroupBox("Response Time Trends")
        response_time_layout = QVBoxLayout(response_time_group)
        
        self.response_time_chart = QLabel("📈 Response time chart will be generated here")
        self.response_time_chart.setAlignment(Qt.AlignCenter)
        self.response_time_chart.setMinimumHeight(200)
        self.response_time_chart.setStyleSheet("QLabel { border: 1px solid #ddd; background-color: #f9f9f9; }")
        response_time_layout.addWidget(self.response_time_chart)
        
        metrics_grid.addWidget(response_time_group, 0, 0)
        
        # System load chart placeholder
        system_load_group = QGroupBox("System Load")
        system_load_layout = QVBoxLayout(system_load_group)
        
        self.system_load_chart = QLabel("💻 System load chart will be generated here")
        self.system_load_chart.setAlignment(Qt.AlignCenter)
        self.system_load_chart.setMinimumHeight(200)
        self.system_load_chart.setStyleSheet("QLabel { border: 1px solid #ddd; background-color: #f9f9f9; }")
        system_load_layout.addWidget(self.system_load_chart)
        
        metrics_grid.addWidget(system_load_group, 0, 1)
        
        layout.addLayout(metrics_grid)
        
        return tab
    
    def create_learning_charts_tab(self) -> QWidget:
        """Create learning progress charts tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Learning metrics
        learning_info = QLabel("🎓 Learning progress analytics will be displayed here")
        learning_info.setAlignment(Qt.AlignCenter)
        learning_info.setStyleSheet("QLabel { color: #666; font-size: 14px; }")
        layout.addWidget(learning_info)
        
        return tab
    
    def create_behavior_charts_tab(self) -> QWidget:
        """Create behavioral patterns charts tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Behavioral analytics
        behavior_info = QLabel("🧠 Behavioral pattern analysis will be displayed here")
        behavior_info.setAlignment(Qt.AlignCenter)
        behavior_info.setStyleSheet("QLabel { color: #666; font-size: 14px; }")
        layout.addWidget(behavior_info)
        
        return tab
    
    def setup_timers(self):
        """Setup update timers for real-time data"""
        # Real-time data update timer (every 2 seconds)
        self.realtime_timer = QTimer()
        self.realtime_timer.timeout.connect(self.update_realtime_data)
        self.realtime_timer.start(2000)
        
        # Charts update timer (every 10 seconds)
        self.charts_timer = QTimer()
        self.charts_timer.timeout.connect(self.update_all_charts)
        self.charts_timer.start(10000)
        
        # Alerts processing timer (every 5 seconds)
        self.alerts_timer = QTimer()
        self.alerts_timer.timeout.connect(self.process_smart_alerts)
        self.alerts_timer.start(5000)
        
        logger.info("Dashboard timers configured for real-time updates")
    
    def setup_alert_system(self):
        """Setup intelligent alert system"""
        self.alert_rules = {
            "negative_emotion_streak": {
                "threshold": 3,
                "timeframe": 300,  # 5 minutes
                "message": "Child showing persistent negative emotions",
                "priority": "high"
            },
            "sudden_mood_change": {
                "threshold": 0.7,  # 70% confidence change
                "message": "Sudden mood change detected",
                "priority": "medium"
            },
            "low_engagement": {
                "threshold": 5,  # Less than 5 interactions in timeframe
                "timeframe": 1800,  # 30 minutes
                "message": "Child engagement appears low",
                "priority": "low"
            },
            "concerning_topics": {
                "keywords": ["hurt", "scared", "sad", "angry"],
                "message": "Child mentioned concerning topic",
                "priority": "high"
            }
        }
        
        self.alert_sensitivity_multiplier = 1.0
    
    def update_realtime_data(self):
        """Update real-time dashboard data"""
        try:
            # Simulate real-time data (in production, this would come from WebSocket)
            import random
            
            # Update basic metrics
            active_children = random.randint(0, 15)
            interactions_today = random.randint(50, 500)
            avg_response_time = random.randint(200, 1500)
            system_health = random.randint(85, 100)
            
            self.active_children_label.setText(str(active_children))
            self.interactions_label.setText(str(interactions_today))
            self.response_time_label.setText(f"{avg_response_time}ms")
            self.health_progress.setValue(system_health)
            
            # Simulate emotion data
            emotions = ["happy", "excited", "calm", "curious", "frustrated", "sad"]
            if random.random() > 0.7:  # 30% chance of emotion update
                current_emotion = random.choice(emotions)
                confidence = random.randint(60, 95)
                self.update_emotion_display(current_emotion, confidence)
                
                # Add to emotion history
                timestamp = datetime.now()
                self.emotion_history.append({
                    "emotion": current_emotion,
                    "confidence": confidence / 100,
                    "timestamp": timestamp
                })
                
                # Keep only last 100 entries
                if len(self.emotion_history) > 100:
                    self.emotion_history.pop(0)
            
        except Exception as e:
            logger.error("Failed to update real-time data", error=str(e))
    
    def update_emotion_display(self, emotion: str, confidence: int):
        """Update emotion display with current mood"""
        emotion_emojis = {
            "happy": "😊", "excited": "🤩", "calm": "😌", "curious": "🤔",
            "frustrated": "😤", "sad": "😢", "angry": "😠", "surprised": "😲",
            "neutral": "😐", "confused": "😕"
        }
        
        emoji = emotion_emojis.get(emotion, "😐")
        self.dominant_emotion_label.setText(f"{emoji} {emotion.title()}")
        self.emotion_confidence.setValue(confidence)
        
        # Update recent emotions list
        timestamp = datetime.now().strftime("%H:%M:%S")
        item_text = f"{emoji} {emotion.title()} ({confidence}%) - {timestamp}"
        self.recent_emotions_list.insertItem(0, item_text)
        
        # Keep only last 10 items
        if self.recent_emotions_list.count() > 10:
            self.recent_emotions_list.takeItem(self.recent_emotions_list.count() - 1)
        
        # Update background color based on emotion
        color_map = {
            "happy": "#e8f5e8", "excited": "#fff3e0", "calm": "#e3f2fd",
            "curious": "#f3e5f5", "frustrated": "#ffebee", "sad": "#f1f8e9"
        }
        bg_color = color_map.get(emotion, "#f0f0f0")
        self.dominant_emotion_label.setStyleSheet(f"""
            QLabel {{
                font-size: 18px;
                font-weight: bold;
                background-color: {bg_color};
                border: 2px solid #ddd;
                border-radius: 8px;
                padding: 10px;
                margin: 5px;
            }}
        """)
    
    def update_connection_status(self, status: str):
        """Update connection status with visual indicators"""
        status_config = {
            "Connected": {"color": "green", "indicator": "●"},
            "Connecting...": {"color": "orange", "indicator": "◐"},
            "Disconnected": {"color": "red", "indicator": "●"},
            "Error": {"color": "red", "indicator": "✖"},
            "Failed": {"color": "red", "indicator": "✖"}
        }
        
        config = status_config.get(status, {"color": "gray", "indicator": "●"})
        
        self.connection_indicator.setText(config["indicator"])
        self.connection_indicator.setStyleSheet(f"QLabel {{ color: {config['color']}; font-size: 20px; }}")
        self.connection_label.setText(status)
    
    def update_emotion_charts(self):
        """Update emotion analytics charts with Plotly"""
        if not self.plotly_available or not self.emotion_history:
            return
            
        try:
            # Clear existing charts
            for i in reversed(range(self.emotion_charts_layout.count())):
                self.emotion_charts_layout.itemAt(i).widget().setParent(None)
            
            chart_type = self.emotion_chart_type.currentText()
            time_range = self.time_range_combo.currentText()
            
            # Filter data based on time range
            filtered_data = self.filter_emotion_data_by_time(time_range)
            
            if chart_type == "Line Chart":
                self.create_emotion_line_chart(filtered_data)
            elif chart_type == "Bar Chart":
                self.create_emotion_bar_chart(filtered_data)
            elif chart_type == "Pie Chart":
                self.create_emotion_pie_chart(filtered_data)
            elif chart_type == "Heatmap":
                self.create_emotion_heatmap(filtered_data)
                
        except Exception as e:
            logger.error("Failed to update emotion charts", error=str(e))
    
    def filter_emotion_data_by_time(self, time_range: str) -> list:
        """Filter emotion data based on selected time range"""
        now = datetime.now()
        
        time_deltas = {
            "Last Hour": 3600,
            "Last 6 Hours": 21600,
            "Last 24 Hours": 86400,
            "Last Week": 604800
        }
        
        seconds = time_deltas.get(time_range, 21600)
        cutoff_time = now - timedelta(seconds=seconds)
        
        return [
            entry for entry in self.emotion_history 
            if entry["timestamp"] >= cutoff_time
        ]
    
    def create_emotion_line_chart(self, data: list):
        """Create interactive emotion line chart with Plotly"""
        if not data:
            return
            
        # Prepare data for plotting
        timestamps = [entry["timestamp"] for entry in data]
        emotions = [entry["emotion"] for entry in data]
        confidences = [entry["confidence"] for entry in data]
        
        # Create line chart
        fig = self.go.Figure()
        
        # Group by emotion and create separate lines
        unique_emotions = list(set(emotions))
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
        
        for i, emotion in enumerate(unique_emotions):
            emotion_times = [timestamps[j] for j, e in enumerate(emotions) if e == emotion]
            emotion_conf = [confidences[j] for j, e in enumerate(emotions) if e == emotion]
            
            fig.add_trace(self.go.Scatter(
                x=emotion_times,
                y=emotion_conf,
                mode='lines+markers',
                name=emotion.title(),
                line=dict(color=colors[i % len(colors)], width=3),
                marker=dict(size=8)
            ))
        
        fig.update_layout(
            title="Emotion Confidence Over Time",
            xaxis_title="Time",
            yaxis_title="Confidence",
            hovermode='x unified',
            template='plotly_white'
        )
        
        # Save and display chart
        self.display_plotly_chart(fig, "emotion_line_chart")
    
    def create_emotion_pie_chart(self, data: list):
        """Create emotion distribution pie chart"""
        if not data:
            return
            
        # Count emotions
        emotion_counts = {}
        for entry in data:
            emotion = entry["emotion"]
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        if not emotion_counts:
            return
            
        fig = self.go.Figure(data=[self.go.Pie(
            labels=list(emotion_counts.keys()),
            values=list(emotion_counts.values()),
            hole=0.3,
            textinfo='label+percent',
            textfont_size=12
        )])
        
        fig.update_layout(
            title="Emotion Distribution",
            template='plotly_white'
        )
        
        self.display_plotly_chart(fig, "emotion_pie_chart")
    
    def display_plotly_chart(self, fig, filename: str):
        """Display Plotly chart in Qt widget"""
        try:
            # Generate HTML
            html_str = fig.to_html(include_plotlyjs='cdn', div_id=filename)
            
            # Create web view to display chart
            from PySide6.QtWebEngineWidgets import QWebEngineView
            
            web_view = QWebEngineView()
            web_view.setHtml(html_str)
            web_view.setMinimumHeight(400)
            
            self.emotion_charts_layout.addWidget(web_view)
            
        except ImportError:
            # Fallback to saving as image and displaying
            logger.warning("QWebEngineView not available - saving chart as image")
            img_path = f"temp_{filename}.png"
            fig.write_image(img_path)
            
            # Display image in label
            pixmap = QPixmap(img_path)
            label = QLabel()
            label.setPixmap(pixmap.scaled(800, 400, Qt.KeepAspectRatio))
            self.emotion_charts_layout.addWidget(label)
    
    def process_smart_alerts(self):
        """Process and generate smart alerts for parents"""
        if not self.alerts_enabled.isChecked():
            return
            
        try:
            current_time = datetime.now()
            
            # Check for negative emotion streak
            self.check_negative_emotion_streak(current_time)
            
            # Check for sudden mood changes
            self.check_sudden_mood_changes()
            
            # Update alert statistics
            self.update_alert_statistics()
            
        except Exception as e:
            logger.error("Failed to process smart alerts", error=str(e))
    
    def check_negative_emotion_streak(self, current_time: datetime):
        """Check for streak of negative emotions"""
        negative_emotions = ["sad", "angry", "frustrated", "confused"]
        recent_emotions = [
            entry for entry in self.emotion_history[-10:] 
            if entry["emotion"] in negative_emotions
        ]
        
        if len(recent_emotions) >= 3:
            self.trigger_alert(
                "negative_streak",
                "⚠️ Child showing persistent negative emotions",
                {"emotions": recent_emotions, "severity": "medium"}
            )
    
    def trigger_alert(self, alert_type: str, message: str, data: dict):
        """Trigger a smart alert"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        alert_text = f"[{timestamp}] {message}\n"
        
        current_text = self.alerts_display.toPlainText()
        self.alerts_display.setPlainText(alert_text + current_text)
        
        # Add to alerts log
        self.alerts_log.append({
            "type": alert_type,
            "message": message,
            "data": data,
            "timestamp": datetime.now()
        })
        
        # Emit signal for parent window
        self.alert_triggered.emit(alert_type, message, data)
        
        logger.info("Smart alert triggered", type=alert_type, message=message)
    
    def toggle_alerts(self, enabled: bool):
        """Toggle smart alerts on/off"""
        if enabled:
            self.alerts_timer.start(5000)
            logger.info("Smart alerts enabled")
        else:
            self.alerts_timer.stop()
            logger.info("Smart alerts disabled")
    
    def update_alert_sensitivity(self, value: int):
        """Update alert sensitivity"""
        self.alert_sensitivity_multiplier = value / 3.0  # 1-5 scale to 0.33-1.67 multiplier
        logger.info("Alert sensitivity updated", multiplier=self.alert_sensitivity_multiplier)
    
    def update_alert_statistics(self):
        """Update alert statistics display"""
        today = datetime.now().date()
        today_alerts = [
            alert for alert in self.alerts_log 
            if alert["timestamp"].date() == today
        ]
        
        priority_alerts = [
            alert for alert in today_alerts 
            if alert.get("data", {}).get("severity") in ["high", "critical"]
        ]
        
        self.alerts_today_label.setText(str(len(today_alerts)))
        self.priority_alerts_label.setText(str(len(priority_alerts)))
    
    def update_all_charts(self):
        """Update all charts and visualizations"""
        self.update_emotion_charts()
        # Add other chart updates here
    
    def refresh_emotion_data(self):
        """Manually refresh emotion data and charts"""
        self.update_emotion_charts()
        logger.info("Emotion data refreshed manually")
    
    def add_child_profile(self, child_data: dict):
        """Add new child profile to dashboard"""
        name = child_data.get("name", "Unknown")
        age = child_data.get("age", "Unknown")
        
        profile_text = f"{name} (Age: {age})"
        self.profiles_list.addItem(profile_text)
        
        # Update totals
        self.total_children_label.setText(str(self.profiles_list.count()))
        
        logger.info("Child profile added to dashboard", name=name, age=age)
    
    def update_session_analytics(self, analytics: dict):
        """Update session analytics data"""
        self.session_analytics.update(analytics)
        self.analytics_updated.emit(analytics)
    
    def get_dashboard_summary(self) -> dict:
        """Get comprehensive dashboard summary"""
        return {
            "active_children": int(self.active_children_label.text()),
            "interactions_today": int(self.interactions_label.text()),
            "system_health": self.health_progress.value(),
            "alerts_today": len([a for a in self.alerts_log if a["timestamp"].date() == datetime.now().date()]),
            "emotion_history_count": len(self.emotion_history),
            "total_profiles": self.profiles_list.count()
        }


# Update the alias for backward compatibility
ModernDashboardWidget = EnterpriseDashboardWidget


class ModernAudioWidget(QWidget):
    """Modern audio interface widget with real recording capabilities"""
    
    audio_recorded = Signal(bytes)
    audio_level_changed = Signal(float)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_audio_config()
        self.setup_ui()
        self.setup_audio_system()
        
    def setup_audio_config(self):
        """Setup audio configuration"""
        self.is_recording = False
        self.sample_rate = 16000  # Hz
        self.channels = 1  # Mono
        self.chunk_size = 1024
        self.audio_format = pyaudio.paInt16 if PYAUDIO_AVAILABLE else None
        self.audio_data = []
        self.recording_thread = None
        self.audio_stream = None
        self.pyaudio_instance = None
        
        # Audio visualization
        self.waveform_data = np.zeros(100)
        self.volume_level = 0
        
        # Audio processing engine
        self.audio_processor = AudioProcessingEngine(sample_rate=self.sample_rate)
        self.processing_level = "auto"  # Default processing level
        self.enable_processing = True
        
    def setup_ui(self):
        """Setup audio interface"""
        layout = QVBoxLayout(self)
        
        # Audio device selection
        device_group = QGroupBox("Audio Device Configuration")
        device_layout = QGridLayout(device_group)
        
        # Input device selection
        device_layout.addWidget(QLabel("Input Device:"), 0, 0)
        self.input_device_combo = QComboBox()
        self.populate_audio_devices()
        device_layout.addWidget(self.input_device_combo, 0, 1)
        
        # Sample rate selection
        device_layout.addWidget(QLabel("Sample Rate:"), 1, 0)
        self.sample_rate_combo = QComboBox()
        self.sample_rate_combo.addItems(["16000", "22050", "44100", "48000"])
        self.sample_rate_combo.setCurrentText("16000")
        self.sample_rate_combo.currentTextChanged.connect(self.update_sample_rate)
        device_layout.addWidget(self.sample_rate_combo, 1, 1)
        
        layout.addWidget(device_group)
        
        # Audio processing configuration
        processing_group = QGroupBox("Audio Processing & Enhancement")
        processing_layout = QGridLayout(processing_group)
        
        # Enable processing toggle
        processing_layout.addWidget(QLabel("Enable Processing:"), 0, 0)
        self.enable_processing_checkbox = QCheckBox("Enhanced Audio Processing")
        self.enable_processing_checkbox.setChecked(True)
        self.enable_processing_checkbox.toggled.connect(self.toggle_audio_processing)
        processing_layout.addWidget(self.enable_processing_checkbox, 0, 1)
        
        # Processing level selection
        processing_layout.addWidget(QLabel("Processing Level:"), 1, 0)
        self.processing_level_combo = QComboBox()
        self.processing_level_combo.addItems(["auto", "low", "medium", "high"])
        self.processing_level_combo.setCurrentText("auto")
        self.processing_level_combo.currentTextChanged.connect(self.update_processing_level)
        processing_layout.addWidget(self.processing_level_combo, 1, 1)
        
        # Processing capabilities info
        capabilities = self.audio_processor.get_processing_capabilities()
        capabilities_text = f"System: {capabilities['performance_mode'].title()} Performance\n"
        capabilities_text += f"Recommended: {capabilities['recommended_level'].title()}\n"
        capabilities_text += f"Est. Time: {capabilities['max_processing_time']}"
        
        self.capabilities_label = QLabel(capabilities_text)
        self.capabilities_label.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 8px;
                font-size: 11px;
                color: #666;
            }
        """)
        processing_layout.addWidget(self.capabilities_label, 2, 0, 1, 2)
        
        # Processing steps indicator
        processing_layout.addWidget(QLabel("Processing Steps:"), 3, 0)
        self.processing_steps_label = QLabel("Will be shown after recording")
        self.processing_steps_label.setStyleSheet("QLabel { font-size: 11px; color: #888; }")
        processing_layout.addWidget(self.processing_steps_label, 3, 1)
        
        layout.addWidget(processing_group)
        
        # Recording controls
        controls_group = QGroupBox("Recording Controls")
        controls_layout = QHBoxLayout(controls_group)
        
        self.record_button = QPushButton("🎤 Start Recording")
        self.record_button.setMinimumHeight(60)
        self.record_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        self.record_button.clicked.connect(self.toggle_recording)
        
        self.stop_button = QPushButton("⏹️ Stop")
        self.stop_button.setMinimumHeight(60)
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_recording)
        
        self.test_button = QPushButton("🔧 Test Audio")
        self.test_button.setMinimumHeight(60)
        self.test_button.clicked.connect(self.test_audio_device)
        
        self.performance_test_button = QPushButton("⚡ Test Processing")
        self.performance_test_button.setMinimumHeight(60)
        self.performance_test_button.clicked.connect(self.test_processing_performance)
        
        controls_layout.addWidget(self.record_button)
        controls_layout.addWidget(self.stop_button)
        controls_layout.addWidget(self.test_button)
        controls_layout.addWidget(self.performance_test_button)
        
        layout.addWidget(controls_group)
        
        # Live audio visualization
        viz_group = QGroupBox("Live Audio Visualization")
        viz_layout = QVBoxLayout(viz_group)
        
        # Volume level
        volume_layout = QHBoxLayout()
        volume_layout.addWidget(QLabel("Volume:"))
        self.volume_meter = QProgressBar()
        self.volume_meter.setRange(0, 100)
        self.volume_meter.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ddd;
                border-radius: 5px;
                text-align: center;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4CAF50, stop:0.7 #FFC107, stop:1 #F44336);
                border-radius: 3px;
            }
        """)
        volume_layout.addWidget(self.volume_meter)
        self.volume_label = QLabel("0%")
        self.volume_label.setMinimumWidth(40)
        volume_layout.addWidget(self.volume_label)
        viz_layout.addLayout(volume_layout)
        
        # Waveform display
        self.waveform_widget = WaveformWidget()
        self.waveform_widget.setMinimumHeight(120)
        viz_layout.addWidget(QLabel("Live Waveform:"))
        viz_layout.addWidget(self.waveform_widget)
        
        layout.addWidget(viz_group)
        
        # Recording info and status
        info_group = QGroupBox("Recording Information")
        info_layout = QGridLayout(info_group)
        
        self.status_label = QLabel("Ready to record")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("QLabel { font-size: 14px; color: #666; font-weight: bold; }")
        info_layout.addWidget(self.status_label, 0, 0, 1, 2)
        
        info_layout.addWidget(QLabel("Duration:"), 1, 0)
        self.duration_label = QLabel("0:00")
        info_layout.addWidget(self.duration_label, 1, 1)
        
        info_layout.addWidget(QLabel("File Size:"), 2, 0)
        self.file_size_label = QLabel("0 KB")
        info_layout.addWidget(self.file_size_label, 2, 1)
        
        layout.addWidget(info_group)
        
    def setup_audio_system(self):
        """Initialize audio system"""
        try:
            if PYAUDIO_AVAILABLE:
                self.pyaudio_instance = pyaudio.PyAudio()
                logger.info("PyAudio initialized successfully")
            elif SOUNDDEVICE_AVAILABLE:
                logger.info("Using SoundDevice for audio")
            else:
                self.status_label.setText("❌ No audio library available")
                self.record_button.setEnabled(False)
                logger.error("No audio recording library available")
                return
                
            # Setup visualization timer
            self.visualization_timer = QTimer()
            self.visualization_timer.timeout.connect(self.update_waveform)
            
            # Setup recording timer
            self.recording_timer = QTimer()
            self.recording_timer.timeout.connect(self.update_recording_info)
            
            self.status_label.setText("🟢 Audio system ready")
            
        except Exception as e:
            logger.error("Failed to initialize audio system", error=str(e))
            self.status_label.setText(f"❌ Audio init error: {e}")
            self.record_button.setEnabled(False)
    
    def populate_audio_devices(self):
        """Populate audio device list"""
        self.input_device_combo.clear()
        
        try:
            if SOUNDDEVICE_AVAILABLE:
                devices = sd.query_devices()
                for i, device in enumerate(devices):
                    if device['max_input_channels'] > 0:
                        device_name = f"{device['name']} ({i})"
                        self.input_device_combo.addItem(device_name, i)
            
            if self.input_device_combo.count() == 0:
                self.input_device_combo.addItem("Default Device", None)
                
        except Exception as e:
            logger.error("Failed to enumerate audio devices", error=str(e))
            self.input_device_combo.addItem("Default Device", None)
    
    def update_sample_rate(self, rate_text):
        """Update sample rate"""
        try:
            self.sample_rate = int(rate_text)
            # Update audio processor with new sample rate
            self.audio_processor = AudioProcessingEngine(sample_rate=self.sample_rate)
            logger.info("Sample rate updated", rate=self.sample_rate)
        except ValueError:
            logger.error("Invalid sample rate", rate=rate_text)
    
    def toggle_audio_processing(self, enabled):
        """Toggle audio processing on/off"""
        self.enable_processing = enabled
        self.processing_level_combo.setEnabled(enabled)
        
        status = "enabled" if enabled else "disabled"
        logger.info("Audio processing toggled", status=status)
    
    def update_processing_level(self, level):
        """Update audio processing level"""
        self.processing_level = level
        
        # Update capabilities display
        capabilities = self.audio_processor.get_processing_capabilities()
        if level == "auto":
            actual_level = capabilities['performance_mode']
        else:
            actual_level = level
            
        # Update estimated processing time
        time_estimates = {
            "low": "< 1 second",
            "medium": "< 3 seconds", 
            "high": "< 10 seconds"
        }
        
        capabilities_text = f"System: {capabilities['performance_mode'].title()} Performance\n"
        capabilities_text += f"Selected: {level.title()} → {actual_level.title()}\n"
        capabilities_text += f"Est. Time: {time_estimates.get(actual_level, 'Unknown')}"
        
        self.capabilities_label.setText(capabilities_text)
        logger.info("Processing level updated", level=level, actual=actual_level)
    
    def toggle_recording(self):
        """Toggle recording state"""
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        """Start recording audio - REAL IMPLEMENTATION"""
        try:
            self.is_recording = True
            self.audio_data = []
            self.recording_start_time = datetime.now()
            
            # Update UI
            self.record_button.setText("🔴 Recording...")
            self.record_button.setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 16px;
                    font-weight: bold;
                    animation: pulse 1s infinite;
                }
            """)
            self.stop_button.setEnabled(True)
            self.record_button.setEnabled(False)
            self.status_label.setText("🔴 Recording in progress...")
            
            # Start recording with preferred method
            if SOUNDDEVICE_AVAILABLE:
                self._start_sounddevice_recording()
            elif PYAUDIO_AVAILABLE:
                self._start_pyaudio_recording()
            else:
                raise Exception("No audio library available")
            
            # Start visualization and info timers
            self.visualization_timer.start(50)  # 20 FPS
            self.recording_timer.start(100)     # 10 Hz
            
            logger.info("Audio recording started successfully", 
                       sample_rate=self.sample_rate, channels=self.channels)
            
        except Exception as e:
            logger.error("Failed to start recording", error=str(e))
            self.status_label.setText(f"❌ Recording failed: {e}")
            self._reset_recording_state()
    
    def _start_sounddevice_recording(self):
        """Start recording using SoundDevice"""
        def audio_callback(indata, frames, time, status):
            if status:
                logger.warning("SoundDevice status", status=status)
            
            if self.is_recording:
                # Convert to the format we need
                audio_chunk = (indata[:, 0] * 32767).astype(np.int16)
                self.audio_data.append(audio_chunk.tobytes())
                
                # Calculate volume level for visualization
                volume = np.sqrt(np.mean(audio_chunk**2))
                self.volume_level = min(100, (volume / 1000) * 100)
                
                # Update waveform data
                self.waveform_data = np.roll(self.waveform_data, -len(audio_chunk))
                self.waveform_data[-len(audio_chunk):] = audio_chunk
        
        # Get selected device
        device_data = self.input_device_combo.currentData()
        device = device_data if device_data is not None else None
        
        self.audio_stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            callback=audio_callback,
            device=device,
            blocksize=self.chunk_size
        )
        self.audio_stream.start()
    
    def _start_pyaudio_recording(self):
        """Start recording using PyAudio"""
        def audio_callback(in_data, frame_count, time_info, status):
            if self.is_recording:
                self.audio_data.append(in_data)
                
                # Convert bytes to numpy array for visualization
                audio_chunk = np.frombuffer(in_data, dtype=np.int16)
                
                # Calculate volume level
                volume = np.sqrt(np.mean(audio_chunk**2))
                self.volume_level = min(100, (volume / 1000) * 100)
                
                # Update waveform data
                self.waveform_data = np.roll(self.waveform_data, -len(audio_chunk))
                self.waveform_data[-len(audio_chunk):] = audio_chunk
                
            return (in_data, pyaudio.paContinue)
        
        self.audio_stream = self.pyaudio_instance.open(
            format=self.audio_format,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size,
            stream_callback=audio_callback
        )
        self.audio_stream.start_stream()
    
    def stop_recording(self):
        """Stop recording audio and process the result"""
        try:
            self.is_recording = False
            
            # Stop audio stream
            if self.audio_stream:
                if hasattr(self.audio_stream, 'stop'):
                    self.audio_stream.stop()
                    self.audio_stream.close()
                else:
                    self.audio_stream.stop_stream()
                    self.audio_stream.close()
                self.audio_stream = None
            
            # Stop timers
            self.visualization_timer.stop()
            self.recording_timer.stop()
            
            # Update UI
            self.status_label.setText("⏳ Processing audio...")
            
            # Process recorded audio
            QTimer.singleShot(100, self._process_recorded_audio)
            
            logger.info("Audio recording stopped")
            
        except Exception as e:
            logger.error("Error stopping recording", error=str(e))
            self.status_label.setText(f"❌ Stop error: {e}")
            self._reset_recording_state()
    
    def _process_recorded_audio(self):
        """Process the recorded audio data with professional enhancement"""
        try:
            if not self.audio_data:
                self.status_label.setText("❌ No audio data recorded")
                self._reset_recording_state()
                return
            
            # Combine all audio chunks
            audio_bytes = b''.join(self.audio_data)
            
            # Convert to numpy array for processing
            audio_array = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
            
            processing_info = {}
            processed_audio = audio_array
            
            # Apply professional audio processing if enabled
            if self.enable_processing:
                self.status_label.setText("🔄 Enhancing audio quality...")
                
                try:
                    # Professional audio enhancement (السطر 365 - معالجة الصوت الاحترافية)
                    processed_audio, processing_info = self.audio_processor.clean_audio(
                        audio_array, self.processing_level
                    )
                    
                    # Update processing steps display
                    steps_text = " → ".join(processing_info.get("steps_applied", ["none"]))
                    self.processing_steps_label.setText(f"Applied: {steps_text}")
                    
                    # Show processing time
                    processing_time = processing_info.get("processing_time", 0)
                    quality_info = processing_info.get("quality_improvement", {})
                    
                    logger.info("Audio enhancement completed", 
                               processing_time=processing_time,
                               steps=processing_info.get("steps_applied", []),
                               quality_metrics=quality_info)
                    
                except Exception as e:
                    logger.warning("Audio processing failed, using original", error=str(e))
                    processed_audio = audio_array
                    processing_info = {"error": str(e)}
                    self.processing_steps_label.setText(f"Processing failed: {e}")
            else:
                self.processing_steps_label.setText("Processing disabled")
            
            # Convert back to int16 format
            processed_audio_int16 = (processed_audio * 32767).astype(np.int16)
            processed_bytes = processed_audio_int16.tobytes()
            
            # Create WAV file with processed audio
            wav_data = self._create_wav_data(processed_bytes)
            
            # Emit signal with processed audio
            self.audio_recorded.emit(wav_data)
            
            # Send to server via WebSocket with processing info
            self._send_audio_to_server(wav_data, processing_info)
            
            # Update UI with comprehensive info
            duration = (datetime.now() - self.recording_start_time).total_seconds()
            original_size = len(audio_bytes) / 1024  # KB
            final_size = len(wav_data) / 1024  # KB
            
            # Create status message
            status_parts = [f"✅ Audio recorded ({duration:.1f}s, {final_size:.1f}KB)"]
            
            if self.enable_processing and "processing_time" in processing_info:
                proc_time = processing_info["processing_time"]
                steps_count = len(processing_info.get("steps_applied", []))
                status_parts.append(f"Enhanced in {proc_time:.1f}s ({steps_count} steps)")
            
            self.status_label.setText(" | ".join(status_parts))
            
            logger.info("Complete audio processing finished", 
                       duration=duration, 
                       original_size_kb=original_size,
                       final_size_kb=final_size,
                       processing_enabled=self.enable_processing,
                       processing_info=processing_info)
            
        except Exception as e:
            logger.error("Error in audio processing pipeline", error=str(e))
            self.status_label.setText(f"❌ Processing error: {e}")
        finally:
            self._reset_recording_state()
    
    def _create_wav_data(self, audio_bytes: bytes) -> bytes:
        """Create WAV file data from raw audio bytes"""
        with tempfile.NamedTemporaryFile() as temp_file:
            with wave.open(temp_file.name, 'wb') as wav_file:
                wav_file.setnchannels(self.channels)
                wav_file.setsampwidth(2)  # 16-bit = 2 bytes
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(audio_bytes)
            
            temp_file.seek(0)
            return temp_file.read()
    
    def _send_audio_to_server(self, wav_data: bytes, processing_info: dict = None):
        """Send audio data to server via advanced enterprise WebSocket system"""
        try:
            # Get parent main window to access WebSocket client
            main_window = self.window()
            if not hasattr(main_window, 'websocket_client'):
                self.status_label.setText("❌ No WebSocket connection available")
                logger.error("WebSocket client not available in main window")
                return
            
            # Initialize enterprise message sender if not exists
            if not hasattr(self, 'message_sender'):
                self.message_sender = EnterpriseMessageSender(main_window.websocket_client)
                self._setup_message_sender_connections()
            
            # Prepare comprehensive metadata
            metadata = {
                "session_id": getattr(self, 'current_session_id', str(uuid.uuid4())),
                "device_id": "teddy_ui_client_audio",
                "timestamp": datetime.now().isoformat(),
                "audio_specs": {
                    "sample_rate": self.sample_rate,
                    "channels": self.channels,
                    "duration_seconds": len(wav_data) / (self.sample_rate * self.channels * 2),
                    "size_bytes": len(wav_data),
                    "format": "wav",
                    "bit_depth": 16,
                    "compression": "none"
                },
                "processing_info": processing_info or {},
                "user_context": {
                    "recording_method": "live_recording",
                    "processing_enabled": self.enable_processing,
                    "processing_level": self.processing_level,
                    "ui_version": "2.0.0",
                    "capabilities": self.get_audio_system_info(),
                    "device_performance": self.audio_processor.performance_mode
                },
                "delivery_requirements": {
                    "priority": "high",  # Audio messages are high priority
                    "acknowledgment_required": True,
                    "timeout_seconds": 30,
                    "chunking_enabled": True,  # Allow chunking for large audio
                    "compression_enabled": True  # Allow compression
                },
                "conversation_context": {
                    "message_type": "user_voice_input",
                    "expected_response": "ai_voice_response",
                    "language": "auto_detect",
                    "emotion_analysis": True
                }
            }
            
            # Update UI to show sending state
            self.status_label.setText("📤 Sending audio to AI server...")
            
            # Send audio message asynchronously
            asyncio.create_task(self._send_audio_async(wav_data, metadata))
            
            logger.info("Audio message preparation complete", 
                       size_mb=len(wav_data) / (1024 * 1024),
                       duration=metadata["audio_specs"]["duration_seconds"],
                       processing_applied=bool(processing_info))
            
        except Exception as e:
            logger.error("Failed to prepare audio message", error=str(e))
            self.status_label.setText(f"❌ Audio preparation failed: {e}")
    
    async def _send_audio_async(self, wav_data: bytes, metadata: dict):
        """Send audio message asynchronously with full enterprise features"""
        try:
            # Send via enterprise message sender
            message_id = await self.message_sender.send_audio_message(wav_data, metadata)
            
            if message_id:
                # Store message ID for tracking
                self.current_message_id = message_id
                self.status_label.setText(f"📤 Audio uploaded (ID: {message_id[:8]}...)")
                
                # Update conversation widget if exists
                if hasattr(self, 'conversation_widget'):
                    self.conversation_widget.add_message(
                        "User", 
                        f"🎤 Voice message sent ({metadata['audio_specs']['duration_seconds']:.1f}s)"
                    )
                
                logger.info("Audio message sent successfully", 
                           message_id=message_id,
                           size_mb=len(wav_data) / (1024 * 1024),
                           duration=metadata["audio_specs"]["duration_seconds"])
            else:
                self.status_label.setText("❌ Failed to send audio")
                
        except Exception as e:
            logger.error("Failed to send audio message", error=str(e))
            self.status_label.setText(f"❌ Send failed: {e}")
    
    def _setup_message_sender_connections(self):
        """Setup connections for enterprise message sender signals"""
        if hasattr(self, 'message_sender'):
            # Connect message sender signals for real-time UI updates
            self.message_sender.message_sent.connect(self._on_message_sent)
            self.message_sender.message_delivered.connect(self._on_message_delivered)
            self.message_sender.message_failed.connect(self._on_message_failed)
            self.message_sender.sending_progress.connect(self._on_sending_progress)
            self.message_sender.connection_restored.connect(self._on_connection_restored)
    
    def _on_message_sent(self, message_id: str):
        """Handle message sent confirmation"""
        self.status_label.setText(f"✅ Message sent, awaiting AI response...")
        logger.info("Message sent confirmation received", message_id=message_id)
    
    def _on_message_delivered(self, message_id: str, response: dict):
        """Handle message delivery and comprehensive server response"""
        try:
            response_type = response.get("type", "unknown")
            
            if response_type == "audio_response":
                # Handle AI audio/text response
                payload = response.get("payload", {})
                ai_response = payload.get("response", "No response")
                confidence = payload.get("confidence", 0)
                processing_time = payload.get("processing_time", 0)
                
                self.status_label.setText(f"🤖 AI Response (confidence: {confidence:.2f})")
                
                # Add to conversation widget
                if hasattr(self, 'conversation_widget'):
                    self.conversation_widget.add_message("Teddy AI", ai_response)
                
                # Handle emotional analysis if available
                emotions = payload.get("emotions", [])
                if emotions:
                    emotion_text = ", ".join([f"{e['name']} ({e['confidence']:.2f})" for e in emotions[:3]])
                    logger.info("Emotional analysis received", emotions=emotion_text)
                    
                    # Update parent window if it has emotion display
                    main_window = self.window()
                    if hasattr(main_window, '_update_emotion_display'):
                        main_window._update_emotion_display(emotions, confidence)
                
                # Handle voice response if available
                voice_data = payload.get("voice_response")
                if voice_data:
                    logger.info("Voice response received", size=len(voice_data))
                    # TODO: Play voice response
                
                logger.info("AI response delivered successfully", 
                           message_id=message_id,
                           response_length=len(ai_response),
                           confidence=confidence,
                           processing_time=processing_time,
                           emotions_detected=len(emotions))
                
            elif response_type == "message_ack":
                # Simple acknowledgment
                self.status_label.setText(f"✅ Message acknowledged, processing...")
                
            elif response_type == "processing_update":
                # Processing status update
                stage = response.get("payload", {}).get("stage", "unknown")
                progress = response.get("payload", {}).get("progress", 0)
                self.status_label.setText(f"🔄 Processing: {stage} ({progress}%)")
                
            elif response_type == "error_response":
                # Error from server
                error_msg = response.get("payload", {}).get("error", "Unknown error")
                error_code = response.get("payload", {}).get("error_code", "UNKNOWN")
                
                self.status_label.setText(f"❌ Server error: {error_msg}")
                logger.error("Server error response", 
                            message_id=message_id, 
                            error=error_msg, 
                            error_code=error_code)
                
                # Show error in conversation
                if hasattr(self, 'conversation_widget'):
                    self.conversation_widget.add_message(
                        "System", 
                        f"⚠️ Error: {error_msg} (Code: {error_code})"
                    )
                
        except Exception as e:
            logger.error("Failed to handle message delivery", error=str(e), response=response)
            self.status_label.setText("❌ Response processing failed")
    
    def _on_message_failed(self, message_id: str, error: str):
        """Handle message sending failure with intelligent retry logic"""
        self.status_label.setText(f"❌ Send failed: {error}")
        logger.error("Message sending failed", message_id=message_id, error=error)
        
        # Analyze error type and provide appropriate feedback
        if any(term in error.lower() for term in ["connection", "network", "timeout"]):
            self.status_label.setText(f"🔄 Network issue - will retry automatically")
            
            # Add network issue to conversation
            if hasattr(self, 'conversation_widget'):
                self.conversation_widget.add_message(
                    "System", 
                    "🔄 Connection issue detected. Message will be retried automatically."
                )
                
        elif "max retries" in error.lower():
            self.status_label.setText(f"❌ All retry attempts failed")
            
            # Add failure to conversation
            if hasattr(self, 'conversation_widget'):
                self.conversation_widget.add_message(
                    "System", 
                    "❌ Unable to send message after multiple attempts. Please check connection."
                )
        else:
            # Unknown error
            if hasattr(self, 'conversation_widget'):
                self.conversation_widget.add_message(
                    "System", 
                    f"❌ Send error: {error}"
                )
    
    def _on_sending_progress(self, message_id: str, progress: int):
        """Handle sending progress updates with visual feedback"""
        if progress < 25:
            self.status_label.setText(f"📤 Preparing message... {progress}%")
        elif progress < 50:
            self.status_label.setText(f"🗜️ Compressing audio... {progress}%")
        elif progress < 75:
            self.status_label.setText(f"📡 Uploading to server... {progress}%")
        elif progress < 100:
            self.status_label.setText(f"✅ Upload complete... {progress}%")
        else:
            self.status_label.setText(f"⏳ Processing on server...")
    
    def _on_connection_restored(self):
        """Handle connection restoration with user feedback"""
        self.status_label.setText("🔄 Connection restored - retrying pending messages...")
        logger.info("Connection restored - enterprise message sender will retry pending messages")
        
        # Notify in conversation
        if hasattr(self, 'conversation_widget'):
            self.conversation_widget.add_message(
                "System", 
                "✅ Connection restored. Pending messages will be sent automatically."
            )
    
    def send_text_message(self, text: str, context: dict = None):
        """Send text message to server using enterprise system"""
        try:
            # Get parent main window
            main_window = self.window()
            if not hasattr(main_window, 'websocket_client'):
                logger.error("WebSocket client not available for text message")
                return
            
            # Initialize message sender if needed
            if not hasattr(self, 'message_sender'):
                self.message_sender = EnterpriseMessageSender(main_window.websocket_client)
                self._setup_message_sender_connections()
            
            # Prepare metadata for text message
            metadata = {
                "session_id": getattr(self, 'current_session_id', str(uuid.uuid4())),
                "device_id": "teddy_ui_client_text",
                "timestamp": datetime.now().isoformat(),
                "text_specs": {
                    "length": len(text),
                    "language": "auto",
                    "encoding": "utf-8",
                    "word_count": len(text.split())
                },
                "user_context": context or {
                    "input_method": "text_input",
                    "ui_version": "2.0.0"
                },
                "delivery_requirements": {
                    "priority": "normal",
                    "acknowledgment_required": True,
                    "timeout_seconds": 15
                },
                "conversation_context": {
                    "message_type": "user_text_input",
                    "expected_response": "ai_text_response",
                    "language": "auto_detect"
                }
            }
            
            # Send text message asynchronously
            asyncio.create_task(self._send_text_async(text, metadata))
            
        except Exception as e:
            logger.error("Failed to send text message", error=str(e))
            self.status_label.setText(f"❌ Text send failed: {e}")
    
    async def _send_text_async(self, text: str, metadata: dict):
        """Send text message asynchronously"""
        try:
            message_id = await self.message_sender.send_text_message(text, metadata)
            
            if message_id:
                self.current_message_id = message_id
                self.status_label.setText(f"📤 Text sent (ID: {message_id[:8]}...)")
                logger.info("Text message sent", message_id=message_id, text_length=len(text))
            else:
                self.status_label.setText("❌ Failed to send text")
                
        except Exception as e:
            logger.error("Failed to send text message", error=str(e))
            self.status_label.setText(f"❌ Text send failed: {e}")
    
    def get_message_sender_status(self) -> dict:
        """Get comprehensive status of message sender system"""
        if hasattr(self, 'message_sender'):
            main_window = self.window()
            return {
                "pending_messages": self.message_sender.get_pending_messages_count(),
                "connection_status": main_window.websocket_client.is_connected if hasattr(main_window, 'websocket_client') else False,
                "last_message_id": getattr(self, 'current_message_id', None),
                "current_session": getattr(self, 'current_session_id', None),
                "retry_queue_size": len(self.message_sender.retry_queue),
                "max_retry_attempts": self.message_sender.max_retry_attempts,
                "system_initialized": True
            }
        return {
            "system_initialized": False,
            "error": "Enterprise message sender not initialized"
        }
    
    def _reset_recording_state(self):
        """Reset recording UI state"""
        self.record_button.setText("🎤 Start Recording")
        self.record_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.stop_button.setEnabled(False)
        self.record_button.setEnabled(True)
        self.volume_meter.setValue(0)
        self.volume_label.setText("0%")
        
        # Reset waveform
        self.waveform_data = np.zeros(100)
        if hasattr(self, 'waveform_widget'):
            self.waveform_widget.update()
    
    def update_waveform(self):
        """Update waveform display with live audio data"""
        if self.is_recording:
            # Update volume meter
            self.volume_meter.setValue(int(self.volume_level))
            self.volume_label.setText(f"{int(self.volume_level)}%")
            
            # Update waveform widget
            if hasattr(self, 'waveform_widget'):
                self.waveform_widget.update_data(self.waveform_data)
    
    def update_recording_info(self):
        """Update recording duration and file size info"""
        if self.is_recording:
            duration = (datetime.now() - self.recording_start_time).total_seconds()
            minutes = int(duration // 60)
            seconds = int(duration % 60)
            self.duration_label.setText(f"{minutes}:{seconds:02d}")
            
            # Estimate file size
            estimated_size = len(self.audio_data) * 2 / 1024  # Rough estimate in KB
            self.file_size_label.setText(f"{estimated_size:.1f} KB")
    
    def test_audio_device(self):
        """Test the selected audio device"""
        try:
            self.status_label.setText("🔧 Testing audio device...")
            
            if SOUNDDEVICE_AVAILABLE:
                # Record a short test
                device_data = self.input_device_combo.currentData()
                device = device_data if device_data is not None else None
                
                test_duration = 1.0  # 1 second
                test_data = sd.rec(
                    int(test_duration * self.sample_rate),
                    samplerate=self.sample_rate,
                    channels=self.channels,
                    device=device
                )
                sd.wait()  # Wait for recording to complete
                
                # Check if we got any audio
                if np.max(np.abs(test_data)) > 0.001:
                    self.status_label.setText("✅ Audio device test successful")
                else:
                    self.status_label.setText("⚠️ Audio device test: very low signal")
                    
            else:
                self.status_label.setText("❌ Test requires SoundDevice library")
                
        except Exception as e:
            logger.error("Audio device test failed", error=str(e))
            self.status_label.setText(f"❌ Test failed: {e}")
        
        # Reset status after 3 seconds
        QTimer.singleShot(3000, lambda: self.status_label.setText("🟢 Audio system ready"))
    
    def test_processing_performance(self):
        """Test audio processing performance on current device"""
        try:
            self.status_label.setText("⚡ Testing processing performance...")
            self.performance_test_button.setEnabled(False)
            
            # Generate test audio signal (5 seconds of synthetic speech-like signal)
            test_duration = 5.0
            samples = int(test_duration * self.sample_rate)
            
            # Create synthetic audio with multiple frequency components
            t = np.linspace(0, test_duration, samples)
            
            # Simulate human speech with fundamental frequency around 120 Hz
            fundamental = 120  # Hz
            test_audio = (
                np.sin(2 * np.pi * fundamental * t) * 0.3 +          # Fundamental
                np.sin(2 * np.pi * fundamental * 2 * t) * 0.2 +       # 2nd harmonic
                np.sin(2 * np.pi * fundamental * 3 * t) * 0.1 +       # 3rd harmonic
                np.sin(2 * np.pi * 1500 * t) * 0.1 +                 # Formant
                np.random.normal(0, 0.05, samples)                   # Background noise
            )
            
            # Test all processing levels
            test_results = {}
            
            for level in ["low", "medium", "high"]:
                self.status_label.setText(f"⚡ Testing {level} level processing...")
                QApplication.processEvents()  # Update UI
                
                start_time = time.time()
                
                try:
                    # Test processing
                    processed_audio, proc_info = self.audio_processor.process_audio(
                        test_audio, level
                    )
                    
                    processing_time = time.time() - start_time
                    
                    test_results[level] = {
                        "success": True,
                        "processing_time": processing_time,
                        "steps_applied": proc_info.get("steps_applied", []),
                        "quality_improvement": proc_info.get("quality_improvement", {}),
                        "real_time_factor": processing_time / test_duration
                    }
                    
                except Exception as e:
                    test_results[level] = {
                        "success": False,
                        "error": str(e),
                        "processing_time": time.time() - start_time
                    }
            
            # Analyze results and provide recommendations
            self._display_performance_results(test_results, test_duration)
            
        except Exception as e:
            logger.error("Performance test failed", error=str(e))
            self.status_label.setText(f"❌ Performance test failed: {e}")
        
        finally:
            self.performance_test_button.setEnabled(True)
            # Reset status after 5 seconds
            QTimer.singleShot(5000, lambda: self.status_label.setText("🟢 Audio system ready"))
    
    def _display_performance_results(self, results: dict, test_duration: float):
        """Display performance test results"""
        # Calculate performance summary
        successful_levels = [level for level, data in results.items() if data.get("success", False)]
        
        if not successful_levels:
            self.status_label.setText("❌ All processing levels failed")
            return
        
        # Find best performance level
        best_level = None
        best_time = float('inf')
        
        performance_summary = []
        
        for level in ["low", "medium", "high"]:
            if level in successful_levels:
                data = results[level]
                proc_time = data["processing_time"]
                rt_factor = data["real_time_factor"]
                steps = len(data["steps_applied"])
                
                # Real-time capability assessment
                if rt_factor < 0.5:
                    capability = "Excellent"
                elif rt_factor < 1.0:
                    capability = "Good" 
                elif rt_factor < 2.0:
                    capability = "Acceptable"
                else:
                    capability = "Slow"
                
                performance_summary.append(
                    f"{level.title()}: {proc_time:.1f}s ({steps} steps) - {capability}"
                )
                
                if proc_time < best_time and rt_factor < 2.0:  # Must be reasonably fast
                    best_time = proc_time
                    best_level = level
        
        # Update processing level recommendation
        if best_level and best_level != self.processing_level:
            self.processing_level_combo.setCurrentText(best_level)
            self.update_processing_level(best_level)
        
        # Create detailed results message
        result_message = f"⚡ Performance Test Results:\n"
        result_message += "\n".join(performance_summary)
        
        if best_level:
            result_message += f"\n\n✅ Recommended: {best_level.title()} level"
        
        # Show results in a message box for detailed view
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Audio Processing Performance Test")
        msg_box.setText(result_message)
        msg_box.setDetailedText(self._format_detailed_results(results))
        msg_box.setIcon(QMessageBox.Information)
        msg_box.exec()
        
        # Update status
        if best_level:
            self.status_label.setText(f"✅ Performance test complete - Recommended: {best_level.title()}")
        else:
            self.status_label.setText("⚠️ Performance test complete - Check results")
        
        logger.info("Performance test completed", 
                   results=results, 
                   recommendation=best_level)
    
    def _format_detailed_results(self, results: dict) -> str:
        """Format detailed performance results"""
        detailed = "Detailed Performance Analysis:\n\n"
        
        system_info = self.audio_processor.get_processing_capabilities()
        detailed += f"System Performance Mode: {system_info['performance_mode'].title()}\n"
        detailed += f"Available Libraries:\n"
        detailed += f"  - LibROSA: {'✅' if system_info['librosa_available'] else '❌'}\n"
        detailed += f"  - NoiseReduce: {'✅' if system_info['noisereduce_available'] else '❌'}\n"
        detailed += f"  - SciPy: {'✅' if system_info['scipy_available'] else '❌'}\n\n"
        
        for level, data in results.items():
            detailed += f"{level.upper()} LEVEL:\n"
            
            if data.get("success", False):
                detailed += f"  Processing Time: {data['processing_time']:.2f}s\n"
                detailed += f"  Real-time Factor: {data['real_time_factor']:.2f}x\n"
                detailed += f"  Steps Applied: {', '.join(data['steps_applied'])}\n"
                
                quality = data.get('quality_improvement', {})
                if quality and 'rms_ratio' in quality:
                    detailed += f"  Quality Metrics:\n"
                    detailed += f"    - RMS Improvement: {quality['rms_ratio']:.2f}x\n"
                    if 'dynamic_range_improvement' in quality:
                        detailed += f"    - Dynamic Range: {quality['dynamic_range_improvement']:.2f}x\n"
            else:
                detailed += f"  FAILED: {data.get('error', 'Unknown error')}\n"
                
            detailed += "\n"
        
        return detailed
    
    def get_audio_system_info(self) -> dict:
        """Get detailed audio system information"""
        info = {
            "sounddevice_available": SOUNDDEVICE_AVAILABLE,
            "pyaudio_available": PYAUDIO_AVAILABLE,
            "sample_rate": self.sample_rate,
            "channels": self.channels,
            "chunk_size": self.chunk_size,
            "recording_active": self.is_recording
        }
        
        if SOUNDDEVICE_AVAILABLE:
            try:
                devices = sd.query_devices()
                info["available_devices"] = len(devices)
                info["default_device"] = sd.default.device
            except:
                info["device_query_error"] = True
        
        return info
    
    def closeEvent(self, event):
        """Cleanup on widget close"""
        if self.is_recording:
            self.stop_recording()
        
        if self.pyaudio_instance:
            self.pyaudio_instance.terminate()
        
        super().closeEvent(event)


class WaveformWidget(QWidget):
    """Custom widget for displaying live audio waveform"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.waveform_data = np.zeros(100)
        self.setMinimumHeight(100)
        
    def update_data(self, data):
        """Update waveform data and redraw"""
        self.waveform_data = data
        self.update()
    
    def paintEvent(self, event):
        """Draw the waveform"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Background
        painter.fillRect(self.rect(), QColor(248, 249, 250))
        
        # Border
        painter.setPen(QPen(QColor(224, 224, 224), 1))
        painter.drawRect(self.rect())
        
        if len(self.waveform_data) == 0:
            return
        
        # Draw waveform
        width = self.width() - 20
        height = self.height() - 20
        center_y = height // 2 + 10
        
        # Normalize data
        if np.max(np.abs(self.waveform_data)) > 0:
            normalized_data = self.waveform_data / np.max(np.abs(self.waveform_data))
        else:
            normalized_data = self.waveform_data
        
        # Draw waveform line
        painter.setPen(QPen(QColor(76, 175, 80), 2))
        
        points = []
        for i, sample in enumerate(normalized_data[-width:]):
            x = int(10 + (i / len(normalized_data[-width:])) * width)
            y = int(center_y - (sample * height * 0.4))
            points.append(QPoint(x, y))
        
        if len(points) > 1:
            for i in range(len(points) - 1):
                painter.drawLine(points[i], points[i + 1])
        
        # Draw center line
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        painter.drawLine(10, center_y, width + 10, center_y)


class ConversationWidget(QWidget):
    """Modern conversation display widget"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.conversation_history = []
        
    def setup_ui(self):
        """Setup conversation UI"""
        layout = QVBoxLayout(self)
        
        # Conversation display
        self.conversation_text = QTextEdit()
        self.conversation_text.setReadOnly(True)
        self.conversation_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 12px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
                line-height: 1.4;
            }
        """)
        
        layout.addWidget(QLabel("Conversation History:"))
        layout.addWidget(self.conversation_text)
        
        # Input area
        input_group = QGroupBox("Send Message")
        input_layout = QHBoxLayout(input_group)
        
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Type your message here...")
        self.message_input.setMinimumHeight(40)
        self.message_input.returnPressed.connect(self.send_message)
        
        self.send_button = QPushButton("Send")
        self.send_button.setMinimumHeight(40)
        self.send_button.setMinimumWidth(80)
        self.send_button.clicked.connect(self.send_message)
        
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)
        
        layout.addWidget(input_group)
    
    def add_message(self, sender: str, message: str, timestamp: Optional[datetime] = None):
        """Add message to conversation"""
        if timestamp is None:
            timestamp = datetime.now()
        
        time_str = timestamp.strftime("%H:%M:%S")
        
        # Add to history
        self.conversation_history.append({
            "sender": sender,
            "message": message,
            "timestamp": timestamp
        })
        
        # Format message
        if sender == "User":
            formatted = f'<div style="margin: 8px 0; padding: 8px; background-color: #e3f2fd; border-radius: 8px; text-align: right;"><strong>{sender}</strong> <span style="color: #666;">({time_str})</span><br>{message}</div>'
        else:
            formatted = f'<div style="margin: 8px 0; padding: 8px; background-color: #f1f8e9; border-radius: 8px;"><strong>{sender}</strong> <span style="color: #666;">({time_str})</span><br>{message}</div>'
        
        # Add to display
        self.conversation_text.append(formatted)
        
        # Scroll to bottom
        cursor = self.conversation_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.conversation_text.setTextCursor(cursor)
    
    def send_message(self):
        """Send user message to backend server"""
        message = self.message_input.text().strip()
        if message:
            self.add_message("User", message)
            self.message_input.clear()
            
            # Send message to backend via WebSocket
            self._send_message_to_server(message)
            
            logger.info("User message sent", message=message)
    
    def _send_message_to_server(self, message: str):
        """Send text message to server via enterprise WebSocket system"""
        try:
            # Get parent main window to access WebSocket client
            main_window = self.window()
            if not hasattr(main_window, 'websocket_client'):
                self.add_message("System", "❌ No connection to server available")
                logger.error("WebSocket client not available for text message")
                return
            
            # Find audio widget to use its message sender
            audio_widget = None
            for widget in main_window.findChildren(ModernAudioWidget):
                if hasattr(widget, 'message_sender'):
                    audio_widget = widget
                    break
            
            if audio_widget:
                # Use existing message sender
                audio_widget.send_text_message(message, {
                    "source": "conversation_widget",
                    "conversation_context": True
                })
                self.add_message("System", "📤 Message sent via voice system")
            else:
                # Fallback to direct WebSocket (legacy)
                server_message = {
                    "type": "text_message",
                    "device_id": "UI_CLIENT_CONVERSATION", 
                    "message": message,
                    "timestamp": datetime.now().isoformat(),
                    "language": "auto",  # Auto-detect language
                    "source": "conversation_widget"
                }
                
                # Send via WebSocket
                success = main_window.websocket_client.send_message(server_message)
                if success:
                    self.add_message("System", "📤 Message sent (legacy mode)")
                else:
                    self.add_message("System", "❌ Failed to send message")
                
        except Exception as e:
            logger.error("Failed to send text message from conversation", error=str(e))
            self.add_message("System", f"❌ Send error: {e}")


class TeddyMainWindow(QMainWindow):
    """Main window for AI Teddy Bear application"""
    
    def __init__(self):
        super().__init__()
        self.websocket_client = WebSocketClient(self)
        self.settings = QSettings("AI Teddy", "TeddyBear")
        self.setup_ui()
        self.setup_connections()
        self.setup_system_tray()
        self.restore_window_state()
        
        # Connect to server on startup
        QTimer.singleShot(1000, self.websocket_client.connect_to_server)
    
    def setup_ui(self):
        """Setup main UI"""
        self.setWindowTitle("AI Teddy Bear - Enterprise Control Panel")
        self.setMinimumSize(1200, 800)
        
        # Apply modern styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #fafafa;
            }
            QTabWidget::pane {
                border: 1px solid #e0e0e0;
                background-color: white;
                border-radius: 8px;
            }
            QTabBar::tab {
                background-color: #f5f5f5;
                border: 1px solid #e0e0e0;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 1px solid white;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 8px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
            }
        """)
        
        # Central widget with tabs
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # Dashboard tab with Enterprise features
        try:
            from .enterprise_dashboard import EnterpriseDashboardWidget
            self.dashboard_widget = EnterpriseDashboardWidget()
            self.dashboard_widget.alert_triggered.connect(self._handle_dashboard_alert)
            self.dashboard_widget.emotion_detected.connect(self._handle_emotion_detection)
            logger.info("Enterprise dashboard loaded successfully")
        except ImportError:
            # Fallback to basic dashboard
            self.dashboard_widget = ModernDashboardWidget()
            logger.warning("Using basic dashboard - enterprise features not available")
        
        self.tab_widget.addTab(self.dashboard_widget, "📊 Enterprise Dashboard")
        
        # Audio tab
        self.audio_widget = ModernAudioWidget()
        self.tab_widget.addTab(self.audio_widget, "🎤 Audio")
        
        # Conversation tab
        self.conversation_widget = ConversationWidget()
        self.tab_widget.addTab(self.conversation_widget, "💬 Conversation")
        
        # Settings tab
        self.settings_widget = self.create_settings_widget()
        self.tab_widget.addTab(self.settings_widget, "⚙️ Settings")
        
        layout.addWidget(self.tab_widget)
        
        # Setup menu bar
        self.create_menu_bar()
        
        # Enterprise dashboard event handlers
        self.setup_enterprise_dashboard_handlers()
        
        # Setup status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.connection_status_label = QLabel("Disconnected")
        self.status_bar.addPermanentWidget(self.connection_status_label)
    
    def create_settings_widget(self) -> QWidget:
        """Create settings widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Server settings
        server_group = QGroupBox("Server Configuration")
        server_layout = QGridLayout(server_group)
        
        server_layout.addWidget(QLabel("Server URL:"), 0, 0)
        self.server_url_input = QLineEdit("ws://localhost:8000")
        server_layout.addWidget(self.server_url_input, 0, 1)
        
        server_layout.addWidget(QLabel("API Key:"), 1, 0)
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        server_layout.addWidget(self.api_key_input, 1, 1)
        
        layout.addWidget(server_group)
        
        # Audio settings
        audio_group = QGroupBox("Audio Configuration")
        audio_layout = QGridLayout(audio_group)
        
        audio_layout.addWidget(QLabel("Sample Rate:"), 0, 0)
        self.sample_rate_combo = QComboBox()
        self.sample_rate_combo.addItems(["16000", "22050", "44100", "48000"])
        audio_layout.addWidget(self.sample_rate_combo, 0, 1)
        
        audio_layout.addWidget(QLabel("Channels:"), 1, 0)
        self.channels_combo = QComboBox()
        self.channels_combo.addItems(["1 (Mono)", "2 (Stereo)"])
        audio_layout.addWidget(self.channels_combo, 1, 1)
        
        layout.addWidget(audio_group)
        
        # UI settings
        ui_group = QGroupBox("UI Preferences")
        ui_layout = QGridLayout(ui_group)
        
        self.dark_mode_checkbox = QCheckBox("Dark Mode")
        ui_layout.addWidget(self.dark_mode_checkbox, 0, 0)
        
        self.auto_connect_checkbox = QCheckBox("Auto-connect on startup")
        ui_layout.addWidget(self.auto_connect_checkbox, 1, 0)
        
        self.minimize_to_tray_checkbox = QCheckBox("Minimize to system tray")
        ui_layout.addWidget(self.minimize_to_tray_checkbox, 2, 0)
        
        layout.addWidget(ui_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_button = QPushButton("Save Settings")
        save_button.clicked.connect(self.save_settings)
        
        reset_button = QPushButton("Reset to Defaults")
        reset_button.clicked.connect(self.reset_settings)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(reset_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        return widget
    
    def create_menu_bar(self):
        """Create application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        connect_action = QAction("Connect to Server", self)
        connect_action.triggered.connect(self.websocket_client.connect_to_server)
        file_menu.addAction(connect_action)
        
        disconnect_action = QAction("Disconnect", self)
        disconnect_action.triggered.connect(self.websocket_client.disconnect_from_server)
        file_menu.addAction(disconnect_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        fullscreen_action = QAction("Toggle Fullscreen", self)
        fullscreen_action.setShortcut("F11")
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(fullscreen_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_connections(self):
        """Setup signal connections"""
        # WebSocket connections
        self.websocket_client.connected.connect(self.on_connected)
        self.websocket_client.disconnected.connect(self.on_disconnected)
        self.websocket_client.message_received.connect(self.on_message_received)
        self.websocket_client.error_occurred.connect(self.on_error)
        self.websocket_client.connection_status_changed.connect(self.update_connection_status)
    
    def setup_system_tray(self):
        """Setup system tray icon"""
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = QSystemTrayIcon(self)
            
            # Set icon (you would use a real icon file)
            icon = self.style().standardIcon(QStyle.SP_ComputerIcon)
            self.tray_icon.setIcon(icon)
            
            # Create tray menu
            tray_menu = self.tray_icon.contextMenu() or self.tray_icon.setContextMenu(self.create_tray_menu())
            
            self.tray_icon.show()
            self.tray_icon.messageClicked.connect(self.show)
    
    def create_tray_menu(self):
        """Create system tray menu"""
        from PySide6.QtWidgets import QMenu
        
        menu = QMenu()
        
        show_action = menu.addAction("Show")
        show_action.triggered.connect(self.show)
        
        hide_action = menu.addAction("Hide")
        hide_action.triggered.connect(self.hide)
        
        menu.addSeparator()
        
        quit_action = menu.addAction("Quit")
        quit_action.triggered.connect(QApplication.quit)
        
        return menu
    
    def on_connected(self):
        """Handle WebSocket connection"""
        self.status_bar.showMessage("Connected to server", 3000)
        logger.info("UI connected to server")
    
    def on_disconnected(self):
        """Handle WebSocket disconnection"""
        self.status_bar.showMessage("Disconnected from server", 3000)
        logger.warning("UI disconnected from server")
    
    def on_message_received(self, message: dict):
        """Handle received WebSocket message and update UI immediately"""
        message_type = message.get("type")
        
        # Update enterprise dashboard with server data
        self.update_dashboard_with_server_data(message)
        
        if message_type == "response" or message_type == "ai_response":
            # Add AI response to conversation
            text = message.get("text", "")
            if text:
                self.conversation_widget.add_message("AI Teddy", text)
                self.status_bar.showMessage("✅ AI response received", 2000)
        
        elif message_type == "audio_response":
            # Handle audio processing response
            text = message.get("text", "")
            emotions = message.get("emotions", [])
            analytics = message.get("analytics", {})
            
            if text:
                self.conversation_widget.add_message("AI Teddy", text)
            
            # Update dashboard with emotion data
            if emotions:
                self._update_emotion_display(emotions)
            
            # Update analytics
            if analytics:
                self._update_analytics_display(analytics)
                
            self.status_bar.showMessage("✅ Audio processed successfully", 3000)
        
        elif message_type == "system_status":
            # Update dashboard metrics immediately
            status_data = message.get("data", {})
            self._update_dashboard_metrics(status_data)
            
        elif message_type == "emotion_analysis":
            # Real-time emotion updates
            emotions = message.get("emotions", [])
            confidence = message.get("confidence", 0)
            self._update_emotion_display(emotions, confidence)
            
        elif message_type == "analytics_update":
            # Real-time analytics updates
            analytics = message.get("data", {})
            self._update_analytics_display(analytics)
            
        elif message_type == "device_status":
            # Device connection status
            device_id = message.get("device_id", "")
            status = message.get("status", "")
            self._update_device_status(device_id, status)
            
        elif message_type == "notification":
            # System notifications
            notification = message.get("message", "")
            level = message.get("level", "info")
            self._show_notification(notification, level)
            
        elif message_type == "error":
            error_msg = message.get("message", "Unknown error")
            self.status_bar.showMessage(f"❌ Error: {error_msg}", 5000)
            logger.error("Server error received", message=error_msg)
            
        else:
            logger.debug("Unknown message type received", type=message_type)
    
    def _update_dashboard_metrics(self, status_data: dict):
        """Update dashboard metrics with real-time data"""
        try:
            # Update dashboard widget metrics
            if hasattr(self.dashboard_widget, 'sessions_label'):
                sessions = status_data.get("active_sessions", 0)
                self.dashboard_widget.sessions_label.setText(str(sessions))
            
            if hasattr(self.dashboard_widget, 'messages_label'):
                messages = status_data.get("messages_processed", 0)
                self.dashboard_widget.messages_label.setText(str(messages))
            
            if hasattr(self.dashboard_widget, 'health_progress'):
                health = status_data.get("system_health", 100)
                self.dashboard_widget.health_progress.setValue(health)
            
            # Update performance chart if available
            response_time = status_data.get("avg_response_time", 0)
            if response_time > 0:
                self._update_performance_chart(response_time)
                
            logger.debug("Dashboard metrics updated", data=status_data)
            
        except Exception as e:
            logger.error("Failed to update dashboard metrics", error=str(e))
    
    def _update_emotion_display(self, emotions: list, confidence: float = 0):
        """Update emotion visualization"""
        try:
            # Format emotion data for display
            emotion_text = "Recent Emotions:\n"
            for emotion in emotions[:5]:  # Show top 5 emotions
                name = emotion.get("name", "Unknown")
                score = emotion.get("score", 0)
                emotion_text += f"• {name}: {score:.1%}\n"
            
            if confidence > 0:
                emotion_text += f"\nConfidence: {confidence:.1%}"
            
            # Add to conversation as system message
            self.conversation_widget.add_message("Emotion Analysis", emotion_text)
            
            # Update status bar
            if emotions:
                dominant_emotion = emotions[0].get("name", "neutral")
                self.status_bar.showMessage(f"😊 Emotion detected: {dominant_emotion}", 3000)
                
        except Exception as e:
            logger.error("Failed to update emotion display", error=str(e))
    
    def _update_analytics_display(self, analytics: dict):
        """Update analytics information"""
        try:
            # Extract analytics data
            total_interactions = analytics.get("total_interactions", 0)
            session_duration = analytics.get("session_duration", 0)
            topics_discussed = analytics.get("topics", [])
            
            # Create analytics summary
            analytics_text = f"Session Analytics:\n"
            analytics_text += f"• Total interactions: {total_interactions}\n"
            analytics_text += f"• Session duration: {session_duration:.1f}s\n"
            
            if topics_discussed:
                analytics_text += f"• Topics: {', '.join(topics_discussed[:3])}\n"
            
            # Add to conversation as system message
            self.conversation_widget.add_message("Analytics", analytics_text)
            
            logger.debug("Analytics updated", data=analytics)
            
        except Exception as e:
            logger.error("Failed to update analytics display", error=str(e))
    
    def _update_device_status(self, device_id: str, status: str):
        """Update device connection status"""
        try:
            status_message = f"Device {device_id}: {status}"
            self.status_bar.showMessage(status_message, 3000)
            
            # Update connection indicator if it's the main device
            if "ESP32" in device_id or "DEMO" in device_id:
                color = "green" if status == "connected" else "orange"
                self.connection_status_label.setStyleSheet(f"color: {color};")
                
        except Exception as e:
            logger.error("Failed to update device status", error=str(e))
    
    def _show_notification(self, message: str, level: str):
        """Show system notification"""
        try:
            # Map level to colors and icons
            level_config = {
                "info": ("ℹ️", "blue"),
                "warning": ("⚠️", "orange"), 
                "error": ("❌", "red"),
                "success": ("✅", "green")
            }
            
            icon, color = level_config.get(level, ("ℹ️", "blue"))
            
            # Show in status bar
            self.status_bar.showMessage(f"{icon} {message}", 5000)
            
            # Add to conversation
            self.conversation_widget.add_message("System", f"{icon} {message}")
            
            logger.info("Notification shown", message=message, level=level)
            
        except Exception as e:
            logger.error("Failed to show notification", error=str(e))
    
    def _update_performance_chart(self, response_time: float):
        """Update performance chart with new data point"""
        try:
            # This would update the chart in the dashboard
            # Implementation depends on the chart library being used
            if hasattr(self.dashboard_widget, 'chart_view'):
                # Add new data point to performance chart
                chart = self.dashboard_widget.chart_view.chart()
                if chart and chart.series():
                    series = chart.series()[0]
                    
                    # Add new point
                    current_time = datetime.now().timestamp()
                    series.append(current_time, response_time)
                    
                    # Keep only last 20 points
                    if series.count() > 20:
                        series.remove(0)
                    
                    # Update axes
                    chart.axes()[0].setRange(
                        series.at(0).x(), 
                        series.at(series.count()-1).x()
                    )
                    
        except Exception as e:
            logger.error("Failed to update performance chart", error=str(e))
    
    def on_error(self, error: str):
        """Handle WebSocket error"""
        self.status_bar.showMessage(f"Connection error: {error}", 5000)
        logger.error("WebSocket error", error=error)
    
    def update_connection_status(self, status: str):
        """Update connection status display"""
        self.connection_status_label.setText(status)
        self.dashboard_widget.update_connection_status(status)
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About AI Teddy Bear",
            """
            <h3>AI Teddy Bear Enterprise</h3>
            <p>Version 2.0.0</p>
            <p>Modern, secure AI assistant for children</p>
            <p>Built with PySide6 and FastAPI</p>
            <p>© 2025 AI Teddy Team</p>
            """
        )
    
    def save_settings(self):
        """Save application settings"""
        self.settings.setValue("server_url", self.server_url_input.text())
        self.settings.setValue("api_key", self.api_key_input.text())
        self.settings.setValue("sample_rate", self.sample_rate_combo.currentText())
        self.settings.setValue("channels", self.channels_combo.currentIndex())
        self.settings.setValue("dark_mode", self.dark_mode_checkbox.isChecked())
        self.settings.setValue("auto_connect", self.auto_connect_checkbox.isChecked())
        self.settings.setValue("minimize_to_tray", self.minimize_to_tray_checkbox.isChecked())
        
        self.status_bar.showMessage("Settings saved", 2000)
        logger.info("Application settings saved")
    
    def reset_settings(self):
        """Reset settings to defaults"""
        self.server_url_input.setText("ws://localhost:8000")
        self.api_key_input.clear()
        self.sample_rate_combo.setCurrentText("16000")
        self.channels_combo.setCurrentIndex(0)
        self.dark_mode_checkbox.setChecked(False)
        self.auto_connect_checkbox.setChecked(True)
        self.minimize_to_tray_checkbox.setChecked(True)
        
        self.status_bar.showMessage("Settings reset to defaults", 2000)
    
    def save_window_state(self):
        """Save window state"""
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
    
    def restore_window_state(self):
        """Restore window state"""
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        
        window_state = self.settings.value("windowState")
        if window_state:
            self.restoreState(window_state)
    
    def setup_enterprise_dashboard_handlers(self):
        """Setup enterprise dashboard event handlers"""
        if hasattr(self.dashboard_widget, 'alert_triggered'):
            # Dashboard already connected in setup_ui
            logger.info("Enterprise dashboard handlers configured")
        else:
            logger.warning("Dashboard does not support enterprise features")
    
    def _handle_dashboard_alert(self, alert_type: str, message: str, data: dict):
        """Handle smart alert from enterprise dashboard"""
        try:
            # Show in status bar
            self.status_bar.showMessage(f"🚨 ALERT: {message}", 10000)
            
            # Add to conversation for visibility
            timestamp = datetime.now().strftime("%H:%M:%S")
            alert_message = f"🚨 [{timestamp}] PARENTAL ALERT\n{message}"
            self.conversation_widget.add_message("Smart Alert System", alert_message)
            
            # Log for analysis
            logger.warning("Parental alert triggered", 
                          type=alert_type, 
                          message=message, 
                          data=data)
            
            # Show system tray notification if available
            if hasattr(self, 'tray_icon') and self.tray_icon.isVisible():
                self.tray_icon.showMessage(
                    "AI Teddy - Parental Alert",
                    message,
                    QSystemTrayIcon.Warning,
                    5000
                )
            
            # Send alert to backend for parent notification
            if hasattr(self, 'websocket_client') and self.websocket_client.is_connected:
                alert_data = {
                    "type": "parental_alert",
                    "alert_type": alert_type,
                    "message": message,
                    "data": data,
                    "timestamp": datetime.now().isoformat(),
                    "severity": data.get("priority", "medium")
                }
                self.websocket_client.send_message(alert_data)
                
        except Exception as e:
            logger.error("Failed to handle dashboard alert", error=str(e))
    
    def _handle_emotion_detection(self, emotions: list, confidence: float):
        """Handle emotion detection from enterprise dashboard"""
        try:
            if not emotions:
                return
            
            # Get dominant emotion
            dominant_emotion = emotions[0] if isinstance(emotions[0], dict) else {"emotion": emotions[0], "confidence": confidence}
            
            # Update main window UI based on emotion
            self._update_ui_for_emotion(dominant_emotion)
            
            # Send emotion data to backend
            if hasattr(self, 'websocket_client') and self.websocket_client.is_connected:
                emotion_data = {
                    "type": "emotion_detected",
                    "emotions": emotions,
                    "confidence": confidence,
                    "timestamp": datetime.now().isoformat(),
                    "source": "enterprise_dashboard"
                }
                self.websocket_client.send_message(emotion_data)
            
            logger.info("Emotion processed by main window", 
                       emotion=dominant_emotion.get("emotion"),
                       confidence=confidence)
                       
        except Exception as e:
            logger.error("Failed to handle emotion detection", error=str(e))
    
    def _update_ui_for_emotion(self, emotion_data: dict):
        """Update UI elements based on detected emotion"""
        try:
            emotion = emotion_data.get("emotion", "neutral")
            confidence = emotion_data.get("confidence", 0)
            
            # Update window title with emotion indicator
            base_title = "AI Teddy Bear - Enterprise Control Panel"
            emotion_emojis = {
                "happy": "😊", "excited": "🤩", "calm": "😌", "curious": "🤔",
                "frustrated": "😤", "sad": "😢", "angry": "😠", "neutral": "😐"
            }
            
            emoji = emotion_emojis.get(emotion, "😐")
            self.setWindowTitle(f"{base_title} {emoji}")
            
            # Update status bar with emotion info
            confidence_percent = int(confidence * 100)
            self.status_bar.showMessage(
                f"Current Emotion: {emoji} {emotion.title()} ({confidence_percent}%)", 
                3000
            )
            
        except Exception as e:
            logger.error("Failed to update UI for emotion", error=str(e))
    
    def update_dashboard_with_server_data(self, message: dict):
        """Update enterprise dashboard with real server data"""
        try:
            if hasattr(self.dashboard_widget, 'add_emotion_data'):
                # Extract emotion data from server message
                if message.get("type") == "emotion_analysis":
                    emotions = message.get("emotions", [])
                    if emotions:
                        dominant = emotions[0]
                        emotion_name = dominant.get("name", "neutral")
                        confidence = dominant.get("confidence", 0)
                        
                        # Add to enterprise dashboard
                        self.dashboard_widget.add_emotion_data(emotion_name, confidence)
                
                elif message.get("type") == "audio_response":
                    # Extract emotion from AI response
                    payload = message.get("payload", {})
                    emotions = payload.get("emotions", [])
                    
                    if emotions:
                        for emotion in emotions[:1]:  # Process first emotion
                            emotion_name = emotion.get("name", "neutral") 
                            confidence = emotion.get("confidence", 0)
                            
                            self.dashboard_widget.add_emotion_data(emotion_name, confidence)
                
                elif message.get("type") == "child_profile_update":
                    # Add child profile
                    child_data = message.get("child_data", {})
                    if child_data:
                        name = child_data.get("name", "Unknown")
                        age = child_data.get("age", 0)
                        self.dashboard_widget.add_child_profile(name, age, child_data)
                        
        except Exception as e:
            logger.error("Failed to update dashboard with server data", error=str(e))
    
    def closeEvent(self, event):
        """Handle close event"""
        if hasattr(self, 'tray_icon') and self.minimize_to_tray_checkbox.isChecked():
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                "AI Teddy Bear",
                "Application was minimized to tray",
                QSystemTrayIcon.Information,
                2000
            )
        else:
            self.save_window_state()
            self.websocket_client.disconnect_from_server()
            event.accept()


class ModernTeddyUI:
    """Main UI application class"""
    
    def __init__(self):
        self.app = None
        self.main_window = None
    
    def run(self):
        """Run the application"""
        # Create QApplication
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("AI Teddy Bear")
        self.app.setApplicationVersion("2.0.0")
        self.app.setOrganizationName("AI Teddy Team")
        
        # Set application icon
        # icon = QIcon("path/to/teddy_icon.png")  # Use actual icon file
        # self.app.setWindowIcon(icon)
        
        # Apply modern styling
        self.apply_modern_theme()
        
        # Create main window
        self.main_window = TeddyMainWindow()
        self.main_window.show()
        
        # Setup exception handling
        sys.excepthook = self.handle_exception
        
        # Run application
        try:
            sys.exit(self.app.exec())
        except SystemExit:
            pass
    
    def apply_modern_theme(self):
        """Apply modern theme to application"""
        style = """
        QApplication {
            font-family: 'Segoe UI', 'Arial', sans-serif;
            font-size: 10pt;
        }
        
        QPushButton {
            background-color: #2196F3;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }
        
        QPushButton:hover {
            background-color: #1976D2;
        }
        
        QPushButton:pressed {
            background-color: #0D47A1;
        }
        
        QPushButton:disabled {
            background-color: #BBBBBB;
            color: #666666;
        }
        
        QLineEdit {
            border: 2px solid #E0E0E0;
            border-radius: 4px;
            padding: 8px;
            font-size: 10pt;
        }
        
        QLineEdit:focus {
            border-color: #2196F3;
        }
        
        QComboBox {
            border: 2px solid #E0E0E0;
            border-radius: 4px;
            padding: 8px;
            font-size: 10pt;
        }
        
        QTextEdit {
            border: 2px solid #E0E0E0;
            border-radius: 4px;
            padding: 8px;
            font-size: 10pt;
        }
        """
        
        self.app.setStyleSheet(style)
    
    def handle_exception(self, exc_type, exc_value, exc_traceback):
        """Handle uncaught exceptions"""
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        logger.error("Uncaught exception", 
                    exc_type=exc_type.__name__,
                    exc_value=str(exc_value),
                    exc_info=(exc_type, exc_value, exc_traceback))
        
        # Show error dialog
        if self.main_window:
            QMessageBox.critical(
                self.main_window,
                "Unexpected Error",
                f"An unexpected error occurred:\n\n{exc_type.__name__}: {exc_value}"
            )


def main():
    """Main entry point"""
    try:
        ui = ModernTeddyUI()
        ui.run()
    except Exception as e:
        logger.error("Failed to start UI application", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    main() 