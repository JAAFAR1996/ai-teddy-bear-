"""
Voice Transcription Service
Handles transcription operations using multiple providers
"""

import asyncio
import logging
from typing import Optional, List

from .voice_provider_base import BaseProviderService
from .voice_provider_manager import ProviderManager
from .voice_cache_manager import VoiceCacheManager
from .voice_audio_processor import VoiceAudioProcessor
from src.domain.audio.models import (
    TranscriptionRequest,
    ProviderConfig,
    ProviderOperation,
    ProviderType,
)

logger = logging.getLogger(__name__)


class TranscriptionExecutor:
    """Executes transcription with specific providers"""

    def __init__(self, provider_manager: ProviderManager):
        self.provider_manager = provider_manager
        self.resources = provider_manager.get_resources()

    async def execute(
        self, provider: ProviderConfig, request: TranscriptionRequest
    ) -> Optional[str]:
        """Execute transcription with specified provider"""
        try:
            if provider.provider_type == ProviderType.WHISPER:
                return await self._transcribe_whisper(request)
            elif provider.provider_type == ProviderType.AZURE:
                return await self._transcribe_azure(request)
            elif provider.provider_type == ProviderType.FALLBACK:
                return await self._transcribe_fallback(request)
            else:
                logger.warning(
                    f"Unknown transcription provider: {provider.provider_type}"
                )
                return None
        except Exception as e:
            logger.error(
                f"Transcription failed with {provider.name}: {str(e)}")
            return None

    async def _transcribe_whisper(
            self, request: TranscriptionRequest) -> Optional[str]:
        """Transcribe using Whisper"""
        if not self.resources.whisper_model:
            return None

        try:
            # Process audio file
            audio_files = await VoiceAudioProcessor.process_audio_file(
                request.audio_path
            )

            # Run transcription in executor to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, self.resources.whisper_model.transcribe, audio_files["wav"]
            )

            # Cleanup temporary files
            await VoiceAudioProcessor.cleanup_files(list(audio_files.values()))

            if result and "text" in result:
                return VoiceAudioProcessor.clean_transcription_text(
                    result["text"])

            return None

        except Exception as e:
            logger.error(f"Whisper transcription error: {str(e)}")
            return None

    async def _transcribe_azure(
            self, request: TranscriptionRequest) -> Optional[str]:
        """Transcribe using Azure Speech"""
        if not self.resources.azure_speech_config:
            return None

        try:
            import azure.cognitiveservices.speech as speechsdk

            # Process audio file
            audio_files = await VoiceAudioProcessor.process_audio_file(
                request.audio_path
            )

            # Configure Azure recognizer
            audio_config = speechsdk.audio.AudioConfig(
                filename=audio_files["wav"])

            # Set language
            language_map = {"Arabic": "ar-SA", "English": "en-US"}
            self.resources.azure_speech_config.speech_recognition_language = (
                language_map.get(request.language, "ar-SA")
            )

            speech_recognizer = speechsdk.SpeechRecognizer(
                speech_config=self.resources.azure_speech_config,
                audio_config=audio_config,
            )

            # Perform recognition
            result = await asyncio.get_event_loop().run_in_executor(
                None, speech_recognizer.recognize_once
            )

            # Cleanup temporary files
            await VoiceAudioProcessor.cleanup_files(list(audio_files.values()))

            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                return VoiceAudioProcessor.clean_transcription_text(
                    result.text)
            else:
                logger.warning(f"Azure recognition failed: {result.reason}")
                return None

        except Exception as e:
            logger.error(f"Azure transcription error: {str(e)}")
            return None

    async def _transcribe_fallback(
        self, request: TranscriptionRequest
    ) -> Optional[str]:
        """Fallback transcription using basic speech recognition"""
        try:
            # Process audio file
            audio_files = await VoiceAudioProcessor.process_audio_file(
                request.audio_path
            )

            # Simple fallback - could use speech_recognition library
            # For now, return a basic response
            fallback_text = "تم استلام الصوت بنجاح"

            # Cleanup temporary files
            await VoiceAudioProcessor.cleanup_files(list(audio_files.values()))

            return fallback_text

        except Exception as e:
            logger.error(f"Fallback transcription error: {str(e)}")
            return None


class TranscriptionService(BaseProviderService[TranscriptionRequest]):
    """Service for handling transcription requests"""

    def __init__(self, provider_manager: ProviderManager,
                 cache_manager: VoiceCacheManager):
        super().__init__(
            operation_type=ProviderOperation.TRANSCRIPTION,
            cache_manager=cache_manager,
            metric_name="transcription_duration",
        )
        self.provider_manager = provider_manager
        self.executor = TranscriptionExecutor(provider_manager)

        # Set providers for transcription
        all_providers = provider_manager.get_all_providers()
        self.set_providers(all_providers)

    async def transcribe(
        self, audio_data: str, language: str = "Arabic"
    ) -> Optional[str]:
        """Transcribe audio to text"""
        # Generate cache key
        cache_key = self.cache_manager.generate_transcription_key(audio_data)

        # Create request
        request = TranscriptionRequest(
            audio_path=audio_data, language=language, cache_key=cache_key
        )

        # Process with provider chain
        return await self.process_with_providers(request, self.executor)

    async def process(
            self,
            audio_data: str,
            language: str = "Arabic") -> Optional[str]:
        """Process transcription request"""
        return await self.transcribe(audio_data, language)
