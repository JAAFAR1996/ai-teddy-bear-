"""
🗣️ Text-to-Speech Service
High cohesion component for text-to-speech conversion with multiple providers
"""

import asyncio
import io
import logging
from typing import Optional, Dict, Any

from .models import TextToSpeechRequest, ProcessingResult, TTSProvider, AudioFormat


class TTSProviderManager:
    """
    Manages availability and selection of TTS providers.
    Extracted from main TTS service to eliminate bumpy road pattern.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._provider_availability = {}
        self._check_provider_availability()
    
    def _check_provider_availability(self):
        """Check which TTS providers are available"""
        # Check ElevenLabs
        try:
            from elevenlabs import generate
            self._provider_availability[TTSProvider.ELEVENLABS] = True
        except ImportError:
            self._provider_availability[TTSProvider.ELEVENLABS] = False
        
        # Check gTTS
        try:
            from gtts import gTTS
            self._provider_availability[TTSProvider.GTTS] = True
        except ImportError:
            self._provider_availability[TTSProvider.GTTS] = False
        
        # Check Azure
        try:
            import azure.cognitiveservices.speech as speechsdk
            self._provider_availability[TTSProvider.AZURE] = True
        except ImportError:
            self._provider_availability[TTSProvider.AZURE] = False
    
    def is_provider_available(self, provider: TTSProvider) -> bool:
        """Check if a specific provider is available"""
        return self._provider_availability.get(provider, False)
    
    def get_available_providers(self) -> list:
        """Get list of available providers"""
        return [provider for provider, available in self._provider_availability.items() if available]
    
    def get_fallback_provider(self, preferred: TTSProvider) -> Optional[TTSProvider]:
        """Get fallback provider if preferred is not available"""
        available = self.get_available_providers()
        
        if not available:
            return None
        
        # If preferred is available, return it
        if preferred in available:
            return preferred
        
        # Otherwise return first available
        return available[0]


class ElevenLabsTTSProcessor:
    """
    ElevenLabs TTS processing logic.
    Extracted from main service to eliminate bumpy road complexity.
    """
    
    def __init__(self, api_key: str, default_voice: str = "Rachel"):
        self.api_key = api_key
        self.default_voice = default_voice
        self.logger = logging.getLogger(__name__)
    
    async def synthesize(self, request: TextToSpeechRequest) -> ProcessingResult:
        """Synthesize speech using ElevenLabs"""
        try:
            from elevenlabs import generate
            
            voice = request.voice or self.default_voice
            
            audio_bytes = await asyncio.to_thread(
                generate,
                text=request.text,
                voice=voice,
                model="eleven_multilingual_v2",
                api_key=self.api_key
            )
            
            self.logger.debug(f"ElevenLabs synthesis successful: {len(audio_bytes)} bytes")
            
            return ProcessingResult.success_result(
                data=audio_bytes,
                metadata={
                    "provider": "elevenlabs",
                    "voice": voice,
                    "format": "mp3",
                    "size": len(audio_bytes)
                }
            )
            
        except Exception as e:
            self.logger.error(f"ElevenLabs synthesis failed: {e}")
            return ProcessingResult.error_result(f"ElevenLabs error: {str(e)}")


class GTTSProcessor:
    """
    Google Text-to-Speech processing logic.
    Extracted from main service to eliminate bumpy road complexity.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def synthesize(self, request: TextToSpeechRequest) -> ProcessingResult:
        """Synthesize speech using gTTS"""
        try:
            from gtts import gTTS
            
            # Use language from request
            lang = request.language if request.language in ['ar', 'en', 'es', 'fr'] else 'ar'
            
            tts = gTTS(text=request.text, lang=lang)
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            audio_bytes = audio_buffer.read()
            
            self.logger.debug(f"gTTS synthesis successful: {len(audio_bytes)} bytes")
            
            return ProcessingResult.success_result(
                data=audio_bytes,
                metadata={
                    "provider": "gtts",
                    "language": lang,
                    "format": "mp3",
                    "size": len(audio_bytes)
                }
            )
            
        except Exception as e:
            self.logger.error(f"gTTS synthesis failed: {e}")
            return ProcessingResult.error_result(f"gTTS error: {str(e)}")


