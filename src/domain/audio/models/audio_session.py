"""Audio session domain models for AI Teddy Bear."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class AudioSessionType(Enum):
    """Types of audio sessions."""

    CONVERSATION = "conversation"
    STORY_TELLING = "story_telling"
    LEARNING = "learning"
    PLAY_TIME = "play_time"
    EMERGENCY = "emergency"
    SYSTEM_TEST = "system_test"


class AudioQualityMode(Enum):
    """Audio quality modes for different scenarios."""

    POWER_SAVE = "power_save"  # Low quality, minimal processing
    BALANCED = "balanced"  # Good quality, moderate processing
    HIGH_QUALITY = "high_quality"  # Best quality, full processing
    ADAPTIVE = "adaptive"  # Auto-adjust based on conditions


@dataclass
class AudioSession:
    """Audio session information."""

    session_id: str
    session_type: AudioSessionType
    child_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_recordings: int = 0
    total_duration: float = 0.0
    quality_mode: AudioQualityMode = AudioQualityMode.BALANCED
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    @property
    def duration_seconds(self) -> float:
        """Calculate session duration in seconds."""
        if self.end_time is None:
            return (datetime.now() - self.start_time).total_seconds()
        return (self.end_time - self.start_time).total_seconds()

    @property
    def is_active(self) -> bool:
        """Check if session is currently active."""
        return self.end_time is None

    def add_recording(self, duration: float) -> None:
        """Add a recording to this session."""
        self.total_recordings += 1
        self.total_duration += duration

    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary."""
        return {
            "session_id": self.session_id,
            "session_type": self.session_type.value,
            "child_id": self.child_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "total_recordings": self.total_recordings,
            "total_duration": self.total_duration,
            "quality_mode": self.quality_mode.value,
            "metadata": self.metadata,
        }
