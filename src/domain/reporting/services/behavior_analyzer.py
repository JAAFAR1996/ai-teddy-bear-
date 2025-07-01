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

    def identify_improvement_areas(
        self, interactions: List[InteractionAnalysis]
    ) -> List[str]:
        """Identify behavioral areas needing improvement"""
        try:
            improvement_areas = []

            if not interactions:
                return ["لا توجد بيانات كافية للتحليل"]

            # Low interaction count
            if len(interactions) < 3:
                improvement_areas.append("زيادة تكرار التفاعلات")

            # Short conversations
            avg_duration = sum(
                interaction.duration for interaction in interactions
            ) / len(interactions)
            if avg_duration < 120:  # Less than 2 minutes
                improvement_areas.append("تطوير مدة التفاعل والتركيز")

            # Limited topics
            all_topics = []
            for interaction in interactions:
                all_topics.extend(interaction.topics_discussed)
            unique_topics = len(set(all_topics))
            if unique_topics < 5:
                improvement_areas.append("توسيع المواضيع المناقشة")

            # Low quality interactions
            high_quality_count = sum(
                1 for interaction in interactions if interaction.is_high_quality()
            )
            if high_quality_count < len(interactions) * 0.5:
                improvement_areas.append("تحسين جودة التفاعل والمشاركة")

            # Check for behavioral indicators
            all_indicators = []
            for interaction in interactions:
                all_indicators.extend(interaction.behavioral_indicators)

            # Look for concerning behavioral patterns
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

            concerning_count = sum(
                1
                for indicator in all_indicators
                if any(
                    negative in indicator.lower() for negative in negative_indicators
                )
            )

            if concerning_count > len(interactions) * 0.3:
                improvement_areas.append("تطوير مهارات التنظيم الذاتي")

            # Check attention span
            attention_span = self._calculate_attention_span(interactions)
            if attention_span < 3:  # Less than 3 minutes average
                improvement_areas.append("تحسين فترة التركيز والانتباه")

            # Check social engagement
            social_skills_used = sum(
                1
                for interaction in interactions
                if "social_skills" in interaction.skills_used
            )

            if social_skills_used < len(interactions) * 0.2:
                improvement_areas.append("تطوير المهارات الاجتماعية")

            return improvement_areas

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

            durations = [interaction.duration_minutes() for interaction in interactions]
            return mean(durations)

        except Exception as e:
            self.logger.error(f"Attention span calculation error: {e}")
            return 0.0

    def analyze_behavioral_patterns(
        self, interactions: List[InteractionAnalysis]
    ) -> Dict[str, Any]:
        """Analyze overall behavioral patterns"""
        try:
            patterns = {
                "engagement_level": "low",
                "attention_consistency": "variable",
                "social_responsiveness": "developing",
                "emotional_regulation": "stable",
                "cooperation_level": "medium",
                "behavioral_concerns": [],
            }

            if not interactions:
                return patterns

            # Analyze engagement level
            avg_quality = mean(
                interaction.quality_score for interaction in interactions
            )
            if avg_quality >= 0.8:
                patterns["engagement_level"] = "high"
            elif avg_quality >= 0.6:
                patterns["engagement_level"] = "medium"
            else:
                patterns["engagement_level"] = "low"

            # Analyze attention consistency
            durations = [interaction.duration_minutes() for interaction in interactions]
            if durations:
                duration_variance = self._calculate_variance(durations)
                if duration_variance < 2:
                    patterns["attention_consistency"] = "consistent"
                elif duration_variance < 5:
                    patterns["attention_consistency"] = "moderate"
                else:
                    patterns["attention_consistency"] = "variable"

            # Analyze social responsiveness
            social_indicators = 0
            for interaction in interactions:
                if "social_skills" in interaction.skills_used:
                    social_indicators += 1
                if any(
                    "social" in topic.lower() for topic in interaction.topics_discussed
                ):
                    social_indicators += 1

            social_rate = social_indicators / len(interactions)
            if social_rate >= 0.6:
                patterns["social_responsiveness"] = "excellent"
            elif social_rate >= 0.4:
                patterns["social_responsiveness"] = "good"
            elif social_rate >= 0.2:
                patterns["social_responsiveness"] = "developing"
            else:
                patterns["social_responsiveness"] = "needs_attention"

            # Analyze emotional regulation
            emotion_changes = 0
            for i in range(1, len(interactions)):
                if (
                    interactions[i].primary_emotion
                    != interactions[i - 1].primary_emotion
                ):
                    emotion_changes += 1

            if len(interactions) > 1:
                change_rate = emotion_changes / (len(interactions) - 1)
                if change_rate < 0.3:
                    patterns["emotional_regulation"] = "excellent"
                elif change_rate < 0.6:
                    patterns["emotional_regulation"] = "stable"
                else:
                    patterns["emotional_regulation"] = "needs_support"

            # Analyze cooperation level
            cooperation_score = self._calculate_cooperation_score(interactions)
            if cooperation_score >= 0.8:
                patterns["cooperation_level"] = "excellent"
            elif cooperation_score >= 0.6:
                patterns["cooperation_level"] = "good"
            elif cooperation_score >= 0.4:
                patterns["cooperation_level"] = "medium"
            else:
                patterns["cooperation_level"] = "needs_improvement"

            # Identify behavioral concerns
            patterns["behavioral_concerns"] = self._identify_behavioral_concerns(
                interactions
            )

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

    def _identify_behavioral_concerns(
        self, interactions: List[InteractionAnalysis]
    ) -> List[str]:
        """Identify specific behavioral concerns"""
        try:
            concerns = []

            # Check for attention issues
            avg_duration = mean(
                interaction.duration_minutes() for interaction in interactions
            )
            if avg_duration < 2:
                concerns.append("صعوبة في التركيز لفترات طويلة")

            # Check for social withdrawal
            social_engagement = sum(
                1
                for interaction in interactions
                if len(interaction.topics_discussed) >= 2
            )

            if social_engagement < len(interactions) * 0.5:
                concerns.append("انخفاض في التفاعل الاجتماعي")

            # Check for emotional instability
            negative_emotions = ["sad", "angry", "scared"]
            negative_count = sum(
                1
                for interaction in interactions
                if interaction.primary_emotion in negative_emotions
            )

            if negative_count > len(interactions) * 0.4:
                concerns.append("تكرار المشاعر السلبية")

            # Check for quality issues
            low_quality_count = sum(
                1 for interaction in interactions if interaction.quality_score < 0.4
            )

            if low_quality_count > len(interactions) * 0.5:
                concerns.append("انخفاض جودة التفاعل")

            return concerns

        except Exception as e:
            self.logger.error(f"Behavioral concerns identification error: {e}")
            return []

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
                    recommendations.append("استخدام نظام مكافآت للسلوك الإيجابي")

            return list(set(recommendations))  # Remove duplicates

        except Exception as e:
            self.logger.error(f"Behavioral recommendations generation error: {e}")
            return ["استشارة أخصائي السلوك للحصول على توجيه مخصص"]