class AzureTTSProcessor:
    """
    Azure Text-to-Speech processing logic.
    Extracted from main service to eliminate bumpy road complexity.
    """
    
    def __init__(self, api_key: str, region: str):
        self.api_key = api_key
        self.region = region
        self.logger = logging.getLogger(__name__)
    
    async def synthesize(self, request: TextToSpeechRequest) -> ProcessingResult:
        """Synthesize speech using Azure TTS"""
        try:
            import azure.cognitiveservices.speech as speechsdk
            
            # Configure speech service
            speech_config = speechsdk.SpeechConfig(
                subscription=self.api_key,
                region=self.region
            )
            
            # Set voice based on language
            voice_map = {
                'ar': 'ar-SA-ZariyahNeural',
                'en': 'en-US-JennyNeural',
                'es': 'es-ES-ElviraNeural',
                'fr': 'fr-FR-DeniseNeural'
            }
            
            speech_config.speech_synthesis_voice_name = voice_map.get(
                request.language, voice_map['ar']
            )
            
            # Create synthesizer
            synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
            
            # Synthesize
            result = await asyncio.to_thread(
                synthesizer.speak_text_async(request.text).get
            )
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                audio_bytes = result.audio_data
                
                self.logger.debug(f"Azure synthesis successful: {len(audio_bytes)} bytes")
                
                return ProcessingResult.success_result(
                    data=audio_bytes,
                    metadata={
                        "provider": "azure",
                        "voice": speech_config.speech_synthesis_voice_name,
                        "format": "wav",
                        "size": len(audio_bytes)
                    }
                )
            else:
                return ProcessingResult.error_result(f"Azure synthesis failed: {result.reason}")
                
        except Exception as e:
            self.logger.error(f"Azure synthesis failed: {e}")
            return ProcessingResult.error_result(f"Azure error: {str(e)}")


