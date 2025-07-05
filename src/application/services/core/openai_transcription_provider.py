from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import io
from dataclasses import dataclass

from openai import AsyncOpenAI
from pydantic import BaseModel
import structlog

# This will cause a circular import if not handled carefully.
# Assuming TranscriptionResult and TranscriptionConfig are defined in a separate models file.
# For now, let's define them here for clarity.


class TranscriptionConfig(BaseModel):
    """Transcription configuration"""
    provider: Any  # Using Any to avoid circular dependency for now
    language: str = "ar"
    model: str = "whisper-1"
    temperature: float = 0.0
    enable_punctuation: bool = True
    enable_word_timestamps: bool = False
    enable_speaker_diarization: bool = False
    max_alternatives: int = 1
    profanity_filter: bool = True
    timeout: float = 30.0


@dataclass
class TranscriptionResult:
    """Transcription result"""
    text: str
    language: str
    confidence: float = 1.0
    duration: Optional[float] = None
    words: List[Dict[str, Any]] = None
    alternatives: List[Dict[str, Any]] = None
    metadata: Dict[str, Any] = None


logger = structlog.get_logger()


class TranscriptionProviderBase(ABC):
    """Base class for transcription providers"""

    @abstractmethod
    async def transcribe(self, audio_data: bytes, config: "TranscriptionConfig") -> "TranscriptionResult":
        """Transcribe audio data"""
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        """Check if provider is available"""
        pass


class OpenAITranscriptionProvider(TranscriptionProviderBase):
    """OpenAI Whisper API provider"""

    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)

    async def transcribe(self, audio_data: bytes, config: "TranscriptionConfig") -> "TranscriptionResult":
        """Transcribe using OpenAI Whisper API."""
        try:
            response = await self._call_openai_api(audio_data, config)
            result = self._parse_openai_response(response, config)
            self._log_transcription_success(result)
            return result
        except Exception as e:
            logger.error("OpenAI transcription failed", error=str(e))
            raise

    async def _call_openai_api(self, audio_data: bytes, config: "TranscriptionConfig"):
        """Call OpenAI API with proper formatting."""
        audio_file = io.BytesIO(audio_data)
        audio_file.name = "audio.wav"
        return await self.client.audio.transcriptions.create(
            model=config.model,
            file=audio_file,
            language=config.language,
            temperature=config.temperature,
            response_format="verbose_json" if config.enable_word_timestamps else "json",
        )

    def _parse_openai_response(self, response: Any, config: "TranscriptionConfig") -> "TranscriptionResult":
        """Parse OpenAI response into TranscriptionResult."""
        return TranscriptionResult(
            text=response.text,
            language=getattr(response, "language", config.language),
            duration=getattr(response, "duration", None),
            words=getattr(response, "words", None),
            metadata={"provider": "openai", "model": config.model},
        )

    def _log_transcription_success(self, result: "TranscriptionResult") -> None:
        """Log successful transcription."""
        logger.info("OpenAI transcription completed", text_length=len(
            result.text), language=result.language)

    async def is_available(self) -> bool:
        """Check if OpenAI is available."""
        try:
            await self.client.models.list()
            return True
        except Exception as e:
            logger.error("OpenAI availability check failed", error=str(e))
            return False
