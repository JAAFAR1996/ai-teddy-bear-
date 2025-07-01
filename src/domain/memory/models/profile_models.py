"""
Memory Profile Models - Child profiles and conversation summaries
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class ConversationSummary:
    """Summary of a conversation session - Domain entity"""

    session_id: str
    child_id: str
    start_time: datetime
    end_time: datetime
    message_count: int
    topics_discussed: List[str]
    emotional_journey: List[Tuple[datetime, str]]  # (timestamp, emotion)
    key_learnings: List[str]
    memorable_moments: List[str]
    overall_sentiment: float
    engagement_level: float

    @property
    def duration_minutes(self) -> float:
        """Calculate session duration in minutes"""
        return (self.end_time - self.start_time).total_seconds() / 60

    @property
    def average_sentiment(self) -> float:
        """Get average sentiment normalized"""
        return max(-1.0, min(1.0, self.overall_sentiment))

    def get_dominant_emotions(self) -> List[str]:
        """Extract dominant emotions from emotional journey"""
        if not self.emotional_journey:
            return []

        # Count emotion frequencies
        emotion_counts = {}
        for _, emotion in self.emotional_journey:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

        # Return emotions sorted by frequency
        return sorted(
            emotion_counts.keys(), key=lambda e: emotion_counts[e], reverse=True
        )[:3]

    def was_engaging(self) -> bool:
        """Check if conversation was engaging"""
        return (
            self.engagement_level > 0.7
            and self.duration_minutes > 5
            and len(self.topics_discussed) > 1
        )


@dataclass
class ChildMemoryProfile:
    """Complete memory profile for a child - Aggregate root"""

    child_id: str
    name: str
    age: int
    total_interactions: int
    first_interaction: datetime
    last_interaction: datetime

    # Preferences learned over time
    favorite_topics: Dict[str, float] = field(default_factory=dict)
    favorite_activities: List[str] = field(default_factory=list)
    favorite_stories: List[str] = field(default_factory=list)

    # Learning progress
    concepts_learned: Dict[str, datetime] = field(default_factory=dict)
    skills_developed: Dict[str, float] = field(default_factory=dict)
    vocabulary_growth: List[Tuple[str, datetime]] = field(default_factory=list)

    # Emotional patterns
    emotional_triggers: Dict[str, List[str]] = field(default_factory=dict)
    comfort_strategies: List[str] = field(default_factory=list)

    # Behavioral patterns
    interaction_patterns: Dict[str, Any] = field(default_factory=dict)
    attention_span_minutes: float = 10.0
    preferred_interaction_style: str = "conversational"

    def add_interaction(self, timestamp: Optional[datetime] = None) -> None:
        """Record a new interaction - Domain behavior"""
        self.total_interactions += 1
        interaction_time = timestamp or datetime.now()

        if not self.first_interaction:
            self.first_interaction = interaction_time

        self.last_interaction = interaction_time

    def update_topic_preference(self, topic: str, weight: float = 1.0) -> None:
        """Update preference for a topic"""
        current_weight = self.favorite_topics.get(topic, 0.0)
        # Use exponential moving average
        self.favorite_topics[topic] = 0.7 * current_weight + 0.3 * weight

        # Keep only top 20 topics
        if len(self.favorite_topics) > 20:
            sorted_topics = sorted(
                self.favorite_topics.items(), key=lambda x: x[1], reverse=True
            )
            self.favorite_topics = dict(sorted_topics[:20])

    def learn_concept(self, concept: str, timestamp: Optional[datetime] = None) -> None:
        """Record learning of a new concept"""
        learn_time = timestamp or datetime.now()
        self.concepts_learned[concept] = learn_time

    def develop_skill(self, skill: str, proficiency: float) -> None:
        """Update skill development"""
        # Ensure proficiency is between 0 and 1
        proficiency = max(0.0, min(1.0, proficiency))
        self.skills_developed[skill] = proficiency

    def add_vocabulary_word(
        self, word: str, timestamp: Optional[datetime] = None
    ) -> None:
        """Add new vocabulary word"""
        word_time = timestamp or datetime.now()
        # Check if word already exists
        for existing_word, _ in self.vocabulary_growth:
            if existing_word.lower() == word.lower():
                return  # Don't add duplicates

        self.vocabulary_growth.append((word, word_time))

        # Keep only recent 1000 words
        if len(self.vocabulary_growth) > 1000:
            self.vocabulary_growth = self.vocabulary_growth[-1000:]

    def get_recent_vocabulary(self, days: int = 30) -> List[str]:
        """Get vocabulary learned in recent days"""
        cutoff = datetime.now() - datetime.timedelta(days=days)
        return [
            word for word, timestamp in self.vocabulary_growth if timestamp > cutoff
        ]

    def get_learning_velocity(self) -> Dict[str, float]:
        """Calculate learning velocity metrics"""
        if not self.first_interaction:
            return {"concepts_per_week": 0.0, "vocabulary_per_week": 0.0}

        days_active = (self.last_interaction - self.first_interaction).days
        if days_active == 0:
            days_active = 1

        weeks_active = days_active / 7

        return {
            "concepts_per_week": len(self.concepts_learned) / weeks_active,
            "vocabulary_per_week": len(self.vocabulary_growth) / weeks_active,
            "interactions_per_week": self.total_interactions / weeks_active,
        }

    def is_active_learner(self) -> bool:
        """Check if child is actively learning"""
        velocity = self.get_learning_velocity()
        return (
            velocity["concepts_per_week"] > 1.0 or velocity["vocabulary_per_week"] > 5.0
        )
