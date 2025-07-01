import asyncio
import json
import math
import statistics
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class VoicePattern(Enum):
    """أنماط الصوت المختلفة"""

    CONFIDENT = "واثق"
    HESITANT = "متردد"
    EXCITED = "متحمس"
    ANXIOUS = "قلق"
    CALM = "هادئ"
    TIRED = "متعب"
    HAPPY = "سعيد"
    SAD = "حزين"


class BehavioralConcern(Enum):
    """المخاوف السلوكية التي تحتاج تنبيه الوالدين"""

    REPEATED_ANXIETY = "قلق_متكرر"
    SOCIAL_WITHDRAWAL = "انسحاب_اجتماعي"
    LOW_CONFIDENCE = "ثقة_منخفضة"
    AGGRESSIVE_PATTERNS = "أنماط_عدوانية"
    REGRESSION_SIGNS = "علامات_تراجع"
    EMOTIONAL_INSTABILITY = "عدم_استقرار_عاطفي"


@dataclass
class VoiceAnalysis:
    """تحليل مفصل للصوت"""

    speed_wpm: float  # كلمات في الدقيقة
    pause_frequency: float  # تكرار التوقفات
    pause_duration_avg: float  # متوسط مدة التوقفات
    pitch_variation: float  # تنوع طبقة الصوت
    volume_consistency: float  # ثبات الصوت
    confidence_score: float  # نقاط الثقة (0-1)
    emotional_tone: str  # النبرة العاطفية
    detected_patterns: List[VoicePattern]
    analysis_timestamp: datetime


@dataclass
class BehavioralAlert:
    """تنبيه سلوكي للوالدين"""

    id: str
    child_name: str
    device_id: str
    concern_type: BehavioralConcern
    severity_level: str  # "منخفض", "متوسط", "عالي"
    description: str
    evidence: List[str]  # الأدلة المؤدية للتنبيه
    recommendations: List[str]
    created_at: datetime
    parent_notified: bool = False


@dataclass
class PsychologicalProfile:
    """الملف النفسي للطفل"""

    child_name: str
    device_id: str
    personality_traits: Dict[str, float]  # الصفات الشخصية مع نقاطها
    emotional_patterns: Dict[str, List[float]]  # أنماط المشاعر عبر الوقت
    stress_indicators: List[str]  # مؤشرات التوتر
    strengths: List[str]  # نقاط القوة
    areas_of_concern: List[str]  # مناطق الاهتمام
    social_skills_level: float  # مستوى المهارات الاجتماعية
    confidence_trend: List[float]  # اتجاه الثقة بالنفس
    last_updated: datetime


