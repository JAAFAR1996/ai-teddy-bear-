"""
🎤 Voice Service - Clean Architecture Implementation
Enterprise-grade voice processing with async operations
"""

import asyncio
import logging
import base64
import tempfile
import os
from typing import Optional, Dict, Any
from pathlib import Path
import aiofiles
import numpy as np

from elevenlabs import VoiceSettings
from elevenlabs.client import AsyncElevenLabs
    import whisper
from gtts import gTTS
    import azure.cognitiveservices.speech as speechsdk

from core.domain.value_objects import Language, EmotionalTone
from core.infrastructure.config import Settings
from core.infrastructure.caching.cache_service import CacheService
from core.infrastructure.monitoring.metrics import metrics_collector

logger = logging.getLogger(__name__)

# ================== VOICE SERVICE INTERFACE ==================

class IVoiceService:
    """Voice Service interface (Port)"""
    
    async def transcribe_audio(
        self,
        audio_data: str,
        language: str = "Arabic"
    ) -> Optional[str]:
        """Transcribe audio to text"""
        raise NotImplementedError
    
    async def synthesize_speech(
        self,
        text: str,
        emotion: str = "neutral",
        language: str = "Arabic"
    ) -> str:
        """Synthesize text to speech"""
        raise NotImplementedError

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
        
        async with aiofiles.open(temp_path, 'wb') as f:
            await f.write(data)
        
        return temp_path
    
    @staticmethod
    async def convert_mp3_to_wav(mp3_path: str) -> str:
        """Convert MP3 to WAV asynchronously using ffmpeg"""
        wav_path = mp3_path.replace('.mp3', '.wav')
        
        # Run ffmpeg in executor to avoid blocking
        loop = asyncio.get_event_loop()
        proc = await asyncio.create_subprocess_exec(
            'ffmpeg', '-i', mp3_path, '-ar', '16000', '-ac', '1', wav_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await proc.communicate()
        
        if proc.returncode != 0:
            logger.error(f"FFmpeg conversion failed: {stderr.decode()}")
            raise RuntimeError("Audio conversion failed")
        
        return wav_path

# ================== MULTI-PROVIDER VOICE SERVICE ==================

class MultiProviderVoiceService(IVoiceService):
    """Voice service supporting multiple providers"""
    
    def __init__(self, settings: Settings, cache_service: CacheService):
        self.settings = settings
        self.cache = cache_service
        self.audio_processor = AsyncAudioProcessor()
        
        # Initialize providers
        self._init_whisper()
        self._init_elevenlabs()
        self._init_azure()
    
    def _init_whisper(self):
        """Initialize Whisper model"""
        try:
            self.whisper_model = whisper.load_model("base")
            logger.info("✅ Whisper model loaded")
            except Exception as e:
            logger.error(f"Failed to load Whisper: {str(e)}")
                self.whisper_model = None
        
    def _init_elevenlabs(self):
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
    
    def _init_azure(self):
        """Initialize Azure Speech services"""
        try:
            if self.settings.azure_speech_key and self.settings.azure_speech_region:
                self.azure_speech_config = speechsdk.SpeechConfig(
                    subscription=self.settings.azure_speech_key,
                    region=self.settings.azure_speech_region
                )
                logger.info("✅ Azure Speech initialized")
            else:
                self.azure_speech_config = None
        except Exception as e:
            logger.error(f"Failed to initialize Azure Speech: {str(e)}")
            self.azure_speech_config = None
    
    async def transcribe_audio(
        self, 
        audio_data: str,
        language: str = "Arabic"
    ) -> Optional[str]:
        """Transcribe audio with fallback providers"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Decode audio data
            audio_bytes = await self.audio_processor.decode_base64_audio(audio_data)
            
            # Check cache
            cache_key = f"transcription_{hash(audio_data[:100])}"
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                return cached_result
            
            # Save to temporary file
            temp_mp3 = await self.audio_processor.save_temp_file(audio_bytes, '.mp3')
            
            try:
                # Convert to WAV for Whisper
                temp_wav = await self.audio_processor.convert_mp3_to_wav(temp_mp3)
                
                # Try providers in order
                transcription = None
                
                # 1. Try Whisper (best quality)
                if self.whisper_model and not transcription:
                    transcription = await self._transcribe_with_whisper(temp_wav, language)
                
                # 2. Try Azure (good quality)
                if self.azure_speech_config and not transcription:
                    transcription = await self._transcribe_with_azure(temp_wav, language)
                
                # 3. Fallback to basic recognition
                if not transcription:
                    transcription = await self._transcribe_fallback(temp_wav, language)
                
                if transcription:
                    # Clean and cache result
                    transcription = self._clean_transcription(transcription)
                    await self.cache.set(cache_key, transcription, ttl=3600)
                    
                    # Record metrics
                    processing_time = asyncio.get_event_loop().time() - start_time
                    await metrics_collector.record_metric(
                        "voice_transcription_time",
                        processing_time
                    )
                
                return transcription
                
            finally:
                # Cleanup temp files
                await self._cleanup_files([temp_mp3, temp_wav])
                
        except Exception as e:
            logger.error(f"Transcription error: {str(e)}", exc_info=True)
            return None
    
    async def _transcribe_with_whisper(
        self,
        audio_path: str,
        language: str
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
                    audio_path,
                    language=whisper_lang,
                    task="transcribe",
                    fp16=False
                )
            )
            
            return result.get("text", "").strip()
            
        except Exception as e:
            logger.error(f"Whisper transcription failed: {str(e)}")
            return None
    
    async def _transcribe_with_azure(
        self,
        audio_path: str,
        language: str
    ) -> Optional[str]:
        """Transcribe using Azure Speech Services"""
        try:
            # Configure language
            speech_lang = "ar-SA" if language == "Arabic" else "en-US"
            self.azure_speech_config.speech_recognition_language = speech_lang
            
            # Create recognizer
            audio_config = speechsdk.AudioConfig(filename=audio_path)
            recognizer = speechsdk.SpeechRecognizer(
                speech_config=self.azure_speech_config,
                audio_config=audio_config
            )
            
            # Async recognition
            future = asyncio.Future()
            
            def handle_result(evt):
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
        self,
        audio_path: str,
        language: str
    ) -> Optional[str]:
        """Fallback transcription using speech_recognition"""
        try:
            import speech_recognition as sr
            
            loop = asyncio.get_event_loop()
            
            def transcribe():
                r = sr.Recognizer()
                with sr.AudioFile(audio_path) as source:
                    audio = r.record(source)
                    
                lang_code = "ar-SA" if language == "Arabic" else "en-US"
                try:
                    return r.recognize_google(audio, language=lang_code)
                except Exception as e:
    logger.error(f"Error in operation: {e}", exc_info=True)Exception as e:
    logger.error(f"Error in operation: {e}", exc_info=True)                    return None
            
            return await loop.run_in_executor(None, transcribe)
            
        except Exception as e:
            logger.error(f"Fallback transcription failed: {str(e)}")
            return None
    
    async def synthesize_speech(
        self,
        text: str,
        emotion: str = "neutral",
        language: str = "Arabic"
    ) -> str:
        """Synthesize speech with emotion support"""
        try:
            # Check cache
            cache_key = f"tts_{hash(f'{text}_{emotion}_{language}')}"
            cached_audio = await self.cache.get(cache_key)
            if cached_audio:
                return cached_audio
            
            # Try providers in order
            audio_base64 = None
            
            # 1. Try ElevenLabs (best quality + emotion)
            if self.elevenlabs_client and not audio_base64:
                audio_base64 = await self._synthesize_with_elevenlabs(text, emotion)
            
            # 2. Try Azure (good quality)
            if self.azure_speech_config and not audio_base64:
                audio_base64 = await self._synthesize_with_azure(text, emotion, language)
            
            # 3. Fallback to gTTS
            if not audio_base64:
                audio_base64 = await self._synthesize_with_gtts(text, language)
            
            if audio_base64:
                # Cache result
                await self.cache.set(cache_key, audio_base64, ttl=86400)  # 24 hours
            
            return audio_base64 or ""
                        
        except Exception as e:
            logger.error(f"Speech synthesis error: {str(e)}", exc_info=True)
            return ""
    
    async def _synthesize_with_elevenlabs(
        self, 
        text: str,
        emotion: str
    ) -> Optional[str]:
        """Synthesize using ElevenLabs with emotion"""
        try:
            # Map emotion to voice settings
            voice_settings = self._get_elevenlabs_voice_settings(emotion)
            
            # Generate audio
            audio_bytes = await self.elevenlabs_client.generate(
                text=text,
                voice="Rachel",  # Or configured voice
                voice_settings=voice_settings
            )
            
            # Convert to base64
            return base64.b64encode(audio_bytes).decode('utf-8')
                    
        except Exception as e:
            logger.error(f"ElevenLabs synthesis failed: {str(e)}")
            return None
    
    async def _synthesize_with_azure(
        self,
        text: str,
        emotion: str,
        language: str
    ) -> Optional[str]:
        """Synthesize using Azure with SSML for emotion"""
        try:
            # Configure voice
            voice_name = "ar-SA-ZariyahNeural" if language == "Arabic" else "en-US-JennyNeural"
            
            # Build SSML with emotion
            ssml = self._build_azure_ssml(text, emotion, voice_name)
            
            # Create synthesizer
            audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=False)
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.azure_speech_config,
                audio_config=audio_config
            )
            
            # Async synthesis
            future = asyncio.Future()
            
            def handle_result(evt):
                if evt.result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                    audio_data = evt.result.audio_data
                    future.set_result(base64.b64encode(audio_data).decode('utf-8'))
                else:
                    future.set_result(None)
            
            synthesizer.synthesis_completed.connect(handle_result)
            
            # Start synthesis
            synthesizer.speak_ssml_async(ssml)
            return await future
                
        except Exception as e:
            logger.error(f"Azure synthesis failed: {str(e)}")
            return None
    
    async def _synthesize_with_gtts(
        self,
        text: str,
        language: str
    ) -> Optional[str]:
        """Fallback synthesis using gTTS"""
        try:
            loop = asyncio.get_event_loop()
            
            # Map language
            lang_code = "ar" if language == "Arabic" else "en"
            
            # Generate in executor
            def generate():
                tts = gTTS(text=text, lang=lang_code, slow=False)
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
                tts.save(temp_file.name)
                
                with open(temp_file.name, 'rb') as f:
                    audio_data = f.read()
                
                os.unlink(temp_file.name)
                return base64.b64encode(audio_data).decode('utf-8')
            
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
            "neutral": {"stability": 0.5, "similarity_boost": 0.75, "style": 0.5}
        }
        
        settings = emotion_settings.get(emotion, emotion_settings["neutral"])
        return VoiceSettings(**settings)
    
    def _build_azure_ssml(
        self,
        text: str,
        emotion: str,
        voice_name: str
    ) -> str:
        """Build SSML for Azure with emotion"""
        emotion_styles = {
            "happy": "cheerful",
            "sad": "sad",
            "excited": "excited",
            "angry": "angry",
            "calm": "calm",
            "neutral": "neutral"
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
        text = ' '.join(text.split())
        
        # Fix common Arabic issues
        text = text.replace('إ', 'ا')  # Normalize hamza
        
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

# ================== FACTORY ==================

class VoiceServiceFactory:
    """Factory for creating voice service instances"""
    
    @staticmethod
    def create(
        settings: Settings,
        cache_service: CacheService
    ) -> IVoiceService:
        """Create voice service"""
        return MultiProviderVoiceService(settings, cache_service)

# Re-export the main service
VoiceService = IVoiceService 