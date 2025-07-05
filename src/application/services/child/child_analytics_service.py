"""
Child Analytics Domain Service

Domain service for child analytics and engagement insights business logic.
"""

import logging
from datetime import datetime
from typing import List

from src.domain.child.models.child_analytics import (
    ActivityStatistics,
    AgeStatistics,
    ChildEngagementInsight,
    ChildStatistics,
    EngagementLevel,
    InteractionMetrics,
)
from src.domain.entities.child import Child


class ChildAnalyticsDomainService:
    """Domain service for child analytics business logic"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def calculate_engagement_insights(
        self, child: Child, total_days_since_creation: int
    ) -> ChildEngagementInsight:
        """
        Calculate comprehensive engagement insights for a child

        Args:
            child: Child entity
            total_days_since_creation: Total days since child profile creation

        Returns:
            ChildEngagementInsight with complete analysis
        """
        # Calculate interaction metrics
        metrics = self._calculate_interaction_metrics(child, total_days_since_creation)

        # Determine engagement level
        engagement_level = self._determine_engagement_level(metrics)

        # Create engagement insight
        insight = ChildEngagementInsight(
            child_id=child.id,
            engagement_level=engagement_level,
            metrics=metrics,
            recommendations=[],  # Will be generated automatically
            analysis_timestamp=datetime.now(),
        )

        return insight

    def _calculate_interaction_metrics(
        self, child: Child, total_days_since_creation: int
    ) -> InteractionMetrics:
        """Calculate interaction metrics for a child"""

        # Calculate days since last interaction
        days_since_last_interaction = 0
        if child.last_interaction:
            days_since_last_interaction = (datetime.now() - child.last_interaction).days
        else:
            days_since_last_interaction = total_days_since_creation

        # Calculate daily average time
        daily_avg_time = child.total_interaction_time / max(
            total_days_since_creation, 1
        )

        # Calculate time utilization percentage
        time_utilization = 0.0
        if child.max_daily_interaction_time > 0:
            time_utilization = (
                child.total_interaction_time / child.max_daily_interaction_time
            ) * 100

        # Calculate interaction streak
        interaction_streak = max(0, 7 - days_since_last_interaction)

        return InteractionMetrics(
            total_interaction_time=child.total_interaction_time,
            daily_average_time=daily_avg_time,
            time_utilization_percentage=min(time_utilization, 100.0),  # Cap at 100%
            interaction_streak=interaction_streak,
            days_since_last_interaction=days_since_last_interaction,
        )

    def _determine_engagement_level(
        self, metrics: InteractionMetrics
    ) -> EngagementLevel:
        """Determine engagement level based on metrics"""

        if metrics.days_since_last_interaction > 14:
            return EngagementLevel.INACTIVE
        elif metrics.days_since_last_interaction > 7:
            return EngagementLevel.LOW
        elif metrics.days_since_last_interaction > 3:
            return EngagementLevel.MEDIUM
        else:
            return EngagementLevel.HIGH

    def calculate_statistics(
        self, children: List[Child], active_children_last_7_days: int
    ) -> ChildStatistics:
        """
        Calculate comprehensive statistics for children

        Args:
            children: List of all children
            active_children_last_7_days: Count of children active in last 7 days

        Returns:
            ChildStatistics with comprehensive analytics
        """
        if not children:
            return self._create_empty_statistics()

        # Calculate all statistics components
        age_stats = self._calculate_age_statistics(children)
        language_distribution = self._calculate_language_distribution(children)
        activity_stats = self._calculate_activity_statistics(
            children, active_children_last_7_days
        )

        return ChildStatistics(
            total_children=len(children),
            age_statistics=age_stats,
            language_distribution=language_distribution,
            activity_statistics=activity_stats,
            generated_at=datetime.now(),
        )

    def _create_empty_statistics(self) -> ChildStatistics:
        """Create empty statistics for when no children are provided."""
        return ChildStatistics(
            total_children=0,
            age_statistics=AgeStatistics(min_age=0, max_age=0, average_age=0.0),
            language_distribution={},
            activity_statistics=ActivityStatistics(
                children_active_last_7_days=0,
                activity_percentage=0.0,
                total_children=0,
            ),
            generated_at=datetime.now(),
        )

    def _calculate_age_statistics(self, children: List[Child]) -> AgeStatistics:
        """Calculate age statistics from children list."""
        ages = [child.age for child in children if child.age is not None]
        return AgeStatistics(
            min_age=min(ages) if ages else 0,
            max_age=max(ages) if ages else 0,
            average_age=sum(ages) / len(ages) if ages else 0.0,
        )

    def _calculate_language_distribution(self, children: List[Child]) -> dict:
        """Calculate language distribution from children list."""
        language_distribution = {}
        for child in children:
            lang = child.language_preference or "unknown"
            language_distribution[lang] = language_distribution.get(lang, 0) + 1
        return language_distribution

    def _calculate_activity_statistics(
        self, children: List[Child], active_children_last_7_days: int
    ) -> ActivityStatistics:
        """Calculate activity statistics from children list."""
        total_children = len(children)
        activity_percentage = (
            (active_children_last_7_days / total_children * 100)
            if total_children > 0
            else 0.0
        )

        return ActivityStatistics(
            children_active_last_7_days=active_children_last_7_days,
            activity_percentage=round(activity_percentage, 1),
            total_children=total_children,
        )

    def identify_at_risk_children(self, children: List[Child]) -> List[Child]:
        """
        Identify children at risk of disengagement

        Args:
            children: List of children to analyze

        Returns:
            List of children identified as at-risk
        """
        at_risk_children = []

        for child in children:
            try:
                total_days = (
                    (datetime.now() - child.created_at).days if child.created_at else 30
                )
                insight = self.calculate_engagement_insights(child, total_days)

                if insight.is_at_risk():
                    at_risk_children.append(child)

            except Exception as e:
                self.logger.warning(f"Failed to analyze child {child.id}: {e}")
                continue

        return at_risk_children

    def generate_engagement_recommendations(
        self, child: Child, metrics: InteractionMetrics
    ) -> List[str]:
        """
        Generate personalized engagement recommendations

        Args:
            child: Child entity
            metrics: Child's interaction metrics

        Returns:
            List of personalized recommendations
        """
        recommendations = []

        # Time-based recommendations
        if metrics.needs_engagement_reminder():
            recommendations.append("Send gentle reminder to engage with AI assistant")

        if metrics.is_under_utilization_threshold():
            recommendations.append(
                "Suggest shorter, more frequent interaction sessions"
            )
        elif metrics.is_over_utilization_threshold():
            recommendations.append("Consider extending daily interaction time limits")

        # Age-based recommendations
        if child.age and child.age < 6:
            recommendations.append("Focus on play-based learning activities")
        elif child.age and child.age > 12:
            recommendations.append("Introduce more complex topics and challenges")

        # Interest-based recommendations
        if child.interests and len(child.interests) < 3:
            recommendations.append("Help child discover new interests and hobbies")

        # Special needs considerations
        if child.special_needs and child.special_needs != []:
            recommendations.append("Ensure interactions are adapted for special needs")

        # Language-based recommendations
        if child.language_preference and child.language_preference != "en":
            recommendations.append(
                f"Provide more {child.language_preference} language content"
            )

        return recommendations

    def calculate_learning_progress_score(self, child: Child) -> float:
        """
        Calculate learning progress score for a child

        Args:
            child: Child entity

        Returns:
            Learning progress score (0.0 to 1.0)
        """
        score = 0.0
        max_score = 5.0

        # Calculate all scoring components
        score += self._calculate_interaction_consistency_score(child)
        score += self._calculate_topic_diversity_score(child)
        score += self._calculate_engagement_level_score(child)
        score += self._calculate_profile_completeness_score(child)
        score += self._calculate_recent_activity_score(child)

        return min(score / max_score, 1.0)

    def _calculate_interaction_consistency_score(self, child: Child) -> float:
        """Calculate interaction consistency score (0-1)."""
        if child.total_interaction_time > 0:
            days_since_creation = (
                (datetime.now() - child.created_at).days if child.created_at else 1
            )
            consistency = min(
                child.total_interaction_time / (days_since_creation * 1800), 1.0
            )  # 30 min/day ideal
            return consistency
        return 0.0

    def _calculate_topic_diversity_score(self, child: Child) -> float:
        """Calculate topic diversity score (0-1)."""
        if child.interests:
            return min(len(child.interests) / 5.0, 1.0)  # 5 interests is ideal
        return 0.0

    def _calculate_engagement_level_score(self, child: Child) -> float:
        """Calculate engagement level score (0-1)."""
        total_days = (
            (datetime.now() - child.created_at).days if child.created_at else 30
        )
        insight = self.calculate_engagement_insights(child, total_days)

        engagement_scores = {
            EngagementLevel.HIGH: 1.0,
            EngagementLevel.MEDIUM: 0.7,
            EngagementLevel.LOW: 0.4,
            EngagementLevel.INACTIVE: 0.0,
        }
        return engagement_scores.get(insight.engagement_level, 0.0)

    def _calculate_profile_completeness_score(self, child: Child) -> float:
        """Calculate profile completeness score (0-1)."""
        profile_fields = [
            child.name,
            child.age,
            child.interests,
            child.personality_traits,
            child.learning_preferences,
            child.communication_style,
        ]
        completeness = sum(1 for field in profile_fields if field) / len(profile_fields)
        return completeness

    def _calculate_recent_activity_score(self, child: Child) -> float:
        """Calculate recent activity score (0-1)."""
        if child.last_interaction:
            days_since_last = (datetime.now() - child.last_interaction).days
            # Decay over 30 days
            return max(0, 1.0 - (days_since_last / 30.0))
        return 0.0
