from typing import Any, Dict, List, Optional

#!/usr/bin/env python3
"""
🎤 Enhanced HUME AI Integration - 2025 Edition
تكامل متطور مع HUME AI يدعم:
- معايرة دقة تحليل المشاعر
- دعم اللغات المتعددة (العربية والإنجليزية) 
- تكامل البيانات التاريخية
- معالجة Batch و Stream متقدمة
- مراقبة الأداء والجودة
"""

import asyncio
import hashlib
import json
import logging
import os
import statistics
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import aiofiles
import numpy as np

# Third-party imports
try:
    import librosa
    import soundfile as sf
    from hume import AsyncHumeClient, HumeClient
    HUME_AVAILABLE = True
except ImportError as e:
    HUME_AVAILABLE = False
    logging.warning(f"HUME AI SDK not available: {e}")

from ..domain.entities.child import Child
# Internal imports
from ..infrastructure.persistence.conversation_sqlite_repository import \
    ConversationSQLiteRepository
from ..infrastructure.security.audit_logger import AuditLogger


class Language(Enum):
    """Supported languages for emotion analysis"""
    ARABIC = "ar"
    ENGLISH = "en"
    AUTO_DETECT = "auto"


class AnalysisMode(Enum):
    """Analysis processing modes"""
    STREAM = "stream"
    BATCH = "batch"
    HYBRID = "hybrid"


@dataclass
class EmotionCalibrationConfig:
    """Configuration for emotion analysis calibration"""
    confidence_threshold: float = 0.7
    energy_threshold: float = 0.3
    minimum_duration: float = 1.0  # seconds
    maximum_duration: float = 30.0  # seconds
    sample_rate: int = 16000
    language_weights: Dict[str, float] = None
    
    def __post_init__(self):
        if self.language_weights is None:
            self.language_weights = {
                Language.ARABIC.value: 1.0,
                Language.ENGLISH.value: 0.9,
                Language.AUTO_DETECT.value: 0.8
            }


@dataclass
class EmotionAnalysisResult:
    """Result of emotion analysis with enhanced metadata"""
    session_id: Optional[str]
    udid: str
    child_name: str
    child_age: int
    language: Language
    mode: AnalysisMode
    dominant_emotion: str
    emotions: Dict[str, float]
    confidence: float
    energy_level: float
    voice_quality: float
    emotional_intensity: float
    developmental_indicators: Dict[str, Any]
    processing_time: float
    audio_duration: float
    audio_hash: str
    timestamp: datetime
    calibration_applied: bool = False
    historical_context: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        result['language'] = self.language.value
        result['mode'] = self.mode.value
        return result


