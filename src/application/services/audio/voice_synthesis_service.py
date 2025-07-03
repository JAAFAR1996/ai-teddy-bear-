"""
Voice Synthesis Service
Handles text-to-speech synthesis operations using multiple providers
"""

import asyncio
import logging
from typing import Optional, Dict, Any
import tempfile
import os

from .voice_provider_base import BaseProviderService
from .voice_provider_manager import ProviderManager
from .voice_cache_manager import VoiceCacheManager
from .voice_audio_processor import VoiceAudioProcessor
from src.domain.audio.models import (
    SynthesisRequest, ProviderConfig, 
    ProviderOperation, ProviderType
)

logger = logging.getLogger(__name__)


class SynthesisExecutor:
    """Executes synthesis with specific providers"""
    
    def __init__(self, provider_manager: ProviderManager):
        self.provider_manager = provider_manager
        self.resources = provider_manager.get_resources()
    
    async def execute(
        self, provider: ProviderConfig, request: SynthesisRequest
    ) -> Optional[str]:
        """Execute synthesis with specified provider"""
        try:
            if provider.provider_type == ProviderType.ELEVENLABS:
                return await self._synthesize_elevenlabs(request)
            elif provider.provider_type == ProviderType.AZURE:
                return await self._synthesize_azure(request)
            elif provider.provider_type == ProviderType.GTTS:
                return await self._synthesize_gtts(request)
            else:
                logger.warning(f"Unknown synthesis provider: {provider.provider_type}")
                return None
        except Exception as e:
            logger.error(f"Synthesis failed with {provider.name}: {str(e)}")
            return None
    
    async def _synthesize_elevenlabs(self, request: SynthesisRequest) -> Optional[str]:
        """Synthesize using ElevenLabs"""
        if not self.resources.elevenlabs_client:
            return None
        
        try:
            # Configure voice settings based on emotion
            voice_settings = self._get_elevenlabs_voice_settings(request.emotion)
            
            # Generate speech
            audio_generator = await self.resources.elevenlabs_client.generate(
                text=request.text,
                voice="Rachel",  # Default voice, could be configurable
                model="eleven_multilingual_v2",
                voice_settings=voice_settings
            )
            
            # Collect audio chunks
            audio_chunks = []
            async for chunk in audio_generator:
                if chunk:
                    audio_chunks.append(chunk)
            
            if audio_chunks:
                # Combine chunks and encode to base64
                audio_data = b''.join(audio_chunks)
                return await VoiceAudioProcessor.encode_audio_base64(audio_data)
            
            return None
            
        except Exception as e:
            logger.error(f"ElevenLabs synthesis error: {str(e)}")
            return None
    
    async def _synthesize_azure(self, request: SynthesisRequest) -> Optional[str]:
        """Synthesize using Azure Speech"""
        if not self.resources.azure_speech_config:
            return None
        
        try:
            import azure.cognitiveservices.speech as speechsdk
            
            # Configure language and voice
            voice_map = {
                "Arabic": "ar-SA-ZariyahNeural",
                "English": "en-US-JennyNeural"
            }
            
            voice_name = voice_map.get(request.language, "ar-SA-ZariyahNeural")
            self.resources.azure_speech_config.speech_synthesis_voice_name = voice_name
            
            # Create synthesizer
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.resources.azure_speech_config
            )
            
            # Build SSML with emotion
            ssml_text = self._build_azure_ssml(
                request.text, voice_name, request.emotion
            )
            
            # Perform synthesis
            result = await asyncio.get_event_loop().run_in_executor(
                None, synthesizer.speak_ssml_async(ssml_text).get
            )
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                # Convert audio data to base64
                return await VoiceAudioProcessor.encode_audio_base64(result.audio_data)
            else:
                logger.warning(f"Azure synthesis failed: {result.reason}")
                return None
                
        except Exception as e:
            logger.error(f"Azure synthesis error: {str(e)}")
            return None
    
    async def _synthesize_gtts(self, request: SynthesisRequest) -> Optional[str]:
        """Synthesize using Google TTS (gTTS)"""
        try:
            from gtts import gTTS
            
            # Configure language
            lang_map = {
                "Arabic": "ar",
                "English": "en"
            }
            
            lang = lang_map.get(request.language, "ar")
            
            # Create gTTS object
            tts = gTTS(text=request.text, lang=lang, slow=False)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                temp_path = temp_file.name
            
            # Generate audio
            await asyncio.get_event_loop().run_in_executor(
                None, tts.save, temp_path
            )
            
            # Read and encode audio
            audio_data = await VoiceAudioProcessor.read_temp_file(temp_path)
            encoded_audio = await VoiceAudioProcessor.encode_audio_base64(audio_data)
            
            # Cleanup
            await VoiceAudioProcessor.cleanup_files([temp_path])
            
            return encoded_audio
            
        except Exception as e:
            logger.error(f"gTTS synthesis error: {str(e)}")
            return None
    
    def _get_elevenlabs_voice_settings(self, emotion: str) -> Dict[str, Any]:
        """Get ElevenLabs voice settings based on emotion"""
        settings_map = {
            "happy": {"stability": 0.75, "similarity_boost": 0.75, "style": 0.2},
            "sad": {"stability": 0.85, "similarity_boost": 0.65, "style": 0.1},
            "excited": {"stability": 0.65, "similarity_boost": 0.8, "style": 0.3},
            "calm": {"stability": 0.9, "similarity_boost": 0.7, "style": 0.0},
            "neutral": {"stability": 0.8, "similarity_boost": 0.75, "style": 0.1}
        }
        
        return settings_map.get(emotion, settings_map["neutral"])
    
    def _build_azure_ssml(self, text: str, voice_name: str, emotion: str) -> str:
        """Build SSML for Azure Speech with emotion"""
        emotion_styles = {
            "happy": "cheerful",
            "sad": "sad",
            "excited": "excited",
            "calm": "calm",
            "neutral": "neutral"
        }
        
        style = emotion_styles.get(emotion, "neutral")
        
        return f"""
        <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="ar-SA">
            <voice name="{voice_name}">
                <mstts:express-as style="{style}">
                    {text}
                </mstts:express-as>
            </voice>
        </speak>
        """


class SynthesisService(BaseProviderService[SynthesisRequest]):
    """Service for handling text-to-speech synthesis requests"""
    
    def __init__(
        self, 
        provider_manager: ProviderManager, 
        cache_manager: VoiceCacheManager
    ):
        super().__init__(
            operation_type=ProviderOperation.SYNTHESIS,
            cache_manager=cache_manager,
            metric_name="synthesis_duration"
        )
        self.provider_manager = provider_manager
        self.executor = SynthesisExecutor(provider_manager)
        
        # Set providers for synthesis
        all_providers = provider_manager.get_all_providers()
        self.set_providers(all_providers)
    
    async def synthesize(
        self, 
        text: str, 
        emotion: str = "neutral", 
        language: str = "Arabic"
    ) -> str:
        """Synthesize text to speech"""
        # Generate cache key
        cache_key = self.cache_manager.generate_synthesis_key(text, emotion, language)
        
        # Create request
        request = SynthesisRequest(
            text=text,
            emotion=emotion,
            language=language,
            cache_key=cache_key
        )
        
        # Process with provider chain
        result = await self.process_with_providers(request, self.executor)
        
        # Return result or empty base64 audio
        return result or ""
    
    async def process(
        self, 
        text: str, 
        emotion: str = "neutral", 
        language: str = "Arabic"
    ) -> str:
        """Process synthesis request"""
        return await self.synthesize(text, emotion, language)
