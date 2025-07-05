#!/usr/bin/env python3
"""
🔄 Fallback Synthesis Provider
موفر خدمة تركيب الصوت الاحتياطي
"""

import asyncio
import logging
from typing import AsyncIterator, Optional

import numpy as np

from .base_provider import BaseSynthesisProvider
from ..models import SynthesisContext

logger = logging.getLogger(__name__)


class FallbackProvider(BaseSynthesisProvider):
    """Fallback synthesis provider using system TTS or generated audio"""
    
    def __init__(self):
        """Initialize Fallback provider"""
        super().__init__("Fallback")
        self.sample_rate = 24000
        
    async def initialize(self, credentials: dict) -> bool:
        """Initialize fallback provider (always succeeds)"""
        try:
            self.is_initialized = True
            logger.info("✅ Fallback provider initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Fallback provider: {e}")
            return False
    
    async def synthesize_audio(self, context: SynthesisContext) -> Optional[bytes]:
        """Synthesize audio using fallback method"""
        try:
            logger.warning("Using fallback synthesis - limited functionality")
            
            # Generate simple tone or silence as placeholder
            duration = self._estimate_duration(context.text)
            audio_data = self._generate_placeholder_audio(duration)
            
            logger.debug(f"Fallback synthesis completed: {len(audio_data)} bytes")
            return audio_data
            
        except Exception as e:
            logger.error(f"❌ Fallback synthesis failed: {e}")
            return None
    
    async def synthesize_stream(self, context: SynthesisContext) -> AsyncIterator[bytes]:
        """Synthesize streaming audio using fallback method"""
        try:
            audio_data = await self.synthesize_audio(context)
            if audio_data:
                chunk_size = 1024
                for i in range(0, len(audio_data), chunk_size):
                    yield audio_data[i:i + chunk_size]
                    await asyncio.sleep(0.01)  # Small delay for streaming effect
                    
        except Exception as e:
            logger.error(f"❌ Fallback streaming synthesis failed: {e}")
    
    def _estimate_duration(self, text: str) -> float:
        """Estimate audio duration based on text length"""
        # Approximate duration: ~150 words per minute
        words = len(text.split())
        duration = max(0.5, words / 2.5)  # Minimum 0.5 seconds
        return duration
    
    def _generate_placeholder_audio(self, duration: float) -> bytes:
        """Generate placeholder audio (silence or simple tone)"""
        try:
            samples = int(duration * self.sample_rate)
            
            # Generate soft tone as audio placeholder
            frequency = 440  # A4 note
            time_array = np.linspace(0, duration, samples)
            
            # Create a soft sine wave
            audio = np.sin(2 * np.pi * frequency * time_array) * 0.1
            
            # Add fade in/out to avoid clicks
            fade_samples = min(samples // 10, 1000)
            if fade_samples > 0:
                # Fade in
                audio[:fade_samples] *= np.linspace(0, 1, fade_samples)
                # Fade out
                audio[-fade_samples:] *= np.linspace(1, 0, fade_samples)
            
            # Convert to 16-bit PCM
            audio_int16 = (audio * 32767).astype(np.int16)
            return audio_int16.tobytes()
            
        except Exception as e:
            logger.error(f"Failed to generate placeholder audio: {e}")
            # Return silence as ultimate fallback
            samples = int(duration * self.sample_rate)
            silence = np.zeros(samples, dtype=np.int16)
            return silence.tobytes()
    
    def _generate_silence(self, duration: float) -> bytes:
        """Generate silent audio of specified duration"""
        try:
            samples = int(duration * self.sample_rate)
            silence = np.zeros(samples, dtype=np.int16)
            return silence.tobytes()
            
        except Exception as e:
            logger.error(f"Failed to generate silence: {e}")
            return b""
    
    async def health_check(self) -> dict:
        """Check fallback provider health (should always be healthy)"""
        try:
            # Test audio generation
            test_audio = self._generate_placeholder_audio(0.1)  # 100ms test
            
            return {
                "status": "healthy",
                "provider": self.provider_name,
                "test_audio_size": len(test_audio),
                "note": "Fallback provider using generated audio"
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "provider": self.provider_name,
                "error": str(e)
            } 