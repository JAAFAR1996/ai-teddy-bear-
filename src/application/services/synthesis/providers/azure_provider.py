#!/usr/bin/env python3
"""
☁️ Azure Speech Synthesis Provider
موفر خدمة تركيب الصوت من Azure
"""

import asyncio
import logging
from typing import AsyncIterator, Optional

try:
    import azure.cognitiveservices.speech as speechsdk
except ImportError:
    speechsdk = None

from .base_provider import BaseSynthesisProvider
from ..models import SynthesisContext
from src.domain.value_objects import EmotionalTone

logger = logging.getLogger(__name__)


class AzureProvider(BaseSynthesisProvider):
    """Azure Speech synthesis provider implementation"""
    
    def __init__(self):
        """Initialize Azure provider"""
        super().__init__("Azure")
        self.speech_config: Optional[speechsdk.SpeechConfig] = None
        
    async def initialize(self, credentials: dict) -> bool:
        """Initialize Azure Speech client"""
        try:
            if speechsdk is None:
                logger.error("Azure Speech SDK not available")
                return False
            
            speech_key = credentials.get("azure_speech_key")
            speech_region = credentials.get("azure_speech_region", "eastus")
            
            if not speech_key:
                logger.warning("Azure Speech key not provided")
                return False
            
            self.speech_config = speechsdk.SpeechConfig(
                subscription=speech_key,
                region=speech_region
            )
            self.is_initialized = True
            
            logger.info("✅ Azure provider initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Azure provider: {e}")
            return False
    
    async def synthesize_audio(self, context: SynthesisContext) -> Optional[bytes]:
        """Synthesize complete audio using Azure Speech"""
        if not self.is_available():
            logger.error("Azure provider not initialized")
            return None
        
        try:
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.speech_config
            )
            
            ssml = self._build_azure_ssml(context)
            result = await asyncio.to_thread(synthesizer.speak_ssml, ssml)
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                logger.debug(f"Azure synthesis completed: {len(result.audio_data)} bytes")
                return result.audio_data
            else:
                logger.error(f"Azure synthesis failed: {result.reason}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Azure synthesis failed: {e}")
            return None
    
    async def synthesize_stream(self, context: SynthesisContext) -> AsyncIterator[bytes]:
        """Synthesize streaming audio using Azure Speech"""
        if not self.is_available():
            logger.error("Azure provider not initialized")
            return
        
        try:
            # Azure doesn't have true streaming, so we'll chunk the result
            audio_data = await self.synthesize_audio(context)
            if audio_data:
                chunk_size = 1024
                for i in range(0, len(audio_data), chunk_size):
                    yield audio_data[i:i + chunk_size]
                    await asyncio.sleep(0.01)
                    
        except Exception as e:
            logger.error(f"❌ Azure streaming synthesis failed: {e}")
    
    def _build_azure_ssml(self, context: SynthesisContext) -> str:
        """Build SSML for Azure Speech with emotion"""
        # Map emotions to Azure styles
        azure_emotions = {
            EmotionalTone.HAPPY: "cheerful",
            EmotionalTone.EXCITED: "excited",
            EmotionalTone.CALM: "calm",
            EmotionalTone.FRIENDLY: "friendly",
            EmotionalTone.LOVE: "affectionate",
            EmotionalTone.ENCOURAGING: "encouraging"
        }
        
        style = azure_emotions.get(context.emotion, "friendly")
        
        # Adjust speech rate based on character
        rate = f"{int((context.character.speed_adjustment - 1) * 100):+d}%"
        
        # Adjust pitch
        pitch = f"{context.character.pitch_adjustment:+.1f}st"
        
        ssml = f'''
        <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" 
               xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="{context.character.language}">
            <voice name="{context.character.voice_id}">
                <mstts:express-as style="{style}">
                    <prosody rate="{rate}" pitch="{pitch}">
                        {context.text}
                    </prosody>
                </mstts:express-as>
            </voice>
        </speak>
        '''
        
        return ssml.strip()
    
    async def health_check(self) -> dict:
        """Check Azure provider health"""
        try:
            if not self.is_available():
                return {
                    "status": "unavailable",
                    "provider": self.provider_name,
                    "error": "Not initialized"
                }
            
            # Simple test synthesis
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.speech_config
            )
            
            result = await asyncio.to_thread(synthesizer.speak_text, "Test")
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                return {
                    "status": "healthy",
                    "provider": self.provider_name,
                    "test_audio_size": len(result.audio_data)
                }
            else:
                return {
                    "status": "unhealthy",
                    "provider": self.provider_name,
                    "error": f"Synthesis failed: {result.reason}"
                }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "provider": self.provider_name,
                "error": str(e)
            } 