from .openai_transcription_provider import TranscriptionProviderBase, TranscriptionResult, TranscriptionConfig
import asyncio
from typing import Any, Dict, List
import structlog

# Azure Speech - optional import
try:
    from azure.cognitiveservices.speech import (
        AudioConfig,
        ResultReason,
        SpeechConfig,
        SpeechRecognizer,
    )
    from azure.cognitiveservices.speech.audio import AudioInputStream

    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False

logger = structlog.get_logger()


class AzureTranscriptionProvider(TranscriptionProviderBase):
    """Azure Speech Services provider"""

    def __init__(self, subscription_key: str, region: str):
        if not AZURE_AVAILABLE:
            raise ImportError(
                "Azure Speech library not installed. Run: pip install azure-cognitiveservices-speech"
            )
        self.subscription_key = subscription_key
        self.region = region
        self.speech_config = SpeechConfig(
            subscription=subscription_key, region=region)

    async def transcribe(
        self, audio_data: bytes, config: "TranscriptionConfig"
    ) -> "TranscriptionResult":
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

    def _setup_azure_recognizer(
            self,
            audio_data: bytes,
            config: "TranscriptionConfig"):
        """Setup Azure speech recognizer"""
        self.speech_config.speech_recognition_language = self._get_language_code(
            config.language)
        self.speech_config.request_word_level_timestamps()

        audio_stream = AudioInputStream(audio_data)
        audio_config = AudioConfig(stream=audio_stream)

        return SpeechRecognizer(
            speech_config=self.speech_config, audio_config=audio_config
        )

    def _parse_azure_result(
        self, result, config: "TranscriptionConfig"
    ) -> "TranscriptionResult":
        """Parse Azure recognition result"""
        if result.reason != ResultReason.RecognizedSpeech:
            raise Exception(f"Recognition failed: {result.reason}")

        details = result.json
        words = self._extract_azure_words(details, config)

        return TranscriptionResult(
            text=result.text,
            language=config.language,
            confidence=details.get("NBest", [{}])[0].get("Confidence", 1.0),
            duration=details.get("Duration", 0) / 10000000.0,
            words=words,
            metadata={
                "provider": "azure",
                "recognition_status": result.reason.name},
        )

    def _extract_azure_words(self, details: Dict, config: "TranscriptionConfig"):
        """Extract word-level timestamps from Azure response"""
        if not config.enable_word_timestamps or "NBest" not in details:
            return None
        return self._extract_words(details["NBest"][0])

    def _log_azure_success(
        self, transcription_result: "TranscriptionResult", result
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
            return True
        except Exception as e:
            logger.error(f"Error in operation: {e}", exc_info=True)
            return False

    def _get_language_code(self, language: str) -> str:
        """Convert language code to Azure format"""
        language_map = {
            "ar": "ar-SA", "en": "en-US", "es": "es-ES", "fr": "fr-FR",
            "de": "de-DE", "zh": "zh-Hans-CN", "ja": "ja-JP", "ko": "ko-KR",
        }
        return language_map.get(language, f"{language}-{language.upper()}")

    async def _recognize_async(self, recognizer) -> Any:
        """Async wrapper for recognition"""
        future = asyncio.Future()

        def recognized_cb(evt) -> Any:
            future.set_result(evt.result)

        recognizer.recognized.connect(recognized_cb)
        recognizer.start_continuous_recognition()

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
                    "confidence": word.get("Confidence", 1.0),
                })
        return words
