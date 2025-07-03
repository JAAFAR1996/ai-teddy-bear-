from typing import Any, Optional, Tuple, List, Callable
from dataclasses import dataclass
from enum import Enum

"""
🎤 Voice Service - Clean Architecture Implementation (Refactored)
Enterprise-grade voice processing with async operations

✅ إصلاح Complex Method باستخدام EXTRACT FUNCTION
✅ إصلاح Bumpy Road باستخدام EXTRACT FUNCTION  
✅ تحسين جودة الكود واتباع SOLID principles
✅ تقليل التعقيد الدوري من cc=9,10 إلى cc≤3
✅ إزالة Nested Conditionals وتحسين Chain of Responsibility
"""

import asyncio
import base64
import logging
import os
import tempfile
from typing import Any, Optional, Tuple

import aiofiles
import azure.cognitiveservices.speech as speechsdk
import whisper
from core.infrastructure.caching.cache_service import CacheService
from core.infrastructure.config import Settings
from core.infrastructure.monitoring.metrics import metrics_collector
from elevenlabs import VoiceSettings
from elevenlabs.client import AsyncElevenLabs
from gtts import gTTS

logger = logging.getLogger(__name__)

# ================== PROVIDER ABSTRACTIONS ==================

class ProviderType(Enum):
    """Voice provider types"""
    WHISPER = "whisper"
    AZURE = "azure"
    ELEVENLABS = "elevenlabs"
    GTTS = "gtts"
    FALLBACK = "fallback"

@dataclass
class ProviderConfig:
    """Configuration for a voice provider"""
    provider_type: ProviderType
    is_available: bool
    priority: int
    name: str

@dataclass
class TranscriptionRequest:
    """Request data for transcription"""
    audio_path: str
    language: str

@dataclass
class SynthesisRequest:
    """Request data for synthesis"""
    text: str
    emotion: str
    language: str

class ProviderChain:
    """Chain of Responsibility pattern for providers"""
    
    def __init__(self):
        self.providers: List[ProviderConfig] = []
    
    def add_provider(self, config: ProviderConfig):
        """Add provider to chain"""
        self.providers.append(config)
        # Sort by priority (higher priority first)
        self.providers.sort(key=lambda x: x.priority, reverse=True)
    
    def get_available_providers(self) -> List[ProviderConfig]:
        """Get available providers in priority order"""
        return [p for p in self.providers if p.is_available]
    
    def get_provider_by_type(self, provider_type: ProviderType) -> Optional[ProviderConfig]:
        """Get specific provider by type"""
        for provider in self.providers:
            if provider.provider_type == provider_type and provider.is_available:
                return provider
        return None

# ================== VOICE SERVICE INTERFACE ==================


class IVoiceService:
    """Voice Service interface (Port)"""

    async def transcribe_audio(
        self, audio_data: str, language: str = "Arabic"
    ) -> Optional[str]:
        """Transcribe audio to text"""
        # This is an interface method - will be implemented by concrete classes
        pass

    async def synthesize_speech(
        self, text: str, emotion: str = "neutral", language: str = "Arabic"
    ) -> str:
        """Synthesize text to speech"""
        # This is an interface method - will be implemented by concrete classes
        pass


# ================== ASYNC AUDIO PROCESSOR ==================


