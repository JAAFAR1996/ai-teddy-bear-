from typing import Any, Dict, List, Optional

"""
🎵 Enhanced Audio Processor - 2025 Edition
معالج صوت متطور مع معالجة متوازية وتحسين الأداء

Lead Architect: جعفر أديب (Jaafar Adeeb)
Senior Backend Developer & Professor
"""

import asyncio
import hashlib
import logging
import time
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any, AsyncIterator, Dict, List, Optional, Tuple

import numpy as np
import structlog
from cachetools import TTLCache

# Audio processing imports
try:
    import librosa
    import noisereduce as nr
    import soundfile as sf
    import webrtcvad
    from scipy import signal
except ImportError as e:
    logging.warning(f"Audio processing library not available: {e}")

# AI/ML imports
try:
    import torch
    import whisper
    from openai import AsyncOpenAI
except ImportError as e:
    logging.warning(f"AI library not available: {e}")

logger = structlog.get_logger(__name__)


@dataclass
class AudioConfig:
    """تكوين معالجة الصوت"""

    sample_rate: int = 16000
    channels: int = 1
    chunk_size: int = 1024
    noise_reduction_strength: float = 0.6
    vad_aggressiveness: int = 2
    silence_threshold: float = 0.01
    max_silence_duration: float = 2.0


@dataclass
class AudioProcessingResult:
    """نتيجة معالجة الصوت"""

    processed_audio: np.ndarray
    original_audio: np.ndarray
    noise_level: float
    voice_activity_score: float
    emotion_features: Dict[str, float]
    processing_time_ms: float
    quality_score: float
    confidence: float


@dataclass
class EmotionFeatures:
    """خصائص المشاعر المستخرجة من الصوت"""

    energy: float = 0.0
    pitch_mean: float = 0.0
    pitch_std: float = 0.0
    spectral_centroid: float = 0.0
    spectral_rolloff: float = 0.0
    zero_crossing_rate: float = 0.0
    mfcc_features: List[float] = field(default_factory=list)
    tempo: float = 0.0
    harmonics: List[float] = field(default_factory=list)


