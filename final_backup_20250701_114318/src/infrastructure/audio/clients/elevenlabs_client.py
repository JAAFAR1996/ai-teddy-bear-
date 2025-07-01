"""
ElevenLabs Client Infrastructure
Handles ElevenLabs API integration
"""

import logging
from typing import AsyncIterator, Optional

try:
    from elevenlabs import ElevenLabs, VoiceSettings, generate, stream
except ImportError:
    from src.infrastructure.external_services.mock.elevenlabs import ElevenLabs, VoiceSettings, generate, stream


class ElevenLabsClient:
    """Infrastructure client for ElevenLabs API"""

    def __init__(self, api_key: str):
        self.client = ElevenLabs(api_key=api_key)
        self.logger = logging.getLogger(self.__class__.__name__)

    async def generate_speech(
        self, text: str, voice_id: str, voice_settings: VoiceSettings, model: str = "eleven_multilingual_v2"
    ) -> Optional[bytes]:
        """Generate speech audio"""
        try:
            audio = generate(text=text, voice=voice_id, model=model, voice_settings=voice_settings)
            return audio

        except Exception as e:
            self.logger.error(f"ElevenLabs speech generation error: {e}")
            return None

    async def stream_speech(
        self, text: str, voice_id: str, voice_settings: VoiceSettings, model: str = "eleven_multilingual_v2"
    ) -> Optional[AsyncIterator[bytes]]:
        """Stream speech audio"""
        try:
            audio_stream = stream(text=text, voice=voice_id, model=model, voice_settings=voice_settings)
            return audio_stream

        except Exception as e:
            self.logger.error(f"ElevenLabs streaming error: {e}")
            return None

    async def get_available_voices(self) -> list:
        """Get available voices"""
        try:
            voices = self.client.voices.get_all()
            return voices.voices

        except Exception as e:
            self.logger.error(f"Failed to get voices: {e}")
            return []

    def is_available(self) -> bool:
        """Check if service is available"""
        try:
            # Simple health check
            self.client.voices.get_all()
            return True
        except Exception:
            return False
