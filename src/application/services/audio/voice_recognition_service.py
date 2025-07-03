"""
Voice Recognition Application Service
Handles speech-to-text conversion and audio transcription
"""

import logging
import tempfile
from typing import Any, Dict, Optional, Union

import numpy as np
import soundfile as sf
import whisper
from openai import AsyncOpenAI

from src.domain.audio.models.voice_models import Language


class VoiceRecognitionService:
    """Application service for voice recognition operations"""

    def __init__(self, config=None):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)

        # Initialize recognition engines
        self._init_recognition_engines()

    def _init_recognition_engines(self):
        """Initialize speech recognition engines"""
        # Whisper
        try:
            model_size = getattr(self.config, "WHISPER_MODEL_SIZE", "base")
            self.whisper_model = whisper.load_model(model_size)
            self.logger.info(f"Loaded Whisper model: {model_size}")
        except Exception as e:
            self.logger.error(f"Whisper model loading error: {e}")
            self.whisper_model = None

        # OpenAI
        if getattr(self.config, "OPENAI_API_KEY", None):
            self.openai_client = AsyncOpenAI(
                api_key=getattr(self.config, "OPENAI_API_KEY")
            )
        else:
            self.openai_client = None

    async def transcribe_audio(
        self,
        audio_data: Union[np.ndarray, bytes, str],
        language: Optional[Language] = None,
        use_openai: bool = False,
    ) -> Dict[str, Any]:
        """
        Transcribe audio to text

        Args:
            audio_data: Audio data in various formats
            language: Target language for transcription
            use_openai: Whether to use OpenAI instead of Whisper

        Returns:
            Dictionary with transcription results
        """
        try:
            # Convert audio data to numpy array
            audio_array = await self._prepare_audio_data(audio_data)

            if audio_array is None:
                return {"error": "Failed to process audio data", "text": ""}

            # Choose transcription method
            if use_openai and self.openai_client:
                result = await self._transcribe_openai(audio_array, language)
            elif self.whisper_model:
                result = await self._transcribe_whisper(audio_array, language)
            else:
                return {"error": "No transcription service available", "text": ""}

            return result

        except Exception as e:
            self.logger.error(f"Transcription error: {e}")
            return {"error": str(e), "text": ""}

    async def _prepare_audio_data(
        self, audio_data: Union[np.ndarray, bytes, str]
    ) -> Optional[np.ndarray]:
        """Prepare audio data for transcription"""
        try:
            if isinstance(audio_data, np.ndarray):
                return audio_data
            elif isinstance(audio_data, bytes):
                # Convert bytes to numpy array
                return (
                    np.frombuffer(audio_data, dtype=np.int16).astype(np.float32)
                    / 32768.0
                )
            elif isinstance(audio_data, str):
                # Load from file
                data, _ = sf.read(audio_data)
                return data
            else:
                self.logger.error(f"Unsupported audio data type: {type(audio_data)}")
                return None

        except Exception as e:
            self.logger.error(f"Audio preparation error: {e}")
            return None

    async def _transcribe_whisper(
        self, audio_array: np.ndarray, language: Optional[Language]
    ) -> Dict[str, Any]:
        """Transcribe using Whisper model"""
        try:
            # Prepare language parameter
            lang_code = language.value if language else None

            # Transcribe
            result = self.whisper_model.transcribe(
                audio_array, language=lang_code, task="transcribe"
            )

            return {
                "text": result["text"].strip(),
                "language": result.get("language"),
                "confidence": self._calculate_whisper_confidence(result),
                "segments": result.get("segments", []),
                "method": "whisper",
            }

        except Exception as e:
            self.logger.error(f"Whisper transcription error: {e}")
            return {"error": str(e), "text": ""}

    async def _transcribe_openai(
        self, audio_array: np.ndarray, language: Optional[Language]
    ) -> Dict[str, Any]:
        """Transcribe using OpenAI API"""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                sf.write(temp_file.name, audio_array, 16000)

                # Transcribe with OpenAI
                with open(temp_file.name, "rb") as audio_file:
                    transcript = await self.openai_client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        language=language.value if language else None,
                    )

                return {
                    "text": transcript.text.strip(),
                    "language": language.value if language else "auto",
                    "confidence": 0.95,  # OpenAI doesn't provide confidence
                    "method": "openai",
                }

        except Exception as e:
            self.logger.error(f"OpenAI transcription error: {e}")
            return {"error": str(e), "text": ""}

    def _calculate_whisper_confidence(self, result: Dict) -> float:
        """Calculate average confidence from Whisper result"""
        try:
            segments = result.get("segments", [])
            if not segments:
                return 0.5

            # Average probability from all segments
            total_prob = sum(segment.get("avg_logprob", -1.0) for segment in segments)
            avg_logprob = total_prob / len(segments)

            # Convert log probability to confidence (rough approximation)
            confidence = max(0.0, min(1.0, (avg_logprob + 1.0) / 1.0))
            return confidence

        # FIXME: replace with specific exception
except Exception as exc:return 0.5

    async def detect_language(self, audio_array: np.ndarray) -> Optional[Language]:
        """Detect language from audio"""
        try:
            if not self.whisper_model:
                return None

            # Use Whisper's language detection
            result = self.whisper_model.transcribe(audio_array, task="transcribe")
            detected_lang = result.get("language")

            # Map to our Language enum
            lang_mapping = {
                "en": Language.ENGLISH,
                "ar": Language.ARABIC,
                "es": Language.SPANISH,
                "fr": Language.FRENCH,
                "de": Language.GERMAN,
                "zh": Language.CHINESE,
                "ja": Language.JAPANESE,
                "ko": Language.KOREAN,
            }

            return lang_mapping.get(detected_lang)

        except Exception as e:
            self.logger.error(f"Language detection error: {e}")
            return None

    async def test_recognition(self, duration: float = 5.0) -> Dict[str, Any]:
        """Test speech recognition capability"""
        try:
            # Create test audio (silence)
            sample_rate = 16000
            test_audio = np.zeros(int(sample_rate * duration), dtype=np.float32)

            result = await self.transcribe_audio(test_audio)

            return {
                "success": "text" in result,
                "method": result.get("method", "unknown"),
                "error": result.get("error"),
            }

        except Exception as e:
            self.logger.error(f"Recognition test failed: {e}")
            return {"success": False, "error": str(e)}