class EnhancedAudioProcessor:
    """
    معالج صوت متطور مع:
    - معالجة متوازية للتحسين السرعة
    - كاش ذكي للاستجابات المتشابهة
    - تحليل عاطفي متقدم
    - تحسين جودة الصوت
    """

    def __init__(self, config: AudioConfig = None):
        self.config = config or AudioConfig()
        self.logger = structlog.get_logger(__name__)

        # كاش ذكي للمعالجة
        self.preprocessing_cache = TTLCache(maxsize=1000, ttl=300)  # 5 دقائق
        self.response_cache = TTLCache(maxsize=500, ttl=600)  # 10 دقائق
        self.model_cache = {}

        # إحصائيات الأداء
        self.processing_stats = {
            "total_requests": 0,
            "cache_hits": 0,
            "average_processing_time": 0.0,
            "total_processing_time": 0.0,
        }

        # تهيئة المودلات
        self._initialize_models()

    def _initialize_models(self) -> Any:
        """تهيئة المودلات المطلوبة"""
        try:
            # تحميل مودل Whisper للتحليل
            self.whisper_model = whisper.load_model("base")

            # تهيئة VAD (Voice Activity Detection)
            self.vad = webrtcvad.Vad(self.config.vad_aggressiveness)

            # تهيئة OpenAI للتحليل المتقدم
            self.openai_client = AsyncOpenAI()

            self.logger.info("✅ Audio models initialized successfully")

        except Exception as e:
            self.logger.error(f"❌ Failed to initialize audio models: {e}")
            # Fallback to basic processing
            self.whisper_model = None
            self.vad = None
            self.openai_client = None

    async def process_audio_stream(
        self,
        audio_stream: AsyncIterator[bytes],
        child_context: Optional[Dict[str, Any]] = None,
    ) -> AudioProcessingResult:
        """معالجة الصوت بشكل متدفق للتقليل من زمن الاستجابة"""

        start_time = time.time()
        self.processing_stats["total_requests"] += 1

        try:
            # تحويل البيانات إلى numpy array
            audio_data = await self._stream_to_numpy(audio_stream)

            # توليد مفتاح كاش
            cache_key = self._generate_cache_key(audio_data, child_context)

            # فحص الكاش أولاً
            if cached_result := self.preprocessing_cache.get(cache_key):
                self.processing_stats["cache_hits"] += 1
                self.logger.info("🎯 Cache hit for audio processing")
                return cached_result

            # 1. معالجة متوازية للصوت
            tasks = [
                self._noise_reduction(audio_data),
                self._voice_activity_detection(audio_data),
                self._extract_emotion_features(audio_data),
            ]

            processed_audio, vad_result, emotion_features = await asyncio.gather(*tasks)

            # 2. تحليل جودة الصوت
            quality_score = await self._assess_audio_quality(processed_audio)

            # 3. حساب الثقة
            confidence = self._calculate_confidence(
                vad_result, quality_score, emotion_features
            )

            # إنشاء النتيجة
            result = AudioProcessingResult(
                processed_audio=processed_audio,
                original_audio=audio_data,
                noise_level=await self._calculate_noise_level(audio_data),
                voice_activity_score=vad_result,
                emotion_features=emotion_features,
                processing_time_ms=(time.time() - start_time) * 1000,
                quality_score=quality_score,
                confidence=confidence,
            )

            # حفظ في الكاش
            self.preprocessing_cache[cache_key] = result

            # تحديث الإحصائيات
            self._update_processing_stats(result.processing_time_ms)

            return result

        except Exception as e:
            self.logger.error(f"❌ Audio processing failed: {e}")
            raise

    async def _stream_to_numpy(self, audio_stream: AsyncIterator[bytes]) -> np.ndarray:
        """تحويل stream إلى numpy array"""
        chunks = []
        async for chunk in audio_stream:
            chunks.append(np.frombuffer(chunk, dtype=np.int16))

        if not chunks:
            return np.array([], dtype=np.float32)

        audio_data = np.concatenate(chunks).astype(np.float32)
        # تطبيع البيانات
        if np.max(np.abs(audio_data)) > 0:
            audio_data = audio_data / np.max(np.abs(audio_data))

        return audio_data

    async def _noise_reduction(self, audio_data: np.ndarray) -> np.ndarray:
        """إزالة الضوضاء من الصوت"""
        try:
            if len(audio_data) < 1000:  # صوت قصير جداً
                return audio_data

            # تطبيق فلتر بسيط للضوضاء
            from scipy import signal

            b, a = signal.butter(4, 0.2, "high")
            filtered = signal.filtfilt(b, a, audio_data)

            return filtered.astype(np.float32)

        except Exception as e:
            self.logger.warning(f"Noise reduction failed: {e}")
            return audio_data

    async def _voice_activity_detection(self, audio_data: np.ndarray) -> float:
        """كشف النشاط الصوتي"""
        try:
            if self.vad is None:
                return 1.0  # افتراض وجود صوت

            # تحويل إلى التنسيق المطلوب للـ VAD
            audio_16bit = (audio_data * 32767).astype(np.int16)

            frame_length = int(self.config.sample_rate * 0.02)  # 20ms frames
            voice_frames = 0
            total_frames = 0

            for i in range(0, len(audio_16bit) - frame_length, frame_length):
                frame = audio_16bit[i : i + frame_length].tobytes()

                if self.vad.is_speech(frame, self.config.sample_rate):
                    voice_frames += 1
                total_frames += 1

            if total_frames == 0:
                return 0.0

            return voice_frames / total_frames

        except Exception as e:
            self.logger.warning(f"VAD failed: {e}")
            return 1.0

    async def _extract_emotion_features(
        self, audio_data: np.ndarray
    ) -> Dict[str, float]:
        """استخراج خصائص المشاعر من الصوت"""
        try:
            if len(audio_data) < 1000:
                return {}

            features = {}

            # الطاقة
            features["energy"] = float(np.sum(audio_data**2))

            # معدل عبور الصفر
            zero_crossings = np.where(np.diff(np.sign(audio_data)))[0]
            features["zero_crossing_rate"] = float(
                len(zero_crossings) / len(audio_data)
            )

            # الانحراف المعياري
            features["std_deviation"] = float(np.std(audio_data))

            # أقصى قيمة
            features["max_amplitude"] = float(np.max(np.abs(audio_data)))

            return features

        except Exception as e:
            self.logger.warning(f"Feature extraction failed: {e}")
            return {}

    async def _assess_audio_quality(self, audio_data: np.ndarray) -> float:
        """تقييم جودة الصوت"""
        try:
            if len(audio_data) == 0:
                return 0.0

            # حساب SNR تقريبي
            signal_power = np.mean(audio_data**2)

            if signal_power < 1e-10:
                return 0.0

            # تقدير الضوضاء
            silence_mask = np.abs(audio_data) < self.config.silence_threshold
            if np.any(silence_mask):
                noise_power = np.mean(audio_data[silence_mask] ** 2)
                if noise_power > 0:
                    snr = 10 * np.log10(signal_power / noise_power)
                    quality_score = min(1.0, max(0.0, (snr + 10) / 40))
                else:
                    quality_score = 1.0
            else:
                quality_score = 0.8

            return float(quality_score)

        except Exception as e:
            self.logger.warning(f"Quality assessment failed: {e}")
            return 0.5

    def _calculate_confidence(
        self, vad_score: float, quality_score: float, emotion_features: Dict[str, float]
    ) -> float:
        """حساب مستوى الثقة في النتيجة"""

        factors = [
            min(1.0, vad_score * 2),
            quality_score,
            min(1.0, len(emotion_features) / 10) if emotion_features else 0.0,
        ]

        return float(np.mean(factors))

    async def _calculate_noise_level(self, audio_data: np.ndarray) -> float:
        """حساب مستوى الضوضاء"""
        if len(audio_data) == 0:
            return 1.0

        silence_mask = np.abs(audio_data) < self.config.silence_threshold

        if np.any(silence_mask):
            noise_level = np.std(audio_data[silence_mask])
        else:
            noise_level = np.std(audio_data) * 0.1

        return float(noise_level)

    def _generate_cache_key(
        self, audio_data: np.ndarray, context: Optional[Dict[str, Any]]
    ) -> str:
        """توليد مفتاح كاش للصوت"""

        data_to_hash = []

        if len(audio_data) > 0:
            data_to_hash.extend(
                [len(audio_data), float(np.mean(audio_data)), float(np.std(audio_data))]
            )

        if context:
            data_to_hash.append(str(sorted(context.items())))

        hash_input = str(data_to_hash).encode("utf-8")
        return hashlib.md5(hash_input).hexdigest()

    def _update_processing_stats(float) -> None:
        """تحديث إحصائيات الأداء"""
        self.processing_stats["total_processing_time"] += processing_time
        self.processing_stats["average_processing_time"] = (
            self.processing_stats["total_processing_time"]
            / self.processing_stats["total_requests"]
        )

    def get_performance_stats(self) -> Dict[str, Any]:
        """الحصول على إحصائيات الأداء"""
        return {
            **self.processing_stats,
            "cache_hit_rate": (
                self.processing_stats["cache_hits"]
                / max(1, self.processing_stats["total_requests"])
            ),
            "cache_size": len(self.preprocessing_cache),
        }

    async def cleanup(self):
        """تنظيف الموارد"""
        try:
            # مسح الكاش
            self.preprocessing_cache.clear()
            self.response_cache.clear()

            # إغلاق OpenAI client
            if hasattr(self.openai_client, "close"):
                await self.openai_client.close()

            self.logger.info("✅ Audio processor cleanup completed")

        except Exception as e:
            self.logger.error(f"❌ Cleanup failed: {e}")


