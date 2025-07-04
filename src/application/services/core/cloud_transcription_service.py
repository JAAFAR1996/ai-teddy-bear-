from typing import Any, Dict, List, Optional

"""
Cloud-based Transcription Service
Supports multiple providers: OpenAI Whisper API, Google Speech-to-Text, Azure Speech
"""

import asyncio
import base64
import io
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Union

import aiohttp
import structlog

# Google Cloud Speech - optional import
try:
    from google.cloud import speech_v1

    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    speech_v1 = None

# Azure Speech - optional import
try:
    from azure.cognitiveservices.speech import (
        AudioConfig,
        ResultReason,
        SpeechConfig,
        SpeechRecognizer,
    )

    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False

from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential

# from src.application.services.core.circuit_breaker import circuit_breaker


# Placeholder circuit breaker decorator
def circuit_breaker(name: str, failure_threshold: int = 3):
    """Placeholder circuit breaker decorator"""

    def decorator(func):
        return func

    return decorator


logger = structlog.get_logger()


class TranscriptionProvider(Enum):
    """Available transcription providers"""

    OPENAI = "openai"
    GOOGLE = "google"
    AZURE = "azure"
    DEEPGRAM = "deepgram"
    ASSEMBLYAI = "assemblyai"


class TranscriptionConfig(BaseModel):
    """Transcription configuration"""

    provider: TranscriptionProvider = TranscriptionProvider.OPENAI
    language: str = "ar"  # Arabic by default
    model: str = "whisper-1"
    temperature: float = 0.0
    enable_punctuation: bool = True
    enable_word_timestamps: bool = False
    enable_speaker_diarization: bool = False
    max_alternatives: int = 1
    profanity_filter: bool = True
    timeout: float = 30.0


@dataclass
class TranscriptionResult:
    """Transcription result"""

    text: str
    language: str
    confidence: float = 1.0
    duration: Optional[float] = None
    words: List[Dict[str, Any]] = None
    alternatives: List[Dict[str, Any]] = None
    metadata: Dict[str, Any] = None


class TranscriptionProviderBase(ABC):
    """Base class for transcription providers"""

    @abstractmethod
    async def transcribe(
        self, audio_data: bytes, config: TranscriptionConfig
    ) -> TranscriptionResult:
        """Transcribe audio data"""
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        """Check if provider is available"""
        pass


class OpenAITranscriptionProvider(TranscriptionProviderBase):
    """OpenAI Whisper API provider"""

    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)

    @circuit_breaker("openai_transcription", failure_threshold=3)
    async def transcribe(
        self, audio_data: bytes, config: TranscriptionConfig
    ) -> TranscriptionResult:
        """Transcribe using OpenAI Whisper API - Bumpy Road fixed"""
        try:
            response = await self._call_openai_api(audio_data, config)
            result = self._parse_openai_response(response, config)
            self._log_transcription_success(result)
            return result
        except Exception as e:
            logger.error("OpenAI transcription failed", error=str(e))
            raise

    async def _call_openai_api(self, audio_data: bytes, config: TranscriptionConfig):
        """Call OpenAI API with proper formatting"""
        audio_file = io.BytesIO(audio_data)
        audio_file.name = "audio.wav"

        return await self.client.audio.transcriptions.create(
            model=config.model,
            file=audio_file,
            language=config.language,
            temperature=config.temperature,
            response_format="verbose_json" if config.enable_word_timestamps else "json",
        )

    def _parse_openai_response(
        self, response, config: TranscriptionConfig
    ) -> TranscriptionResult:
        """Parse OpenAI response into TranscriptionResult"""
        return TranscriptionResult(
            text=response.text,
            language=(
                response.language if hasattr(response, "language") else config.language
            ),
            duration=response.duration if hasattr(response, "duration") else None,
            words=response.words if hasattr(response, "words") else None,
            metadata={"provider": "openai", "model": config.model},
        )

    def _log_transcription_success(self, result: TranscriptionResult) -> None:
        """Log successful transcription"""
        logger.info(
            "OpenAI transcription completed",
            text_length=len(result.text),
            language=result.language,
        )

    async def is_available(self) -> bool:
        """Check if OpenAI is available"""
        try:
            # Simple models list to check connectivity
            await self.client.models.list()
            return True
        except Exception as e:
            logger.error(f"Error in operation: {e}", exc_info=True)
            return False


