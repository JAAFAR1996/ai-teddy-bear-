"""Enhanced high-level audio system manager for AI Teddy Bear."""

import logging
import asyncio
import threading
import time
import os
import traceback
from typing import Optional, List, Tuple, Callable, Dict, Any, Union
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from datetime import datetime, timedelta
import numpy as np
import json

# Audio processing imports
try:
    import soundfile as sf
    import librosa
    import pydub
    from pydub import AudioSegment
    from pydub.playback import play
    import pygame
    import io
    AUDIO_LIBS_AVAILABLE = True
except ImportError:
    AUDIO_LIBS_AVAILABLE = False
    logger.warning("⚠️ Audio libraries not available. Some features will be limited.")

# Try to import local audio components
try:
    from .audio_recorder import AudioRecorder
    from .audio_processing import AudioProcessor, process_audio
    from .audio_io import AudioIO, AudioFormat, AudioQuality, AudioMetadata
    from .tts_playback import TTSPlayback
    from .state_manager import state_manager, StateChangeEvent, AudioState
    LOCAL_AUDIO_AVAILABLE = True
except ImportError:
    LOCAL_AUDIO_AVAILABLE = False
    logger.warning("⚠️ Local audio components not fully available")


class AudioSessionType(Enum):
    """Types of audio sessions."""
    CONVERSATION = "conversation"
    STORY_TELLING = "story_telling"
    LEARNING = "learning"
    PLAY_TIME = "play_time"
    EMERGENCY = "emergency"
    SYSTEM_TEST = "system_test"


class AudioQualityMode(Enum):
    """Audio quality modes for different scenarios."""
    POWER_SAVE = "power_save"      # Low quality, minimal processing
    BALANCED = "balanced"          # Good quality, moderate processing
    HIGH_QUALITY = "high_quality"  # Best quality, full processing
    ADAPTIVE = "adaptive"          # Auto-adjust based on conditions


class AudioFormatType(Enum):
    """Supported audio formats."""
    WAV = "wav"
    MP3 = "mp3"
    OPUS = "opus"
    OGG = "ogg"
    FLAC = "flac"
    M4A = "m4a"


@dataclass
class AudioSession:
    """Audio session information."""
    session_id: str
    session_type: AudioSessionType
    child_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_recordings: int = 0
    total_duration: float = 0.0
    quality_mode: AudioQualityMode = AudioQualityMode.BALANCED
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class AudioSystemConfig:
    """Audio system configuration."""
    default_record_duration: int = 10
    max_record_duration: int = 60
    auto_process_audio: bool = True
    auto_save_sessions: bool = True
    noise_reduction_enabled: bool = True
    voice_activity_detection: bool = True
    adaptive_quality: bool = True
    emergency_override: bool = True
    session_timeout_minutes: int = 30
    max_concurrent_sessions: int = 3
    volume_level: float = 0.8
    language_preference: str = "en"
    child_safe_mode: bool = True
    # New audio format settings
    default_output_format: AudioFormatType = AudioFormatType.WAV
    sample_rate: int = 44100
    channels: int = 2
    bitrate: int = 192  # For compressed formats
    compression_quality: int = 5  # 0-10 scale
    enable_cloud_sync: bool = True
    cloud_backup_enabled: bool = True


class AudioSystemError(Exception):
    """Audio system specific error."""
    pass