class TextToSpeechService:
    """
    Dedicated service for text-to-speech conversion.
    High cohesion: all methods work with TTS conversion and provider management.
    
    ✅ Solved Bumpy Road problem by extracting provider logic into separate classes
    ✅ Each processor handles one provider (Single Responsibility)
    ✅ Main service coordinates between providers (high-level orchestration)
    """
    
    def __init__(self, elevenlabs_api_key: str = None, azure_api_key: str = None, azure_region: str = None):
        """Initialize TTS service with provider configurations"""
        self.logger = logging.getLogger(__name__)
        
        # Provider management
        self.provider_manager = TTSProviderManager()
        
        # Initialize processors
        self.processors = {}
        
        if elevenlabs_api_key and self.provider_manager.is_provider_available(TTSProvider.ELEVENLABS):
            self.processors[TTSProvider.ELEVENLABS] = ElevenLabsTTSProcessor(elevenlabs_api_key)
        
        if self.provider_manager.is_provider_available(TTSProvider.GTTS):
            self.processors[TTSProvider.GTTS] = GTTSProcessor()
        
        if azure_api_key and azure_region and self.provider_manager.is_provider_available(TTSProvider.AZURE):
            self.processors[TTSProvider.AZURE] = AzureTTSProcessor(azure_api_key, azure_region)
        
        # Statistics
        self.synthesis_count = 0
        self.successful_synthesis = 0
        self.provider_usage = {provider: 0 for provider in TTSProvider}
        
        self.logger.info(f"TTS Service initialized with {len(self.processors)} providers")
    
    async def synthesize_speech(self, request: TextToSpeechRequest) -> ProcessingResult:
        """
        Synthesize speech from text using best available provider.
        EXTRACT FUNCTION applied - no more bumpy road pattern.
        """
        try:
            self.synthesis_count += 1
            
            # Validate request
            if not self._validate_request(request):
                return ProcessingResult.error_result("Invalid TTS request")
            
            # Get appropriate provider
            provider = self._select_provider(request.provider)
            if not provider:
                return ProcessingResult.error_result("No TTS providers available")
            
            # Perform synthesis
            result = await self._perform_synthesis(provider, request)
            
            # Update statistics
            self._update_statistics(provider, result.success)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in speech synthesis: {e}")
            return ProcessingResult.error_result(f"TTS service error: {str(e)}")
    
    def _validate_request(self, request: TextToSpeechRequest) -> bool:
        """Validate TTS request"""
        if not request.text or not request.text.strip():
            self.logger.error("Empty text provided for synthesis")
            return False
        
        if len(request.text) > 5000:
            self.logger.error("Text too long for synthesis")
            return False
        
        return True
    
    def _select_provider(self, preferred: TTSProvider) -> Optional[TTSProvider]:
        """Select appropriate TTS provider"""
        # Check if preferred provider is available
        if preferred in self.processors:
            return preferred
        
        # Get fallback provider
        fallback = self.provider_manager.get_fallback_provider(preferred)
        if fallback and fallback in self.processors:
            self.logger.info(f"Using fallback provider: {fallback}")
            return fallback
        
        self.logger.error("No TTS providers available")
        return None
    
    async def _perform_synthesis(self, provider: TTSProvider, request: TextToSpeechRequest) -> ProcessingResult:
        """Perform synthesis using selected provider"""
        processor = self.processors[provider]
        
        self.logger.debug(f"Synthesizing with provider: {provider}")
        result = await processor.synthesize(request)
        
        if result.success:
            self.logger.info(f"Synthesis successful with {provider}")
        else:
            self.logger.warning(f"Synthesis failed with {provider}: {result.error_message}")
        
        return result
    
    def _update_statistics(self, provider: TTSProvider, success: bool):
        """Update synthesis statistics"""
        self.provider_usage[provider] += 1
        
        if success:
            self.successful_synthesis += 1
    
    async def synthesize_with_fallback(self, request: TextToSpeechRequest) -> ProcessingResult:
        """
        Synthesize speech with automatic fallback to other providers.
        Tries providers in order of preference until one succeeds.
        """
        available_providers = [p for p in TTSProvider if p in self.processors]
        
        if not available_providers:
            return ProcessingResult.error_result("No TTS providers available")
        
        # Try preferred provider first
        if request.provider in available_providers:
            available_providers.remove(request.provider)
            available_providers.insert(0, request.provider)
        
        last_error = None
        
        for provider in available_providers:
            try:
                # Update request to use current provider
                provider_request = TextToSpeechRequest(
                    text=request.text,
                    voice=request.voice,
                    provider=provider,
                    format=request.format,
                    language=request.language
                )
                
                result = await self._perform_synthesis(provider, provider_request)
                
                if result.success:
                    self._update_statistics(provider, True)
                    return result
                else:
                    last_error = result.error_message
                    
            except Exception as e:
                last_error = str(e)
                self.logger.warning(f"Provider {provider} failed: {e}")
                continue
        
        return ProcessingResult.error_result(f"All TTS providers failed. Last error: {last_error}")
    
    def get_provider_stats(self) -> Dict[str, Any]:
        """Get TTS provider statistics"""
        success_rate = (
            self.successful_synthesis / self.synthesis_count 
            if self.synthesis_count > 0 else 0
        )
        
        return {
            "service_name": "TextToSpeechService",
            "total_synthesis": self.synthesis_count,
            "successful_synthesis": self.successful_synthesis,
            "success_rate": success_rate,
            "available_providers": list(self.processors.keys()),
            "provider_usage": dict(self.provider_usage),
            "high_cohesion": True,
            "responsibility": "Text-to-speech conversion with multiple providers"
        }
    
    def get_available_voices(self, provider: TTSProvider) -> list:
        """Get available voices for a specific provider"""
        if provider == TTSProvider.ELEVENLABS and provider in self.processors:
            # Would return actual voices from ElevenLabs API
            return ["Rachel", "Domi", "Bella", "Antoni", "Elli", "Josh"]
        elif provider == TTSProvider.GTTS:
            return ["Standard"]
        elif provider == TTSProvider.AZURE and provider in self.processors:
            return ["ar-SA-ZariyahNeural", "en-US-JennyNeural", "es-ES-ElviraNeural"]
        else:
            return []
    
    async def test_provider(self, provider: TTSProvider) -> ProcessingResult:
        """Test a specific TTS provider"""
        if provider not in self.processors:
            return ProcessingResult.error_result(f"Provider {provider} not available")
        
        test_request = TextToSpeechRequest(
            text="This is a test message",
            provider=provider,
            language="en"
        )
        
        return await self._perform_synthesis(provider, test_request) 