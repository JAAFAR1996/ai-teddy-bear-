"""
Recommendation Domain Models
Models for various types of recommendations and interventions
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List

from .report_models import UrgencyLevel


class RecommendationType(Enum):
    """Types of recommendations"""

    ACTIVITY = "activity"
    INTERVENTION = "intervention"
    EDUCATIONAL = "educational"
    SOCIAL = "social"
    EMOTIONAL = "emotional"
    BEHAVIORAL = "behavioral"


class ImplementationDifficulty(Enum):
    """Implementation difficulty levels"""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


@dataclass
class ActivityRecommendation:
    """Recommendation for specific activities"""

    activity_name: str
    description: str
    target_skills: List[str]
    age_appropriate: bool
    duration_minutes: int
    required_materials: List[str]
    implementation_difficulty: ImplementationDifficulty
    expected_outcomes: List[str]

    def is_suitable_for_age(self, age: int) -> bool:
        """Check if activity is suitable for child's age"""
        return self.age_appropriate

    def get_skill_count(self) -> int:
        """Get number of target skills"""
        return len(self.target_skills)


@dataclass
class InterventionRecommendation:
    """Recommendation for interventions"""

    concern_area: str
    intervention_type: str
    description: str
    implementation_steps: List[str]
    urgency_level: UrgencyLevel
    expected_duration_weeks: int
    success_indicators: List[str]
    professional_help_needed: bool

    def is_urgent(self) -> bool:
        """Check if intervention is urgent"""
        return self.urgency_level in [UrgencyLevel.HIGH, UrgencyLevel.CRITICAL]

    def requires_professional(self) -> bool:
        """Check if professional help is needed"""
        return self.professional_help_needed


@dataclass
class LLMRecommendation:
    """AI-generated recommendation with reasoning"""

    category: str
    recommendation: str
    reasoning: str
    implementation_steps: List[str]
    priority_level: int
    confidence_score: float
    generated_at: datetime

    def is_high_confidence(self, threshold: float = 0.8) -> bool:
        """Check if recommendation has high confidence"""
        return self.confidence_score >= threshold

    def is_high_priority(self) -> bool:
        """Check if recommendation is high priority"""
        return self.priority_level >= 4

    def get_step_count(self) -> int:
        """Get number of implementation steps"""
        return len(self.implementation_steps)


@dataclass
class RecommendationBundle:
    """Bundle of related recommendations"""

    bundle_id: str
    title: str
    description: str
    activity_recommendations: List[ActivityRecommendation]
    intervention_recommendations: List[InterventionRecommendation]
    llm_recommendations: List[LLMRecommendation]
    created_at: datetime

    def get_total_recommendations(self) -> int:
        """Get total number of recommendations"""
        return (
            len(self.activity_recommendations)
            + len(self.intervention_recommendations)
            + len(self.llm_recommendations)
        )

    def get_urgent_interventions(self) -> List[InterventionRecommendation]:
        """Get urgent intervention recommendations"""
        return [
            intervention
            for intervention in self.intervention_recommendations
            if intervention.is_urgent()
        ]

    def get_high_priority_llm_recommendations(self) -> List[LLMRecommendation]:
        """Get high priority LLM recommendations"""
        return [rec for rec in self.llm_recommendations if rec.is_high_priority()]

    def has_urgent_items(self) -> bool:
        """Check if bundle has urgent items"""
        return len(self.get_urgent_interventions()) > 0
