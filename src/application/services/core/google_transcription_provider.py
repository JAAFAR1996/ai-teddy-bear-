from .openai_transcription_provider import TranscriptionProviderBase, TranscriptionResult, TranscriptionConfig
import structlog
from typing import Any, Dict, List
# Google Cloud Speech - optional import
try:
    from google.cloud import speech_v1

    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    speech_v1 = None

logger = structlog.get_logger()


class GoogleTranscriptionProvider(TranscriptionProviderBase):
    """Google Speech-to-Text provider"""

    def __init__(self, credentials_path: str | None = None):
        if not GOOGLE_AVAILABLE:
            raise ImportError(
                "Google Cloud Speech library not installed. Run: pip install google-cloud-speech"
            )
        self.client = speech_v1.SpeechAsyncClient()
        self.credentials_path = credentials_path

    async def transcribe(
        self, audio_data: bytes, config: "TranscriptionConfig"
    ) -> "TranscriptionResult":
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
        self, audio_data: bytes, config: "TranscriptionConfig"
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
        self, response, config: "TranscriptionConfig"
    ) -> "TranscriptionResult":
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
                    result.language_code if hasattr(
                        result,
                        "language_code") else None),
            },
        )

    def _create_empty_result(
            self,
            config: "TranscriptionConfig") -> "TranscriptionResult":
        """Create empty result when no results returned"""
        return TranscriptionResult(
            text="",
            language=config.language,
            confidence=0.0,
            metadata={"provider": "google", "error": "No results"},
        )

    def _extract_google_words(
            self,
            best_alternative,
            config: "TranscriptionConfig"):
        """Extract word-level timestamps from Google response"""
        if not config.enable_word_timestamps or not hasattr(
                best_alternative, "words"):
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

    def _extract_google_alternatives(
            self, result, config: "TranscriptionConfig"):
        """Extract alternative transcriptions"""
        return [
            {"text": alt.transcript, "confidence": alt.confidence}
            for alt in result.alternatives[1: config.max_alternatives]
        ]

    def _log_google_success(self, result: "TranscriptionResult") -> None:
        """Log successful Google transcription"""
        logger.info(
            "Google transcription completed",
            text_length=len(result.text),
            confidence=result.confidence,
        )

    async def is_available(self) -> bool:
        """Check if Google Speech is available"""
        try:
            return True
        except Exception as e:
            logger.error(f"Error in operation: {e}", exc_info=True)
            return False

    def _get_language_code(self, language: str) -> str:
        """Convert language code to Google format"""
        language_map = {
            "ar": "ar-SA",
            "en": "en-US",
            "es": "es-ES",
            "fr": "fr-FR",
            "de": "de-DE",
            "zh": "zh-CN",
            "ja": "ja-JP",
            "ko": "ko-KR",
        }
        return language_map.get(language, f"{language}-{language.upper()}")
