"""Audio format and configuration domain models."""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict


class AudioFormatType(Enum):
    """Supported audio formats."""

    WAV = "wav"
    MP3 = "mp3"
    OPUS = "opus"
    OGG = "ogg"
    FLAC = "flac"
    M4A = "m4a"


@dataclass
class AudioSystemConfig:
    """Audio system configuration."""

    # Recording settings
    default_record_duration: int = 10
    max_record_duration: int = 60
    auto_process_audio: bool = True
    auto_save_sessions: bool = True

    # Processing settings
    noise_reduction_enabled: bool = True
    voice_activity_detection: bool = True
    adaptive_quality: bool = True

    # System settings
    emergency_override: bool = True
    session_timeout_minutes: int = 30
    max_concurrent_sessions: int = 3
    volume_level: float = 0.8
    language_preference: str = "en"
    child_safe_mode: bool = True

    # Audio format settings
    default_output_format: AudioFormatType = AudioFormatType.WAV
    sample_rate: int = 44100
    channels: int = 2
    bitrate: int = 192  # For compressed formats
    compression_quality: int = 5  # 0-10 scale

    # Cloud settings
    enable_cloud_sync: bool = True
    cloud_backup_enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "default_record_duration": self.default_record_duration,
            "max_record_duration": self.max_record_duration,
            "auto_process_audio": self.auto_process_audio,
            "auto_save_sessions": self.auto_save_sessions,
            "noise_reduction_enabled": self.noise_reduction_enabled,
            "voice_activity_detection": self.voice_activity_detection,
            "adaptive_quality": self.adaptive_quality,
            "emergency_override": self.emergency_override,
            "session_timeout_minutes": self.session_timeout_minutes,
            "max_concurrent_sessions": self.max_concurrent_sessions,
            "volume_level": self.volume_level,
            "language_preference": self.language_preference,
            "child_safe_mode": self.child_safe_mode,
            "default_output_format": self.default_output_format.value,
            "sample_rate": self.sample_rate,
            "channels": self.channels,
            "bitrate": self.bitrate,
            "compression_quality": self.compression_quality,
            "enable_cloud_sync": self.enable_cloud_sync,
            "cloud_backup_enabled": self.cloud_backup_enabled,
        }

    @classmethod
    def create_child_safe_config(cls) -> "AudioSystemConfig":
        """Create child-safe configuration."""
        return cls(
            child_safe_mode=True,
            max_record_duration=30,
            volume_level=0.6,
            noise_reduction_enabled=True,
            voice_activity_detection=True,
            emergency_override=True,
        )

    @classmethod
    def create_high_quality_config(cls) -> "AudioSystemConfig":
        """Create high-quality configuration."""
        return cls(
            default_output_format=AudioFormatType.FLAC,
            sample_rate=48000,
            channels=2,
            compression_quality=8,
            noise_reduction_enabled=True,
            adaptive_quality=False,
        )

    @classmethod
    def create_low_latency_config(cls) -> "AudioSystemConfig":
        """Create low-latency configuration."""
        return cls(
            auto_process_audio=False,
            default_output_format=AudioFormatType.OPUS,
            sample_rate=16000,
            channels=1,
            compression_quality=3,
            cloud_backup_enabled=False,
        )
