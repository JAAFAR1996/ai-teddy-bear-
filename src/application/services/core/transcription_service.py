"""
🎤 Modern Transcription Service - 2025 Edition
Streaming Speech-to-Text with lazy model loading and async processing
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from enum import Enum
from functools import lru_cache
from typing import Any, AsyncIterator, Dict, Optional, Union

import numpy as np
import torch

# Audio processing
import whisper

try:
    import torchaudio
except ImportError:
    torchaudio = None
import librosa
from openai import AsyncOpenAI

from .transcription_models import (
    AudioFormat,
    ProcessingState,
    TranscriptionConfig,
)
from .audio_processor import AudioProcessor
from .streaming_audio_buffer import StreamingAudioBuffer
from .child_speech_processor import ChildSpeechProcessor
from .providers.base import BaseProvider
from .providers.whisper_provider import WhisperProvider
from .providers.openai_provider import OpenAIProvider
from .performance_tracker import PerformanceTracker

# Value objects

logger = logging.getLogger(__name__)


# ================== TRANSCRIPTION SERVICE ==================


class ModernTranscriptionService:
    """
    🎤 Modern Transcription Service with 2025 Features:
    - Lazy model loading with singleton pattern
    - Real-time streaming transcription
    - Multi-provider support (Whisper, OpenAI)
    - Smart buffering and voice activity detection
    - GPU acceleration support
    - Confidence scoring and language detection
    """

    _instance = None
    _model_cache = {}
    _model_lock = asyncio.Lock()

    def __init__(self, config: Optional[TranscriptionConfig] = None):
        self.config = config or TranscriptionConfig()
        self.model = None
        self.openai_client = None
        self.whisper_provider = None
        self.openai_provider = None

        # Initialize audio processor for complex audio handling
        self.audio_processor = AudioProcessor(self.config)
        self.child_speech_processor = ChildSpeechProcessor()
        self.performance_tracker = PerformanceTracker()

        logger.info(
            f"✅ Modern Transcription Service initialized (model: {self.config.whisper_model}, device: {self.config.device})"
        )

    @classmethod
    async def get_instance(
        cls, config: Optional[TranscriptionConfig] = None
    ) -> "ModernTranscriptionService":
        """Get singleton instance with lazy initialization"""
        if cls._instance is None:
            cls._instance = cls(config)
        return cls._instance

    async def initialize(self, openai_api_key: Optional[str] = None) -> None:
        """Initialize services asynchronously"""
        try:
            # Initialize OpenAI client if API key provided
            if openai_api_key:
                self.openai_client = AsyncOpenAI(api_key=openai_api_key)
                self.openai_provider = OpenAIProvider(
                    self.openai_client, self.config)
                logger.info("✅ OpenAI client initialized for transcription")

            # Pre-load model for faster first transcription
            await self._ensure_model_loaded()
            if self.model:
                self.whisper_provider = WhisperProvider(
                    self.model, self.config)

            logger.info("🚀 Transcription service fully initialized")

        except Exception as e:
            logger.error(f"❌ Failed to initialize transcription service: {e}")
            raise

    async def _ensure_model_loaded(self) -> None:
        """Ensure Whisper model is loaded (lazy loading with caching)"""
        model_key = f"{self.config.whisper_model}_{self.config.device}"

        if model_key in self._model_cache:
            self.model = self._model_cache[model_key]
            logger.debug(f"📦 Using cached Whisper model: {model_key}")
            return

        async with self._model_lock:
            # Double-check after acquiring lock
            if model_key in self._model_cache:
                self.model = self._model_cache[model_key]
                return

            logger.info(
                f"📥 Loading Whisper model: {self.config.whisper_model} on {self.config.device}"
            )
            start_time = time.time()

            try:
                # Load model in thread to avoid blocking
                model = await asyncio.to_thread(
                    whisper.load_model,
                    self.config.whisper_model,
                    device=self.config.device,
                )

                # Cache the model
                self._model_cache[model_key] = model
                self.model = model

                load_time = time.time() - start_time
                logger.info(f"✅ Whisper model loaded in {load_time:.2f}s")

            except Exception as e:
                logger.error(f"❌ Failed to load Whisper model: {e}")
                raise

    async def transcribe_stream(
        self, audio_stream: AsyncIterator[np.ndarray]
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        🌊 Stream transcription with real-time processing

        Args:
            audio_stream: Async iterator of audio chunks

        Yields:
            Transcription results with metadata
        """
        await self._ensure_model_loaded()

        buffer = StreamingAudioBuffer(self.config)

        try:
            async for audio_chunk in audio_stream:
                # Add chunk to buffer
                buffer.add_chunk(audio_chunk)

                # Check if we have a complete chunk ready
                ready_chunk = buffer.get_ready_chunk()
                if ready_chunk is not None:
                    # Transcribe the chunk
                    result = await self.transcribe_audio(ready_chunk)

                    # Only yield if confidence is high enough
                    if result["confidence"] >= self.config.confidence_threshold:
                        yield result

        except Exception as e:
            logger.error(f"❌ Stream transcription error: {e}")
            self.performance_tracker.increment_error_count()

    async def transcribe_audio(
        self,
        audio_data: Union[np.ndarray, bytes, str],
        language: Optional[str] = None,
        provider: str = "whisper",
        child_mode: bool = True,  # 👶 تفعيل الوضع الخاص بالأطفال
    ) -> Dict[str, Any]:
        """
        🎯 Transcribe audio with enhanced child speech recognition

        Special features for teddy bear:
        - Enhanced sensitivity for child voices
        - Better handling of incomplete words
        - Noise reduction for play environments
        - Confidence boosting for clear child speech

        Args:
            audio_data: Audio data in various formats
            language: Language code (auto-detect if None)
            provider: "whisper" or "openai"
            child_mode: Enable child-specific optimizations

        Returns:
            Transcription result with confidence and metadata
        """
        start_time = time.time()

        # 🎪 تحسينات خاصة بالأطفال
        original_confidence_threshold = self.config.confidence_threshold
        if child_mode:
            # تقليل عتبة الثقة للأطفال (أصواتهم أقل وضوحاً أحياناً)
            self.config.confidence_threshold = max(
                0.5, self.config.confidence_threshold - 0.1
            )

        try:
            # تحضير البيانات الصوتية مع تحسينات للأطفال
            audio_array = await self._prepare_audio(audio_data)

            # 🔊 تحسين الصوت للأطفال
            if child_mode:
                audio_array = self.child_speech_processor.enhance_for_children(
                    audio_array)

            # اختيار مقدم الخدمة
            if provider == "openai" and self.openai_provider:
                result = await self.openai_provider.transcribe(audio_array, language)
            elif self.whisper_provider:
                result = await self.whisper_provider.transcribe(audio_array, language)
            else:
                raise RuntimeError("No transcription provider is available.")

            # 👶 تحسين النتيجة للأطفال
            if child_mode:
                result = self.child_speech_processor.post_process_child_speech(
                    result)

            # حساب وقت المعالجة
            processing_time = time.time() - start_time
            result["processing_time_ms"] = int(processing_time * 1000)
            result["child_mode"] = child_mode

            # تحديث الإحصائيات
            self.performance_tracker.update_stats(result, processing_time)

            logger.debug(
                f"🎯 {'👶 Child mode' if child_mode else 'Adult mode'} transcription in {processing_time:.2f}s: '{result['text'][:50]}...'"
            )
            return result

        except Exception as e:
            logger.error(f"❌ Transcription failed: {e}")
            self.performance_tracker.increment_error_count()

            return {
                "text": "",
                "confidence": 0.0,
                "language": "unknown",
                "error": str(e),
                "processing_time_ms": int((time.time() - start_time) * 1000),
                "child_mode": child_mode,
            }

        finally:
            # استعادة الإعدادات الأصلية
            self.config.confidence_threshold = original_confidence_threshold

    async def _prepare_audio(
        self, audio_data: Union[np.ndarray, bytes, str]
    ) -> np.ndarray:
        """
        📋 Prepare audio data for transcription
        Using AudioProcessor with fallback mechanism for reliability
        """
        try:
            # استخدام AudioProcessor المحسن مع آليات احتياطية
            audio_array = await self.audio_processor.process_with_fallback(audio_data)

            # التأكد من التنسيق النهائي والجودة
            audio_array = self._finalize_audio_quality(audio_array)

            return audio_array

        except Exception as e:
            logger.error(f"❌ Critical audio preparation failure: {e}")
            self.performance_tracker.increment_error_count()

            # آلية احتياطية أساسية جداً
            return await self._emergency_audio_fallback(audio_data)

    def _finalize_audio_quality(self, audio_array: np.ndarray) -> np.ndarray:
        """
        تحسين جودة الصوت النهائية للنسخ
        Single responsibility: quality optimization only
        """
        # تطبيع مستوى الصوت
        max_val = np.max(np.abs(audio_array))
        if max_val > 0:
            audio_array = audio_array / max_val * 0.95  # تجنب التشبع

        # إزالة الصمت من البداية والنهاية
        audio_array = self._trim_silence(audio_array)

        return audio_array

    def _trim_silence(
        self, audio_array: np.ndarray, threshold: float = 0.01
    ) -> np.ndarray:
        """إزالة الصمت من بداية ونهاية التسجيل"""
        # العثور على نقاط بداية ونهاية الكلام
        above_threshold = np.abs(audio_array) > threshold

        if not np.any(above_threshold):
            # إذا كان كل التسجيل صمت، إرجاع عينة قصيرة
            return audio_array[: int(0.1 * self.config.sample_rate)]

        # إيجاد أول وآخر نقطة فوق العتبة
        first_sound = np.argmax(above_threshold)
        last_sound = len(above_threshold) - 1 - \
            np.argmax(above_threshold[::-1])

        # إضافة هامش صغير
        margin = int(0.1 * self.config.sample_rate)  # 100ms margin
        start = max(0, first_sound - margin)
        end = min(len(audio_array), last_sound + margin)

        return audio_array[start:end]

    async def _emergency_audio_fallback(self, audio_data: Any) -> np.ndarray:
        """
        آلية احتياطية للحالات الطارئة
        تضمن عدم فشل الخدمة حتى لو فشلت كل الطرق الأخرى
        """
        self.performance_tracker.increment_fallback_usage()
        logger.warning(
            "🚨 Using emergency audio fallback - basic processing only")

        try:
            if isinstance(audio_data, str):
                # تحميل أساسي جداً
                audio, _ = librosa.load(audio_data, sr=self.config.sample_rate)
                return audio.astype(np.float32)
            elif isinstance(audio_data, bytes):
                # تحويل أساسي
                return (
                    np.frombuffer(
                        audio_data,
                        dtype=np.int16).astype(
                        np.float32) /
                    32768.0)
            else:
                # numpy array أساسي
                audio = np.array(audio_data, dtype=np.float32)
                if audio.ndim > 1:
                    audio = np.mean(audio, axis=-1)  # تحويل إلى mono
                return audio

        except Exception as e:
            logger.critical(f"💥 Emergency fallback also failed: {e}")
            # إنشاء صوت صامت لتجنب الانهيار الكامل
            return np.zeros(int(0.5 * self.config.sample_rate),
                            dtype=np.float32)

    def _calculate_confidence(self, segments: list) -> float:
        """Calculate overall confidence from segments"""
        if not segments:
            return 0.5  # Default confidence

        # Average confidence from segments (if available)
        confidences = []
        for segment in segments:
            if "avg_logprob" in segment:
                # Convert log probability to confidence
                confidence = np.exp(segment["avg_logprob"])
                confidences.append(confidence)

        if confidences:
            return float(np.mean(confidences))

        return 0.8  # Default high confidence for Whisper

    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        📊 Get comprehensive performance metrics
        Enhanced for teddy bear monitoring and optimization
        """
        return self.performance_tracker.get_metrics(self.config)

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        try:
            # Test with a short audio sample
            test_audio = (
                np.random.randn(
                    self.config.sample_rate).astype(
                    np.float32) * 0.01)
            result = await self.transcribe_audio(test_audio)

            return {
                "status": "healthy",
                "model_loaded": self.model is not None,
                "device": self.config.device,
                "test_processing_time_ms": result.get("processing_time_ms", 0),
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "model_loaded": self.model is not None,
            }


# ================== FACTORY FUNCTION ==================


async def create_transcription_service(
        config: Optional[TranscriptionConfig] = None,
        openai_api_key: Optional[str] = None) -> ModernTranscriptionService:
    """Factory function to create and initialize transcription service"""
    service = await ModernTranscriptionService.get_instance(config)
    await service.initialize(openai_api_key)
    return service


# Re-export for compatibility
TranscriptionService = ModernTranscriptionService