# Factory function للاستخدام مع dependency injection
def create_enhanced_audio_processor(
    config: Optional[AudioConfig] = None,
) -> EnhancedAudioProcessor:
    """إنشاء معالج صوت محسن"""
    return EnhancedAudioProcessor(config)


# Utility functions للاختبار
async def test_audio_processor():
    """اختبار سريع لمعالج الصوت"""

    processor = EnhancedAudioProcessor()

    # إنشاء صوت تجريبي
    sample_rate = 16000
    duration = 1.0
    frequency = 440  # A4 note

    t = np.linspace(0, duration, int(sample_rate * duration))
    test_audio = 0.5 * np.sin(2 * np.pi * frequency * t)

    # إضافة ضوضاء خفيفة
    noise = np.random.normal(0, 0.1, test_audio.shape)
    noisy_audio = test_audio + noise

    async def audio_stream():
        chunk_size = 1024
        for i in range(0, len(noisy_audio), chunk_size):
            chunk = noisy_audio[i : i + chunk_size].astype(np.int16).tobytes()
            yield chunk

    # معالجة الصوت
    result = await processor.process_audio_stream(audio_stream())

    logger.info("🎵 Audio Processing Test Results:")
    logger.info(f"   Original length: {len(test_audio)}")
    logger.info(f"   Processed length: {len(result.processed_audio)}")
    logger.info(f"   Quality score: {result.quality_score:.3f}")
    logger.info(f"   Voice activity: {result.voice_activity_score:.3f}")
    logger.info(f"   Processing time: {result.processing_time_ms:.1f}ms")
    logger.info(f"   Confidence: {result.confidence:.3f}")
    logger.info(f"   Emotion features: {len(result.emotion_features)}")

    # إحصائيات الأداء
    stats = processor.get_performance_stats()
    logger.info(f"   Performance stats: {stats}")

    await processor.cleanup()

    return result


if __name__ == "__main__":
    # تشغيل الاختبار
    asyncio.run(test_audio_processor())
