# voice_interaction_service.py - Enhanced voice interaction with streaming integration

import asyncio
import logging
from typing import Dict, Any, Optional, List, AsyncIterator, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import io
import json
import uuid
from pathlib import Path
import wave
import struct
from collections import deque
from typing import Union
import numpy as np
import sounddevice as sd
import soundfile as sf
import whisper
import torch
import torchaudio
from openai import AsyncOpenAI
from elevenlabs import ElevenLabs, Voice, VoiceSettings
import webrtcvad
import noisereduce as nr
from scipy import signal
from scipy.io import wavfile
import librosa
import pyrubberband as pyrb
from pydub import AudioSegment
from pydub.effects import normalize
import azure.cognitiveservices.speech as speechsdk
from src.core.application.interfaces.services import IAIService

from src.infrastructure.config import get_config
from src.application.services.streaming_service import StreamingService
from src.domain.entities.audio_stream import AudioStream


class EmotionalTone(Enum):
    """Enhanced emotional voice tones for the teddy bear"""
    HAPPY = "happy"
    CALM = "calm"
    CURIOUS = "curious"
    SUPPORTIVE = "supportive"
    PLAYFUL = "playful"
    SLEEPY = "sleepy"
    EXCITED = "excited"
    STORYTELLING = "storytelling"
    EDUCATIONAL = "educational"
    COMFORTING = "comforting"


class Language(Enum):
    """Supported languages"""
    ENGLISH = "en"
    ARABIC = "ar"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    CHINESE = "zh"
    JAPANESE = "ja"
    KOREAN = "ko"


@dataclass
class AudioConfig:
    """Audio configuration settings"""
    sample_rate: int = 24000
    channels: int = 1
    chunk_size: int = 1024
    format: str = 'int16'

    # Voice Activity Detection
    vad_mode: int = 3  # 0-3, 3 is most aggressive
    vad_frame_duration: int = 30  # milliseconds

    # Noise reduction
    enable_noise_reduction: bool = True
    noise_reduction_strength: float = 0.5

    # Audio enhancement
    enable_normalization: bool = True
    target_loudness: float = -20.0  # dB

    # Recording
    silence_threshold: float = 0.01
    silence_duration: float = 2.0  # seconds
    max_recording_duration: float = 30.0  # seconds


@dataclass
class VoiceProfile:
    """Voice profile for different characters/modes"""
    id: str
    name: str
    voice_id: str  # ElevenLabs voice ID
    language: Language
    emotional_settings: Dict[EmotionalTone, VoiceSettings]
    pitch_adjustment: float = 0.0
    speed_adjustment: float = 1.0
    personality_prompt: str = ""


class VoiceActivityDetector:
    """Voice Activity Detection wrapper"""

    def __init__(self, config: AudioConfig):
        self.vad = webrtcvad.Vad(config.vad_mode)
        self.config = config
        self.frame_duration = config.vad_frame_duration
        self.sample_rate = config.sample_rate

    def is_speech(self, audio_frame: bytes) -> bool:
        """Check if audio frame contains speech"""
        return self.vad.is_speech(audio_frame, self.sample_rate)

    def get_speech_segments(self, audio_data: np.ndarray) -> List[tuple]:
        """Get speech segments from audio"""
        # Convert to bytes
        audio_bytes = audio_data.astype('int16').tobytes()

        # Frame size
        frame_size = int(self.sample_rate * self.frame_duration / 1000)

        segments = []
        speech_start = None

        for i in range(0, len(audio_data) - frame_size, frame_size):
            frame = audio_bytes[i*2:(i+frame_size)*2]

            if self.is_speech(frame):
                if speech_start is None:
                    speech_start = i
            else:
                if speech_start is not None:
                    segments.append((speech_start, i))
                    speech_start = None

        # Handle last segment
        if speech_start is not None:
            segments.append((speech_start, len(audio_data)))

        return segments


