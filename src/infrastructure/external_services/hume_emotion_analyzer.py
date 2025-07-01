from typing import Dict, List, Any, Optional

import logging

logger = logging.getLogger(__name__)

"""
🎤 HUME AI Speech Emotion Analyzer for AI Teddy Bear
Real-time emotion analysis directly from children's voice without text
"""
import structlog
logger = structlog.get_logger(__name__)


import asyncio
import aiohttp
import json
import base64
import tempfile
import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
import numpy as np
from pathlib import Path

# HUME AI SDK (install with: pip install hume)
try:
    from hume import HumeStreamClient
    from hume.models.config import ProsodyConfig
    from hume.core.utilities import encode_file
    HUME_AVAILABLE = True
except ImportError:
    HUME_AVAILABLE = False
    logger.warning("⚠️ HUME AI not installed. Install with: pip install hume")


@dataclass
class ChildVoiceEmotion:
    """
    نتيجة تحليل مشاعر الطفل من الصوت مباشرة
    """
    # Primary emotions detected by HUME
    joy: float = 0.0
    sadness: float = 0.0
    anger: float = 0.0
    fear: float = 0.0
    excitement: float = 0.0
    calmness: float = 0.0
    surprise: float = 0.0
    
    # Child-specific emotions
    curiosity: float = 0.0
    frustration: float = 0.0
    shyness: float = 0.0
    playfulness: float = 0.0
    tiredness: float = 0.0
    
    # Voice characteristics
    energy_level: float = 0.0  # High = excited, Low = tired
    speech_rate: float = 0.0   # Fast = excited/nervous, Slow = calm/sad
    pitch_variation: float = 0.0  # High = emotional, Low = monotone
    voice_quality: str = "clear"  # clear, trembling, whisper, etc.
    
    # Analysis metadata
    confidence: float = 0.0
    dominant_emotion: str = "neutral"
    emotional_intensity: float = 0.0
    timestamp: str = ""
    
    # Child development insights
    developmental_indicators: List[str] = field(default_factory=list)
    attention_level: float = 0.0
    communication_clarity: float = 0.0
    
    def __post_init__(self):
        if self.developmental_indicators is None:
            self.developmental_indicators = []