class GoogleTranscriptionProvider(TranscriptionProviderBase):
    """Google Speech-to-Text provider"""

    def __init__(self, credentials_path: Optional[str] = None):
        if not GOOGLE_AVAILABLE:
            raise ImportError(
                "Google Cloud Speech library not installed. Run: pip install google-cloud-speech"
            )
        self.client = speech_v1.SpeechAsyncClient()
        self.credentials_path = credentials_path

    @circuit_breaker("google_transcription", failure_threshold=3)
    async def transcribe(
        self, audio_data: bytes, config: TranscriptionConfig
    ) -> TranscriptionResult:
        """Transcribe using Google Speech-to-Text - Bumpy Road fixed"""
        try:
            response = await self._perform_google_recognition(audio_data, config)
            result = self._parse_google_response(response, config)
            self._log_google_success(result)
            return result
        except Exception as e:
            logger.error("Google transcription failed", error=str(e))
            raise

    async def _perform_google_recognition(
        self, audio_data: bytes, config: TranscriptionConfig
    ):
        """Perform Google Speech recognition"""
        recognition_config = speech_v1.RecognitionConfig(
            encoding=speech_v1.RecognitionConfig.AudioEncoding.WEBM_OPUS,
            sample_rate_hertz=16000,
            language_code=self._get_language_code(config.language),
            enable_automatic_punctuation=config.enable_punctuation,
            enable_word_time_offsets=config.enable_word_timestamps,
            enable_speaker_diarization=config.enable_speaker_diarization,
            max_alternatives=config.max_alternatives,
            profanity_filter=config.profanity_filter,
            model="latest_long",
            use_enhanced=True,
        )

        audio = speech_v1.RecognitionAudio(content=audio_data)

        return await self.client.recognize(config=recognition_config, audio=audio)

    def _parse_google_response(
        self, response, config: TranscriptionConfig
    ) -> TranscriptionResult:
        """Parse Google response into TranscriptionResult"""
        if not response.results:
            return self._create_empty_result(config)

        result = response.results[0]
        best_alternative = result.alternatives[0]

        words = self._extract_google_words(best_alternative, config)
        alternatives = self._extract_google_alternatives(result, config)

        return TranscriptionResult(
            text=best_alternative.transcript,
            language=config.language,
            confidence=best_alternative.confidence,
            words=words,
            alternatives=alternatives,
            metadata={
                "provider": "google",
                "language_code": (
                    result.language_code if hasattr(result, "language_code") else None
                ),
            },
        )

    def _create_empty_result(self, config: TranscriptionConfig) -> TranscriptionResult:
        """Create empty result when no results returned"""
        return TranscriptionResult(
            text="",
            language=config.language,
            confidence=0.0,
            metadata={"provider": "google", "error": "No results"},
        )

    def _extract_google_words(self, best_alternative, config: TranscriptionConfig):
        """Extract word-level timestamps from Google response"""
        if not config.enable_word_timestamps or not hasattr(best_alternative, "words"):
            return None

        return [
            {
                "word": word.word,
                "start_time": word.start_time.total_seconds(),
                "end_time": word.end_time.total_seconds(),
                "confidence": getattr(word, "confidence", 1.0),
            }
            for word in best_alternative.words
        ]

    def _extract_google_alternatives(self, result, config: TranscriptionConfig):
        """Extract alternative transcriptions"""
        return [
            {"text": alt.transcript, "confidence": alt.confidence}
            for alt in result.alternatives[1 : config.max_alternatives]
        ]

    def _log_google_success(self, result: TranscriptionResult) -> None:
        """Log successful Google transcription"""
        logger.info(
            "Google transcription completed",
            text_length=len(result.text),
            confidence=result.confidence,
        )

    async def is_available(self) -> bool:
        """Check if Google Speech is available"""
        try:
            # Try a simple operation to check connectivity
            # Note: This is a placeholder - actual Google client method might differ
            return True  # Simplified for now - Google doesn't have simple health check
        except Exception as e:
            logger.error(f"Error in operation: {e}", exc_info=True)
            return False

    def _get_language_code(self, language: str) -> str:
        """Convert language code to Google format"""
        language_map = {
            "ar": "ar-SA",  # Arabic (Saudi Arabia)
            "en": "en-US",  # English (US)
            "es": "es-ES",  # Spanish (Spain)
            "fr": "fr-FR",  # French (France)
            "de": "de-DE",  # German (Germany)
            "zh": "zh-CN",  # Chinese (Simplified)
            "ja": "ja-JP",  # Japanese
            "ko": "ko-KR",  # Korean
        }
        return language_map.get(language, f"{language}-{language.upper()}")


