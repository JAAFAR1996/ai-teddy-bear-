"""
🧸 AI Teddy Bear - Voice Service
خدمة معالجة الصوت المحسنة
"""

import asyncio
import logging
import base64
import tempfile
import wave
import io
from typing import Optional, Dict, Any, Tuple
from pathlib import Path
import json

import numpy as np
from pydub import AudioSegment
from pydub.playback import play
import speech_recognition as sr
from gtts import gTTS

from ..infrastructure.config import Settings
from ..domain.models import AudioData, Language, EmotionType


logger = logging.getLogger(__name__)


class VoiceService:
    """Voice processing service with STT/TTS capabilities"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.recognizer = sr.Recognizer()
        self.whisper_model = None
        self.elevenlabs_client = None
        self.azure_client = None
        self._initialize()
    
    def _initialize(self):
        """Initialize voice processing engines"""
        # Initialize Whisper
        self._init_whisper()
        
        # Initialize ElevenLabs
        self._init_elevenlabs()
        
        # Initialize Azure Speech
        self._init_azure()
        
        logger.info("Voice service initialized")
    
    def _init_whisper(self):
        """Initialize Whisper model"""
        try:
            import whisper
            self.whisper_model = whisper.load_model(
                self.settings.whisper_model,
                device="cpu"
            )
            logger.info(f"Whisper model '{self.settings.whisper_model}' loaded")
        except Exception as e:
            logger.warning(f"Whisper initialization failed: {e}")
            self.whisper_model = None
    
    def _init_elevenlabs(self):
        """Initialize ElevenLabs client"""
        try:
            if self.settings.elevenlabs_api_key:
                from elevenlabs import AsyncElevenLabs
                self.elevenlabs_client = AsyncElevenLabs(
                    api_key=self.settings.elevenlabs_api_key.get_secret_value()
                )
                logger.info("ElevenLabs client initialized")
        except Exception as e:
            logger.warning(f"ElevenLabs initialization failed: {e}")
            self.elevenlabs_client = None
    
    def _init_azure(self):
        """Initialize Azure Speech Services"""
        try:
            if self.settings.azure_speech_key:
                import azure.cognitiveservices.speech as speechsdk
                
                speech_config = speechsdk.SpeechConfig(
                    subscription=self.settings.azure_speech_key.get_secret_value(),
                    region=self.settings.azure_speech_region
                )
                
                # Arabic voice configuration
                speech_config.speech_synthesis_voice_name = "ar-SA-HamedNeural"
                speech_config.speech_recognition_language = "ar-SA"
                
                self.azure_client = {
                    "config": speech_config,
                    "recognizer": speechsdk.SpeechRecognizer(speech_config=speech_config),
                    "synthesizer": speechsdk.SpeechSynthesizer(speech_config=speech_config)
                }
                
                logger.info("Azure Speech Services initialized")
        except Exception as e:
            logger.warning(f"Azure Speech initialization failed: {e}")
            self.azure_client = None
    
    async def process_audio(self, audio_data: AudioData) -> Tuple[str, Dict[str, Any]]:
        """
        Process audio data and return transcription with metadata
        
        Returns:
            Tuple of (transcribed_text, metadata)
        """
        try:
            # Decode audio
            audio_bytes = base64.b64decode(audio_data.audio_base64)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=f".{audio_data.format}"
            ) as tmp_file:
                tmp_file.write(audio_bytes)
                tmp_path = tmp_file.name
            
            # Process based on format
            if audio_data.format == "mp3":
                transcription, metadata = await self._process_mp3(tmp_path)
            elif audio_data.format == "wav":
                transcription, metadata = await self._process_wav(tmp_path)
            else:
                transcription, metadata = await self._process_generic(tmp_path)
            
            # Clean up
            Path(tmp_path).unlink(missing_ok=True)
            
            # Add audio info to metadata
            metadata.update({
                "format": audio_data.format,
                "duration": audio_data.duration_seconds,
                "size_bytes": audio_data.size_bytes,
                "sample_rate": audio_data.sample_rate
            })
            
            return transcription, metadata
            
        except Exception as e:
            logger.error(f"Audio processing failed: {e}")
            return "", {"error": str(e)}
    
    async def _process_mp3(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """Process MP3 audio file"""
        try:
            # Convert MP3 to WAV for processing
            audio = AudioSegment.from_mp3(file_path)
            
            # Convert to mono and set sample rate
            audio = audio.set_channels(1)
            audio = audio.set_frame_rate(self.settings.audio_sample_rate)
            
            # Export to WAV
            wav_path = file_path.replace(".mp3", ".wav")
            audio.export(wav_path, format="wav")
            
            # Process WAV
            transcription, metadata = await self._process_wav(wav_path)
            
            # Clean up
            Path(wav_path).unlink(missing_ok=True)
            
            # Add MP3-specific metadata
            metadata["original_format"] = "mp3"
            metadata["compression_ratio"] = len(open(file_path, 'rb').read()) / len(audio.raw_data)
            
            return transcription, metadata
            
        except Exception as e:
            logger.error(f"MP3 processing failed: {e}")
            return "", {"error": str(e)}
    
    async def _process_wav(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """Process WAV audio file"""
        # Try multiple STT engines in order of preference
        
        # 1. Try Whisper (best quality)
        if self.whisper_model:
            try:
                result = await self._transcribe_with_whisper(file_path)
                if result[0]:
                    return result
            except Exception as e:
                logger.warning(f"Whisper transcription failed: {e}")
        
        # 2. Try Azure (good quality, cloud)
        if self.azure_client:
            try:
                result = await self._transcribe_with_azure(file_path)
                if result[0]:
                    return result
            except Exception as e:
                logger.warning(f"Azure transcription failed: {e}")
        
        # 3. Fallback to Google Speech Recognition
        try:
            result = await self._transcribe_with_google(file_path)
            return result
        except Exception as e:
            logger.error(f"All transcription methods failed: {e}")
            return "", {"error": "Transcription failed"}
    
    async def _process_generic(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """Process generic audio format"""
        try:
            # Try to load with pydub
            audio = AudioSegment.from_file(file_path)
            
            # Convert to WAV
            wav_path = file_path + ".wav"
            audio.export(wav_path, format="wav")
            
            # Process WAV
            result = await self._process_wav(wav_path)
            
            # Clean up
            Path(wav_path).unlink(missing_ok=True)
            
            return result
            
        except Exception as e:
            logger.error(f"Generic audio processing failed: {e}")
            return "", {"error": str(e)}
    
    async def _transcribe_with_whisper(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """Transcribe using Whisper"""
        loop = asyncio.get_event_loop()
        
        def transcribe():
            result = self.whisper_model.transcribe(
                file_path,
                language=self.settings.stt_language,
                task="transcribe",
                fp16=False
            )
            return result
        
        # Run in thread pool
        result = await loop.run_in_executor(None, transcribe)
        
        text = result["text"].strip()
        
        metadata = {
            "engine": "whisper",
            "language": result.get("language", self.settings.stt_language),
            "segments": len(result.get("segments", [])),
            "confidence": 0.95  # Whisper doesn't provide confidence
        }
        
        return text, metadata
    
    async def _transcribe_with_azure(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """Transcribe using Azure Speech Services"""
        recognizer = self.azure_client["recognizer"]
        
        # Configure audio input
        audio_config = speechsdk.AudioConfig(filename=file_path)
        recognizer = speechsdk.SpeechRecognizer(
            speech_config=self.azure_client["config"],
            audio_config=audio_config
        )
        
        # Recognize
        result = await asyncio.get_event_loop().run_in_executor(
            None, recognizer.recognize_once
        )
        
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            text = result.text
            metadata = {
                "engine": "azure",
                "language": self.settings.stt_language,
                "confidence": result.properties.get(
                    speechsdk.PropertyId.SpeechServiceResponse_JsonResult, 
                    {}
                ).get("NBest", [{}])[0].get("Confidence", 0.0)
            }
            return text, metadata
        else:
            return "", {"error": f"Azure recognition failed: {result.reason}"}
    
    async def _transcribe_with_google(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """Transcribe using Google Speech Recognition"""
        with sr.AudioFile(file_path) as source:
            audio = self.recognizer.record(source)
        
        try:
            # Map language codes
            lang_map = {
                "ar": "ar-SA",
                "en": "en-US",
                "es": "es-ES",
                "fr": "fr-FR",
                "de": "de-DE"
            }
            
            language = lang_map.get(
                self.settings.stt_language,
                self.settings.stt_language
            )
            
            text = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.recognizer.recognize_google(
                    audio,
                    language=language,
                    show_all=False
                )
            )
            
            metadata = {
                "engine": "google",
                "language": language,
                "confidence": 0.8  # Google doesn't provide confidence in free tier
            }
            
            return text, metadata
            
        except sr.UnknownValueError:
            return "", {"error": "Could not understand audio"}
        except sr.RequestError as e:
            return "", {"error": f"Google API error: {e}"}
    
    async def synthesize_speech(
        self,
        text: str,
        language: Language = Language.ARABIC,
        voice_settings: Optional[Dict[str, Any]] = None,
        emotion: Optional[EmotionType] = None
    ) -> Optional[AudioData]:
        """
        Synthesize speech from text
        
        Returns:
            AudioData object with synthesized speech
        """
        try:
            # Select voice based on emotion
            if emotion and voice_settings:
                voice_id = self._select_voice_for_emotion(emotion, voice_settings)
            else:
                voice_id = self.settings.tts_voice_id
            
            # Try ElevenLabs first (best quality)
            if self.elevenlabs_client:
                audio_data = await self._synthesize_with_elevenlabs(
                    text, language, voice_id, voice_settings
                )
                if audio_data:
                    return audio_data
            
            # Try Azure (good quality)
            if self.azure_client:
                audio_data = await self._synthesize_with_azure(
                    text, language, voice_settings
                )
                if audio_data:
                    return audio_data
            
            # Fallback to gTTS
            audio_data = await self._synthesize_with_gtts(text, language)
            return audio_data
            
        except Exception as e:
            logger.error(f"Speech synthesis failed: {e}")
            return None
    
    async def _synthesize_with_elevenlabs(
        self,
        text: str,
        language: Language,
        voice_id: str,
        voice_settings: Optional[Dict[str, Any]] = None
    ) -> Optional[AudioData]:
        """Synthesize using ElevenLabs"""
        try:
            from elevenlabs import Voice, VoiceSettings
            
            # Configure voice settings
            settings = VoiceSettings(
                stability=voice_settings.get("stability", 0.5),
                similarity_boost=voice_settings.get("similarity_boost", 0.75),
                style=voice_settings.get("style", 0.0),
                use_speaker_boost=True
            )
            
            # Generate audio
            audio = await self.elevenlabs_client.generate(
                text=text,
                voice=Voice(
                    voice_id=voice_id,
                    settings=settings
                ),
                model="eleven_multilingual_v2" if language != Language.ENGLISH else "eleven_monolingual_v1"
            )
            
            # Convert to AudioData
            audio_bytes = b"".join(audio)
            
            return AudioData(
                audio_base64=base64.b64encode(audio_bytes).decode('utf-8'),
                format="mp3",
                sample_rate=44100,
                size_bytes=len(audio_bytes)
            )
            
        except Exception as e:
            logger.error(f"ElevenLabs synthesis failed: {e}")
            return None
    
    async def _synthesize_with_azure(
        self,
        text: str,
        language: Language,
        voice_settings: Optional[Dict[str, Any]] = None
    ) -> Optional[AudioData]:
        """Synthesize using Azure Speech Services"""
        try:
            synthesizer = self.azure_client["synthesizer"]
            
            # Select voice based on language
            voice_map = {
                Language.ARABIC: "ar-SA-HamedNeural",
                Language.ENGLISH: "en-US-JennyNeural",
                Language.SPANISH: "es-ES-ElviraNeural",
                Language.FRENCH: "fr-FR-DeniseNeural",
                Language.GERMAN: "de-DE-KatjaNeural"
            }
            
            # Configure SSML for emotion and style
            ssml = f"""
            <speak version='1.0' xml:lang='{language.value}'>
                <voice name='{voice_map.get(language, "ar-SA-HamedNeural")}'>
                    <prosody rate='{voice_settings.get("speed", 1.0)}' 
                             pitch='{voice_settings.get("pitch", 1.0)}' 
                             volume='{voice_settings.get("volume", 1.0)}'>
                        {text}
                    </prosody>
                </voice>
            </speak>
            """
            
            # Synthesize
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                synthesizer.speak_ssml,
                ssml
            )
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                audio_bytes = result.audio_data
                
                return AudioData(
                    audio_base64=base64.b64encode(audio_bytes).decode('utf-8'),
                    format="wav",
                    sample_rate=16000,
                    size_bytes=len(audio_bytes)
                )
            else:
                logger.error(f"Azure synthesis failed: {result.reason}")
                return None
                
        except Exception as e:
            logger.error(f"Azure synthesis failed: {e}")
            return None
    
    async def _synthesize_with_gtts(
        self,
        text: str,
        language: Language
    ) -> Optional[AudioData]:
        """Synthesize using gTTS (fallback)"""
        try:
            # Create gTTS object
            tts = gTTS(
                text=text,
                lang=language.value,
                slow=False
            )
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                tts.save(tmp_file.name)
                tmp_path = tmp_file.name
            
            # Read audio data
            with open(tmp_path, 'rb') as f:
                audio_bytes = f.read()
            
            # Clean up
            Path(tmp_path).unlink(missing_ok=True)
            
            return AudioData(
                audio_base64=base64.b64encode(audio_bytes).decode('utf-8'),
                format="mp3",
                sample_rate=22050,
                size_bytes=len(audio_bytes)
            )
            
        except Exception as e:
            logger.error(f"gTTS synthesis failed: {e}")
            return None
    
    def _select_voice_for_emotion(
        self,
        emotion: EmotionType,
        voice_settings: Dict[str, Any]
    ) -> str:
        """Select appropriate voice ID based on emotion"""
        # Map emotions to voice characteristics
        emotion_voices = {
            EmotionType.HAPPY: voice_settings.get("happy_voice", self.settings.tts_voice_id),
            EmotionType.SAD: voice_settings.get("sad_voice", self.settings.tts_voice_id),
            EmotionType.EXCITED: voice_settings.get("excited_voice", self.settings.tts_voice_id),
            EmotionType.NEUTRAL: self.settings.tts_voice_id
        }
        
        return emotion_voices.get(emotion, self.settings.tts_voice_id)
    
    async def extract_audio_features(
        self,
        audio_data: AudioData
    ) -> Dict[str, float]:
        """Extract audio features for analysis"""
        try:
            # Decode audio
            audio_bytes = base64.b64decode(audio_data.audio_base64)
            
            # Load audio
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{audio_data.format}") as tmp:
                tmp.write(audio_bytes)
                tmp_path = tmp.name
            
            # Load with pydub
            audio = AudioSegment.from_file(tmp_path)
            
            # Extract features
            features = {
                "duration_seconds": len(audio) / 1000.0,
                "dBFS": audio.dBFS,
                "max_dBFS": audio.max_dBFS,
                "rms": audio.rms,
                "channels": audio.channels,
                "frame_rate": audio.frame_rate,
                "frame_width": audio.frame_width,
            }
            
            # Clean up
            Path(tmp_path).unlink(missing_ok=True)
            
            return features
            
        except Exception as e:
            logger.error(f"Feature extraction failed: {e}")
            return {}
