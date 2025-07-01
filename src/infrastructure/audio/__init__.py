"""Enhanced Audio System Module.

This module provides a complete audio processing system with capabilities for:
- Audio recording and playback with modern format support
- Text-to-speech conversion with emotional context
- Multi-format audio file I/O operations (WAV, MP3, OPUS, OGG, FLAC)
- Advanced audio signal processing
- Session management and performance monitoring
- Cloud integration and backup capabilities

The system follows clean architecture principles with clear separation of concerns
and robust error handling throughout.

Example usage:
    from src.audio import EnhancedAudioManager, create_child_safe_config

    # Create audio manager
    config = create_child_safe_config()
    audio_manager = EnhancedAudioManager(config)

    # Start session
    session_id = audio_manager.start_session("child_001")

    # Record audio
    audio_data, metadata = audio_manager.record_audio(duration=5, session_id=session_id)

    # Play audio
    audio_manager.play_audio(audio_data=audio_data, volume=0.7)

    # Text-to-speech
    audio_manager.speak("مرحباً! كيف حالك اليوم؟", language="ar", session_id=session_id)

    # Save audio in multiple formats
    audio_manager.save_audio(audio_data, "recording.mp3", format=AudioFormatType.MP3)

    # Cleanup
    audio_manager.end_session(session_id)
    audio_manager.cleanup()
"""

try:
    import structlog

    logger = structlog.get_logger(__name__)
except ImportError:
    import logging

    logger = logging.getLogger(__name__)
try:
    from .audio_manager import (EnhancedAudioManager,
                                create_child_safe_config)

    AudioManager = EnhancedAudioManager
    ENHANCED_AUDIO_AVAILABLE = True
except Exception as e:
    logger.warning(f"⚠️ Enhanced audio manager not available: {e}")
    ENHANCED_AUDIO_AVAILABLE = False
MODERN_AUDIO_AVAILABLE = False
try:
    from .audio_processing import (AudioProcessor, detect_silence,
                                   get_audio_stats, normalize_volume,
                                   process_audio, trim_silence)

    AUDIO_PROCESSING_AVAILABLE = True
except ImportError:
    AUDIO_PROCESSING_AVAILABLE = False
try:
    from .audio_io import (AudioFormat, AudioIO, AudioMetadata, AudioQuality,
                           cleanup_temp_files, get_audio_duration,
                           get_audio_files, get_audio_format)

    AUDIO_IO_AVAILABLE = True
except ImportError:
    AUDIO_IO_AVAILABLE = False
try:
    from .tts_playback import TTSPlayback, cleanup_tts_cache

    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
try:
    from .state_manager import (AudioState, StateChangeEvent, StateManager,
                                state_manager)

    STATE_MANAGER_AVAILABLE = True
except ImportError:
    STATE_MANAGER_AVAILABLE = False
try:
    from .hume_emotion_analyzer import (ChildVoiceEmotion,
                                        HumeSpeechEmotionAnalyzer)

    EMOTION_ANALYSIS_AVAILABLE = True
except ImportError:
    EMOTION_ANALYSIS_AVAILABLE = False
__all__ = []
if ENHANCED_AUDIO_AVAILABLE:
    __all__.extend(
        [
            "EnhancedAudioManager",
            "AudioManager",
            "AudioSystemConfig",
            "AudioSessionType",
            "AudioQualityMode",
            "AudioFormatType",
            "AudioSession",
            "AudioSystemError",
            "create_audio_manager",
            "create_child_safe_config",
            "create_high_quality_config",
            "create_low_latency_config",
            "get_audio_manager",
            "shutdown_audio_manager",
        ]
    )
if AUDIO_PROCESSING_AVAILABLE:
    __all__.extend(
        [
            "AudioProcessor",
            "process_audio",
            "normalize_volume",
            "detect_silence",
            "trim_silence",
            "get_audio_stats",
        ]
    )
if AUDIO_IO_AVAILABLE:
    __all__.extend(
        [
            "AudioIO",
            "AudioFormat",
            "AudioQuality",
            "AudioMetadata",
            "cleanup_temp_files",
            "get_audio_files",
            "get_audio_duration",
            "get_audio_format",
        ]
    )
if TTS_AVAILABLE:
    __all__.extend(["TTSPlayback", "cleanup_tts_cache"])
if STATE_MANAGER_AVAILABLE:
    __all__.extend(["state_manager", "AudioState", "StateChangeEvent", "StateManager"])
if EMOTION_ANALYSIS_AVAILABLE:
    __all__.extend(["HumeSpeechEmotionAnalyzer", "ChildVoiceEmotion"])


def get_system_info() -> dict:
    """Get information about available audio system components."""
    return {
        "enhanced_audio_available": ENHANCED_AUDIO_AVAILABLE,
        "modern_audio_available": MODERN_AUDIO_AVAILABLE,
        "audio_processing_available": AUDIO_PROCESSING_AVAILABLE,
        "audio_io_available": AUDIO_IO_AVAILABLE,
        "tts_available": TTS_AVAILABLE,
        "state_manager_available": STATE_MANAGER_AVAILABLE,
        "emotion_analysis_available": EMOTION_ANALYSIS_AVAILABLE,
    }


def create_default_audio_manager():
    """Create default audio manager with best available implementation."""
    if ENHANCED_AUDIO_AVAILABLE:
        config = create_child_safe_config()
        return EnhancedAudioManager(config)
    else:
        raise ImportError("No audio manager implementation available")


if ENHANCED_AUDIO_AVAILABLE:
    _default_audio_manager = None

    def get_default_audio_manager():
        """Get or create default global audio manager instance."""
        global _default_audio_manager
        if _default_audio_manager is None:
            _default_audio_manager = create_default_audio_manager()
        return _default_audio_manager

    def shutdown_default_audio_manager():
        """Shutdown and cleanup default global audio manager."""
        global _default_audio_manager
        if _default_audio_manager is not None:
            _default_audio_manager.cleanup()
            _default_audio_manager = None

    __all__.extend(["get_default_audio_manager", "shutdown_default_audio_manager"])
__version__ = "2.0.0"
__author__ = "AI Teddy Bear Team"
__license__ = "MIT"


def _print_init_status():
    """Print module initialization status."""
    available_components = []
    if ENHANCED_AUDIO_AVAILABLE:
        available_components.append("Enhanced Audio Manager")
    if AUDIO_PROCESSING_AVAILABLE:
        available_components.append("Audio Processing")
    if EMOTION_ANALYSIS_AVAILABLE:
        available_components.append("Emotion Analysis")
    if available_components:
        logger.info(
            f"🎵 Audio System v{__version__} - Available: {', '.join(available_components)}"
        )
    else:
        logger.info(
            f"⚠️ Audio System v{__version__} - Limited functionality (no components available)"
        )


if __name__ != "__main__":
    _print_init_status()