class AzureTranscriptionProvider(TranscriptionProviderBase):
    """Azure Speech Services provider"""

    def __init__(self, subscription_key: str, region: str):
        if not AZURE_AVAILABLE:
            raise ImportError(
                "Azure Speech library not installed. Run: pip install azure-cognitiveservices-speech"
            )
        self.subscription_key = subscription_key
        self.region = region
        self.speech_config = SpeechConfig(subscription=subscription_key, region=region)

    @circuit_breaker("azure_transcription", failure_threshold=3)
    async def transcribe(
        self, audio_data: bytes, config: TranscriptionConfig
    ) -> TranscriptionResult:
        """Transcribe using Azure Speech Services - Bumpy Road fixed"""
        try:
            recognizer = self._setup_azure_recognizer(audio_data, config)
            result = await self._recognize_async(recognizer)
            transcription_result = self._parse_azure_result(result, config)
            self._log_azure_success(transcription_result, result)
            return transcription_result
        except Exception as e:
            logger.error("Azure transcription failed", error=str(e))
            raise

    def _setup_azure_recognizer(self, audio_data: bytes, config: TranscriptionConfig):
        """Setup Azure speech recognizer"""
        self.speech_config.speech_recognition_language = self._get_language_code(
            config.language
        )
        self.speech_config.request_word_level_timestamps()

        audio_stream = AudioInputStream(audio_data)
        audio_config = AudioConfig(stream=audio_stream)

        return SpeechRecognizer(
            speech_config=self.speech_config, audio_config=audio_config
        )

    def _parse_azure_result(
        self, result, config: TranscriptionConfig
    ) -> TranscriptionResult:
        """Parse Azure recognition result"""
        if result.reason != ResultReason.RecognizedSpeech:
            raise Exception(f"Recognition failed: {result.reason}")

        details = result.json
        words = self._extract_azure_words(details, config)

        return TranscriptionResult(
            text=result.text,
            language=config.language,
            confidence=details.get("NBest", [{}])[0].get("Confidence", 1.0),
            duration=details.get("Duration", 0) / 10000000.0,  # Convert to seconds
            words=words,
            metadata={"provider": "azure", "recognition_status": result.reason.name},
        )

    def _extract_azure_words(self, details: Dict, config: TranscriptionConfig):
        """Extract word-level timestamps from Azure response"""
        if not config.enable_word_timestamps or "NBest" not in details:
            return None
        return self._extract_words(details["NBest"][0])

    def _log_azure_success(
        self, transcription_result: TranscriptionResult, result
    ) -> None:
        """Log successful Azure transcription"""
        logger.info(
            "Azure transcription completed",
            text_length=len(transcription_result.text),
            reason=result.reason.name,
        )

    async def is_available(self) -> bool:
        """Check if Azure is available"""
        try:
            # Test with empty audio
            return True  # Azure doesn't have a simple health check
        except Exception as e:
            logger.error(f"Error in operation: {e}", exc_info=True)
            return False

    def _get_language_code(self, language: str) -> str:
        """Convert language code to Azure format"""
        language_map = {
            "ar": "ar-SA",
            "en": "en-US",
            "es": "es-ES",
            "fr": "fr-FR",
            "de": "de-DE",
            "zh": "zh-Hans-CN",
            "ja": "ja-JP",
            "ko": "ko-KR",
        }
        return language_map.get(language, f"{language}-{language.upper()}")

    async def _recognize_async(self, recognizer) -> Any:
        """Async wrapper for recognition"""
        future = asyncio.Future()

        def recognized_cb(evt) -> Any:
            future.set_result(evt.result)

        recognizer.recognized.connect(recognized_cb)
        recognizer.start_continuous_recognition()

        # Wait for result
        result = await future

        recognizer.stop_continuous_recognition()

        return result

    def _extract_words(self, nbest_result: Dict) -> List[Dict]:
        """Extract word-level timestamps"""
        words = []
        if "Words" in nbest_result:
            for word in nbest_result["Words"]:
                words.append(
                    {
                        "word": word["Word"],
                        "start_time": word["Offset"] / 10000000.0,
                        "end_time": (word["Offset"] + word["Duration"]) / 10000000.0,
                        "confidence": word.get("Confidence", 1.0),
                    }
                )
        return words


