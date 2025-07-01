"""Enhanced Audio Manager - Coordinator for specialized audio services."""

import logging
import threading
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

# Import specialized services
from ...application.services.audio import (AudioPlaybackService,
                                           AudioRecordingService,
                                           AudioSessionService)
# Import domain models
from ...domain.audio.models import (AudioFormatType, AudioQualityMode,
                                    AudioSession, AudioSessionType,
                                    AudioSystemConfig, PerformanceMetrics)


class AudioSystemError(Exception):
    """Audio system specific error."""

    pass


class EnhancedAudioManager:
    """
    Enhanced Audio Manager - Coordinator for specialized services.

    This class now acts as a facade/coordinator that delegates work to
    specialized services instead of handling everything internally.
    """

    def __init__(self, config: Optional[AudioSystemConfig] = None):
        """Initialize the enhanced audio manager coordinator."""
        self.logger = logging.getLogger(__name__)
        self.config = config or AudioSystemConfig()

        # Initialize performance metrics
        self.metrics = PerformanceMetrics()

        # Initialize specialized services
        self._initialize_services()

        # Background tasks
        self._monitoring_task = None
        self._start_background_monitoring()

        self.logger.info("Enhanced Audio Manager coordinator initialized")

    def _initialize_services(self) -> None:
        """Initialize specialized audio services."""
        try:
            # Initialize core services
            self.recording_service = AudioRecordingService(self.config, self.metrics)
            self.playback_service = AudioPlaybackService(self.config, self.metrics)
            self.session_service = AudioSessionService(self.config, self.metrics)

            self.logger.info("All audio services initialized successfully")

        except Exception as e:
            error_msg = f"Failed to initialize audio services: {e}"
            self.logger.error(error_msg)
            raise AudioSystemError(error_msg)

    def _start_background_monitoring(self) -> None:
        """Start background monitoring tasks."""

        def monitoring_worker():
            while True:
                try:
                    time.sleep(30)  # Check every 30 seconds

                    # Check session timeouts
                    self.session_service.check_session_timeouts()

                    # Update metrics
                    self.metrics.update_health_check()

                    # Log system health
                    if self.metrics.status.value != "healthy":
                        self.logger.warning(
                            f"System status: {self.metrics.status.value}"
                        )

                except Exception as e:
                    self.logger.error(f"Monitoring worker error: {e}")

        # Start daemon thread
        self._monitoring_task = threading.Thread(target=monitoring_worker, daemon=True)
        self._monitoring_task.start()

    # === Session Management ===

    def start_session(
        self,
        child_id: str,
        session_type: AudioSessionType = AudioSessionType.CONVERSATION,
        quality_mode: AudioQualityMode = AudioQualityMode.BALANCED,
    ) -> str:
        """Start a new audio session."""
        return self.session_service.start_session(child_id, session_type, quality_mode)

    def end_session(self, session_id: str) -> bool:
        """End an audio session."""
        return self.session_service.end_session(session_id)

    def get_current_session(self) -> Optional[AudioSession]:
        """Get current active session."""
        return self.session_service.get_current_session()

    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed session information."""
        return self.session_service.get_session_info(session_id)

    # === Recording Operations ===

    def record_audio(
        self,
        duration: Optional[int] = None,
        process: bool = None,
        save: bool = None,
        filename: Optional[str] = None,
        session_id: Optional[str] = None,
        format: Optional[AudioFormatType] = None,
    ) -> Optional[Tuple[np.ndarray, Dict[str, Any]]]:
        """Record audio with specified parameters."""
        # Get current session if none specified
        if session_id is None:
            current_session = self.session_service.get_current_session()
            session = current_session
        else:
            session = self.session_service.get_session(session_id)

        return self.recording_service.record_audio(
            duration=duration, session=session, format_type=format
        )

    def is_recording(self) -> bool:
        """Check if currently recording."""
        return self.recording_service.is_recording()

    def stop_recording(self) -> bool:
        """Stop current recording."""
        return self.recording_service.stop_recording()

    # === Playback Operations ===

    def play_audio(
        self,
        audio_data: Optional[np.ndarray] = None,
        filename: Optional[str] = None,
        volume: Optional[float] = None,
        session_id: Optional[str] = None,
        format_hint: Optional[AudioFormatType] = None,
        loop: bool = False,
        fade_in: float = 0.0,
        fade_out: float = 0.0,
    ) -> bool:
        """Play audio from data or file."""
        # Get current session if none specified
        if session_id is None:
            current_session = self.session_service.get_current_session()
            session = current_session
        else:
            session = self.session_service.get_session(session_id)

        return self.playback_service.play_audio(
            audio_data=audio_data,
            filename=filename,
            volume=volume,
            session=session,
            format_hint=format_hint,
            loop=loop,
            fade_in=fade_in,
            fade_out=fade_out,
        )

    def speak(
        self,
        text: str,
        language: Optional[str] = None,
        speed: float = 1.0,
        volume: Optional[float] = None,
        cache: bool = True,
        session_id: Optional[str] = None,
        voice_style: str = "friendly",
    ) -> bool:
        """Convert text to speech and play."""
        # Get current session if none specified
        if session_id is None:
            current_session = self.session_service.get_current_session()
            session = current_session
        else:
            session = self.session_service.get_session(session_id)

        return self.playback_service.speak(
            text=text,
            language=language,
            speed=speed,
            volume=volume,
            cache=cache,
            session=session,
            voice_style=voice_style,
        )

    def is_playing(self) -> bool:
        """Check if currently playing audio."""
        return self.playback_service.is_playing()

    def stop_playback(self) -> bool:
        """Stop current playback."""
        return self.playback_service.stop_playback()

    def stop_all(self, session_id: Optional[str] = None) -> bool:
        """Stop all audio operations."""
        recording_stopped = self.stop_recording()
        playback_stopped = self.stop_playback()
        return recording_stopped or playback_stopped

    # === System Information ===

    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics."""
        base_stats = self.metrics.to_dict()
        session_stats = self.session_service.get_session_statistics()
        recording_status = self.recording_service.get_recording_status()
        playback_status = self.playback_service.get_playback_status()

        return {
            **base_stats,
            "sessions": session_stats,
            "recording": recording_status,
            "playback": playback_status,
            "config": self.config.to_dict(),
        }

    def get_supported_formats(self) -> List[str]:
        """Get list of supported audio formats."""
        return [format_type.value for format_type in AudioFormatType]

    def get_format_info(self, format: AudioFormatType) -> Dict[str, Any]:
        """Get information about specific audio format."""
        format_info = {
            AudioFormatType.WAV: {
                "name": "WAV",
                "description": "Uncompressed audio",
                "quality": "Lossless",
                "typical_size": "Large",
                "compatibility": "Excellent",
            },
            AudioFormatType.MP3: {
                "name": "MP3",
                "description": "Compressed audio",
                "quality": "Good",
                "typical_size": "Small",
                "compatibility": "Excellent",
            },
            AudioFormatType.OPUS: {
                "name": "Opus",
                "description": "Modern compressed audio",
                "quality": "Very Good",
                "typical_size": "Very Small",
                "compatibility": "Good",
            },
            AudioFormatType.FLAC: {
                "name": "FLAC",
                "description": "Lossless compressed audio",
                "quality": "Lossless",
                "typical_size": "Medium",
                "compatibility": "Good",
            },
            AudioFormatType.OGG: {
                "name": "OGG Vorbis",
                "description": "Open source compressed audio",
                "quality": "Good",
                "typical_size": "Small",
                "compatibility": "Moderate",
            },
            AudioFormatType.M4A: {
                "name": "M4A/AAC",
                "description": "Apple compressed audio",
                "quality": "Good",
                "typical_size": "Small",
                "compatibility": "Good",
            },
        }

        return format_info.get(
            format, {"name": "Unknown", "description": "Unknown format"}
        )

    def test_audio_system(self) -> Dict[str, Any]:
        """Test audio system functionality."""
        test_results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "overall_status": "unknown",
            "errors": [],
        }

        try:
            # Test session creation
            test_session_id = self.start_session(
                "test_child", AudioSessionType.SYSTEM_TEST
            )
            test_results["tests"]["session_creation"] = True

            # Test recording
            try:
                recording_result = self.record_audio(
                    duration=1, session_id=test_session_id
                )
                test_results["tests"]["recording"] = recording_result is not None
            except Exception as e:
                test_results["tests"]["recording"] = False
                test_results["errors"].append(f"Recording test failed: {e}")

            # Test TTS
            try:
                tts_result = self.speak("Test message", session_id=test_session_id)
                test_results["tests"]["text_to_speech"] = tts_result
            except Exception as e:
                test_results["tests"]["text_to_speech"] = False
                test_results["errors"].append(f"TTS test failed: {e}")

            # Test session cleanup
            session_ended = self.end_session(test_session_id)
            test_results["tests"]["session_cleanup"] = session_ended

            # Calculate overall status
            passed_tests = sum(1 for result in test_results["tests"].values() if result)
            total_tests = len(test_results["tests"])

            if passed_tests == total_tests:
                test_results["overall_status"] = "pass"
            elif passed_tests > 0:
                test_results["overall_status"] = "partial"
            else:
                test_results["overall_status"] = "fail"

            test_results["score"] = f"{passed_tests}/{total_tests}"

        except Exception as e:
            test_results["overall_status"] = "error"
            test_results["errors"].append(f"System test error: {e}")

        return test_results

    # === Configuration Management ===

    def update_config(self, new_config: AudioSystemConfig) -> None:
        """Update system configuration."""
        self.config = new_config

        # Update services with new config
        self.recording_service.update_config(new_config)
        # playback_service and session_service would also be updated if they had update methods

        self.logger.info("Audio system configuration updated")

    def get_config(self) -> AudioSystemConfig:
        """Get current system configuration."""
        return self.config

    # === Cleanup and Context Management ===

    def cleanup(self) -> None:
        """Cleanup audio manager resources."""
        try:
            # Stop all operations
            self.stop_all()

            # End all sessions
            self.session_service.force_end_all_sessions()

            # Cleanup services
            if hasattr(self.recording_service, "cleanup"):
                self.recording_service.cleanup()
            if hasattr(self.playback_service, "cleanup"):
                self.playback_service.cleanup()

            self.logger.info("Audio manager cleanup completed")

        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()