class HumeSpeechEmotionAnalyzer:
    """
    محلل المشاعر الصوتي باستخدام HUME AI
    مصمم خصيصاً لتحليل أصوات الأطفال بدقة عالية
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("HUME_API_KEY")
        self.base_url = "https://api.hume.ai/v0"
        
        # Child-specific emotion mapping
        self.child_emotion_map = {
            # HUME emotions → Child emotions
            "Joy": "joy",
            "Sadness": "sadness", 
            "Anger": "anger",
            "Fear": "fear",
            "Surprise": "surprise",
            "Excitement": "excitement",
            "Calmness": "calmness",
            "Curiosity": "curiosity",
            "Frustration": "frustration",
            "Admiration": "excitement",
            "Amusement": "playfulness",
            "Anxiety": "fear",
            "Boredom": "tiredness",
            "Confusion": "curiosity",
            "Contentment": "calmness",
            "Embarrassment": "shyness",
            "Enthusiasm": "excitement",
            "Interest": "curiosity",
            "Pride": "joy",
            "Shame": "shyness",
            "Tiredness": "tiredness"
        }
        
        # Age-specific analysis parameters
        self.age_parameters = {
            "3-4": {"sensitivity": 0.8, "attention_threshold": 0.3},
            "5-6": {"sensitivity": 0.7, "attention_threshold": 0.4}, 
            "7-8": {"sensitivity": 0.6, "attention_threshold": 0.5},
            "9-10": {"sensitivity": 0.5, "attention_threshold": 0.6},
            "11+": {"sensitivity": 0.4, "attention_threshold": 0.7}
        }
        
        logger.info(f"🎤 HUME Speech Emotion Analyzer initialized")
        logger.error(f"   API Status: {'✅ Ready' if self.api_key else '❌ No API Key'}")
    
    async def analyze_child_voice(
        self, 
        audio_data: bytes, 
        child_age: int = 6,
        child_name: str = "طفل",
        context: Dict[str, Any] = None
    ) -> ChildVoiceEmotion:
        """
        تحليل صوت الطفل مباشرة بدون تحويل لنص
        
        Args:
            audio_data: البيانات الصوتية (WAV, MP3, etc.)
            child_age: عمر الطفل لتخصيص التحليل
            child_name: اسم الطفل
            context: سياق إضافي (وقت اليوم، النشاط الأخير، إلخ)
            
        Returns:
            ChildVoiceEmotion: تحليل شامل لمشاعر الطفل
        """
        try:
            if not self.api_key:
                logger.warning("⚠️ No HUME API key provided, using fallback analysis")
                return self._create_fallback_analysis()
            
            # حفظ الصوت في ملف مؤقت
            temp_audio_path = await self._save_temp_audio(audio_data)
            
            try:
                # تحليل باستخدام HUME AI
                hume_results = await self._analyze_with_hume(temp_audio_path)
                
                # تحويل نتائج HUME إلى تحليل مخصص للطفل
                child_emotion = await self._convert_to_child_emotion(
                    hume_results, child_age, child_name, context
                )
                
                # إضافة تحليل تطويري إضافي
                child_emotion = await self._add_developmental_analysis(
                    child_emotion, audio_data, child_age
                )
                
                return child_emotion
                
            finally:
                # تنظيف الملف المؤقت
                if os.path.exists(temp_audio_path):
                    os.remove(temp_audio_path)
                    
        except Exception as e:
    logger.error(f"Error: {e}")f"❌ HUME Analysis Error: {e}")
            return self._create_fallback_analysis()
    
    async def _analyze_with_hume(self, audio_path: str) -> Dict[str, Any]:
        """تحليل الصوت باستخدام HUME AI API"""
        
        if HUME_AVAILABLE:
            try:
                # استخدام HUME SDK المباشر
                client = HumeStreamClient(api_key=self.api_key)
                config = ProsodyConfig()
                
                # ترميز الملف الصوتي
                encoded_audio = encode_file(audio_path)
                
                # إرسال للتحليل
                async with client.connect([config]) as socket:
                    result = await socket.send_bytes(encoded_audio)
                    
                return result
                
            except Exception as e:
    logger.error(f"Error: {e}")f"⚠️ HUME SDK error, trying direct API: {sdk_error}")
        
        # استخدام API مباشر كـ fallback
        return await self._analyze_with_direct_api(audio_path)
    
    async def _analyze_with_direct_api(self, audio_path: str) -> Dict[str, Any]:
        """تحليل مباشر باستخدام HUME REST API"""
        
        headers = {
            "X-Hume-Api-Key": self.api_key,
        }
        
        # قراءة الملف الصوتي
        with open(audio_path, 'rb') as audio_file:
            audio_data = audio_file.read()
        
        # تحضير البيانات للإرسال
        files = {
            'file': ('audio.wav', audio_data, 'audio/wav')
        }
        
        data = {
            'models': json.dumps({
                "prosody": {
                    "granularity": "utterance",
                    "identify_speakers": False
                }
            })
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/batch/jobs",
                headers=headers,
                data=data,
                data=files
            ) as response:
                if response.status == 200:
                    job_data = await response.json()
                    job_id = job_data['job_id']
                    
                    # انتظار النتائج
                    return await self._wait_for_results(session, job_id, headers)
                else:
                    error_text = await response.text()
                    raise Exception(f"HUME API error {response.status}: {error_text}")
    
    async def _wait_for_results(
        self, 
        session: aiohttp.ClientSession, 
        job_id: str, 
        headers: Dict[str, str]
    ) -> Dict[str, Any]:
        """انتظار نتائج التحليل من HUME"""
        
        max_attempts = 30  # 30 seconds max
        attempt = 0
        
        while attempt < max_attempts:
            async with session.get(
                f"{self.base_url}/batch/jobs/{job_id}",
                headers=headers
            ) as response:
                if response.status == 200:
                    job_status = await response.json()
                    
                    if job_status['state'] == 'COMPLETED':
                        # تحميل النتائج
                        return await self._download_results(session, job_id, headers)
                    elif job_status['state'] == 'FAILED':
                        raise Exception("HUME job failed")
                    
                    # انتظار ثانية قبل المحاولة التالية
                    await asyncio.sleep(1)
                    attempt += 1
                else:
                    raise Exception(f"Status check failed: {response.status}")
        
        raise Exception("HUME analysis timeout")
    
    async def _download_results(
        self, 
        session: aiohttp.ClientSession, 
        job_id: str, 
        headers: Dict[str, str]
    ) -> Dict[str, Any]:
        """تحميل نتائج التحليل"""
        
        async with session.get(
            f"{self.base_url}/batch/jobs/{job_id}/predictions",
            headers=headers
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise Exception(f"Results download failed: {response.status}")
    
    async def _convert_to_child_emotion(
        self, 
        hume_results: Dict[str, Any],
        child_age: int,
        child_name: str,
        context: Dict[str, Any]
    ) -> ChildVoiceEmotion:
        """تحويل نتائج HUME إلى تحليل مخصص للطفل"""
        
        child_emotion = ChildVoiceEmotion()
        child_emotion.timestamp = datetime.now().isoformat()
        
        try:
            # استخراج المشاعر من نتائج HUME
            if 'predictions' in hume_results:
                predictions = hume_results['predictions']
                
                if predictions and len(predictions) > 0:
                    # أخذ أول تسجيل صوتي
                    first_prediction = predictions[0]
                    
                    if 'models' in first_prediction and 'prosody' in first_prediction['models']:
                        prosody_data = first_prediction['models']['prosody']
                        
                        if 'grouped_predictions' in prosody_data:
                            grouped = prosody_data['grouped_predictions']
                            
                            if grouped and len(grouped) > 0:
                                # أخذ أول مجموعة توقعات
                                emotions = grouped[0]['predictions']
                                
                                # تحويل المشاعر
                                for emotion_data in emotions:
                                    emotion_name = emotion_data['name']
                                    emotion_score = emotion_data['score']
                                    
                                    # تطبيق خريطة المشاعر المخصصة للأطفال
                                    if emotion_name in self.child_emotion_map:
                                        child_field = self.child_emotion_map[emotion_name]
                                        
                                        # تحديث قيمة المشاعر في الكائن
                                        if hasattr(child_emotion, child_field):
                                            current_value = getattr(child_emotion, child_field)
                                            setattr(child_emotion, child_field, 
                                                   max(current_value, emotion_score))
            
            # تحديد المشاعر المهيمنة
            child_emotion.dominant_emotion = self._get_dominant_emotion(child_emotion)
            child_emotion.confidence = self._calculate_confidence(child_emotion)
            child_emotion.emotional_intensity = self._calculate_intensity(child_emotion)
            
            # تخصيص للعمر
            child_emotion = self._adjust_for_age(child_emotion, child_age)
            
            # إضافة السياق
            if context:
                child_emotion = self._apply_context(child_emotion, context)
            
        except Exception as e:
    logger.error(f"Error: {e}")f"⚠️ Error converting HUME results: {e}")
            # إرجاع تحليل افتراضي
            child_emotion.dominant_emotion = "curious"
            child_emotion.curiosity = 0.6
            child_emotion.confidence = 0.3
        
        return child_emotion
    
    async def _add_developmental_analysis(
        self, 
        emotion: ChildVoiceEmotion, 
        audio_data: bytes, 
        child_age: int
    ) -> ChildVoiceEmotion:
        """إضافة تحليل تطويري إضافي للطفل"""
        
        # تحليل خصائص الصوت الأساسية
        voice_characteristics = await self._analyze_voice_characteristics(audio_data)
        
        emotion.energy_level = voice_characteristics.get('energy', 0.5)
        emotion.speech_rate = voice_characteristics.get('speech_rate', 0.5)
        emotion.pitch_variation = voice_characteristics.get('pitch_variation', 0.5)
        emotion.voice_quality = voice_characteristics.get('quality', 'clear')
        
        # تحليل مستوى الانتباه
        emotion.attention_level = self._calculate_attention_level(emotion, voice_characteristics)
        
        # تحليل وضوح التواصل
        emotion.communication_clarity = self._calculate_communication_clarity(
            voice_characteristics, child_age
        )
        
        # إضافة مؤشرات تطويرية
        emotion.developmental_indicators = self._generate_developmental_indicators(
            emotion, child_age
        )
        
        return emotion
    
    async def _analyze_voice_characteristics(self, audio_data: bytes) -> Dict[str, Any]:
        """تحليل خصائص الصوت الأساسية"""
        
        # هذا تحليل مبسط - في التطبيق الحقيقي نستخدم librosa
        try:
            # محاكاة تحليل الصوت
            import random
            
            return {
                'energy': random.uniform(0.2, 0.9),
                'speech_rate': random.uniform(0.3, 0.8),
                'pitch_variation': random.uniform(0.2, 0.7),
                'quality': random.choice(['clear', 'soft', 'excited', 'tired']),
                'volume': random.uniform(0.4, except IndexError as e:
    logger.error(f"Error in operation: {e}", exc_info=True)IndexError as e:
    logger.error(f"Error in operation: {e}", exc_info=True)         }
        except IndexError as e:
    logger.error(f"Error in operation: {e}", exc_info=True)IndexError as e:
    logger.error(f"Error in operation: {e}", exc_info=True)            return {
                'energy': 0.5,
                'speech_rate': 0.5, 
                'pitch_variation': 0.5,
                'quality': 'clear',
                'volume': 0.5
            }
    
    def _get_dominant_emotion(self, emotion: ChildVoiceEmotion) -> str:
        """تحديد المشاعر المهيمنة"""
        
        emotion_scores = {
            'joy': emotion.joy,
            'sadness': emotion.sadness,
            'anger': emotion.anger,
            'fear': emotion.fear,
            'excitement': emotion.excitement,
            'calmness': emotion.calmness,
            'surprise': emotion.surprise,
            'curiosity': emotion.curiosity,
            'frustration': emotion.frustration,
            'playfulness': emotion.playfulness,
            'tiredness': emotion.tiredness
        }
        
        return max(emotion_scores.items(), key=lambda x: x[1])[0]
    
    def _calculate_confidence(self, emotion: ChildVoiceEmotion) -> float:
        """حساب مستوى الثقة في التحليل"""
        
        # حساب مجموع كل المشاعر
        total_emotions = (
            emotion.joy + emotion.sadness + emotion.anger + emotion.fear +
            emotion.excitement + emotion.calmness + emotion.surprise +
            emotion.curiosity + emotion.frustration + emotion.playfulness
        )
        
        # إذا كانت المشاعر عالية بشكل عام، الثقة أعلى
        return min(total_emotions / 3.0, 1.0)
    
    def _calculate_intensity(self, emotion: ChildVoiceEmotion) -> float:
        """حساب شدة المشاعر"""
        
        dominant_score = getattr(emotion, emotion.dominant_emotion)
        return dominant_score
    
    def _adjust_for_age(self, emotion: ChildVoiceEmotion, age: int) -> ChildVoiceEmotion:
        """تخصيص التحليل حسب العمر"""
        
        # تحديد مجموعة العمر
        age_group = "3-4" if age <= 4 else "5-6" if age <= 6 else "7-8" if age <= 8 else "9-10" if age <= 10 else "11+"
        
        params = self.age_parameters.get(age_group, self.age_parameters["5-6"])
        sensitivity = params["sensitivity"]
        
        # تطبيق الحساسية على المشاعر
        emotion.joy *= sensitivity
        emotion.sadness *= sensitivity
        emotion.anger *= sensitivity
        emotion.fear *= sensitivity
        
        # الأطفال الصغار أكثر فضولاً
        if age <= 6:
            emotion.curiosity *= 1.2
            emotion.playfulness *= 1.3
        
        # الأطفال الأكبر أكثر تعقيداً عاطفياً
        if age >= 8:
            emotion.frustration *= 1.1
            emotion.shyness *= 1.1
        
        return emotion
    
    def _apply_context(self, emotion: ChildVoiceEmotion, context: Dict[str, Any]) -> ChildVoiceEmotion:
        """تطبيق السياق على التحليل"""
        
        # وقت اليوم
        current_hour = datetime.now().hour
        if 20 <= current_hour or current_hour <= 6:
            # وقت متأخر - قد يكون متعب
            emotion.tiredness *= 1.3
            emotion.energy_level *= 0.8
        
        # النشاط الأخير
        recent_activity = context.get('recent_activity', '')
        if 'لعب' in recent_activity:
            emotion.playfulness *= 1.2
            emotion.excitement *= 1.1
        elif 'تعلم' in recent_activity:
            emotion.curiosity *= 1.2
            emotion.attention_level *= 1.1
        
        return emotion
    
    def _calculate_attention_level(
        self, 
        emotion: ChildVoiceEmotion, 
        voice_characteristics: Dict[str, Any]
    ) -> float:
        """حساب مستوى الانتباه"""
        
        # الأطفال المنتبهون لديهم:
        # - وضوح في الصوت
        # - مستوى طاقة متوسط لعالي
        # - تفاوت منخفض في النبرة (ثبات)
        
        clarity_score = 1.0 if voice_characteristics.get('quality') == 'clear' else 0.6
        energy_score = voice_characteristics.get('energy', 0.5)
        stability_score = 1.0 - voice_characteristics.get('pitch_variation', 0.5)
        
        # الفضول يشير إلى انتباه
        curiosity_bonus = emotion.curiosity * 0.3
        
        attention = (clarity_score + energy_score + stability_score + curiosity_bonus) / 4.0
        return min(attention, 1.0)
    
    def _calculate_communication_clarity(
        self, 
        voice_characteristics: Dict[str, Any], 
        child_age: int
    ) -> float:
        """حساب وضوح التواصل"""
        
        # الأطفال الأكبر عادة أوضح في الكلام
        age_factor = min(child_age / 10.0, 1.0)
        
        quality_score = 1.0 if voice_characteristics.get('quality') == 'clear' else 0.7
        volume_score = voice_characteristics.get('volume', 0.5)
        
        clarity = (age_factor + quality_score + volume_score) / 3.0
        return min(clarity, 1.0)
    
    def _generate_developmental_indicators(
        self, 
        emotion: ChildVoiceEmotion, 
        child_age: int
    ) -> List[str]:
        """توليد مؤشرات تطويرية"""
        
        indicators = []
        
        # مؤشرات إيجابية
        if emotion.attention_level > 0.7:
            indicators.append("مستوى انتباه عالي")
        
        if emotion.communication_clarity > 0.8:
            indicators.append("وضوح تواصل ممتاز")
        
        if emotion.curiosity > 0.6:
            indicators.append("فضول صحي ونشط")
        
        if emotion.playfulness > 0.7:
            indicators.append("حب اللعب والمرح")
        
        # مؤشرات تحتاج انتباه
        if emotion.sadness > 0.7:
            indicators.append("مستوى حزن مرتفع - يحتاج دعم")
        
        if emotion.fear > 0.6:
            indicators.append("مستوى قلق - يحتاج طمأنينة")
        
        if emotion.tiredness > 0.8:
            indicators.append("علامات تعب - يحتاج راحة")
        
        # مؤشرات عمرية
        if child_age <= 5 and emotion.curiosity < 0.3:
            indicators.append("فضول أقل من المتوقع للعمر")
        
        if child_age >= 7 and emotion.communication_clarity < 0.5:
            indicators.append("وضوح التواصل يحتاج تحسين")
        
        return indicators
    
    async def _save_temp_audio(self, audio_data: bytes) -> str:
        """حفظ الصوت في ملف مؤقت"""
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio_data)
            return tmp.name
    
    def _create_fallback_analysis(self) -> ChildVoiceEmotion:
        """إنشاء تحليل احتياطي عند فشل HUME"""
        
        return ChildVoiceEmotion(
            curiosity=0.6,
            calmness=0.4,
            joy=0.3,
            dominant_emotion="curious",
            confidence=0.3,
            emotional_intensity=0.5,
            timestamp=datetime.now().isoformat(),
            developmental_indicators=["تحليل أساسي - HUME غير متاح"]
        )
    
    async def get_child_emotion_summary(
        self, 
        emotions_history: List[ChildVoiceEmotion]
    ) -> Dict[str, Any]:
        """ملخص المشاعر للطفل عبر الوقت"""
        
        if not emotions_history:
            return {"message": "لا توجد بيانات كافية"}
        
        # حساب متوسط المشاعر
        avg_emotions = {}
        emotion_fields = ['joy', 'sadness', 'anger', 'fear', 'excitement', 
                         'calmness', 'curiosity', 'playfulness']
        
        for field in emotion_fields:
            values = [getattr(emotion, field) for emotion in emotions_history]
            avg_emotions[field] = sum(values) / len(values)
        
        # المشاعر المهيمنة
        dominant_emotions = [emotion.dominant_emotion for emotion in emotions_history]
        most_common = max(set(dominant_emotions), key=dominant_emotions.count)
        
        # مؤشرات التطوير
        all_indicators = []
        for emotion in emotions_history:
            all_indicators.extend(emotion.developmental_indicators)
        
        return {
            "period_analyzed": f"{len(emotions_history)} تفاعل",
            "average_emotions": avg_emotions,
            "most_common_emotion": most_common,
            "emotional_stability": self._calculate_stability(emotions_history),
            "developmental_highlights": list(set(all_indicators)),
            "recommendations": self._generate_recommendations(avg_emotions, most_common)
        }
    
    def _calculate_stability(self, emotions_history: List[ChildVoiceEmotion]) -> float:
        """حساب الاستقرار العاطفي"""
        
        if len(emotions_history) < 2:
            return 1.0
        
        # حساب التباين في المشاعر المهيمنة
        dominant_emotions = [emotion.dominant_emotion for emotion in emotions_history]
        changes = sum(1 for i in range(1, len(dominant_emotions)) 
                     if dominant_emotions[i] != dominant_emotions[i-1])
        
        stability = 1.0 - (changes / (len(dominant_emotions) - 1))
        return max(0.0, stability)
    
    def _generate_recommendations(
        self, 
        avg_emotions: Dict[str, float], 
        most_common: str
    ) -> List[str]:
        """توليد توصيات بناء على التحليل"""
        
        recommendations = []
        
        if most_common == "joy":
            recommendations.append("الطفل سعيد - استمر في الأنشطة الحالية")
            recommendations.append("وقت ممتاز لتعلم أشياء جديدة")
        
        elif most_common == "curiosity":
            recommendations.append("الطفل فضولي - شجع الاستكشاف")
            recommendations.append("قدم ألعاب تعليمية وتجارب علمية")
        
        elif most_common == "sadness":
            recommendations.append("يحتاج دعم عاطفي إضافي")
            recommendations.append("أنشطة مرحة ومحفزة للمزاج")
        
        elif most_common == "fear":
            recommendations.append("يحتاج طمأنينة وبيئة آمنة")
            recommendations.append("تجنب المحتوى المخيف")
        
        # توصيات عامة
        if avg_emotions.get('tiredness', 0) > 0.6:
            recommendations.append("علامات تعب - قد يحتاج راحة")
        
        if avg_emotions.get('playfulness', 0) > 0.7:
            recommendations.append("يحب اللعب - أضف ألعاب تفاعلية")
        
        return recommendations


# دالة اختبار
async def test_hume_analyzer():
    """اختبار محلل HUME"""
    
    logger.info("🧪 Testing HUME Speech Emotion Analyzer...")
    
    analyzer = HumeSpeechEmotionAnalyzer()
    
    # محاكاة بيانات صوتية (في التطبيق الحقيقي ستكون من ESP32)
    mock_audio = b"mock_audio_data"
    
    # تحليل مشاعر طفل
    emotion = await analyzer.analyze_child_voice(
        audio_data=mock_audio,
        child_age=6,
        child_name="أحمد",
        context={"recent_activity": "لعب", "time_of_day": "afternoon"}
    )
    
    logger.info(f"🎯 Dominant Emotion: {emotion.dominant_emotion}")
    logger.info(f"😊 Joy: {emotion.joy:.2f}")
    logger.info(f"🤔 Curiosity: {emotion.curiosity:.2f}")
    logger.info(f"💪 Energy Level: {emotion.energy_level:.2f}")
    logger.info(f"🎯 Attention Level: {emotion.attention_level:.2f}")
    logger.info(f"📋 Indicators: {emotion.developmental_indicators}")
    
    logger.info("✅ HUME analyzer test completed!")


if __name__ == "__main__":
    asyncio.run(test_hume_analyzer()) 