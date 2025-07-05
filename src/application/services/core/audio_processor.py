from functools import lru_cache
from typing import Any, Union
import numpy as np
import librosa
import logging

from .transcription_models import (
    AudioFormat,
    ProcessingState,
    TranscriptionConfig,
)

logger = logging.getLogger(__name__)


class AudioProcessor:
    """
    🎛️ معالج الصوت المحسن مع نمط State Machine
    يدير تحويل البيانات الصوتية خلال مراحل معالجة محددة
    """

    def __init__(self, config: "TranscriptionConfig"):
        self.config = config
        self.state = ProcessingState.INITIAL

    @lru_cache(maxsize=50)
    def get_audio_format(
        self, data_type: str, has_sample_rate: bool = False
    ) -> AudioFormat:
        """تحديد تنسيق البيانات الصوتية مع تخزين مؤقت للنتائج"""
        if data_type == "str":
            return AudioFormat.FILE_PATH
        elif data_type == "bytes":
            return AudioFormat.BYTES_DATA
        elif data_type == "ndarray":
            return AudioFormat.NUMPY_ARRAY
        return AudioFormat.UNKNOWN

    async def process_with_fallback(
        self, audio_data: Union[np.ndarray, bytes, str]
    ) -> np.ndarray:
        """معالجة الصوت مع آليات احتياطية للأخطاء"""
        try:
            return await self._process_primary_method(audio_data)
        except Exception as e:
            logger.warning(
                f"⚠️ Primary processing failed, trying fallback: {e}")
            return await self._process_fallback_method(audio_data)

    async def _process_primary_method(self, audio_data: Any) -> np.ndarray:
        """الطريقة الأساسية للمعالجة (محسنة للأداء)"""
        audio_format = self.get_audio_format(
            type(audio_data).__name__, hasattr(audio_data, "sample_rate")
        )

        if audio_format == AudioFormat.FILE_PATH:
            return await self._load_from_file_optimized(audio_data)
        elif audio_format == AudioFormat.BYTES_DATA:
            return self._convert_bytes_optimized(audio_data)
        elif audio_format == AudioFormat.NUMPY_ARRAY:
            return self._process_array_optimized(audio_data)
        else:
            raise ValueError(f"Unsupported audio format: {audio_format}")

    async def _process_fallback_method(self, audio_data: Any) -> np.ndarray:
        """طريقة احتياطية أساسية للمعالجة"""
        if isinstance(audio_data, str):
            # تحميل أساسي بدون تحسينات
            audio, _ = librosa.load(audio_data, sr=None)
            return librosa.resample(
                audio, orig_sr=22050, target_sr=self.config.sample_rate
            )
        elif isinstance(audio_data, bytes):
            # تحويل أساسي
            return (
                np.frombuffer(
                    audio_data,
                    dtype=np.int16).astype(
                    np.float32) /
                32768.0)
        else:
            # تحويل أساسي لـ numpy
            return np.array(audio_data, dtype=np.float32)

    async def _load_from_file_optimized(self, file_path: str) -> np.ndarray:
        """تحميل محسن من الملف مع معالجة الأخطاء"""
        try:
            # استخدام librosa مع إعدادات محسنة
            audio, sr = librosa.load(
                file_path,
                sr=self.config.sample_rate,
                mono=True,  # تحويل مباشر إلى mono
                dtype=np.float32,
            )
            return audio
        except Exception as e:
            logger.error(f"❌ Optimized file loading failed: {e}")
            raise

    def _convert_bytes_optimized(self, audio_bytes: bytes) -> np.ndarray:
        """تحويل محسن من bytes"""
        # تحويل محسن مع فحص الأخطاء
        if len(audio_bytes) == 0:
            raise ValueError("Empty audio bytes received")

        try:
            return (
                np.frombuffer(
                    audio_bytes,
                    dtype=np.int16).astype(
                    np.float32) /
                32768.0)
        except ValueError as e:
            # محاولة تنسيقات أخرى
            logger.warning(f"⚠️ Int16 conversion failed, trying float32: {e}")
            return np.frombuffer(audio_bytes, dtype=np.float32)

    def _process_array_optimized(self, audio_array: np.ndarray) -> np.ndarray:
        """معالجة محسنة لـ numpy array"""
        if audio_array.size == 0:
            raise ValueError("Empty audio array received")

        # تحويل إلى float32 إذا لم يكن كذلك
        if audio_array.dtype != np.float32:
            audio_array = audio_array.astype(np.float32)

        # تحويل إلى mono بطريقة محسنة
        if audio_array.ndim > 1:
            if audio_array.shape[0] < audio_array.shape[1]:
                # شكل (channels, samples)
                audio_array = np.mean(audio_array, axis=0)
            else:
                # شكل (samples, channels)
                audio_array = np.mean(audio_array, axis=1)

        return audio_array
