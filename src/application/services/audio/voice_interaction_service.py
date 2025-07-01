"""
Voice Interaction Service - Clean Architecture Coordinator
Enhanced voice interaction with streaming integration using Clean Architecture
"""

import asyncio
import logging
from collections import deque
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import sounddevice as sd

from src.application.services.streaming_service import StreamingService
from src.core.application.interfaces.services import IAIService
from src.core.domain.entities.audio_stream import AudioStream
# Domain imports
from src.domain.audio.models import (AudioConfig, EmotionalTone, Language,
                                     VoiceProfile)
from src.domain.audio.services import AudioProcessor, VoiceActivityDetector
from src.infrastructure.config import get_config

from .voice_profile_service import VoiceProfileService
from .voice_recognition_service import VoiceRecognitionService
# Application service imports
from .voice_synthesis_service import VoiceSynthesisService


class VoiceInteractionService:
    """
    Clean Architecture Coordinator for Voice Interaction
    Orchestrates voice synthesis, recognition, and profile management
    """

    def __init__(self, config=None):
        """Initialize voice interaction service with dependency injection"""
        self.config = config or get_config()
        self.logger = logging.getLogger(self.__class__.__name__)

        # Initialize domain services
        self.audio_config = AudioConfig()
        self.audio_processor = AudioProcessor(self.audio_config)
        self.vad = VoiceActivityDetector(self.audio_config)

        # Initialize application services
        self.voice_synthesis = VoiceSynthesisService(self.config)
        self.voice_recognition = VoiceRecognitionService(self.config)
        self.voice_profile_service = VoiceProfileService(
            storage_path="data/voice_profiles", config=self.config
        )

        # External service references
        self.streaming_service: Optional[StreamingService] = None
        self.ai_service: Optional[IAIService] = None

        # Current state
        self.current_profile: Optional[VoiceProfile] = None
        self.is_recording = False

        # Audio streams and buffers
        self.input_stream = None
        self.output_stream = None
        self.audio_buffer = deque(
            maxlen=int(
                self.audio_config.sample_rate * self.audio_config.max_recording_duration
            )
        )

        # Storage paths
        self.recordings_path = Path(
            getattr(self.config, "RECORDINGS_PATH", "data/recordings")
        )
        self.recordings_path.mkdir(parents=True, exist_ok=True)

        # Initialize emotion analyzer integration
        self._init_emotion_integration()

    def _init_emotion_integration(self):
        """Initialize emotion analysis integration"""
        try:
            from src.application.services.ai.emotion_analyzer_service import \
                EmotionAnalyzer
            from src.domain.emotion_config import EmotionConfig

            emotion_config = EmotionConfig(
                api_key=getattr(self.config, "HUME_API_KEY", "")
            )
            self.emotion_analyzer = EmotionAnalyzer(emotion_config.api_key)
        except ImportError:
            self.logger.warning("Emotion analyzer not available")
            self.emotion_analyzer = None

    def set_streaming_service(self, streaming_service: StreamingService):
        """Set streaming service for integration"""
        self.streaming_service = streaming_service
        self.voice_synthesis.set_streaming_service(streaming_service)

    def set_ai_service(self, ai_service: IAIService):
        """Set AI service for integration"""
        self.ai_service = ai_service

    async def initialize_default_profiles(self):
        """Initialize default voice profiles"""
        try:
            profiles = await self.voice_profile_service.create_default_profiles()
            if profiles:
                self.current_profile = profiles.get("teddy_bear")
                self.logger.info(f"Initialized {len(profiles)} default profiles")
            return profiles
        except Exception as e:
            self.logger.error(f"Failed to initialize profiles: {e}")
            return {}

    async def start_voice_interaction(
        self, profile_id: str, session_id: str
    ) -> Dict[str, Any]:
        """Start voice interaction session"""
        try:
            # Validate inputs
            if not isinstance(profile_id, str) or not profile_id:
                return {"status": "error", "reason": "Invalid profile_id"}
            if not isinstance(session_id, str) or not session_id:
                return {"status": "error", "reason": "Invalid session_id"}

            # Load voice profile
            profile = await self.voice_profile_service.load_profile(profile_id)
            if not profile:
                return {"status": "error", "reason": f"Profile not found: {profile_id}"}

            self.current_profile = profile

            # Start audio streams
            await self._start_audio_streams()

            # Start recording loop
            self.is_recording = True
            asyncio.create_task(self._recording_loop(session_id))

            self.logger.info(
                f"Started voice interaction: {profile_id}, session: {session_id}"
            )
            return {"status": "success", "profile": profile_id, "session": session_id}

        except Exception as e:
            self.logger.error(f"Failed to start voice interaction: {e}")
            return {"status": "error", "reason": str(e)}

    async def stop_voice_interaction(self):
        """Stop voice interaction session"""
        try:
            self.is_recording = False
            await self._stop_audio_streams()
            self.logger.info("Stopped voice interaction")
        except Exception as e:
            self.logger.error(f"Failed to stop voice interaction: {e}")

    async def synthesize_speech(
        self,
        text: str,
        emotion: EmotionalTone = EmotionalTone.CALM,
        language: Optional[Language] = None,
        stream_output: bool = True,
    ) -> Optional[bytes]:
        """Synthesize speech with emotional nuance"""
        try:
            if not self.current_profile:
                self.logger.error("No voice profile set")
                return None

            # Use voice synthesis service
            audio_data = await self.voice_synthesis.synthesize_speech(
                text=text,
                voice_profile=self.current_profile,
                emotion=emotion,
                stream_output=stream_output,
            )

            # Apply voice adjustments if needed
            if audio_data and not stream_output:
                audio_data = await self._apply_voice_adjustments(audio_data)

            return audio_data

        except Exception as e:
            self.logger.error(f"Speech synthesis error: {e}")
            return None

    async def transcribe_audio(
        self, audio_data, language: Optional[Language] = None, use_openai: bool = False
    ) -> Dict[str, Any]:
        """Transcribe audio to text"""
        try:
            # Process audio first
            if isinstance(audio_data, np.ndarray):
                audio_data = await self.audio_processor.process_audio(audio_data)

            # Use voice recognition service
            result = await self.voice_recognition.transcribe_audio(
                audio_data=audio_data, language=language, use_openai=use_openai
            )

            return result

        except Exception as e:
            self.logger.error(f"Audio transcription error: {e}")
            return {"error": str(e), "text": ""}

    async def detect_wake_word(
        self,
        wake_words: List[str] = ["hey teddy", "hello teddy", "مرحبا دبدوب"],
        sensitivity: float = 0.5,
    ) -> bool:
        """Detect wake word in audio stream"""
        try:
            # Read audio chunk
            audio_chunk = await self._read_audio_chunk()
            if audio_chunk is None:
                return False

            # Transcribe the chunk
            result = await self.transcribe_audio(audio_chunk)
            text = result.get("text", "").lower()

            # Check for wake words
            for wake_word in wake_words:
                if wake_word.lower() in text:
                    confidence = result.get("confidence", 0.0)
                    return confidence >= sensitivity

            return False

        except Exception as e:
            self.logger.error(f"Wake word detection error: {e}")
            return False

    async def calibrate_audio(self, duration: float = 3.0) -> Dict[str, float]:
        """Calibrate audio input levels"""
        try:
            self.logger.info(f"Starting audio calibration for {duration}s")

            # Record calibration audio
            sample_rate = self.audio_config.sample_rate
            frames = int(sample_rate * duration)

            audio_data = sd.rec(frames, samplerate=sample_rate, channels=1)
            sd.wait()

            # Calculate metrics
            rms_level = np.sqrt(np.mean(audio_data**2))
            peak_level = np.max(np.abs(audio_data))

            # Check speech activity
            speech_ratio = self.vad.calculate_speech_ratio(audio_data.flatten())

            calibration_result = {
                "rms_level": float(rms_level),
                "peak_level": float(peak_level),
                "speech_ratio": speech_ratio,
                "recommended_gain": self._calculate_recommended_gain(rms_level),
            }

            self.logger.info(f"Calibration complete: {calibration_result}")
            return calibration_result

        except Exception as e:
            self.logger.error(f"Audio calibration error: {e}")
            return {"error": str(e)}

    async def play_audio(self, audio_data, wait: bool = True):
        """Play audio data"""
        try:
            if isinstance(audio_data, bytes):
                # Convert bytes to numpy array
                audio_array = (
                    np.frombuffer(audio_data, dtype=np.int16).astype(np.float32)
                    / 32768.0
                )
            else:
                audio_array = audio_data

            # Play audio
            sd.play(audio_array, samplerate=self.audio_config.sample_rate)
            if wait:
                sd.wait()

        except Exception as e:
            self.logger.error(f"Audio playback error: {e}")

    async def save_recording(
        self, audio_data: np.ndarray, session_id: str, metadata: Optional[Dict] = None
    ) -> str:
        """Save audio recording with metadata"""
        try:
            from datetime import datetime

            import soundfile as sf

            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{session_id}_{timestamp}.wav"
            filepath = self.recordings_path / filename

            # Save audio
            sf.write(filepath, audio_data, self.audio_config.sample_rate)

            # Save metadata if provided
            if metadata:
                import json

                metadata_file = filepath.with_suffix(".json")
                with open(metadata_file, "w") as f:
                    json.dump(metadata, f, indent=2)

            self.logger.info(f"Saved recording: {filepath}")
            return str(filepath)

        except Exception as e:
            self.logger.error(f"Failed to save recording: {e}")
            return ""

    async def _recording_loop(self, session_id: str):
        """Main recording loop"""
        try:
            while self.is_recording:
                # Read audio chunk
                audio_chunk = await self._read_audio_chunk()
                if audio_chunk is not None:
                    # Process utterance
                    await self._process_utterance(audio_chunk, session_id)

                # Small delay to prevent CPU overload
                await asyncio.sleep(0.01)

        except Exception as e:
            self.logger.error(f"Recording loop error: {e}")

    async def _process_utterance(self, audio_data: np.ndarray, session_id: str):
        """Process complete utterance"""
        try:
            # Transcribe audio
            result = await self.transcribe_audio(audio_data)

            if result.get("text") and self.ai_service:
                # Process with AI service
                conversation_id = f"{session_id}_{len(self.audio_buffer)}"
                await self.ai_service.process_message(
                    conversation_id, {"text": result["text"], "audio_metadata": result}
                )

        except Exception as e:
            self.logger.error(f"Utterance processing error: {e}")

    async def _apply_voice_adjustments(self, audio_data: bytes) -> bytes:
        """Apply voice profile adjustments to audio"""
        try:
            if not self.current_profile:
                return audio_data

            # Convert bytes to numpy array
            audio_array = (
                np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
            )

            # Apply pitch adjustment
            if self.current_profile.pitch_adjustment != 0:
                audio_array = await self.audio_processor.change_pitch(
                    audio_array, self.current_profile.pitch_adjustment
                )

            # Apply speed adjustment
            if self.current_profile.speed_adjustment != 1.0:
                audio_array = await self.audio_processor.change_speed(
                    audio_array, self.current_profile.speed_adjustment
                )

            # Convert back to bytes
            audio_int16 = (audio_array * 32767).astype(np.int16)
            return audio_int16.tobytes()

        except Exception as e:
            self.logger.error(f"Voice adjustment error: {e}")
            return audio_data

    async def _start_audio_streams(self):
        """Start audio input/output streams"""
        try:
            # Configure audio parameters
            sample_rate = self.audio_config.sample_rate
            channels = self.audio_config.channels
            chunk_size = self.audio_config.chunk_size

            # Start input stream
            self.input_stream = sd.InputStream(
                callback=self._input_callback,
                samplerate=sample_rate,
                channels=channels,
                blocksize=chunk_size,
            )
            self.input_stream.start()

            # Start output stream
            self.output_stream = sd.OutputStream(
                callback=self._output_callback,
                samplerate=sample_rate,
                channels=channels,
                blocksize=chunk_size,
            )
            self.output_stream.start()

            self.logger.info("Started audio streams")

        except Exception as e:
            self.logger.error(f"Failed to start audio streams: {e}")

    async def _stop_audio_streams(self):
        """Stop audio streams"""
        try:
            if self.input_stream:
                self.input_stream.stop()
                self.input_stream.close()
                self.input_stream = None

            if self.output_stream:
                self.output_stream.stop()
                self.output_stream.close()
                self.output_stream = None

            self.logger.info("Stopped audio streams")

        except Exception as e:
            self.logger.error(f"Failed to stop audio streams: {e}")

    def _input_callback(self, indata, frames, time_info, status):
        """Audio input callback"""
        if status:
            self.logger.warning(f"Audio input status: {status}")

        # Add to buffer
        self.audio_buffer.extend(indata.flatten())

    def _output_callback(self, outdata, frames, time_info, status):
        """Audio output callback"""
        if status:
            self.logger.warning(f"Audio output status: {status}")

        # Get output audio (implement based on streaming service)
        outdata.fill(0)  # Silent for now

    async def _read_audio_chunk(self) -> Optional[np.ndarray]:
        """Read audio chunk from buffer"""
        try:
            if len(self.audio_buffer) >= self.audio_config.chunk_size:
                # Extract chunk
                chunk = np.array(
                    list(self.audio_buffer)[: self.audio_config.chunk_size]
                )

                # Remove processed data
                for _ in range(self.audio_config.chunk_size):
                    if self.audio_buffer:
                        self.audio_buffer.popleft()

                return chunk

            return None

        except Exception as e:
            self.logger.error(f"Audio chunk read error: {e}")
            return None

    def _calculate_recommended_gain(self, rms_level: float) -> float:
        """Calculate recommended gain adjustment"""
        target_rms = 0.1  # Target RMS level
        if rms_level > 0:
            return target_rms / rms_level
        return 1.0

    async def test_voice_synthesis(
        self,
        test_text: str = "Hello, I'm your friendly teddy bear! How are you today?",
        emotion: EmotionalTone = EmotionalTone.HAPPY,
    ) -> bool:
        """Test voice synthesis capability"""
        try:
            if not self.current_profile:
                await self.initialize_default_profiles()

            audio_data = await self.synthesize_speech(
                test_text, emotion, stream_output=False
            )
            return audio_data is not None

        except Exception as e:
            self.logger.error(f"Synthesis test failed: {e}")
            return False

    async def test_speech_recognition(self, duration: float = 5.0) -> Dict[str, Any]:
        """Test speech recognition capability"""
        try:
            return await self.voice_recognition.test_recognition(duration)
        except Exception as e:
            self.logger.error(f"Recognition test failed: {e}")
            return {"success": False, "error": str(e)}

    async def get_supported_languages(self) -> List[Dict[str, str]]:
        """Get supported languages"""
        return [{"code": lang.value, "name": lang.name} for lang in Language]


