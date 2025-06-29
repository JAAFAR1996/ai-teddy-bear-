"""
Cloud-based Transcription Service
Supports multiple providers: OpenAI Whisper API, Google Speech-to-Text, Azure Speech
"""

import asyncio
import base64
import io
from abc import ABC, abstractmethod
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
import io
from typing import Any, Dict, List, Optional, Union

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
        SpeechConfig,
        SpeechRecognizer,
        AudioConfig,
        ResultReason
    )
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False

from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential

from src.application.services.circuit_breaker import circuit_breaker

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
        self,
        audio_data: bytes,
        config: TranscriptionConfig
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
        self,
        audio_data: bytes,
        config: TranscriptionConfig
    ) -> TranscriptionResult:
        """Transcribe using OpenAI Whisper API"""
        try:
            # Create file-like object
            audio_file = io.BytesIO(audio_data)
            audio_file.name = "audio.wav"
            
            # Call OpenAI API
            response = await self.client.audio.transcriptions.create(
                model=config.model,
                file=audio_file,
                language=config.language,
                temperature=config.temperature,
                response_format="verbose_json" if config.enable_word_timestamps else "json"
            )
            
            # Parse response
            result = TranscriptionResult(
                text=response.text,
                language=response.language if hasattr(response, 'language') else config.language,
                duration=response.duration if hasattr(response, 'duration') else None,
                words=response.words if hasattr(response, 'words') else None,
                metadata={"provider": "openai", "model": config.model}
            )
            
            logger.info(
                "OpenAI transcription completed",
                text_length=len(result.text),
                language=result.language
            )
            
            return result
            
        except Exception as e:
            logger.error("OpenAI transcription failed", error=str(e))
            raise
    
    async def is_available(self) -> bool:
        """Check if OpenAI is available"""
        try:
            # Simple models list to check connectivity
            await self.client.models.list()
            return True
        except:
            return False


class GoogleTranscriptionProvider(TranscriptionProviderBase):
    """Google Speech-to-Text provider"""
    
    def __init__(self, credentials_path: Optional[str] = None):
        if not GOOGLE_AVAILABLE:
            raise ImportError("Google Cloud Speech library not installed. Run: pip install google-cloud-speech")
        self.client = speech_v1.SpeechAsyncClient()
        self.credentials_path = credentials_path
    
    @circuit_breaker("google_transcription", failure_threshold=3)
    async def transcribe(
        self,
        audio_data: bytes,
        config: TranscriptionConfig
    ) -> TranscriptionResult:
        """Transcribe using Google Speech-to-Text"""
        try:
            # Configure recognition
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
            
            # Perform recognition
            response = await self.client.recognize(
                config=recognition_config,
                audio=audio
            )
            
            # Parse response
            if not response.results:
                return TranscriptionResult(
                    text="",
                    language=config.language,
                    confidence=0.0,
                    metadata={"provider": "google", "error": "No results"}
                )
            
            # Get best alternative
            result = response.results[0]
            best_alternative = result.alternatives[0]
            
            # Extract words if available
            words = None
            if config.enable_word_timestamps and hasattr(best_alternative, 'words'):
                words = [
                    {
                        "word": word.word,
                        "start_time": word.start_time.total_seconds(),
                        "end_time": word.end_time.total_seconds(),
                        "confidence": getattr(word, 'confidence', 1.0)
                    }
                    for word in best_alternative.words
                ]
            
            transcription_result = TranscriptionResult(
                text=best_alternative.transcript,
                language=config.language,
                confidence=best_alternative.confidence,
                words=words,
                alternatives=[
                    {"text": alt.transcript, "confidence": alt.confidence}
                    for alt in result.alternatives[1:config.max_alternatives]
                ],
                metadata={
                    "provider": "google",
                    "language_code": result.language_code if hasattr(result, 'language_code') else None
                }
            )
            
            logger.info(
                "Google transcription completed",
                text_length=len(transcription_result.text),
                confidence=transcription_result.confidence
            )
            
            return transcription_result
            
        except Exception as e:
            logger.error("Google transcription failed", error=str(e))
            raise
    
    async def is_available(self) -> bool:
        """Check if Google Speech is available"""
        try:
            # Try a simple operation
            await self.client.list_phrase_set(parent="projects/-/locations/global")
            return True
        except:
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
            raise ImportError("Azure Speech library not installed. Run: pip install azure-cognitiveservices-speech")
        self.subscription_key = subscription_key
        self.region = region
        self.speech_config = SpeechConfig(
            subscription=subscription_key,
            region=region
        )
    
    @circuit_breaker("azure_transcription", failure_threshold=3)
    async def transcribe(
        self,
        audio_data: bytes,
        config: TranscriptionConfig
    ) -> TranscriptionResult:
        """Transcribe using Azure Speech Services"""
        try:
            # Configure speech recognition
            self.speech_config.speech_recognition_language = self._get_language_code(config.language)
            self.speech_config.request_word_level_timestamps()
            
            # Create audio stream
            audio_stream = AudioInputStream(audio_data)
            audio_config = AudioConfig(stream=audio_stream)
            
            # Create recognizer
            recognizer = SpeechRecognizer(
                speech_config=self.speech_config,
                audio_config=audio_config
            )
            
            # Perform recognition
            result = await self._recognize_async(recognizer)
            
            if result.reason == ResultReason.RecognizedSpeech:
                # Extract detailed results
                details = result.json
                
                words = None
                if config.enable_word_timestamps and "NBest" in details:
                    words = self._extract_words(details["NBest"][0])
                
                transcription_result = TranscriptionResult(
                    text=result.text,
                    language=config.language,
                    confidence=details.get("NBest", [{}])[0].get("Confidence", 1.0),
                    duration=details.get("Duration", 0) / 10000000.0,  # Convert to seconds
                    words=words,
                    metadata={
                        "provider": "azure",
                        "recognition_status": result.reason.name
                    }
                )
                
                logger.info(
                    "Azure transcription completed",
                    text_length=len(transcription_result.text),
                    reason=result.reason.name
                )
                
                return transcription_result
                
            else:
                raise Exception(f"Recognition failed: {result.reason}")
                
        except Exception as e:
            logger.error("Azure transcription failed", error=str(e))
            raise
    
    async def is_available(self) -> bool:
        """Check if Azure Speech is available"""
        try:
            # Test with empty audio
            return True  # Azure doesn't have a simple health check
        except:
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
        
        def recognized_cb(evt):
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
                words.append({
                    "word": word["Word"],
                    "start_time": word["Offset"] / 10000000.0,
                    "end_time": (word["Offset"] + word["Duration"]) / 10000000.0,
                    "confidence": word.get("Confidence", 1.0)
                })
        return words


