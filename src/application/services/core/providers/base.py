from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import numpy as np


class BaseProvider(ABC):
    """Abstract base class for transcription providers."""

    @abstractmethod
    async def transcribe(
        self, audio_array: np.ndarray, language: Optional[str]
    ) -> Dict[str, Any]:
        """Transcribes audio data and returns the result."""
        pass
