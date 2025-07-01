"""History service for emotion tracking and trends."""

from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import structlog

from ....domain.emotion.models import ChildEmotionProfile, EmotionResult, EmotionTrend

logger = structlog.get_logger(__name__)


class EmotionHistoryService:
    """Service for managing emotion history and trends."""

    def __init__(self, max_history_size: int = 1000):
        self.max_history_size = max_history_size
        self.emotion_cache = defaultdict(lambda: deque(maxlen=max_history_size))

    async def add_emotion_to_history(self, child_id: str, emotion_result: EmotionResult) -> None:
        """Add emotion result to child's history."""
        try:
            self.emotion_cache[child_id].append(emotion_result)
            logger.debug(f"Added emotion to history for child {child_id}")
        except Exception as e:
            logger.error(f" Failed to add emotion to history: {e}")

    async def get_emotion_history(self, child_id: str, hours: int = 24, limit: int = 100) -> List[EmotionResult]:
        """Get emotion history for a child."""
        try:
            if child_id not in self.emotion_cache:
                return []

            cutoff_time = datetime.now() - timedelta(hours=hours)
            emotions = list(self.emotion_cache[child_id])

            # Filter by time
            recent_emotions = [e for e in emotions if datetime.fromisoformat(e.timestamp) > cutoff_time]

            # Sort by timestamp (most recent first)
            recent_emotions.sort(key=lambda x: datetime.fromisoformat(x.timestamp), reverse=True)

            return recent_emotions[:limit]

        except Exception as e:
            logger.error(f" Failed to get emotion history: {e}")
            return []

    async def get_emotion_trends(self, child_id: str, days: int = 7, granularity: str = "daily") -> List[EmotionTrend]:
        """Get emotion trends over time."""
        try:
            emotions = await self.get_emotion_history(child_id, hours=days * 24, limit=1000)

            if not emotions:
                return []

            # Group emotions by time period
            time_groups = self._group_emotions_by_time(emotions, granularity)

            # Calculate trends for each emotion type
            emotion_types = ["happy", "sad", "angry", "scared", "calm", "curious"]
            trends = []

            for emotion_type in emotion_types:
                trend = self._calculate_emotion_trend(emotion_type, time_groups, granularity)
                if trend:
                    trends.append(trend)

            return trends

        except Exception as e:
            logger.error(f" Failed to get emotion trends: {e}")
            return []

    async def generate_child_profile(self, child_id: str, analysis_days: int = 30) -> Optional[ChildEmotionProfile]:
        """Generate comprehensive emotional profile for child."""
        try:
            emotions = await self.get_emotion_history(child_id, hours=analysis_days * 24, limit=1000)

            if not emotions:
                return None

            # Calculate dominant emotions
            emotion_counts = defaultdict(int)
            total_emotions = len(emotions)

            for emotion in emotions:
                emotion_counts[emotion.primary_emotion] += 1

            dominant_emotions = {emotion: count / total_emotions for emotion, count in emotion_counts.items()}

            # Identify behavioral patterns
            behavioral_patterns = self._identify_behavioral_patterns(emotions)

            # Identify emotional triggers
            emotional_triggers = self._identify_emotional_triggers(emotions)

            # Identify positive indicators
            positive_indicators = self._identify_positive_indicators(emotions)

            # Identify risk factors
            risk_factors = self._identify_risk_factors(emotions)

            return ChildEmotionProfile(
                child_id=child_id,
                dominant_emotions=dominant_emotions,
                behavioral_patterns=behavioral_patterns,
                emotional_triggers=emotional_triggers,
                positive_indicators=positive_indicators,
                risk_factors=risk_factors,
                last_updated=datetime.now(),
            )

        except Exception as e:
            logger.error(f" Failed to generate child profile: {e}")
            return None

    async def get_emotional_stability_score(self, child_id: str, days: int = 7) -> float:
        """Calculate emotional stability score for child."""
        try:
            emotions = await self.get_emotion_history(child_id, hours=days * 24, limit=1000)

            if not emotions:
                return 0.5  # Neutral stability

            # Calculate emotion distribution
            emotion_counts = defaultdict(int)
            for emotion in emotions:
                emotion_counts[emotion.primary_emotion] += 1

            total = len(emotions)

            # Calculate stability metrics
            positive_ratio = (emotion_counts["happy"] + emotion_counts["calm"]) / total

            negative_ratio = (emotion_counts["sad"] + emotion_counts["angry"] + emotion_counts["scared"]) / total

            # Stability score based on positive vs negative balance
            stability = positive_ratio - (negative_ratio * 0.5)

            # Factor in consistency (lower variance = higher stability)
            variance_penalty = self._calculate_emotion_variance(emotions)
            stability -= variance_penalty * 0.2

            return max(0, min(1, stability))

        except Exception as e:
            logger.error(f" Failed to calculate stability: {e}")
            return 0.5

    async def identify_concerning_patterns(self, child_id: str, days: int = 7) -> List[Dict[str, Any]]:
        """Identify concerning emotional patterns."""
        try:
            emotions = await self.get_emotion_history(child_id, hours=days * 24, limit=1000)

            patterns = []

            if len(emotions) < 5:
                return patterns

            # Check for consecutive negative emotions
            consecutive_negative = 0
            max_consecutive = 0

            for emotion in emotions:
                if emotion.primary_emotion in ["sad", "angry", "scared"]:
                    consecutive_negative += 1
                    max_consecutive = max(max_consecutive, consecutive_negative)
                else:
                    consecutive_negative = 0

            if max_consecutive >= 3:
                patterns.append(
                    {
                        "type": "consecutive_negative",
                        "description": f"Consecutive negative emotions detected ({max_consecutive} in a row)",
                        "severity": "high" if max_consecutive >= 5 else "medium",
                        "recommendation": "Provide immediate emotional support",
                    }
                )

            # Check for sudden emotional changes
            emotion_changes = self._detect_sudden_changes(emotions)
            for change in emotion_changes:
                patterns.append(change)

            # Check for declining interaction quality
            quality_decline = self._detect_interaction_quality_decline(emotions)
            if quality_decline:
                patterns.append(quality_decline)

            return patterns

        except Exception as e:
            logger.error(f" Failed to identify patterns: {e}")
            return []

    def _group_emotions_by_time(
        self, emotions: List[EmotionResult], granularity: str
    ) -> Dict[str, List[EmotionResult]]:
        """Group emotions by time periods."""
        groups = defaultdict(list)

        for emotion in emotions:
            timestamp = datetime.fromisoformat(emotion.timestamp)

            if granularity == "hourly":
                key = timestamp.strftime("%Y-%m-%d %H:00")
            elif granularity == "daily":
                key = timestamp.strftime("%Y-%m-%d")
            elif granularity == "weekly":
                # Get start of week
                start_of_week = timestamp - timedelta(days=timestamp.weekday())
                key = start_of_week.strftime("%Y-%m-%d")
            else:
                key = timestamp.strftime("%Y-%m-%d")

            groups[key].append(emotion)

        return groups

    def _calculate_emotion_trend(
        self, emotion_type: str, time_groups: Dict[str, List[EmotionResult]], granularity: str
    ) -> Optional[EmotionTrend]:
        """Calculate trend for specific emotion type."""
        if len(time_groups) < 2:
            return None

        dates = []
        values = []

        for time_key in sorted(time_groups.keys()):
            emotions_in_period = time_groups[time_key]
            emotion_count = sum(1 for e in emotions_in_period if e.primary_emotion == emotion_type)
            total_count = len(emotions_in_period)

            ratio = emotion_count / total_count if total_count > 0 else 0

            dates.append(datetime.strptime(time_key.split()[0], "%Y-%m-%d").date())
            values.append(ratio)

        if len(values) < 2:
            return None

        # Calculate trend direction
        recent_values = values[-3:] if len(values) >= 3 else values[-2:]
        earlier_values = values[:-3] if len(values) > 3 else values[:-2]

        recent_avg = sum(recent_values) / len(recent_values)
        earlier_avg = sum(earlier_values) / len(earlier_values) if earlier_values else recent_avg

        change = (recent_avg - earlier_avg) / max(earlier_avg, 0.01)

        if change > 0.1:
            direction = "increasing"
        elif change < -0.1:
            direction = "decreasing"
        else:
            direction = "stable"

        significance = "high" if abs(change) > 0.3 else "medium" if abs(change) > 0.1 else "low"

        return EmotionTrend(
            emotion=emotion_type,
            dates=dates,
            values=values,
            direction=direction,
            change_percentage=change * 100,
            significance=significance,
        )

    def _calculate_emotion_variance(self, emotions: List[EmotionResult]) -> float:
        """Calculate variance in emotion confidence scores."""
        if len(emotions) < 2:
            return 0

        confidences = [e.confidence for e in emotions]
        mean_confidence = sum(confidences) / len(confidences)
        variance = sum((c - mean_confidence) ** 2 for c in confidences) / len(confidences)

        return variance

    def _identify_behavioral_patterns(self, emotions: List[EmotionResult]) -> List[str]:
        """Identify behavioral patterns from emotion history."""
        patterns = []

        # Analyze behavioral indicators
        all_indicators = []
        for emotion in emotions:
            all_indicators.extend(emotion.behavioral_indicators)

        # Count common patterns
        from collections import Counter

        indicator_counts = Counter(all_indicators)

        # Identify significant patterns
        total_interactions = len(emotions)
        for indicator, count in indicator_counts.items():
            if count / total_interactions > 0.3:  # 30% or more
                patterns.append(f"Frequent {indicator}")

        return patterns

    def _identify_emotional_triggers(self, emotions: List[EmotionResult]) -> List[str]:
        """Identify potential emotional triggers."""
        triggers = []

        # Look for patterns in negative emotions
        negative_emotions = [e for e in emotions if e.primary_emotion in ["sad", "angry", "scared"]]

        if len(negative_emotions) > len(emotions) * 0.3:
            triggers.append("High frequency of negative emotions")

        # Analyze time patterns
        hour_emotions = defaultdict(list)
        for emotion in emotions:
            hour = datetime.fromisoformat(emotion.timestamp).hour
            hour_emotions[hour].append(emotion.primary_emotion)

        # Look for time-based triggers
        for hour, hour_emotion_list in hour_emotions.items():
            negative_ratio = sum(1 for e in hour_emotion_list if e in ["sad", "angry", "scared"]) / len(
                hour_emotion_list
            )

            if negative_ratio > 0.5 and len(hour_emotion_list) >= 3:
                triggers.append(f"Negative emotions common at {hour:02d}:00")

        return triggers

    def _identify_positive_indicators(self, emotions: List[EmotionResult]) -> List[str]:
        """Identify positive emotional indicators."""
        indicators = []

        # Count positive emotions
        positive_count = sum(1 for e in emotions if e.primary_emotion in ["happy", "calm", "curious"])

        positive_ratio = positive_count / len(emotions) if emotions else 0

        if positive_ratio > 0.6:
            indicators.append("High frequency of positive emotions")

        if positive_ratio > 0.8:
            indicators.append("Exceptional emotional positivity")

        # Check for consistent curiosity
        curious_count = sum(1 for e in emotions if e.primary_emotion == "curious")
        if curious_count / len(emotions) > 0.25:
            indicators.append("Strong curiosity and engagement")

        return indicators

    def _identify_risk_factors(self, emotions: List[EmotionResult]) -> List[str]:
        """Identify emotional risk factors."""
        risk_factors = []

        if not emotions:
            return risk_factors

        # High negative emotion ratio
        negative_count = sum(1 for e in emotions if e.primary_emotion in ["sad", "angry", "scared"])
        negative_ratio = negative_count / len(emotions)

        if negative_ratio > 0.4:
            risk_factors.append("High frequency of negative emotions")

        # Low interaction confidence
        avg_confidence = sum(e.confidence for e in emotions) / len(emotions)
        if avg_confidence < 0.5:
            risk_factors.append("Low confidence in emotion detection")

        # Concerning behavioral indicators
        concerning_indicators = ["short response", "hesitation", "quiet voice", "withdrawal"]

        for emotion in emotions:
            for indicator in emotion.behavioral_indicators:
                if any(concern in indicator.lower() for concern in concerning_indicators):
                    risk_factors.append(f"Behavioral concern: {indicator}")
                    break

        return list(set(risk_factors))  # Remove duplicates
