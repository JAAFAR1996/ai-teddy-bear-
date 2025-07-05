from datetime import datetime
from typing import Any, Dict, List, Optional

from ....domain.entities import Child, Conversation


@dataclass
class SafetyAssessmentResult:
    """Result of comprehensive safety assessment"""

    overall_safety_score: float  # 0.0 to 1.0
    risk_factors: List[str]
    protective_factors: List[str]
    recommendations: List[str]
    requires_parent_review: bool


class SafetyAssessor:
    """Performs safety assessments for a child."""

    def conduct_comprehensive_safety_assessment(
        self,
        child: Child,
        recent_conversations: List[Conversation],
        parent_feedback: Optional[Dict[str, Any]] = None,
    ) -> SafetyAssessmentResult:
        """
        Conduct a comprehensive safety assessment for a child based on
        their profile, recent activity, and parent feedback.
        """
        risk_factors = []
        protective_factors = []
        recommendations = []
        overall_safety_score = 1.0

        overall_safety_score, risk_factors, protective_factors, recommendations = self._assess_safety_violations(
            child, overall_safety_score, risk_factors, protective_factors, recommendations
        )
        overall_safety_score, risk_factors, protective_factors, recommendations = self._assess_behavioral_patterns(
            child, recent_conversations, overall_safety_score, risk_factors, protective_factors, recommendations
        )
        (
            overall_safety_score,
            protective_factors,
            recommendations,
            requires_parent_review,
        ) = self._assess_parent_involvement_and_review(
            child, parent_feedback, overall_safety_score, protective_factors, recommendations
        )

        return SafetyAssessmentResult(
            overall_safety_score=max(0.0, overall_safety_score),
            risk_factors=risk_factors,
            protective_factors=protective_factors,
            recommendations=recommendations,
            requires_parent_review=requires_parent_review,
        )

    def _assess_safety_violations(
        self, child: Child, overall_safety_score: float, risk_factors: List[str], protective_factors: List[str], recommendations: List[str]
    ) -> tuple[float, List[str], List[str], List[str]]:
        """Assess safety violations and their impact."""
        if child.safety_violations_count > 0:
            violation_impact = min(0.3, child.safety_violations_count * 0.1)
            overall_safety_score -= violation_impact
            risk_factors.append(
                f"{child.safety_violations_count} safety violations detected")
            if child.safety_violations_count >= 3:
                recommendations.append(
                    "Consider reviewing and updating safety settings")
        else:
            protective_factors.append(
                "No safety violations in recent activity")
        return overall_safety_score, risk_factors, protective_factors, recommendations

    def _assess_behavioral_patterns(
        self,
        child: Child,
        recent_conversations: List[Conversation],
        overall_safety_score: float,
        risk_factors: List[str],
        protective_factors: List[str],
        recommendations: List[str],
    ) -> tuple[float, List[str], List[str], List[str]]:
        """Assess conversation patterns, emotional stability, and usage patterns."""
        conversation_safety_score = self._assess_conversation_patterns_safety(
            recent_conversations)
        overall_safety_score *= conversation_safety_score
        if conversation_safety_score < 0.8:
            risk_factors.append(
                "Concerning patterns detected in recent conversations")
            recommendations.append("Review recent conversation transcripts")
        else:
            protective_factors.append("Healthy conversation patterns observed")

        emotion_stability_score = self._assess_emotional_stability(child)
        overall_safety_score *= emotion_stability_score
        if emotion_stability_score < 0.7:
            risk_factors.append("Emotional instability indicators detected")
            recommendations.append("Consider emotional support or counseling")
        else:
            protective_factors.append("Stable emotional patterns observed")

        usage_safety_score = self._assess_usage_patterns_safety(child)
        overall_safety_score *= usage_safety_score
        if usage_safety_score < 0.8:
            risk_factors.append("Potentially concerning usage patterns")
            recommendations.append("Review time limits and usage restrictions")
        else:
            protective_factors.append("Healthy usage patterns maintained")
        return overall_safety_score, risk_factors, protective_factors, recommendations

    def _assess_parent_involvement_and_review(
        self,
        child: Child,
        parent_feedback: Optional[Dict[str, Any]],
        overall_safety_score: float,
        protective_factors: List[str],
        recommendations: List[str],
    ) -> tuple[float, List[str], List[str], bool]:
        """Assess parent involvement and determine review requirements."""
        if parent_feedback:
            parent_involvement_score = self._assess_parent_involvement(
                parent_feedback)
            overall_safety_score *= parent_involvement_score
            if parent_involvement_score > 0.8:
                protective_factors.append(
                    "Strong parent involvement and oversight")
            else:
                recommendations.append(
                    "Encourage more parent involvement and oversight")

        requires_parent_review = (
            overall_safety_score < 0.7 or child.safety_violations_count >= 2 or child.escalation_count > 0
        )
        if requires_parent_review and "parent review" not in [r.lower() for r in recommendations]:
            recommendations.append("Parent review and approval required")
        return overall_safety_score, protective_factors, recommendations, requires_parent_review

    def _assess_conversation_patterns_safety(self, conversations: List[Conversation]) -> float:
        """Assess safety based on conversation patterns."""
        if not conversations:
            return 1.0
        safety_score = 1.0
        escalation_count = sum(
            1 for conv in conversations if conv.status == "escalated")
        if escalation_count > 0:
            safety_score -= escalation_count * 0.2
        total_violations = sum(
            conv.safety_violations for conv in conversations)
        if total_violations > 0:
            safety_score -= total_violations * 0.15
        low_engagement_count = sum(
            1 for conv in conversations if conv.child_engagement_score < 0.3)
        if low_engagement_count > len(conversations) * 0.5:
            safety_score -= 0.1
        return max(0.0, safety_score)

    def _assess_emotional_stability(self, child: Child) -> float:
        """Assess emotional stability based on emotion history."""
        if not child.emotional_state_history:
            return 0.8
        recent_emotions = child.emotional_state_history[-10:]
        negative_emotions = ["sad", "frustrated", "anxious", "angry"]
        negative_count = sum(
            1 for entry in recent_emotions if entry["emotion"] in negative_emotions)
        negative_ratio = negative_count / len(recent_emotions)
        if negative_ratio > 0.7:
            return 0.3
        elif negative_ratio > 0.5:
            return 0.6
        elif negative_ratio > 0.3:
            return 0.8
        else:
            return 1.0

    def _assess_usage_patterns_safety(self, child: Child) -> float:
        """Assess safety based on usage patterns."""
        safety_score = 1.0
        if child.safety_settings:
            usage_ratio = child.daily_usage_minutes / \
                child.safety_settings.max_daily_minutes
            if usage_ratio > 0.9:
                safety_score -= 0.1
            elif usage_ratio > 1.0:
                safety_score -= 0.3
        if child.total_conversations_today > 10:
            safety_score -= 0.1
        return max(0.0, safety_score)

    def _assess_parent_involvement(self, parent_feedback: Dict[str, Any]) -> float:
        """Assess parent involvement level."""
        involvement_score = 0.5
        if parent_feedback.get("recent_review", False):
            involvement_score += 0.2
        if parent_feedback.get("settings_updated_recently", False):
            involvement_score += 0.1
        if parent_feedback.get("feedback_provided", False):
            involvement_score += 0.2
        return min(1.0, involvement_score)
