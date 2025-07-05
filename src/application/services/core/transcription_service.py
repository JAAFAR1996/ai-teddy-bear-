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

# Value objects

logger = logging.getLogger(__name__)

# ================== AUDIO PROCESSING ENUMS ==================


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


# ================== AUDIO PROCESSOR ==================


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


# ================== CONFIGURATION ==================


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


# ================== AUDIO BUFFER ==================


class StreamingAudioBuffer:
    """Smart audio buffer for streaming transcription"""

    def __init__(self, config: TranscriptionConfig):
        self.config = config
        self.buffer = np.array([], dtype=np.float32)
        self.sample_rate = config.sample_rate
        self.chunk_samples = int(config.chunk_duration * self.sample_rate)
        self.overlap_samples = int(config.overlap_duration * self.sample_rate)
        self.min_silence_samples = int(
            config.min_silence_duration * self.sample_rate)

        # State tracking
        self.last_activity = time.time()
        self.is_speech_detected = False

    def add_chunk(self, audio_chunk: np.ndarray) -> None:
        """Add audio chunk to buffer"""
        # Ensure correct format
        if audio_chunk.dtype != np.float32:
            audio_chunk = audio_chunk.astype(np.float32)

        # Normalize if needed
        if np.max(np.abs(audio_chunk)) > 1.0:
            audio_chunk = audio_chunk / np.max(np.abs(audio_chunk))

        # Add to buffer
        self.buffer = np.concatenate([self.buffer, audio_chunk])

        # Update activity detection
        if self._detect_activity(audio_chunk):
            self.last_activity = time.time()
            self.is_speech_detected = True

    def _detect_activity(self, audio_chunk: np.ndarray) -> bool:
        """Simple voice activity detection"""
        # Calculate RMS energy
        rms = np.sqrt(np.mean(audio_chunk**2))

        # Dynamic threshold based on recent history
        threshold = 0.01  # Base threshold
        return rms > threshold

    def get_ready_chunk(self) -> Optional[np.ndarray]:
        """Get audio chunk ready for transcription"""
        if len(self.buffer) < self.chunk_samples:
            return None

        # Check for silence gap
        silence_duration = time.time() - self.last_activity

        if (
            self.is_speech_detected
            and silence_duration >= self.config.min_silence_duration
        ):
            # Extract complete utterance
            chunk = self.buffer.copy()
            self.buffer = np.array([], dtype=np.float32)
            self.is_speech_detected = False
            return chunk

        # Extract chunk with overlap
        if len(self.buffer) >= self.chunk_samples:
            chunk = self.buffer[: self.chunk_samples]
            # Keep overlap for next chunk
            self.buffer = self.buffer[self.chunk_samples -
                                      self.overlap_samples:]
            return chunk

        return None

    @property
    def duration(self) -> float:
        """Current buffer duration in seconds"""
        return len(self.buffer) / self.sample_rate

    def clear(self) -> None:
        """Clear the buffer"""
        self.buffer = np.array([], dtype=np.float32)
        self.is_speech_detected = False


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

        # Initialize audio processor for complex audio handling
        self.audio_processor = AudioProcessor(self.config)

        # Performance tracking
        self.stats = {
            "total_transcriptions": 0,
            "total_processing_time": 0.0,
            "average_confidence": 0.0,
            "error_count": 0,
            "fallback_usage": 0,  # تتبع استخدام الطرق الاحتياطية
        }

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
                logger.info("✅ OpenAI client initialized for transcription")

            # Pre-load model for faster first transcription
            await self._ensure_model_loaded()

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
            self.stats["error_count"] += 1

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
                audio_array = self._enhance_for_children(audio_array)

            # اختيار مقدم الخدمة
            if provider == "openai" and self.openai_client:
                result = await self._transcribe_openai(audio_array, language)
            else:
                result = await self._transcribe_whisper(audio_array, language)

            # 👶 تحسين النتيجة للأطفال
            if child_mode:
                result = self._post_process_child_speech(result)

            # حساب وقت المعالجة
            processing_time = time.time() - start_time
            result["processing_time_ms"] = int(processing_time * 1000)
            result["child_mode"] = child_mode

            # تحديث الإحصائيات
            self._update_stats(result, processing_time)

            logger.debug(
                f"🎯 {'👶 Child mode' if child_mode else 'Adult mode'} transcription in {processing_time:.2f}s: '{result['text'][:50]}...'"
            )
            return result

        except Exception as e:
            logger.error(f"❌ Transcription failed: {e}")
            self.stats["error_count"] += 1

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

    def _enhance_for_children(self, audio_array: np.ndarray) -> np.ndarray:
        """
        🎪 تحسين البيانات الصوتية للأطفال
        Child-specific audio enhancements
        """
        # تعزيز الترددات العالية (أصوات الأطفال عادة أعلى)
        audio_array = self._boost_high_frequencies(audio_array)

        # تقليل الضوضاء الخلفية (اللعب، الحركة)
        audio_array = self._reduce_background_noise(audio_array)

        # تطبيع الصوت للأطفال الهادئين
        audio_array = self._normalize_for_quiet_children(audio_array)

        return audio_array

    def _boost_high_frequencies(self, audio_array: np.ndarray) -> np.ndarray:
        """تعزيز الترددات العالية لأصوات الأطفال"""
        # تطبيق مرشح تمرير عالي بسيط
        # هذا تبسيط - في الواقع نحتاج مرشح أكثر تعقيداً
        if len(audio_array) > 2:
            # تطبيق تنعيم بسيط للترددات العالية
            enhanced = np.copy(audio_array)
            enhanced[1:-1] = (0.25 * enhanced[:-2] + 0.5 *
                              enhanced[1:-1] + 0.25 * enhanced[2:])
            return enhanced
        return audio_array

    def _reduce_background_noise(self, audio_array: np.ndarray) -> np.ndarray:
        """تقليل ضوضاء الخلفية الشائعة في بيئة الأطفال"""
        # تطبيق حد أدنى للإشارة (noise gate)
        noise_threshold = np.std(audio_array) * 0.1
        audio_array = np.where(
            np.abs(audio_array) < noise_threshold, 0, audio_array)
        return audio_array

    def _normalize_for_quiet_children(
            self, audio_array: np.ndarray) -> np.ndarray:
        """تطبيع الصوت للأطفال ذوي الأصوات المنخفضة"""
        max_val = np.max(np.abs(audio_array))
        if max_val > 0 and max_val < 0.3:  # أصوات منخفضة
            # تعزيز الإشارة مع تجنب التشبع
            boost_factor = min(3.0, 0.8 / max_val)
            audio_array = audio_array * boost_factor
        return audio_array

    def _post_process_child_speech(
            self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        👶 معالجة لاحقة لتحسين نتائج نسخ كلام الأطفال
        """
        text = result.get("text", "").strip()

        if not text:
            return result

        # 🔤 إصلاح الأخطاء الشائعة في كلام الأطفال
        text = self._fix_common_child_speech_errors(text)

        # 🎯 تعزيز الثقة للكلمات الواضحة
        confidence = result.get("confidence", 0.0)
        if self._is_clear_child_speech(text):
            confidence = min(1.0, confidence + 0.1)

        result["text"] = text
        result["confidence"] = confidence
        result["child_optimized"] = True

        return result

    def _fix_common_child_speech_errors(self, text: str) -> str:
        """إصلاح الأخطاء الشائعة في كلام الأطفال"""
        # قاموس للإصلاحات الشائعة (يمكن توسيعه)
        common_fixes = {
            " wike ": " like ",
            " wove ": " love ",
            " pwease ": " please ",
            " fwiend ": " friend ",
            " bwother ": " brother ",
            " sistew ": " sister ",
            # يمكن إضافة المزيد من الإصلاحات حسب اللغة
        }

        for wrong, correct in common_fixes.items():
            text = text.replace(wrong, correct)

        return text

    def _is_clear_child_speech(self, text: str) -> bool:
        """تحديد ما إذا كان النص يشير إلى كلام طفل واضح"""
        # مؤشرات الكلام الواضح للأطفال
        clear_indicators = [
            len(text.split()) >= 3,  # جمل كاملة
            not any(char in text for char in "[](){}"),  # بدون رموز غريبة
            text.count(" ") >= 2,  # أكثر من كلمتين
            any(
                word in text.lower()
                for word in ["hello", "hi", "teddy", "play", "story"]
            ),  # كلمات شائعة
        ]

        return sum(clear_indicators) >= 2

    async def _transcribe_whisper(
        self, audio_array: np.ndarray, language: Optional[str]
    ) -> Dict[str, Any]:
        """Transcribe using Whisper model"""
        await self._ensure_model_loaded()

        # Prepare options
        options = {
            "language": language or self.config.language,
            "task": "transcribe"}

        # Run transcription in thread to avoid blocking
        result = await asyncio.to_thread(
            self.model.transcribe,
            audio_array,
            **{k: v for k, v in options.items() if v is not None},
        )

        # Extract confidence from segments
        confidence = self._calculate_confidence(result.get("segments", []))

        return {
            "text": result["text"].strip(),
            "confidence": confidence,
            "language": result.get("language", "unknown"),
            "segments": result.get("segments", []),
            "provider": "whisper",
        }

    async def _transcribe_openai(
        self, audio_array: np.ndarray, language: Optional[str]
    ) -> Dict[str, Any]:
        """Transcribe using OpenAI Whisper API"""
        try:
            # Convert to wav bytes
            import io

            import soundfile as sf

            buffer = io.BytesIO()
            sf.write(
                buffer,
                audio_array,
                self.config.sample_rate,
                format="WAV")
            buffer.seek(0)

            # Call OpenAI API
            response = await self.openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=buffer,
                language=language,
                response_format="verbose_json",
            )

            return {
                "text": response.text.strip(),
                "confidence": 0.95,  # OpenAI doesn't provide confidence
                "language": response.language,
                "segments": getattr(response, "segments", []),
                "provider": "openai",
            }

        except Exception as e:
            logger.error(f"❌ OpenAI transcription failed: {e}")
            # Fallback to Whisper
            return await self._transcribe_whisper(audio_array, language)

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
            self.stats["error_count"] += 1

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
        self.stats["fallback_usage"] += 1
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

    def _update_stats(
            self, result: Dict[str, Any], processing_time: float) -> None:
        """Update performance statistics"""
        self.stats["total_transcriptions"] += 1
        self.stats["total_processing_time"] += processing_time

        # Update average confidence
        current_avg = self.stats["average_confidence"]
        count = self.stats["total_transcriptions"]
        new_confidence = result.get("confidence", 0.0)

        self.stats["average_confidence"] = (
            current_avg * (count - 1) + new_confidence
        ) / count

    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        📊 Get comprehensive performance metrics
        Enhanced for teddy bear monitoring and optimization
        """
        total_transcriptions = self.stats["total_transcriptions"]

        avg_processing_time = (
            self.stats["total_processing_time"] / total_transcriptions
            if total_transcriptions > 0
            else 0
        )

        error_rate = (
            self.stats["error_count"] / total_transcriptions
            if total_transcriptions > 0
            else 0
        )

        fallback_rate = (
            self.stats["fallback_usage"] / total_transcriptions
            if total_transcriptions > 0
            else 0
        )

        return {
            # 📈 Basic metrics
            "total_transcriptions": total_transcriptions,
            "average_processing_time_s": round(avg_processing_time, 3),
            "average_confidence": round(self.stats["average_confidence"], 3),
            # 🔧 Reliability metrics
            "error_count": self.stats["error_count"],
            "error_rate": round(error_rate, 3),
            "fallback_usage": self.stats["fallback_usage"],
            "fallback_rate": round(fallback_rate, 3),
            # 🎯 Teddy bear specific metrics
            "is_child_friendly": error_rate < 0.05 and avg_processing_time < 2.0,
            "response_quality": (
                "excellent"
                if error_rate < 0.02
                else "good" if error_rate < 0.05 else "needs_improvement"
            ),
            "processing_speed": (
                "fast"
                if avg_processing_time < 1.0
                else "acceptable" if avg_processing_time < 2.0 else "slow"
            ),
            # 🖥️ System info
            "model": self.config.whisper_model,
            "device": self.config.device,
            "sample_rate": self.config.sample_rate,
            "confidence_threshold": self.config.confidence_threshold,
        }

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
