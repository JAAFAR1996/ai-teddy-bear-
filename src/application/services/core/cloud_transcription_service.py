from typing import Any, Dict, List, Optional, Union
from enum import Enum
from pydantic import BaseModel, Field
from dataclasses import dataclass
import base64
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from .openai_transcription_provider import OpenAITranscriptionProvider, TranscriptionProviderBase, TranscriptionResult, TranscriptionConfig
from .google_transcription_provider import GoogleTranscriptionProvider, GOOGLE_AVAILABLE
from .azure_transcription_provider import AzureTranscriptionProvider, AZURE_AVAILABLE

logger = structlog.get_logger()


class TranscriptionProvider(Enum):
    """Available transcription providers"""
    OPENAI = "openai"
    GOOGLE = "google"
    AZURE = "azure"


class CloudTranscriptionService:
    """Multi-provider cloud transcription service with fallback"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.providers = self._initialize_providers()
        self.default_config = TranscriptionConfig(
            provider=TranscriptionProvider.OPENAI)

    def _initialize_providers(self) -> Dict[TranscriptionProvider, TranscriptionProviderBase]:
        """Initialize available providers."""
        providers = {}
        self._try_initialize_openai_provider(providers)
        self._try_initialize_google_provider(providers)
        self._try_initialize_azure_provider(providers)
        if not providers:
            logger.warning("No transcription providers could be initialized!")
        logger.info(f"Initialized providers: {list(providers.keys())}")
        return providers

    def _try_initialize_openai_provider(self, providers: Dict[TranscriptionProvider, TranscriptionProviderBase]):
        if key := self.config.get("OPENAI_API_KEY"):
            try:
                providers[TranscriptionProvider.OPENAI] = OpenAITranscriptionProvider(
                    key)
                logger.info("OpenAI Whisper provider initialized.")
            except Exception as e:
                logger.warning(
                    "Failed to initialize OpenAI provider", error=str(e))

    def _try_initialize_google_provider(self, providers: Dict[TranscriptionProvider, TranscriptionProviderBase]):
        if GOOGLE_AVAILABLE and (creds := self.config.get("GOOGLE_APPLICATION_CREDENTIALS")):
            try:
                providers[TranscriptionProvider.GOOGLE] = GoogleTranscriptionProvider(
                    creds)
                logger.info("Google Speech provider initialized.")
            except Exception as e:
                logger.warning(
                    "Failed to initialize Google provider", error=str(e))

    def _try_initialize_azure_provider(self, providers: Dict[TranscriptionProvider, TranscriptionProviderBase]):
        if AZURE_AVAILABLE and (key := self.config.get("AZURE_SPEECH_KEY")) and (region := self.config.get("AZURE_SPEECH_REGION")):
            try:
                providers[TranscriptionProvider.AZURE] = AzureTranscriptionProvider(
                    key, region)
                logger.info("Azure Speech provider initialized.")
            except Exception as e:
                logger.warning(
                    "Failed to initialize Azure provider", error=str(e))

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def transcribe(
        self, audio_data: Union[bytes, str], language: str = "ar", provider: Optional[TranscriptionProvider] = None, **kwargs
    ) -> TranscriptionResult:
        """Transcribe audio with automatic provider selection and fallback."""
        audio_bytes = self._prepare_audio_data(audio_data)
        config = self._create_transcription_config(
            language, provider, **kwargs)

        primary_provider = provider or config.provider
        if primary_provider in self.providers:
            try:
                return await self.providers[primary_provider].transcribe(audio_bytes, config)
            except Exception as e:
                logger.warning(
                    f"Provider {primary_provider} failed, trying fallbacks.", error=str(e))

        return await self._try_fallback_providers(audio_bytes, config, primary_provider)

    def _prepare_audio_data(self, audio_data: Union[bytes, str]) -> bytes:
        """Prepare audio data for transcription."""
        return base64.b64decode(audio_data) if isinstance(audio_data, str) else audio_data

    def _create_transcription_config(
        self, language: str, provider: Optional[TranscriptionProvider], **kwargs
    ) -> TranscriptionConfig:
        """Create transcription configuration."""
        return TranscriptionConfig(language=language, provider=provider or self.default_config.provider, **kwargs)

    async def _try_fallback_providers(
        self, audio_data: bytes, config: TranscriptionConfig, failed_provider: Optional[TranscriptionProvider]
    ) -> TranscriptionResult:
        """Try all remaining providers as fallback."""
        errors = []
        for prov_type, prov_instance in self.providers.items():
            if prov_type == failed_provider:
                continue
            try:
                config.provider = prov_type
                result = await prov_instance.transcribe(audio_data, config)
                logger.info(
                    f"Transcription successful with fallback: {prov_type}")
                return result
            except Exception as e:
                errors.append(f"{prov_type}: {str(e)}")
        raise Exception(
            f"All transcription providers failed: {'; '.join(errors)}")

    async def get_available_providers(self) -> List[TranscriptionProvider]:
        """Get list of available providers."""
        return [p for p, i in self.providers.items() if await i.is_available()]

    async def health_check(self) -> Dict[str, bool]:
        """Check health of all providers."""
        return {p.value: await i.is_available() for p, i in self.providers.items()}