class EnhancedAudioManager:
    """Enhanced audio system manager with modern format support and cloud integration."""

    def __init__(self, config: Optional[AudioSystemConfig] = None):
        """
        Initialize enhanced audio manager.

        Args:
            config: Audio system configuration
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or AudioSystemConfig()

        # Initialize pygame mixer for audio playback
        self._init_pygame_mixer()

        # Component initialization
        self._initialize_components()

        # Session management
        self.active_sessions: Dict[str, AudioSession] = {}
        self.current_session: Optional[AudioSession] = None
        self._session_lock = threading.Lock()

        # Performance monitoring
        self.performance_stats = {
            "total_recordings": 0,
            "total_playbacks": 0,
            "total_errors": 0,
            "average_processing_time": 0.0,
            "last_error": None,
            "uptime_start": datetime.now(),
            "formats_supported": list(AudioFormatType),
            "cloud_syncs": 0,
            "cache_hits": 0
        }

        # Audio file management
        self.audio_cache: Dict[str, bytes] = {}
        self.temp_files: List[Path] = []
        self.log_directory = Path("logs/audio")
        
        # Cloud integration
        self.cloud_sync_enabled = self.config.enable_cloud_sync
        self.cloud_queue: List[Dict[str, Any]] = []

        # Event callbacks
        self.event_callbacks: Dict[str, List[Callable]] = {
            "session_start": [],
            "session_end": [],
            "recording_start": [],
            "recording_end": [],
            "playback_start": [],
            "playback_end": [],
            "error": [],
            "quality_change": [],
            "format_change": [],
            "cloud_sync": []
        }

        # Background tasks
        self._monitoring_task = None
        self._cleanup_task = None
        self._cloud_sync_task = None
        self._start_background_tasks()

        # Register state observers if available
        if LOCAL_AUDIO_AVAILABLE:
            state_manager.add_observer("error", self._handle_error)
            state_manager.add_observer("recording_change", self._handle_recording_state)
            state_manager.add_observer("playback_change", self._handle_playback_state)

        self.logger.info("Enhanced audio manager initialized with modern format support")

    def _init_pygame_mixer(self) -> Any:
        """Initialize pygame mixer for audio playback."""
        try:
            import pygame
            pygame.mixer.pre_init(
                frequency=self.config.sample_rate,
                size=-16,
                channels=self.config.channels,
                buffer=1024
            )
            pygame.mixer.init()
            self.pygame_available = True
            self.logger.info("Pygame mixer initialized successfully")
        except ImportError:
            self.pygame_available = False
            self.logger.warning("Pygame not available - limited audio playback support")
        except Exception as e:
            self.pygame_available = False
            self.logger.error(f"Error initializing pygame mixer: {e}")

    def _initialize_components(self) -> Any:
        """Initialize audio system components."""
        try:
            # Initialize core components if available
            if LOCAL_AUDIO_AVAILABLE:
                try:
                    self.recorder = AudioRecorder()
                    self.processor = AudioProcessor()
                    self.audio_io = AudioIO(auto_cleanup=True)
                    self.tts = TTSPlayback(on_playback_complete=self._on_playback_complete)
                except Exception as e:
                    self.logger.warning(f"Some audio components failed to initialize: {e}")
                    # Create mock components
                    self._create_mock_components()
            else:
                self._create_mock_components()

            # Configure components based on settings
            self._configure_components()

        except Exception as e:
            self.logger.error(f"Error initializing audio components: {e}")
            raise AudioSystemError(f"Failed to initialize audio system: {e}")

    def _create_mock_components(self) -> Any:
        """Create mock components for testing when real components aren't available."""
        self.recorder = MockAudioRecorder()
        self.processor = MockAudioProcessor()
        self.audio_io = MockAudioIO()
        self.tts = MockTTSPlayback()
        self.logger.info("Using mock audio components")

    def _configure_components(self) -> Any:
        """Configure components based on current settings."""
        try:
            # Configure recorder
            if hasattr(self.recorder, 'set_noise_reduction'):
                self.recorder.set_noise_reduction(self.config.noise_reduction_enabled)

            # Configure TTS volume
            if hasattr(self.tts, 'set_volume'):
                self.tts.set_volume(self.config.volume_level)

            # Configure processor for child-safe mode
            if hasattr(self.processor, 'set_child_safe_mode'):
                self.processor.set_child_safe_mode(self.config.child_safe_mode)

        except Exception as e:
            self.logger.warning(f"Error configuring components: {e}")

    def _start_background_tasks(self) -> Any:
        """Start background monitoring and cleanup tasks."""
        def monitoring_worker() -> Any:
            while True:
                try:
                    time.sleep(30)  # Check every 30 seconds
                    self._check_session_timeouts()
                    self._update_performance_stats()
                    self._check_system_health()
                except Exception as e:
                    self.logger.error(f"Monitoring worker error: {e}")

        def cleanup_worker() -> Any:
            while True:
                try:
                    time.sleep(300)  # Clean up every 5 minutes
                    self._cleanup_old_sessions()
                    self._cleanup_temp_files()
                    self._cleanup_audio_cache()
                except Exception as e:
                    self.logger.error(f"Cleanup worker error: {e}")

        def cloud_sync_worker() -> Any:
            while True:
                try:
                    time.sleep(60)  # Sync every minute
                    if self.cloud_sync_enabled:
                        self._process_cloud_queue()
                except Exception as e:
                    self.logger.error(f"Cloud sync worker error: {e}")

        # Start daemon threads
        self._monitoring_task = threading.Thread(target=monitoring_worker, daemon=True)
        self._cleanup_task = threading.Thread(target=cleanup_worker, daemon=True)
        self._cloud_sync_task = threading.Thread(target=cloud_sync_worker, daemon=True)

        self._monitoring_task.start()
        self._cleanup_task.start()
        self._cloud_sync_task.start()

    def start_session(
        self,
        child_id: str,
        session_type: AudioSessionType = AudioSessionType.CONVERSATION,
        quality_mode: AudioQualityMode = AudioQualityMode.BALANCED
    ) -> str:
        """
        Start a new audio session.

        Args:
            child_id: Child identifier
            session_type: Type of audio session
            quality_mode: Audio quality mode

        Returns:
            Session ID
        """
        try:
            with self._session_lock:
                # Check concurrent session limit
                if len(self.active_sessions) >= self.config.max_concurrent_sessions:
                    # End oldest session
                    oldest_session_id = min(
                        self.active_sessions.keys(),
                        key=lambda sid: self.active_sessions[sid].start_time
                    )
                    self.end_session(oldest_session_id)

                # Create new session
                session_id = f"session_{child_id}_{int(time.time())}"
                session = AudioSession(
                    session_id=session_id,
                    session_type=session_type,
                    child_id=child_id,
                    start_time=datetime.now(),
                    quality_mode=quality_mode
                )

                self.active_sessions[session_id] = session
                self.current_session = session

                # Configure quality mode
                self._set_quality_mode(quality_mode)

                # Trigger callbacks
                self._trigger_event("session_start", {
                    "session_id": session_id,
                    "child_id": child_id,
                    "session_type": session_type.value
                })

                self.logger.info(
                    f"Started audio session {session_id} for child {child_id}")
                return session_id

        except Exception as e:
            self.logger.error(f"Error starting session: {e}")
            raise AudioSystemError(f"Failed to start session: {e}")

    def end_session(self, session_id: str) -> bool:
        """
        End an audio session.

        Args:
            session_id: Session to end

        Returns:
            Success status
        """
        try:
            with self._session_lock:
                if session_id not in self.active_sessions:
                    self.logger.warning(f"Session {session_id} not found")
                    return False

                session = self.active_sessions[session_id]
                session.end_time = datetime.now()

                # Save session data if configured
                if self.config.auto_save_sessions:
                    self._save_session_data(session)

                # Remove from active sessions
                del self.active_sessions[session_id]

                # Update current session
                if self.current_session and self.current_session.session_id == session_id:
                    self.current_session = None

                # Trigger callbacks
                self._trigger_event("session_end", {
                    "session_id": session_id,
                    "duration": (session.end_time - session.start_time).total_seconds(),
                    "recordings": session.total_recordings
                })

                self.logger.info(f"Ended audio session {session_id}")
                return True

        except Exception as e:
            self.logger.error(f"Error ending session: {e}")
            return False

    def record_audio(
        self,
        duration: Optional[int] = None,
        process: bool = None,
        save: bool = None,
        filename: Optional[str] = None,
        session_id: Optional[str] = None,
        format: AudioFormatType = None
    ) -> Optional[Tuple[np.ndarray, Dict[str, Any]]]:
        """
        Enhanced record audio with format support.

        Args:
            duration: Recording duration (uses config default if None)
            process: Whether to process audio (uses config default if None)
            save: Whether to save audio (uses config default if None)
            filename: Custom filename for saving
            session_id: Session to associate recording with
            format: Audio format for saving

        Returns:
            Tuple of (audio_data, metadata) or None
        """
        try:
            # Use configuration defaults
            if duration is None:
                duration = self.config.default_record_duration
            if process is None:
                process = self.config.auto_process_audio
            if save is None:
                save = self.config.auto_save_sessions
            if format is None:
                format = self.config.default_output_format

            # Validate duration
            duration = min(duration, self.config.max_record_duration)

            # Check if already recording
            if hasattr(self.recorder, 'is_recording') and self.recorder.is_recording():
                self.logger.warning("Recording already in progress")
                return None

            # Get or create session
            session = self._get_session(session_id)

            # Trigger recording start event
            self._trigger_event("recording_start", {
                "duration": duration,
                "session_id": session.session_id if session else None,
                "format": format.value
            })

            start_time = time.time()

            # Record audio
            self.logger.info(f"Starting recording for {duration} seconds")
            if hasattr(self.recorder, 'record_audio'):
                audio_data = self.recorder.record_audio(duration)
            else:
                # Mock recording
                audio_data = np.random.random(duration * self.config.sample_rate).astype(np.float32)

            if audio_data is None or len(audio_data) == 0:
                self.logger.error("No audio data recorded")
                return None

            # Create metadata
            metadata = {
                "filename": filename or "recording",
                "format": format.value,
                "duration": len(audio_data) / self.config.sample_rate,
                "sample_rate": self.config.sample_rate,
                "channels": 1,
                "created_at": datetime.now().isoformat(),
                "session_id": session.session_id if session else None,
                "child_id": session.child_id if session else None,
                "recording_type": "user_input"
            }

            # Process audio if requested
            if process and hasattr(self.processor, 'process'):
                if LOCAL_AUDIO_AVAILABLE:
                    state_manager.set_processing(True)
                try:
                    processed_audio = self.processor.process(audio_data)
                    if processed_audio is not None:
                        audio_data = processed_audio
                        metadata["processed"] = True
                finally:
                    if LOCAL_AUDIO_AVAILABLE:
                        state_manager.set_processing(False)

            # Save if requested
            if save:
                if filename is None:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    child_id = session.child_id if session else "unknown"
                    filename = f"recording_{child_id}_{timestamp}.{format.value}"

                success = self.save_audio(
                    audio_data,
                    filename,
                    format=format,
                    metadata=metadata,
                    session_id=session_id
                )
                
                if success:
                    metadata["filename"] = filename

            # Update session stats
            if session:
                session.total_recordings += 1
                session.total_duration += metadata["duration"]

            # Update performance stats
            processing_time = time.time() - start_time
            self.performance_stats["total_recordings"] += 1
            self._update_avg_processing_time(processing_time)

            # Trigger recording end event
            self._trigger_event("recording_end", {
                "duration": metadata["duration"],
                "processing_time": processing_time,
                "session_id": session.session_id if session else None,
                "saved": save and success if save else False
            })

            self.logger.info(f"Recording completed: {metadata['duration']:.2f}s")
            return audio_data, metadata

        except Exception as e:
            self.logger.error(f"Error recording audio: {e}")
            self.performance_stats["total_errors"] += 1
            self.performance_stats["last_error"] = str(e)
            if LOCAL_AUDIO_AVAILABLE:
                state_manager.set_error(str(e))
            return None

    def play_audio(
        self,
        audio_data: Optional[np.ndarray] = None,
        filename: Optional[str] = None,
        volume: Optional[float] = None,
        session_id: Optional[str] = None,
        format_hint: Optional[AudioFormatType] = None,
        loop: bool = False,
        fade_in: float = 0.0,
        fade_out: float = 0.0
    ) -> bool:
        """
        Enhanced audio playback with modern format support.

        Args:
            audio_data: Audio data to play (numpy array)
            filename: Audio file to play
            volume: Playback volume (0.0-1.0)
            session_id: Session to associate playback with
            format_hint: Hint about audio format for optimization
            loop: Whether to loop the audio
            fade_in: Fade in duration in seconds
            fade_out: Fade out duration in seconds

        Returns:
            Success status
        """
        try:
            # Check inputs
            if audio_data is None and filename is None:
                raise ValueError("Must provide audio_data or filename")

            # Get session info
            session = self._get_session(session_id)
            play_volume = volume or self.config.volume_level

            # Trigger playback start event
            self._trigger_event("playback_start", {
                "session_id": session.session_id if session else None,
                "volume": play_volume,
                "has_audio_data": audio_data is not None,
                "filename": filename,
                "format_hint": format_hint.value if format_hint else None
            })

            start_time = time.time()
            success = False

            # Play from file
            if filename:
                success = self._play_audio_file(
                    filename, play_volume, loop, fade_in, fade_out, format_hint
                )
                duration = self._get_audio_duration(filename)
            
            # Play from numpy array
            elif audio_data is not None:
                success = self._play_audio_array(
                    audio_data, play_volume, loop, fade_in, fade_out
                )
                duration = len(audio_data) / self.config.sample_rate

            # Update performance stats
            playback_time = time.time() - start_time
            if success:
                self.performance_stats["total_playbacks"] += 1

            # Trigger playback end event
            self._trigger_event("playback_end", {
                "session_id": session.session_id if session else None,
                "success": success,
                "duration": duration,
                "actual_time": playback_time
            })

            if success:
                self.logger.info(f"Audio playback successful ({duration:.2f}s)")
            else:
                self.logger.error("Audio playback failed")

            return success

        except Exception as e:
            self.logger.error(f"Error playing audio: {e}")
            self.performance_stats["total_errors"] += 1
            self.performance_stats["last_error"] = str(e)
            
            if LOCAL_AUDIO_AVAILABLE:
                state_manager.set_error(str(e))
            
            self._trigger_event("error", {
                "type": "playback_error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            return False

    def save_audio(
        self,
        audio_data: np.ndarray,
        filename: str,
        format: AudioFormatType = None,
        quality: int = None,
        metadata: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
        cloud_sync: bool = None
    ) -> bool:
        """
        Enhanced audio saving with modern format support.

        Args:
            audio_data: Audio data to save
            filename: Output filename
            format: Audio format (auto-detect from extension if None)
            quality: Compression quality (0-10, format dependent)
            metadata: Additional metadata to embed
            session_id: Session to associate with
            cloud_sync: Whether to sync to cloud

        Returns:
            Success status
        """
        try:
            # Auto-detect format from filename if not specified
            if format is None:
                format = self._detect_audio_format(filename)

            # Use default quality if not specified
            if quality is None:
                quality = self.config.compression_quality

            # Use config cloud sync setting if not specified
            if cloud_sync is None:
                cloud_sync = self.config.cloud_backup_enabled

            # Ensure parent directory exists
            file_path = Path(filename)
            file_path.parent.mkdir(parents=True, exist_ok=True)

            start_time = time.time()

            # Save based on format
            success = False
            if format == AudioFormatType.WAV:
                success = self._save_wav(audio_data, filename, metadata)
            elif format == AudioFormatType.MP3:
                success = self._save_mp3(audio_data, filename, quality, metadata)
            elif format == AudioFormatType.OPUS:
                success = self._save_opus(audio_data, filename, quality, metadata)
            elif format == AudioFormatType.OGG:
                success = self._save_ogg(audio_data, filename, quality, metadata)
            elif format == AudioFormatType.FLAC:
                success = self._save_flac(audio_data, filename, metadata)
            else:
                # Fallback to WAV
                success = self._save_wav(audio_data, filename, metadata)

            if success:
                # Add to temp files list for cleanup
                self.temp_files.append(file_path)

                # Add to cloud sync queue if enabled
                if cloud_sync:
                    self._add_to_cloud_queue(filename, session_id, metadata)

                save_time = time.time() - start_time
                file_size = file_path.stat().st_size

                self.logger.info(f"Audio saved: {filename} ({format.value}, {file_size} bytes, {save_time:.2f}s)")

                # Trigger save event
                self._trigger_event("audio_saved", {
                    "filename": filename,
                    "format": format.value,
                    "size_bytes": file_size,
                    "save_time": save_time,
                    "session_id": session_id,
                    "cloud_sync": cloud_sync
                })

            return success

        except Exception as e:
            self.logger.error(f"Error saving audio: {e}")
            self.performance_stats["total_errors"] += 1
            self.performance_stats["last_error"] = str(e)
            return False

    def speak(
        self,
        text: str,
        language: Optional[str] = None,
        speed: float = 1.0,
        volume: Optional[float] = None,
        cache: bool = True,
        session_id: Optional[str] = None,
        voice_style: str = "friendly"
    ) -> bool:
        """
        Enhanced text-to-speech with session support.

        Args:
            text: Text to speak
            language: Language code (uses config default if None)
            speed: Speech speed multiplier
            volume: Speech volume (0.0-1.0)
            cache: Whether to cache generated speech
            session_id: Session to associate speech with
            voice_style: Voice style for emotional context

        Returns:
            Success status
        """
        try:
            # Use configuration defaults
            if language is None:
                language = self.config.language_preference

            # Get session info
            session = self._get_session(session_id)

            # Set volume if specified
            if volume is not None:
                volume = max(0.0, min(1.0, volume))
                if hasattr(self.tts, 'set_volume'):
                    self.tts.set_volume(volume)

            # Add session context to TTS metadata
            tts_metadata = {
                "session_id": session.session_id if session else None,
                "child_id": session.child_id if session else None,
                "timestamp": datetime.now().isoformat(),
                "voice_style": voice_style
            }

            # Generate and play speech
            if hasattr(self.tts, 'speak_with_metadata'):
                success = self.tts.speak_with_metadata(
                    text, language, speed, cache, tts_metadata
                )
            elif hasattr(self.tts, 'speak'):
                success = self.tts.speak(text, language, speed, cache)
            else:
                # Mock TTS
                self.logger.info(f"Mock TTS: '{text}' in {language}")
                time.sleep(len(text) * 0.05)  # Simulate speech duration
                success = True

            if success:
                self.logger.info(f"TTS completed for session {session.session_id if session else 'none'}")

            return success

        except Exception as e:
            self.logger.error(f"Error in text-to-speech: {e}")
            self.performance_stats["total_errors"] += 1
            self.performance_stats["last_error"] = str(e)
            if LOCAL_AUDIO_AVAILABLE:
                state_manager.set_error(str(e))
            return False

    def stop_all(self, session_id -> Any: Optional[str] = None) -> Any:
        """
        Stop all audio operations, optionally for specific session.

        Args:
            session_id: Specific session to stop (None for all)
        """
        try:
            if session_id:
                self.logger.info(f"Stopping audio operations for session {session_id}")
            else:
                self.logger.info("Stopping all audio operations")

            # Stop recording
            if hasattr(self.recorder, 'is_recording') and self.recorder.is_recording():
                if hasattr(self.recorder, 'stop_recording'):
                    self.recorder.stop_recording()

            # Stop playback
            if self.pygame_available:
                import pygame
                pygame.mixer.stop()
                pygame.mixer.music.stop()

            # Stop TTS
            if hasattr(self.tts, 'is_playing') and self.tts.is_playing():
                if hasattr(self.tts, 'stop'):
                    self.tts.stop()

            # Stop any ongoing processing
            if LOCAL_AUDIO_AVAILABLE:
                state_manager.set_processing(False)

            self.logger.info("Audio operations stopped successfully")

        except Exception as e:
            self.logger.error(f"Error stopping operations: {e}")
            if LOCAL_AUDIO_AVAILABLE:
                state_manager.set_error(str(e))

    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about an audio session.

        Args:
            session_id: Session ID

        Returns:
            Session information dictionary
        """
        if session_id not in self.active_sessions:
            return None

        session = self.active_sessions[session_id]
        current_duration = (datetime.now() - session.start_time).total_seconds()

        return {
            "session_id": session.session_id,
            "session_type": session.session_type.value,
            "child_id": session.child_id,
            "start_time": session.start_time.isoformat(),
            "current_duration": current_duration,
            "total_recordings": session.total_recordings,
            "total_audio_duration": session.total_duration,
            "quality_mode": session.quality_mode.value,
            "metadata": session.metadata
        }

    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics."""
        uptime = (datetime.now() - self.performance_stats["uptime_start"]).total_seconds()

        return {
            "performance": self.performance_stats.copy(),
            "uptime_seconds": uptime,
            "active_sessions": len(self.active_sessions),
            "current_session": self.current_session.session_id if self.current_session else None,
            "configuration": {
                "auto_process": self.config.auto_process_audio,
                "auto_save": self.config.auto_save_sessions,
                "noise_reduction": self.config.noise_reduction_enabled,
                "child_safe_mode": self.config.child_safe_mode,
                "volume_level": self.config.volume_level,
                "language": self.config.language_preference,
                "default_format": self.config.default_output_format.value,
                "sample_rate": self.config.sample_rate,
                "cloud_sync": self.config.enable_cloud_sync
            },
            "component_status": {
                "recorder_available": hasattr(self, 'recorder') and self.recorder is not None,
                "processor_available": hasattr(self, 'processor') and self.processor is not None,
                "tts_available": hasattr(self, 'tts') and self.tts is not None,
                "audio_io_available": hasattr(self, 'audio_io') and self.audio_io is not None,
                "pygame_available": self.pygame_available,
                "audio_libs_available": AUDIO_LIBS_AVAILABLE
            }
        }

    def get_supported_formats(self) -> List[str]:
        """Get list of supported audio formats."""
        formats = [format.value for format in AudioFormatType]
        
        # Filter based on available libraries
        if not AUDIO_LIBS_AVAILABLE:
            # Only WAV is available without external libraries
            formats = [AudioFormatType.WAV.value]
        
        return formats

    def get_format_info(self, format: AudioFormatType) -> Dict[str, Any]:
        """Get information about a specific audio format."""
        format_info = {
            AudioFormatType.WAV: {
                "name": "WAV",
                "description": "Uncompressed audio format",
                "compression": "None",
                "quality": "Lossless",
                "file_size": "Large",
                "compatibility": "Universal"
            },
            AudioFormatType.MP3: {
                "name": "MP3",
                "description": "Popular compressed audio format",
                "compression": "Lossy",
                "quality": "Good",
                "file_size": "Small",
                "compatibility": "Universal"
            },
            AudioFormatType.OPUS: {
                "name": "OPUS",
                "description": "Modern low-latency audio codec",
                "compression": "Lossy",
                "quality": "Excellent",
                "file_size": "Very Small",
                "compatibility": "Modern"
            },
            AudioFormatType.OGG: {
                "name": "OGG Vorbis",
                "description": "Open-source audio format",
                "compression": "Lossy",
                "quality": "Good",
                "file_size": "Small",
                "compatibility": "Good"
            },
            AudioFormatType.FLAC: {
                "name": "FLAC",
                "description": "Free lossless audio codec",
                "compression": "Lossless",
                "quality": "Perfect",
                "file_size": "Medium",
                "compatibility": "Good"
            }
        }
        
        return format_info.get(format, {
            "name": format.value.upper(),
            "description": "Audio format",
            "compression": "Unknown",
            "quality": "Unknown",
            "file_size": "Unknown",
            "compatibility": "Unknown"
        })

    def test_audio_system(self) -> Dict[str, Any]:
        """
        Comprehensive audio system test.

        Returns:
            Test results dictionary
        """
        test_results = {
            "overall_status": "unknown",
            "tests": {},
            "timestamp": datetime.now().isoformat()
        }

        try:
            self.logger.info("Starting comprehensive audio system test")

            # Test 1: Component initialization
            test_results["tests"]["component_init"] = {
                "recorder": hasattr(self, 'recorder') and self.recorder is not None,
                "processor": hasattr(self, 'processor') and self.processor is not None,
                "audio_io": hasattr(self, 'audio_io') and self.audio_io is not None,
                "tts": hasattr(self, 'tts') and self.tts is not None,
                "pygame": self.pygame_available
            }

            # Test 2: Format support
            try:
                supported_formats = self.get_supported_formats()
                test_results["tests"]["format_support"] = {
                    "status": len(supported_formats) > 0,
                    "formats": supported_formats,
                    "count": len(supported_formats)
                }
            except Exception as e:
                test_results["tests"]["format_support"] = {
                    "status": False,
                    "error": str(e)
                }

            # Test 3: Audio recording
            try:
                self.logger.info("Testing audio recording...")
                test_audio, test_metadata = self.record_audio(
                    duration=1, 
                    save=False, 
                    process=False
                )
                test_results["tests"]["recording"] = {
                    "status": test_audio is not None and len(test_audio) > 0,
                    "duration": test_metadata["duration"] if test_metadata else 0,
                    "sample_rate": test_metadata["sample_rate"] if test_metadata else 0
                }
            except Exception as e:
                test_results["tests"]["recording"] = {
                    "status": False,
                    "error": str(e)
                }

            # Test 4: Audio playback
            try:
                self.logger.info("Testing audio playback...")
                test_tone = np.sin(2 * np.pi * 440 * np.arange(8000) / self.config.sample_rate).astype(np.float32)
                playback_success = self.play_audio(test_tone)
                test_results["tests"]["playback"] = {
                    "status": playback_success,
                    "test_duration": len(test_tone) / self.config.sample_rate
                }
            except Exception as e:
                test_results["tests"]["playback"] = {
                    "status": False,
                    "error": str(e)
                }

            # Test 5: TTS
            try:
                self.logger.info("Testing text-to-speech...")
                tts_success = self.speak("Test audio system", cache=False)
                test_results["tests"]["tts"] = {
                    "status": tts_success,
                    "test_text": "Test audio system"
                }
            except Exception as e:
                test_results["tests"]["tts"] = {
                    "status": False,
                    "error": str(e)
                }

            # Test 6: File operations
            try:
                self.logger.info("Testing file operations...")
                test_audio = np.sin(2 * np.pi * 440 * np.arange(8000) / self.config.sample_rate).astype(np.float32)
                test_file = "test_audio_save.wav"
                save_success = self.save_audio(test_audio, test_file, AudioFormatType.WAV)
                
                # Clean up test file
                if Path(test_file).exists():
                    Path(test_file).unlink()
                
                test_results["tests"]["file_operations"] = {
                    "status": save_success,
                    "format": AudioFormatType.WAV.value
                }
            except Exception as e:
                test_results["tests"]["file_operations"] = {
                    "status": False,
                    "error": str(e)
                }

            # Determine overall status
            all_tests_passed = all(
                test.get("status", False) 
                for test in test_results["tests"].values()
            )
            test_results["overall_status"] = "pass" if all_tests_passed else "partial"

            self.logger.info(f"Audio system test completed: {test_results['overall_status']}")

        except Exception as e:
            test_results["overall_status"] = "fail"
            test_results["error"] = str(e)
            self.logger.error(f"Audio system test failed: {e}")

        return test_results

    def _set_quality_mode(self, quality_mode -> Any: AudioQualityMode) -> Any:
        """Set audio quality mode for all components."""
        try:
            quality_config = {
                AudioQualityMode.POWER_SAVE: {
                    "sample_rate": 16000,
                    "processing_level": "minimal",
                    "noise_reduction": False,
                    "compression_quality": 3
                },
                AudioQualityMode.BALANCED: {
                    "sample_rate": 22050,
                    "processing_level": "standard",
                    "noise_reduction": True,
                    "compression_quality": 5
                },
                AudioQualityMode.HIGH_QUALITY: {
                    "sample_rate": 44100,
                    "processing_level": "advanced",
                    "noise_reduction": True,
                    "compression_quality": 8
                },
                AudioQualityMode.ADAPTIVE: {
                    "sample_rate": 22050,
                    "processing_level": "adaptive",
                    "noise_reduction": True,
                    "compression_quality": 6
                }
            }

            config = quality_config[quality_mode]

            # Update system configuration
            self.config.sample_rate = config["sample_rate"]
            self.config.compression_quality = config["compression_quality"]

            # Configure components
            if hasattr(self.recorder, 'set_sample_rate'):
                self.recorder.set_sample_rate(config["sample_rate"])

            if hasattr(self.processor, 'set_processing_level'):
                self.processor.set_processing_level(config["processing_level"])

            if hasattr(self.recorder, 'set_noise_reduction'):
                self.recorder.set_noise_reduction(config["noise_reduction"])

            # Trigger quality change event
            self._trigger_event("quality_change", {
                "quality_mode": quality_mode.value,
                "config": config
            })

            self.logger.info(f"Set audio quality mode to {quality_mode.value}")

        except Exception as e:
            self.logger.error(f"Error setting quality mode: {e}")

    def _trigger_event(self, event_type -> Any: str, event_data -> Any: Dict[str, Any]) -> Any:
        """Trigger event callbacks."""
        try:
            if event_type in self.event_callbacks:
                for callback in self.event_callbacks[event_type]:
                    try:
                        callback(event_data)
                    except Exception as e:
                        self.logger.error(f"Error in event callback: {e}")
        except Exception as e:
            self.logger.error(f"Error triggering event {event_type}: {e}")

    def add_event_listener(self, event_type -> Any: str, callback -> Any: Callable[[Dict[str, Any]], None]) -> Any:
        """Add event listener."""
        if event_type not in self.event_callbacks:
            self.event_callbacks[event_type] = []
        self.event_callbacks[event_type].append(callback)

    def remove_event_listener(self, event_type -> Any: str, callback -> Any: Callable[[Dict[str, Any]], None]) -> Any:
        """Remove event listener."""
        if event_type in self.event_callbacks and callback in self.event_callbacks[event_type]:
            self.event_callbacks[event_type].remove(callback)

    def _check_session_timeouts(self) -> Any:
        """Check for session timeouts."""
        try:
            timeout_threshold = timedelta(minutes=self.config.session_timeout_minutes)
            current_time = datetime.now()

            sessions_to_end = []
            for session_id, session in self.active_sessions.items():
                if current_time - session.start_time > timeout_threshold:
                    sessions_to_end.append(session_id)

            for session_id in sessions_to_end:
                self.logger.info(f"Session {session_id} timed out")
                self.end_session(session_id)

        except Exception as e:
            self.logger.error(f"Error checking session timeouts: {e}")

    def _update_performance_stats(self) -> Any:
        """Update performance statistics."""
        try:
            # Add any performance monitoring logic here
            pass
        except Exception as e:
            self.logger.error(f"Error updating performance stats: {e}")

    def _check_system_health(self) -> Any:
        """Check overall system health."""
        try:
            # Check component health
            issues = []

            if not hasattr(self, 'recorder') or self.recorder is None:
                issues.append("Audio recorder not available")

            if not hasattr(self, 'tts') or self.tts is None:
                issues.append("TTS system not available")

            if not self.pygame_available and not AUDIO_LIBS_AVAILABLE:
                issues.append("No audio playback libraries available")

            if issues:
                self.logger.warning(f"System health issues: {issues}")

            # Check cloud sync queue size
            if len(self.cloud_queue) > 100:
                self.logger.warning(f"Cloud sync queue is large: {len(self.cloud_queue)} items")

        except Exception as e:
            self.logger.error(f"Error checking system health: {e}")

    def _update_avg_processing_time(self, new_time -> Any: float) -> Any:
        """Update average processing time."""
        current_avg = self.performance_stats["average_processing_time"]
        total_recordings = self.performance_stats["total_recordings"]

        if total_recordings == 1:
            self.performance_stats["average_processing_time"] = new_time
        else:
            # Moving average
            self.performance_stats["average_processing_time"] = (
                (current_avg * (total_recordings - 1) + new_time) / total_recordings
            )

    def _save_session_data(self, session -> Any: AudioSession) -> Any:
        """Save session data to storage."""
        try:
            session_data = {
                "session_id": session.session_id,
                "session_type": session.session_type.value,
                "child_id": session.child_id,
                "start_time": session.start_time.isoformat(),
                "end_time": session.end_time.isoformat() if session.end_time else None,
                "total_recordings": session.total_recordings,
                "total_duration": session.total_duration,
                "quality_mode": session.quality_mode.value,
                "metadata": session.metadata
            }

            # Save to file
            session_file = self.log_directory / f"session_{session.session_id}.json"
            self.log_directory.mkdir(exist_ok=True)
            
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"Error saving session data: {e}")

    def _cleanup_old_sessions(self) -> Any:
        """Cleanup old session files."""
        try:
            if not hasattr(self, 'log_directory'):
                return

            cutoff_time = datetime.now() - timedelta(days=7)

            for session_file in self.log_directory.glob("session_*.json"):
                try:
                    if datetime.fromtimestamp(session_file.stat().st_mtime) < cutoff_time:
                        session_file.unlink()
                except Exception as e:
                    self.logger.warning(f"Error removing session file {session_file}: {e}")

        except Exception as e:
            self.logger.error(f"Error cleaning up old sessions: {e}")

    def _handle_error(self, event -> Any: StateChangeEvent) -> Any:
        """Handle error state changes."""
        if event.details and "error" in event.details:
            error_msg = event.details['error']
            self.logger.error(f"Audio system error: {error_msg}")

            # Trigger error event
            self._trigger_event("error", {
                "error": error_msg, 
                "timestamp": datetime.now().isoformat()
            })

            # Stop any ongoing operations
            self.stop_all()

    def _handle_recording_state(self, event -> Any: StateChangeEvent) -> Any:
        """Handle recording state changes."""
        if hasattr(event, 'new_state'):
            if event.new_state == AudioState.RECORDING:
                self.logger.debug("Recording state changed to RECORDING")
            elif event.new_state == AudioState.IDLE:
                self.logger.debug("Recording state changed to IDLE")

    def _handle_playback_state(self, event -> Any: StateChangeEvent) -> Any:
        """Handle playback state changes."""
        if hasattr(event, 'new_state'):
            if event.new_state == AudioState.PLAYING:
                self.logger.debug("Playback state changed to PLAYING")
            elif event.new_state == AudioState.IDLE:
                self.logger.debug("Playback state changed to IDLE")

    def _on_playback_complete(self) -> Any:
        """Callback function for when TTS playback is complete."""
        self.logger.info("TTS playback complete.")
        if LOCAL_AUDIO_AVAILABLE:
            state_manager.set_state("playback", AudioState.IDLE)

    def cleanup(self) -> Any:
        """Clean up all resources and stop background tasks."""
        try:
            self.logger.info("Starting audio manager cleanup")

            # Stop all active operations
            self.stop_all()

            # End all active sessions
            with self._session_lock:
                for session_id in list(self.active_sessions.keys()):
                    self.end_session(session_id)

            # Clean up temporary files
            self._cleanup_temp_files()

            # Clean up audio cache
            self._cleanup_audio_cache()

            # Clean up TTS cache
            if hasattr(self, 'tts') and hasattr(self.tts, 'cleanup_cache'):
                self.tts.cleanup_cache()

            # Clean up pygame
            if self.pygame_available:
                try:
                    import pygame
                    pygame.mixer.quit()
                except Exception as e:
                    self.logger.warning(f"Error cleaning up pygame: {e}")

            self.logger.info("Audio manager cleanup completed")

        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.cleanup()

    def _play_audio_file(
        self, 
        filename: str, 
        volume: float, 
        loop: bool, 
        fade_in: float, 
        fade_out: float,
        format_hint: Optional[AudioFormatType] = None
    ) -> bool:
        """Play audio file with format-specific optimizations."""
        try:
            file_path = Path(filename)
            if not file_path.exists():
                raise FileNotFoundError(f"Audio file not found: {filename}")

            # Detect format if not provided
            if format_hint is None:
                format_hint = self._detect_audio_format(filename)

            # Use pygame for supported formats
            if self.pygame_available and format_hint in [AudioFormatType.WAV, AudioFormatType.OGG]:
                return self._play_with_pygame(filename, volume, loop)
            
            # Use pydub for other formats
            elif AUDIO_LIBS_AVAILABLE:
                return self._play_with_pydub(filename, volume, loop, fade_in, fade_out)
            
            # Fallback to basic playback
            else:
                return self._play_basic(filename, volume)

        except Exception as e:
            self.logger.error(f"Error playing file {filename}: {e}")
            return False

    def _play_audio_array(
        self, 
        audio_data: np.ndarray, 
        volume: float, 
        loop: bool, 
        fade_in: float, 
        fade_out: float
    ) -> bool:
        """Play numpy audio array."""
        try:
            # Apply volume
            if volume != 1.0:
                audio_data = audio_data * volume

            # Apply fades if requested
            if fade_in > 0 or fade_out > 0:
                audio_data = self._apply_fades(audio_data, fade_in, fade_out)

            # Convert to appropriate format for playback
            if self.pygame_available:
                return self._play_array_with_pygame(audio_data, loop)
            elif AUDIO_LIBS_AVAILABLE:
                return self._play_array_with_pydub(audio_data, loop)
            else:
                # Mock playback
                time.sleep(len(audio_data) / self.config.sample_rate)
                return True

        except Exception as e:
            self.logger.error(f"Error playing audio array: {e}")
            return False

    def _play_with_pygame(self, filename: str, volume: float, loop: bool) -> bool:
        """Play audio using pygame mixer."""
        try:
            import pygame
            
            # Load and play
            pygame.mixer.music.load(filename)
            pygame.mixer.music.set_volume(volume)
            
            loops = -1 if loop else 0
            pygame.mixer.music.play(loops)
            
            # Wait for playback to complete if not looping
            if not loop:
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
            
            return True
        except Exception as e:
            self.logger.error(f"Pygame playback error: {e}")
            return False

    def _play_with_pydub(
        self, 
        filename: str, 
        volume: float, 
        loop: bool, 
        fade_in: float, 
        fade_out: float
    ) -> bool:
        """Play audio using pydub."""
        try:
            # Load audio
            audio = AudioSegment.from_file(filename)
            
            # Apply volume (convert to dB)
            if volume != 1.0:
                volume_db = 20 * np.log10(volume) if volume > 0 else -60
                audio = audio + volume_db
            
            # Apply fades
            if fade_in > 0:
                audio = audio.fade_in(int(fade_in * 1000))
            if fade_out > 0:
                audio = audio.fade_out(int(fade_out * 1000))
            
            # Play (note: this is blocking)
            play(audio)
            return True
            
        except Exception as e:
            self.logger.error(f"Pydub playback error: {e}")
            return False

    def _play_array_with_pygame(self, audio_data: np.ndarray, loop: bool) -> bool:
        """Play numpy array using pygame."""
        try:
            import pygame
            
            # Convert to pygame format
            audio_data_int16 = (audio_data * 32767).astype(np.int16)
            
            # Create pygame sound
            sound = pygame.sndarray.make_sound(audio_data_int16)
            
            loops = -1 if loop else 0
            sound.play(loops)
            
            # Wait for playback to complete if not looping
            if not loop:
                duration = len(audio_data) / self.config.sample_rate
                time.sleep(duration)
            
            return True
        except Exception as e:
            self.logger.error(f"Pygame array playback error: {e}")
            return False

    def _play_array_with_pydub(self, audio_data: np.ndarray, loop: bool) -> bool:
        """Play numpy array using pydub."""
        try:
            # Convert to pydub AudioSegment
            audio_data_int16 = (audio_data * 32767).astype(np.int16)
            audio = AudioSegment(
                audio_data_int16.tobytes(),
                frame_rate=self.config.sample_rate,
                sample_width=2,
                channels=1
            )
            
            play(audio)
            return True
            
        except Exception as e:
            self.logger.error(f"Pydub array playback error: {e}")
            return False

    def _play_basic(self, filename: str, volume: float) -> bool:
        """Basic fallback playback method."""
        try:
            # This is a very basic implementation
            # In a real scenario, you might use system commands or other libraries
            self.logger.info(f"Basic playback of {filename} at volume {volume}")
            
            # Simulate playback duration
            duration = self._get_audio_duration(filename)
            time.sleep(duration)
            
            return True
        except Exception as e:
            self.logger.error(f"Basic playback error: {e}")
            return False

    def _save_wav(self, audio_data: np.ndarray, filename: str, metadata: Optional[Dict] = None) -> bool:
        """Save audio as WAV format."""
        try:
            if AUDIO_LIBS_AVAILABLE:
                sf.write(filename, audio_data, self.config.sample_rate, subtype='PCM_16')
            else:
                # Basic WAV writing (simplified)
                self._write_basic_wav(audio_data, filename)
            
            # Add metadata if supported
            if metadata:
                self._embed_wav_metadata(filename, metadata)
            
            return True
        except Exception as e:
            self.logger.error(f"Error saving WAV: {e}")
            return False

    def _save_mp3(self, audio_data: np.ndarray, filename: str, quality: int, metadata: Optional[Dict] = None) -> bool:
        """Save audio as MP3 format."""
        try:
            if not AUDIO_LIBS_AVAILABLE:
                raise RuntimeError("Audio libraries required for MP3 encoding")

            # Convert to pydub AudioSegment
            audio_data_int16 = (audio_data * 32767).astype(np.int16)
            audio = AudioSegment(
                audio_data_int16.tobytes(),
                frame_rate=self.config.sample_rate,
                sample_width=2,
                channels=1
            )

            # Determine bitrate from quality (0-10 scale)
            bitrate_map = {
                0: "64k", 1: "80k", 2: "96k", 3: "112k", 4: "128k",
                5: "160k", 6: "192k", 7: "224k", 8: "256k", 9: "320k", 10: "320k"
            }
            bitrate = bitrate_map.get(quality, "192k")

            # Export as MP3
            audio.export(filename, format="mp3", bitrate=bitrate, tags=metadata or {})
            
            return True
        except Exception as e:
            self.logger.error(f"Error saving MP3: {e}")
            return False

    def _save_opus(self, audio_data: np.ndarray, filename: str, quality: int, metadata: Optional[Dict] = None) -> bool:
        """Save audio as OPUS format."""
        try:
            if not AUDIO_LIBS_AVAILABLE:
                raise RuntimeError("Audio libraries required for OPUS encoding")

            # Convert to pydub AudioSegment
            audio_data_int16 = (audio_data * 32767).astype(np.int16)
            audio = AudioSegment(
                audio_data_int16.tobytes(),
                frame_rate=self.config.sample_rate,
                sample_width=2,
                channels=1
            )

            # OPUS quality is different (VBR mode)
            codec_params = ["-acodec", "libopus", "-b:a", f"{32 + quality * 28}k"]
            
            audio.export(filename, format="opus", codec="libopus", parameters=codec_params)
            
            return True
        except Exception as e:
            self.logger.error(f"Error saving OPUS: {e}")
            return False

    def _save_ogg(self, audio_data: np.ndarray, filename: str, quality: int, metadata: Optional[Dict] = None) -> bool:
        """Save audio as OGG format."""
        try:
            if not AUDIO_LIBS_AVAILABLE:
                raise RuntimeError("Audio libraries required for OGG encoding")

            # Convert to pydub AudioSegment
            audio_data_int16 = (audio_data * 32767).astype(np.int16)
            audio = AudioSegment(
                audio_data_int16.tobytes(),
                frame_rate=self.config.sample_rate,
                sample_width=2,
                channels=1
            )

            # OGG Vorbis quality
            codec_params = ["-acodec", "libvorbis", "-q:a", str(quality)]
            
            audio.export(filename, format="ogg", codec="libvorbis", parameters=codec_params)
            
            return True
        except Exception as e:
            self.logger.error(f"Error saving OGG: {e}")
            return False

    def _save_flac(self, audio_data: np.ndarray, filename: str, metadata: Optional[Dict] = None) -> bool:
        """Save audio as FLAC format (lossless)."""
        try:
            if AUDIO_LIBS_AVAILABLE:
                sf.write(filename, audio_data, self.config.sample_rate, subtype='PCM_16', format='FLAC')
            else:
                raise RuntimeError("Audio libraries required for FLAC encoding")
            
            return True
        except Exception as e:
            self.logger.error(f"Error saving FLAC: {e}")
            return False

    # Helper methods for audio processing

    def _detect_audio_format(self, filename: str) -> AudioFormatType:
        """Detect audio format from filename extension."""
        file_path = Path(filename)
        extension = file_path.suffix.lower().lstrip('.')
        
        format_map = {
            'wav': AudioFormatType.WAV,
            'mp3': AudioFormatType.MP3,
            'opus': AudioFormatType.OPUS,
            'ogg': AudioFormatType.OGG,
            'flac': AudioFormatType.FLAC,
            'm4a': AudioFormatType.M4A
        }
        
        return format_map.get(extension, self.config.default_output_format)

    def _get_audio_duration(self, filename: str) -> float:
        """Get audio file duration in seconds."""
        try:
            if AUDIO_LIBS_AVAILABLE:
                audio = AudioSegment.from_file(filename)
                return len(audio) / 1000.0  # Convert ms to seconds
            else:
                # Fallback estimate
                file_size = Path(filename).stat().st_size
                # Rough estimate: assume 16-bit, 44.1kHz, mono
                return file_size / (2 * 44100)
        except Exception as e:
            self.logger.error(f"Error getting audio duration: {e}")
            return 1.0  # Default fallback

    def _apply_fades(self, audio_data: np.ndarray, fade_in: float, fade_out: float) -> np.ndarray:
        """Apply fade-in and fade-out effects to audio data."""
        try:
            audio_copy = audio_data.copy()
            sample_rate = self.config.sample_rate
            
            # Apply fade-in
            if fade_in > 0:
                fade_samples = int(fade_in * sample_rate)
                fade_samples = min(fade_samples, len(audio_copy))
                
                fade_curve = np.linspace(0, 1, fade_samples)
                audio_copy[:fade_samples] *= fade_curve
            
            # Apply fade-out
            if fade_out > 0:
                fade_samples = int(fade_out * sample_rate)
                fade_samples = min(fade_samples, len(audio_copy))
                
                fade_curve = np.linspace(1, 0, fade_samples)
                audio_copy[-fade_samples:] *= fade_curve
            
            return audio_copy
        except Exception as e:
            self.logger.error(f"Error applying fades: {e}")
            return audio_data

    def _write_basic_wav(self, audio_data -> Any: np.ndarray, filename -> Any: str) -> Any:
        """Write basic WAV file without external libraries."""
        import struct
        import wave
        
        try:
            # Convert to 16-bit integer
            audio_data_int16 = (audio_data * 32767).astype(np.int16)
            
            with wave.open(filename, 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(self.config.sample_rate)
                wav_file.writeframes(audio_data_int16.tobytes())
                
        except Exception as e:
            self.logger.error(f"Error writing basic WAV: {e}")
            raise

    def _embed_wav_metadata(self, filename -> Any: str, metadata -> Any: Dict[str, Any]) -> Any:
        """Embed metadata in WAV file (simplified)."""
        try:
            # This is a simplified implementation
            # In practice, you might use mutagen or similar library
            self.logger.info(f"Metadata would be embedded: {metadata}")
        except Exception as e:
            self.logger.error(f"Error embedding WAV metadata: {e}")

    # Cloud integration methods

    def _add_to_cloud_queue(self, filename -> Any: str, session_id -> Any: Optional[str], metadata -> Any: Optional[Dict]) -> Any:
        """Add file to cloud sync queue."""
        try:
            cloud_item = {
                "filename": filename,
                "session_id": session_id,
                "metadata": metadata or {},
                "timestamp": datetime.now().isoformat(),
                "retry_count": 0
            }
            
            self.cloud_queue.append(cloud_item)
            self.logger.debug(f"Added to cloud queue: {filename}")
            
        except Exception as e:
            self.logger.error(f"Error adding to cloud queue: {e}")

    def _process_cloud_queue(self) -> Any:
        """Process pending cloud sync operations."""
        if not self.cloud_queue:
            return
        
        try:
            items_to_remove = []
            
            for i, item in enumerate(self.cloud_queue):
                try:
                    success = self._sync_to_cloud(item)
                    if success:
                        items_to_remove.append(i)
                        self.performance_stats["cloud_syncs"] += 1
                    else:
                        item["retry_count"] += 1
                        if item["retry_count"] > 3:
                            items_to_remove.append(i)
                            self.logger.warning(f"Cloud sync failed after 3 retries: {item['filename']}")
                
                except Exception as e:
                    self.logger.error(f"Error processing cloud item: {e}")
                    item["retry_count"] += 1
            
            # Remove processed items
            for i in reversed(items_to_remove):
                self.cloud_queue.pop(i)
                
        except Exception as e:
            self.logger.error(f"Error processing cloud queue: {e}")

    def _sync_to_cloud(self, item: Dict[str, Any]) -> bool:
        """Sync individual item to cloud storage."""
        try:
            # Mock cloud sync implementation
            # In practice, this would upload to AWS S3, Google Cloud, etc.
            
            filename = item["filename"]
            file_path = Path(filename)
            
            if not file_path.exists():
                self.logger.warning(f"File not found for cloud sync: {filename}")
                return True  # Consider it "processed"
            
            # Simulate cloud upload
            time.sleep(0.1)  # Simulate network delay
            
            self.logger.info(f"Mock cloud sync completed: {filename}")
            
            # Trigger cloud sync event
            self._trigger_event("cloud_sync", {
                "filename": filename,
                "session_id": item["session_id"],
                "success": True,
                "timestamp": datetime.now().isoformat()
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Cloud sync error: {e}")
            return False

    # Cleanup and maintenance methods

    def _cleanup_temp_files(self) -> Any:
        """Clean up temporary audio files."""
        try:
            files_cleaned = 0
            
            for file_path in self.temp_files[:]:
                try:
                    if file_path.exists():
                        # Check if file is old enough to clean up
                        file_age = datetime.now() - datetime.fromtimestamp(file_path.stat().st_mtime)
                        if file_age.total_seconds() > 3600:  # 1 hour old
                            file_path.unlink()
                            self.temp_files.remove(file_path)
                            files_cleaned += 1
                except Exception as e:
                    self.logger.warning(f"Error cleaning temp file {file_path}: {e}")
            
            if files_cleaned > 0:
                self.logger.info(f"Cleaned up {files_cleaned} temporary files")
                
        except Exception as e:
            self.logger.error(f"Error cleaning temp files: {e}")

    def _cleanup_audio_cache(self) -> Any:
        """Clean up audio cache to free memory."""
        try:
            cache_size = len(self.audio_cache)
            
            if cache_size > 50:  # Keep only 50 recent items
                # Remove oldest items
                items_to_remove = list(self.audio_cache.keys())[:-50]
                for key in items_to_remove:
                    del self.audio_cache[key]
                
                self.logger.info(f"Cleaned audio cache: removed {len(items_to_remove)} items")
                
        except Exception as e:
            self.logger.error(f"Error cleaning audio cache: {e}")

    def _get_session(self, session_id: Optional[str]) -> Optional[AudioSession]:
        """Get session by ID or return current session."""
        if session_id and session_id in self.active_sessions:
            return self.active_sessions[session_id]
        return self.current_session

    # Additional convenience methods

    def record_audio(
        self,
        duration: Optional[int] = None,
        process: bool = None,
        save: bool = None,
        filename: Optional[str] = None,
        session_id: Optional[str] = None,
        format: AudioFormatType = None
    ) -> Optional[Tuple[np.ndarray, Dict[str, Any]]]:
        """
        Enhanced record audio with format support.

        Args:
            duration: Recording duration (uses config default if None)
            process: Whether to process audio (uses config default if None)
            save: Whether to save audio (uses config default if None)
            filename: Custom filename for saving
            session_id: Session to associate recording with
            format: Audio format for saving

        Returns:
            Tuple of (audio_data, metadata) or None
        """
        try:
            # Use configuration defaults
            if duration is None:
                duration = self.config.default_record_duration
            if process is None:
                process = self.config.auto_process_audio
            if save is None:
                save = self.config.auto_save_sessions
            if format is None:
                format = self.config.default_output_format

            # Validate duration
            duration = min(duration, self.config.max_record_duration)

            # Check if already recording
            if hasattr(self.recorder, 'is_recording') and self.recorder.is_recording():
                self.logger.warning("Recording already in progress")
                return None

            # Get or create session
            session = self._get_session(session_id)

            # Trigger recording start event
            self._trigger_event("recording_start", {
                "duration": duration,
                "session_id": session.session_id if session else None,
                "format": format.value
            })

            start_time = time.time()

            # Record audio
            self.logger.info(f"Starting recording for {duration} seconds")
            if hasattr(self.recorder, 'record_audio'):
                audio_data = self.recorder.record_audio(duration)
            else:
                # Mock recording
                audio_data = np.random.random(duration * self.config.sample_rate).astype(np.float32)

            if audio_data is None or len(audio_data) == 0:
                self.logger.error("No audio data recorded")
                return None

            # Create metadata
            metadata = {
                "filename": filename or "recording",
                "format": format.value,
                "duration": len(audio_data) / self.config.sample_rate,
                "sample_rate": self.config.sample_rate,
                "channels": 1,
                "created_at": datetime.now().isoformat(),
                "session_id": session.session_id if session else None,
                "child_id": session.child_id if session else None,
                "recording_type": "user_input"
            }

            # Process audio if requested
            if process and hasattr(self.processor, 'process'):
                if LOCAL_AUDIO_AVAILABLE:
                    state_manager.set_processing(True)
                try:
                    processed_audio = self.processor.process(audio_data)
                    if processed_audio is not None:
                        audio_data = processed_audio
                        metadata["processed"] = True
                finally:
                    if LOCAL_AUDIO_AVAILABLE:
                        state_manager.set_processing(False)

            # Save if requested
            if save:
                if filename is None:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    child_id = session.child_id if session else "unknown"
                    filename = f"recording_{child_id}_{timestamp}.{format.value}"

                success = self.save_audio(
                    audio_data,
                    filename,
                    format=format,
                    metadata=metadata,
                    session_id=session_id
                )
                
                if success:
                    metadata["filename"] = filename

            # Update session stats
            if session:
                session.total_recordings += 1
                session.total_duration += metadata["duration"]

            # Update performance stats
            processing_time = time.time() - start_time
            self.performance_stats["total_recordings"] += 1
            self._update_avg_processing_time(processing_time)

            # Trigger recording end event
            self._trigger_event("recording_end", {
                "duration": metadata["duration"],
                "processing_time": processing_time,
                "session_id": session.session_id if session else None,
                "saved": save and success if save else False
            })

            self.logger.info(f"Recording completed: {metadata['duration']:.2f}s")
            return audio_data, metadata

        except Exception as e:
            self.logger.error(f"Error recording audio: {e}")
            self.performance_stats["total_errors"] += 1
            self.performance_stats["last_error"] = str(e)
            if LOCAL_AUDIO_AVAILABLE:
                state_manager.set_error(str(e))
            return None

    def speak(
        self,
        text: str,
        language: Optional[str] = None,
        speed: float = 1.0,
        volume: Optional[float] = None,
        cache: bool = True,
        session_id: Optional[str] = None,
        voice_style: str = "friendly"
    ) -> bool:
        """
        Enhanced text-to-speech with session support.

        Args:
            text: Text to speak
            language: Language code (uses config default if None)
            speed: Speech speed multiplier
            volume: Speech volume (0.0-1.0)
            cache: Whether to cache generated speech
            session_id: Session to associate speech with
            voice_style: Voice style for emotional context

        Returns:
            Success status
        """
        try:
            # Use configuration defaults
            if language is None:
                language = self.config.language_preference

            # Get session info
            session = self._get_session(session_id)

            # Set volume if specified
            if volume is not None:
                volume = max(0.0, min(1.0, volume))
                if hasattr(self.tts, 'set_volume'):
                    self.tts.set_volume(volume)

            # Add session context to TTS metadata
            tts_metadata = {
                "session_id": session.session_id if session else None,
                "child_id": session.child_id if session else None,
                "timestamp": datetime.now().isoformat(),
                "voice_style": voice_style
            }

            # Generate and play speech
            if hasattr(self.tts, 'speak_with_metadata'):
                success = self.tts.speak_with_metadata(
                    text, language, speed, cache, tts_metadata
                )
            elif hasattr(self.tts, 'speak'):
                success = self.tts.speak(text, language, speed, cache)
            else:
                # Mock TTS
                self.logger.info(f"Mock TTS: '{text}' in {language}")
                time.sleep(len(text) * 0.05)  # Simulate speech duration
                success = True

            if success:
                self.logger.info(f"TTS completed for session {session.session_id if session else 'none'}")

            return success

        except Exception as e:
            self.logger.error(f"Error in text-to-speech: {e}")
            self.performance_stats["total_errors"] += 1
            self.performance_stats["last_error"] = str(e)
            if LOCAL_AUDIO_AVAILABLE:
                state_manager.set_error(str(e))
            return False

    def stop_all(self, session_id -> Any: Optional[str] = None) -> Any:
        """
        Stop all audio operations, optionally for specific session.

        Args:
            session_id: Specific session to stop (None for all)
        """
        try:
            if session_id:
                self.logger.info(f"Stopping audio operations for session {session_id}")
            else:
                self.logger.info("Stopping all audio operations")

            # Stop recording
            if hasattr(self.recorder, 'is_recording') and self.recorder.is_recording():
                if hasattr(self.recorder, 'stop_recording'):
                    self.recorder.stop_recording()

            # Stop playback
            if self.pygame_available:
                import pygame
                pygame.mixer.stop()
                pygame.mixer.music.stop()

            # Stop TTS
            if hasattr(self.tts, 'is_playing') and self.tts.is_playing():
                if hasattr(self.tts, 'stop'):
                    self.tts.stop()

            # Stop any ongoing processing
            if LOCAL_AUDIO_AVAILABLE:
                state_manager.set_processing(False)

            self.logger.info("Audio operations stopped successfully")

        except Exception as e:
            self.logger.error(f"Error stopping operations: {e}")
            if LOCAL_AUDIO_AVAILABLE:
                state_manager.set_error(str(e))

    # Original methods from the base class (keeping compatibility)
    
    def start_session(
        self,
        child_id: str,
        session_type: AudioSessionType = AudioSessionType.CONVERSATION,
        quality_mode: AudioQualityMode = AudioQualityMode.BALANCED
    ) -> str:
        """
        Start a new audio session.

        Args:
            child_id: Child identifier
            session_type: Type of session
            quality_mode: Audio quality mode

        Returns:
            Session ID
        """
        try:
            # Check session limits
            if len(self.active_sessions) >= self.config.max_concurrent_sessions:
                raise AudioSystemError("Maximum concurrent sessions reached")

            # Generate session ID
            session_id = f"session_{child_id}_{int(datetime.now().timestamp())}"

            # Create session
            session = AudioSession(
                session_id=session_id,
                session_type=session_type,
                child_id=child_id,
                start_time=datetime.now(),
                quality_mode=quality_mode
            )

            # Add to active sessions
            with self._session_lock:
                self.active_sessions[session_id] = session
                self.current_session = session

            # Set quality mode
            self._set_quality_mode(quality_mode)

            # Trigger session start event
            self._trigger_event("session_start", {
                "session_id": session_id,
                "child_id": child_id,
                "session_type": session_type.value,
                "quality_mode": quality_mode.value
            })

            self.logger.info(f"Started audio session: {session_id} for child {child_id}")
            return session_id

        except Exception as e:
            self.logger.error(f"Error starting session: {e}")
            raise AudioSystemError(f"Failed to start session: {e}")

    def end_session(self, session_id: str) -> bool:
        """
        End an audio session.

        Args:
            session_id: Session to end

        Returns:
            Success status
        """
        try:
            with self._session_lock:
                if session_id not in self.active_sessions:
                    self.logger.warning(f"Session {session_id} not found")
                    return False

                session = self.active_sessions[session_id]
                session.end_time = datetime.now()

                # Save session data if configured
                if self.config.auto_save_sessions:
                    self._save_session_data(session)

                # Remove from active sessions
                del self.active_sessions[session_id]

                # Update current session
                if self.current_session and self.current_session.session_id == session_id:
                    self.current_session = None

                # Trigger callbacks
                self._trigger_event("session_end", {
                    "session_id": session_id,
                    "duration": (session.end_time - session.start_time).total_seconds(),
                    "recordings": session.total_recordings
                })

                self.logger.info(f"Ended audio session {session_id}")
                return True

        except Exception as e:
            self.logger.error(f"Error ending session: {e}")
            return False

    # Mock Components for Testing

class MockAudioRecorder:
    """Mock audio recorder for testing."""
    
    def __init__(self):
        self._recording = False
    
    def record_audio(self, duration: int) -> np.ndarray:
        """Mock audio recording."""
        self._recording = True
        time.sleep(0.1)  # Simulate recording delay
        self._recording = False
        return np.random.random(duration * 44100).astype(np.float32)
    
    def is_recording(self) -> bool:
        return self._recording
    
    def stop_recording(self) -> Any:
        self._recording = False
    
    def set_noise_reduction(self, enabled -> Any: bool) -> Any:
        pass
    
    def set_sample_rate(self, rate -> Any: int) -> Any:
        pass


class MockAudioProcessor:
    """Mock audio processor for testing."""
    
    def process(self, audio_data: np.ndarray) -> np.ndarray:
        """Mock audio processing - just return normalized data."""
        max_val = np.max(np.abs(audio_data))
        if max_val > 0:
            return audio_data / max_val * 0.95
        return audio_data
    
    def set_processing_level(self, level -> Any: str) -> Any:
        pass
    
    def set_child_safe_mode(self, enabled -> Any: bool) -> Any:
        pass


class MockAudioIO:
    """Mock audio I/O for testing."""
    
    def __init__(self):
        self.temp_dir = Path("temp_audio")
        self.temp_dir.mkdir(exist_ok=True)
    
    def save_audio(self, audio_data -> Any: np.ndarray, filename -> Any: str, metadata -> Any: Dict = None) -> Any:
        """Mock save audio."""
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        # Just create an empty file to simulate saving
        Path(filename).touch()
    
    def load_audio(self, filename -> Any: str) -> Any:
        """Mock load audio."""
        # Return mock data
        return np.random.random(44100).astype(np.float32), 44100, {"duration": 1.0}
    
    def cleanup_temp_files(self) -> Any:
        """Mock cleanup."""
        pass
    
    def create_temp_file(self, prefix: str = "temp_") -> str:
        """Create temporary file."""
        import tempfile
        fd, path = tempfile.mkstemp(prefix=prefix, suffix=".wav")
        os.close(fd)
        return path


class MockTTSPlayback:
    """Mock TTS playback for testing."""
    
    def __init__(self, on_playback_complete=None):
        self.on_playback_complete = on_playback_complete
        self._playing = False
        self._volume = 1.0
    
    def speak(self, text: str, language: str = "en", speed: float = 1.0, cache: bool = True) -> bool:
        """Mock TTS speech."""
        self._playing = True
        # Simulate speech duration
        duration = len(text) * 0.05 / speed
        time.sleep(min(duration, 3.0))  # Cap at 3 seconds for testing
        self._playing = False
        
        if self.on_playback_complete:
            self.on_playback_complete()
        
        return True
    
    def speak_with_metadata(self, text: str, language: str, speed: float, cache: bool, metadata: Dict) -> bool:
        """Mock TTS with metadata."""
        return self.speak(text, language, speed, cache)
    
    def is_playing(self) -> bool:
        return self._playing
    
    def stop(self) -> Any:
        self._playing = False
    
    def set_volume(self, volume -> Any: float) -> Any:
        self._volume = max(0.0, min(1.0, volume))
    
    def cleanup_cache(self) -> Any:
        pass


# Continue with the rest of the methods and compatibility functions...


# Convenience functions for easy access

def create_audio_manager(config: Optional[AudioSystemConfig] = None) -> EnhancedAudioManager:
    """
    Create and configure audio manager instance.

    Args:
        config: Optional configuration

    Returns:
        AudioManager instance
    """
    return EnhancedAudioManager(config)


def get_default_config() -> AudioSystemConfig:
    """Get default audio system configuration."""
    return AudioSystemConfig()


def create_child_safe_config() -> AudioSystemConfig:
    """Create child-safe audio configuration."""
    return AudioSystemConfig(
        child_safe_mode=True,
        volume_level=0.6,
        max_record_duration=30,
        noise_reduction_enabled=True,
        default_output_format=AudioFormatType.WAV,
        compression_quality=3,
        enable_cloud_sync=False
    )


def create_high_quality_config() -> AudioSystemConfig:
    """Create high-quality audio configuration."""
    return AudioSystemConfig(
        sample_rate=48000,
        channels=2,
        compression_quality=9,
        default_output_format=AudioFormatType.FLAC,
        noise_reduction_enabled=True,
        auto_process_audio=True,
        enable_cloud_sync=True
    )


def create_low_latency_config() -> AudioSystemConfig:
    """Create low-latency audio configuration."""
    return AudioSystemConfig(
        sample_rate=22050,
        channels=1,
        default_output_format=AudioFormatType.OPUS,
        compression_quality=6,
        auto_process_audio=False,
        enable_cloud_sync=False
    )


# Global audio manager instance (singleton pattern)
_global_audio_manager: Optional[EnhancedAudioManager] = None


def get_audio_manager(config: Optional[AudioSystemConfig] = None) -> EnhancedAudioManager:
    """
    Get global audio manager instance (singleton).

    Args:
        config: Configuration for first-time initialization

    Returns:
        Global AudioManager instance
    """
    global _global_audio_manager

    if _global_audio_manager is None:
        _global_audio_manager = EnhancedAudioManager(config)

    return _global_audio_manager


def shutdown_audio_manager() -> Any:
    """Shutdown global audio manager."""
    global _global_audio_manager

    if _global_audio_manager is not None:
        _global_audio_manager.cleanup()
        _global_audio_manager = None


# Module initialization
if __name__ == "__main__":
    # Example usage
    logger.info("AI Teddy Bear Enhanced Audio Manager")
    logger.info("====================================")
    
    # Create audio manager with child-safe config
    config = create_child_safe_config()
    manager = create_audio_manager(config)
    
    logger.info(f"Supported formats: {manager.get_supported_formats()}")
    logger.info(f"System stats: {manager.get_system_stats()}")
    
    # Run system test
    test_results = manager.test_audio_system()
    logger.info(f"System test: {test_results['overall_status']}")
    
    # Clean up
    manager.cleanup()