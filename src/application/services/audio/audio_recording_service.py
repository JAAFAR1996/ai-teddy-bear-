"""Audio recording service for AI Teddy Bear."""

import logging
import time
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

import numpy as np

from ....domain.audio.models import (
    AudioFormatType,
    AudioQualityMode,
    AudioSession,
    AudioSessionType,
    AudioSystemConfig,
    PerformanceMetrics,
)


class AudioSystemError(Exception):
    """Audio system specific error."""

    pass


class AudioRecordingService:
    """Specialized service for audio recording operations."""

    def __init__(self, config: AudioSystemConfig, metrics: PerformanceMetrics):
        """Initialize audio recording service."""
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.metrics = metrics

        # Recording state
        self._is_recording = False
        self._current_recording_session = None

        # Initialize recorder component
        self._initialize_recorder()

    def _initialize_recorder(self) -> None:
        """Initialize audio recorder component."""
        try:
            # Try to import and initialize real recorder
            try:
                from ....infrastructure.audio.audio_recorder import AudioRecorder

                self.recorder = AudioRecorder()
                self.logger.info("Real audio recorder initialized")
            except ImportError:
                # Use mock recorder for testing
                self.recorder = MockAudioRecorder()
                self.logger.info("Using mock audio recorder")

            # Configure recorder
            self._configure_recorder()

        except Exception as e:
            self.logger.error(f"Failed to initialize recorder: {e}")
            raise AudioSystemError(f"Recorder initialization failed: {e}")

    def _configure_recorder(self) -> None:
        """Configure recorder based on system settings."""
        try:
            if hasattr(self.recorder, "set_noise_reduction"):
                self.recorder.set_noise_reduction(self.config.noise_reduction_enabled)

            if hasattr(self.recorder, "set_sample_rate"):
                self.recorder.set_sample_rate(self.config.sample_rate)

            if hasattr(self.recorder, "set_channels"):
                self.recorder.set_channels(self.config.channels)

            self.logger.info("Audio recorder configured successfully")

        except Exception as e:
            self.logger.warning(f"Error configuring recorder: {e}")

    def record_audio(
        self,
        duration: Optional[int] = None,
        session: Optional[AudioSession] = None,
        format_type: Optional[AudioFormatType] = None,
    ) -> Optional[Tuple[np.ndarray, Dict[str, Any]]]:
        """
        Record audio with specified parameters.

        Args:
            duration: Recording duration in seconds
            session: Active audio session
            format_type: Desired audio format

        Returns:
            Tuple of (audio_data, metadata) or None if failed
        """
        if self._is_recording:
            self.logger.warning("Recording already in progress")
            return None

        try:
            # Set defaults
            if duration is None:
                duration = self.config.default_record_duration
            if format_type is None:
                format_type = self.config.default_output_format

            # Validate duration
            duration = min(duration, self.config.max_record_duration)

            # Start recording
            self._start_recording(duration, session)

            # Record audio data
            start_time = time.time()
            audio_data = self._perform_recording(duration)
            processing_time = time.time() - start_time

            if audio_data is None or len(audio_data) == 0:
                self.logger.error("No audio data recorded")
                return None

            # Create metadata
            metadata = self._create_recording_metadata(duration, session, format_type, processing_time)

            # Update metrics
            self.metrics.increment_recordings(processing_time)
            self.metrics.record_format_usage(format_type.value)

            # Update session if provided
            if session:
                session.add_recording(len(audio_data) / self.config.sample_rate)

            self.logger.info(f"Successfully recorded {len(audio_data)} samples")
            return audio_data, metadata

        except Exception as e:
            error_msg = f"Recording failed: {e}"
            self.logger.error(error_msg)
            self.metrics.increment_errors(error_msg)
            return None

        finally:
            self._stop_recording()

    def _start_recording(self, duration: int, session: Optional[AudioSession]) -> None:
        """Start recording process."""
        self._is_recording = True
        self._current_recording_session = session

        self.logger.info(f"Starting recording for {duration} seconds")

        # Trigger recording start event if needed
        # Could emit event here for other services to listen

    def _perform_recording(self, duration: int) -> Optional[np.ndarray]:
        """Perform the actual audio recording."""
        try:
            if hasattr(self.recorder, "record_audio"):
                return self.recorder.record_audio(duration)
            else:
                # Fallback mock recording
                return np.random.random(duration * self.config.sample_rate).astype(np.float32)

        except Exception as e:
            self.logger.error(f"Recording operation failed: {e}")
            return None

    def _stop_recording(self) -> None:
        """Stop recording process."""
        self._is_recording = False
        self._current_recording_session = None

        if hasattr(self.recorder, "stop_recording"):
            self.recorder.stop_recording()

    def _create_recording_metadata(
        self, duration: int, session: Optional[AudioSession], format_type: AudioFormatType, processing_time: float
    ) -> Dict[str, Any]:
        """Create metadata for recorded audio."""
        return {
            "recording_id": f"rec_{int(time.time())}",
            "format": format_type.value,
            "requested_duration": duration,
            "sample_rate": self.config.sample_rate,
            "channels": self.config.channels,
            "created_at": datetime.now().isoformat(),
            "processing_time": processing_time,
            "session_id": session.session_id if session else None,
            "child_id": session.child_id if session else None,
            "recording_type": "user_input",
            "noise_reduction": self.config.noise_reduction_enabled,
            "voice_activity_detection": self.config.voice_activity_detection,
        }

    def is_recording(self) -> bool:
        """Check if currently recording."""
        return self._is_recording

    def stop_recording(self) -> bool:
        """Stop current recording if active."""
        if not self._is_recording:
            return False

        try:
            self._stop_recording()
            self.logger.info("Recording stopped by user request")
            return True

        except Exception as e:
            self.logger.error(f"Error stopping recording: {e}")
            return False

    def get_recording_status(self) -> Dict[str, Any]:
        """Get current recording status."""
        return {
            "is_recording": self._is_recording,
            "current_session": (
                self._current_recording_session.session_id if self._current_recording_session else None
            ),
            "config": {
                "default_duration": self.config.default_record_duration,
                "max_duration": self.config.max_record_duration,
                "sample_rate": self.config.sample_rate,
                "channels": self.config.channels,
                "noise_reduction": self.config.noise_reduction_enabled,
            },
        }

    def update_config(self, new_config: AudioSystemConfig) -> None:
        """Update recording configuration."""
        self.config = new_config
        self._configure_recorder()
        self.logger.info("Recording configuration updated")


class MockAudioRecorder:
    """Mock audio recorder for testing."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._recording = False

    def record_audio(self, duration: int) -> np.ndarray:
        """Mock audio recording."""
        self._recording = True
        time.sleep(0.1)  # Simulate recording time
        # Generate mock audio data
        sample_rate = 44100
        return np.random.random(duration * sample_rate).astype(np.float32)

    def is_recording(self) -> bool:
        """Check if recording."""
        return self._recording

    def stop_recording(self) -> None:
        """Stop recording."""
        self._recording = False

    def set_noise_reduction(self, enabled: bool) -> None:
        """Set noise reduction."""
        pass

    def set_sample_rate(self, rate: int) -> None:
        """Set sample rate."""
        pass

    def set_channels(self, channels: int) -> None:
        """Set number of channels."""
        pass
