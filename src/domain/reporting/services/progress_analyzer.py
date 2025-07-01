"""
Progress Analysis Domain Service
Analyzes child development progress and metrics
"""

import logging
from collections import Counter
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ..models.report_models import (
    ChildProgress,
    EmotionDistribution,
    InteractionAnalysis,
    ProgressMetrics,
    SkillAnalysis,
    UrgencyLevel,
)


class ProgressAnalyzer:
    """Domain service for analyzing child progress"""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def calculate_longest_conversation(self, interactions: List[InteractionAnalysis]) -> int:
        """Calculate longest conversation in minutes"""
        if not interactions:
            return 0

        max_duration = max(interaction.duration for interaction in interactions)
        return int(max_duration / 60)

    def extract_favorite_topics(self, interactions: List[InteractionAnalysis]) -> List[str]:
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

    def analyze_emotion_distribution(self, interactions: List[InteractionAnalysis]) -> EmotionDistribution:
        """Analyze emotion distribution across interactions"""
        try:
            if not interactions:
                return EmotionDistribution(emotions={}, dominant_emotion="neutral", stability_score=0.0)

            # Aggregate emotions
            emotion_totals = {}
            for interaction in interactions:
                for emotion, score in interaction.emotions.items():
                    emotion_totals[emotion] = emotion_totals.get(emotion, 0) + score

            # Calculate percentages
            total_score = sum(emotion_totals.values())
            if total_score == 0:
                emotion_percentages = {}
            else:
                emotion_percentages = {emotion: score / total_score for emotion, score in emotion_totals.items()}

            # Find dominant emotion
            dominant_emotion = (
                max(emotion_percentages.items(), key=lambda x: x[1])[0] if emotion_percentages else "neutral"
            )

            # Calculate stability (inverse of variance)
            stability_score = self._calculate_emotion_stability(interactions)

            return EmotionDistribution(
                emotions=emotion_percentages, dominant_emotion=dominant_emotion, stability_score=stability_score
            )

        except Exception as e:
            self.logger.error(f"Emotion analysis error: {e}")
            return EmotionDistribution(emotions={}, dominant_emotion="neutral", stability_score=0.0)

    def _calculate_emotion_stability(self, interactions: List[InteractionAnalysis]) -> float:
        """Calculate emotional stability score"""
        try:
            if len(interactions) < 2:
                return 1.0

            # Get primary emotions for each interaction
            primary_emotions = [interaction.primary_emotion for interaction in interactions]

            # Calculate how often the emotion changes
            changes = sum(1 for i in range(1, len(primary_emotions)) if primary_emotions[i] != primary_emotions[i - 1])

            # Stability = 1 - (change_rate)
            change_rate = changes / (len(primary_emotions) - 1) if len(primary_emotions) > 1 else 0
            stability = max(0.0, 1.0 - change_rate)

            return min(1.0, stability)

        except Exception as e:
            self.logger.error(f"Stability calculation error: {e}")
            return 0.5

    def analyze_mood_trends(
        self, interactions: List[InteractionAnalysis], start_date: datetime, end_date: datetime
    ) -> Dict[str, List[float]]:
        """Analyze mood trends over time"""
        try:
            # Create daily buckets
            total_days = (end_date - start_date).days + 1
            days = [(start_date + timedelta(days=i)).date() for i in range(total_days)]

            # Initialize mood trends
            mood_trends = {}

            # Group interactions by day
            daily_interactions = {day: [] for day in days}
            for interaction in interactions:
                day = interaction.timestamp.date()
                if day in daily_interactions:
                    daily_interactions[day].append(interaction)

            # Calculate daily mood averages
            all_emotions = set()
            for interaction in interactions:
                all_emotions.update(interaction.emotions.keys())

            for emotion in all_emotions:
                daily_scores = []
                for day in days:
                    day_interactions = daily_interactions[day]
                    if day_interactions:
                        day_emotion_scores = [
                            interaction.emotions.get(emotion, 0.0) for interaction in day_interactions
                        ]
                        avg_score = sum(day_emotion_scores) / len(day_emotion_scores)
                    else:
                        avg_score = 0.0
                    daily_scores.append(avg_score)

                mood_trends[emotion] = daily_scores

            return mood_trends

        except Exception as e:
            self.logger.error(f"Mood trends analysis error: {e}")
            return {}

    def calculate_attention_span(self, interactions: List[InteractionAnalysis]) -> float:
        """Calculate average attention span in minutes"""
        try:
            if not interactions:
                return 0.0

            durations = [interaction.duration_minutes() for interaction in interactions]
            return sum(durations) / len(durations)

        except Exception as e:
            self.logger.error(f"Attention span calculation error: {e}")
            return 0.0

    def calculate_response_time(self, interactions: List[InteractionAnalysis]) -> float:
        """Calculate average response time (placeholder implementation)"""
        try:
            # In a real implementation, this would analyze actual response times
            # For now, estimate based on interaction quality
            if not interactions:
                return 0.0

            quality_scores = [interaction.quality_score for interaction in interactions]
            avg_quality = sum(quality_scores) / len(quality_scores)

            # Higher quality = faster response (inverse relationship)
            estimated_response_time = max(1.0, 10.0 - (avg_quality * 8.0))
            return estimated_response_time

        except Exception as e:
            self.logger.error(f"Response time calculation error: {e}")
            return 5.0

    def estimate_vocabulary_growth(self, interactions: List[InteractionAnalysis]) -> int:
        """Estimate vocabulary growth (placeholder implementation)"""
        try:
            # In a real implementation, this would analyze actual vocabulary usage
            # For now, estimate based on interaction count and quality
            if not interactions:
                return 0

            high_quality_interactions = [interaction for interaction in interactions if interaction.is_high_quality()]

            # Estimate 1-2 new words per high-quality interaction
            estimated_growth = len(high_quality_interactions) * 1.5
            return int(estimated_growth)

        except Exception as e:
            self.logger.error(f"Vocabulary growth estimation error: {e}")
            return 0

    def calculate_question_frequency(self, interactions: List[InteractionAnalysis]) -> float:
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
                estimated_questions = topic_count * duration_factor * 0.5
                total_questions += estimated_questions

            return total_questions / len(interactions)

        except Exception as e:
            self.logger.error(f"Question frequency calculation error: {e}")
            return 0.0

    def analyze_skills_practiced(self, interactions: List[InteractionAnalysis]) -> SkillAnalysis:
        """Analyze skills practiced during interactions"""
        try:
            if not interactions:
                return SkillAnalysis(skills_practiced={}, new_skills_learned=[], improvement_areas=[], mastery_level={})

            # Count skill usage
            skill_counts = {}
            all_skills = set()

            for interaction in interactions:
                for skill in interaction.skills_used:
                    skill_counts[skill] = skill_counts.get(skill, 0) + 1
                    all_skills.add(skill)

            # Identify new skills (skills used less frequently)
            new_skills = [skill for skill, count in skill_counts.items() if count <= 2]  # Used 2 times or less

            # Identify improvement areas (skills used infrequently)
            improvement_areas = [
                skill for skill, count in skill_counts.items() if count <= 3 and skill not in new_skills
            ]

            # Calculate mastery levels
            max_count = max(skill_counts.values()) if skill_counts else 1
            mastery_level = {skill: min(count / max_count, 1.0) for skill, count in skill_counts.items()}

            return SkillAnalysis(
                skills_practiced=skill_counts,
                new_skills_learned=new_skills,
                improvement_areas=improvement_areas,
                mastery_level=mastery_level,
            )

        except Exception as e:
            self.logger.error(f"Skills analysis error: {e}")
            return SkillAnalysis(skills_practiced={}, new_skills_learned=[], improvement_areas=[], mastery_level={})

    def identify_achievements(self, interactions: List[InteractionAnalysis]) -> List[str]:
        """Identify learning achievements"""
        try:
            achievements = []

            if not interactions:
                return achievements

            # High engagement achievement
            if len(interactions) >= 10:
                achievements.append("تفاعل ممتاز - أكثر من 10 محادثات")

            # Long conversation achievement
            longest = self.calculate_longest_conversation(interactions)
            if longest >= 10:
                achievements.append(f"تركيز رائع - محادثة استمرت {longest} دقيقة")

            # Diverse topics achievement
            all_topics = []
            for interaction in interactions:
                all_topics.extend(interaction.topics_discussed)
            unique_topics = len(set(all_topics))
            if unique_topics >= 8:
                achievements.append(f"فضول متنوع - ناقش {unique_topics} مواضيع مختلفة")

            # High quality interactions achievement
            high_quality_count = sum(1 for interaction in interactions if interaction.is_high_quality())
            if high_quality_count >= len(interactions) * 0.7:
                achievements.append("جودة تفاعل عالية - أكثر من 70% محادثات ممتازة")

            return achievements

        except Exception as e:
            self.logger.error(f"Achievement identification error: {e}")
            return []

    def identify_improvement_areas(self, interactions: List[InteractionAnalysis]) -> List[str]:
        """Identify areas needing improvement"""
        try:
            improvement_areas = []

            if not interactions:
                return ["لا توجد بيانات كافية للتحليل"]

            # Low interaction count
            if len(interactions) < 3:
                improvement_areas.append("زيادة تكرار التفاعلات")

            # Short conversations
            avg_duration = sum(interaction.duration for interaction in interactions) / len(interactions)
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
            high_quality_count = sum(1 for interaction in interactions if interaction.is_high_quality())
            if high_quality_count < len(interactions) * 0.5:
                improvement_areas.append("تحسين جودة التفاعل والمشاركة")

            # Emotional instability
            emotion_analysis = self.analyze_emotion_distribution(interactions)
            if not emotion_analysis.is_stable():
                improvement_areas.append("دعم الاستقرار العاطفي")

            return improvement_areas

        except Exception as e:
            self.logger.error(f"Improvement areas identification error: {e}")
            return ["خطأ في تحليل البيانات"]
