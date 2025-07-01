"""
Analytics Domain Service
=======================

Domain service for analytics calculations and business logic.
"""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ..models.analytics_models import AnalyticsData, AnalyticsFilter, ConversationLog, LearningProgress, UsageMetrics
from ..models.user_models import ConversationLogEntry


class AnalyticsDomainService:
    """Domain service for analytics calculations"""

    def calculate_analytics(
        self, logs: List[ConversationLogEntry], filter_criteria: Optional[AnalyticsFilter] = None
    ) -> AnalyticsData:
        """Calculate comprehensive analytics from conversation logs"""

        # Filter logs if criteria provided
        if filter_criteria:
            logs = [log for log in logs if filter_criteria.applies_to_log(self._convert_to_conversation_log(log))]

        if not logs:
            return self._get_empty_analytics()

        # Calculate basic metrics
        total_conversations = len(logs)
        total_duration = sum(log.duration_seconds for log in logs)
        avg_session = total_duration / len(logs) if logs else 0

        # Calculate learning progress
        learning_progress = self._calculate_learning_progress(logs)

        # Calculate usage metrics
        usage_metrics = self._calculate_usage_metrics(logs)

        return AnalyticsData(
            total_conversations=total_conversations,
            total_duration_minutes=total_duration / 60,
            average_session_minutes=avg_session / 60,
            topics_frequency=self._calculate_topic_frequency(logs),
            sentiment_breakdown=self._calculate_sentiment_breakdown(logs),
            peak_usage_hours=self._calculate_peak_hours(logs),
            learning_progress=learning_progress,
            vocabulary_growth=self._calculate_vocabulary_growth(logs),
            interaction_quality_score=self._calculate_quality_score(logs),
            usage_metrics=usage_metrics,
        )

    def _calculate_learning_progress(self, logs: List[ConversationLogEntry]) -> LearningProgress:
        """Calculate learning progress metrics"""

        educational_topics = {"education", "science", "math", "learning", "study"}
        educational_conversations = sum(1 for log in logs if set(log.topics or []) & educational_topics)

        all_topics = set()
        for log in logs:
            all_topics.update(log.topics or [])

        return LearningProgress(
            educational_engagement=educational_conversations / len(logs) if logs else 0,
            topic_diversity=len(all_topics),
            consistency_score=min(len(logs) / 30, 1.0),  # Based on 30-day period
            vocabulary_growth=self._calculate_vocabulary_growth(logs),
        )

    def _calculate_usage_metrics(self, logs: List[ConversationLogEntry]) -> UsageMetrics:
        """Calculate usage pattern metrics"""

        total_duration = sum(log.duration_seconds for log in logs)
        peak_hours = self._calculate_peak_hours(logs)

        # Calculate daily usage trend (last 7 days)
        daily_trend = self._calculate_daily_trend(logs, days=7)

        # Calculate session frequency
        date_range = self._get_date_range(logs)
        frequency = len(logs) / max(date_range, 1) if date_range > 0 else 0

        return UsageMetrics(
            total_conversations=len(logs),
            total_duration_minutes=total_duration / 60,
            average_session_minutes=(total_duration / len(logs) / 60) if logs else 0,
            daily_usage_trend=daily_trend,
            peak_usage_hours=peak_hours,
            session_frequency=frequency,
        )

    def _calculate_topic_frequency(self, logs: List[ConversationLogEntry]) -> Dict[str, int]:
        """Calculate frequency of topics discussed"""
        topic_freq = defaultdict(int)
        for log in logs:
            for topic in log.topics or []:
                topic_freq[topic] += 1
        return dict(topic_freq)

    def _calculate_sentiment_breakdown(self, logs: List[ConversationLogEntry]) -> Dict[str, float]:
        """Calculate average sentiment breakdown"""
        if not logs:
            return {"positive": 0, "neutral": 0, "negative": 0}

        sentiment_totals = defaultdict(float)
        count = 0

        for log in logs:
            if log.sentiment_scores:
                count += 1
                for sentiment, score in log.sentiment_scores.items():
                    sentiment_totals[sentiment] += score

        if count == 0:
            return {"positive": 0, "neutral": 0, "negative": 0}

        return {k: v / count for k, v in sentiment_totals.items()}

    def _calculate_peak_hours(self, logs: List[ConversationLogEntry]) -> List[int]:
        """Calculate peak usage hours"""
        hour_counts = defaultdict(int)
        for log in logs:
            if log.started_at:
                hour = log.started_at.hour
                hour_counts[hour] += 1

        # Get top 3 hours
        sorted_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)
        return [hour for hour, count in sorted_hours[:3]]

    def _calculate_vocabulary_growth(self, logs: List[ConversationLogEntry]) -> int:
        """Calculate vocabulary growth (unique words used)"""
        all_words = set()
        for log in logs:
            if log.transcript:
                for message in log.transcript:
                    if isinstance(message, dict) and message.get("child"):
                        words = message["child"].lower().split()
                        all_words.update(words)
        return len(all_words)

    def _calculate_quality_score(self, logs: List[ConversationLogEntry]) -> float:
        """Calculate overall interaction quality score"""
        if not logs:
            return 0.0

        sentiment_breakdown = self._calculate_sentiment_breakdown(logs)
        topic_frequency = self._calculate_topic_frequency(logs)

        factors = {
            "positive_sentiment": sentiment_breakdown.get("positive", 0) * 0.3,
            "topic_diversity": min(len(topic_frequency) / 10, 1.0) * 0.2,
            "appropriate_duration": self._calculate_duration_score(logs) * 0.3,
            "educational_content": self._calculate_educational_score(logs) * 0.2,
        }

        return sum(factors.values())

    def _calculate_duration_score(self, logs: List[ConversationLogEntry]) -> float:
        """Calculate score based on appropriate session durations"""
        appropriate_sessions = sum(1 for log in logs if 5 <= (log.duration_seconds / 60) <= 30)
        return appropriate_sessions / len(logs) if logs else 0

    def _calculate_educational_score(self, logs: List[ConversationLogEntry]) -> float:
        """Calculate educational content engagement score"""
        educational_topics = {"education", "science", "math", "learning", "study"}
        educational_sessions = sum(1 for log in logs if set(log.topics or []) & educational_topics)
        return educational_sessions / len(logs) if logs else 0

    def _calculate_daily_trend(self, logs: List[ConversationLogEntry], days: int = 7) -> List[float]:
        """Calculate daily usage trend for specified days"""
        if not logs:
            return [0.0] * days

        # Get last N days
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days - 1)

        daily_counts = defaultdict(int)
        for log in logs:
            if log.started_at:
                log_date = log.started_at.date()
                if start_date <= log_date <= end_date:
                    daily_counts[log_date] += 1

        # Create trend list
        trend = []
        current_date = start_date
        for _ in range(days):
            trend.append(float(daily_counts[current_date]))
            current_date += timedelta(days=1)

        return trend

    def _get_date_range(self, logs: List[ConversationLogEntry]) -> int:
        """Get date range span of logs in days"""
        if not logs:
            return 0

        dates = [log.started_at.date() for log in logs if log.started_at]
        if not dates:
            return 0

        return (max(dates) - min(dates)).days + 1

    def _convert_to_conversation_log(self, log_entry: ConversationLogEntry) -> ConversationLog:
        """Convert database model to domain model"""
        return ConversationLog(
            id=log_entry.id,
            child_id=log_entry.child_id,
            session_id=log_entry.session_id or "",
            timestamp=log_entry.started_at,
            duration_seconds=log_entry.duration_seconds or 0,
            message_count=log_entry.message_count or 0,
            topics_discussed=log_entry.topics or [],
            sentiment_scores=log_entry.sentiment_scores or {},
            moderation_flags=log_entry.moderation_flags or [],
            transcript=log_entry.transcript or [],
            audio_url=log_entry.audio_url,
            summary=log_entry.summary,
        )

    def _get_empty_analytics(self) -> AnalyticsData:
        """Get empty analytics data structure"""
        return AnalyticsData(
            total_conversations=0,
            total_duration_minutes=0.0,
            average_session_minutes=0.0,
            topics_frequency={},
            sentiment_breakdown={"positive": 0, "neutral": 0, "negative": 0},
            peak_usage_hours=[],
            learning_progress=LearningProgress(),
            vocabulary_growth=0,
            interaction_quality_score=0.0,
            usage_metrics=UsageMetrics(),
        )
