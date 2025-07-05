"""Analytics service for emotion insights and reporting."""

from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from typing import Dict, List

import structlog

from src.domain.emotion.models import (EmotionInsight, EmotionResult,
                                       EmotionTrend, ParentalReport,
                                       RiskAssessment, RiskLevel)

logger = structlog.get_logger(__name__)


class EmotionAnalyticsService:
    """Service for generating emotion analytics and insights."""

    def __init__(self):
        self.risk_thresholds = self._get_default_risk_thresholds()

    @staticmethod
    def _get_default_risk_thresholds() -> Dict[str, float]:
        """Returns the default dictionary of risk thresholds."""
        return {
            "high_negative_ratio": 0.4,
            "low_stability": 0.3,
            "concerning_patterns": 3,
        }

    async def generate_parental_report(
        self,
        child_id: str,
        child_name: str,
        emotions: List[EmotionResult],
        report_type: str = "weekly",
    ) -> ParentalReport:
        """Generate comprehensive parental report."""
        try:
            period_days = self._get_period_days(report_type)
            period_start = date.today() - timedelta(days=period_days)
            period_end = date.today()

            # Calculate basic statistics and emotion analysis
            basic_stats = self._calculate_basic_statistics(
                emotions, period_days)
            emotion_analysis = self._analyze_emotion_distribution(emotions)

            # Generate behavior and insight analysis
            behavior_insights = self._generate_behavior_insights(
                emotions, period_days)

            # Generate final recommendations and risk assessment
            recommendations = self._generate_parental_recommendations(
                emotion_analysis["dominant_emotions"], behavior_insights["concerns"]
            )
            risk_assessment = await self._assess_risk(child_id, emotions)

            return ParentalReport(
                child_id=child_id,
                child_name=child_name,
                report_type=report_type,
                period_start=period_start,
                period_end=period_end,
                total_interactions=basic_stats["total_interactions"],
                average_daily_interactions=basic_stats["avg_daily"],
                dominant_emotions=emotion_analysis["dominant_emotions"],
                emotional_stability=emotion_analysis["stability"],
                emotion_trends=behavior_insights["trends"],
                behavioral_changes=behavior_insights["behavioral_changes"],
                positive_highlights=behavior_insights["positive_highlights"],
                areas_of_concern=behavior_insights["concerns"],
                parental_recommendations=recommendations,
                risk_level=risk_assessment.overall_risk_level.value,
                risk_factors=risk_assessment.emotional_risk_factors,
                protective_factors=risk_assessment.emotional_strengths,
                generated_at=datetime.now(),
            )

        except Exception as e:
            logger.error(f" Failed to generate report: {e}")
            raise

    async def generate_emotion_insights(
        self, child_id: str, emotions: List[EmotionResult]
    ) -> List[EmotionInsight]:
        """Generate specific insights about emotional patterns."""
        insights = []

        try:
            # Pattern insights
            patterns = self._analyze_emotional_patterns(emotions)
            for pattern in patterns:
                insights.append(pattern)

            # Trigger insights
            triggers = self._identify_emotional_triggers(emotions)
            for trigger in triggers:
                insights.append(trigger)

            # Improvement insights
            improvements = self._identify_improvements(emotions)
            for improvement in improvements:
                insights.append(improvement)

            # Concern insights
            concerns = self._identify_emotional_concerns(emotions)
            for concern in concerns:
                insights.append(concern)

            # Sort by priority
            insights.sort(
                key=lambda x: {"high": 3, "medium": 2, "low": 1}[x.priority],
                reverse=True,
            )

            return insights

        except Exception as e:
            logger.error(f" Failed to generate insights: {e}")
            return []

    async def _assess_risk(
        self, child_id: str, emotions: List[EmotionResult]
    ) -> RiskAssessment:
        """Assess emotional risk for the child."""
        try:
            emotion_counts = Counter(e.primary_emotion for e in emotions)
            total = len(emotions)

            # Calculate risk and protective factors
            emotional_risks = self._calculate_emotional_risks(
                emotion_counts, total)
            behavioral_risks = []
            environmental_factors = []

            emotional_strengths = self._calculate_emotional_strengths(
                emotion_counts, total)
            support_systems = []
            coping_mechanisms = []

            # Calculate overall risk score and level
            risk_score = self._calculate_risk_score(
                emotional_risks, behavioral_risks, environmental_factors)
            risk_level = self._determine_risk_level(risk_score)

            # Generate recommendations
            immediate_actions, monitoring_plan, needs_referral = self._generate_risk_recommendations(
                risk_level)

            return RiskAssessment(
                child_id=child_id,
                assessment_date=datetime.now(),
                overall_risk_level=risk_level,
                risk_score=risk_score,
                emotional_risk_factors=emotional_risks,
                behavioral_risk_factors=behavioral_risks,
                environmental_factors=environmental_factors,
                emotional_strengths=emotional_strengths,
                support_systems=support_systems,
                coping_mechanisms=coping_mechanisms,
                immediate_actions=immediate_actions,
                monitoring_plan=monitoring_plan,
                professional_referral_needed=needs_referral,
            )

        except Exception as e:
            logger.error(f" Risk assessment failed: {e}")
            return self._create_safe_default_assessment(child_id)

    def _calculate_emotional_risks(self, emotion_counts: Counter, total: int) -> List[str]:
        """Calculate emotional risk factors."""
        emotional_risks = []

        if total > 0:
            sad_ratio = emotion_counts.get("sad", 0) / total
            angry_ratio = emotion_counts.get("angry", 0) / total
            scared_ratio = emotion_counts.get("scared", 0) / total

            if sad_ratio > 0.3:
                emotional_risks.append("High frequency of sadness")
            if angry_ratio > 0.2:
                emotional_risks.append("Frequent anger episodes")
            if scared_ratio > 0.25:
                emotional_risks.append("Elevated fear/anxiety levels")

        return emotional_risks

    def _calculate_emotional_strengths(self, emotion_counts: Counter, total: int) -> List[str]:
        """Calculate emotional protective factors."""
        emotional_strengths = []

        if total > 0:
            happy_ratio = emotion_counts.get("happy", 0) / total
            calm_ratio = emotion_counts.get("calm", 0) / total
            curious_ratio = emotion_counts.get("curious", 0) / total

            if happy_ratio > 0.4:
                emotional_strengths.append(
                    "Strong positive emotional expression")
            if calm_ratio > 0.2:
                emotional_strengths.append("Good emotional regulation")
            if curious_ratio > 0.25:
                emotional_strengths.append("Healthy curiosity and engagement")

        return emotional_strengths

    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """Determine risk level based on score."""
        if risk_score >= 75:
            return RiskLevel.CRITICAL
        elif risk_score >= 50:
            return RiskLevel.HIGH
        elif risk_score >= 25:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    def _generate_risk_recommendations(self, risk_level: RiskLevel) -> tuple:
        """Generate recommendations based on risk level."""
        immediate_actions = []
        monitoring_plan = []
        needs_referral = False

        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            immediate_actions.extend([
                "Increase emotional support and attention",
                "Monitor for signs of distress",
                "Consider professional consultation",
            ])
            needs_referral = risk_level == RiskLevel.CRITICAL

        return immediate_actions, monitoring_plan, needs_referral

    def _create_safe_default_assessment(self, child_id: str) -> RiskAssessment:
        """Create safe default risk assessment."""
        return RiskAssessment(
            child_id=child_id,
            assessment_date=datetime.now(),
            overall_risk_level=RiskLevel.LOW,
            risk_score=0,
            emotional_risk_factors=[],
            behavioral_risk_factors=[],
            environmental_factors=[],
            emotional_strengths=["Regular interaction with AI teddy"],
            support_systems=["Family support"],
            coping_mechanisms=[],
            immediate_actions=[],
            monitoring_plan=["Continue regular monitoring"],
            professional_referral_needed=False,
        )

    def _get_period_days(self, report_type: str) -> int:
        """Get number of days for report period."""
        return {"daily": 1, "weekly": 7, "monthly": 30, "custom": 14}.get(
            report_type, 7
        )

    def _calculate_emotional_stability(self, emotions: Dict[str, float]) -> float:
        """Calculate emotional stability score."""
        if not emotions:
            return 0.5

        positive_emotions = emotions.get("happy", 0) + emotions.get("calm", 0)
        negative_emotions = (
            emotions.get("sad", 0)
            + emotions.get("angry", 0)
            + emotions.get("scared", 0)
        )

        stability = positive_emotions - (negative_emotions * 0.5)
        return max(0, min(1, stability))

    def _generate_emotion_trends(
        self, emotions: List[EmotionResult], days: int
    ) -> List[EmotionTrend]:
        """Generate emotion trends over time."""
        trends = []

        # Group emotions by day
        daily_emotions = defaultdict(list)
        for emotion in emotions:
            day = datetime.fromisoformat(emotion.timestamp).date()
            daily_emotions[day].append(emotion.primary_emotion)

        # Calculate trends for each emotion type
        emotion_types = ["happy", "sad", "angry", "scared", "calm", "curious"]

        for emotion_type in emotion_types:
            dates = []
            values = []

            for day in sorted(daily_emotions.keys()):
                dates.append(day)
                day_count = daily_emotions[day].count(emotion_type)
                total_day = len(daily_emotions[day])
                values.append(day_count / total_day if total_day > 0 else 0)

            if len(values) >= 2:
                # Calculate trend direction
                recent_avg = sum(values[-3:]) / min(3, len(values))
                earlier_avg = (
                    sum(values[:-3]) / max(1, len(values) - 3)
                    if len(values) > 3
                    else recent_avg
                )

                change = (recent_avg - earlier_avg) / max(earlier_avg, 0.01)

                if change > 0.1:
                    direction = "increasing"
                elif change < -0.1:
                    direction = "decreasing"
                else:
                    direction = "stable"

                significance = (
                    "high"
                    if abs(change) > 0.3
                    else "medium" if abs(change) > 0.1 else "low"
                )

                trends.append(
                    EmotionTrend(
                        emotion=emotion_type,
                        dates=dates,
                        values=values,
                        direction=direction,
                        change_percentage=change * 100,
                        significance=significance,
                    )
                )

        return trends

    def _calculate_risk_score(
        self,
        emotional_risks: List[str],
        behavioral_risks: List[str],
        environmental_factors: List[str],
    ) -> float:
        """Calculate overall risk score (0-100)."""
        risk_score = 0

        # Emotional risk factors (up to 60 points)
        risk_score += len(emotional_risks) * 20

        # Behavioral risk factors (up to 30 points)
        risk_score += len(behavioral_risks) * 15

        # Environmental factors (up to 10 points)
        risk_score += len(environmental_factors) * 5

        return min(100, risk_score)

    def _analyze_emotional_patterns(
        self, emotions: List[EmotionResult]
    ) -> List[EmotionInsight]:
        """Analyze patterns in emotional data."""
        patterns = []

        if len(emotions) >= 5:
            emotion_sequence = [e.primary_emotion for e in emotions[-5:]]

            # Check for concerning patterns
            if emotion_sequence.count("sad") >= 3:
                patterns.append(
                    EmotionInsight(
                        type="pattern",
                        title="Recurring Sadness Pattern",
                        description="Child has shown sadness in multiple recent interactions",
                        confidence=0.8,
                        supporting_evidence=[
                            f"Sad emotions in {emotion_sequence.count('sad')} of last 5 interactions"
                        ],
                        recommendations=[
                            "Provide additional emotional support",
                            "Engage in uplifting activities",
                        ],
                        priority="high",
                    )
                )

        return patterns

    def _identify_behavioral_changes(self, emotions: List[EmotionResult]) -> List[str]:
        """Identify behavioral changes from emotion indicators."""
        changes = []

        # Analyze behavioral indicators
        all_indicators = []
        for emotion in emotions:
            all_indicators.extend(emotion.behavioral_indicators)

        indicator_counts = Counter(all_indicators)

        # Look for significant behavioral patterns
        if indicator_counts.get("short response", 0) > 3:
            changes.append("Trend toward shorter responses")
        if indicator_counts.get("multiple questions", 0) > 2:
            changes.append("Increased curiosity and questioning")

        return changes

    def _generate_positive_highlights(
        self, emotions: Dict[str, float], changes: List[str]
    ) -> List[str]:
        """Generate positive highlights for the report."""
        highlights = []

        if emotions.get("happy", 0) > 0.4:
            highlights.append(
                "Child shows strong positive emotional expression")
        if emotions.get("curious", 0) > 0.25:
            highlights.append("Healthy level of curiosity and engagement")
        if emotions.get("calm", 0) > 0.2:
            highlights.append("Good emotional regulation and calmness")

        return highlights

    def _identify_concerns(
        self, emotions: Dict[str, float], trends: List[EmotionTrend]
    ) -> List[str]:
        """Identify areas of concern."""
        concerns = []

        if emotions.get("sad", 0) > 0.3:
            concerns.append("Higher than normal levels of sadness")
        if emotions.get("angry", 0) > 0.2:
            concerns.append("Frequent anger or frustration")
        if emotions.get("scared", 0) > 0.25:
            concerns.append("Elevated anxiety or fear levels")

        return concerns

    def _generate_parental_recommendations(
        self, emotions: Dict[str, float], concerns: List[str]
    ) -> List[str]:
        """Generate recommendations for parents."""
        recommendations = []

        if emotions.get("happy", 0) > 0.4:
            recommendations.append("Continue current positive approach")

        if concerns:
            recommendations.extend(
                [
                    "Monitor emotional state closely",
                    "Provide additional emotional support",
                    "Consider professional guidance if concerns persist",
                ]
            )
        else:
            recommendations.append("Maintain regular interaction and support")

        return recommendations

    def _calculate_basic_statistics(self, emotions: List[EmotionResult], period_days: int) -> Dict:
        """Calculate basic statistics for the report."""
        total_interactions = len(emotions)
        avg_daily = total_interactions / period_days if period_days > 0 else 0
        return {
            "total_interactions": total_interactions,
            "avg_daily": avg_daily,
        }

    def _analyze_emotion_distribution(self, emotions: List[EmotionResult]) -> Dict:
        """Analyze emotion distribution and calculate stability."""
        total_interactions = len(emotions)
        emotion_counts = Counter(e.primary_emotion for e in emotions)

        dominant_emotions = (
            {
                emotion: count / total_interactions
                for emotion, count in emotion_counts.items()
            }
            if total_interactions > 0
            else {}
        )

        stability = self._calculate_emotional_stability(dominant_emotions)

        return {
            "dominant_emotions": dominant_emotions,
            "stability": stability,
        }

    def _generate_behavior_insights(self, emotions: List[EmotionResult], period_days: int) -> Dict:
        """Generate behavioral insights and patterns."""
        # Generate trends
        trends = self._generate_emotion_trends(emotions, period_days)

        # Identify behavioral changes
        behavioral_changes = self._identify_behavioral_changes(emotions)

        # Get emotion distribution for analysis
        emotion_analysis = self._analyze_emotion_distribution(emotions)
        dominant_emotions = emotion_analysis["dominant_emotions"]

        # Generate positive highlights and concerns
        positive_highlights = self._generate_positive_highlights(
            dominant_emotions, behavioral_changes)
        concerns = self._identify_concerns(dominant_emotions, trends)

        return {
            "trends": trends,
            "behavioral_changes": behavioral_changes,
            "positive_highlights": positive_highlights,
            "concerns": concerns,
        }
