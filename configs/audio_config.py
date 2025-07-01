from typing import Any, Dict, List, Optional

"""
Audio Configuration for AI Teddy Bear UI
Centralized audio settings and device management
"""

import logging
from datetime import datetime

try:
    import sounddevice as sd

    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    SOUNDDEVICE_AVAILABLE = False

try:
    import pyaudio

    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False

import structlog

logger = structlog.get_logger()


class AudioConfig:
    """Audio configuration manager"""

    def __init__(self):
        self.sample_rate = 16000
        self.channels = 1
        self.chunk_size = 1024
        self.audio_format = pyaudio.paInt16 if PYAUDIO_AVAILABLE else None
        self.is_recording = False
        self.enable_processing = True
        self.processing_level = "auto"

        # Recording state
        self.audio_data = []
        self.recording_start_time = None
        self.volume_level = 0

        logger.info("Audio configuration initialized", sample_rate=self.sample_rate, channels=self.channels)

    def update_sample_rate(int) -> None:
        """Update audio sample rate"""
        self.sample_rate = rate
        logger.info("Sample rate updated", rate=rate)

    def get_audio_devices(self) -> Any:
        """Get available audio input devices"""
        devices = []

        try:
            if SOUNDDEVICE_AVAILABLE:
                device_list = sd.query_devices()
                for i, device in enumerate(device_list):
                    if device["max_input_channels"] > 0:
                        devices.append({"id": i, "name": device["name"], "channels": device["max_input_channels"]})
        except Exception as e:
            logger.error("Failed to get audio devices", error=str(e))
            devices.append({"id": None, "name": "Default Device", "channels": 1})

        return devices if devices else [{"id": None, "name": "Default Device", "channels": 1}]

    def validate_settings(self) -> bool:
        """Validate current audio settings"""
        if not SOUNDDEVICE_AVAILABLE and not PYAUDIO_AVAILABLE:
            logger.error("No audio library available")
            return False

        if self.sample_rate <= 0:
            logger.error("Invalid sample rate", rate=self.sample_rate)
            return False

        return True
