"""
Reporting Domain Models
Core reporting models and value objects
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


class UrgencyLevel(Enum):
    """Urgency levels for recommendations"""

    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class ReportPeriod:
    """Value object representing a report period"""

    start_date: datetime
    end_date: datetime

    def duration_days(self) -> int:
        """Calculate duration in days"""
        return (self.end_date - self.start_date).days

    def is_valid(self) -> bool:
        """Validate period"""
        return self.start_date < self.end_date


@dataclass
class EmotionDistribution:
    """Value object for emotion distribution analysis"""

    emotions: Dict[str, float]
    dominant_emotion: str
    stability_score: float

    def get_emotion_percentage(self, emotion: str) -> float:
        """Get percentage for specific emotion"""
        return self.emotions.get(emotion, 0.0)

    def is_stable(self, threshold: float = 0.7) -> bool:
        """Check if emotions are stable"""
        return self.stability_score >= threshold


@dataclass
class SkillAnalysis:
    """Value object for skill analysis"""

    skills_practiced: Dict[str, int]
    new_skills_learned: List[str]
    improvement_areas: List[str]
    mastery_level: Dict[str, float]

    def get_total_practice_sessions(self) -> int:
        """Get total practice sessions"""
        return sum(self.skills_practiced.values())

    def get_most_practiced_skill(self) -> Optional[str]:
        """Get most practiced skill"""
        if not self.skills_practiced:
            return None
        return max(self.skills_practiced.items(), key=lambda x: x[1])[0]


@dataclass
class InteractionAnalysis:
    """Analysis of a single interaction"""

    timestamp: datetime
    duration: int  # seconds
    primary_emotion: str
    emotions: Dict[str, float]
    topics_discussed: List[str]
    skills_used: List[str]
    behavioral_indicators: List[str]
    quality_score: float  # 0-1

    def is_high_quality(self, threshold: float = 0.7) -> bool:
        """Check if interaction is high quality"""
        return self.quality_score >= threshold

    def duration_minutes(self) -> float:
        """Get duration in minutes"""
        return self.duration / 60.0

    def has_skill(self, skill: str) -> bool:
        """Check if specific skill was used"""
        return skill in self.skills_used


@dataclass
class ProgressMetrics:
    """Child progress metrics for analysis"""

    child_id: int
    analysis_date: datetime
    total_unique_words: int
    new_words_this_period: List[str]
    vocabulary_complexity_score: float
    emotional_intelligence_score: float
    cognitive_development_score: float
    developmental_concerns: List[str]
    intervention_recommendations: List[str]
    urgency_level: UrgencyLevel

    def has_concerns(self) -> bool:
        """Check if there are developmental concerns"""
        return len(self.developmental_concerns) > 0

    def needs_intervention(self) -> bool:
        """Check if intervention is needed"""
        return self.urgency_level in [UrgencyLevel.HIGH, UrgencyLevel.CRITICAL]

    def get_overall_score(self) -> float:
        """Calculate overall development score"""
        return (
            self.vocabulary_complexity_score
            + self.emotional_intelligence_score
            + self.cognitive_development_score
        ) / 3.0


@dataclass
class ChildProgress:
    """Comprehensive child progress report"""

    child_id: str
    child_name: str
    age: int
    period: ReportPeriod

    # Interaction metrics
    total_interactions: int
    avg_daily_interactions: float
    longest_conversation: int  # minutes
    favorite_topics: List[str]

    # Emotional analysis
    emotion_analysis: EmotionDistribution
    mood_trends: Dict[str, List[float]]  # daily mood scores

    # Behavioral metrics
    attention_span: float  # average minutes focused
    response_time: float  # average seconds to respond
    vocabulary_growth: int  # new words learned
    question_frequency: float  # questions per conversation

    # Learning analysis
    skill_analysis: SkillAnalysis
    learning_achievements: List[str]
    recommended_activities: List[str]

    # Social metrics
    empathy_indicators: int
    sharing_behavior: int
    cooperation_level: float

    # Sleep/routine (if available)
    sleep_pattern_quality: Optional[float]
    bedtime_conversations: int

    # Red flags (if any)
    concerning_patterns: List[str]
    urgent_recommendations: List[str]

    def get_engagement_level(self) -> str:
        """Calculate child engagement level"""
        if self.avg_daily_interactions >= 5:
            return "High"
        elif self.avg_daily_interactions >= 2:
            return "Medium"
        else:
            return "Low"

    def has_red_flags(self) -> bool:
        """Check if there are concerning patterns"""
        return len(self.concerning_patterns) > 0 or len(self.urgent_recommendations) > 0

    def get_development_summary(self) -> Dict[str, str]:
        """Get development summary by area"""
        return {
            "emotional": self.emotion_analysis.dominant_emotion,
            "social": "High" if self.empathy_indicators > 5 else "Medium",
            "cognitive": "Developing" if self.vocabulary_growth > 0 else "Stable",
            "attention": "Good" if self.attention_span > 5 else "Needs Improvement",
        }

    def calculate_overall_progress_score(self) -> float:
        """Calculate overall progress score (0-100)"""
        # Weighted scoring system
        interaction_score = min(self.avg_daily_interactions / 5 * 25, 25)
        emotion_score = self.emotion_analysis.stability_score * 25
        attention_score = min(self.attention_span / 10 * 25, 25)
        social_score = min(
            (self.empathy_indicators + self.sharing_behavior) / 20 * 25, 25
        )

        return interaction_score + emotion_score + attention_score + social_score
