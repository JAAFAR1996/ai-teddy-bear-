"""
Voice Synthesis Application Service
Handles text-to-speech conversion with emotional tones
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

import azure.cognitiveservices.speech as speechsdk
import numpy as np
from elevenlabs import ElevenLabs, generate, stream

from src.application.services.streaming_service import StreamingService
from src.domain.audio.models.voice_models import (EmotionalTone, Language,
                                                  VoiceProfile)


class VoiceSynthesisService:
    """Application service for voice synthesis operations"""

    def __init__(self, config=None):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.streaming_service: Optional[StreamingService] = None

        # Initialize synthesis clients
        self._init_synthesis_clients()

    def _init_synthesis_clients(self):
        """Initialize voice synthesis clients"""
        # ElevenLabs
        if getattr(self.config, "ELEVENLABS_API_KEY", None):
            self.elevenlabs_client = ElevenLabs(
                api_key=getattr(self.config, "ELEVENLABS_API_KEY")
            )
        else:
            self.elevenlabs_client = None

        # Azure Speech
        if getattr(self.config, "AZURE_SPEECH_KEY", None):
            speech_config = speechsdk.SpeechConfig(
                subscription=getattr(self.config, "AZURE_SPEECH_KEY"),
                region=getattr(self.config, "AZURE_SPEECH_REGION", "eastus"),
            )
            self.azure_speech_config = speech_config
        else:
            self.azure_speech_config = None

    def set_streaming_service(self, streaming_service: StreamingService):
        """Set streaming service for integration"""
        self.streaming_service = streaming_service

    async def synthesize_speech(
        self,
        text: str,
        voice_profile: VoiceProfile,
        emotion: EmotionalTone = EmotionalTone.CALM,
        stream_output: bool = True,
    ) -> Optional[bytes]:
        """
        Synthesize speech with emotional nuance

        Args:
            text: Text to convert to speech
            voice_profile: Voice profile to use
            emotion: Emotional tone
            stream_output: Whether to stream output

        Returns:
            Audio bytes if not streaming, None if streaming
        """
        try:
            if not text or not voice_profile:
                self.logger.error("Invalid text or voice profile")
                return None

            # Get voice settings for emotion
            voice_settings = voice_profile.get_voice_settings(emotion)

            # Use appropriate service based on language
            if voice_profile.language == Language.ARABIC and self.azure_speech_config:
                # Use Azure for Arabic
                audio_data = await self._synthesize_azure(text, emotion)
            elif self.elevenlabs_client:
                # Use ElevenLabs
                audio_data = await self._synthesize_elevenlabs(
                    text, voice_profile.voice_id, voice_settings, stream_output
                )
            else:
                raise ValueError("No voice synthesis service available")

            return audio_data if not stream_output else None

        except Exception as e:
            self.logger.error(f"Speech synthesis error: {e}")
            return None

    async def _synthesize_elevenlabs(
        self, text: str, voice_id: str, voice_settings, stream_output: bool
    ) -> Optional[bytes]:
        """Synthesize using ElevenLabs"""
        try:
            if stream_output and self.streaming_service:
                # Stream directly to output
                audio_stream = stream(
                    text=text,
                    voice=voice_id,
                    model="eleven_multilingual_v2",
                    voice_settings=voice_settings,
                )

                async for chunk in audio_stream:
                    await self.streaming_service.output_buffer.write(chunk)

                return None
            else:
                # Generate complete audio
                audio = generate(
                    text=text,
                    voice=voice_id,
                    model="eleven_multilingual_v2",
                    voice_settings=voice_settings,
                )
                return audio

        except Exception as e:
            self.logger.error(f"ElevenLabs synthesis error: {e}")
            return None

    async def _synthesize_azure(self, text: str, emotion: EmotionalTone) -> bytes:
        """Synthesize using Azure Speech Services"""
        try:
            # Configure voice name based on emotion
            voice_name = self._get_azure_voice_name(emotion)
            self.azure_speech_config.speech_synthesis_voice_name = voice_name

            # Create synthesizer
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.azure_speech_config
            )

            # Generate speech
            result = synthesizer.speak_text_async(text).get()

            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                return result.audio_data
            else:
                self.logger.error(f"Azure synthesis failed: {result.reason}")
                return None

        except Exception as e:
            self.logger.error(f"Azure synthesis error: {e}")
            return None

    def _get_azure_voice_name(self, emotion: EmotionalTone) -> str:
        """Get Azure voice name based on emotion"""
        voice_mapping = {
            EmotionalTone.HAPPY: "ar-SA-ZariyahNeural",
            EmotionalTone.CALM: "ar-SA-HamedNeural",
            EmotionalTone.EXCITED: "ar-SA-ZariyahNeural",
            EmotionalTone.SLEEPY: "ar-SA-HamedNeural",
            EmotionalTone.STORYTELLING: "ar-SA-ZariyahNeural",
        }

        return voice_mapping.get(emotion, "ar-SA-ZariyahNeural")

    async def test_synthesis(self, text: str, voice_profile: VoiceProfile) -> bool:
        """Test voice synthesis capability"""
        try:
            audio_data = await self.synthesize_speech(
                text, voice_profile, EmotionalTone.HAPPY, stream_output=False
            )
            return audio_data is not None

        except Exception as e:
            self.logger.error(f"Synthesis test failed: {e}")
            return False
