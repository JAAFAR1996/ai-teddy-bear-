#!/usr/bin/env python3
"""
🤖 OpenAI Synthesis Provider
موفر خدمة تركيب الصوت من OpenAI
"""

import asyncio
import logging
from typing import AsyncIterator, Optional

from openai import AsyncOpenAI

from .base_provider import BaseSynthesisProvider
from ..models import SynthesisContext

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseSynthesisProvider):
    """OpenAI synthesis provider implementation"""
    
    def __init__(self):
        """Initialize OpenAI provider"""
        super().__init__("OpenAI")
        self.client: Optional[AsyncOpenAI] = None
        
    async def initialize(self, credentials: dict) -> bool:
        """Initialize OpenAI client with API key"""
        try:
            api_key = credentials.get("openai_api_key")
            if not api_key:
                logger.warning("OpenAI API key not provided")
                return False
            
            self.client = AsyncOpenAI(api_key=api_key)
            self.is_initialized = True
            
            logger.info("✅ OpenAI provider initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize OpenAI provider: {e}")
            return False
    
    async def synthesize_audio(self, context: SynthesisContext) -> Optional[bytes]:
        """Synthesize complete audio using OpenAI"""
        if not self.is_available():
            logger.error("OpenAI provider not initialized")
            return None
        
        try:
            response = await self.client.audio.speech.create(
                model="tts-1-hd",  # Higher quality for non-streaming
                voice=context.character.voice_id,
                input=context.text
            )
            
            audio_data = response.content
            logger.debug(f"OpenAI synthesis completed: {len(audio_data)} bytes")
            return audio_data
            
        except Exception as e:
            logger.error(f"❌ OpenAI synthesis failed: {e}")
            return None
    
    async def synthesize_stream(self, context: SynthesisContext) -> AsyncIterator[bytes]:
        """Synthesize streaming audio using OpenAI"""
        if not self.is_available():
            logger.error("OpenAI provider not initialized")
            return
        
        try:
            response = await self.client.audio.speech.create(
                model="tts-1",
                voice=context.character.voice_id,
                input=context.text,
                response_format="opus"  # Better for streaming
            )
            
            # Stream the response
            async for chunk in response.iter_bytes():
                yield chunk
                
        except Exception as e:
            logger.error(f"❌ OpenAI streaming synthesis failed: {e}")
            
            # Fallback to complete synthesis
            try:
                response = await self.client.audio.speech.create(
                    model="tts-1",
                    voice=context.character.voice_id,
                    input=context.text
                )
                audio_data = response.content
                
                # Chunk for streaming
                chunk_size = 1024
                for i in range(0, len(audio_data), chunk_size):
                    yield audio_data[i:i + chunk_size]
                    await asyncio.sleep(0.01)
                    
            except Exception as fallback_error:
                logger.error(f"❌ OpenAI fallback also failed: {fallback_error}")
    
    async def health_check(self) -> dict:
        """Check OpenAI provider health"""
        try:
            if not self.is_available():
                return {
                    "status": "unavailable",
                    "provider": self.provider_name,
                    "error": "Not initialized"
                }
            
            # Simple test synthesis
            response = await self.client.audio.speech.create(
                model="tts-1",
                voice="alloy",  # Default voice
                input="Test"
            )
            
            return {
                "status": "healthy",
                "provider": self.provider_name,
                "test_audio_size": len(response.content)
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "provider": self.provider_name,
                "error": str(e)
            } 