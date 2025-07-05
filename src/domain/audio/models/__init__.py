"""
Domain Audio Models - Voice Interaction
Contains core audio domain models and enums
"""

from .audio_format import AudioFormat, AudioQuality, AudioFormatType, AudioSystemConfig
from .audio_session import AudioSession, AudioSessionType, AudioQualityMode
from .performance_metrics import PerformanceMetrics
from .playback_options import PlaybackOptions
from .provider_models import (
    ProviderType,
    ProviderOperation,
    ProviderConfig,
    TranscriptionRequest,
    SynthesisRequest,
    ProviderResult,
    AudioProcessingConfig,
    EmotionMapping,
    TTSConfig,
    VoiceModel,
    VoiceStyle,
)
from .voice_models import VoiceSample, VoiceProfile

__all__ = [
    "AudioFormat",
    "AudioQuality",
    "AudioFormatType",
    "AudioSystemConfig",
    "AudioSession",
    "AudioSessionType",
    "AudioQualityMode",
    "PerformanceMetrics",
    "PlaybackOptions",
    "ProviderType",
    "ProviderOperation",
    "ProviderConfig",
    "TranscriptionRequest",
    "SynthesisRequest",
    "ProviderResult",
    "AudioProcessingConfig",
    "EmotionMapping",
    "TTSConfig",
    "VoiceModel",
    "VoiceStyle",
    "VoiceSample",
    "VoiceProfile",
]
