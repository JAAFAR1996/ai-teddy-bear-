"""
Analytics Domain Models
======================

Domain models for analytics data, conversation logs, and learning progress tracking.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional
from collections import defaultdict
import uuid


@dataclass
class ConversationLog:
    """Detailed conversation log entry with business logic"""
    id: str
    child_id: str
    session_id: str
    timestamp: datetime
    duration_seconds: int
    message_count: int
    topics_discussed: List[str]
    sentiment_scores: Dict[str, float]
    moderation_flags: List[str]
    transcript: List[Dict[str, str]]
    audio_url: Optional[str] = None
    summary: Optional[str] = None
    
    def __post_init__(self):
        """Generate ID if not provided"""
        if not self.id:
            self.id = str(uuid.uuid4())
    
    def get_duration_minutes(self) -> float:
        """Get duration in minutes"""
        return self.duration_seconds / 60.0
    
    def get_dominant_sentiment(self) -> str:
        """Get the dominant sentiment from scores"""
        if not self.sentiment_scores:
            return "neutral"
        return max(self.sentiment_scores.items(), key=lambda x: x[1])[0]
    
    def has_educational_content(self) -> bool:
        """Check if conversation had educational content"""
        educational_topics = {'education', 'science', 'math', 'learning', 'study'}
        return bool(set(self.topics_discussed) & educational_topics)
    
    def get_quality_score(self) -> float:
        """Calculate conversation quality score (0-1)"""
        factors = {
            'appropriate_duration': min(self.get_duration_minutes() / 20, 1.0) * 0.3,
            'positive_sentiment': self.sentiment_scores.get('positive', 0) * 0.3,
            'topic_diversity': min(len(self.topics_discussed) / 3, 1.0) * 0.2,
            'educational_value': (1.0 if self.has_educational_content() else 0.0) * 0.2
        }
        return sum(factors.values())
    
    def is_concerning(self) -> bool:
        """Check if conversation has concerning flags"""
        concerning_flags = {'inappropriate_content', 'emotional_distress', 'safety_concern'}
        return bool(set(self.moderation_flags) & concerning_flags)


@dataclass
class LearningProgress:
    """Learning progress metrics with business calculations"""
    educational_engagement: float = 0.0
    topic_diversity: int = 0
    consistency_score: float = 0.0
    vocabulary_growth: int = 0
    skill_improvements: Dict[str, float] = field(default_factory=dict)
    achievements: List[str] = field(default_factory=list)
    
    def get_overall_progress_score(self) -> float:
        """Calculate overall progress score (0-100)"""
        scores = {
            'engagement': min(self.educational_engagement * 100, 100) * 0.3,
            'diversity': min(self.topic_diversity * 10, 100) * 0.2,
            'consistency': self.consistency_score * 100 * 0.3,
            'vocabulary': min(self.vocabulary_growth / 10, 100) * 0.2
        }
        return sum(scores.values())
    
    def get_progress_level(self) -> str:
        """Get qualitative progress level"""
        score = self.get_overall_progress_score()
        if score >= 80:
            return "excellent"
        elif score >= 60:
            return "good"
        elif score >= 40:
            return "fair"
        else:
            return "needs_improvement"
    
    def get_recommendations(self) -> List[str]:
        """Get learning recommendations based on progress"""
        recommendations = []
        
        if self.educational_engagement < 0.3:
            recommendations.append("Encourage more educational conversations")
        
        if self.topic_diversity < 3:
            recommendations.append("Explore new topics to broaden knowledge")
        
        if self.consistency_score < 0.5:
            recommendations.append("Establish a regular learning routine")
        
        if self.vocabulary_growth < 5:
            recommendations.append("Focus on vocabulary building activities")
        
        return recommendations


@dataclass
class UsageMetrics:
    """Usage metrics with trend analysis"""
    total_conversations: int = 0
    total_duration_minutes: float = 0.0
    average_session_minutes: float = 0.0
    daily_usage_trend: List[float] = field(default_factory=list)
    peak_usage_hours: List[int] = field(default_factory=list)
    session_frequency: float = 0.0
    
    def get_usage_pattern(self) -> str:
        """Determine usage pattern"""
        if self.average_session_minutes > 30:
            return "intensive_user"
        elif self.session_frequency > 3:
            return "frequent_user"
        elif self.session_frequency < 1:
            return "occasional_user"
        else:
            return "regular_user"
    
    def is_usage_concerning(self) -> bool:
        """Check if usage patterns are concerning"""
        return (
            self.average_session_minutes > 45 or
            self.total_duration_minutes > 120 or  # More than 2 hours daily
            len([h for h in self.peak_usage_hours if h > 21 or h < 7]) > 0  # Late night usage
        )
    
    def get_usage_insights(self) -> List[str]:
        """Get insights about usage patterns"""
        insights = []
        
        pattern = self.get_usage_pattern()
        if pattern == "intensive_user":
            insights.append("Child enjoys longer conversation sessions")
        elif pattern == "frequent_user":
            insights.append("Child uses the system regularly throughout the day")
        
        if self.peak_usage_hours:
            peak_times = [f"{h}:00" for h in self.peak_usage_hours[:3]]
            insights.append(f"Most active during: {', '.join(peak_times)}")
        
        if self.is_usage_concerning():
            insights.append("Consider setting time limits for healthy usage")
        
        return insights


@dataclass
class AnalyticsData:
    """Comprehensive analytics data with business insights"""
    total_conversations: int
    total_duration_minutes: float
    average_session_minutes: float
    topics_frequency: Dict[str, int]
    sentiment_breakdown: Dict[str, float]
    peak_usage_hours: List[int]
    learning_progress: LearningProgress
    vocabulary_growth: int
    interaction_quality_score: float
    usage_metrics: UsageMetrics
    
    def get_top_topics(self, limit: int = 5) -> List[tuple]:
        """Get top discussed topics"""
        return sorted(
            self.topics_frequency.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:limit]
    
    def get_sentiment_summary(self) -> str:
        """Get sentiment summary"""
        dominant = max(self.sentiment_breakdown.items(), key=lambda x: x[1])
        return f"Predominantly {dominant[0]} ({dominant[1]:.1%})"
    
    def get_health_score(self) -> float:
        """Calculate overall interaction health score (0-100)"""
        factors = {
            'positive_sentiment': self.sentiment_breakdown.get('positive', 0) * 30,
            'quality_interactions': self.interaction_quality_score * 25,
            'learning_progress': self.learning_progress.get_overall_progress_score() * 0.25,
            'balanced_usage': (100 - min(self.usage_metrics.is_usage_concerning() * 50, 50)) * 0.2
        }
        return sum(factors.values())
    
    def get_insights(self) -> List[str]:
        """Get key insights from analytics"""
        insights = []
        
        # Usage insights
        if self.total_conversations > 100:
            insights.append("Child is highly engaged with the system")
        
        # Learning insights
        if self.learning_progress.get_overall_progress_score() > 70:
            insights.append("Excellent learning progress observed")
        
        # Topic insights
        top_topic = self.get_top_topics(1)
        if top_topic:
            insights.append(f"Favorite topic: {top_topic[0][0]} ({top_topic[0][1]} conversations)")
        
        # Sentiment insights
        if self.sentiment_breakdown.get('positive', 0) > 0.7:
            insights.append("Child shows positive engagement patterns")
        elif self.sentiment_breakdown.get('negative', 0) > 0.3:
            insights.append("Some negative sentiment detected - may need attention")
        
        return insights
    
    def get_recommendations(self) -> List[str]:
        """Get recommendations based on analytics"""
        recommendations = []
        
        # Add learning recommendations
        recommendations.extend(self.learning_progress.get_recommendations())
        
        # Add usage recommendations
        recommendations.extend(self.usage_metrics.get_usage_insights())
        
        # Quality recommendations
        if self.interaction_quality_score < 0.6:
            recommendations.append("Focus on improving conversation quality")
        
        return list(set(recommendations))  # Remove duplicates


@dataclass 
class AnalyticsFilter:
    """Filter for analytics queries"""
    child_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    topics: Optional[List[str]] = None
    sentiment_filter: Optional[str] = None
    min_duration: Optional[int] = None
    max_duration: Optional[int] = None
    
    def applies_to_log(self, log: ConversationLog) -> bool:
        """Check if filter applies to a conversation log"""
        if self.child_id and log.child_id != self.child_id:
            return False
        
        if self.start_date and log.timestamp < self.start_date:
            return False
        
        if self.end_date and log.timestamp > self.end_date:
            return False
        
        if self.topics and not set(log.topics_discussed) & set(self.topics):
            return False
        
        if self.sentiment_filter and log.get_dominant_sentiment() != self.sentiment_filter:
            return False
        
        if self.min_duration and log.duration_seconds < self.min_duration:
            return False
        
        if self.max_duration and log.duration_seconds > self.max_duration:
            return False
        
        return True 