from typing import Dict, List, Any, Optional

import structlog
logger = structlog.get_logger(__name__)

from src.domain.repositories.base import BaseRepository
from src.infrastructure.persistence.base_sqlite_repository import BaseSQLiteRepository
from src.domain.entities.transcription import Transcription
import sqlite3
from datetime import datetime
import os
import wave
import contextlib


class TranscriptionSQLiteRepository(BaseSQLiteRepository):
    def __init__(self, connection):
        super().__init__(
            connection,
            table_name="transcriptions",
            entity_class=Transcription
        )

    def _get_table_schema(self) -> str:
        """Get the CREATE TABLE SQL statement for transcriptions"""
        return '''
        CREATE TABLE IF NOT EXISTS transcriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            audio_file_path TEXT,
            text TEXT,
            language TEXT,
            confidence REAL,
            created_at DATETIME,
            user_id INTEGER,
            conversation_id INTEGER,
            duration REAL,
            model_used TEXT
        )
        '''

    def _get_audio_duration(self, audio_file_path) -> Any:
        """Get audio file duration in seconds."""
        try:
            with contextlib.closing(wave.open(audio_file_path, 'rb')) as f:
                frames = f.getnframes()
                rate = f.getframerate()
                duration = frames / float(rate)
                return duration
        except Exception as e:
            return None

    def add(self, transcription: Transcription) -> Transcription:
        """Override add method to handle audio duration and defaults."""
        # Set creation time
        transcription.created_at = datetime.now()

        # If no duration provided, try to get it from file
        if transcription.duration is None and transcription.audio_file_path:
            transcription.duration = self._get_audio_duration(
                transcription.audio_file_path)

        # Default model used if not specified
        if transcription.model_used is None:
            transcription.model_used = 'whisper_base'

        # Use parent class add method
        return super().add(transcription)

    def get_by_audio_path(self, audio_file_path: str) -> Transcription:
        """Get transcription by audio file path."""
        results = self.list(limit=1, audio_file_path=audio_file_path)
        return results[0] if results else None

    def delete_by_audio_path(self, audio_file_path: str) -> bool:
        """Delete transcription records by audio file path."""
        query = 'DELETE FROM transcriptions WHERE audio_file_path = ?'
        cursor = self._connection.cursor()
        cursor.execute(query, (audio_file_path,))
        self._connection.commit()
        return cursor.rowcount > 0

    def get_by_conversation_id(self, conversation_id -> Any: int) -> Any:
        """Retrieve all transcriptions for a specific conversation."""
        return self.list(conversation_id=conversation_id)

    def exists(self, entity_id: str) -> bool:
        query = 'SELECT 1 FROM transcriptions WHERE id = ?'
        cursor = self._connection.cursor()
        cursor.execute(query, (entity_id,))
        return cursor.fetchone() is not None

    def get(self, entity_id -> Any: int) -> Any:
        """Get a transcription by its ID."""
        query = 'SELECT * FROM transcriptions WHERE id = ?'
        cursor = self._connection.cursor()
        cursor.execute(query, (entity_id,))
        row = cursor.fetchone()
        if row:
            # تحويل الصف (row) إلى كائن Transcription باستخدام الدالة الجاهزة غالباً في الأب
            return self._map_row_to_entity(row)
        return None

    # Alias for backward compatibility
    create = add