class EnhancedHumeIntegration:
    """
    🎭 Enhanced HUME AI Integration with 2025 standards
    
    Features:
    - Emotion calibration with confidence thresholds
    - Multi-language support (Arabic/English)
    - Historical data integration
    - Performance monitoring
    - Advanced error handling
    - Async processing with thread pools
    """
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        calibration_config: Optional[EmotionCalibrationConfig] = None
    ):
        """
        Initialize enhanced HUME integration
        
        Args:
            api_key: HUME API key (from env if not provided)
            calibration_config: Calibration settings
        """
        self.api_key = api_key or os.getenv("HUME_API_KEY")
        if not self.api_key:
            raise ValueError("❌ HUME API Key required! Set HUME_API_KEY environment variable")
        
        self.calibration_config = calibration_config or EmotionCalibrationConfig()
        self.logger = logging.getLogger(__name__)
        self.audit_logger = AuditLogger()
        
        # Initialize repositories
        self.conversation_repo = ConversationSQLiteRepository()
        
        # Performance tracking
        self.performance_metrics = {
            "total_analyses": 0,
            "successful_analyses": 0,
            "average_processing_time": 0.0,
            "calibration_adjustments": 0,
            "language_distribution": {lang.value: 0 for lang in Language}
        }
        
        # Initialize HUME clients if available
        if HUME_AVAILABLE:
            self.client = HumeClient(api_key=self.api_key)
            self.async_client = AsyncHumeClient(api_key=self.api_key)
            self.logger.info("✅ HUME AI clients initialized successfully")
        else:
            self.client = None
            self.async_client = None
            self.logger.warning("⚠️ HUME AI SDK not available - running in mock mode")
        
        # Thread pool for CPU-intensive operations
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        self.logger.info(f"🎤 Enhanced HUME Integration initialized")

    # ==================== CALIBRATION METHODS ====================
    
    async def calibrate_hume(
        self, 
        confidence_threshold: float = 0.7,
        test_audio_samples: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        🎯 معايرة دقة تحليل المشاعر
        
        Args:
            confidence_threshold: حد الثقة المطلوب (0.0-1.0)
            test_audio_samples: عينات صوتية للاختبار
            
        Returns:
            نتائج المعايرة وإحصائيات الأداء
        """
        self.logger.info(f"🎯 Starting emotion analysis calibration (threshold: {confidence_threshold})")
        
        try:
            # استخدام عينات افتراضية إذا لم تُمرر
            if not test_audio_samples:
                test_audio_samples = await self._create_calibration_samples()
            
            calibration_results = []
            total_processing_time = 0
            
            for i, audio_path in enumerate(test_audio_samples, 1):
                self.logger.info(f"📊 Testing sample {i}/{len(test_audio_samples)}: {audio_path}")
                
                start_time = datetime.now()
                
                # تحليل العينة
                result = await self.analyze_emotion_multilang(
                    audio_file=audio_path,
                    language=Language.AUTO_DETECT,
                    udid=f"CALIBRATION_TEST_{i}",
                    child_name="Test Child",
                    child_age=6
                )
                
                processing_time = (datetime.now() - start_time).total_seconds()
                total_processing_time += processing_time
                
                # تقييم النتيجة
                calibration_score = self._evaluate_calibration_result(
                    result, confidence_threshold
                )
                
                calibration_results.append({
                    "sample": audio_path,
                    "confidence": result.confidence if result else 0.0,
                    "processing_time": processing_time,
                    "passes_threshold": calibration_score["passes_threshold"],
                    "quality_score": calibration_score["quality_score"],
                    "emotions_detected": len(result.emotions) if result else 0
                })
            
            # حساب إحصائيات المعايرة
            avg_confidence = statistics.mean([r["confidence"] for r in calibration_results])
            avg_processing_time = total_processing_time / len(test_audio_samples)
            success_rate = sum(1 for r in calibration_results if r["passes_threshold"]) / len(calibration_results)
            
            # تحديث إعدادات المعايرة
            self.calibration_config.confidence_threshold = confidence_threshold
            
            # حفظ نتائج المعايرة
            calibration_summary = {
                "timestamp": datetime.now().isoformat(),
                "confidence_threshold": confidence_threshold,
                "samples_tested": len(test_audio_samples),
                "average_confidence": avg_confidence,
                "average_processing_time": avg_processing_time,
                "success_rate": success_rate,
                "recommendation": self._get_calibration_recommendation(
                    avg_confidence, success_rate
                ),
                "detailed_results": calibration_results
            }
            
            # حفظ في ملف
            await self._save_calibration_results(calibration_summary)
            
            self.performance_metrics["calibration_adjustments"] += 1
            
            self.logger.info(f"✅ Calibration completed: {success_rate:.1%} success rate")
            
            return calibration_summary
            
        except Exception as e:
            self.logger.error(f"❌ Calibration failed: {e}")
            await self.audit_logger.log_error("calibration_failed", str(e))
            return {"error": str(e), "status": "failed"}

    def _evaluate_calibration_result(
        self, 
        result: Optional[EmotionAnalysisResult], 
        threshold: float
    ) -> Dict[str, Any]:
        """تقييم نتيجة المعايرة"""
        if not result:
            return {"passes_threshold": False, "quality_score": 0.0}
        
        passes_threshold = result.confidence >= threshold
        
        # حساب نقاط الجودة
        quality_factors = [
            result.confidence,
            result.voice_quality,
            min(1.0, len(result.emotions) / 5),  # تنوع المشاعر
            1.0 if result.processing_time < 5.0 else 0.5  # سرعة المعالجة
        ]
        
        quality_score = statistics.mean(quality_factors)
        
        return {
            "passes_threshold": passes_threshold,
            "quality_score": quality_score
        }

    def _get_calibration_recommendation(
        self, 
        avg_confidence: float, 
        success_rate: float
    ) -> str:
        """توصيات المعايرة"""
        if success_rate >= 0.9 and avg_confidence >= 0.8:
            return "Excellent: System is well calibrated"
        elif success_rate >= 0.7:
            return "Good: Consider slight threshold adjustment"
        elif success_rate >= 0.5:
            return "Fair: Threshold may be too high, consider lowering"
        else:
            return "Poor: Significant calibration needed, check audio quality"

    # ==================== MULTI-LANGUAGE SUPPORT ====================
    
    async def analyze_emotion_multilang(
        self,
        audio_file: Union[str, bytes],
        language: Language = Language.AUTO_DETECT,
        udid: str = "UNKNOWN",
        child_name: str = "Unknown Child",
        child_age: int = 6,
        mode: AnalysisMode = AnalysisMode.STREAM
    ) -> Optional[EmotionAnalysisResult]:
        """
        🌍 تحليل المشاعر مع دعم اللغات المتعددة
        
        Args:
            audio_file: مسار الملف أو البيانات الصوتية
            language: اللغة المستهدفة
            udid: معرف الجهاز
            child_name: اسم الطفل
            child_age: عمر الطفل
            mode: نمط التحليل
            
        Returns:
            نتيجة تحليل المشاعر مع السياق اللغوي
        """
        start_time = datetime.now()
        
        try:
            self.logger.info(f"🌍 Starting multilingual emotion analysis (language: {language.value})")
            
            # تحضير الملف الصوتي
            audio_data, audio_path, audio_hash = await self._prepare_audio_file(audio_file)
            
            if not audio_data:
                return None
            
            # كشف اللغة إذا كان مطلوباً
            detected_language = language
            if language == Language.AUTO_DETECT:
                detected_language = await self._detect_language(audio_data)
                self.logger.info(f"🔍 Language detected: {detected_language.value}")
            
            # تطبيق إعدادات خاصة باللغة
            config = self._get_language_specific_config(detected_language)
            
            # تحليل المشاعر
            hume_result = await self._perform_hume_analysis(
                audio_data, config, mode
            )
            
            if not hume_result:
                return None
            
            # استخراج البيانات
            emotions = self._extract_emotions_from_hume(hume_result)
            
            # تطبيق المعايرة
            calibrated_emotions = self._apply_calibration(emotions, detected_language)
            
            # حساب المقاييس
            dominant_emotion = max(calibrated_emotions, key=calibrated_emotions.get)
            confidence = self._calculate_confidence(calibrated_emotions, detected_language)
            
            # معالجة البيانات التاريخية
            historical_context = await self._get_historical_context(udid, child_age)
            
            # إنشاء النتيجة
            result = EmotionAnalysisResult(
                session_id=None,  # سيتم تعيينه عند الحفظ
                udid=udid,
                child_name=child_name,
                child_age=child_age,
                language=detected_language,
                mode=mode,
                dominant_emotion=dominant_emotion,
                emotions=calibrated_emotions,
                confidence=confidence,
                energy_level=self._calculate_energy_level(audio_data),
                voice_quality=self._assess_voice_quality(audio_data),
                emotional_intensity=self._calculate_emotional_intensity(calibrated_emotions),
                developmental_indicators=self._assess_developmental_indicators(
                    calibrated_emotions, child_age, detected_language
                ),
                processing_time=(datetime.now() - start_time).total_seconds(),
                audio_duration=len(audio_data) / self.calibration_config.sample_rate,
                audio_hash=audio_hash,
                timestamp=datetime.now(),
                calibration_applied=True,
                historical_context=historical_context
            )
            
            # حفظ النتيجة
            await self._save_analysis_result(result)
            
            # تحديث الإحصائيات
            self._update_performance_metrics(result)
            
            self.logger.info(f"✅ Analysis completed: {dominant_emotion} ({confidence:.2f})")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Multilingual analysis failed: {e}")
            await self.audit_logger.log_error("multilingual_analysis_failed", str(e))
            return None

    def _get_language_specific_config(self, language: Language) -> Dict[str, Any]:
        """إعدادات خاصة بكل لغة"""
        base_config = {"prosody": {}, "language": {}}
        
        if language == Language.ARABIC:
            base_config.update({
                "prosody": {
                    "granularity": "word",
                    "identify_speakers": False
                },
                "language": {
                    "granularity": "word",
                    "identify_speakers": False
                }
            })
        elif language == Language.ENGLISH:
            base_config.update({
                "prosody": {
                    "granularity": "utterance",
                    "identify_speakers": False
                }
            })
        
        return base_config

    async def _detect_language(self, audio_data: bytes) -> Language:
        """كشف اللغة من الصوت (محاكاة - يمكن تطوير نموذج حقيقي)"""
        # للآن، محاكاة بسيطة - يمكن تطوير نموذج ML حقيقي
        
        # تحليل خصائص صوتية بسيطة
        try:
            import io
            audio_io = io.BytesIO(audio_data)
            y, sr = librosa.load(audio_io, sr=self.calibration_config.sample_rate)
            
            # تحليل طيفي بسيط (يمكن تحسينه)
            spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
            avg_centroid = np.mean(spectral_centroid)
            
            # قاعدة بسيطة للتمييز (تحتاج تطوير)
            if avg_centroid > 2000:
                return Language.ENGLISH
            else:
                return Language.ARABIC
                
        except Exception as e:
    logger.error(f"Error: {e}", exc_info=True)as e:
    logger.error(f"Error: {e}", exc_info=True)            # الافتراضي: العربية
            return Language.ARABIC

    def _apply_calibration(
        self, 
        emotions: Dict[str, float], 
        language: Language
    ) -> Dict[str, float]:
        """تطبيق المعايرة على النتائج"""
        language_weight = self.calibration_config.language_weights.get(
            language.value, 1.0
        )
        
        calibrated = {}
        for emotion, score in emotions.items():
            # تطبيق وزن اللغة
            adjusted_score = score * language_weight
            
            # تطبيق حد الثقة
            if adjusted_score >= self.calibration_config.confidence_threshold:
                calibrated[emotion] = min(adjusted_score, 1.0)
            else:
                calibrated[emotion] = adjusted_score * 0.8  # تقليل النتائج ضعيفة الثقة
        
        return calibrated

    # ==================== HISTORICAL DATA INTEGRATION ====================
    
    async def merge_historical_data(
        self,
        device_id: str,
        start_date: datetime,
        end_date: datetime,
        include_trends: bool = True
    ) -> Dict[str, Any]:
        """
        📊 تكامل البيانات التاريخية مع تحليل HUME
        
        Args:
            device_id: معرف الجهاز
            start_date: تاريخ البداية
            end_date: تاريخ النهاية
            include_trends: تضمين تحليل الاتجاهات
            
        Returns:
            البيانات التاريخية المدمجة مع تحليلات متقدمة
        """
        self.logger.info(f"📊 Merging historical data for {device_id} ({start_date} to {end_date})")
        
        try:
            # جلب البيانات التاريخية
            historical_sessions = await self._fetch_historical_sessions(
                device_id, start_date, end_date
            )
            
            if not historical_sessions:
                return {"error": "No historical data found", "sessions": 0}
            
            # تجميع البيانات العاطفية
            emotion_timeline = []
            daily_summaries = {}
            
            for session in historical_sessions:
                session_data = await self._process_historical_session(session)
                if session_data:
                    emotion_timeline.append(session_data)
                    
                    # تجميع يومي
                    date_key = session['timestamp'].date().isoformat()
                    if date_key not in daily_summaries:
                        daily_summaries[date_key] = {
                            "sessions": 0,
                            "emotions": {},
                            "avg_confidence": 0.0,
                            "total_duration": 0.0
                        }
                    
                    daily_summaries[date_key]["sessions"] += 1
                    daily_summaries[date_key]["total_duration"] += session_data.get("duration", 0)
                    
                    # دمج المشاعر
                    for emotion, score in session_data.get("emotions", {}).items():
                        if emotion not in daily_summaries[date_key]["emotions"]:
                            daily_summaries[date_key]["emotions"][emotion] = []
                        daily_summaries[date_key]["emotions"][emotion].append(score)
            
            # حساب المتوسطات اليومية
            for date_summary in daily_summaries.values():
                for emotion, scores in date_summary["emotions"].items():
                    date_summary["emotions"][emotion] = statistics.mean(scores)
            
            # تحليل الاتجاهات
            trends_analysis = {}
            if include_trends:
                trends_analysis = await self._analyze_historical_trends(
                    emotion_timeline, daily_summaries
                )
            
            # إحصائيات عامة
            total_sessions = len(emotion_timeline)
            date_range = (end_date - start_date).days
            
            # أكثر المشاعر شيوعاً
            all_emotions = {}
            for session in emotion_timeline:
                for emotion, score in session.get("emotions", {}).items():
                    if emotion not in all_emotions:
                        all_emotions[emotion] = []
                    all_emotions[emotion].append(score)
            
            most_common_emotions = {
                emotion: statistics.mean(scores) 
                for emotion, scores in all_emotions.items()
            }
            most_common_emotions = dict(sorted(
                most_common_emotions.items(), 
                key=lambda x: x[1], 
                reverse=True
            ))
            
            # تحضير النتيجة الشاملة
            merged_data = {
                "device_id": device_id,
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                    "days": date_range
                },
                "statistics": {
                    "total_sessions": total_sessions,
                    "avg_sessions_per_day": total_sessions / max(date_range, 1),
                    "most_common_emotions": most_common_emotions,
                    "emotional_stability": self._calculate_emotional_stability(emotion_timeline)
                },
                "daily_summaries": daily_summaries,
                "emotion_timeline": emotion_timeline,
                "trends_analysis": trends_analysis,
                "generated_at": datetime.now().isoformat()
            }
            
            # حفظ التحليل المدمج
            await self._save_historical_analysis(device_id, merged_data)
            
            self.logger.info(f"✅ Historical data merged: {total_sessions} sessions analyzed")
            
            return merged_data
            
        except Exception as e:
            self.logger.error(f"❌ Historical data merge failed: {e}")
            return {"error": str(e), "status": "failed"}

    async def _get_historical_context(
        self, 
        udid: str, 
        child_age: int,
        days_back: int = 7
    ) -> Dict[str, Any]:
        """جلب السياق التاريخي للطفل"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            recent_data = await self.merge_historical_data(
                udid, start_date, end_date, include_trends=False
            )
            
            if recent_data.get("error"):
                return {"recent_sessions": 0}
            
            stats = recent_data.get("statistics", {})
            
            return {
                "recent_sessions": stats.get("total_sessions", 0),
                "dominant_recent_emotion": list(stats.get("most_common_emotions", {}).keys())[0] if stats.get("most_common_emotions") else "neutral",
                "emotional_stability": stats.get("emotional_stability", 0.5),
                "pattern_consistency": self._assess_pattern_consistency(recent_data),
                "age_appropriate_development": self._assess_age_development(stexcept Exception as e:
    logger.error(f"Error: {e}", exc_info=True)           }
            
        except Exception as e:
    logger.error(f"Error: {e}", exc_info=True)            return {"recent_sessions": 0}

    def _calculate_emotional_stability(self, emotion_timeline: List[Dict]) -> float:
        """حساب الاستقرار العاطفي"""
        if len(emotion_timeline) < 2:
            return 0.5
        
        try:
            # حساب التباين في المشاعر المهيمنة
            dominant_emotions = [session.get("dominant_emotion", "neutral") for session in emotion_timeline]
            
            # حساب التنوع
            unique_emotions = len(set(dominant_emotions))
            total_sessions = len(dominant_emotions)
            
            # حساب الاستقرار (قلة التنوع = استقرار أكبر)
            stability = 1.0 - (unique_emotions / min(toexcept Exception as e:
    logger.error(f"Error: {e}", exc_info=True))
            
            return max(0.0, min(1.0, stability))
            
        except Exception as e:
    logger.error(f"Error: {e}", exc_info=True)            return 0.5

    # ==================== HELPER METHODS ====================
    
    async def _prepare_audio_file(self, audio_file: Union[str, bytes]) -> Tuple[bytes, str, str]:
        """تحضير الملف الصوتي للتحليل"""
        if isinstance(audio_file, str):
            # ملف path
            if not Path(audio_file).exists():
                raise FileNotFoundError(f"Audio file not found: {audio_file}")
            
            async with aiofiles.open(audio_file, 'rb') as f:
                audio_data = await f.read()
            
            audio_path = audio_file
        else:
            # بيانات raw
            audio_data = audio_file
            audio_path = "in_memory_audio"
        
        # حساب hash للملف
        audio_hash = hashlib.md5(audio_data).hexdigest()
        
        return audio_data, audio_path, audio_hash

    async def _perform_hume_analysis(
        self, 
        audio_data: bytes, 
        config: Dict[str, Any], 
        mode: AnalysisMode
    ) -> Optional[Dict[str, Any]]:
        """تنفيذ تحليل HUME فعلي"""
        if not HUME_AVAILABLE:
            # وضع المحاكاة للتطوير
            return self._mock_hume_analysis(audio_data)
        
        try:
            if mode == AnalysisMode.STREAM:
                # Stream mode
                socket = await self.async_client.expression_measurement.stream.connect(config=config)
                result = await socket.send_bytes(audio_data)
                await socket.close()
                return result
            else:
                # Batch mode
                job = self.client.expression_measurement.batch.submit_job(
                    urls=[audio_data],  # إرسال البيانات مباشرة
                    configs=[config]
                )
                
                # انتظار النتيجة
                while job.state not in ["COMPLETED", "FAILED"]:
                    await asyncio.sleep(2)
                    job = self.client.expression_measurement.batch.get_job_details(job.job_id)
                
                if job.state == "COMPLETED":
                    return self.client.expression_measurement.batch.get_job_predictions(job.job_id)
                else:
                    return None
                    
        except Exception as e:
            self.logger.error(f"HUME analysis failed: {e}")
            return None

    def _mock_hume_analysis(self, audio_data: bytes) -> Dict[str, Any]:
        """محاكاة تحليل HUME للتطوير"""
        import random
        
        emotions = [
            "Joy", "Sadness", "Anger", "Fear", "Surprise", 
            "Curiosity", "Excitement", "Calmness", "Playfulness"
        ]
        
        return {
            "prosody": {
                "predictions": [
                    {
                        "name": emotion,
                        "score": random.uniform(0.1, 0.9)
                    }
                    for emotion in emotions
                ]
            }
        }

    def _extract_emotions_from_hume(self, hume_result: Dict[str, Any]) -> Dict[str, float]:
        """استخراج المشاعر من نتيجة HUME"""
        emotions = {}
        
        try:
            if "prosody" in hume_result:
                predictions = hume_result["prosody"].get("predictions", [])
                for pred in predictions:
                    emotions[pred.get("name", "unknown")] = pred.get("score", 0.0)
        except Exception as e:
            self.logger.error(f"Error extracting emotions: {e}")
        
        return emotions

    def _calculate_confidence(self, emotions: Dict[str, float], language: Language) -> float:
        """حساب مستوى الثقة الإجمالي"""
        if not emotions:
            return 0.0
        
        # حساب الثقة بناءً على توزيع المشاعر ووزن اللغة
        max_score = max(emotions.values())
        score_variance = statistics.variance(emotions.values()) if len(emotions) > 1 else 0
        language_weight = self.calibration_config.language_weights.get(language.value, 1.0)
        
        # تجميع العوامل
        confidence = (max_score * 0.6 + (1 - score_variance) * 0.3 + language_weight * 0.1)
        
        return min(1.0, max(0.0, confidence))

    # حفظ في ملف...
    async def _save_analysis_result(self, result: EmotionAnalysisResult) -> None:
        """حفظ نتيجة التحليل في قاعدة البيانات"""
        try:
            # حفظ في conversation repository
            session_id = await self.conversation_repo.save_emotion_analysis(result.to_dict())
            result.session_id = session_id
            
            self.logger.debug(f"Analysis result saved with session_id: {session_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to save analysis result: {e}")

    async def _create_calibration_samples(self) -> List[str]:
        """إنشاء عينات معايرة تلقائية"""
        sample_files = []
        
        try:
            # إنشاء عينات صوتية متنوعة للمعايرة
            emotions_samples = [
                ("joy", 440, 0.8),      # فرح - تردد عالي، طاقة عالية
                ("sadness", 220, 0.3),   # حزن - تردد منخفض، طاقة منخفضة
                ("anger", 300, 0.9),     # غضب - تردد متوسط، طاقة عالية
                ("calm", 260, 0.4),      # هدوء - تردد منخفض، طاقة منخفضة
                ("excitement", 500, 0.95) # إثارة - تردد عالي، طاقة عالية جداً
            ]
            
            for emotion, freq, energy in emotions_samples:
                filename = f"calibration_{emotion}.wav"
                
                # إنشاء موجة صوتية محاكية
                duration = 3.0
                sample_rate = self.calibration_config.sample_rate
                t = np.linspace(0, duration, int(sample_rate * duration))
                
                # موجة أساسية مع تشويش طبيعي
                audio = energy * 0.3 * np.sin(2 * np.pi * freq * t)
                
                # إضافة تشويش وتنوع
                noise = 0.05 * np.random.random(len(audio))
                audio = audio + noise
                
                # تطبيق تأثيرات عاطفية
                if emotion == "joy":
                    # تردد متزايد للفرح
                    audio = audio * (1 + 0.1 * np.sin(2 * np.pi * 2 * t))
                elif emotion == "sadness":
                    # تردد متناقص للحزن
                    audio = audio * (1 - 0.05 * t / duration)
                
                # حفظ الملف
                sf.write(filename, audio, sample_rate)
                sample_files.append(filename)
                
                self.logger.debug(f"Created calibration sample: {filename}")
            
            return sample_files
            
        except Exception as e:
            self.logger.error(f"Failed to create calibration samples: {e}")
            return []

    # نهاية الملف - مع مساحة للتوسع
    def _calculate_energy_level(self, audio_data: bytes) -> float:
        """حساب مستوى الطاقة الصوتية"""
        try:
            import io
            audio_io = io.BytesIO(audio_data)
            y, sr = librosa.load(audio_io, sr=self.calibration_config.sample_rate)
            
            # حساب RMS energy
            rms = librosa.feature.rms(y=y)[0]
            return min(1.0, float(np.mean(rms) * 10))  # تطبيع إلى 0-1
            
        except Exception as e:
            return 0.5  # قيمة افتراضية

    def _assess_voice_quality(self, audio_data: bytes) -> float:
        """تقييم جودة الصوت"""
        try:
            import io
            audio_io = io.BytesIO(audio_data)
            y, sr = librosa.load(audio_io, sr=self.calibration_config.sample_rate)
            
            # حساب SNR تقريبي
            signal_power = np.mean(y ** 2)
            noise_estimate = np.mean(np.abs(np.diff(y))) * 0.1
            
            if noise_estimate > 0:
                snr = 10 * np.log10(signal_power / noise_estimate)
                quality = min(1.0, maxexcept Exception as e:
    logger.error(f"Error: {e}", exc_info=True)/ 40))  # تحويل لمقياس 0-1
            else:
                quality = 1.0
            
            return quality
            
        except Exception as e:
    logger.error(f"Error: {e}", exc_info=True)            return 0.7  # جودة افتراضية مقبولة

    def _calculate_emotional_intensity(self, emotions: Dict[str, float]) -> float:
        """حساب شدة المشاعر الإجمالية"""
        if not emotions:
            return 0.0
        
        # حساب التباين والمتوسط
        scores = list(emotions.values())
        max_score = max(scores)
        mean_score = statistics.mean(scores)
        
        # الشدة = أقصى نقاط + التوزيع
        intensity = (max_score * 0.7) + (mean_score * 0.3)
        
        return min(1.0, intensity)

    def _assess_developmental_indicators(
        self, 
        emotions: Dict[str, float], 
        child_age: int, 
        language: Language
    ) -> Dict[str, Any]:
        """تقييم المؤشرات التطويرية"""
        indicators = {
            "emotional_vocabulary": len(emotions),
            "emotional_range": max(emotions.values()) - min(emotions.values()) if emotions else 0,
            "age_appropriate": True,  # يحتاج تطوير نموذج متقدم
            "language_development": "normal",  # placeholder
            "social_emotional_score": statistics.mean(emotions.values()) if emotions else 0.5
        }
        
        # تقييمات حسب العمر
        if child_age < 4:
            indicators["expected_emotions"] = ["joy", "sadness", "anger"]
        elif child_age < 7:
            indicators["expected_emotions"] = ["joy", "sadness", "anger", "fear", "excitement"]
        else:
            indicators["expected_emotions"] = list(emotions.keys())
        
        return indicators

    def _update_performance_metrics(self, result: EmotionAnalysisResult) -> None:
        """تحديث مقاييس الأداء"""
        self.performance_metrics["total_analyses"] += 1
        
        if result.confidence >= self.calibration_config.confidence_threshold:
            self.performance_metrics["successful_analyses"] += 1
        
        # تحديث متوسط وقت المعالجة
        current_avg = self.performance_metrics["average_processing_time"]
        total = self.performance_metrics["total_analyses"]
        new_avg = ((current_avg * (total - 1)) + result.processing_time) / total
        self.performance_metrics["average_processing_time"] = new_avg
        
        # توزيع اللغات
        self.performance_metrics["language_distribution"][result.language.value] += 1

    async def get_performance_report(self) -> Dict[str, Any]:
        """الحصول على تقرير الأداء"""
        success_rate = 0.0
        if self.performance_metrics["total_analyses"] > 0:
            success_rate = (
                self.performance_metrics["successful_analyses"] / 
                self.performance_metrics["total_analyses"]
            )
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_analyses": self.performance_metrics["total_analyses"],
            "success_rate": success_rate,
            "average_processing_time": self.performance_metrics["average_processing_time"],
            "calibration_adjustments": self.performance_metrics["calibration_adjustments"],
            "language_distribution": self.performance_metrics["language_distribution"],
            "system_health": "excellent" if success_rate > 0.9 else "good" if success_rate > 0.7 else "needs_attention"
        }

    async def __aenter__(self):
        """Context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup resources"""
        if self.executor:
            self.executor.shutdown(wait=True)
        self.logger.info("🎤 Enhanced HUME Integration closed") 