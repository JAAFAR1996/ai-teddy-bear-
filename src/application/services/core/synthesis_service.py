"""
🔊 Modern Synthesis Service - 2025 Edition
Streaming Text-to-Speech with emotional intelligence and multi-provider support
"""

import asyncio
import io
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, AsyncIterator, Dict, List, Optional, Union

import numpy as np

# Audio processing
try:
    import soundfile as sf
except ImportError:
    sf = None
try:
    from pydub import AudioSegment
    from pydub.effects import normalize
except ImportError:
    AudioSegment = None
    normalize = None

# Voice synthesis providers
try:
    from elevenlabs import ElevenLabs, Voice, VoiceSettings, generate, stream
except ImportError:
    try:
        from src.infrastructure.external_services.mock.elevenlabs import (
            ElevenLabs, Voice, VoiceSettings, generate, stream)
    except ImportError:
        ElevenLabs = Voice = VoiceSettings = stream = generate = None
from openai import AsyncOpenAI

try:
    import azure.cognitiveservices.speech as speechsdk
except ImportError:
    speechsdk = None

# Value objects
from src.domain.value_objects import Confidence, EmotionalTone

logger = logging.getLogger(__name__)

# ================== CONFIGURATION ==================

class VoiceProvider(Enum):
    """Supported voice synthesis providers"""
    ELEVENLABS = "elevenlabs"
    OPENAI = "openai"
    AZURE = "azure"
    SYSTEM = "system"  # OS built-in TTS

@dataclass
class SynthesisConfig:
    """Configuration for synthesis service"""
    # Audio settings
    sample_rate: int = 24000
    channels: int = 1
    bit_depth: int = 16
    
    # Streaming settings
    chunk_size: int = 1024
    buffer_size: int = 4096
    streaming_enabled: bool = True
    
    # Quality settings
    voice_stability: float = 0.5
    voice_similarity: float = 0.8
    voice_style: float = 0.4
    voice_boost: bool = True
    
    # Performance settings
    timeout_seconds: float = 30.0
    max_retries: int = 3
    fallback_provider: VoiceProvider = VoiceProvider.SYSTEM
    
    # Language settings
    default_language: str = "en"
    auto_detect_language: bool = True

@dataclass
class VoiceCharacter:
    """Voice character profile with emotional settings"""
    id: str
    name: str
    provider: VoiceProvider
    voice_id: str
    language: str
    description: str
    
    # Emotional voice settings
    emotional_settings: Dict[EmotionalTone, VoiceSettings]
    
    # Voice adjustments
    pitch_adjustment: float = 0.0  # semitones
    speed_adjustment: float = 1.0  # multiplier
    volume_adjustment: float = 1.0  # multiplier

@dataclass
class SynthesisContext:
    """Context for synthesis operations"""
    text: str
    emotion: EmotionalTone
    character: VoiceCharacter
    voice_settings: VoiceSettings

@dataclass
class SynthesisServiceCredentials:
    """Credentials and settings for synthesis service providers"""
    # API Keys
    elevenlabs_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    azure_speech_key: Optional[str] = None
    
    # Provider-specific settings
    azure_speech_region: str = "eastus"
    
    # Validation and helper methods
    def has_elevenlabs(self) -> bool:
        """Check if ElevenLabs credentials are available"""
        return self.elevenlabs_api_key is not None
    
    def has_openai(self) -> bool:
        """Check if OpenAI credentials are available"""
        return self.openai_api_key is not None
    
    def has_azure(self) -> bool:
        """Check if Azure Speech credentials are available"""
        return self.azure_speech_key is not None
    
    def get_available_providers(self) -> List[VoiceProvider]:
        """Get list of available providers based on credentials"""
        providers = []
        if self.has_elevenlabs():
            providers.append(VoiceProvider.ELEVENLABS)
        if self.has_openai():
            providers.append(VoiceProvider.OPENAI)
        if self.has_azure():
            providers.append(VoiceProvider.AZURE)
        providers.append(VoiceProvider.SYSTEM)  # Always available as fallback
        return providers

# ================== STREAMING AUDIO BUFFER ==================

