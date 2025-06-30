"""
🎵 Audio Services Package
Modern audio processing services for the AI Teddy Bear system
"""

from .transcription_service import (
    ModernTranscriptionService,
    TranscriptionService,
    TranscriptionConfig,
    StreamingAudioBuffer,
    create_transcription_service
)

try:
    from .synthesis_service import (
        ModernSynthesisService,
        SynthesisService,
        SynthesisConfig,
        VoiceCharacter,
        VoiceProvider,
        create_synthesis_service
    )
except ImportError:
    # Synthesis service not available
    pass

try:
    from .voice_service import (
        ModernVoiceService,
        VoiceService,
        VoiceConfig,
        VoiceInteractionResult,
        create_voice_service
    )
except ImportError:
    # Voice service not available
    pass

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
    "create_voice_service"
] 