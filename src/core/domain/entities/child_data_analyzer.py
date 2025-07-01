#!/usr/bin/env python3
"""
Child Data Analyzer Service - Single Responsibility
==================================================
مسؤول فقط عن تحليل بيانات الطفل
"""

import logging
import statistics
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class DateRange:
    """نطاق زمني للتحليل"""

    start_date: datetime
    end_date: datetime


@dataclass
class InteractionData:
    """بيانات تفاعل واحد"""

    timestamp: datetime
    duration: int  # seconds
    emotions: Dict[str, float]
    topics: List[str]
    skills_used: List[str]
    behavioral_indicators: List[str]
    quality_score: float


@dataclass
class AnalysisResult:
    """نتيجة تحليل بيانات الطفل"""

    child_id: str
    analysis_period: DateRange

    # Emotional metrics
    emotion_distribution: Dict[str, float]
    dominant_emotion: str
    emotion_stability: float
    mood_trends: Dict[str, List[float]]

    # Behavioral metrics
    attention_span: float
    response_patterns: Dict[str, float]
    social_indicators: Dict[str, int]

    # Learning metrics
    vocabulary_growth: int
    skills_progress: Dict[str, float]
    learning_patterns: List[str]

    # Concerns and recommendations
    concerning_patterns: List[str]
    development_recommendations: List[str]


