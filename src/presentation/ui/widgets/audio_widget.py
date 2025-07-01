"""
Modern Audio Widget for AI Teddy Bear
Comprehensive audio interface with recording, processing, and visualization
"""

import asyncio
from datetime import datetime
from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QGridLayout,
    QPushButton, QLabel, QComboBox, QProgressBar, QCheckBox
)
from PySide6.QtCore import Signal, QTimer, pyqtSlot
from PySide6.QtGui import QFont

from ..audio.audio_config import AudioConfig
from ..audio.audio_recorder import AudioRecorder
from ..audio.audio_engine import AudioProcessingEngine
from .waveform_widget import WaveformWidget

import structlog

logger = structlog.get_logger()


class ModernAudioWidget(QWidget):
    """Modern audio interface widget with professional capabilities"""
    
    audio_recorded = Signal(bytes)
    audio_level_changed = Signal(float)
    recording_status_changed = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.message_sender = None
        self._setup_components()
        self._setup_ui()
        self._setup_timers()
    
    def _setup_components(self) -> Any:
        """Initialize audio components"""
        self.config = AudioConfig()
        self.recorder = AudioRecorder(self.config)
        self.audio_processor = AudioProcessingEngine(sample_rate=self.config.sample_rate)
        
        # Waveform visualization
        self.waveform_widget = WaveformWidget()
    
    def _setup_ui(self) -> Any:
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        
        # Device configuration
        layout.addWidget(self._create_device_group())
        
        # Processing configuration  
        layout.addWidget(self._create_processing_group())
        
        # Recording controls
        layout.addWidget(self._create_controls_group())
        
        # Visualization
        layout.addWidget(self._create_visualization_group())
        
        # Status information
        layout.addWidget(self._create_status_group())
    
    def _create_device_group(self) -> QGroupBox:
        """Create device configuration group"""
        group = QGroupBox("Audio Device Configuration")
        layout = QGridLayout(group)
        
        # Input device selection
        layout.addWidget(QLabel("Input Device:"), 0, 0)
        self.input_device_combo = QComboBox()
        self._populate_audio_devices()
        layout.addWidget(self.input_device_combo, 0, 1)
        
        # Sample rate selection
        layout.addWidget(QLabel("Sample Rate:"), 1, 0)
        self.sample_rate_combo = QComboBox()
        self.sample_rate_combo.addItems(["16000", "22050", "44100", "48000"])
        self.sample_rate_combo.setCurrentText("16000")
        self.sample_rate_combo.currentTextChanged.connect(self._update_sample_rate)
        layout.addWidget(self.sample_rate_combo, 1, 1)
        
        return group
    
    def _create_processing_group(self) -> QGroupBox:
        """Create audio processing group"""
        group = QGroupBox("Audio Processing & Enhancement")
        layout = QGridLayout(group)
        
        # Enable processing toggle
        layout.addWidget(QLabel("Enable Processing:"), 0, 0)
        self.enable_processing_checkbox = QCheckBox("Enhanced Audio Processing")
        self.enable_processing_checkbox.setChecked(True)
        self.enable_processing_checkbox.toggled.connect(self._toggle_processing)
        layout.addWidget(self.enable_processing_checkbox, 0, 1)
        
        # Processing level
        layout.addWidget(QLabel("Processing Level:"), 1, 0)
        self.processing_level_combo = QComboBox()
        self.processing_level_combo.addItems(["auto", "low", "medium", "high"])
        self.processing_level_combo.currentTextChanged.connect(self._update_processing_level)
        layout.addWidget(self.processing_level_combo, 1, 1)
        
        return group
    
    def _create_controls_group(self) -> QGroupBox:
        """Create recording controls group"""
        group = QGroupBox("Recording Controls")
        layout = QHBoxLayout(group)
        
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
            QPushButton:hover { background-color: #1976D2; }
        """)
        self.record_button.clicked.connect(self._toggle_recording)
        
        self.stop_button = QPushButton("⏹️ Stop")
        self.stop_button.setMinimumHeight(60)
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self._stop_recording)
        
        layout.addWidget(self.record_button)
        layout.addWidget(self.stop_button)
        
        return group
    
    def _create_visualization_group(self) -> QGroupBox:
        """Create visualization group"""
        group = QGroupBox("Live Audio Visualization")
        layout = QVBoxLayout(group)
        
        # Volume meter
        volume_layout = QHBoxLayout()
        volume_layout.addWidget(QLabel("Volume:"))
        
        self.volume_meter = QProgressBar()
        self.volume_meter.setRange(0, 100)
        volume_layout.addWidget(self.volume_meter)
        
        self.volume_label = QLabel("0%")
        self.volume_label.setMinimumWidth(40)
        volume_layout.addWidget(self.volume_label)
        
        layout.addLayout(volume_layout)
        
        # Waveform
        layout.addWidget(QLabel("Live Waveform:"))
        layout.addWidget(self.waveform_widget)
        
        return group
    
    def _create_status_group(self) -> QGroupBox:
        """Create status information group"""
        group = QGroupBox("Recording Information")
        layout = QGridLayout(group)
        
        self.status_label = QLabel("Ready to record")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(self.status_label, 0, 0, 1, 2)
        
        layout.addWidget(QLabel("Duration:"), 1, 0)
        self.duration_label = QLabel("0:00")
        layout.addWidget(self.duration_label, 1, 1)
        
        return group
    
    def _setup_timers(self) -> Any:
        """Setup update timers"""
        self.visualization_timer = QTimer()
        self.visualization_timer.timeout.connect(self._update_visualization)
        
        self.recording_timer = QTimer()
        self.recording_timer.timeout.connect(self._update_recording_info)
    
    def _populate_audio_devices(self) -> Any:
        """Populate audio device list"""
        self.input_device_combo.clear()
        devices = self.config.get_audio_devices()
        
        for device in devices:
            self.input_device_combo.addItem(device['name'], device['id'])
    
    def _update_sample_rate(str) -> None:
        """Update sample rate"""
        try:
            rate = int(rate_text)
            self.config.update_sample_rate(rate)
            self.audio_processor = AudioProcessingEngine(sample_rate=rate)
        except ValueError:
            logger.error("Invalid sample rate", rate=rate_text)
    
    def _toggle_processing(bool) -> None:
        """Toggle audio processing"""
        self.config.enable_processing = enabled
        self.processing_level_combo.setEnabled(enabled)
    
    def _update_processing_level(str) -> None:
        """Update processing level"""
        self.config.processing_level = level
    
    @pyqtSlot()
    def _toggle_recording(self) -> Any:
        """Toggle recording state"""
        if not self.config.is_recording:
            self._start_recording()
        else:
            self._stop_recording()
    
    def _start_recording(self) -> Any:
        """Start audio recording"""
        try:
            device_id = self.input_device_combo.currentData()
            self.recorder.start_recording(device_id)
            
            # Update UI
            self.record_button.setText("🔴 Recording...")
            self.record_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.status_label.setText("🔴 Recording in progress...")
            
            # Start timers
            self.visualization_timer.start(50)  # 20 FPS
            self.recording_timer.start(100)     # 10 Hz
            
            self.recording_status_changed.emit("recording")
            
        except Exception as e:
            logger.error("Failed to start recording", error=str(e))
            self.status_label.setText(f"❌ Recording failed: {e}")
            self._reset_ui_state()
    
    def _stop_recording(self) -> Any:
        """Stop recording and process audio"""
        try:
            self.recorder.stop_recording()
            
            # Stop timers
            self.visualization_timer.stop()
            self.recording_timer.stop()
            
            self.status_label.setText("⏳ Processing audio...")
            
            # Process audio after short delay
            QTimer.singleShot(100, self._process_recorded_audio)
            
        except Exception as e:
            logger.error("Failed to stop recording", error=str(e))
            self.status_label.setText(f"❌ Stop failed: {e}")
            self._reset_ui_state()
    
    def _process_recorded_audio(self) -> Any:
        """Process recorded audio with enhancement"""
        try:
            wav_data = self.recorder.get_recorded_audio()
            
            if not wav_data:
                self.status_label.setText("❌ No audio recorded")
                self._reset_ui_state()
                return
            
            # Emit the recorded audio
            self.audio_recorded.emit(wav_data)
            
            # Send to server if available
            if self.message_sender:
                self._send_to_server(wav_data)
            
            self.status_label.setText("✅ Recording completed")
            self._reset_ui_state()
            
        except Exception as e:
            logger.error("Failed to process audio", error=str(e))
            self.status_label.setText(f"❌ Processing failed: {e}")
            self._reset_ui_state()
    
    def _send_to_server(bytes) -> None:
        """Send audio to server"""
        try:
            metadata = {
                "source": "audio_widget",
                "sample_rate": self.config.sample_rate,
                "channels": self.config.channels,
                "timestamp": datetime.now().isoformat()
            }
            
            asyncio.create_task(
                self.message_sender.send_audio_message(wav_data, metadata)
            )
            
        except Exception as e:
            logger.error("Failed to send audio", error=str(e))
    
    def _update_visualization(self) -> Any:
        """Update visualization displays"""
        # Update volume meter
        volume = int(self.config.volume_level)
        self.volume_meter.setValue(volume)
        self.volume_label.setText(f"{volume}%")
        self.audio_level_changed.emit(volume)
        
        # Update waveform (simplified for now)
        if self.config.audio_data:
            # This would need proper waveform data
            pass
    
    def _update_recording_info(self) -> Any:
        """Update recording information"""
        if self.config.recording_start_time:
            elapsed = (datetime.now() - self.config.recording_start_time).total_seconds()
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)
            self.duration_label.setText(f"{minutes}:{seconds:02d}")
    
    def _reset_ui_state(self) -> Any:
        """Reset UI to initial state"""
        self.record_button.setText("🎤 Start Recording")
        self.record_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.recording_status_changed.emit("ready")
    
    def set_message_sender(self, message_sender) -> Any:
        """Set message sender for audio transmission"""
        self.message_sender = message_sender 