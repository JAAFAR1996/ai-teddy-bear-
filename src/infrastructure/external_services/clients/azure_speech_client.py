"""
Azure Speech Client Infrastructure
Handles Azure Cognitive Services Speech API integration
"""

import logging
from typing import Dict, Optional

import azure.cognitiveservices.speech as speechsdk


class AzureSpeechClient:
    """Infrastructure client for Azure Speech Services"""

    def __init__(self, subscription_key: str, region: str = "eastus"):
        self.speech_config = speechsdk.SpeechConfig(
            subscription=subscription_key, region=region
        )
        self.logger = logging.getLogger(self.__class__.__name__)

    async def synthesize_speech(
        self,
        text: str,
        voice_name: str = "ar-SA-ZariyahNeural",
        output_format: str = "Audio16Khz32KBitRateMonoMp3",
    ) -> Optional[bytes]:
        """Synthesize speech using Azure"""
        try:
            # Configure voice and format
            self.speech_config.speech_synthesis_voice_name = voice_name
            self.speech_config.set_speech_synthesis_output_format(
                getattr(speechsdk.SpeechSynthesisOutputFormat, output_format)
            )

            # Create synthesizer
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.speech_config)

            # Generate speech
            result = synthesizer.speak_text_async(text).get()

            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                return result.audio_data
            else:
                self.logger.error(f"Azure synthesis failed: {result.reason}")
                return None

        except Exception as e:
            self.logger.error(f"Azure speech synthesis error: {e}")
            return None

    async def recognize_speech(
        self, audio_data: bytes, language: str = "ar-SA"
    ) -> Optional[Dict]:
        """Recognize speech from audio data"""
        try:
            # Configure recognition
            self.speech_config.speech_recognition_language = language

            # Create recognizer with audio data
            audio_stream = speechsdk.audio.PushAudioInputStream()
            audio_config = speechsdk.audio.AudioConfig(stream=audio_stream)

            recognizer = speechsdk.SpeechRecognizer(
                speech_config=self.speech_config, audio_config=audio_config
            )

            # Push audio data and recognize
            audio_stream.write(audio_data)
            audio_stream.close()

            result = recognizer.recognize_once()

            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                return {
                    "text": result.text, "confidence": (
                        result.confidence if hasattr(
                            result, "confidence") else 0.9), }
            else:
                self.logger.error(f"Azure recognition failed: {result.reason}")
                return None

        except Exception as e:
            self.logger.error(f"Azure speech recognition error: {e}")
            return None

    async def get_available_voices(self, language: str = "ar") -> list:
        """Get available voices for language"""
        try:
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.speech_config)

            result = synthesizer.get_voices_async(language).get()

            if result.reason == speechsdk.ResultReason.VoicesListRetrieved:
                return [voice.name for voice in result.voices]
            else:
                return []

        except Exception as e:
            self.logger.error(f"Failed to get Azure voices: {e}")
            return []

    def is_available(self) -> bool:
        """Check if service is available"""
        try:
            # Simple health check
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.speech_config)
            result = synthesizer.get_voices_async().get()
            return result.reason == speechsdk.ResultReason.VoicesListRetrieved

        # FIXME: replace with specific exception
except Exception as exc:
    return False
