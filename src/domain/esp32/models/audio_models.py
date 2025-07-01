"""ESP32 audio domain models."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class AudioQuality(Enum):
    """Audio quality settings."""

    LOW = "low"  # 8kHz, mono
    MEDIUM = "medium"  # 16kHz, mono
    HIGH = "high"  # 22kHz, stereo


class RecognitionLanguage(Enum):
    """Supported recognition languages."""

    ARABIC = "ar-SA"
    ENGLISH_US = "en-US"
    ENGLISH_UK = "en-GB"


@dataclass
class MicrophoneSettings:
    """Microphone configuration."""

    energy_threshold: int = 300
    dynamic_energy_threshold: bool = False
    pause_threshold: float = 0.3
    phrase_threshold: float = 0.1
    non_speaking_duration: float = 0.2
    calibration_duration: float = 0.1

    def __post_init__(self):
        """Validate microphone settings."""
        if not 100 <= self.energy_threshold <= 1000:
            raise ValueError("Energy threshold must be between 100 and 1000")

    @property
    def is_ultra_sensitive(self) -> bool:
        """Check if microphone is in ultra-sensitive mode."""
        return self.energy_threshold <= 200 and not self.dynamic_energy_threshold and self.pause_threshold <= 0.3


@dataclass
class AudioSettings:
    """Audio system configuration."""

    quality: AudioQuality = AudioQuality.MEDIUM
    volume: int = 50  # 0-100
    microphone: MicrophoneSettings = None
    language: RecognitionLanguage = RecognitionLanguage.ARABIC
    wake_words: List[str] = None

    def __post_init__(self):
        """Initialize default values."""
        if self.microphone is None:
            self.microphone = MicrophoneSettings()
        if self.wake_words is None:
            self.wake_words = ["يا دبدوب", "hey teddy", "hello teddy"]

    @property
    def sample_rate(self) -> int:
        """Get sample rate based on quality."""
        rates = {AudioQuality.LOW: 8000, AudioQuality.MEDIUM: 16000, AudioQuality.HIGH: 22050}
        return rates[self.quality]

    @property
    def channels(self) -> int:
        """Get number of channels based on quality."""
        return 2 if self.quality == AudioQuality.HIGH else 1


@dataclass
class AudioVisualization:
    """Audio visualization state."""

    is_active: bool = False
    bar_count: int = 20
    bar_heights: List[int] = None
    colors: List[str] = None
    animation_speed: int = 100  # milliseconds

    def __post_init__(self):
        """Initialize visualization data."""
        if self.bar_heights is None:
            self.bar_heights = [0] * self.bar_count
        if self.colors is None:
            self.colors = ["#3498db"] * self.bar_count

    def update_bars(self, heights: List[int]) -> None:
        """Update visualization bar heights."""
        if len(heights) == self.bar_count:
            self.bar_heights = heights
            self.colors = ["#e74c3c" if h > 50 else "#f39c12" if h > 30 else "#3498db" for h in heights]

    def start_animation(self) -> None:
        """Start visualization animation."""
        self.is_active = True

    def stop_animation(self) -> None:
        """Stop visualization animation."""
        self.is_active = False
        self.bar_heights = [0] * self.bar_count
        self.colors = ["#3498db"] * self.bar_count


@dataclass
class SpeechRecognition:
    """Speech recognition result."""

    text: str
    confidence: float
    language: str
    wake_word_detected: bool = False
    detected_wake_word: Optional[str] = None
    timestamp: datetime = None

    def __post_init__(self):
        """Set timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.now()

    @property
    def is_high_confidence(self) -> bool:
        """Check if recognition has high confidence."""
        return self.confidence >= 0.8

    @property
    def is_valid(self) -> bool:
        """Check if recognition result is valid."""
        return self.text.strip() != "" and self.confidence >= 0.3
