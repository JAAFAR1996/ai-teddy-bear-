import io
from typing import Any, Dict, Optional
import numpy as np
import soundfile as sf
from openai import AsyncOpenAI
import logging

from .base import BaseProvider
from ..transcription_models import TranscriptionConfig

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseProvider):
    """Transcription provider for the OpenAI API."""

    def __init__(self, client: AsyncOpenAI, config: TranscriptionConfig):
        self.client = client
        self.config = config

    async def transcribe(
        self, audio_array: np.ndarray, language: Optional[str]
    ) -> Dict[str, Any]:
        """Transcribe using OpenAI Whisper API"""
        try:
            buffer = io.BytesIO()
            sf.write(
                buffer,
                audio_array,
                self.config.sample_rate,
                format="WAV"
            )
            buffer.seek(0)

            response = await self.client.audio.transcriptions.create(
                model="whisper-1",
                file=buffer,
                language=language,
                response_format="verbose_json",
            )

            return {
                "text": response.text.strip(),
                "confidence": 0.95,  # OpenAI API does not provide confidence
                "language": response.language,
                "segments": getattr(response, "segments", []),
                "provider": "openai",
            }
        except Exception as e:
            logger.error(f"❌ OpenAI transcription failed: {e}")
            raise  # Re-raise to be handled by the service
