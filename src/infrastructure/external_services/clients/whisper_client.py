"""
Whisper Client Infrastructure
Handles OpenAI Whisper model integration
"""

import logging
from typing import Any, Dict, Optional

import numpy as np
import torch
import whisper


class WhisperClient:
    """Infrastructure client for Whisper speech recognition"""

    def __init__(self, model_size: str = "base", device: Optional[str] = None):
        self.model_size = model_size
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.logger = logging.getLogger(self.__class__.__name__)
        self.model = None

        # Load model
        self._load_model()

    def _load_model(self):
        """Load Whisper model"""
        try:
            self.model = whisper.load_model(self.model_size, device=self.device)
            self.logger.info(
                f"Loaded Whisper model: {self.model_size} on {self.device}"
            )
        except Exception as e:
            self.logger.error(f"Failed to load Whisper model: {e}")
            self.model = None

    async def transcribe_audio(
        self,
        audio_data: np.ndarray,
        language: Optional[str] = None,
        task: str = "transcribe",
    ) -> Optional[Dict[str, Any]]:
        """Transcribe audio using Whisper"""
        try:
            if self.model is None:
                self.logger.error("Whisper model not loaded")
                return None

            # Transcribe
            result = self.model.transcribe(
                audio_data, language=language, task=task, verbose=False
            )

            return {
                "text": result["text"].strip(),
                "language": result.get("language"),
                "segments": result.get("segments", []),
                "confidence": self._calculate_confidence(result),
            }

        except Exception as e:
            self.logger.error(f"Whisper transcription error: {e}")
            return None

    def _calculate_confidence(self, result: Dict) -> float:
        """Calculate confidence score from Whisper result"""
        try:
            segments = result.get("segments", [])
            if not segments:
                return 0.5

            # Average log probability from segments
            total_prob = sum(segment.get("avg_logprob", -1.0) for segment in segments)
            avg_logprob = total_prob / len(segments)

            # Convert to confidence (rough approximation)
            confidence = max(0.0, min(1.0, (avg_logprob + 1.0) / 1.0))
            return confidence

        except Exception:
            return 0.5

    async def detect_language(self, audio_data: np.ndarray) -> Optional[str]:
        """Detect language from audio"""
        try:
            if self.model is None:
                return None

            # Detect language
            audio_segment = whisper.pad_or_trim(audio_data)
            mel = whisper.log_mel_spectrogram(audio_segment).to(self.model.device)
            _, probs = self.model.detect_language(mel)

            # Get most likely language
            detected_language = max(probs, key=probs.get)
            return detected_language

        except Exception as e:
            self.logger.error(f"Language detection error: {e}")
            return None

    def is_available(self) -> bool:
        """Check if Whisper model is available"""
        return self.model is not None

    async def reload_model(self, model_size: Optional[str] = None):
        """Reload model with different size"""
        if model_size:
            self.model_size = model_size

        self._load_model()

    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "model_size": self.model_size,
            "device": self.device,
            "available": self.is_available(),
            "model_loaded": self.model is not None,
        }
