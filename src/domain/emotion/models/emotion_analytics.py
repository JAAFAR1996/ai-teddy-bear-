"""Emotion analytics and reporting models."""

from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from typing import Dict, List


class ReportType(Enum):
    """Types of emotion reports."""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


class RiskLevel(Enum):
    """Risk assessment levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class EmotionAnalytics:
    """Comprehensive emotion analytics for a child."""

    child_id: str
    analysis_period: str
    total_interactions: int
    emotion_distribution: Dict[str, int]
    dominant_emotion: str
    emotional_stability_score: float
    behavioral_patterns: List[str]
    risk_assessment: str
    trends: Dict[str, float]
    recommendations: List[str]
    analysis_date: datetime


@dataclass
class EmotionTrend:
    """Emotion trend over time."""

    emotion: str
    dates: List[date]
    values: List[float]
    direction: str  # "increasing", "decreasing", "stable"
    change_percentage: float
    significance: str  # "high", "medium", "low"


@dataclass
class ParentalReport:
    """Comprehensive report for parents."""

    child_id: str
    child_name: str
    report_type: str
    period_start: date
    period_end: date

    # Summary
    total_interactions: int
    average_daily_interactions: float
    dominant_emotions: Dict[str, float]
    emotional_stability: float

    # Trends
    emotion_trends: List[EmotionTrend]
    behavioral_changes: List[str]

    # Insights
    positive_highlights: List[str]
    areas_of_concern: List[str]
    parental_recommendations: List[str]

    # Risk assessment
    risk_level: str
    risk_factors: List[str]
    protective_factors: List[str]

    generated_at: datetime


@dataclass
class EmotionInsight:
    """Specific insight about child's emotional patterns."""

    type: str  # "pattern", "trigger", "improvement", "concern"
    title: str
    description: str
    confidence: float
    supporting_evidence: List[str]
    recommendations: List[str]
    priority: str  # "high", "medium", "low"


@dataclass
class RiskAssessment:
    """Risk assessment for child's emotional wellbeing."""

    child_id: str
    assessment_date: datetime
    overall_risk_level: RiskLevel
    risk_score: float  # 0-100

    # Risk factors
    emotional_risk_factors: List[str]
    behavioral_risk_factors: List[str]
    environmental_factors: List[str]

    # Protective factors
    emotional_strengths: List[str]
    support_systems: List[str]
    coping_mechanisms: List[str]

    # Recommendations
    immediate_actions: List[str]
    monitoring_plan: List[str]
    professional_referral_needed: bool

    @property
    def needs_immediate_attention(self) -> bool:
        """Check if immediate attention is needed."""
        return (
            self.overall_risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
            or self.risk_score > 70
            or self.professional_referral_needed
        )
