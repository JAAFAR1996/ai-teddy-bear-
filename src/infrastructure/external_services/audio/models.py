"""
Data models for the audio I/O system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class AudioFormat(Enum):
    """Supported audio formats."""

    WAV = "wav"
    MP3 = "mp3"
    OGG = "ogg"
    FLAC = "flac"
    M4A = "m4a"
    AAC = "aac"


class AudioQuality(Enum):
    """Audio quality presets."""

    LOW = {"sample_rate": 8000, "bitrate": "64k"}
    MEDIUM = {"sample_rate": 16000, "bitrate": "128k"}
    HIGH = {"sample_rate": 22050, "bitrate": "192k"}
    PREMIUM = {"sample_rate": 44100, "bitrate": "320k"}


@dataclass
class AudioMetadata:
    """Audio file metadata."""

    filename: str
    format: str
    duration: float
    sample_rate: int
    channels: int
    bitrate: Optional[int] = None
    size_bytes: int = 0
    created_at: datetime = None
    modified_at: datetime = None
    checksum: Optional[str] = None
    tags: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class AudioProcessingConfig:
    """Audio processing configuration."""

    target_sample_rate: int = 16000
    target_channels: int = 1  # Mono
    normalize_audio: bool = True
    remove_silence: bool = True
    apply_noise_reduction: bool = True
    max_duration: Optional[float] = None
    quality: AudioQuality = AudioQuality.MEDIUM