# === Factory Functions ===


def create_audio_manager(
    config: Optional[AudioSystemConfig] = None,
) -> EnhancedAudioManager:
    """
    Factory function to create an audio manager.

    Args:
        config: Optional configuration, uses defaults if None

    Returns:
        Configured EnhancedAudioManager instance
    """
    return EnhancedAudioManager(config)


def get_default_config() -> AudioSystemConfig:
    """Get default audio system configuration."""
    return AudioSystemConfig()


def create_child_safe_config() -> AudioSystemConfig:
    """Create child-safe audio configuration."""
    return AudioSystemConfig.create_child_safe_config()


def create_high_quality_config() -> AudioSystemConfig:
    """Create high-quality audio configuration."""
    return AudioSystemConfig.create_high_quality_config()


def create_low_latency_config() -> AudioSystemConfig:
    """Create low-latency audio configuration."""
    return AudioSystemConfig.create_low_latency_config()


# === Global Instance Management ===

_global_audio_manager: Optional[EnhancedAudioManager] = None


def get_audio_manager(
    config: Optional[AudioSystemConfig] = None,
) -> EnhancedAudioManager:
    """
    Get or create global audio manager instance.

    Args:
        config: Configuration for new instance (ignored if instance exists)

    Returns:
        Global EnhancedAudioManager instance
    """
    global _global_audio_manager

    if _global_audio_manager is None:
        _global_audio_manager = create_audio_manager(config)

    return _global_audio_manager


def shutdown_audio_manager() -> None:
    """Shutdown and cleanup global audio manager."""
    global _global_audio_manager

    if _global_audio_manager:
        _global_audio_manager.cleanup()
        _global_audio_manager = None
