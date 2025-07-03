"""
Voice Provider Domain Models
Core domain models for voice service providers
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any, List


class ProviderType(Enum):
    """Voice provider types"""
    WHISPER = "whisper"
    AZURE = "azure"
    ELEVENLABS = "elevenlabs"
    GTTS = "gtts"
    FALLBACK = "fallback"


class ProviderOperation(Enum):
    """Provider operation types"""
    TRANSCRIPTION = "transcription"
    SYNTHESIS = "synthesis"


@dataclass
class ProviderConfig:
    """Configuration for a voice provider"""
    provider_type: ProviderType
    is_available: bool
    priority: int
    name: str
    supported_operations: List[ProviderOperation]


@dataclass
class TranscriptionRequest:
    """Request data for transcription"""
    audio_path: str
    language: str
    cache_key: Optional[str] = None


@dataclass
class SynthesisRequest:
    """Request data for synthesis"""
    text: str
    emotion: str
    language: str
    cache_key: Optional[str] = None


@dataclass
class ProviderResult:
    """Result from provider operation"""
    success: bool
    data: Optional[str]
    provider_name: str
    error_message: Optional[str] = None
    processing_time_ms: Optional[float] = None


@dataclass
class AudioProcessingConfig:
    """Configuration for audio processing"""
    sample_rate: int = 16000
    channels: int = 1
    format: str = "wav"
    compression: Optional[str] = None


@dataclass
class EmotionMapping:
    """Emotion settings for voice synthesis"""
    emotion_name: str
    provider_settings: Dict[ProviderType, Dict[str, Any]] 