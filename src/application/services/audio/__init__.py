"""
🎵 Audio Services Package
Modern audio processing services for the AI Teddy Bear system
"""

from .transcription_service import (ModernTranscriptionService,
                                    StreamingAudioBuffer, TranscriptionConfig,
                                    TranscriptionService,
                                    create_transcription_service)

try:
    from .synthesis_service import (ModernSynthesisService, SynthesisConfig,
                                    SynthesisService, VoiceCharacter,
                                    VoiceProvider, create_synthesis_service)
except ImportError:
    # Synthesis service not available
    pass

try:
    from .voice_service import (ModernVoiceService, VoiceConfig,
                                VoiceInteractionResult, VoiceService,
                                create_voice_service)
except ImportError:
    # Voice service not available
    pass

from .audio_playback_service import AudioPlaybackService
from .audio_recording_service import AudioRecordingService
from .audio_session_service import AudioSessionService

__all__ = [
    "ModernTranscriptionService",
    "TranscriptionService",
    "TranscriptionConfig",
    "StreamingAudioBuffer",
    "create_transcription_service",
    "ModernVoiceService",
    "VoiceService",
    "VoiceConfig",
    "VoiceInteractionResult",
    "create_voice_service",
    "AudioRecordingService",
    "AudioPlaybackService",
    "AudioSessionService",
]
