import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

import structlog

logger = structlog.get_logger(__name__)

import os
import sqlite3

import azure.cognitiveservices.speech as speechsdk

from src.core.domain.entities.transcription import Transcription
from src.infrastructure.persistence.transcription_sqlite_repository import TranscriptionSQLiteRepository


class AzureSpeechToTextService:
    def __init__(self, db_path, subscription_key=None, region=None):
        # Try to get credentials from environment variables if not provided
        self.subscription_key = subscription_key or os.getenv(
            'AZURE_SPEECH_KEY')
        self.region = region or os.getenv('AZURE_REGION')

        # For debugging
        logger.info()
            f"Azure Speech Key: {self.subscription_key[:5]}... (length: {len(self.subscription_key) if self.subscription_key else 0})")
        logger.info(f"Azure Speech Region: {self.region}")

        if not self.subscription_key or not self.region:
            raise ValueError("Azure Speech Service requires a subscription key and region. "
                             "Set AZURE_SPEECH_KEY and AZURE_REGION environment variables.")

        connection = sqlite3.connect(db_path, check_same_thread=False)
        self.transcription_repo = TranscriptionSQLiteRepository(connection)
        self.speech_config = speechsdk.SpeechConfig(
            subscription=self.subscription_key,
            region=self.region
        )
        # Support multiple languages
        self.speech_config.speech_recognition_language = "ar-SA"  # Default to Arabic

    async def transcribe_audio(
        self,
        audio_file_path: str,
        user_id: int = None,
        conversation_id: int = None,
        language: str = None
    ) -> Transcription:
        # Delete existing transcription if any
        self.transcription_repo.delete_by_audio_path(audio_file_path)

        # Optionally check if already transcribed (now commented out since we're deleting)
        # existing_transcription = self.transcription_repo.get_by_audio_path(audio_file_path)
        # if existing_transcription:
        #     return existing_transcription

        # Set language if provided
        if language:
            self.speech_config.speech_recognition_language = language

        # Create audio configuration
        audio_config = speechsdk.AudioConfig(filename=audio_file_path)

        # Create speech recognizer
        speech_recognizer = speechsdk.SpeechRecognizer(
            speech_config=self.speech_config,
            audio_config=audio_config
        )

        # Perform recognition
        logger.info("----> قبل recognize_once")
        try:
            result = speech_recognizer.recognize_once()
            logger.info("----> بعد recognize_once")
            logger.info("Azure result:", vars(result))
            logger.info("Azure result.text:", result.text)
        except Exception as e:
    logger.error(f"Error: {e}")"!!!!!! Exception داخل Azure recognize_once:", e)
            raise

        # Check recognition result
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            if not result.text.strip():
                logger.info("Azure STT: RecognizedSpeech, but result.text is empty!")
                raise ValueError(
                    "Azure STT: No recognized text in the result.")
            # Create transcription entity
            transcription = Transcription(
                audio_file_path=audio_file_path,
                text=result.text,
                language=self.speech_config.speech_recognition_language,
                confidence=1.0,  # Azure doesn't provide direct confidence score
                user_id=user_id,
                conversation_id=conversation_id,
                model_used='azure_speech_service'
            )

            # Save to database
            return await self.transcription_repo.create(transcription)
        elif result.reason == speechsdk.ResultReason.NoMatch:
            raise ValueError(
                f"No speech could be recognized: {result.no_match_details}")
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation = result.cancellation_details
            raise RuntimeError(
                f"Speech Recognition canceled: {cancellation.reason}. "
                f"Error details: {cancellation.error_details}"
            )

    def transcribe_directory(
        self,
        directory_path: str,
        user_id: int = None,
        conversation_id: int = None,
        language: str = None
    ):
        transcriptions = []
        for filename in os.listdir(directory_path):
            if filename.endswith(('.wav', '.mp3', '.ogg', '.flac')):
                full_path = os.path.join(directory_path, filename)
                transcriptions.append(
                    self.transcribe_audio(
                        full_path,
                        user_id=user_id,
                        conversation_id=conversation_id,
                        language=language
                    )
                )
        return transcriptions

    def get_conversation_transcriptions(int) -> None:
        """Retrieve all transcriptions for a specific conversation."""
        return self.transcription_repo.get_by_conversation_id(conversation_id)