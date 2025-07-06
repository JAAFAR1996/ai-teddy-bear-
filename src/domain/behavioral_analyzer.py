from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from src.domain.config import alert_messages
from src.domain.entities.behavioral_entities import (
    BehavioralAlert,
    BehavioralConcern,
    PsychologicalProfile,
    VoiceAnalysis,
    VoicePattern,
)


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
            BehavioralConcern.LOW_CONFIDENCE: {
                "confidence_threshold": 0.3,
                "consecutive_low_sessions": 5,
            },
            BehavioralConcern.SOCIAL_WITHDRAWAL: {
                "cooperation_score_threshold": 0.2,
                "social_initiative_threshold": 0.3,
            },
        }

    async def analyze_voice_with_context(
        self,
        audio_data: bytes,
        story_context: Optional[Dict] = None,
        child_name: str = None,
        device_id: str = None,
    ) -> VoiceAnalysis:
        """تحليل الصوت مع السياق"""

        # تحليل خصائص الصوت الأساسية
        voice_features = await self._extract_voice_features(audio_data)

        # تحليل النص المستخرج
        transcribed_text = await self._transcribe_audio(audio_data)
        text_analysis = await self._analyze_speech_patterns(transcribed_text)

        # دمج تحليل الصوت مع النص
        combined_analysis = self._combine_voice_and_text_analysis(
            voice_features, text_analysis
        )

        # تطبيق السياق إن وجد
        if story_context:
            combined_analysis = self._apply_story_context(
                combined_analysis, story_context
            )

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
            await self._update_psychological_profile(
                child_name, device_id, voice_analysis
            )

        return voice_analysis

    async def _extract_voice_features(
            self, audio_data: bytes) -> Dict[str, float]:
        """استخراج خصائص الصوت الأساسية"""
        # محاكاة تحليل الصوت - في التطبيق الحقيقي نستخدم مكتبات مثل librosa

        import random

        # محاكاة تحليل السرعة
        speed_wpm = random.uniform(80, 200)  # كلمات في الدقيقة

        # محاكاة تحليل التوقفات
        pause_frequency = random.uniform(0.1, 0.8)  # نسبة التوقفات
        pause_duration_avg = random.uniform(
            0.2, 2.0)  # متوسط مدة التوقف بالثواني

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

    def _get_word_lists(self) -> Dict[str, List[str]]:
        """Returns a dictionary of word lists for speech pattern analysis."""
        return {
            "hesitation": [
                "أمم", "أه", "لست متأكد", "ربما", "لا أعرف", "أعتقد"],
            "anxiety": [
                "مخيف", "خائف", "قلق", "لا أستطيع", "صعب"],
            "confidence": [
                "نعم", "أكيد", "بالطبع", "أستطيع", "سأفعل"],
            "happiness": [
                "سعيد", "رائع", "ممتع", "أحب", "جميل"],
        }

    async def _analyze_speech_patterns(self, text: str) -> Dict[str, Any]:
        """تحليل أنماط الكلام"""
        word_lists = self._get_word_lists()
        text_lower = text.lower()
        word_count = len(text.split())

        if word_count == 0:
            return {
                "hesitation_score": 0,
                "anxiety_score": 0,
                "confidence_score": 0,
                "happiness_score": 0,
                "text_length": 0,
            }

        scores = {}
        for key, words in word_lists.items():
            score = sum(1 for word in words if word in text_lower) / word_count
            scores[f"{key}_score"] = score

        scores["text_length"] = word_count
        return scores

    def _determine_emotional_tone(
        self, voice_features: Dict, text_analysis: Dict
    ) -> str:
        """Determines the emotional tone from combined analysis."""
        if text_analysis["anxiety_score"] > 0.3:
            return "قلق"
        if text_analysis["happiness_score"] > 0.2:
            return "سعيد"
        if voice_features["speed_wpm"] < 100:
            return "هادئ"
        if voice_features["speed_wpm"] > 160:
            return "متحمس"
        return "عادي"

    def _detect_voice_patterns(
            self,
            combined_confidence: float,
            text_analysis: Dict,
            voice_features: Dict) -> List[VoicePattern]:
        """Detects voice patterns from combined analysis."""
        patterns = []
        if combined_confidence < 0.4:
            patterns.append(VoicePattern.HESITANT)
        elif combined_confidence > 0.7:
            patterns.append(VoicePattern.CONFIDENT)

        if text_analysis.get("anxiety_score", 0) > 0.3:
            patterns.append(VoicePattern.ANXIOUS)

        if voice_features.get("speed_wpm", 120) > 160:
            patterns.append(VoicePattern.EXCITED)
        elif voice_features.get("speed_wpm", 120) < 100:
            patterns.append(VoicePattern.CALM)

        return patterns

    def _combine_voice_and_text_analysis(
        self, voice_features: Dict, text_analysis: Dict
    ) -> Dict[str, Any]:
        """دمج تحليل الصوت والنص"""
        voice_confidence = 1.0 - (
            voice_features["pause_frequency"] * 0.5
            + (1.0 - voice_features["volume_consistency"]) * 0.3
        )
        text_confidence = (
            text_analysis["confidence_score"] -
            text_analysis["hesitation_score"])
        combined_confidence = max(
            0.0, min(1.0, voice_confidence * 0.6 + text_confidence * 0.4)
        )

        emotional_tone = self._determine_emotional_tone(
            voice_features, text_analysis)
        detected_patterns = self._detect_voice_patterns(
            combined_confidence, text_analysis, voice_features
        )

        return {
            "confidence_score": combined_confidence,
            "emotional_tone": emotional_tone,
            "detected_patterns": detected_patterns,
        }

    def _apply_story_context(
        self, analysis: Dict, story_context: Dict
    ) -> Dict[str, Any]:
        """تطبيق سياق القصة على التحليل"""

        # إذا كان السياق يتطلب شجاعة ولكن الطفل أظهر قلق
        if (
            story_context.get("requires_courage")
            and VoicePattern.ANXIOUS in analysis["detected_patterns"]
        ):
            analysis["context_notes"] = "أظهر قلقاً في موقف يتطلب الشجاعة"

        # إذا كان السياق اجتماعي والطفل أظهر تردد
        if (
            story_context.get("social_situation")
            and VoicePattern.HESITANT in analysis["detected_patterns"]
        ):
            analysis["context_notes"] = "تردد في الموقف الاجتماعي"

        return analysis

    def _get_or_create_profile(
        self, child_name: str, device_id: str
    ) -> PsychologicalProfile:
        """Gets an existing psychological profile or creates a new one."""
        profile_key = f"{device_id}_{child_name}"
        if profile_key not in self.psychological_profiles:
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
        return self.psychological_profiles[profile_key]

    def _update_profile_trends(
        self, profile: PsychologicalProfile, voice_analysis: VoiceAnalysis
    ):
        """Updates the confidence and emotional pattern trends for a profile."""
        profile.confidence_trend.append(voice_analysis.confidence_score)
        if len(profile.confidence_trend) > 20:
            profile.confidence_trend.pop(0)

        emotional_tone = voice_analysis.emotional_tone
        profile.emotional_patterns.setdefault(emotional_tone, []).append(
            voice_analysis.confidence_score
        )

    def _update_profile_indicators(
        self, profile: PsychologicalProfile, voice_analysis: VoiceAnalysis
    ):
        """Updates stress indicators and strengths based on the latest analysis."""
        if (
            VoicePattern.ANXIOUS in voice_analysis.detected_patterns
            and "قلق متكرر" not in profile.stress_indicators
        ):
            profile.stress_indicators.append("قلق متكرر")

        if (
            voice_analysis.confidence_score < 0.3
            and "ثقة منخفضة" not in profile.stress_indicators
        ):
            profile.stress_indicators.append("ثقة منخفضة")

        if (
            voice_analysis.confidence_score > 0.7
            and "ثقة عالية بالنفس" not in profile.strengths
        ):
            profile.strengths.append("ثقة عالية بالنفس")

    async def _update_psychological_profile(
        self, child_name: str, device_id: str, voice_analysis: VoiceAnalysis
    ):
        """تحديث الملف النفسي للطفل"""
        profile = self._get_or_create_profile(child_name, device_id)

        self._update_profile_trends(profile, voice_analysis)
        self._update_profile_indicators(profile, voice_analysis)

        profile.last_updated = datetime.now()

        await self.check_for_behavioral_concerns(child_name, device_id)

    async def check_for_behavioral_concerns(
            self, child_name: str, device_id: str):
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

    async def _check_repeated_anxiety(
        self, child_name: str, device_id: str, analyses: List[VoiceAnalysis]
    ):
        """فحص القلق المتكرر"""

        anxiety_count = sum(
            1
            for analysis in analyses[-7:]
            if VoicePattern.ANXIOUS in analysis.detected_patterns
        )

        threshold = self.concern_thresholds[BehavioralConcern.REPEATED_ANXIETY]

        if anxiety_count >= threshold["min_occurrences"]:
            # إنشاء تنبيه
            alert_details = alert_messages.REPEATED_ANXIETY
            alert = BehavioralAlert(
                id=f"anxiety_{device_id}_{datetime.now().timestamp()}",
                child_name=child_name,
                device_id=device_id,
                concern_type=BehavioralConcern.REPEATED_ANXIETY,
                severity_level="متوسط" if anxiety_count < 5 else "عالي",
                description=alert_details["description"].format(
                    count=anxiety_count),
                evidence=[ev.format(count=anxiety_count)
                          for ev in alert_details["evidence"]],
                recommendations=alert_details["recommendations"],
                created_at=datetime.now(),
            )

            self.behavioral_alerts.append(alert)

    async def _check_low_confidence(
        self, child_name: str, device_id: str, analyses: List[VoiceAnalysis]
    ):
        """فحص انخفاض الثقة"""

        recent_confidence = [
            analysis.confidence_score for analysis in analyses[-5:]]
        avg_confidence = sum(recent_confidence) / len(recent_confidence)

        threshold = self.concern_thresholds[BehavioralConcern.LOW_CONFIDENCE]

        if avg_confidence < threshold["confidence_threshold"]:
            alert_details = alert_messages.LOW_CONFIDENCE
            alert = BehavioralAlert(
                id=f"confidence_{device_id}_{datetime.now().timestamp()}",
                child_name=child_name,
                device_id=device_id,
                concern_type=BehavioralConcern.LOW_CONFIDENCE,
                severity_level="متوسط",
                description=alert_details["description"].format(
                    avg_confidence=avg_confidence),
                evidence=[ev.format(avg_confidence=avg_confidence)
                          for ev in alert_details["evidence"]],
                recommendations=alert_details["recommendations"],
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
                alert_details = alert_messages.SOCIAL_WITHDRAWAL
                alert = BehavioralAlert(
                    id=f"social_{device_id}_{datetime.now().timestamp()}",
                    child_name=child_name,
                    device_id=device_id,
                    concern_type=BehavioralConcern.SOCIAL_WITHDRAWAL,
                    severity_level="متوسط",
                    description=alert_details["description"],
                    evidence=[ev.format(social_skills_level=profile.social_skills_level)
                              for ev in alert_details["evidence"]],
                    recommendations=alert_details["recommendations"],
                    created_at=datetime.now(),
                )

                self.behavioral_alerts.append(alert)

    def get_child_psychological_report(
        self, child_name: str, device_id: str
    ) -> Dict[str, Any]:
        """
        إنشاء تقرير نفسي مفصل للطفل.
        """
        profile_key = f"{device_id}_{child_name}"
        profile = self.psychological_profiles.get(profile_key)

        if not profile:
            return {"error": "لم يتم العثور على ملف نفسي لهذا الطفل."}

        recommendations = self._generate_overall_recommendations(profile)

        return self._build_psychological_report_dict(profile, recommendations)

    def _build_psychological_report_dict(
        self, profile: PsychologicalProfile, recommendations: List[str]
    ) -> Dict[str, Any]:
        """Builds the psychological report dictionary from a profile and recommendations."""
        main_trait = (
            max(profile.personality_traits, key=profile.personality_traits.get)
            if profile.personality_traits
            else "غير محدد"
        )
        current_emotion = (
            list(profile.emotional_patterns.keys())[-1]
            if profile.emotional_patterns
            else "غير محدد"
        )
        confidence = (
            f"{profile.confidence_trend[-1]:.2f}"
            if profile.confidence_trend
            else "غير محدد"
        )
        top_concern = (
            profile.areas_of_concern[0]
            if profile.areas_of_concern
            else "لا يوجد مخاوف حالية"
        )

        return {
            "child_name": profile.child_name,
            "device_id": profile.device_id,
            "report_generated_at": datetime.now().isoformat(),
            "summary": {
                "main_personality_trait": main_trait,
                "current_emotional_state": current_emotion,
                "confidence_level": confidence,
                "top_concern": top_concern,
            },
            "details": {
                "personality_traits": profile.personality_traits,
                "emotional_patterns": profile.emotional_patterns,
                "confidence_trend": profile.confidence_trend,
                "stress_indicators": profile.stress_indicators,
                "strengths": profile.strengths,
                "areas_of_concern": profile.areas_of_concern,
            },
            "recommendations_for_parents": recommendations,
        }

    def _generate_overall_recommendations(
        self, profile: PsychologicalProfile
    ) -> List[str]:
        """توليد توصيات شاملة"""
        recommendations = []

        # توصيات بناءً على الثقة
        if profile.confidence_trend:
            avg_confidence = sum(profile.confidence_trend) / len(
                profile.confidence_trend
            )

            if avg_confidence < 0.4:
                recommendations.extend(
                    [
                        "ركز على بناء الثقة بالنفس من خلال الأنشطة البسيطة",
                        "احتفل بكل إنجاز مهما كان صغيراً",
                        "تجنب المقارنات مع الآخرين",
                    ]
                )
            elif avg_confidence > 0.7:
                recommendations.append(
                    "الطفل يُظهر ثقة جيدة بالنفس - استمر في التشجيع")

        # توصيات بناءً على المهارات الاجتماعية
        if profile.social_skills_level < 0.4:
            recommendations.extend(
                [
                    "شجع الأنشطة الاجتماعية التدريجية",
                    "انضم لمجموعات لعب منظمة",
                    "مارس الحوار والمشاركة في المنزل",
                ]
            )

        # توصيات بناءً على مؤشرات التوتر
        if "قلق متكرر" in profile.stress_indicators:
            recommendations.extend(
                [
                    "علم الطفل تقنيات التنفس العميق",
                    "وفر روتين يومي مستقر",
                    "فكر في استشارة مختص إذا استمر القلق",
                ]
            )

        return recommendations

    def get_parent_alerts(
            self,
            device_id: str,
            unread_only: bool = True) -> List[Dict]:
        """الحصول على تنبيهات الوالدين"""

        alerts = [
            alert for alert in self.behavioral_alerts if alert.device_id == device_id]

        if unread_only:
            alerts = [alert for alert in alerts if not alert.parent_notified]

        return [{"id": alert.id,
                 "child_name": alert.child_name,
                 "concern_type": alert.concern_type.value,
                 "severity": alert.severity_level,
                 "description": alert.description,
                 "evidence": alert.evidence,
                 "recommendations": alert.recommendations,
                 "created_at": alert.created_at.isoformat(),
                 "is_urgent": alert.severity_level == "عالي",
                 } for alert in sorted(alerts,
                                       key=lambda x: x.created_at,
                                       reverse=True)]

    def mark_alert_as_read(self, alert_id: str) -> None:
        """تأشير التنبيه كمقروء"""
        for alert in self.behavioral_alerts:
            if alert.id == alert_id:
                alert.parent_notified = True
                break
