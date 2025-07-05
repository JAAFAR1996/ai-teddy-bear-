import asyncio
from typing import Any, Dict, Optional
import numpy as np
import whisper
import logging

from .base import BaseProvider
from ..transcription_models import TranscriptionConfig

logger = logging.getLogger(__name__)


class WhisperProvider(BaseProvider):
    """Transcription provider for the Whisper model."""

    def __init__(self, model: Any, config: TranscriptionConfig):
        self.model = model
        self.config = config

    async def transcribe(
        self, audio_array: np.ndarray, language: Optional[str]
    ) -> Dict[str, Any]:
        """Transcribe using Whisper model"""
        options = {
            "language": language or self.config.language,
            "task": "transcribe"
        }

        result = await asyncio.to_thread(
            self.model.transcribe,
            audio_array,
            **{k: v for k, v in options.items() if v is not None},
        )

        confidence = self._calculate_confidence(result.get("segments", []))

        return {
            "text": result["text"].strip(),
            "confidence": confidence,
            "language": result.get("language", "unknown"),
            "segments": result.get("segments", []),
            "provider": "whisper",
        }

    def _calculate_confidence(self, segments: list) -> float:
        """Calculate overall confidence from segments"""
        if not segments:
            return 0.5  # Default confidence

        confidences = [
            np.exp(segment["avg_logprob"])
            for segment in segments
            if "avg_logprob" in segment
        ]

        if confidences:
            return float(np.mean(confidences))

        return 0.8  # Default high confidence for Whisper
