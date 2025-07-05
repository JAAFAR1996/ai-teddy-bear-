"""
Behavior Analysis Domain Service
Analyzes behavioral patterns and social development
"""

import logging
from statistics import mean
from typing import Any, Dict, List

from ..models.report_models import InteractionAnalysis


class BehaviorAnalyzer:
    """Domain service for behavior analysis"""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def _check_interaction_volume(
        self, interactions: List[InteractionAnalysis]
    ) -> List[str]:
        """Check for low interaction count and short conversation duration."""
        areas = []
        if len(interactions) < 3:
            areas.append("زيادة تكرار التفاعلات")

        avg_duration = sum(
            interaction.duration for interaction in interactions) / len(interactions)
        if avg_duration < 120:  # Less than 2 minutes
            areas.append("تطوير مدة التفاعل والتركيز")
        return areas

    def _check_topic_diversity(
        self, interactions: List[InteractionAnalysis]
    ) -> List[str]:
        """Check for limited topic diversity."""
        all_topics = [
            topic
            for interaction in interactions
            for topic in interaction.topics_discussed
        ]
        if len(set(all_topics)) < 5:
            return ["توسيع المواضيع المناقشة"]
        return []

    def _check_interaction_quality(
        self, interactions: List[InteractionAnalysis]
    ) -> List[str]:
        """Check for low quality interactions."""
        high_quality_count = sum(
            1 for interaction in interactions if interaction.is_high_quality()
        )
        if high_quality_count < len(interactions) * 0.5:
            return ["تحسين جودة التفاعل والمشاركة"]
        return []

    def _check_concerning_patterns(
        self, interactions: List[InteractionAnalysis]
    ) -> List[str]:
        """Check for concerning behavioral patterns."""
        negative_indicators = [
            "withdrawal",
            "aggression",
            "defiance",
            "inattention",
            "انسحاب",
            "عدوانية",
            "تمرد",
            "عدم انتباه",
        ]
        all_indicators = [
            indicator
            for interaction in interactions
            for indicator in interaction.behavioral_indicators
        ]
        concerning_count = sum(
            1
            for indicator in all_indicators
            if any(neg in indicator.lower() for neg in negative_indicators)
        )

        if concerning_count > len(interactions) * 0.3:
            return ["تطوير مهارات التنظيم الذاتي"]
        return []

    def _check_skill_development(
        self, interactions: List[InteractionAnalysis]
    ) -> List[str]:
        """Check attention span and social skills development."""
        areas = []
        if self._calculate_attention_span(interactions) < 3:
            areas.append("تحسين فترة التركيز والانتباه")

        social_skills_used = sum(
            1
            for interaction in interactions
            if "social_skills" in interaction.skills_used
        )
        if social_skills_used < len(interactions) * 0.2:
            areas.append("تطوير المهارات الاجتماعية")
        return areas

    def identify_improvement_areas(
        self, interactions: List[InteractionAnalysis]
    ) -> List[str]:
        """Identify behavioral areas needing improvement"""
        try:
            if not interactions:
                return ["لا توجد بيانات كافية للتحليل"]

            improvement_areas = []

            check_functions = [
                self._check_interaction_volume,
                self._check_topic_diversity,
                self._check_interaction_quality,
                self._check_concerning_patterns,
                self._check_skill_development,
            ]

            for check_func in check_functions:
                improvement_areas.extend(check_func(interactions))

            return list(set(improvement_areas))  # Return unique areas

        except Exception as e:
            self.logger.error(f"Improvement areas identification error: {e}")
            return ["خطأ في تحليل البيانات"]

    def _calculate_attention_span(
        self, interactions: List[InteractionAnalysis]
    ) -> float:
        """Calculate average attention span in minutes"""
        try:
            if not interactions:
                return 0.0

            durations = [interaction.duration_minutes()
                         for interaction in interactions]
            return mean(durations)

        except Exception as e:
            self.logger.error(f"Attention span calculation error: {e}")
            return 0.0

    def _analyze_engagement_level(
            self, interactions: List[InteractionAnalysis]) -> str:
        """Analyzes the engagement level from interactions."""
        avg_quality = mean(
            interaction.quality_score for interaction in interactions)
        if avg_quality >= 0.8:
            return "high"
        elif avg_quality >= 0.6:
            return "medium"
        return "low"

    def _analyze_attention_consistency(
        self, interactions: List[InteractionAnalysis]
    ) -> str:
        """Analyzes the attention consistency from interactions."""
        durations = [interaction.duration_minutes()
                     for interaction in interactions]
        if not durations:
            return "variable"

        duration_variance = self._calculate_variance(durations)
        if duration_variance < 2:
            return "consistent"
        elif duration_variance < 5:
            return "moderate"
        return "variable"

    def _analyze_social_responsiveness(
        self, interactions: List[InteractionAnalysis]
    ) -> str:
        """Analyzes the social responsiveness from interactions."""
        social_indicators = 0
        for interaction in interactions:
            if "social_skills" in interaction.skills_used:
                social_indicators += 1
            if any("social" in topic.lower()
                   for topic in interaction.topics_discussed):
                social_indicators += 1

        social_rate = social_indicators / len(interactions)
        if social_rate >= 0.6:
            return "excellent"
        elif social_rate >= 0.4:
            return "good"
        elif social_rate >= 0.2:
            return "developing"
        return "needs_attention"

    def _analyze_emotional_regulation(
        self, interactions: List[InteractionAnalysis]
    ) -> str:
        """Analyzes emotional regulation from interactions."""
        if len(interactions) <= 1:
            return "stable"

        emotion_changes = sum(
            1
            for i in range(1, len(interactions))
            if interactions[i].primary_emotion != interactions[i - 1].primary_emotion
        )
        change_rate = emotion_changes / (len(interactions) - 1)

        if change_rate < 0.3:
            return "excellent"
        elif change_rate < 0.6:
            return "stable"
        return "needs_support"

    def _analyze_cooperation_level(
        self, interactions: List[InteractionAnalysis]
    ) -> str:
        """Analyzes the cooperation level from interactions."""
        cooperation_score = self._calculate_cooperation_score(interactions)
        if cooperation_score >= 0.8:
            return "excellent"
        elif cooperation_score >= 0.6:
            return "good"
        elif cooperation_score >= 0.4:
            return "medium"
        return "needs_improvement"

    def analyze_behavioral_patterns(
        self, interactions: List[InteractionAnalysis]
    ) -> Dict[str, Any]:
        """Analyze overall behavioral patterns"""
        try:
            if not interactions:
                return {
                    "engagement_level": "low",
                    "attention_consistency": "variable",
                    "social_responsiveness": "developing",
                    "emotional_regulation": "stable",
                    "cooperation_level": "medium",
                    "behavioral_concerns": [],
                }

            patterns = {
                "engagement_level": self._analyze_engagement_level(interactions),
                "attention_consistency": self._analyze_attention_consistency(interactions),
                "social_responsiveness": self._analyze_social_responsiveness(interactions),
                "emotional_regulation": self._analyze_emotional_regulation(interactions),
                "cooperation_level": self._analyze_cooperation_level(interactions),
                "behavioral_concerns": self._identify_behavioral_concerns(interactions),
            }
            return patterns

        except Exception as e:
            self.logger.error(f"Behavioral pattern analysis error: {e}")
            return {"error": "Analysis failed"}

    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of a list of values"""
        if len(values) < 2:
            return 0.0

        avg = mean(values)
        variance = sum((x - avg) ** 2 for x in values) / len(values)
        return variance

    def _calculate_cooperation_score(
        self, interactions: List[InteractionAnalysis]
    ) -> float:
        """Calculate cooperation score based on interactions"""
        try:
            if not interactions:
                return 0.0

            cooperation_indicators = []

            for interaction in interactions:
                score = 0.0

                # High quality indicates cooperation
                score += interaction.quality_score * 0.4

                # Positive emotions indicate cooperation
                positive_emotions = ["happy", "calm", "curious"]
                for emotion in positive_emotions:
                    score += interaction.emotions.get(emotion, 0) * 0.2

                cooperation_indicators.append(min(1.0, score))

            return mean(cooperation_indicators)

        except Exception as e:
            self.logger.error(f"Cooperation score calculation error: {e}")
            return 0.5

    def _check_negative_sentiment(
        self, interactions: List[InteractionAnalysis]
    ) -> bool:
        """Check for persistent negative sentiment."""
        negative_emotions = [
            interaction.emotions.get("sad", 0) + interaction.emotions.get("angry", 0)
            for interaction in interactions
        ]
        return mean(negative_emotions) > 0.4

    def _check_low_engagement(
            self,
            interactions: List[InteractionAnalysis]) -> bool:
        """Check for low engagement levels."""
        engagement_scores = [
            interaction.quality_score for interaction in interactions]
        return mean(engagement_scores) < 0.3

    def _check_social_withdrawal(
            self, interactions: List[InteractionAnalysis]) -> bool:
        """Check for signs of social withdrawal."""
        social_skills_used = sum(
            1
            for interaction in interactions
            if "social_skills" in interaction.skills_used
        )
        return (social_skills_used / len(interactions)) < 0.1

    def _check_attention_deficit(
            self, interactions: List[InteractionAnalysis]) -> bool:
        """Check for attention deficit signs."""
        return self._calculate_attention_span(interactions) < 1.5

    def _identify_behavioral_concerns(
        self, interactions: List[InteractionAnalysis]
    ) -> List[str]:
        """Identify significant behavioral concerns from interactions."""
        if not interactions:
            return []

        concerns = []

        concern_checks = [
            ("Persistent Negative Sentiment", self._check_negative_sentiment),
            ("Low Engagement", self._check_low_engagement),
            ("Social Withdrawal", self._check_social_withdrawal),
            ("Attention Deficit", self._check_attention_deficit),
        ]

        for concern_name, check_func in concern_checks:
            if check_func(interactions):
                concerns.append(concern_name)

        return concerns

    def generate_behavioral_recommendations(
        self, interactions: List[InteractionAnalysis]
    ) -> List[str]:
        """Generate recommendations for behavioral improvement"""
        try:
            recommendations = []

            improvement_areas = self.identify_improvement_areas(interactions)

            # Map improvement areas to specific recommendations
            area_recommendations = {
                "زيادة تكرار التفاعلات": [
                    "تحديد أوقات ثابتة للتفاعل يومياً",
                    "استخدام تذكيرات لجلسات التفاعل",
                ],
                "تطوير مدة التفاعل والتركيز": [
                    "بدء بجلسات قصيرة وزيادتها تدريجياً",
                    "استخدام أنشطة تفاعلية مثيرة للاهتمام",
                ],
                "توسيع المواضيع المناقشة": [
                    "تقديم مواضيع جديدة ومتنوعة",
                    "ربط المواضيع باهتمامات الطفل",
                ],
                "تحسين جودة التفاعل والمشاركة": [
                    "تشجيع الطفل على المشاركة الفعّالة",
                    "استخدام أساليب تفاعل إيجابية",
                ],
                "تطوير مهارات التنظيم الذاتي": [
                    "تعليم تقنيات التهدئة الذاتية",
                    "وضع قواعد واضحة للتفاعل",
                ],
            }

            # Add specific recommendations based on improvement areas
            for area in improvement_areas:
                if area in area_recommendations:
                    recommendations.extend(area_recommendations[area])

            # Add general behavioral recommendations
            if len(interactions) > 0:
                avg_quality = mean(
                    interaction.quality_score for interaction in interactions
                )
                if avg_quality < 0.6:
                    recommendations.append("إنشاء بيئة داعمة ومشجعة للتفاعل")
                    recommendations.append(
                        "استخدام نظام مكافآت للسلوك الإيجابي")

            return list(set(recommendations))  # Remove duplicates

        except Exception as e:
            self.logger.error(
                f"Behavioral recommendations generation error: {e}")
            return ["استشارة أخصائي السلوك للحصول على توجيه مخصص"]
