import logging
import os
import sqlite3
from typing import Any

import whisper

from src.core.domain.entities.transcription import Transcription
from src.infrastructure.persistence.transcription_sqlite_repository import \
    TranscriptionSQLiteRepository


class SpeechToTextService:
    def __init__(self, db_path, model_size="medium"):
        self.db_path = db_path
        self.model_size = model_size
        self.logger = logging.getLogger(__name__)
        try:
            self.whisper_model = whisper.load_model(model_size)
            self.logger.info("Whisper model loaded successfully.")
        except Exception as e:
            self.whisper_model = None
            self.logger.error(f"Failed to load Whisper model: {e}")

        self.azure_service = None
        self.logger = logging.getLogger(__name__)

        async def transcribe_audio(
            self,
            audio_file_path: str,
            user_id=None,
            conversation_id=None,
            language=None,
        ):
            if not self.whisper_model:
                self.logger.error("Whisper model not loaded, cannot transcribe.")
                return None

            self.logger.info(f"Starting transcription for file: {audio_file_path}")
            try:
                result = self.whisper_model.transcribe(audio_file_path, language="ar")
                text = result.get("text", None)

                if not text:
                    self.logger.warning("Whisper transcription returned empty text.")
                    return None
                cleaned_text = self._clean_arabic_text(text)
                self.logger.info(f"Transcription cleaned text: {cleaned_text}")

                # حفظ النص في قاعدة البيانات (اختياري، لو تريد تخزين)
                conn = sqlite3.connect(self.db_path)
                conn.row_factory = sqlite3.Row
                transcription = Transcription(
                    audio_file_path=audio_file_path,
                    text=cleaned_text,
                    language="ar",
                    confidence=result.get("confidence", 0.0),
                    user_id=user_id,
                    conversation_id=conversation_id,
                    model_used=self.model_size,
                )
                repo = TranscriptionSQLiteRepository(conn)
                # تأكد أن create هي async، إذا لا، احذف await
                await repo.create(transcription)

                return cleaned_text
            except Exception as e:
                self.logger.error(f"Error during transcription: {e}")
                return None

    def _validate_azure_service(self) -> Any:
        """
        Perform a validation check on Azure Speech Service
        Raises an exception if the service is not fully operational
        """
        if not self.azure_service:
            raise ValueError("Azure Speech Service not initialized")

        # Add any additional validation checks specific to Azure service
        # For example, check configuration, network connectivity, etc.
        # This is a placeholder and should be expanded based on Azure SDK capabilities

    def _load_whisper_model(self) -> Any:
        """
        Load Whisper model as a last resort fallback

        Returns:
            whisper model or None
        """
        if not self.whisper_model:
            try:
                # Use a larger model for better Arabic support
                self.whisper_model = whisper.load_model("medium")
                self.logger.warning("Whisper model loaded as FALLBACK option")
                return self.whisper_model
            except Exception as e:
                self.logger.error(f"Whisper model loading failed: {e}")
                self.whisper_model = None
                return None

    def _clean_arabic_text(self, text: str) -> str:
        logger.info("نص قبل التنظيف في الدالة:", text)
        """
        Clean up Arabic transcription text
        - Remove extra whitespaces
        - Remove non-Arabic characters if they seem out of place
        """
        # Remove leading/trailing whitespaces
        text = text.strip()

        # Remove any random English words or characters that don't belong
        import re

        # Keep Arabic characters, spaces, and some punctuation
        cleaned_text = re.sub(r"[^\u0600-\u06FF\s\.\،\؟\?\!]", "", text)

        # Remove multiple consecutive spaces
        cleaned_text = re.sub(r"\s+", " ", cleaned_text)
        logger.info("نص بعد التنظيف في الدالة:", cleaned_text)

        return cleaned_text

    async def transcribe_directory(
        self, directory_path: str, user_id=None, conversation_id=None, language=None
    ):
        transcriptions = []
        for filename in os.listdir(directory_path):
            if filename.endswith((".wav", ".mp3", ".ogg", ".flac")):
                full_path = os.path.join(directory_path, filename)
                text = await self.transcribe_audio(
                    full_path,
                    user_id=user_id,
                    conversation_id=conversation_id,
                    language=language,
                )
                transcriptions.append(text)
        return transcriptions

    def get_conversation_transcriptions(int) -> None:
        """Retrieve all transcriptions for a specific conversation."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return TranscriptionSQLiteRepository(conn).get_by_conversation_id(
            conversation_id
        )

    async def transcribe(self, audio_data: bytes) -> str:
        """تحويل بيانات صوتية إلى نص"""
        import os
        import tempfile

        # حفظ مؤقت
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio_data)
            tmp_path = tmp.name

        try:
            # استخدم الدالة الموجودة
            transcription = self.transcribe_audio(tmp_path)
            return transcription.text if transcription else ""
        finally:
            # تنظيف
            os.unlink(tmp_path)
