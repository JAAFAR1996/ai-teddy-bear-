"""
Voice Domain Models
Core audio domain models, enums and value objects
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict

try:
    from elevenlabs import VoiceSettings
except ImportError:
    from src.infrastructure.external_services.mock.elevenlabs import VoiceSettings


class EmotionalTone(Enum):
    """Enhanced emotional voice tones for the teddy bear"""

    HAPPY = "happy"
    CALM = "calm"
    CURIOUS = "curious"
    SUPPORTIVE = "supportive"
    PLAYFUL = "playful"
    SLEEPY = "sleepy"
    EXCITED = "excited"
    STORYTELLING = "storytelling"
    EDUCATIONAL = "educational"
    COMFORTING = "comforting"


class Language(Enum):
    """Supported languages"""

    ENGLISH = "en"
    ARABIC = "ar"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    CHINESE = "zh"
    JAPANESE = "ja"
    KOREAN = "ko"


@dataclass
class AudioConfig:
    """Audio configuration settings"""

    sample_rate: int = 24000
    channels: int = 1
    chunk_size: int = 1024
    format: str = "int16"

    # Voice Activity Detection
    vad_mode: int = 3  # 0-3, 3 is most aggressive
    vad_frame_duration: int = 30  # milliseconds

    # Noise reduction
    enable_noise_reduction: bool = True
    noise_reduction_strength: float = 0.5

    # Audio enhancement
    enable_normalization: bool = True
    target_loudness: float = -20.0  # dB

    # Recording
    silence_threshold: float = 0.01
    silence_duration: float = 2.0  # seconds
    max_recording_duration: float = 30.0  # seconds

    def validate(self) -> bool:
        """Validate audio configuration"""
        if self.sample_rate <= 0:
            return False
        if self.channels not in [1, 2]:
            return False
        if self.vad_mode not in range(4):
            return False
        return True


@dataclass
class VoiceProfile:
    """Voice profile for different characters/modes"""

    id: str
    name: str
    voice_id: str  # ElevenLabs voice ID
    language: Language
    emotional_settings: Dict[EmotionalTone, VoiceSettings]
    pitch_adjustment: float = 0.0
    speed_adjustment: float = 1.0
    personality_prompt: str = ""

    def get_voice_settings(self, emotion: EmotionalTone) -> VoiceSettings:
        """Get voice settings for specific emotion"""
        return self.emotional_settings.get(
            emotion, self.emotional_settings.get(EmotionalTone.CALM)
        )

    def is_valid(self) -> bool:
        """Validate voice profile"""
        return (
            bool(self.id)
            and bool(self.name)
            and bool(self.voice_id)
            and self.emotional_settings
        )