class AudioProcessor:
    """Advanced audio processing"""

    def __init__(self, config: AudioConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)

    async def process_audio(self, audio_data: np.ndarray) -> np.ndarray:
        """Apply audio processing pipeline"""
        try:
            # Noise reduction
            if self.config.enable_noise_reduction:
                audio_data = await self.reduce_noise(audio_data)

            # Normalization
            if self.config.enable_normalization:
                audio_data = await self.normalize_audio(audio_data)

            return audio_data

        except Exception as e:
            self.logger.error(f"Audio processing error: {e}")
            return audio_data

    async def reduce_noise(self, audio_data: np.ndarray) -> np.ndarray:
        """Reduce background noise"""
        try:
            # Use noisereduce library
            reduced = nr.reduce_noise(
                y=audio_data,
                sr=self.config.sample_rate,
                prop_decrease=self.config.noise_reduction_strength
            )
            return reduced

        except Exception as e:
            self.logger.error(f"Noise reduction error: {e}")
            return audio_data

    async def normalize_audio(self, audio_data: np.ndarray) -> np.ndarray:
        """Normalize audio levels"""
        try:
            # Calculate current RMS
            rms = np.sqrt(np.mean(audio_data**2))

            if rms > 0:
                # Calculate target RMS from dB
                target_rms = 10**(self.config.target_loudness/20)

                # Apply normalization
                normalized = audio_data * (target_rms / rms)

                # Prevent clipping
                max_val = np.max(np.abs(normalized))
                if max_val > 1.0:
                    normalized = normalized / max_val

                return normalized

            return audio_data

        except Exception as e:
            self.logger.error(f"Normalization error: {e}")
            return audio_data

    async def change_pitch(self, audio_data: np.ndarray, semitones: float) -> np.ndarray:
        """Change audio pitch"""
        try:
            # Use pyrubberband for pitch shifting
            shifted = pyrb.pitch_shift(
                audio_data,
                self.config.sample_rate,
                semitones
            )
            return shifted

        except Exception as e:
            self.logger.error(f"Pitch shift error: {e}")
            return audio_data

    async def change_speed(self, audio_data: np.ndarray, speed_factor: float) -> np.ndarray:
        """Change audio speed without affecting pitch"""
        try:
            # Use pyrubberband for time stretching
            stretched = pyrb.time_stretch(
                audio_data,
                self.config.sample_rate,
                speed_factor
            )
            return stretched

        except Exception as e:
            self.logger.error(f"Speed change error: {e}")
            return audio_data


