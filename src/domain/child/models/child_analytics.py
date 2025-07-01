"""
Child Analytics Domain Models

Contains domain models for child analytics and engagement insights.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


class EngagementLevel(Enum):
    """Child engagement levels"""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INACTIVE = "inactive"


@dataclass
class InteractionMetrics:
    """Child interaction metrics value object"""

    total_interaction_time: int
    daily_average_time: float
    time_utilization_percentage: float
    interaction_streak: int
    days_since_last_interaction: int

    def is_over_utilization_threshold(self, threshold: float = 90.0) -> bool:
        """Check if time utilization exceeds threshold"""
        return self.time_utilization_percentage > threshold

    def is_under_utilization_threshold(self, threshold: float = 30.0) -> bool:
        """Check if time utilization is below threshold"""
        return self.time_utilization_percentage < threshold

    def needs_engagement_reminder(self, days_threshold: int = 3) -> bool:
        """Check if child needs engagement reminder"""
        return self.days_since_last_interaction > days_threshold


@dataclass
class ChildEngagementInsight:
    """Child engagement insight domain entity"""

    child_id: str
    engagement_level: EngagementLevel
    metrics: InteractionMetrics
    recommendations: List[str]
    analysis_timestamp: datetime

    def __post_init__(self):
        """Validate and generate recommendations after initialization"""
        self._validate_metrics()
        self._generate_recommendations()

    def _validate_metrics(self) -> None:
        """Validate interaction metrics"""
        if self.metrics.total_interaction_time < 0:
            raise ValueError("Total interaction time cannot be negative")

        if (
            self.metrics.time_utilization_percentage < 0
            or self.metrics.time_utilization_percentage > 100
        ):
            raise ValueError("Time utilization percentage must be between 0 and 100")

    def _generate_recommendations(self) -> None:
        """Generate personalized recommendations based on metrics"""
        recommendations = []

        if self.metrics.needs_engagement_reminder():
            recommendations.append(
                "Consider sending a gentle reminder to engage with the AI assistant"
            )

        if self.metrics.is_under_utilization_threshold():
            recommendations.append(
                "Child may benefit from shorter, more frequent interactions"
            )
        elif self.metrics.is_over_utilization_threshold():
            recommendations.append("Consider increasing daily interaction time limit")

        if self.engagement_level == EngagementLevel.LOW:
            recommendations.append(
                "Try introducing new topics or activities to boost engagement"
            )

        if self.metrics.interaction_streak == 0:
            recommendations.append("Schedule regular interaction times to build habits")

        self.recommendations.extend(
            [r for r in recommendations if r not in self.recommendations]
        )

    def is_at_risk(self) -> bool:
        """Check if child is at risk of disengagement"""
        return (
            self.engagement_level in [EngagementLevel.LOW, EngagementLevel.INACTIVE]
            or self.metrics.days_since_last_interaction > 7
        )


@dataclass
class AgeStatistics:
    """Age statistics value object"""

    min_age: int
    max_age: int
    average_age: float

    def get_age_range_description(self) -> str:
        """Get human-readable age range description"""
        if self.max_age <= 5:
            return "Preschool"
        elif self.max_age <= 11:
            return "Elementary"
        elif self.max_age <= 14:
            return "Middle School"
        else:
            return "Mixed Ages"


@dataclass
class ActivityStatistics:
    """Activity statistics value object"""

    children_active_last_7_days: int
    activity_percentage: float
    total_children: int

    def is_healthy_activity_rate(self, threshold: float = 70.0) -> bool:
        """Check if activity rate is healthy"""
        return self.activity_percentage >= threshold

    def get_activity_status(self) -> str:
        """Get activity status description"""
        if self.activity_percentage >= 80:
            return "Excellent"
        elif self.activity_percentage >= 60:
            return "Good"
        elif self.activity_percentage >= 40:
            return "Moderate"
        else:
            return "Needs Attention"


@dataclass
class ChildStatistics:
    """Child statistics domain entity"""

    total_children: int
    age_statistics: AgeStatistics
    language_distribution: Dict[str, int]
    activity_statistics: ActivityStatistics
    generated_at: datetime

    def get_dominant_language(self) -> Optional[str]:
        """Get the most common language"""
        if not self.language_distribution:
            return None
        return max(self.language_distribution.items(), key=lambda x: x[1])[0]

    def get_language_diversity_score(self) -> float:
        """Calculate language diversity score (0-1)"""
        if not self.language_distribution or len(self.language_distribution) <= 1:
            return 0.0

        total = sum(self.language_distribution.values())
        if total == 0:
            return 0.0

        # Calculate entropy-based diversity
        entropy = 0.0
        for count in self.language_distribution.values():
            if count > 0:
                p = count / total
                entropy -= p * (p.bit_length() - 1)  # Simplified entropy

        max_entropy = (len(self.language_distribution)).bit_length() - 1
        return entropy / max_entropy if max_entropy > 0 else 0.0

    def get_insights(self) -> List[str]:
        """Generate insights from statistics"""
        insights = []

        if self.total_children == 0:
            insights.append("No active children in the system")
            return insights

        # Age insights
        if self.age_statistics.average_age < 8:
            insights.append("Majority of children are in early development stage")
        elif self.age_statistics.average_age > 12:
            insights.append("Majority of children are in advanced learning stage")

        # Language insights
        dominant_lang = self.get_dominant_language()
        if dominant_lang:
            insights.append(f"Primary language is {dominant_lang}")

        diversity_score = self.get_language_diversity_score()
        if diversity_score > 0.7:
            insights.append("High language diversity - consider multilingual features")

        # Activity insights
        activity_status = self.activity_statistics.get_activity_status()
        insights.append(f"Overall activity level: {activity_status}")

        if not self.activity_statistics.is_healthy_activity_rate():
            insights.append("Consider engagement campaigns to boost activity")

        return insights
