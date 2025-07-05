from dataclasses import dataclass
from enum import Enum
from typing import Optional
import torch


class AudioFormat(Enum):
    """تصنيف أنواع البيانات الصوتية المدعومة"""

    FILE_PATH = "file_path"
    BYTES_DATA = "bytes_data"
    NUMPY_ARRAY = "numpy_array"
    UNKNOWN = "unknown"


class ProcessingState(Enum):
    """حالات معالجة البيانات الصوتية"""

    INITIAL = "initial"
    CONVERTED = "converted"
    FORMATTED = "formatted"
    RESAMPLED = "resampled"
    READY = "ready"


@dataclass
class TranscriptionConfig:
    """Configuration for transcription service"""

    whisper_model: str = "base"  # tiny, base, small, medium, large
    chunk_duration: float = 3.0  # seconds
    overlap_duration: float = 0.5  # seconds
    min_silence_duration: float = 1.0  # seconds
    confidence_threshold: float = 0.7
    sample_rate: int = 16000
    use_gpu: bool = True
    language: Optional[str] = None  # Auto-detect if None

    @property
    def device(self) -> str:
        """Get optimal computing device for transcription"""
        if self._should_use_cuda():
            return "cuda"
        elif self._should_use_mps():
            return "mps"
        return "cpu"

    def _should_use_cuda(self) -> bool:
        """تحديد ما إذا كان يجب استخدام CUDA GPU"""
        return self.use_gpu and torch.cuda.is_available()

    def _should_use_mps(self) -> bool:
        """تحديد ما إذا كان يجب استخدام Apple Silicon MPS"""
        has_mps_backend = hasattr(torch.backends, "mps")
        mps_available = has_mps_backend and torch.backends.mps.is_available()
        return self.use_gpu and mps_available
