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
import structlog
logger = structlog.get_logger(__name__)


# Import main enhanced audio manager
try:
    from .audio_manager import (
        EnhancedAudioManager,
        AudioManager,  # Alias for backward compatibility
        AudioSystemConfig,
        AudioSessionType,
        AudioQualityMode,
        AudioFormatType,
        AudioSession,
        AudioSystemError,
        create_audio_manager,
        create_child_safe_config,
        create_high_quality_config,
        create_low_latency_config,
        get_audio_manager,
        shutdown_audio_manager
    )
    ENHANCED_AUDIO_AVAILABLE = True
except Exception as e:
    logger.error(f"Error: {e}")f"⚠️ Enhanced audio manager not available: {e}")
    ENHANCED_AUDIO_AVAILABLE = False

# Import modern async audio manager
try:
    from .modern_audio_manager import (
        ModernAudioManager,
        create_modern_audio_manager,
        bridge_to_enhanced_manager
    )
    MODERN_AUDIO_AVAILABLE = True
except Exception as e:
    logger.error(f"Error: {e}")f"⚠️ Modern audio manager not available: {e}")
    MODERN_AUDIO_AVAILABLE = False

# Import audio processing components (optional)
try:
    from .audio_processing import (
        AudioProcessor,
        process_audio,
        normalize_volume,
        detect_silence,
        trim_silence,
        get_audio_stats
    )
    AUDIO_PROCESSING_AVAILABLE = True
except ImportError:
    AUDIO_PROCESSING_AVAILABLE = False

# Import audio I/O components (optional)
try:
    from .audio_io import (
        AudioIO,
        AudioFormat,
        AudioQuality,
        AudioMetadata,
        cleanup_temp_files,
        get_audio_files,
        get_audio_duration,
        get_audio_format
    )
    AUDIO_IO_AVAILABLE = True
except ImportError:
    AUDIO_IO_AVAILABLE = False

# Import TTS components (optional)
try:
    from .tts_playback import (
        TTSPlayback,
        cleanup_tts_cache
    )
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

# Import state management (optional)
try:
    from .state_manager import (
        state_manager,
        AudioState,
        StateChangeEvent,
        StateManager
    )
    STATE_MANAGER_AVAILABLE = True
except ImportError:
    STATE_MANAGER_AVAILABLE = False

# Import emotion analysis (optional)
try:
    from .hume_emotion_analyzer import (
        HumeSpeechEmotionAnalyzer,
        ChildVoiceEmotion
    )
    EMOTION_ANALYSIS_AVAILABLE = True
except ImportError:
    EMOTION_ANALYSIS_AVAILABLE = False


# Export main classes and functions
__all__ = []

# Enhanced Audio Manager exports
if ENHANCED_AUDIO_AVAILABLE:
    __all__.extend([
        'EnhancedAudioManager',
        'AudioManager',
        'AudioSystemConfig',
        'AudioSessionType',
        'AudioQualityMode',
        'AudioFormatType',
        'AudioSession',
        'AudioSystemError',
        'create_audio_manager',
        'create_child_safe_config',
        'create_high_quality_config',
        'create_low_latency_config',
        'get_audio_manager',
        'shutdown_audio_manager'
    ])

# Modern Audio Manager exports  
if MODERN_AUDIO_AVAILABLE:
    __all__.extend([
        'ModernAudioManager',
        'create_modern_audio_manager',
        'bridge_to_enhanced_manager'
    ])

# Audio processing exports
if AUDIO_PROCESSING_AVAILABLE:
    __all__.extend([
        'AudioProcessor',
        'process_audio',
        'normalize_volume',
        'detect_silence',
        'trim_silence',
        'get_audio_stats'
    ])

# Audio I/O exports
if AUDIO_IO_AVAILABLE:
    __all__.extend([
        'AudioIO',
        'AudioFormat',
        'AudioQuality', 
        'AudioMetadata',
        'cleanup_temp_files',
        'get_audio_files',
        'get_audio_duration',
        'get_audio_format'
    ])

# TTS exports
if TTS_AVAILABLE:
    __all__.extend([
        'TTSPlayback',
        'cleanup_tts_cache'
    ])

# State management exports
if STATE_MANAGER_AVAILABLE:
    __all__.extend([
        'state_manager',
        'AudioState',
        'StateChangeEvent',
        'StateManager'
    ])

# Emotion analysis exports
if EMOTION_ANALYSIS_AVAILABLE:
    __all__.extend([
        'HumeSpeechEmotionAnalyzer',
        'ChildVoiceEmotion'
    ])


# Convenience functions

def get_system_info() -> dict:
    """Get information about available audio system components."""
    return {
        "enhanced_audio_available": ENHANCED_AUDIO_AVAILABLE,
        "modern_audio_available": MODERN_AUDIO_AVAILABLE,
        "audio_processing_available": AUDIO_PROCESSING_AVAILABLE,
        "audio_io_available": AUDIO_IO_AVAILABLE,
        "tts_available": TTS_AVAILABLE,
        "state_manager_available": STATE_MANAGER_AVAILABLE,
        "emotion_analysis_available": EMOTION_ANALYSIS_AVAILABLE
    }


def create_default_audio_manager():
    """Create default audio manager with best available implementation."""
    if ENHANCED_AUDIO_AVAILABLE:
        config = create_child_safe_config()
        return EnhancedAudioManager(config)
    else:
        raise ImportError("No audio manager implementation available")


async def create_default_modern_audio_manager(container=None):
    """Create default modern audio manager with async support."""
    if MODERN_AUDIO_AVAILABLE:
        return await create_modern_audio_manager(container)
    else:
        raise ImportError("Modern audio manager not available")


# For backward compatibility with existing code
if ENHANCED_AUDIO_AVAILABLE:
    # Create global instance (use with caution in production)
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
    
    # Add to exports
    __all__.extend(['get_default_audio_manager', 'shutdown_default_audio_manager'])


# Version info
__version__ = '2.0.0'
__author__ = 'AI Teddy Bear Team'
__license__ = 'MIT'

# Module initialization message
def _print_init_status():
    """Print module initialization status."""
    available_components = []
    if ENHANCED_AUDIO_AVAILABLE:
        available_components.append("Enhanced Audio Manager")
    if MODERN_AUDIO_AVAILABLE:
        available_components.append("Modern Audio Manager")
    if AUDIO_PROCESSING_AVAILABLE:
        available_components.append("Audio Processing")
    if EMOTION_ANALYSIS_AVAILABLE:
        available_components.append("Emotion Analysis")
    
    if available_components:
        print(f"🎵 Audio System v{__version__} - Available: {', '.join(available_components)}")
    else:
        print(f"⚠️ Audio System v{__version__} - Limited functionality (no components available)")

# Print status only if running directly
if __name__ != "__main__":
    _print_init_status()