# Utility functions
def is_arabic(text: str) -> bool:
    """Check if text contains Arabic characters"""
    return any("\u0600" <= char <= "\u06ff" for char in text)


def is_english(text: str) -> bool:
    """Check if text is primarily English"""
    return text.isascii() and any(char.isalpha() for char in text)


def get_emotion_from_sentiment(sentiment: str) -> EmotionalTone:
    """Map sentiment to emotional tone"""
    sentiment_mapping = {
        "happy": EmotionalTone.HAPPY,
        "joy": EmotionalTone.HAPPY,
        "excited": EmotionalTone.EXCITED,
        "calm": EmotionalTone.CALM,
        "sad": EmotionalTone.COMFORTING,
        "angry": EmotionalTone.CALM,
        "curious": EmotionalTone.CURIOUS,
        "playful": EmotionalTone.PLAYFUL,
    }
    return sentiment_mapping.get(sentiment.lower(), EmotionalTone.CALM)


def get_time_based_emotion() -> EmotionalTone:
    """Get emotion based on time of day"""
    from datetime import datetime

    hour = datetime.now().hour

    if 6 <= hour < 12:
        return EmotionalTone.HAPPY  # Morning
    elif 12 <= hour < 18:
        return EmotionalTone.PLAYFUL  # Afternoon
    elif 18 <= hour < 21:
        return EmotionalTone.CALM  # Evening
    else:
        return EmotionalTone.SLEEPY  # Night
