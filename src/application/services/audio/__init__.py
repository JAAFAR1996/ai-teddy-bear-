"""
🎵 Audio Services Package
Modern audio processing services for the AI Teddy Bear system
"""

from .transcription_service import (
    ModernTranscriptionService,
    StreamingAudioBuffer,
    TranscriptionConfig,
    TranscriptionService,
    create_transcription_service,
)

try:
    from .synthesis_service import (
        ModernSynthesisService,
        SynthesisConfig,
        SynthesisService,
        VoiceCharacter,
        VoiceProvider,
        create_synthesis_service,
    )
except ImportError:
    # Synthesis service not available
    pass

try:
    from .voice_service_refactored import (
        IVoiceService,
        MultiProviderVoiceService,
        VoiceServiceFactory,
        Settings,
    )
except ImportError:
    # Voice service not available
    pass

from .audio_playback_service import AudioPlaybackService
from .audio_recording_service import AudioRecordingService
from .audio_session_service import AudioSessionService

from .voice_service_refactored import (
    IVoiceService,
    MultiProviderVoiceService,
    VoiceServiceFactory,
    Settings,
)

from src.domain.audio.models import (
    ProviderType,
    ProviderOperation,
    ProviderConfig,
    TranscriptionRequest,
    SynthesisRequest,
    ProviderResult,
)

from .voice_provider_manager import ProviderManager
from .voice_cache_manager import VoiceCacheManager
from .voice_audio_processor import VoiceAudioProcessor

__all__ = [
    "ModernTranscriptionService",
    "TranscriptionService",
    "TranscriptionConfig",
    "StreamingAudioBuffer",
    "create_transcription_service",
    "IVoiceService",
    "MultiProviderVoiceService",
    "VoiceServiceFactory",
    "Settings",
    "AudioRecordingService",
    "AudioPlaybackService",
    "AudioSessionService",
    "ProviderType",
    "ProviderOperation",
    "ProviderConfig",
    "TranscriptionRequest",
    "SynthesisRequest",
    "ProviderResult",
    "ProviderManager",
    "VoiceCacheManager",
    "VoiceAudioProcessor",
]
