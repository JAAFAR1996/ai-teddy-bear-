"""Audio playback service for AI Teddy Bear."""

import logging
import time
from pathlib import Path
from typing import Any, Callable, Dict, Optional

import numpy as np

from ....domain.audio.models import (
    AudioFormatType,
    AudioSession,
    AudioSystemConfig,
    PerformanceMetrics,
    PlaybackOptions,
)


class AudioPlaybackService:
    """Specialized service for audio playback operations."""

    def __init__(self, config: AudioSystemConfig, metrics: PerformanceMetrics):
        """Initialize audio playback service."""
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.metrics = metrics

        # Playback state
        self._is_playing = False
        self._current_playback_session = None
        self._playback_callbacks = []

        # Initialize playback components
        self._initialize_playback_systems()

    def _initialize_playback_systems(self) -> None:
        """Initialize various playback systems."""
        try:
            # Initialize pygame mixer
            self._init_pygame_mixer()

            # Initialize TTS system
            self._init_tts_system()

            self.logger.info("Audio playback systems initialized")

        except Exception as e:
            self.logger.error(f"Failed to initialize playback systems: {e}")

    def _init_pygame_mixer(self) -> None:
        """Initialize pygame mixer for audio playback."""
        try:
            import pygame

            pygame.mixer.pre_init(
                frequency=self.config.sample_rate,
                size=-16,
                channels=self.config.channels,
                buffer=1024,
            )
            pygame.mixer.init()
            self.pygame_available = True
            self.logger.info("Pygame mixer initialized successfully")
        except ImportError:
            self.pygame_available = False
            self.logger.warning(
                "Pygame not available - using alternative playback")
        except Exception as e:
            self.pygame_available = False
            self.logger.error(f"Error initializing pygame mixer: {e}")

    def _init_tts_system(self) -> None:
        """Initialize text-to-speech system."""
        try:
            from ....infrastructure.audio.tts_playback import TTSPlayback

            self.tts = TTSPlayback(
                on_playback_complete=self._on_playback_complete)
            self.tts_available = True
        except ImportError:
            self.tts = MockTTSPlayback()
            self.tts_available = False
            self.logger.warning("Using mock TTS system")

    def _handle_playback(
        self,
        audio_data: Optional[np.ndarray],
        filename: Optional[str],
        volume: float,
        options: PlaybackOptions,
        format_hint: Optional[AudioFormatType] = None,
    ) -> bool:
        """Handles the actual playback logic."""
        if filename:
            return self._play_audio_file(
                filename,
                volume,
                options.loop,
                options.fade_in,
                options.fade_out,
                format_hint,
            )
        elif audio_data is not None:
            return self._play_audio_array(
                audio_data, volume, options.loop, options.fade_in, options.fade_out
            )
        return False

    def play_audio(
        self,
        audio_data: Optional[np.ndarray] = None,
        filename: Optional[str] = None,
        session: Optional[AudioSession] = None,
        format_hint: Optional[AudioFormatType] = None,
        options: Optional[PlaybackOptions] = None,
    ) -> bool:
        """Play audio from data or file."""
        options = options or PlaybackOptions()

        if self._is_playing and not options.loop:
            self.logger.warning("Playback already in progress")
            return False

        if audio_data is None and filename is None:
            self.logger.error("Either audio_data or filename must be provided")
            return False

        try:
            volume = (
                options.volume
                if options.volume is not None
                else self.config.volume_level
            )

            self._start_playback(session)

            success = self._handle_playback(
                audio_data, filename, volume, options, format_hint
            )

            if success:
                self.metrics.increment_playbacks()
                if format_hint:
                    self.metrics.record_format_usage(format_hint.value)
                self.logger.info("Audio playback started successfully")
            else:
                self._stop_playback()

            return success

        except Exception as e:
            error_msg = f"Playback failed: {e}"
            self.logger.error(error_msg)
            self.metrics.increment_errors(error_msg)
            self._stop_playback()
            return False

    def speak(
        self,
        text: str,
        language: Optional[str] = None,
        speed: float = 1.0,
        volume: Optional[float] = None,
        cache: bool = True,
        session: Optional[AudioSession] = None,
        voice_style: str = "friendly",
    ) -> bool:
        """Convert text to speech and play."""
        if not text.strip():
            self.logger.warning("Empty text provided for TTS")
            return False

        try:
            # Set defaults
            if language is None:
                language = self.config.language_preference
            if volume is None:
                volume = self.config.volume_level

            # Validate for child safety
            if self.config.child_safe_mode:
                if not self._validate_child_safe_text(text):
                    self.logger.warning("Text failed child safety validation")
                    return False

            # Start TTS playback
            self._start_playback(session)

            success = self.tts.speak(
                text=text,
                language=language,
                speed=speed,
                volume=volume,
                cache=cache,
                voice_style=voice_style,
            )

            if success:
                self.metrics.increment_playbacks()
                self.logger.info(f"TTS started for text: {text[:50]}...")
            else:
                self._stop_playback()

            return success

        except Exception as e:
            error_msg = f"TTS failed: {e}"
            self.logger.error(error_msg)
            self.metrics.increment_errors(error_msg)
            self._stop_playback()
            return False

    def stop_playback(self) -> bool:
        """Stop current playback."""
        if not self._is_playing:
            return False

        try:
            # Stop pygame playback
            if self.pygame_available:
                import pygame

                pygame.mixer.stop()

            # Stop TTS
            if hasattr(self.tts, "stop"):
                self.tts.stop()

            self._stop_playback()
            self.logger.info("Playback stopped")
            return True

        except Exception as e:
            self.logger.error(f"Error stopping playback: {e}")
            return False

    def is_playing(self) -> bool:
        """Check if currently playing audio."""
        return self._is_playing

    def _start_playback(self, session: Optional[AudioSession]) -> None:
        """Start playback process."""
        self._is_playing = True
        self._current_playback_session = session

    def _stop_playback(self) -> None:
        """Stop playback process."""
        self._is_playing = False
        self._current_playback_session = None

        # Trigger completion callbacks
        for callback in self._playback_callbacks:
            try:
                callback()
            except Exception as e:
                self.logger.error(f"Playback callback error: {e}")

    def _on_playback_complete(self) -> None:
        """Handle playback completion."""
        self._stop_playback()
        self.logger.info("Playback completed")

    def _play_audio_file(
        self,
        filename: str,
        volume: float,
        loop: bool,
        fade_in: float,
        fade_out: float,
        format_hint: Optional[AudioFormatType] = None,
    ) -> bool:
        """Play audio from file."""
        try:
            if not Path(filename).exists():
                self.logger.error(f"Audio file not found: {filename}")
                return False

            # Try pygame first
            if self.pygame_available:
                return self._play_with_pygame(filename, volume, loop)
            else:
                return self._play_basic(filename, volume)

        except Exception as e:
            self.logger.error(f"File playback error: {e}")
            return False

    def _play_audio_array(
        self,
        audio_data: np.ndarray,
        volume: float,
        loop: bool,
        fade_in: float,
        fade_out: float,
    ) -> bool:
        """Play audio from numpy array."""
        try:
            # Apply volume
            audio_data = audio_data * volume

            # Apply fades if specified
            if fade_in > 0 or fade_out > 0:
                audio_data = self._apply_fades(audio_data, fade_in, fade_out)

            # Use pygame if available
            if self.pygame_available:
                return self._play_array_with_pygame(audio_data, loop)
            else:
                self.logger.warning("Array playback requires pygame")
                return False

        except Exception as e:
            self.logger.error(f"Array playback error: {e}")
            return False

    def _play_with_pygame(
            self,
            filename: str,
            volume: float,
            loop: bool) -> bool:
        """Play audio file using pygame."""
        try:
            import pygame

            sound = pygame.mixer.Sound(filename)
            sound.set_volume(volume)

            loops = -1 if loop else 0
            sound.play(loops=loops)
            return True

        except Exception as e:
            self.logger.error(f"Pygame playback error: {e}")
            return False

    def _play_basic(self, filename: str, volume: float) -> bool:
        """Basic audio playback fallback."""
        self.logger.info(f"Mock playback: {filename} at volume {volume}")
        return True

    def _play_array_with_pygame(
            self,
            audio_data: np.ndarray,
            loop: bool) -> bool:
        """Play numpy array using pygame."""
        self.logger.warning("Pygame array playback not fully implemented")
        return False

    def _apply_fades(
        self, audio_data: np.ndarray, fade_in: float, fade_out: float
    ) -> np.ndarray:
        """Apply fade in/out effects to audio data."""
        if len(audio_data) == 0:
            return audio_data

        result = audio_data.copy()
        samples = len(audio_data)
        sample_rate = self.config.sample_rate

        # Apply fade in
        if fade_in > 0:
            fade_samples = int(fade_in * sample_rate)
            fade_samples = min(fade_samples, samples // 2)

            for i in range(fade_samples):
                result[i] *= i / fade_samples

        # Apply fade out
        if fade_out > 0:
            fade_samples = int(fade_out * sample_rate)
            fade_samples = min(fade_samples, samples // 2)

            for i in range(fade_samples):
                result[samples - 1 - i] *= i / fade_samples

        return result

    def _validate_child_safe_text(self, text: str) -> bool:
        """Validate text for child safety."""
        unsafe_words = ["password", "address", "phone", "secret"]
        text_lower = text.lower()

        for word in unsafe_words:
            if word in text_lower:
                return False

        return True

    def add_playback_callback(self, callback: Callable[[], None]) -> None:
        """Add callback for playback completion."""
        self._playback_callbacks.append(callback)

    def remove_playback_callback(self, callback: Callable[[], None]) -> None:
        """Remove playback callback."""
        if callback in self._playback_callbacks:
            self._playback_callbacks.remove(callback)

    def get_playback_status(self) -> Dict[str, Any]:
        """Get current playback status."""
        return {
            "is_playing": self._is_playing,
            "current_session": (
                self._current_playback_session.session_id
                if self._current_playback_session
                else None
            ),
            "volume": self.config.volume_level,
            "pygame_available": self.pygame_available,
            "tts_available": self.tts_available,
        }


class MockTTSPlayback:
    """Mock TTS playback for testing."""

    def __init__(self, on_playback_complete=None):
        self.logger = logging.getLogger(__name__)
        self.on_playback_complete = on_playback_complete
        self._playing = False

    def speak(
        self,
        text: str,
        language: str = "en",
        speed: float = 1.0,
        volume: float = 1.0,
        cache: bool = True,
        voice_style: str = "friendly",
    ) -> bool:
        """Mock TTS speak."""
        self._playing = True
        self.logger.info(f"Mock TTS: {text[:50]}...")

        # Simulate TTS processing time
        time.sleep(0.1)

        # Call completion callback
        if self.on_playback_complete:
            self.on_playback_complete()

        return True

    def is_playing(self) -> bool:
        """Check if playing."""
        return self._playing

    def stop(self) -> None:
        """Stop TTS."""
        self._playing = False

    def set_volume(self, volume: float) -> None:
        """Set volume."""
        pass