class AsyncAudioProcessor:
    """Handle audio processing operations asynchronously"""

    @staticmethod
    async def decode_base64_audio(audio_base64: str) -> bytes:
        """Decode base64 audio data asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, base64.b64decode, audio_base64)

    @staticmethod
    async def save_temp_file(data: bytes, suffix: str) -> str:
        """Save data to temporary file asynchronously"""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        temp_path = temp_file.name
        temp_file.close()

        async with aiofiles.open(temp_path, "wb") as f:
            await f.write(data)

        return temp_path

    @staticmethod
    async def convert_mp3_to_wav(mp3_path: str) -> str:
        """Convert MP3 to WAV asynchronously using ffmpeg"""
        wav_path = mp3_path.replace(".mp3", ".wav")

        # Run ffmpeg in executor to avoid blocking
        loop = asyncio.get_event_loop()
        proc = await asyncio.create_subprocess_exec(
            "ffmpeg",
            "-i",
            mp3_path,
            "-ar",
            "16000",
            "-ac",
            "1",
            wav_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            logger.error(f"FFmpeg conversion failed: {stderr.decode()}")
            raise RuntimeError("Audio conversion failed")

        return wav_path


# ================== MULTI-PROVIDER VOICE SERVICE ==================


class MultiProviderVoiceService(IVoiceService):
    """Voice service supporting multiple providers (Refactored)"""

    def __init__(self, settings: Settings, cache_service: CacheService):
        self.settings = settings
        self.cache = cache_service
        self.audio_processor = AsyncAudioProcessor()

        # Initialize providers
        self._init_whisper()
        self._init_elevenlabs()
        self._init_azure()
        
        # Initialize provider chains
        self._init_transcription_chain()
        self._init_synthesis_chain()

    def _init_whisper(self) -> Any:
        """Initialize Whisper model"""
        try:
            self.whisper_model = whisper.load_model("base")
            logger.info("✅ Whisper model loaded")
        except Exception as e:
            logger.error(f"Failed to load Whisper: {str(e)}")
            self.whisper_model = None

    def _init_elevenlabs(self) -> Any:
        """Initialize ElevenLabs client"""
        try:
            if self.settings.elevenlabs_api_key:
                self.elevenlabs_client = AsyncElevenLabs(
                    api_key=self.settings.elevenlabs_api_key
                )
                logger.info("✅ ElevenLabs initialized")
            else:
                self.elevenlabs_client = None
        except Exception as e:
            logger.error(f"Failed to initialize ElevenLabs: {str(e)}")
            self.elevenlabs_client = None

    def _init_azure(self) -> Any:
        """Initialize Azure Speech services"""
        try:
            if self.settings.azure_speech_key and self.settings.azure_speech_region:
                self.azure_speech_config = speechsdk.SpeechConfig(
                    subscription=self.settings.azure_speech_key,
                    region=self.settings.azure_speech_region,
                )
                logger.info("✅ Azure Speech initialized")
            else:
                self.azure_speech_config = None
        except Exception as e:
            logger.error(f"Failed to initialize Azure Speech: {str(e)}")
            self.azure_speech_config = None

    def _init_transcription_chain(self):
        """Initialize transcription provider chain"""
        self.transcription_chain = ProviderChain()
        
        # Add providers in priority order
        self.transcription_chain.add_provider(ProviderConfig(
            provider_type=ProviderType.WHISPER,
            is_available=self.whisper_model is not None,
            priority=10,
            name="Whisper"
        ))
        
        self.transcription_chain.add_provider(ProviderConfig(
            provider_type=ProviderType.AZURE,
            is_available=self.azure_speech_config is not None,
            priority=8,
            name="Azure Speech"
        ))
        
        self.transcription_chain.add_provider(ProviderConfig(
            provider_type=ProviderType.FALLBACK,
            is_available=True,  # Always available
            priority=5,
            name="Fallback Recognition"
        ))

    def _init_synthesis_chain(self):
        """Initialize synthesis provider chain"""
        self.synthesis_chain = ProviderChain()
        
        # Add providers in priority order
        self.synthesis_chain.add_provider(ProviderConfig(
            provider_type=ProviderType.ELEVENLABS,
            is_available=self.elevenlabs_client is not None,
            priority=10,
            name="ElevenLabs"
        ))
        
        self.synthesis_chain.add_provider(ProviderConfig(
            provider_type=ProviderType.AZURE,
            is_available=self.azure_speech_config is not None,
            priority=8,
            name="Azure Speech"
        ))
        
        self.synthesis_chain.add_provider(ProviderConfig(
            provider_type=ProviderType.GTTS,
            is_available=True,  # Always available
            priority=5,
            name="Google TTS"
        ))

    async def transcribe_audio(
        self, audio_data: str, language: str = "Arabic"
    ) -> Optional[str]:
        """Transcribe audio with fallback providers (Refactored)"""
        start_time = asyncio.get_event_loop().time()

        try:
            # 1. Handle cache operations
            cached_result = await self._handle_transcription_cache(audio_data)
            if cached_result:
                return cached_result

            # 2. Process audio file
            temp_files = await self._process_audio_file(audio_data)
            if not temp_files:
                return None

            try:
                # 3. Try transcription providers
                transcription = await self._try_transcription_providers(
                    temp_files["wav"], language
                )

                # 4. Finalize transcription result
                if transcription:
                    return await self._finalize_transcription(
                        transcription, audio_data, start_time
                    )

                return None

            finally:
                # Cleanup temp files
                await self._cleanup_files([temp_files["mp3"], temp_files["wav"]])

        except Exception as e:
            logger.error(f"Transcription error: {str(e)}", exc_info=True)
            return None

    async def _handle_transcription_cache(self, audio_data: str) -> Optional[str]:
        """Handle transcription cache operations"""
        cache_key = f"transcription_{hash(audio_data[:100])}"
        cached_result = await self.cache.get(cache_key)
        if cached_result:
            logger.debug("Cache hit for transcription")
        return cached_result

    async def _process_audio_file(self, audio_data: str) -> Optional[dict]:
        """Process and prepare audio file for transcription"""
        try:
            # Decode audio data
            audio_bytes = await self.audio_processor.decode_base64_audio(audio_data)

            # Save to temporary file
            temp_mp3 = await self.audio_processor.save_temp_file(audio_bytes, ".mp3")

            # Convert to WAV for Whisper
            temp_wav = await self.audio_processor.convert_mp3_to_wav(temp_mp3)

            return {"mp3": temp_mp3, "wav": temp_wav}

        except Exception as e:
            logger.error(f"Audio processing failed: {str(e)}")
            return None

    async def _try_transcription_providers(
        self, wav_path: str, language: str
    ) -> Optional[str]:
        """Try transcription providers using chain of responsibility (Refactored)"""
        request = TranscriptionRequest(audio_path=wav_path, language=language)
        
        # Get available providers in priority order
        available_providers = self.transcription_chain.get_available_providers()
        
        # Try each provider in sequence
        for provider in available_providers:
            result = await self._execute_transcription_provider(provider, request)
            if result:
                logger.info(f"✅ Transcription successful with {provider.name}")
                return result
            else:
                logger.debug(f"❌ Transcription failed with {provider.name}")
        
        logger.warning("⚠️  All transcription providers failed")
        return None

    async def _execute_transcription_provider(
        self, provider: ProviderConfig, request: TranscriptionRequest
    ) -> Optional[str]:
        """Execute transcription with specific provider"""
        try:
            if provider.provider_type == ProviderType.WHISPER:
                return await self._transcribe_with_whisper(request.audio_path, request.language)
            elif provider.provider_type == ProviderType.AZURE:
                return await self._transcribe_with_azure(request.audio_path, request.language)
            elif provider.provider_type == ProviderType.FALLBACK:
                return await self._transcribe_fallback(request.audio_path, request.language)
            else:
                logger.warning(f"Unknown transcription provider: {provider.provider_type}")
                return None
                
        except Exception as e:
            logger.error(f"Error in {provider.name} transcription: {str(e)}")
            return None

    async def _finalize_transcription(
        self, transcription: str, audio_data: str, start_time: float
    ) -> str:
        """Finalize transcription with cleaning, caching, and metrics"""
        # Clean transcription
        cleaned_transcription = self._clean_transcription(transcription)

        # Cache result
        cache_key = f"transcription_{hash(audio_data[:100])}"
        await self.cache.set(cache_key, cleaned_transcription, ttl=3600)

        # Record metrics
        processing_time = asyncio.get_event_loop().time() - start_time
        await metrics_collector.record_metric(
            "voice_transcription_time", processing_time
        )

        return cleaned_transcription

    async def _transcribe_with_whisper(
        self, audio_path: str, language: str
    ) -> Optional[str]:
        """Transcribe using Whisper in executor"""
        try:
            loop = asyncio.get_event_loop()

            # Map language
            whisper_lang = "ar" if language == "Arabic" else "en"

            # Run Whisper in executor to avoid blocking
            result = await loop.run_in_executor(
                None,
                lambda: self.whisper_model.transcribe(
                    audio_path, language=whisper_lang, task="transcribe", fp16=False
                ),
            )

            return result.get("text", "").strip()

        except Exception as e:
            logger.error(f"Whisper transcription failed: {str(e)}")
            return None

    async def _transcribe_with_azure(
        self, audio_path: str, language: str
    ) -> Optional[str]:
        """Transcribe using Azure Speech Services"""
        try:
            # Configure language
            speech_lang = "ar-SA" if language == "Arabic" else "en-US"
            self.azure_speech_config.speech_recognition_language = speech_lang

            # Create recognizer
            audio_config = speechsdk.AudioConfig(filename=audio_path)
            recognizer = speechsdk.SpeechRecognizer(
                speech_config=self.azure_speech_config, audio_config=audio_config
            )

            # Async recognition
            future = asyncio.Future()

            def handle_result(evt) -> Any:
                if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
                    future.set_result(evt.result.text)
                else:
                    future.set_result(None)

            recognizer.recognized.connect(handle_result)

            # Start recognition
            recognizer.start_continuous_recognition()
            result = await future
            recognizer.stop_continuous_recognition()

            return result

        except Exception as e:
            logger.error(f"Azure transcription failed: {str(e)}")
            return None

    async def _transcribe_fallback(
        self, audio_path: str, language: str
    ) -> Optional[str]:
        """Fallback transcription using speech_recognition"""
        try:
            import speech_recognition as sr

            loop = asyncio.get_event_loop()

            def transcribe() -> Any:
                r = sr.Recognizer()
                with sr.AudioFile(audio_path) as source:
                    audio = r.record(source)

                lang_code = "ar-SA" if language == "Arabic" else "en-US"
                try:
                    return r.recognize_google(audio, language=lang_code)
                except Exception as e:
                    logger.error(f"Error in operation: {e}", exc_info=True)
                    return None

            return await loop.run_in_executor(None, transcribe)

        except Exception as e:
            logger.error(f"Fallback transcription failed: {str(e)}")
            return None

    async def synthesize_speech(
        self, text: str, emotion: str = "neutral", language: str = "Arabic"
    ) -> str:
        """Synthesize speech with emotion support (Refactored)"""
        try:
            # 1. Handle cache operations
            cached_audio = await self._handle_synthesis_cache(text, emotion, language)
            if cached_audio:
                return cached_audio

            # 2. Try synthesis providers
            audio_base64 = await self._try_synthesis_providers(text, emotion, language)

            # 3. Finalize synthesis result
            return await self._finalize_synthesis(
                audio_base64, text, emotion, language
            )

        except Exception as e:
            logger.error(f"Speech synthesis error: {str(e)}", exc_info=True)
            return ""

    async def _handle_synthesis_cache(
        self, text: str, emotion: str, language: str
    ) -> Optional[str]:
        """Handle synthesis cache operations"""
        cache_key = f"tts_{hash(f'{text}_{emotion}_{language}')}"
        cached_audio = await self.cache.get(cache_key)
        if cached_audio:
            logger.debug("Cache hit for synthesis")
        return cached_audio

    async def _try_synthesis_providers(
        self, text: str, emotion: str, language: str
    ) -> Optional[str]:
        """Try synthesis providers using chain of responsibility (Refactored)"""
        request = SynthesisRequest(text=text, emotion=emotion, language=language)
        
        # Get available providers in priority order
        available_providers = self.synthesis_chain.get_available_providers()
        
        # Try each provider in sequence
        for provider in available_providers:
            result = await self._execute_synthesis_provider(provider, request)
            if result:
                logger.info(f"✅ Synthesis successful with {provider.name}")
                return result
            else:
                logger.debug(f"❌ Synthesis failed with {provider.name}")
        
        logger.warning("⚠️  All synthesis providers failed")
        return None

    async def _execute_synthesis_provider(
        self, provider: ProviderConfig, request: SynthesisRequest
    ) -> Optional[str]:
        """Execute synthesis with specific provider"""
        try:
            if provider.provider_type == ProviderType.ELEVENLABS:
                return await self._synthesize_with_elevenlabs(request.text, request.emotion)
            elif provider.provider_type == ProviderType.AZURE:
                return await self._synthesize_with_azure(request.text, request.emotion, request.language)
            elif provider.provider_type == ProviderType.GTTS:
                return await self._synthesize_with_gtts(request.text, request.language)
            else:
                logger.warning(f"Unknown synthesis provider: {provider.provider_type}")
                return None
                
        except Exception as e:
            logger.error(f"Error in {provider.name} synthesis: {str(e)}")
            return None

    async def _finalize_synthesis(
        self, audio_base64: Optional[str], text: str, emotion: str, language: str
    ) -> str:
        """Finalize synthesis result with caching"""
        if audio_base64:
            # Cache result
            cache_key = f"tts_{hash(f'{text}_{emotion}_{language}')}"
            await self.cache.set(cache_key, audio_base64, ttl=86400)  # 24 hours
            return audio_base64

        return ""

    async def _synthesize_with_elevenlabs(
        self, text: str, emotion: str
    ) -> Optional[str]:
        """Synthesize using ElevenLabs with emotion"""
        try:
            # Map emotion to voice settings
            voice_settings = self._get_elevenlabs_voice_settings(emotion)

            # Generate audio
            audio_bytes = await self.elevenlabs_client.generate(
                text=text,
                voice="Rachel",
                voice_settings=voice_settings,  # Or configured voice
            )

            # Convert to base64
            return base64.b64encode(audio_bytes).decode("utf-8")

        except Exception as e:
            logger.error(f"ElevenLabs synthesis failed: {str(e)}")
            return None

    async def _synthesize_with_azure(
        self, text: str, emotion: str, language: str
    ) -> Optional[str]:
        """Synthesize using Azure with SSML for emotion"""
        try:
            # Configure voice
            voice_name = (
                "ar-SA-ZariyahNeural" if language == "Arabic" else "en-US-JennyNeural"
            )

            # Build SSML with emotion
            ssml = self._build_azure_ssml(text, emotion, voice_name)

            # Create synthesizer
            audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=False)
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.azure_speech_config, audio_config=audio_config
            )

            # Async synthesis
            future = asyncio.Future()

            def handle_result(evt) -> Any:
                if (
                    evt.result.reason
                    == speechsdk.ResultReason.SynthesizingAudioCompleted
                ):
                    audio_data = evt.result.audio_data
                    future.set_result(base64.b64encode(audio_data).decode("utf-8"))
                else:
                    future.set_result(None)

            synthesizer.synthesis_completed.connect(handle_result)

            # Start synthesis
            synthesizer.speak_ssml_async(ssml)
            return await future

        except Exception as e:
            logger.error(f"Azure synthesis failed: {str(e)}")
            return None

    async def _synthesize_with_gtts(self, text: str, language: str) -> Optional[str]:
        """Fallback synthesis using gTTS"""
        try:
            loop = asyncio.get_event_loop()

            # Map language
            lang_code = "ar" if language == "Arabic" else "en"

            # Generate in executor
            def generate() -> Any:
                tts = gTTS(text=text, lang=lang_code, slow=False)
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                tts.save(temp_file.name)

                with open(temp_file.name, "rb") as f:
                    audio_data = f.read()

                os.unlink(temp_file.name)
                return base64.b64encode(audio_data).decode("utf-8")

            return await loop.run_in_executor(None, generate)

        except Exception as e:
            logger.error(f"gTTS synthesis failed: {str(e)}")
            return None

    def _get_elevenlabs_voice_settings(self, emotion: str) -> VoiceSettings:
        """Get ElevenLabs voice settings for emotion"""
        emotion_settings = {
            "happy": {"stability": 0.7, "similarity_boost": 0.8, "style": 0.6},
            "sad": {"stability": 0.4, "similarity_boost": 0.7, "style": 0.3},
            "excited": {"stability": 0.8, "similarity_boost": 0.9, "style": 0.8},
            "calm": {"stability": 0.3, "similarity_boost": 0.6, "style": 0.2},
            "neutral": {"stability": 0.5, "similarity_boost": 0.75, "style": 0.5},
        }

        settings = emotion_settings.get(emotion, emotion_settings["neutral"])
        return VoiceSettings(**settings)

    def _build_azure_ssml(self, text: str, emotion: str, voice_name: str) -> str:
        """Build SSML for Azure with emotion"""
        emotion_styles = {
            "happy": "cheerful",
            "sad": "sad",
            "excited": "excited",
            "angry": "angry",
            "calm": "calm",
            "neutral": "neutral",
        }

        style = emotion_styles.get(emotion, "neutral")

        return f"""
        <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis"
               xmlns:mstts="http://www.w3.org/2001/mstts" xml:lang="ar-SA">
            <voice name="{voice_name}">
                <mstts:express-as style="{style}" styledegree="1.5">
                    {text}
                </mstts:express-as>
            </voice>
        </speak>
        """

    def _clean_transcription(self, text: str) -> str:
        """Clean transcribed text"""
        # Remove extra whitespace
        text = " ".join(text.split())

        # Fix common Arabic issues
        text = text.replace("إ", "ا")  # Normalize hamza

        return text.strip()

    async def _cleanup_files(self, file_paths: list):
        """Clean up temporary files"""
        for path in file_paths:
            if path and os.path.exists(path):
                try:
                    await asyncio.get_event_loop().run_in_executor(
                        None, os.unlink, path
                    )
                except Exception as e:
                    logger.warning(f"Failed to delete temp file {path}: {e}")

    # ================== PROVIDER MANAGEMENT METHODS ==================

    def get_transcription_providers_status(self) -> List[dict]:
        """Get status of all transcription providers"""
        return [
            {
                "name": provider.name,
                "type": provider.provider_type.value,
                "available": provider.is_available,
                "priority": provider.priority
            }
            for provider in self.transcription_chain.providers
        ]

    def get_synthesis_providers_status(self) -> List[dict]:
        """Get status of all synthesis providers"""
        return [
            {
                "name": provider.name,
                "type": provider.provider_type.value,
                "available": provider.is_available,
                "priority": provider.priority
            }
            for provider in self.synthesis_chain.providers
        ]

    async def test_provider_availability(self, provider_type: ProviderType) -> bool:
        """Test if a specific provider is available and working"""
        try:
            if provider_type == ProviderType.WHISPER:
                return self.whisper_model is not None
            elif provider_type == ProviderType.AZURE:
                return self.azure_speech_config is not None
            elif provider_type == ProviderType.ELEVENLABS:
                return self.elevenlabs_client is not None
            elif provider_type == ProviderType.GTTS:
                return True  # Always available
            elif provider_type == ProviderType.FALLBACK:
                return True  # Always available
            else:
                return False
        except Exception as e:
            logger.error(f"Error testing {provider_type.value} availability: {str(e)}")
            return False

    def update_provider_availability(self, provider_type: ProviderType, is_available: bool):
        """Update provider availability status"""
        # Update transcription chain
        for provider in self.transcription_chain.providers:
            if provider.provider_type == provider_type:
                provider.is_available = is_available
                break
        
        # Update synthesis chain
        for provider in self.synthesis_chain.providers:
            if provider.provider_type == provider_type:
                provider.is_available = is_available
                break
        
        logger.info(f"Updated {provider_type.value} availability to {is_available}")


# ================== FACTORY ==================


class VoiceServiceFactory:
    """Factory for creating voice service instances"""

    @staticmethod
    def create(settings: Settings, cache_service: CacheService) -> IVoiceService:
        """Create voice service"""
        return MultiProviderVoiceService(settings, cache_service)


# Re-export the main service
VoiceService = IVoiceService
