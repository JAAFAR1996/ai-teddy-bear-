"""
Progress Analysis Domain Service
Analyzes child development progress and metrics
"""

import logging
from collections import Counter
from datetime import datetime, timedelta
from typing import Dict, List, Any

from ..models.report_models import (
    EmotionDistribution,
    InteractionAnalysis,
    SkillAnalysis,
)


class ProgressAnalyzer:
    """Domain service for analyzing child progress"""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def calculate_longest_conversation(
        self, interactions: List[InteractionAnalysis]
    ) -> int:
        """Calculate longest conversation in minutes"""
        if not interactions:
            return 0

        max_duration = max(
            interaction.duration for interaction in interactions)
        return int(max_duration / 60)

    def extract_favorite_topics(
        self, interactions: List[InteractionAnalysis]
    ) -> List[str]:
        """Extract most frequently discussed topics"""
        try:
            all_topics = []
            for interaction in interactions:
                all_topics.extend(interaction.topics_discussed)

            topic_counts = Counter(all_topics)
            # Return top 5 topics
            return [topic for topic, _ in topic_counts.most_common(5)]

        except Exception as e:
            self.logger.error(f"Topic extraction error: {e}")
            return []

    def analyze_emotion_distribution(
        self, interactions: List[InteractionAnalysis]
    ) -> EmotionDistribution:
        """Analyze emotion distribution across interactions"""
        try:
            if not interactions:
                return EmotionDistribution(
                    emotions={},
                    dominant_emotion="neutral",
                    stability_score=0.0)

            # Aggregate emotions
            emotion_totals = {}
            for interaction in interactions:
                for emotion, score in interaction.emotions.items():
                    emotion_totals[emotion] = emotion_totals.get(
                        emotion, 0) + score

            # Calculate percentages
            total_score = sum(emotion_totals.values())
            if total_score == 0:
                emotion_percentages = {}
            else:
                emotion_percentages = {
                    emotion: score / total_score
                    for emotion, score in emotion_totals.items()
                }

            # Find dominant emotion
            dominant_emotion = (
                max(emotion_percentages.items(), key=lambda x: x[1])[0]
                if emotion_percentages
                else "neutral"
            )

            # Calculate stability (inverse of variance)
            stability_score = self._calculate_emotion_stability(interactions)

            return EmotionDistribution(
                emotions=emotion_percentages,
                dominant_emotion=dominant_emotion,
                stability_score=stability_score,
            )

        except Exception as e:
            self.logger.error(f"Emotion analysis error: {e}")
            return EmotionDistribution(
                emotions={}, dominant_emotion="neutral", stability_score=0.0
            )

    def _calculate_emotion_stability(
        self, interactions: List[InteractionAnalysis]
    ) -> float:
        """Calculate emotional stability score"""
        try:
            if len(interactions) < 2:
                return 1.0

            # Get primary emotions for each interaction
            primary_emotions = [
                interaction.primary_emotion for interaction in interactions
            ]

            # Calculate how often the emotion changes
            changes = sum(
                1
                for i in range(1, len(primary_emotions))
                if primary_emotions[i] != primary_emotions[i - 1]
            )

            # Stability = 1 - (change_rate)
            change_rate = (
                changes / (len(primary_emotions) - 1)
                if len(primary_emotions) > 1
                else 0
            )
            stability = max(0.0, 1.0 - change_rate)

            return min(1.0, stability)

        except Exception as e:
            self.logger.error(f"Stability calculation error: {e}")
            return 0.5

    def _group_interactions_by_day(
        self,
        interactions: List[InteractionAnalysis],
        start_date: datetime,
        end_date: datetime,
    ) -> Dict[datetime.date, List[InteractionAnalysis]]:
        """Groups interactions into daily buckets."""
        total_days = (end_date - start_date).days + 1
        days = [(start_date + timedelta(days=i)).date()
                for i in range(total_days)]

        daily_interactions = {day: [] for day in days}
        for interaction in interactions:
            day = interaction.timestamp.date()
            if day in daily_interactions:
                daily_interactions[day].append(interaction)
        return daily_interactions

    def _get_all_emotions(
            self,
            interactions: List[InteractionAnalysis]) -> set:
        """Gets a unique set of all emotions from interactions."""
        return set(
            emotion
            for interaction in interactions
            for emotion in interaction.emotions.keys()
        )

    def _calculate_daily_emotion_scores(
        self,
        daily_interactions: Dict[datetime.date, List[InteractionAnalysis]],
        emotion: str,
    ) -> List[float]:
        """Calculates the average daily score for a specific emotion."""
        daily_scores = []
        for day_interactions in daily_interactions.values():
            if day_interactions:
                day_emotion_scores = [
                    interaction.emotions.get(emotion, 0.0)
                    for interaction in day_interactions
                ]
                avg_score = sum(day_emotion_scores) / len(day_emotion_scores)
            else:
                avg_score = 0.0
            daily_scores.append(avg_score)
        return daily_scores

    def analyze_mood_trends(
        self,
        interactions: List[InteractionAnalysis],
        start_date: datetime,
        end_date: datetime,
    ) -> Dict[str, List[float]]:
        """Analyze mood trends over time"""
        try:
            if not interactions:
                return {}

            daily_interactions = self._group_interactions_by_day(
                interactions, start_date, end_date
            )
            all_emotions = self._get_all_emotions(interactions)

            mood_trends = {}
            for emotion in all_emotions:
                mood_trends[emotion] = self._calculate_daily_emotion_scores(
                    daily_interactions, emotion
                )

            return mood_trends

        except Exception as e:
            self.logger.error(f"Mood trends analysis error: {e}")
            return {}

    def calculate_attention_span(
        self, interactions: List[InteractionAnalysis]
    ) -> float:
        """Calculate average attention span in minutes"""
        try:
            if not interactions:
                return 0.0

            durations = [interaction.duration_minutes()
                         for interaction in interactions]
            return sum(durations) / len(durations)

        except Exception as e:
            self.logger.error(f"Attention span calculation error: {e}")
            return 0.0

    def calculate_response_time(
            self, interactions: List[InteractionAnalysis]) -> float:
        """Calculate average response time (placeholder implementation)"""
        try:
            # In a real implementation, this would analyze actual response times
            # For now, estimate based on interaction quality
            if not interactions:
                return 0.0

            quality_scores = [
                interaction.quality_score for interaction in interactions]
            avg_quality = sum(quality_scores) / len(quality_scores)

            # Higher quality = faster response (inverse relationship)
            estimated_response_time = max(1.0, 10.0 - (avg_quality * 8.0))
            return estimated_response_time

        except Exception as e:
            self.logger.error(f"Response time calculation error: {e}")
            return 5.0

    def estimate_vocabulary_growth(
        self, interactions: List[InteractionAnalysis]
    ) -> int:
        """Estimate vocabulary growth (placeholder implementation)"""
        try:
            # In a real implementation, this would analyze actual vocabulary usage
            # For now, estimate based on interaction count and quality
            if not interactions:
                return 0

            high_quality_interactions = [
                interaction
                for interaction in interactions
                if interaction.is_high_quality()
            ]

            # Estimate 1-2 new words per high-quality interaction
            estimated_growth = len(high_quality_interactions) * 1.5
            return int(estimated_growth)

        except Exception as e:
            self.logger.error(f"Vocabulary growth estimation error: {e}")
            return 0

    def calculate_question_frequency(
        self, interactions: List[InteractionAnalysis]
    ) -> float:
        """Calculate questions per conversation"""
        try:
            if not interactions:
                return 0.0

            # Estimate based on topic diversity and interaction quality
            total_questions = 0
            for interaction in interactions:
                # Estimate questions based on topics discussed and duration
                topic_count = len(interaction.topics_discussed)
                duration_factor = min(interaction.duration_minutes() / 5, 3.0)
                quality_factor = interaction.quality_score

                estimated_questions = topic_count * duration_factor * quality_factor
                total_questions += estimated_questions

            return total_questions / len(interactions)

        except Exception as e:
            self.logger.error(f"Question frequency calculation error: {e}")
            return 0.0

    def _get_all_skills_and_proficiencies(
        self, interactions: List[InteractionAnalysis]
    ) -> Dict[str, List[float]]:
        """Aggregates all skills and their proficiency scores from interactions."""
        skill_proficiencies = {}
        for interaction in interactions:
            for skill, proficiency in interaction.skills_used.items():
                if skill not in skill_proficiencies:
                    skill_proficiencies[skill] = []
                skill_proficiencies[skill].append(proficiency)
        return skill_proficiencies

    def _calculate_skill_usage(
        self, skill_proficiencies: Dict[str, List[float]]
    ) -> Dict[str, int]:
        """Calculates the usage count for each skill."""
        return {
            skill: len(proficiencies)
            for skill, proficiencies in skill_proficiencies.items()
        }

    def _calculate_skill_proficiency(
        self, skill_proficiencies: Dict[str, List[float]]
    ) -> Dict[str, float]:
        """Calculates the average proficiency for each skill."""
        skill_proficiency = {}
        for skill, proficiencies in skill_proficiencies.items():
            if proficiencies:
                skill_proficiency[skill] = sum(
                    proficiencies) / len(proficiencies)
        return skill_proficiency

    def _calculate_skill_trends(
        self, skill_proficiencies: Dict[str, List[float]]
    ) -> Dict[str, str]:
        """Analyzes the trend for each skill."""
        skill_trends = {}
        for skill, proficiencies in skill_proficiencies.items():
            if len(proficiencies) > 2:
                # Simplified trend: compare first half to second half
                mid_point = len(proficiencies) // 2
                first_half_avg = sum(proficiencies[:mid_point]) / mid_point
                second_half_avg = sum(proficiencies[mid_point:]) / (
                    len(proficiencies) - mid_point
                )
                if second_half_avg > first_half_avg + 0.1:
                    skill_trends[skill] = "improving"
                elif second_half_avg < first_half_avg - 0.1:
                    skill_trends[skill] = "declining"
                else:
                    skill_trends[skill] = "stable"
            else:
                skill_trends[skill] = "stable"
        return skill_trends

    def analyze_skills_practiced(
        self, interactions: List[InteractionAnalysis]
    ) -> SkillAnalysis:
        """Analyze skills practiced and their trends"""
        try:
            if not interactions:
                return SkillAnalysis(usage={}, proficiency={}, trends={})

            skill_proficiencies = self._get_all_skills_and_proficiencies(
                interactions)

            usage = self._calculate_skill_usage(skill_proficiencies)
            proficiency = self._calculate_skill_proficiency(
                skill_proficiencies)
            trends = self._calculate_skill_trends(skill_proficiencies)

            return SkillAnalysis(
                usage=usage,
                proficiency=proficiency,
                trends=trends,
            )
        except Exception as e:
            self.logger.error(f"Skill analysis error: {e}")
            return SkillAnalysis(usage={}, proficiency={}, trends={})

    def _aggregate_interaction_data(self, interactions: List[InteractionAnalysis]) -> Dict[str, Any]:
        """Aggregate data from interactions for achievement checks."""
        if not interactions:
            return {}

        total_duration_minutes = sum(i.duration_minutes()
                                     for i in interactions)
        avg_quality = sum(
            i.quality_score for i in interactions) / len(interactions)
        all_topics = {
            topic for i in interactions for topic in i.topics_discussed}
        all_skills = {
            skill for i in interactions for skill in i.skills_used.keys()}

        return {
            "total_duration_minutes": total_duration_minutes,
            "avg_quality": avg_quality,
            "topic_count": len(all_topics),
            "skill_count": len(all_skills),
        }

    def _check_milestone_achievements(self, aggregated_data: Dict[str, Any]) -> List[str]:
        """Check for milestone-based achievements."""
        achievements = []
        if aggregated_data.get("total_duration_minutes", 0) > 100:
            achievements.append("تجاوز 100 دقيقة من المحادثات")
        if aggregated_data.get("avg_quality", 0) > 0.8:
            achievements.append("مستوى تفاعل عالي")
        if aggregated_data.get("topic_count", 0) > 10:
            achievements.append("مستكشف فضولي")
        if aggregated_data.get("skill_count", 0) > 5:
            achievements.append("متعلم متعدد المهارات")
        return achievements

    def _check_performance_achievements(self, interactions: List[InteractionAnalysis]) -> List[str]:
        """Check for performance-based achievements in single interactions."""
        achievements = []
        if any(p > 0.9 for i in interactions for p in i.skills_used.values()):
            achievements.append("إتقان مهارة جديدة")
        if any(i.duration_minutes() > 15 for i in interactions):
            achievements.append("محادثة طويلة ومميزة")
        return achievements

    def identify_achievements(
        self, interactions: List[InteractionAnalysis]
    ) -> List[str]:
        """Identify key achievements from interactions"""
        try:
            if not interactions:
                return []

            aggregated_data = self._aggregate_interaction_data(interactions)

            milestone_achievements = self._check_milestone_achievements(
                aggregated_data)
            performance_achievements = self._check_performance_achievements(
                interactions)

            return milestone_achievements + performance_achievements

        except Exception as e:
            self.logger.error(f"Achievements identification error: {e}")
            return []

    def identify_improvement_areas(
        self, interactions: List[InteractionAnalysis]
    ) -> List[str]:
        """Identify areas for improvement from interactions"""
        try:
            if not interactions:
                return []

            improvement_areas = []

            # Data aggregations
            avg_duration_minutes = sum(
                i.duration_minutes() for i in interactions
            ) / len(interactions)
            avg_quality = sum(
                i.quality_score for i in interactions) / len(interactions)
            emotion_dist = self.analyze_emotion_distribution(interactions)
            skill_analysis = self.analyze_skills_practiced(interactions)

            improvement_checks = [
                ("تطوير مدة التفاعل والتركيز",
                 lambda: avg_duration_minutes < 3),
                ("تحسين جودة الحوار",
                 lambda: avg_quality < 0.6),
                ("تعزيز الاستقرار العاطفي",
                 lambda: emotion_dist.stability_score < 0.5),
                ("توسيع المهارات المستخدمة",
                 lambda: len(
                     skill_analysis.usage) < 4),
                ("زيادة المبادرة في المحادثة",
                    lambda: self.calculate_question_frequency(
                        interactions) < 1.0,
                 ),
            ]

            for area, check in improvement_checks:
                if check():
                    improvement_areas.append(area)

            # Check for declining skill trends
            for skill, trend in skill_analysis.trends.items():
                if trend == "declining":
                    improvement_areas.append(f"مراجعة مهارة: {skill}")

            return list(set(improvement_areas))

        except Exception as e:
            self.logger.error(f"Improvement areas identification error: {e}")
            return []
