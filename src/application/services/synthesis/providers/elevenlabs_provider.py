#!/usr/bin/env python3
"""
🔊 ElevenLabs Synthesis Provider
موفر خدمة تركيب الصوت من ElevenLabs
"""

import asyncio
import logging
from typing import AsyncIterator, Optional

# ElevenLabs imports
try:
    from elevenlabs import ElevenLabs, generate, stream
except ImportError:
    try:
        from src.infrastructure.external_services.mock.elevenlabs import (
            ElevenLabs,
            generate,
            stream,
        )
    except ImportError:
        ElevenLabs = generate = stream = None

from .base_provider import BaseSynthesisProvider
from ..models import SynthesisContext

logger = logging.getLogger(__name__)


class ElevenLabsProvider(BaseSynthesisProvider):
    """ElevenLabs synthesis provider implementation"""

    def __init__(self):
        """Initialize ElevenLabs provider"""
        super().__init__("ElevenLabs")
        self.client: Optional[ElevenLabs] = None

    async def initialize(self, credentials: dict) -> bool:
        """Initialize ElevenLabs client with API key"""
        try:
            api_key = credentials.get("elevenlabs_api_key")
            if not api_key:
                logger.warning("ElevenLabs API key not provided")
                return False

            if ElevenLabs is None:
                logger.error("ElevenLabs library not available")
                return False

            self.client = ElevenLabs(api_key=api_key)
            self.is_initialized = True

            logger.info("✅ ElevenLabs provider initialized")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to initialize ElevenLabs provider: {e}")
            return False

    async def synthesize_audio(
            self, context: SynthesisContext) -> Optional[bytes]:
        """Synthesize complete audio using ElevenLabs"""
        if not self.is_available():
            logger.error("ElevenLabs provider not initialized")
            return None

        try:
            audio = generate(
                text=context.text,
                voice=context.character.voice_id,
                model="eleven_multilingual_v2",
                voice_settings=context.voice_settings,
            )

            logger.debug(f"ElevenLabs synthesis completed: {len(audio)} bytes")
            return audio

        except Exception as e:
            logger.error(f"❌ ElevenLabs synthesis failed: {e}")
            return None

    async def synthesize_stream(
        self, context: SynthesisContext
    ) -> AsyncIterator[bytes]:
        """Synthesize streaming audio using ElevenLabs"""
        if not self.is_available():
            logger.error("ElevenLabs provider not initialized")
            return

        try:
            # Generate stream
            audio_stream = stream(
                text=context.text,
                voice=context.character.voice_id,
                model="eleven_multilingual_v2",
                voice_settings=context.voice_settings,
            )

            # Yield chunks
            for chunk in audio_stream:
                yield chunk

        except Exception as e:
            logger.error(f"❌ ElevenLabs streaming failed: {e}")

            # Fallback to regular generation
            try:
                audio = generate(
                    text=context.text,
                    voice=context.character.voice_id,
                    voice_settings=context.voice_settings,
                )

                # Chunk for streaming
                chunk_size = 1024
                for i in range(0, len(audio), chunk_size):
                    yield audio[i: i + chunk_size]
                    await asyncio.sleep(0.01)

            except Exception as fallback_error:
                logger.error(
                    f"❌ ElevenLabs fallback also failed: {fallback_error}")

    async def health_check(self) -> dict:
        """Check ElevenLabs provider health"""
        try:
            if not self.is_available():
                return {
                    "status": "unavailable",
                    "provider": self.provider_name,
                    "error": "Not initialized",
                }

            # Simple test synthesis
            test_audio = generate(
                text="Test", voice="josh", voice_settings=None  # Default voice
            )

            return {
                "status": "healthy",
                "provider": self.provider_name,
                "test_audio_size": len(test_audio) if test_audio else 0,
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "provider": self.provider_name,
                "error": str(e),
            }