class ChildDataAnalyzer:
    """مسؤول فقط عن تحليل بيانات الطفل"""

    def __init__(self, database_service=None):
        self.db = database_service

    async def analyze(self, child_id: str, period: DateRange) -> AnalysisResult:
        """
        تحليل بيانات الطفل - المسؤولية الوحيدة لهذا الكلاس

        Args:
            child_id: معرف الطفل
            period: الفترة الزمنية للتحليل

        Returns:
            AnalysisResult with comprehensive analysis
        """
        try:
            # جلب بيانات التفاعلات
            interactions = await self._get_interactions_data(child_id, period)

            if not interactions:
                logger.warning(f"No interaction data found for child {child_id}")
                return self._create_empty_analysis(child_id, period)

            # تحليل المشاعر
            emotion_analysis = self._analyze_emotions(interactions)

            # تحليل السلوك
            behavior_analysis = self._analyze_behavior(interactions)

            # تحليل التعلم
            learning_analysis = self._analyze_learning(interactions)

            # تحديد المشاكل والتوصيات
            concerns = self._identify_concerns(interactions, emotion_analysis, behavior_analysis)
            recommendations = self._generate_recommendations(emotion_analysis, behavior_analysis, learning_analysis)

            result = AnalysisResult(
                child_id=child_id,
                analysis_period=period,
                emotion_distribution=emotion_analysis["distribution"],
                dominant_emotion=emotion_analysis["dominant"],
                emotion_stability=emotion_analysis["stability"],
                mood_trends=emotion_analysis["trends"],
                attention_span=behavior_analysis["attention_span"],
                response_patterns=behavior_analysis["response_patterns"],
                social_indicators=behavior_analysis["social_indicators"],
                vocabulary_growth=learning_analysis["vocabulary_growth"],
                skills_progress=learning_analysis["skills_progress"],
                learning_patterns=learning_analysis["patterns"],
                concerning_patterns=concerns,
                development_recommendations=recommendations,
            )

            logger.info(f"Analysis completed for child {child_id}")
            return result

        except Exception as e:
            logger.error(f"Analysis error for child {child_id}: {e}")
            return self._create_empty_analysis(child_id, period)

    def _analyze_emotions(self, interactions: List[InteractionData]) -> Dict:
        """تحليل المشاعر فقط"""
        try:
            # توزيع المشاعر
            emotion_counts = {}
            all_emotions = []

            for interaction in interactions:
                for emotion, intensity in interaction.emotions.items():
                    emotion_counts[emotion] = emotion_counts.get(emotion, 0) + intensity
                    all_emotions.append((emotion, intensity))

            # تحديد المشاعر المهيمنة
            total_emotions = sum(emotion_counts.values())
            distribution = {emotion: count / total_emotions for emotion, count in emotion_counts.items()}
            dominant = max(distribution.keys(), key=distribution.get) if distribution else "calm"

            # حساب استقرار المشاعر
            stability = self._calculate_emotion_stability(interactions)

            # اتجاهات المزاج عبر الوقت
            trends = self._calculate_mood_trends(interactions)

            return {"distribution": distribution, "dominant": dominant, "stability": stability, "trends": trends}

        except Exception as e:
            logger.error(f"Emotion analysis error: {e}")
            return {"distribution": {}, "dominant": "calm", "stability": 0.5, "trends": {}}

    def _analyze_behavior(self, interactions: List[InteractionData]) -> Dict:
        """تحليل السلوك فقط"""
        try:
            # حساب مدة التركيز
            durations = [interaction.duration for interaction in interactions]
            attention_span = statistics.mean(durations) / 60 if durations else 0  # في دقائق

            # أنماط الاستجابة
            response_patterns = self._analyze_response_patterns(interactions)

            # المؤشرات الاجتماعية
            social_indicators = self._count_social_indicators(interactions)

            return {
                "attention_span": attention_span,
                "response_patterns": response_patterns,
                "social_indicators": social_indicators,
            }

        except Exception as e:
            logger.error(f"Behavior analysis error: {e}")
            return {"attention_span": 0, "response_patterns": {}, "social_indicators": {}}

    def _analyze_learning(self, interactions: List[InteractionData]) -> Dict:
        """تحليل التعلم فقط"""
        try:
            # نمو المفردات
            all_topics = []
            for interaction in interactions:
                all_topics.extend(interaction.topics)

            vocabulary_growth = len(set(all_topics))

            # تقدم المهارات
            skills_usage = {}
            for interaction in interactions:
                for skill in interaction.skills_used:
                    skills_usage[skill] = skills_usage.get(skill, 0) + 1

            # تحويل إلى نسب تقدم
            max_usage = max(skills_usage.values()) if skills_usage else 1
            skills_progress = {skill: count / max_usage for skill, count in skills_usage.items()}

            # أنماط التعلم
            learning_patterns = self._identify_learning_patterns(interactions)

            return {
                "vocabulary_growth": vocabulary_growth,
                "skills_progress": skills_progress,
                "patterns": learning_patterns,
            }

        except Exception as e:
            logger.error(f"Learning analysis error: {e}")
            return {"vocabulary_growth": 0, "skills_progress": {}, "patterns": []}

    def _calculate_emotion_stability(self, interactions: List[InteractionData]) -> float:
        """حساب استقرار المشاعر"""
        try:
            if len(interactions) < 2:
                return 0.5

            # حساب التباين في المشاعر المهيمنة
            dominant_emotions = []
            for interaction in interactions:
                if interaction.emotions:
                    dominant = max(interaction.emotions.keys(), key=interaction.emotions.get)
                    dominant_emotions.append(dominant)

            # حساب التنوع
            unique_emotions = len(set(dominant_emotions))
            total_emotions = len(dominant_emotions)

            # كلما قل التنوع، زاد الاستقرار
            stability = 1.0 - (unique_emotions - 1) / max(total_emotions - 1, 1)
            return max(0.0, min(1.0, stability))

        except Exception as e:
            logger.error(f"Emotion stability calculation error: {e}")
            return 0.5

    def _calculate_mood_trends(self, interactions: List[InteractionData]) -> Dict[str, List[float]]:
        """حساب اتجاهات المزاج"""
        try:
            # تجميع المشاعر حسب اليوم
            daily_emotions = {}

            for interaction in interactions:
                day = interaction.timestamp.date()
                if day not in daily_emotions:
                    daily_emotions[day] = {}

                for emotion, intensity in interaction.emotions.items():
                    if emotion not in daily_emotions[day]:
                        daily_emotions[day][emotion] = []
                    daily_emotions[day][emotion].append(intensity)

            # حساب متوسط يومي لكل مشاعر
            trends = {}
            all_emotions = set()
            for day_emotions in daily_emotions.values():
                all_emotions.update(day_emotions.keys())

            for emotion in all_emotions:
                trends[emotion] = []
                for day in sorted(daily_emotions.keys()):
                    if emotion in daily_emotions[day]:
                        avg_intensity = statistics.mean(daily_emotions[day][emotion])
                        trends[emotion].append(avg_intensity)
                    else:
                        trends[emotion].append(0.0)

            return trends

        except Exception as e:
            logger.error(f"Mood trends calculation error: {e}")
            return {}

    def _analyze_response_patterns(self, interactions: List[InteractionData]) -> Dict[str, float]:
        """تحليل أنماط الاستجابة"""
        try:
            patterns = {
                "quick_response": 0,  # استجابة سريعة
                "thoughtful_response": 0,  # استجابة متأنية
                "creative_response": 0,  # استجابة إبداعية
                "emotional_response": 0,  # استجابة عاطفية
            }

            for interaction in interactions:
                # تحديد نوع الاستجابة بناءً على المدة والمحتوى
                if interaction.duration < 30:  # أقل من 30 ثانية
                    patterns["quick_response"] += 1
                elif interaction.duration > 120:  # أكثر من دقيقتين
                    patterns["thoughtful_response"] += 1

                # فحص المؤشرات السلوكية
                if "creative" in interaction.behavioral_indicators:
                    patterns["creative_response"] += 1
                if "emotional" in interaction.behavioral_indicators:
                    patterns["emotional_response"] += 1

            # تحويل إلى نسب
            total = len(interactions)
            if total > 0:
                patterns = {key: value / total for key, value in patterns.items()}

            return patterns

        except Exception as e:
            logger.error(f"Response patterns analysis error: {e}")
            return {}

    def _count_social_indicators(self, interactions: List[InteractionData]) -> Dict[str, int]:
        """عد المؤشرات الاجتماعية"""
        try:
            indicators = {"empathy": 0, "sharing": 0, "cooperation": 0, "politeness": 0}

            for interaction in interactions:
                for indicator in interaction.behavioral_indicators:
                    if "empathy" in indicator.lower():
                        indicators["empathy"] += 1
                    elif "sharing" in indicator.lower() or "share" in indicator.lower():
                        indicators["sharing"] += 1
                    elif "cooperation" in indicator.lower() or "cooperate" in indicator.lower():
                        indicators["cooperation"] += 1
                    elif "polite" in indicator.lower() or "please" in indicator.lower() or "thank" in indicator.lower():
                        indicators["politeness"] += 1

            return indicators

        except Exception as e:
            logger.error(f"Social indicators counting error: {e}")
            return {}

    def _identify_learning_patterns(self, interactions: List[InteractionData]) -> List[str]:
        """تحديد أنماط التعلم"""
        try:
            patterns = []

            # تحليل أوقات النشاط
            morning_interactions = sum(1 for i in interactions if 6 <= i.timestamp.hour < 12)
            afternoon_interactions = sum(1 for i in interactions if 12 <= i.timestamp.hour < 18)
            evening_interactions = sum(1 for i in interactions if 18 <= i.timestamp.hour < 22)

            total = len(interactions)
            if total > 0:
                if morning_interactions / total > 0.4:
                    patterns.append("learner_morning_active")
                if afternoon_interactions / total > 0.4:
                    patterns.append("learner_afternoon_active")
                if evening_interactions / total > 0.4:
                    patterns.append("learner_evening_active")

            # تحليل تفضيلات المواضيع
            topic_counts = {}
            for interaction in interactions:
                for topic in interaction.topics:
                    topic_counts[topic] = topic_counts.get(topic, 0) + 1

            if topic_counts:
                favorite_topic = max(topic_counts.keys(), key=topic_counts.get)
                patterns.append(f"prefers_{favorite_topic}")

            return patterns

        except Exception as e:
            logger.error(f"Learning patterns identification error: {e}")
            return []

    def _identify_concerns(
        self, interactions: List[InteractionData], emotion_analysis: Dict, behavior_analysis: Dict
    ) -> List[str]:
        """تحديد المشاكل المثيرة للقلق"""
        concerns = []

        # فحص استقرار المشاعر
        if emotion_analysis.get("stability", 0.5) < 0.3:
            concerns.append("emotion_instability")

        # فحص مدة التركيز
        if behavior_analysis.get("attention_span", 0) < 2:  # أقل من دقيقتين
            concerns.append("short_attention_span")

        # فحص المشاعر السلبية المهيمنة
        negative_emotions = ["sad", "angry", "scared"]
        if emotion_analysis.get("dominant") in negative_emotions:
            concerns.append("negative_emotional_dominance")

        return concerns

    def _generate_recommendations(
        self, emotion_analysis: Dict, behavior_analysis: Dict, learning_analysis: Dict
    ) -> List[str]:
        """إنشاء توصيات التطوير"""
        recommendations = []

        # توصيات عاطفية
        if emotion_analysis.get("stability", 0.5) < 0.5:
            recommendations.append("focus_on_emotional_regulation_activities")

        # توصيات سلوكية
        if behavior_analysis.get("attention_span", 0) < 5:
            recommendations.append("implement_short_engaging_activities")

        # توصيات تعليمية
        if learning_analysis.get("vocabulary_growth", 0) < 10:
            recommendations.append("increase_vocabulary_building_activities")

        return recommendations

    async def _get_interactions_data(self, child_id: str, period: DateRange) -> List[InteractionData]:
        """جلب بيانات التفاعلات من قاعدة البيانات"""
        if not self.db:
            # بيانات تجريبية للاختبار
            return [
                InteractionData(
                    timestamp=datetime.now() - timedelta(days=1),
                    duration=180,
                    emotions={"happy": 0.7, "curious": 0.3},
                    topics=["colors", "animals"],
                    skills_used=["counting", "naming"],
                    behavioral_indicators=["attentive", "responsive"],
                    quality_score=0.8,
                )
            ]

        return await self.db.get_interactions(child_id, period.start_date, period.end_date)

    def _create_empty_analysis(self, child_id: str, period: DateRange) -> AnalysisResult:
        """إنشاء تحليل فارغ في حالة عدم وجود بيانات"""
        return AnalysisResult(
            child_id=child_id,
            analysis_period=period,
            emotion_distribution={},
            dominant_emotion="calm",
            emotion_stability=0.5,
            mood_trends={},
            attention_span=0,
            response_patterns={},
            social_indicators={},
            vocabulary_growth=0,
            skills_progress={},
            learning_patterns=[],
            concerning_patterns=[],
            development_recommendations=[],
        )