class AdvancedBehavioralAnalyzer:
    """محلل السلوك والمشاعر المتقدم"""

    def __init__(self):
        self.voice_analyses: List[VoiceAnalysis] = []
        self.behavioral_alerts: List[BehavioralAlert] = []
        self.psychological_profiles: Dict[str, PsychologicalProfile] = {}

        # معايير الكشف
        self.concern_thresholds = {
            BehavioralConcern.REPEATED_ANXIETY: {
                "min_occurrences": 3,
                "time_window_days": 7,
                "anxiety_score_threshold": 0.7,
            },
            BehavioralConcern.LOW_CONFIDENCE: {"confidence_threshold": 0.3, "consecutive_low_sessions": 5},
            BehavioralConcern.SOCIAL_WITHDRAWAL: {
                "cooperation_score_threshold": 0.2,
                "social_initiative_threshold": 0.3,
            },
        }

    async def analyze_voice_with_context(
        self, audio_data: bytes, story_context: Optional[Dict] = None, child_name: str = None, device_id: str = None
    ) -> VoiceAnalysis:
        """تحليل الصوت مع السياق"""

        # تحليل خصائص الصوت الأساسية
        voice_features = await self._extract_voice_features(audio_data)

        # تحليل النص المستخرج
        transcribed_text = await self._transcribe_audio(audio_data)
        text_analysis = await self._analyze_speech_patterns(transcribed_text)

        # دمج تحليل الصوت مع النص
        combined_analysis = self._combine_voice_and_text_analysis(voice_features, text_analysis)

        # تطبيق السياق إن وجد
        if story_context:
            combined_analysis = self._apply_story_context(combined_analysis, story_context)

        # إنشاء تحليل الصوت
        voice_analysis = VoiceAnalysis(
            speed_wpm=voice_features["speed_wpm"],
            pause_frequency=voice_features["pause_frequency"],
            pause_duration_avg=voice_features["pause_duration_avg"],
            pitch_variation=voice_features["pitch_variation"],
            volume_consistency=voice_features["volume_consistency"],
            confidence_score=combined_analysis["confidence_score"],
            emotional_tone=combined_analysis["emotional_tone"],
            detected_patterns=combined_analysis["detected_patterns"],
            analysis_timestamp=datetime.now(),
        )

        # حفظ التحليل
        self.voice_analyses.append(voice_analysis)

        # تحديث الملف النفسي للطفل
        if child_name and device_id:
            await self._update_psychological_profile(child_name, device_id, voice_analysis)

        return voice_analysis

    async def _extract_voice_features(self, audio_data: bytes) -> Dict[str, float]:
        """استخراج خصائص الصوت الأساسية"""
        # محاكاة تحليل الصوت - في التطبيق الحقيقي نستخدم مكتبات مثل librosa

        import random

        # محاكاة تحليل السرعة
        speed_wpm = random.uniform(80, 200)  # كلمات في الدقيقة

        # محاكاة تحليل التوقفات
        pause_frequency = random.uniform(0.1, 0.8)  # نسبة التوقفات
        pause_duration_avg = random.uniform(0.2, 2.0)  # متوسط مدة التوقف بالثواني

        # محاكاة تحليل طبقة الصوت
        pitch_variation = random.uniform(0.1, 1.0)  # تنوع الطبقة

        # محاكاة ثبات مستوى الصوت
        volume_consistency = random.uniform(0.3, 1.0)  # ثبات الصوت

        return {
            "speed_wpm": speed_wpm,
            "pause_frequency": pause_frequency,
            "pause_duration_avg": pause_duration_avg,
            "pitch_variation": pitch_variation,
            "volume_consistency": volume_consistency,
        }

    async def _transcribe_audio(self, audio_data: bytes) -> str:
        """تحويل الصوت إلى نص"""
        # محاكاة - في التطبيق الحقيقي نستخدم Whisper أو Azure Speech
        sample_responses = [
            "نعم أريد أن أساعد الطفل الجديد",
            "لست متأكداً من هذا الخيار",
            "أعتقد أنه يجب أن نخبر الوالدين أولاً",
            "هذا يبدو مخيفاً قليلاً",
            "أريد أن ألعب مع أصدقائي",
        ]
        import random

        return random.choice(sample_responses)

    async def _analyze_speech_patterns(self, text: str) -> Dict[str, Any]:
        """تحليل أنماط الكلام"""

        # كلمات تدل على التردد
        hesitation_words = ["أمم", "أه", "لست متأكد", "ربما", "لا أعرف", "أعتقد"]

        # كلمات تدل على القلق
        anxiety_words = ["مخيف", "خائف", "قلق", "لا أستطيع", "صعب"]

        # كلمات تدل على الثقة
        confidence_words = ["نعم", "أكيد", "بالطبع", "أستطيع", "سأفعل"]

        # كلمات تدل على السعادة
        happiness_words = ["سعيد", "رائع", "ممتع", "أحب", "جميل"]

        text_lower = text.lower()

        # حساب النقاط
        hesitation_score = sum(1 for word in hesitation_words if word in text_lower) / len(text.split())
        anxiety_score = sum(1 for word in anxiety_words if word in text_lower) / len(text.split())
        confidence_score = sum(1 for word in confidence_words if word in text_lower) / len(text.split())
        happiness_score = sum(1 for word in happiness_words if word in text_lower) / len(text.split())

        return {
            "hesitation_score": hesitation_score,
            "anxiety_score": anxiety_score,
            "confidence_score": confidence_score,
            "happiness_score": happiness_score,
            "text_length": len(text.split()),
        }

    def _combine_voice_and_text_analysis(self, voice_features: Dict, text_analysis: Dict) -> Dict[str, Any]:
        """دمج تحليل الصوت والنص"""

        # حساب نقاط الثقة المجمعة
        voice_confidence = 1.0 - (
            voice_features["pause_frequency"] * 0.5 + (1.0 - voice_features["volume_consistency"]) * 0.3
        )
        text_confidence = text_analysis["confidence_score"] - text_analysis["hesitation_score"]

        combined_confidence = voice_confidence * 0.6 + text_confidence * 0.4
        combined_confidence = max(0.0, min(1.0, combined_confidence))  # تطبيع بين 0 و 1

        # تحديد النبرة العاطفية
        if text_analysis["anxiety_score"] > 0.3:
            emotional_tone = "قلق"
        elif text_analysis["happiness_score"] > 0.2:
            emotional_tone = "سعيد"
        elif voice_features["speed_wpm"] < 100:
            emotional_tone = "هادئ"
        elif voice_features["speed_wpm"] > 160:
            emotional_tone = "متحمس"
        else:
            emotional_tone = "عادي"

        # كشف الأنماط
        detected_patterns = []

        if combined_confidence < 0.4:
            detected_patterns.append(VoicePattern.HESITANT)
        elif combined_confidence > 0.7:
            detected_patterns.append(VoicePattern.CONFIDENT)

        if text_analysis["anxiety_score"] > 0.3:
            detected_patterns.append(VoicePattern.ANXIOUS)

        if voice_features["speed_wpm"] > 160:
            detected_patterns.append(VoicePattern.EXCITED)
        elif voice_features["speed_wpm"] < 100:
            detected_patterns.append(VoicePattern.CALM)

        return {
            "confidence_score": combined_confidence,
            "emotional_tone": emotional_tone,
            "detected_patterns": detected_patterns,
        }

    def _apply_story_context(self, analysis: Dict, story_context: Dict) -> Dict[str, Any]:
        """تطبيق سياق القصة على التحليل"""

        # إذا كان السياق يتطلب شجاعة ولكن الطفل أظهر قلق
        if story_context.get("requires_courage") and VoicePattern.ANXIOUS in analysis["detected_patterns"]:
            analysis["context_notes"] = "أظهر قلقاً في موقف يتطلب الشجاعة"

        # إذا كان السياق اجتماعي والطفل أظهر تردد
        if story_context.get("social_situation") and VoicePattern.HESITANT in analysis["detected_patterns"]:
            analysis["context_notes"] = "تردد في الموقف الاجتماعي"

        return analysis

    async def _update_psychological_profile(self, child_name: str, device_id: str, voice_analysis: VoiceAnalysis):
        """تحديث الملف النفسي للطفل"""

        profile_key = f"{device_id}_{child_name}"

        if profile_key not in self.psychological_profiles:
            # إنشاء ملف جديد
            self.psychological_profiles[profile_key] = PsychologicalProfile(
                child_name=child_name,
                device_id=device_id,
                personality_traits={},
                emotional_patterns={},
                stress_indicators=[],
                strengths=[],
                areas_of_concern=[],
                social_skills_level=0.5,
                confidence_trend=[],
                last_updated=datetime.now(),
            )

        profile = self.psychological_profiles[profile_key]

        # تحديث اتجاه الثقة
        profile.confidence_trend.append(voice_analysis.confidence_score)
        if len(profile.confidence_trend) > 20:  # الاحتفاظ بآخر 20 قراءة
            profile.confidence_trend.pop(0)

        # تحديث الأنماط العاطفية
        emotional_tone = voice_analysis.emotional_tone
        if emotional_tone not in profile.emotional_patterns:
            profile.emotional_patterns[emotional_tone] = []
        profile.emotional_patterns[emotional_tone].append(voice_analysis.confidence_score)

        # كشف مؤشرات التوتر
        if VoicePattern.ANXIOUS in voice_analysis.detected_patterns:
            if "قلق متكرر" not in profile.stress_indicators:
                profile.stress_indicators.append("قلق متكرر")

        if voice_analysis.confidence_score < 0.3:
            if "ثقة منخفضة" not in profile.stress_indicators:
                profile.stress_indicators.append("ثقة منخفضة")

        # تحديث نقاط القوة
        if voice_analysis.confidence_score > 0.7:
            if "ثقة عالية بالنفس" not in profile.strengths:
                profile.strengths.append("ثقة عالية بالنفس")

        profile.last_updated = datetime.now()

        # فحص الحاجة لتنبيهات
        await self._check_for_behavioral_concerns(child_name, device_id)

    async def check_for_behavioral_concerns(self, child_name: str, device_id: str):
        """فحص المخاوف السلوكية وإنشاء تنبيهات"""

        # الحصول على تحليلات الطفل الأخيرة
        recent_analyses = [
            analysis
            for analysis in self.voice_analyses[-30:]  # آخر 30 تحليل
            # في التطبيق الحقيقي نربط بـ child_name و device_id
        ]

        if len(recent_analyses) < 5:  # نحتاج عينة كافية
            return

        # فحص القلق المتكرر
        await self._check_repeated_anxiety(child_name, device_id, recent_analyses)

        # فحص انخفاض الثقة
        await self._check_low_confidence(child_name, device_id, recent_analyses)

        # فحص الانسحاب الاجتماعي
        await self._check_social_withdrawal(child_name, device_id)

    async def _check_repeated_anxiety(self, child_name: str, device_id: str, analyses: List[VoiceAnalysis]):
        """فحص القلق المتكرر"""

        anxiety_count = sum(1 for analysis in analyses[-7:] if VoicePattern.ANXIOUS in analysis.detected_patterns)

        threshold = self.concern_thresholds[BehavioralConcern.REPEATED_ANXIETY]

        if anxiety_count >= threshold["min_occurrences"]:
            # إنشاء تنبيه
            alert = BehavioralAlert(
                id=f"anxiety_{device_id}_{datetime.now().timestamp()}",
                child_name=child_name,
                device_id=device_id,
                concern_type=BehavioralConcern.REPEATED_ANXIETY,
                severity_level="متوسط" if anxiety_count < 5 else "عالي",
                description=f"الطفل أظهر علامات قلق في {anxiety_count} من آخر 7 جلسات",
                evidence=[
                    f"قلق مكتشف في {anxiety_count} جلسات",
                    "أنماط صوتية تدل على التوتر",
                    "استخدام كلمات تدل على الخوف",
                ],
                recommendations=[
                    "تحدث مع الطفل عن مشاعره",
                    "وفر بيئة آمنة ومطمئنة",
                    "فكر في استشارة مختص إذا استمر القلق",
                    "شجع أنشطة الاسترخاء",
                ],
                created_at=datetime.now(),
            )

            self.behavioral_alerts.append(alert)

    async def _check_low_confidence(self, child_name: str, device_id: str, analyses: List[VoiceAnalysis]):
        """فحص انخفاض الثقة"""

        recent_confidence = [analysis.confidence_score for analysis in analyses[-5:]]
        avg_confidence = sum(recent_confidence) / len(recent_confidence)

        threshold = self.concern_thresholds[BehavioralConcern.LOW_CONFIDENCE]

        if avg_confidence < threshold["confidence_threshold"]:
            alert = BehavioralAlert(
                id=f"confidence_{device_id}_{datetime.now().timestamp()}",
                child_name=child_name,
                device_id=device_id,
                concern_type=BehavioralConcern.LOW_CONFIDENCE,
                severity_level="متوسط",
                description=f"متوسط الثقة بالنفس منخفض: {avg_confidence:.2f}",
                evidence=[
                    f"متوسط نقاط الثقة: {avg_confidence:.2f}",
                    "تردد واضح في الاختيارات",
                    "استخدام كلمات تدل على عدم اليقين",
                ],
                recommendations=[
                    "شجع الطفل وامدح محاولاته",
                    "ابدأ بأنشطة سهلة لبناء الثقة",
                    "تجنب النقد المباشر",
                    "احتفل بالإنجازات الصغيرة",
                ],
                created_at=datetime.now(),
            )

            self.behavioral_alerts.append(alert)

    async def _check_social_withdrawal(self, child_name: str, device_id: str):
        """فحص الانسحاب الاجتماعي"""

        # هذا يتطلب دمج مع بيانات اختيارات القصص
        # من الـ InteractiveStoryEngine

        # محاكاة للمثال
        profile_key = f"{device_id}_{child_name}"
        if profile_key in self.psychological_profiles:
            profile = self.psychological_profiles[profile_key]

            # فحص إذا كان الطفل يتجنب الخيارات الاجتماعية
            if profile.social_skills_level < 0.3:
                alert = BehavioralAlert(
                    id=f"social_{device_id}_{datetime.now().timestamp()}",
                    child_name=child_name,
                    device_id=device_id,
                    concern_type=BehavioralConcern.SOCIAL_WITHDRAWAL,
                    severity_level="متوسط",
                    description="الطفل يُظهر علامات تجنب للمواقف الاجتماعية",
                    evidence=[
                        f"مستوى المهارات الاجتماعية: {profile.social_skills_level:.2f}",
                        "تجنب خيارات التفاعل الاجتماعي في القصص",
                    ],
                    recommendations=[
                        "شجع اللعب مع الأطفال الآخرين",
                        "انضم لأنشطة جماعية",
                        "مارس الحوار اليومي مع الطفل",
                        "فكر في أنشطة اجتماعية تدريجية",
                    ],
                    created_at=datetime.now(),
                )

                self.behavioral_alerts.append(alert)

    def get_child_psychological_report(self, child_name: str, device_id: str) -> Dict[str, Any]:
        """الحصول على التقرير النفسي للطفل"""

        profile_key = f"{device_id}_{child_name}"

        if profile_key not in self.psychological_profiles:
            return {"error": "لا يوجد ملف نفسي للطفل"}

        profile = self.psychological_profiles[profile_key]

        # حساب الاتجاهات
        confidence_trend = "مستقر"
        if len(profile.confidence_trend) >= 5:
            recent_avg = sum(profile.confidence_trend[-5:]) / 5
            earlier_avg = (
                sum(profile.confidence_trend[-10:-5]) / 5 if len(profile.confidence_trend) >= 10 else recent_avg
            )

            if recent_avg > earlier_avg + 0.1:
                confidence_trend = "متحسن"
            elif recent_avg < earlier_avg - 0.1:
                confidence_trend = "متراجع"

        # الحصول على التنبيهات الأخيرة
        recent_alerts = [
            alert
            for alert in self.behavioral_alerts
            if alert.child_name == child_name
            and alert.device_id == device_id
            and alert.created_at >= datetime.now() - timedelta(days=30)
        ]

        return {
            "child_name": child_name,
            "device_id": device_id,
            "confidence_level": (
                sum(profile.confidence_trend) / len(profile.confidence_trend) if profile.confidence_trend else 0.5
            ),
            "confidence_trend": confidence_trend,
            "emotional_patterns": profile.emotional_patterns,
            "strengths": profile.strengths,
            "areas_of_concern": profile.areas_of_concern,
            "stress_indicators": profile.stress_indicators,
            "social_skills_level": profile.social_skills_level,
            "recent_alerts": [
                {
                    "type": alert.concern_type.value,
                    "severity": alert.severity_level,
                    "description": alert.description,
                    "date": alert.created_at.isoformat(),
                }
                for alert in recent_alerts
            ],
            "recommendations": self._generate_overall_recommendations(profile),
            "last_updated": profile.last_updated.isoformat(),
        }

    def _generate_overall_recommendations(self, profile: PsychologicalProfile) -> List[str]:
        """توليد توصيات شاملة"""
        recommendations = []

        # توصيات بناءً على الثقة
        if profile.confidence_trend:
            avg_confidence = sum(profile.confidence_trend) / len(profile.confidence_trend)

            if avg_confidence < 0.4:
                recommendations.extend(
                    [
                        "ركز على بناء الثقة بالنفس من خلال الأنشطة البسيطة",
                        "احتفل بكل إنجاز مهما كان صغيراً",
                        "تجنب المقارنات مع الآخرين",
                    ]
                )
            elif avg_confidence > 0.7:
                recommendations.append("الطفل يُظهر ثقة جيدة بالنفس - استمر في التشجيع")

        # توصيات بناءً على المهارات الاجتماعية
        if profile.social_skills_level < 0.4:
            recommendations.extend(
                ["شجع الأنشطة الاجتماعية التدريجية", "انضم لمجموعات لعب منظمة", "مارس الحوار والمشاركة في المنزل"]
            )

        # توصيات بناءً على مؤشرات التوتر
        if "قلق متكرر" in profile.stress_indicators:
            recommendations.extend(
                ["علم الطفل تقنيات التنفس العميق", "وفر روتين يومي مستقر", "فكر في استشارة مختص إذا استمر القلق"]
            )

        return recommendations

    def get_parent_alerts(self, device_id: str, unread_only: bool = True) -> List[Dict]:
        """الحصول على تنبيهات الوالدين"""

        alerts = [alert for alert in self.behavioral_alerts if alert.device_id == device_id]

        if unread_only:
            alerts = [alert for alert in alerts if not alert.parent_notified]

        return [
            {
                "id": alert.id,
                "child_name": alert.child_name,
                "concern_type": alert.concern_type.value,
                "severity": alert.severity_level,
                "description": alert.description,
                "evidence": alert.evidence,
                "recommendations": alert.recommendations,
                "created_at": alert.created_at.isoformat(),
                "is_urgent": alert.severity_level == "عالي",
            }
            for alert in sorted(alerts, key=lambda x: x.created_at, reverse=True)
        ]

    def mark_alert_as_read(str) -> None:
        """تأشير التنبيه كمقروء"""
        for alert in self.behavioral_alerts:
            if alert.id == alert_id:
                alert.parent_notified = True
                break