class StreamingAudioBuffer:
    """Buffer for streaming audio output"""
    
    def __init__(self, config: SynthesisConfig):
        self.config = config
        self.buffer = bytearray()
        self.lock = asyncio.Lock()
        self.total_bytes = 0
        
    async def write(self, audio_chunk: bytes) -> None:
        """Write audio chunk to buffer"""
        async with self.lock:
            self.buffer.extend(audio_chunk)
            self.total_bytes += len(audio_chunk)
    
    async def read(self, size: int = None) -> bytes:
        """Read audio chunk from buffer"""
        async with self.lock:
            if size is None:
                size = self.config.chunk_size
            
            if len(self.buffer) >= size:
                chunk = bytes(self.buffer[:size])
                self.buffer = self.buffer[size:]
                return chunk
            
            return bytes()
    
    async def read_all(self) -> bytes:
        """Read all audio from buffer"""
        async with self.lock:
            audio = bytes(self.buffer)
            self.buffer.clear()
            return audio
    
    def is_empty(self) -> bool:
        """Check if buffer is empty"""
        return len(self.buffer) == 0
    
    @property
    def size(self) -> int:
        """Current buffer size"""
        return len(self.buffer)

# ================== SYNTHESIS SERVICE ==================

class ModernSynthesisService:
    """
    🔊 Modern Synthesis Service with 2025 Features:
    - Multi-provider support (ElevenLabs, OpenAI, Azure)
    - Real-time streaming synthesis
    - Emotional voice modulation
    - Voice character management
    - Smart fallback mechanisms
    - Performance monitoring
    """
    
    def __init__(self, config: Optional[SynthesisConfig] = None):
        self.config = config or SynthesisConfig()
        
        # Provider clients
        self.elevenlabs_client: Optional[ElevenLabs] = None
        self.openai_client: Optional[AsyncOpenAI] = None
        self.azure_speech_config: Optional[speechsdk.SpeechConfig] = None
        
        # Voice characters
        self.voice_characters: Dict[str, VoiceCharacter] = {}
        self.current_character: Optional[VoiceCharacter] = None
        
        # Streaming buffer
        self.output_buffer = StreamingAudioBuffer(self.config)
        
        # Performance tracking
        self.stats = {
            "total_syntheses": 0,
            "total_processing_time": 0.0,
            "total_audio_duration": 0.0,
            "error_count": 0,
            "provider_usage": {}
        }
        
        logger.info("✅ Modern Synthesis Service initialized")
    
    async def initialize(
        self,
        credentials: Optional[SynthesisServiceCredentials] = None
    ) -> None:
        """Initialize synthesis providers using credentials object"""
        if credentials is None:
            credentials = SynthesisServiceCredentials()
            
        try:
            # Initialize ElevenLabs
            if credentials.has_elevenlabs():
                self.elevenlabs_client = ElevenLabs(api_key=credentials.elevenlabs_api_key)
                logger.info("✅ ElevenLabs client initialized")
            
            # Initialize OpenAI
            if credentials.has_openai():
                self.openai_client = AsyncOpenAI(api_key=credentials.openai_api_key)
                logger.info("✅ OpenAI client initialized for TTS")
            
            # Initialize Azure Speech
            if credentials.has_azure():
                self.azure_speech_config = speechsdk.SpeechConfig(
                    subscription=credentials.azure_speech_key,
                    region=credentials.azure_speech_region
                )
                logger.info("✅ Azure Speech client initialized")
            
            # Load default voice characters
            await self._load_default_characters()
            
            # Log available providers
            available_providers = credentials.get_available_providers()
            logger.info(f"🚀 Synthesis service initialized with providers: {[p.value for p in available_providers]}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize synthesis service: {e}")
            raise
    
    async def _load_default_characters(self) -> None:
        """Load default voice characters"""
        # Teddy Bear Character (English)
        teddy_emotional_settings = {
            EmotionalTone.HAPPY: VoiceSettings(stability=0.3, similarity_boost=0.7, style=0.4),
            EmotionalTone.CALM: VoiceSettings(stability=0.6, similarity_boost=0.5, style=0.2),
            EmotionalTone.EXCITED: VoiceSettings(stability=0.2, similarity_boost=0.8, style=0.7),
            EmotionalTone.CURIOUS: VoiceSettings(stability=0.4, similarity_boost=0.6, style=0.5),
            EmotionalTone.LOVE: VoiceSettings(stability=0.7, similarity_boost=0.4, style=0.3),
            EmotionalTone.ENCOURAGING: VoiceSettings(stability=0.5, similarity_boost=0.6, style=0.4),
            EmotionalTone.FRIENDLY: VoiceSettings(stability=0.4, similarity_boost=0.7, style=0.5)
        }
        
        self.voice_characters["teddy_en"] = VoiceCharacter(
            id="teddy_en",
            name="Friendly Teddy (English)",
            provider=VoiceProvider.ELEVENLABS,
            voice_id="josh",  # Default ElevenLabs voice
            language="en",
            description="Warm, friendly teddy bear voice for children",
            emotional_settings=teddy_emotional_settings,
            pitch_adjustment=2.0,  # Higher pitch for child-friendly voice
            speed_adjustment=0.95,  # Slightly slower for clarity
            volume_adjustment=1.0
        )
        
        # Arabic Teddy Character
        self.voice_characters["teddy_ar"] = VoiceCharacter(
            id="teddy_ar",
            name="دبدوب الودود (Arabic)",
            provider=VoiceProvider.AZURE,  # Better Arabic support
            voice_id="ar-SA-ZariyahNeural",
            language="ar",
            description="صوت دبدوب ودود للأطفال باللغة العربية",
            emotional_settings=teddy_emotional_settings,
            pitch_adjustment=1.5,
            speed_adjustment=0.9,
            volume_adjustment=1.0
        )
        
        # Set default character
        self.current_character = self.voice_characters["teddy_en"]
        logger.info(f"📝 Loaded {len(self.voice_characters)} voice characters")
    
    async def synthesize_stream(
        self,
        text: str,
        emotion: EmotionalTone = EmotionalTone.FRIENDLY,
        character_id: Optional[str] = None,
        language: Optional[str] = None
    ) -> AsyncIterator[bytes]:
        """
        🌊 Stream synthesis with real-time audio generation
        
        Args:
            text: Text to synthesize
            emotion: Emotional tone
            character_id: Voice character ID
            language: Language override
            
        Yields:
            Audio chunks as bytes
        """
        start_time = time.time()
        
        try:
            # Prepare synthesis context
            synthesis_context = await self._prepare_synthesis_context(text, emotion, character_id, language)
            
            # Execute streaming synthesis
            async for chunk in self._execute_streaming_synthesis(synthesis_context):
                yield chunk
            
            # Update stats
            processing_time = time.time() - start_time
            self._update_stats(synthesis_context.character.provider, processing_time)
            
        except Exception as e:
            logger.error(f"❌ Stream synthesis failed: {e}")
            # Fallback synthesis
            async for chunk in self._fallback_synthesis_stream(text):
                yield chunk
    
    async def synthesize_audio(
        self,
        text: str,
        emotion: EmotionalTone = EmotionalTone.FRIENDLY,
        character_id: Optional[str] = None,
        language: Optional[str] = None
    ) -> Optional[bytes]:
        """
        🎯 Synthesize complete audio with multiple provider support
        
        Args:
            text: Text to synthesize
            emotion: Emotional tone
            character_id: Voice character ID
            language: Language override
            
        Returns:
            Complete audio as bytes or None if failed
        """
        start_time = time.time()
        
        try:
            # Prepare synthesis context
            synthesis_context = await self._prepare_synthesis_context(text, emotion, character_id, language)
            
            # Execute audio synthesis
            audio_data = await self._execute_audio_synthesis(synthesis_context)
            
            # Apply post-processing
            if audio_data:
                audio_data = await self._apply_voice_adjustments(audio_data, synthesis_context.character)
            
            # Update stats
            processing_time = time.time() - start_time
            self._update_stats(synthesis_context.character.provider, processing_time)
            
            logger.debug(f"🎯 Synthesized in {processing_time:.2f}s: '{text[:50]}...'")
            return audio_data
            
        except Exception as e:
            logger.error(f"❌ Audio synthesis failed: {e}")
            self.stats["error_count"] += 1
            return await self._synthesize_fallback(text)
    
    async def _prepare_synthesis_context(
        self,
        text: str,
        emotion: EmotionalTone,
        character_id: Optional[str],
        language: Optional[str]
    ) -> 'SynthesisContext':
        """Prepare synthesis context with character and voice settings"""
        character = await self._select_character(character_id, language)
        voice_settings = character.emotional_settings.get(
            emotion, 
            character.emotional_settings[EmotionalTone.FRIENDLY]
        )
        
        return SynthesisContext(
            text=text,
            emotion=emotion,
            character=character,
            voice_settings=voice_settings
        )
    
    async def _execute_streaming_synthesis(self, context: 'SynthesisContext') -> AsyncIterator[bytes]:
        """Execute streaming synthesis based on provider using strategy pattern"""
        provider_strategy = self._get_streaming_strategy(context.character.provider)
        
        try:
            async for chunk in provider_strategy(context):
                yield chunk
        except Exception as e:
            logger.error(f"❌ Provider {context.character.provider.value} streaming failed: {e}")
            # Fallback to chunked audio synthesis
            async for chunk in self._fallback_streaming_synthesis(context):
                yield chunk
    
    def _get_streaming_strategy(self, provider: VoiceProvider):
        """Get streaming strategy function for the given provider"""
        strategies = {
            VoiceProvider.ELEVENLABS: self._stream_elevenlabs_strategy,
            VoiceProvider.OPENAI: self._stream_openai_strategy,
            VoiceProvider.AZURE: self._stream_azure_strategy,
        }
        
        return strategies.get(provider, self._stream_fallback_strategy)
    
    async def _stream_elevenlabs_strategy(self, context: 'SynthesisContext') -> AsyncIterator[bytes]:
        """ElevenLabs streaming strategy"""
        if not self.elevenlabs_client:
            async for chunk in self._stream_fallback_strategy(context):
                yield chunk
            return
            
        async for chunk in self._synthesize_elevenlabs_stream(context.text, context.character, context.voice_settings):
            yield chunk
    
    async def _stream_openai_strategy(self, context: 'SynthesisContext') -> AsyncIterator[bytes]:
        """OpenAI streaming strategy"""
        if not self.openai_client:
            async for chunk in self._stream_fallback_strategy(context):
                yield chunk
            return
            
        async for chunk in self._synthesize_openai_stream(context.text, context.character):
            yield chunk
    
    async def _stream_azure_strategy(self, context: 'SynthesisContext') -> AsyncIterator[bytes]:
        """Azure streaming strategy"""
        if not self.azure_speech_config:
            async for chunk in self._stream_fallback_strategy(context):
                yield chunk
            return
            
        async for chunk in self._synthesize_azure_stream(context.text, context.character, context.emotion):
            yield chunk
    
    async def _stream_fallback_strategy(self, context: 'SynthesisContext') -> AsyncIterator[bytes]:
        """Fallback streaming strategy"""
        async for chunk in self._fallback_streaming_synthesis(context):
            yield chunk
    
    async def _execute_audio_synthesis(self, context: 'SynthesisContext') -> Optional[bytes]:
        """Execute audio synthesis based on provider"""
        provider = context.character.provider
        
        if provider == VoiceProvider.ELEVENLABS and self.elevenlabs_client:
            return await self._synthesize_elevenlabs(context.text, context.character, context.voice_settings)
        elif provider == VoiceProvider.OPENAI and self.openai_client:
            return await self._synthesize_openai(context.text, context.character)
        elif provider == VoiceProvider.AZURE and self.azure_speech_config:
            return await self._synthesize_azure(context.text, context.character, context.emotion)
        else:
            return await self._synthesize_fallback(context.text)
    
    async def _synthesize_elevenlabs_stream(
        self,
        text: str,
        character: VoiceCharacter,
        voice_settings: VoiceSettings
    ) -> AsyncIterator[bytes]:
        """Stream synthesis using ElevenLabs"""
        try:
            # Generate stream
            audio_stream = stream(
                text=text,
                voice=character.voice_id,
                model="eleven_multilingual_v2",
                voice_settings=voice_settings
            )
            
            # Yield chunks
            for chunk in audio_stream:
                yield chunk
                
        except Exception as e:
            logger.error(f"❌ ElevenLabs streaming failed: {e}")
            # Fallback to regular generation
            audio = generate(
                text=text,
                voice=character.voice_id,
                voice_settings=voice_settings
            )
            # Chunk for streaming
            chunk_size = self.config.chunk_size
            for i in range(0, len(audio), chunk_size):
                yield audio[i:i + chunk_size]
                await asyncio.sleep(0.01)
    
    async def _synthesize_elevenlabs(
        self,
        text: str,
        character: VoiceCharacter,
        voice_settings: VoiceSettings
    ) -> bytes:
        """Synthesize using ElevenLabs"""
        try:
            audio = generate(
                text=text,
                voice=character.voice_id,
                model="eleven_multilingual_v2",
                voice_settings=voice_settings
            )
            return audio
            
        except Exception as e:
            logger.error(f"❌ ElevenLabs synthesis failed: {e}")
            raise
    
    async def _synthesize_openai_stream(
        self,
        text: str,
        character: VoiceCharacter
    ) -> AsyncIterator[bytes]:
        """Stream synthesis using OpenAI (TTS-1)"""
        try:
            response = await self.openai_client.audio.speech.create(
                model="tts-1",
                voice=character.voice_id,
                input=text,
                response_format="opus"  # Better for streaming
            )
            
            # Stream the response
            async for chunk in response.iter_bytes():
                yield chunk
                
        except Exception as e:
            logger.error(f"❌ OpenAI streaming synthesis failed: {e}")
            # Fallback to complete synthesis
            response = await self.openai_client.audio.speech.create(
                model="tts-1",
                voice=character.voice_id,
                input=text
            )
            audio_data = response.content
            # Chunk for streaming
            chunk_size = self.config.chunk_size
            for i in range(0, len(audio_data), chunk_size):
                yield audio_data[i:i + chunk_size]
                await asyncio.sleep(0.01)
    
    async def _synthesize_openai(
        self,
        text: str,
        character: VoiceCharacter
    ) -> bytes:
        """Synthesize using OpenAI"""
        try:
            response = await self.openai_client.audio.speech.create(
                model="tts-1-hd",  # Higher quality for non-streaming
                voice=character.voice_id,
                input=text
            )
            return response.content
            
        except Exception as e:
            logger.error(f"❌ OpenAI synthesis failed: {e}")
            raise
    
    async def _synthesize_azure_stream(
        self,
        text: str,
        character: VoiceCharacter,
        emotion: EmotionalTone
    ) -> AsyncIterator[bytes]:
        """Stream synthesis using Azure Speech"""
        try:
            # Configure speech synthesis
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.azure_speech_config,
                audio_config=None  # We'll handle the audio ourselves
            )
            
            # Build SSML with emotion
            ssml = self._build_azure_ssml(text, character, emotion)
            
            # Synthesize
            result = await asyncio.to_thread(synthesizer.speak_ssml, ssml)
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                audio_data = result.audio_data
                # Chunk for streaming
                chunk_size = self.config.chunk_size
                for i in range(0, len(audio_data), chunk_size):
                    yield audio_data[i:i + chunk_size]
                    await asyncio.sleep(0.01)
            else:
                logger.error(f"Azure synthesis failed: {result.reason}")
                
        except Exception as e:
            logger.error(f"❌ Azure streaming synthesis failed: {e}")
    
    async def _synthesize_azure(
        self,
        text: str,
        character: VoiceCharacter,
        emotion: EmotionalTone
    ) -> bytes:
        """Synthesize using Azure Speech"""
        try:
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.azure_speech_config
            )
            
            ssml = self._build_azure_ssml(text, character, emotion)
            result = await asyncio.to_thread(synthesizer.speak_ssml, ssml)
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                return result.audio_data
            else:
                raise Exception(f"Azure synthesis failed: {result.reason}")
                
        except Exception as e:
            logger.error(f"❌ Azure synthesis failed: {e}")
            raise
    
    def _build_azure_ssml(
        self,
        text: str,
        character: VoiceCharacter,
        emotion: EmotionalTone
    ) -> str:
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
        
        style = azure_emotions.get(emotion, "friendly")
        
        # Adjust speech rate based on character
        rate = f"{int((character.speed_adjustment - 1) * 100):+d}%"
        
        # Adjust pitch
        pitch = f"{character.pitch_adjustment:+.1f}st"
        
        ssml = f'''
        <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" 
               xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="{character.language}">
            <voice name="{character.voice_id}">
                <mstts:express-as style="{style}">
                    <prosody rate="{rate}" pitch="{pitch}">
                        {text}
                    </prosody>
                </mstts:express-as>
            </voice>
        </speak>
        '''
        
        return ssml.strip()
    
    async def _synthesize_fallback(self, text: str) -> bytes:
        """Fallback synthesis using system TTS"""
        try:
            # Simple fallback - could use system TTS or pre-recorded audio
            logger.warning("Using fallback synthesis - limited functionality")
            
            # Generate silence as placeholder (replace with actual system TTS)
            duration = len(text) * 0.1  # Approximate duration
            sample_rate = self.config.sample_rate
            samples = int(duration * sample_rate)
            
            # Generate simple tone as placeholder
            audio = np.sin(2 * np.pi * 440 * np.linspace(0, duration, samples)) * 0.1
            audio = (audio * 32767).astype(np.int16)
            
            return audio.tobytes()
            
        except Exception as e:
            logger.error(f"❌ Fallback synthesis failed: {e}")
            return b""
    
    async def _fallback_synthesis_stream(self, text: str) -> AsyncIterator[bytes]:
        """Fallback streaming synthesis"""
        audio_data = await self._synthesize_fallback(text)
        if audio_data:
            chunk_size = self.config.chunk_size
            for i in range(0, len(audio_data), chunk_size):
                yield audio_data[i:i + chunk_size]
                await asyncio.sleep(0.01)
    
    async def _fallback_streaming_synthesis(self, context: SynthesisContext) -> AsyncIterator[bytes]:
        """Fallback streaming synthesis by chunking regular synthesis"""
        audio_data = await self.synthesize_audio(context.text, context.emotion, context.character.id)
        if audio_data:
            chunk_size = self.config.chunk_size
            for i in range(0, len(audio_data), chunk_size):
                yield audio_data[i:i + chunk_size]
                await asyncio.sleep(0.01)  # Small delay for streaming effect
    
    async def _select_character(
        self,
        character_id: Optional[str],
        language: Optional[str]
    ) -> VoiceCharacter:
        """Select appropriate voice character"""
        if character_id and character_id in self.voice_characters:
            return self.voice_characters[character_id]
        
        # Auto-select based on language
        if language:
            for character in self.voice_characters.values():
                if character.language == language:
                    return character
        
        # Return current or default character
        return self.current_character or self.voice_characters["teddy_en"]
    
    async def _apply_voice_adjustments(
        self,
        audio_data: bytes,
        character: VoiceCharacter
    ) -> bytes:
        """Apply voice adjustments (pitch, speed, volume)"""
        try:
            # Convert to audio segment for processing
            audio_segment = AudioSegment.from_raw(
                io.BytesIO(audio_data),
                sample_width=2,
                frame_rate=self.config.sample_rate,
                channels=self.config.channels
            )
            
            # Apply volume adjustment
            if character.volume_adjustment != 1.0:
                volume_change = 20 * np.log10(character.volume_adjustment)
                audio_segment = audio_segment + volume_change
            
            # Apply normalization
            audio_segment = normalize(audio_segment)
            
            # Export back to bytes
            buffer = io.BytesIO()
            audio_segment.export(buffer, format="raw")
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"❌ Voice adjustment failed: {e}")
            return audio_data
    
    def _update_stats(self, provider: VoiceProvider, processing_time: float) -> None:
        """Update performance statistics"""
        self.stats["total_syntheses"] += 1
        self.stats["total_processing_time"] += processing_time
        
        provider_name = provider.value
        if provider_name not in self.stats["provider_usage"]:
            self.stats["provider_usage"][provider_name] = 0
        self.stats["provider_usage"][provider_name] += 1
    
    def set_character(self, character_id: str) -> bool:
        """Set current voice character"""
        if character_id in self.voice_characters:
            self.current_character = self.voice_characters[character_id]
            logger.info(f"🎭 Voice character set to: {self.current_character.name}")
            return True
        return False
    
    def get_available_characters(self) -> List[Dict[str, Any]]:
        """Get list of available voice characters"""
        return [
            {
                "id": char.id,
                "name": char.name,
                "language": char.language,
                "provider": char.provider.value,
                "description": char.description
            }
            for char in self.voice_characters.values()
        ]
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        avg_processing_time = (
            self.stats["total_processing_time"] / self.stats["total_syntheses"]
            if self.stats["total_syntheses"] > 0 else 0
        )
        
        return {
            "total_syntheses": self.stats["total_syntheses"],
            "average_processing_time_s": avg_processing_time,
            "error_count": self.stats["error_count"],
            "error_rate": (
                self.stats["error_count"] / self.stats["total_syntheses"]
                if self.stats["total_syntheses"] > 0 else 0
            ),
            "provider_usage": self.stats["provider_usage"],
            "available_characters": len(self.voice_characters)
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        try:
            # Test synthesis with short text
            test_text = "Hello, I am your friendly teddy bear!"
            result = await self.synthesize_audio(test_text, EmotionalTone.FRIENDLY)
            
            return {
                "status": "healthy" if result else "degraded",
                "providers_available": {
                    "elevenlabs": self.elevenlabs_client is not None,
                    "openai": self.openai_client is not None,
                    "azure": self.azure_speech_config is not None
                },
                "characters_loaded": len(self.voice_characters),
                "current_character": self.current_character.id if self.current_character else None
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }

# ================== FACTORY FUNCTIONS ==================

async def create_synthesis_service(
    config: Optional[SynthesisConfig] = None,
    credentials: Optional[SynthesisServiceCredentials] = None
) -> ModernSynthesisService:
    """
    🏭 Factory function to create and initialize synthesis service
    
    Args:
        config: Optional synthesis configuration
        credentials: Optional service credentials for providers
        
    Returns:
        Initialized synthesis service
        
    Example:
        >>> credentials = SynthesisServiceCredentials(
        ...     elevenlabs_api_key="your_key",
        ...     openai_api_key="your_key"
        ... )
        >>> service = await create_synthesis_service(credentials=credentials)
    """
    service = ModernSynthesisService(config)
    await service.initialize(credentials=credentials)
    return service

# Legacy compatibility function with reduced arguments
async def create_synthesis_service_legacy(
    config: Optional[SynthesisConfig] = None,
    api_keys: Optional[Dict[str, str]] = None,
    azure_region: str = "eastus"
) -> ModernSynthesisService:
    """
    🔄 Legacy factory function with reduced arguments
    
    ⚠️ DEPRECATED: Use create_synthesis_service with SynthesisServiceCredentials instead
    
    Args:
        config: Optional synthesis configuration
        api_keys: Dict with keys: 'elevenlabs', 'openai', 'azure'
        azure_region: Azure region for speech services
        
    Example:
        >>> await create_synthesis_service_legacy(
        ...     api_keys={'elevenlabs': 'key1', 'openai': 'key2'}
        ... )
    """
    api_keys = api_keys or {}
    
    credentials = SynthesisServiceCredentials(
        elevenlabs_api_key=api_keys.get('elevenlabs'),
        openai_api_key=api_keys.get('openai'),
        azure_speech_key=api_keys.get('azure'),
        azure_speech_region=azure_region
    )
    return await create_synthesis_service(config=config, credentials=credentials)

# Ultra-legacy function for maximum backward compatibility (will be removed in v3.0)
async def create_synthesis_service_old(
    elevenlabs_key: Optional[str] = None,
    openai_key: Optional[str] = None,
    azure_key: Optional[str] = None,
    azure_region: str = "eastus"
) -> ModernSynthesisService:
    """
    🚨 ULTRA-DEPRECATED: Will be removed in v3.0
    Use create_synthesis_service instead
    """
    import warnings
    warnings.warn(
        "create_synthesis_service_old is deprecated and will be removed in v3.0. "
        "Use create_synthesis_service with SynthesisServiceCredentials instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    api_keys = {}
    if elevenlabs_key:
        api_keys['elevenlabs'] = elevenlabs_key
    if openai_key:
        api_keys['openai'] = openai_key
    if azure_key:
        api_keys['azure'] = azure_key
        
    return await create_synthesis_service_legacy(api_keys=api_keys, azure_region=azure_region)

# Re-export for compatibility
SynthesisService = ModernSynthesisService