class CloudTranscriptionService:
    """
    Multi-provider cloud transcription service with fallback
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.providers = self._initialize_providers()
        self.default_config = TranscriptionConfig()
    
    def _initialize_providers(self) -> Dict[TranscriptionProvider, TranscriptionProviderBase]:
        """Initialize available providers"""
        providers = {}
        
        # OpenAI
        if openai_key := self.config.get("OPENAI_API_KEY"):
            try:
                providers[TranscriptionProvider.OPENAI] = OpenAITranscriptionProvider(openai_key)
                logger.info("OpenAI Whisper provider initialized")
            except Exception as e:
                logger.warning("Failed to initialize OpenAI provider", error=str(e))
        
        # Google (optional)
        if GOOGLE_AVAILABLE and (google_creds := self.config.get("GOOGLE_APPLICATION_CREDENTIALS")):
            try:
                providers[TranscriptionProvider.GOOGLE] = GoogleTranscriptionProvider(google_creds)
                logger.info("Google Speech provider initialized")
            except Exception as e:
                logger.warning("Failed to initialize Google provider", error=str(e))
        
        # Azure (optional)
        if AZURE_AVAILABLE and (azure_key := self.config.get("AZURE_SPEECH_KEY")) and \
           (azure_region := self.config.get("AZURE_SPEECH_REGION")):
            try:
                providers[TranscriptionProvider.AZURE] = AzureTranscriptionProvider(
                    azure_key,
                    azure_region
                )
                logger.info("Azure Speech provider initialized")
            except Exception as e:
                logger.warning("Failed to initialize Azure provider", error=str(e))
        
        if not providers:
            logger.warning("No transcription providers could be initialized! Only text mode will work.")
        
        logger.info(f"Initialized transcription providers: {list(providers.keys())}")
        
        return providers
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def transcribe(
        self,
        audio_data: Union[bytes, str],
        language: str = "ar",
        provider: Optional[TranscriptionProvider] = None,
        **kwargs
    ) -> TranscriptionResult:
        """
        Transcribe audio with automatic provider selection and fallback
        """
        # Handle base64 input
        if isinstance(audio_data, str):
            audio_data = base64.b64decode(audio_data)
        
        # Create config
        config = TranscriptionConfig(
            language=language,
            provider=provider or self.default_config.provider,
            **kwargs
        )
        
        # Try specified provider first
        if provider and provider in self.providers:
            try:
                return await self.providers[provider].transcribe(audio_data, config)
            except Exception as e:
                logger.warning(
                    f"Provider {provider} failed, trying fallback",
                    error=str(e)
                )
        
        # Try all available providers
        errors = []
        for prov_type, prov_instance in self.providers.items():
            if prov_type == provider:  # Skip already tried
                continue
            
            try:
                config.provider = prov_type
                result = await prov_instance.transcribe(audio_data, config)
                logger.info(f"Transcription successful with fallback provider: {prov_type}")
                return result
            except Exception as e:
                errors.append(f"{prov_type}: {str(e)}")
                continue
        
        # All providers failed
        raise Exception(f"All transcription providers failed: {'; '.join(errors)}")
    
    async def get_available_providers(self) -> List[TranscriptionProvider]:
        """Get list of available providers"""
        available = []
        
        for provider_type, provider_instance in self.providers.items():
            try:
                if await provider_instance.is_available():
                    available.append(provider_type)
            except:
                pass
        
        return available
    
    async def health_check(self) -> Dict[str, bool]:
        """Check health of all providers"""
        health = {}
        
        for provider_type, provider_instance in self.providers.items():
            try:
                health[provider_type.value] = await provider_instance.is_available()
            except:
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
            return b''
        
        data = self.audio_data[self.position:self.position + size]
        self.position += len(data)
        return data
    
    def close(self):
        """Close stream"""
        pass 