class CloudTranscriptionService:
    """
    Multi-provider cloud transcription service with fallback
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.providers = self._initialize_providers()
        self.default_config = TranscriptionConfig()

    def _initialize_providers(
        self,
    ) -> Dict[TranscriptionProvider, TranscriptionProviderBase]:
        """Initialize available providers"""
        providers = {}

        # Initialize each provider using extracted methods
        self._try_initialize_openai_provider(providers)
        self._try_initialize_google_provider(providers)
        self._try_initialize_azure_provider(providers)

        if not providers:
            logger.warning(
                "No transcription providers could be initialized! Only text mode will work."
            )

        logger.info(f"Initialized transcription providers: {list(providers.keys())}")

        return providers

    def _try_initialize_openai_provider(
        self, providers: Dict[TranscriptionProvider, TranscriptionProviderBase]
    ) -> None:
        """Try to initialize OpenAI provider"""
        openai_key = self.config.get("OPENAI_API_KEY")
        if not openai_key:
            return

        try:
            providers[TranscriptionProvider.OPENAI] = OpenAITranscriptionProvider(
                openai_key
            )
            logger.info("OpenAI Whisper provider initialized")
        except Exception as e:
            logger.warning("Failed to initialize OpenAI provider", error=str(e))

    def _try_initialize_google_provider(
        self, providers: Dict[TranscriptionProvider, TranscriptionProviderBase]
    ) -> None:
        """Try to initialize Google provider"""
        if not GOOGLE_AVAILABLE:
            return

        google_creds = self.config.get("GOOGLE_APPLICATION_CREDENTIALS")
        if not google_creds:
            return

        try:
            providers[TranscriptionProvider.GOOGLE] = GoogleTranscriptionProvider(
                google_creds
            )
            logger.info("Google Speech provider initialized")
        except Exception as e:
            logger.warning("Failed to initialize Google provider", error=str(e))

    def _try_initialize_azure_provider(
        self, providers: Dict[TranscriptionProvider, TranscriptionProviderBase]
    ) -> None:
        """Try to initialize Azure provider"""
        if not AZURE_AVAILABLE:
            return

        azure_key = self.config.get("AZURE_SPEECH_KEY")
        azure_region = self.config.get("AZURE_SPEECH_REGION")

        if not azure_key or not azure_region:
            return

        try:
            providers[TranscriptionProvider.AZURE] = AzureTranscriptionProvider(
                azure_key, azure_region
            )
            logger.info("Azure Speech provider initialized")
        except Exception as e:
            logger.warning("Failed to initialize Azure provider", error=str(e))

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def transcribe(
        self,
        audio_data: Union[bytes, str],
        language: str = "ar",
        provider: Optional[TranscriptionProvider] = None,
        **kwargs,
    ) -> TranscriptionResult:
        """
        Transcribe audio with automatic provider selection and fallback - Complex Method fixed
        """
        audio_bytes = self._prepare_audio_data(audio_data)
        config = self._create_transcription_config(language, provider, **kwargs)

        # Try primary provider first
        result = await self._try_primary_provider(audio_bytes, config, provider)
        if result:
            return result

        # Fall back to other providers
        return await self._try_fallback_providers(audio_bytes, config, provider)

    def _prepare_audio_data(self, audio_data: Union[bytes, str]) -> bytes:
        """Prepare audio data for transcription"""
        if isinstance(audio_data, str):
            return base64.b64decode(audio_data)
        return audio_data

    def _create_transcription_config(
        self, language: str, provider: Optional[TranscriptionProvider], **kwargs
    ) -> TranscriptionConfig:
        """Create transcription configuration"""
        return TranscriptionConfig(
            language=language,
            provider=provider or self.default_config.provider,
            **kwargs,
        )

    async def _try_primary_provider(
        self,
        audio_data: bytes,
        config: TranscriptionConfig,
        provider: Optional[TranscriptionProvider],
    ) -> Optional[TranscriptionResult]:
        """Try the specified provider first"""
        if not provider or provider not in self.providers:
            return None

        try:
            return await self.providers[provider].transcribe(audio_data, config)
        except Exception as e:
            logger.warning(f"Provider {provider} failed, trying fallback", error=str(e))
            return None

    async def _try_fallback_providers(
        self,
        audio_data: bytes,
        config: TranscriptionConfig,
        failed_provider: Optional[TranscriptionProvider],
    ) -> TranscriptionResult:
        """Try all remaining providers as fallback"""
        errors = []

        for prov_type, prov_instance in self.providers.items():
            if prov_type == failed_provider:  # Skip already tried
                continue

            try:
                config.provider = prov_type
                result = await prov_instance.transcribe(audio_data, config)
                logger.info(
                    f"Transcription successful with fallback provider: {prov_type}"
                )
                return result
            except Exception as e:
                errors.append(f"{prov_type}: {str(e)}")
                continue

        # All providers failed
        raise Exception(f"All transcription providers failed: {'; '.join(errors)}")

    async def get_available_providers(self) -> List[TranscriptionProvider]:
        """Get list of available providers - Bumpy Road fixed"""
        available = []

        for provider_type, provider_instance in self.providers.items():
            is_available = await self._check_provider_availability(
                provider_type, provider_instance
            )
            if is_available:
                available.append(provider_type)

        return available

    async def _check_provider_availability(
        self,
        provider_type: TranscriptionProvider,
        provider_instance: TranscriptionProviderBase,
    ) -> bool:
        """Check if a specific provider is available"""
        try:
            return await provider_instance.is_available()
        except Exception as e:
            logger.warning(
                f"Provider {provider_type.value} availability check failed: {e}"
            )
            return False

    async def health_check(self) -> Dict[str, bool]:
        """Check health of all providers"""
        health = {}

        for provider_type, provider_instance in self.providers.items():
            try:
                health[provider_type.value] = await provider_instance.is_available()
            except Exception as e:
                logger.error(f"Error in operation: {e}", exc_info=True)
                health[provider_type.value] = False

        return health


# Helper class for Azure audio stream
class AudioInputStream:
    """Audio input stream for Azure"""

    def __init__(self, audio_data: bytes):
        self.audio_data = audio_data
        self.position = 0

    def read(self, size: int) -> bytes:
        """Read audio data"""
        if self.position >= len(self.audio_data):
            return b""

        data = self.audio_data[self.position : self.position + size]
        self.position += len(data)
        return data

    def close(self) -> Any:
        """Close stream"""
        pass