class VoiceInteractionService:
    """
    Enhanced voice interaction service with full integration
    """

    def __init__(self, config=None):
        """Initialize voice interaction service"""
        self.config = config or get_config()
        self.logger = logging.getLogger(self.__class__.__name__)

        # Audio configuration
        self.audio_config = AudioConfig()

        # Initialize components
        self.audio_processor = AudioProcessor(self.audio_config)
        self.vad = VoiceActivityDetector(self.audio_config)

        # Voice synthesis setup
        self._init_voice_synthesis()

        # Speech recognition setup
        self._init_speech_recognition()

        # Voice profiles
        self.voice_profiles = self._load_voice_profiles()
        self.current_profile = None

        # Audio streams
        self.input_stream = None
        self.output_stream = None

        # Recording state
        self.is_recording = False
        self.audio_buffer = deque(maxlen=int(
            self.audio_config.sample_rate * self.audio_config.max_recording_duration
        ))

        # Streaming service integration
        self.streaming_service: Optional[StreamingService] = None
        
        # AI Service integration
        self.ai_service: Optional[IAIService] = None  # استخدم Interface
        
        # [AI-Generated by Amazon Q]: تم إضافة هذا الكود تلقائياً وفق دليل المشروع.
        # Emotion analysis integration
        from src.domain.services.emotion_analyzer import EmotionAnalyzer
        from src.domain.emotion_config import EmotionConfig
        emotion_config = EmotionConfig(
            api_key=getattr(self.config, 'HUME_API_KEY', '')
        )
        self.emotion_analyzer = EmotionAnalyzer(emotion_config.api_key)

        # Storage
        self.recordings_path = Path(getattr(
            self.config, 'RECORDINGS_PATH', 'data/recordings'))
        self.recordings_path.mkdir(parents=True, exist_ok=True)

    def _init_voice_synthesis(self):
        """Initialize voice synthesis"""
        # ElevenLabs
        if getattr(self.config, 'ELEVENLABS_API_KEY', None):
            self.elevenlabs_client = ElevenLabs(
                api_key=getattr(self.config, 'ELEVENLABS_API_KEY'))
        else:
            self.elevenlabs_client = None

        # Azure Speech (for additional language support)
        if getattr(self.config, 'AZURE_SPEECH_KEY', None):
            speech_config = speechsdk.SpeechConfig(
                subscription=getattr(self.config, 'AZURE_SPEECH_KEY'),
                region=getattr(self.config, 'AZURE_SPEECH_REGION', 'eastus')
            )
            self.azure_speech_config = speech_config
        else:
            self.azure_speech_config = None

    def _init_speech_recognition(self):
        """Initialize speech recognition"""
        # Whisper
        try:
            model_size = getattr(self.config, 'WHISPER_MODEL_SIZE', 'base')
            self.whisper_model = whisper.load_model(model_size)
            self.logger.info(f"Loaded Whisper model: {model_size}")
        except Exception as e:
            self.logger.error(f"Whisper model loading error: {e}")
            self.whisper_model = None

        # OpenAI (for better accuracy)
        if getattr(self.config, 'OPENAI_API_KEY', None):
            self.openai_client = AsyncOpenAI(
                api_key=getattr(self.config, 'OPENAI_API_KEY'))
        else:
            self.openai_client = None

    def _load_voice_profiles(self) -> Dict[str, VoiceProfile]:
        """Load voice profiles"""
        profiles = {}

        # Default teddy bear profile
        teddy_settings = {
            EmotionalTone.HAPPY: VoiceSettings(stability=0.3, similarity_boost=0.7, style=0.4),
            EmotionalTone.CALM: VoiceSettings(stability=0.5, similarity_boost=0.5, style=0.2),
            EmotionalTone.CURIOUS: VoiceSettings(stability=0.4, similarity_boost=0.6, style=0.5),
            EmotionalTone.SUPPORTIVE: VoiceSettings(stability=0.6, similarity_boost=0.4, style=0.3),
            EmotionalTone.PLAYFUL: VoiceSettings(stability=0.2, similarity_boost=0.8, style=0.6),
            EmotionalTone.SLEEPY: VoiceSettings(stability=0.7, similarity_boost=0.3, style=0.1),
            EmotionalTone.EXCITED: VoiceSettings(stability=0.1, similarity_boost=0.9, style=0.8),
            EmotionalTone.STORYTELLING: VoiceSettings(stability=0.4, similarity_boost=0.5, style=0.4),
            EmotionalTone.EDUCATIONAL: VoiceSettings(stability=0.6, similarity_boost=0.5, style=0.3),
            EmotionalTone.COMFORTING: VoiceSettings(
                stability=0.7, similarity_boost=0.4, style=0.2)
        }

        profiles['teddy_bear'] = VoiceProfile(
            id='teddy_bear',
            name='Friendly Teddy',
            voice_id=getattr(self.config, 'DEFAULT_VOICE_ID', 'josh'),
            language=Language.ENGLISH,
            emotional_settings=teddy_settings,
            pitch_adjustment=2.0,  # Slightly higher pitch
            speed_adjustment=0.95,  # Slightly slower
            personality_prompt="You are a warm, friendly teddy bear who loves children."
        )

        # Arabic voice profile
        if getattr(self.config, 'ARABIC_VOICE_ID', None):
            profiles['teddy_bear_ar'] = VoiceProfile(
                id='teddy_bear_ar',
                name='دبدوب الودود',
                voice_id=getattr(self.config, 'ARABIC_VOICE_ID'),
                language=Language.ARABIC,
                emotional_settings=teddy_settings,
                pitch_adjustment=1.5,
                speed_adjustment=0.9,
                personality_prompt="أنت دبدوب ودود يحب الأطفال ويتحدث بلطف."
            )

        return profiles

    def set_streaming_service(self, streaming_service: StreamingService):
        """Set streaming service for integration"""
        self.streaming_service = streaming_service

    async def start_voice_interaction(self, profile_id: str, session_id: str) -> dict:
        """Start voice interaction with input validation and real backend"""
        if not isinstance(profile_id, str) or not profile_id:
            self.logger.error("Invalid profile_id for start_voice_interaction")
            return {"status": "error", "reason": "Invalid profile_id"}
        if not isinstance(session_id, str) or not session_id:
            self.logger.error("Invalid session_id for start_voice_interaction")
            return {"status": "error", "reason": "Invalid session_id"}
        if hasattr(self, 'voice_backend'):
            return await self.voice_backend.start(profile_id, session_id)
        self.logger.error("voice_backend not configured")
        return {"status": "error", "reason": "Voice backend not configured"}

    async def stop_voice_interaction(self):
        """Stop voice interaction session"""
        try:
            self.is_recording = False

            # Stop audio streams
            await self._stop_audio_streams()

            self.logger.info("Stopped voice interaction")

        except Exception as e:
            self.logger.error(f"Failed to stop voice interaction: {e}")

    async def synthesize_speech(
        self,
        text: str,
        emotion: EmotionalTone = EmotionalTone.CALM,
        language: Optional[Language] = None,
        stream_output: bool = True
    ) -> Optional[bytes]:
        """
        Synthesize speech with emotional nuance

        Args:
            text: Text to convert to speech
            emotion: Emotional tone
            language: Language override
            stream_output: Whether to stream output

        Returns:
            Audio bytes if not streaming, None if streaming
        """
        try:
            if not self.current_profile:
                self.current_profile = self.voice_profiles['teddy_bear']

            # Get voice settings for emotion
            voice_settings = self.current_profile.emotional_settings.get(
                emotion,
                self.current_profile.emotional_settings[EmotionalTone.CALM]
            )

            # Use appropriate service based on language
            target_language = language or self.current_profile.language

            if target_language == Language.ARABIC and self.azure_speech_config:
                # Use Azure for Arabic
                audio_data = await self._synthesize_azure(text, emotion)
            elif self.elevenlabs_client:
                # Use ElevenLabs
                audio_data = await self._synthesize_elevenlabs(
                    text,
                    self.current_profile.voice_id,
                    voice_settings,
                    stream_output
                )
            else:
                raise ValueError("No voice synthesis service available")

            # Apply voice profile adjustments
            if audio_data and not stream_output:
                audio_data = await self._apply_voice_adjustments(audio_data)

            return audio_data if not stream_output else None

        except Exception as e:
            self.logger.error(f"Speech synthesis error: {e}")
            return None

    async def _synthesize_elevenlabs(
        self,
        text: str,
        voice_id: str,
        voice_settings: VoiceSettings,
        stream_output: bool
    ) -> Optional[bytes]:
        """Synthesize using ElevenLabs"""
        try:
            if stream_output and self.streaming_service:
                # Stream directly to output
                audio_stream = stream(
                    text=text,
                    voice=voice_id,
                    model="eleven_multilingual_v2",
                    voice_settings=voice_settings
                )

                async for chunk in audio_stream:
                    await self.streaming_service.output_buffer.write(chunk)

                return None
            else:
                # Generate complete audio
                audio = generate(
                    text=text,
                    voice=voice_id,
                    model="eleven_multilingual_v2",
                    voice_settings=voice_settings
                )
                return audio

        except Exception as e:
            self.logger.error(f"ElevenLabs synthesis error: {e}")
            return None

    async def _synthesize_azure(self, text: str, emotion: EmotionalTone) -> bytes:
        """Synthesize using Azure Speech"""
        try:
            # Configure voice based on emotion
            voice_name = self._get_azure_voice_name(emotion)

            speech_synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.azure_speech_config,
                audio_config=None
            )

            # SSML for emotional expression
            ssml = f"""
            <speak version='1.0' xml:lang='ar-SA'>
                <voice name='{voice_name}'>
                    <prosody rate='0.9' pitch='+5%'>
                        {text}
                    </prosody>
                </voice>
            </speak>
            """

            result = speech_synthesizer.speak_ssml_async(ssml).get()

            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                return result.audio_data
            else:
                raise Exception(f"Azure synthesis failed: {result.reason}")

        except Exception as e:
            self.logger.error(f"Azure synthesis error: {e}")
            return b""

    async def transcribe_audio(
        self,
        audio_data: Union[np.ndarray, bytes, str],
        language: Optional[Language] = None
    ) -> Dict[str, Any]:
        """
        Transcribe audio using best available service

        Args:
            audio_data: Audio as numpy array, bytes, or file path
            language: Expected language

        Returns:
            Transcription details
        """
        try:
            # Convert to numpy array if needed
            if isinstance(audio_data, bytes):
                audio_array = np.frombuffer(audio_data, dtype=np.int16)
            elif isinstance(audio_data, str):
                audio_array, _ = librosa.load(
                    audio_data, sr=self.audio_config.sample_rate)
            else:
                audio_array = audio_data

            # Process audio
            audio_array = await self.audio_processor.process_audio(audio_array)

            # Try OpenAI first for better accuracy
            if self.openai_client:
                result = await self._transcribe_openai(audio_array, language)
                if result['text']:
                    return result

            # Fall back to Whisper
            if self.whisper_model:
                result = await self._transcribe_whisper(audio_array, language)
                if result['text']:
                    return result

            # Fall back to Azure
            if self.azure_speech_config:
                result = await self._transcribe_azure(audio_array, language)
                if result['text']:
                    return result

            return {"text": "", "language": "", "confidence": 0.0}

        except Exception as e:
            self.logger.error(f"Transcription error: {e}")
            return {"text": "", "language": "", "confidence": 0.0}

    async def _transcribe_whisper(
        self,
        audio_array: np.ndarray,
        language: Optional[Language]
    ) -> Dict[str, Any]:
        """Transcribe using Whisper"""
        try:
            # Prepare audio
            audio_float32 = audio_array.astype(np.float32) / 32768.0

            # Transcribe
            result = self.whisper_model.transcribe(
                audio_float32,
                language=language.value if language else None,
                task='transcribe'
            )

            return {
                "text": result['text'].strip(),
                "language": result.get('language', ''),
                "confidence": 1.0 - result.get('no_speech_prob', 0.0),
                "segments": result.get('segments', [])
            }

        except Exception as e:
            self.logger.error(f"Whisper transcription error: {e}")
            return {"text": "", "language": "", "confidence": 0.0}

    async def _transcribe_openai(
        self,
        audio_array: np.ndarray,
        language: Optional[Language]
    ) -> Dict[str, Any]:
        """Transcribe using OpenAI API"""
        try:
            # Save to temporary file
            temp_path = self.recordings_path / f"temp_{uuid.uuid4()}.wav"
            sf.write(temp_path, audio_array, self.audio_config.sample_rate)

            # Transcribe
            with open(temp_path, 'rb') as audio_file:
                transcript = await self.openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language.value if language else None
                )

            # Clean up
            temp_path.unlink()

            return {
                "text": transcript.text,
                "language": language.value if language else "unknown",
                "confidence": 0.95  # OpenAI doesn't provide confidence
            }

        except Exception as e:
            self.logger.error(f"OpenAI transcription error: {e}")
            return {"text": "", "language": "", "confidence": 0.0}

    async def _recording_loop(self, session_id: str):
        """Main recording loop"""
        try:
            self.is_recording = True
            silence_samples = 0
            speech_buffer = []

            while self.is_recording:
                # Read from input stream
                audio_chunk = await self._read_audio_chunk()

                if audio_chunk is None:
                    await asyncio.sleep(0.01)
                    continue

                # Add to buffer
                self.audio_buffer.extend(audio_chunk)

                # Check for speech
                is_speech = self.vad.is_speech(
                    audio_chunk.astype('int16').tobytes()
                )

                if is_speech:
                    speech_buffer.extend(audio_chunk)
                    silence_samples = 0
                else:
                    silence_samples += len(audio_chunk)

                    # Check if silence threshold reached
                    silence_duration = silence_samples / self.audio_config.sample_rate

                    if speech_buffer and silence_duration >= self.audio_config.silence_duration:
                        # Process complete utterance
                        await self._process_utterance(
                            np.array(speech_buffer),
                            session_id
                        )

                        # Clear buffer
                        speech_buffer = []

        except Exception as e:
            self.logger.error(f"Recording loop error: {e}")
        finally:
            self.is_recording = False

    async def _process_utterance(self, audio_data: np.ndarray, session_id: str):
        """Process a complete utterance"""
        try:
            # Save recording
            recording_path = await self.save_recording(audio_data, session_id)

            # Transcribe
            transcription = await self.transcribe_audio(audio_data)

            if transcription['text'] and self.streaming_service:
                # Send to streaming service for processing
                await self.streaming_service.process_text_input(
                    transcription['text'],
                    session_id
                )

        except Exception as e:
            self.logger.error(f"Utterance processing error: {e}")

    async def save_recording(
        self,
        audio_data: np.ndarray,
        session_id: str,
        metadata: Optional[Dict] = None
    ) -> str:
        """Save audio recording with metadata"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{session_id}_{timestamp}.wav"
            filepath = self.recordings_path / filename

            # Save audio
            sf.write(
                filepath,
                audio_data,
                self.audio_config.sample_rate,
                subtype='PCM_16'
            )

            # Save metadata
            metadata_path = filepath.with_suffix('.json')
            metadata_content = {
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'duration_seconds': len(audio_data) / self.audio_config.sample_rate,
                'sample_rate': self.audio_config.sample_rate,
                **(metadata or {})
            }

            with open(metadata_path, 'w') as f:
                json.dump(metadata_content, f, indent=2)

            return str(filepath)

        except Exception as e:
            self.logger.error(f"Recording save error: {e}")
            return ""

    async def _apply_voice_adjustments(self, audio_data: bytes) -> bytes:
        """Apply voice profile adjustments"""
        try:
            # Convert to numpy
            audio_array = np.frombuffer(
                audio_data, dtype=np.int16).astype(np.float32)

            # Apply pitch adjustment
            if self.current_profile.pitch_adjustment != 0:
                audio_array = await self.audio_processor.change_pitch(
                    audio_array,
                    self.current_profile.pitch_adjustment
                )

            # Apply speed adjustment
            if self.current_profile.speed_adjustment != 1.0:
                audio_array = await self.audio_processor.change_speed(
                    audio_array,
                    self.current_profile.speed_adjustment
                )

            # Convert back to bytes
            return audio_array.astype(np.int16).tobytes()

        except Exception as e:
            self.logger.error(f"Voice adjustment error: {e}")
            return audio_data

    async def _start_audio_streams(self):
        """Start audio input/output streams"""
        try:
            # Input stream for recording
            self.input_stream = sd.InputStream(
                samplerate=self.audio_config.sample_rate,
                channels=self.audio_config.channels,
                dtype=self.audio_config.format,
                blocksize=self.audio_config.chunk_size,
                callback=self._input_callback
            )

            # Output stream for playback
            self.output_stream = sd.OutputStream(
                samplerate=self.audio_config.sample_rate,
                channels=self.audio_config.channels,
                dtype=self.audio_config.format,
                blocksize=self.audio_config.chunk_size,
                callback=self._output_callback
            )

            self.input_stream.start()
            self.output_stream.start()

        except Exception as e:
            self.logger.error(f"Failed to start audio streams: {e}")
            raise

    async def _stop_audio_streams(self):
        """Stop audio streams"""
        try:
            if self.input_stream:
                self.input_stream.stop()
                self.input_stream.close()

            if self.output_stream:
                self.output_stream.stop()
                self.output_stream.close()

        except Exception as e:
            self.logger.error(f"Failed to stop audio streams: {e}")

    def _input_callback(self, indata, frames, time_info, status):
        """Audio input callback"""
        if status:
            self.logger.warning(f"Input status: {status}")

        # Add to recording buffer
        if self.is_recording and indata is not None:
            asyncio.create_task(self._add_to_buffer(indata.copy()))

    def _output_callback(self, outdata, frames, time_info, status):
        """Audio output callback"""
        if status:
            self.logger.warning(f"Output status: {status}")

        # Get audio from streaming service output buffer
        if self.streaming_service:
            asyncio.create_task(self._get_output_audio(outdata, frames))
        else:
            # Fill with silence
            outdata.fill(0)

    async def _add_to_buffer(self, audio_data):
        """Add audio data to buffer"""
        self.audio_buffer.extend(audio_data.flatten())

    async def _get_output_audio(self, outdata, frames):
        """Get audio from output buffer"""
        try:
            audio_bytes = await self.streaming_service.output_buffer.read(frames * 2)

            if audio_bytes:
                audio_array = np.frombuffer(audio_bytes, dtype=np.int16)

                # Ensure correct size
                if len(audio_array) < frames:
                    # Pad with silence
                    padded = np.zeros(frames, dtype=np.int16)
                    padded[:len(audio_array)] = audio_array
                    audio_array = padded
                elif len(audio_array) > frames:
                    audio_array = audio_array[:frames]

                outdata[:] = audio_array.reshape(-1, 1)
            else:
                outdata.fill(0)

        except Exception as e:
            self.logger.error(f"Output audio error: {e}")
            outdata.fill(0)

    async def _read_audio_chunk(self) -> Optional[np.ndarray]:
        """Read audio chunk from input"""
        try:
            if len(self.audio_buffer) >= self.audio_config.chunk_size:
                # Get chunk from buffer
                chunk = []
                for _ in range(self.audio_config.chunk_size):
                    chunk.append(self.audio_buffer.popleft())

                return np.array(chunk, dtype=np.int16)

            return None

        except Exception as e:
            self.logger.error(f"Read audio chunk error: {e}")
            return None

    def _get_azure_voice_name(self, emotion: EmotionalTone) -> str:
        """Get Azure voice name based on emotion"""
        # Arabic voices with emotional variants
        voice_map = {
            EmotionalTone.HAPPY: "ar-SA-ZariyahNeural",
            EmotionalTone.CALM: "ar-SA-HamedNeural",
            EmotionalTone.STORYTELLING: "ar-SA-ZariyahNeural",
            EmotionalTone.EDUCATIONAL: "ar-SA-HamedNeural"
        }

        return voice_map.get(emotion, "ar-SA-ZariyahNeural")

    async def calibrate_audio(self, duration: float = 3.0) -> Dict[str, float]:
        """Calibrate audio levels"""
        try:
            self.logger.info("Starting audio calibration...")

            # Record ambient noise
            calibration_buffer = []
            start_time = asyncio.get_event_loop().time()

            while asyncio.get_event_loop().time() - start_time < duration:
                chunk = await self._read_audio_chunk()
                if chunk is not None:
                    calibration_buffer.extend(chunk)
                await asyncio.sleep(0.01)

            # Calculate noise profile
            noise_array = np.array(calibration_buffer, dtype=np.float32)

            # Calculate RMS
            noise_rms = np.sqrt(np.mean(noise_array**2))

            # Calculate peak
            noise_peak = np.max(np.abs(noise_array))

            # Update silence threshold
            self.audio_config.silence_threshold = noise_rms * 3  # 3x noise floor

            calibration_results = {
                'noise_rms': float(noise_rms),
                'noise_peak': float(noise_peak),
                'silence_threshold': float(self.audio_config.silence_threshold),
                'recommended_volume': 0.7 if noise_rms < 0.01 else 0.9
            }

            self.logger.info(f"Calibration complete: {calibration_results}")

            return calibration_results

        except Exception as e:
            self.logger.error(f"Calibration error: {e}")
            return {}

    async def play_audio(
        self,
        audio_data: Union[bytes, np.ndarray],
        wait: bool = True
    ):
        """Play audio through output stream"""
        try:
            # Convert to numpy array if needed
            if isinstance(audio_data, bytes):
                audio_array = np.frombuffer(audio_data, dtype=np.int16)
            else:
                audio_array = audio_data

            # Apply processing
            audio_array = await self.audio_processor.process_audio(audio_array)

            # Play through sounddevice
            sd.play(audio_array, samplerate=self.audio_config.sample_rate)

            if wait:
                sd.wait()

        except Exception as e:
            self.logger.error(f"Audio playback error: {e}")

    async def detect_wake_word(
        self,
        wake_words: List[str] = ["hey teddy", "hello teddy", "مرحبا دبدوب"],
        sensitivity: float = 0.5
    ) -> bool:
        """Detect wake word in audio stream"""
        try:
            # Get recent audio
            audio_data = np.array(list(self.audio_buffer))

            if len(audio_data) < self.audio_config.sample_rate:
                return False

            # Transcribe recent audio
            result = await self.transcribe_audio(audio_data[-self.audio_config.sample_rate * 3:])

            if result['text']:
                text_lower = result['text'].lower()

                # Check for wake words
                for wake_word in wake_words:
                    if wake_word.lower() in text_lower:
                        self.logger.info(f"Wake word detected: {wake_word}")
                        return True

            return False

        except Exception as e:
            self.logger.error(f"Wake word detection error: {e}")
            return False

    async def handle_interruption(self):
        """Handle user interruption during playback"""
        try:
            self.logger.info("User interruption detected")

            # Stop current playback
            sd.stop()

            # Clear output buffer if streaming
            if self.streaming_service:
                await self.streaming_service.output_buffer.clear()

            # Send interruption signal to streaming service
            if self.streaming_service:
                await self.streaming_service.handle_control_command(
                    "interrupt",
                    "session_id"
                )

        except Exception as e:
            self.logger.error(f"Interruption handling error: {e}")

    async def get_supported_languages(self) -> List[Dict[str, str]]:
        """Get list of supported languages"""
        languages = []

        # ElevenLabs languages
        if self.elevenlabs_client:
            languages.extend([
                {"code": "en", "name": "English", "service": "elevenlabs"},
                {"code": "es", "name": "Spanish", "service": "elevenlabs"},
                {"code": "fr", "name": "French", "service": "elevenlabs"},
                {"code": "de", "name": "German", "service": "elevenlabs"},
                {"code": "it", "name": "Italian", "service": "elevenlabs"},
                {"code": "pt", "name": "Portuguese", "service": "elevenlabs"},
                {"code": "pl", "name": "Polish", "service": "elevenlabs"},
                {"code": "tr", "name": "Turkish", "service": "elevenlabs"},
                {"code": "ru", "name": "Russian", "service": "elevenlabs"},
                {"code": "nl", "name": "Dutch", "service": "elevenlabs"},
                {"code": "sv", "name": "Swedish", "service": "elevenlabs"},
                {"code": "id", "name": "Indonesian", "service": "elevenlabs"},
                {"code": "fil", "name": "Filipino", "service": "elevenlabs"},
                {"code": "ja", "name": "Japanese", "service": "elevenlabs"},
                {"code": "ko", "name": "Korean", "service": "elevenlabs"},
                {"code": "zh", "name": "Chinese", "service": "elevenlabs"},
                {"code": "hi", "name": "Hindi", "service": "elevenlabs"},
                {"code": "ar", "name": "Arabic", "service": "elevenlabs"}
            ])

        # Azure languages (additional)
        if self.azure_speech_config:
            languages.extend([
                {"code": "ar", "name": "Arabic", "service": "azure"},
                {"code": "he", "name": "Hebrew", "service": "azure"},
                {"code": "ur", "name": "Urdu", "service": "azure"},
                {"code": "fa", "name": "Persian", "service": "azure"}
            ])

        # Remove duplicates
        seen = set()
        unique_languages = []
        for lang in languages:
            if lang['code'] not in seen:
                seen.add(lang['code'])
                unique_languages.append(lang)

        return unique_languages

    async def test_voice_synthesis(
        self,
        test_text: str = "Hello, I'm your friendly teddy bear! How are you today?",
        emotion: EmotionalTone = EmotionalTone.HAPPY
    ) -> bool:
        """Test voice synthesis"""
        try:
            self.logger.info("Testing voice synthesis...")

            # Synthesize
            audio_data = await self.synthesize_speech(
                test_text,
                emotion=emotion,
                stream_output=False
            )

            if audio_data:
                # Play audio
                await self.play_audio(audio_data)
                return True

            return False

        except Exception as e:
            self.logger.error(f"Voice synthesis test failed: {e}")
            return False

    async def test_speech_recognition(self, duration: float = 5.0) -> Dict[str, Any]:
        """Test speech recognition"""
        try:
            self.logger.info(
                f"Testing speech recognition for {duration} seconds...")

            # Record audio
            recording_buffer = []
            start_time = asyncio.get_event_loop().time()

            while asyncio.get_event_loop().time() - start_time < duration:
                chunk = await self._read_audio_chunk()
                if chunk is not None:
                    recording_buffer.extend(chunk)
                await asyncio.sleep(0.01)

            # Transcribe
            audio_array = np.array(recording_buffer, dtype=np.int16)
            result = await self.transcribe_audio(audio_array)

            self.logger.info(f"Recognition result: {result}")

            return result

        except Exception as e:
            self.logger.error(f"Speech recognition test failed: {e}")
            return {"text": "", "language": "", "confidence": 0.0}

    def set_ai_service(self, ai_service):
        self.ai_service = ai_service



async def process_message(self, conversation_id, data):
    import re
    from langdetect import detect
    from src.domain.entities.child import Child, ChildPreferences
    from textblob import TextBlob
    import logging
    user_text = data.get("text", "")
    session_id = conversation_id or data.get("session_id") or "test-session-1"
    logger = logging.getLogger(__name__)

    # --- Language Detection ---
    try:
        detected_language = detect(user_text) if user_text.strip() else "ar"
    except Exception as e:
    logger.error(f"Error: {e}", exc_info=True)as e:
    logger.error(f"Error: {e}", exc_info=True)        detected_language = "ar"

    # --- Child Name Extraction ---
    name_pattern = r"(?:اسمي|أنا اسمي|My name is|I am|I'm|انا اسمي|انا)\s+([\u0600-\u06FF\w]+)"
    match = re.search(name_pattern, user_text, re.IGNORECASE)
    extracted_name = match.group(1) if match else None

    # --- Session Context Management ---
    context = self.ai_service.active_contexts.get(session_id, {})
    child_name = extracted_name or context.get('child_name', 'Ahmad')
    preferred_language = detected_language or context.get('preferred_language', 'ar')
    memory = context.get('memory', [])
    age = context.get('age', 7)
    learning_interests = context.get('learning_interests', ['games'])

    # Update context
    context.update({
        'child_name': child_name,
        'preferred_language': preferred_language,
        'memory': memory,
        'age': age,
        'learning_interests': learning_interests
    })
    self.ai_service.active_contexts[session_id] = context

    # --- Child Object for Session (if needed) ---
    if session_id not in self.ai_service.active_contexts:
        dummy_child = Child(
            id=session_id,
            name=child_name,
            age=age,
            preferences=ChildPreferences(
                language=preferred_language,
                learning_interests=learning_interests)
        )
        await self.ai_service.create_session_context(dummy_child, session_id=session_id)

    # --- Prompt Construction ---
    prompt = f"Child Name: {child_name}\nPreferred Language: {preferred_language}\n"
    if memory:
        prompt += f"Memory: {memory}\n"
    prompt += f"Input: {user_text}"

    # --- AI Response Generation ---
    ai_response = await self.ai_service.get_response(prompt, session_id=session_id)
    response_text = ai_response.content if hasattr(ai_response, 'content') else ai_response

    # --- Translation Fallback ---
    if preferred_language == 'ar' and is_english(response_text):
        try:
            tb = TextBlob(response_text)
            translated = str(tb.translate(to='ar'))
            response_text = translated
        except Exception as e:
            logger.warning(f"Translation to Arabic failed: {e}")

    return {"type": "response", "text": response_text}

def is_arabic(text):
    return any('\u0600' <= c <= '\u06FF' for c in text)

def is_english(text):
    return all(ord(c) < 128 for c in text if c.isalpha())

def get_emotion_from_sentiment(sentiment: str) -> EmotionalTone:
    """Map sentiment to emotional tone"""
    sentiment_map = {
        'positive': EmotionalTone.HAPPY,
        'negative': EmotionalTone.COMFORTING,
        'neutral': EmotionalTone.CALM,
        'question': EmotionalTone.CURIOUS,
        'excited': EmotionalTone.EXCITED,
        'sad': EmotionalTone.SUPPORTIVE,
        'tired': EmotionalTone.SLEEPY
    }

    return sentiment_map.get(sentiment.lower(), EmotionalTone.CALM)


def get_time_based_emotion() -> EmotionalTone:
    """Get appropriate emotion based on time of day"""
    current_hour = datetime.now().hour

    if 6 <= current_hour < 12:
        return EmotionalTone.HAPPY  # Morning
    elif 12 <= current_hour < 17:
        return EmotionalTone.PLAYFUL  # Afternoon
    elif 17 <= current_hour < 20:
        return EmotionalTone.CALM  # Evening
    else:
        return EmotionalTone.SLEEPY  # Night


class VoiceProfileManager:
    """Manage custom voice profiles"""

    def __init__(self, storage_path: str = "data/voice_profiles"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

    async def save_profile(self, profile: VoiceProfile) -> bool:
        """Save voice profile"""
        try:
            profile_path = self.storage_path / f"{profile.id}.json"

            profile_data = {
                'id': profile.id,
                'name': profile.name,
                'voice_id': profile.voice_id,
                'language': profile.language.value,
                'pitch_adjustment': profile.pitch_adjustment,
                'speed_adjustment': profile.speed_adjustment,
                'personality_prompt': profile.personality_prompt,
                'emotional_settings': {
                    emotion.value: {
                        'stability': settings.stability,
                        'similarity_boost': settings.similarity_boost,
                        'style': settings.style
                    }
                    for emotion, settings in profile.emotional_settings.items()
                }
            }

            with open(profile_path, 'w') as f:
                json.dump(profile_data, f, indent=2)

            return True

        except Exception as e:
            logging.error(f"Failed to save voice profile: {e}")
            return False

    async def load_profile(self, profile_id: str) -> Optional[VoiceProfile]:
        """Load voice profile"""
        try:
            profile_path = self.storage_path / f"{profile_id}.json"

            if not profile_path.exists():
                return None

            with open(profile_path, 'r') as f:
                profile_data = json.load(f)

            # Reconstruct emotional settings
            emotional_settings = {}
            for emotion_str, settings in profile_data['emotional_settings'].items():
                emotional_settings[EmotionalTone(
                    emotion_str)] = VoiceSettings(**settings)

            profile = VoiceProfile(
                id=profile_data['id'],
                name=profile_data['name'],
                voice_id=profile_data['voice_id'],
                language=Language(profile_data['language']),
                emotional_settings=emotional_settings,
                pitch_adjustment=profile_data['pitch_adjustment'],
                speed_adjustment=profile_data['speed_adjustment'],
                personality_prompt=profile_data['personality_prompt']
            )

            return profile

        except Exception as e:
            logging.error(f"Failed to load voice profile: {e}")
            return None
