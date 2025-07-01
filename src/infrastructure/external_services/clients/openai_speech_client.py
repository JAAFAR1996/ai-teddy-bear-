"""
OpenAI Speech Client Infrastructure
Handles OpenAI Speech API integration
"""

import logging
import tempfile
from typing import Any, Dict, Optional

import numpy as np
import soundfile as sf
from openai import AsyncOpenAI


class OpenAISpeechClient:
    """Infrastructure client for OpenAI Speech API"""

    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
        self.logger = logging.getLogger(self.__class__.__name__)

    async def transcribe_audio(
        self,
        audio_data: np.ndarray,
        language: Optional[str] = None,
        model: str = "whisper-1",
    ) -> Optional[Dict[str, Any]]:
        """Transcribe audio using OpenAI Whisper API"""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                # Write audio data to temp file
                sf.write(temp_file.name, audio_data, 16000)

                # Transcribe with OpenAI
                with open(temp_file.name, "rb") as audio_file:
                    transcript = await self.client.audio.transcriptions.create(
                        model=model,
                        file=audio_file,
                        language=language,
                        response_format="verbose_json",
                        timestamp_granularities=["word", "segment"],
                    )

                return {
                    "text": transcript.text.strip(),
                    "language": transcript.language,
                    "duration": transcript.duration,
                    "segments": getattr(transcript, "segments", []),
                    "words": getattr(transcript, "words", []),
                }

        except Exception as e:
            self.logger.error(f"OpenAI transcription error: {e}")
            return None

    async def generate_speech(
        self,
        text: str,
        voice: str = "alloy",
        model: str = "tts-1",
        response_format: str = "mp3",
        speed: float = 1.0,
    ) -> Optional[bytes]:
        """Generate speech using OpenAI TTS"""
        try:
            response = await self.client.audio.speech.create(
                model=model,
                voice=voice,
                input=text,
                response_format=response_format,
                speed=speed,
            )

            return response.content

        except Exception as e:
            self.logger.error(f"OpenAI speech generation error: {e}")
            return None

    def get_available_voices(self) -> list:
        """Get available TTS voices"""
        return ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

    async def is_available(self) -> bool:
        """Check if OpenAI service is available"""
        try:
            # Simple health check by listing models
            models = await self.client.models.list()
            return len(models.data) > 0
        except Exception:
            return False
