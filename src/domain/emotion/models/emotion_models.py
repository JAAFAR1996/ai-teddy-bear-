"""Core emotion domain models."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


class EmotionType(Enum):
    """Child-friendly emotion categories."""

    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    SCARED = "scared"
    CALM = "calm"
    CURIOUS = "curious"


class AnalysisSource(Enum):
    """Source of emotion analysis."""

    TEXT = "text"
    AUDIO = "audio"
    COMBINED = "combined"


@dataclass
class EmotionResult:
    """Emotion analysis result with confidence scores."""

    primary_emotion: str
    confidence: float
    all_emotions: Dict[str, float]
    source: str
    timestamp: str
    behavioral_indicators: List[str]
    recommendations: List[str]

    def __post_init__(self):
        """Validate emotion result data."""
        if self.confidence < 0 or self.confidence > 1:
            raise ValueError("Confidence must be between 0 and 1")

        if self.primary_emotion not in self.all_emotions:
            self.all_emotions[self.primary_emotion] = self.confidence


@dataclass
class BehavioralIndicator:
    """Behavioral pattern indicator."""

    name: str
    description: str
    emotion_type: str
    confidence: float
    source: str


@dataclass
class EmotionContext:
    """Context information for emotion analysis."""

    child_age: Optional[int] = None
    time_of_day: Optional[str] = None
    recent_activities: Optional[List[str]] = None
    interaction_count_today: Optional[int] = None
    mood_trend: Optional[str] = None
    parent_reported_mood: Optional[str] = None


@dataclass
class ChildEmotionProfile:
    """Emotional profile for a child."""

    child_id: str
    dominant_emotions: Dict[str, float]
    behavioral_patterns: List[str]
    emotional_triggers: List[str]
    positive_indicators: List[str]
    risk_factors: List[str]
    last_updated: datetime

    @property
    def emotional_stability(self) -> float:
        """Calculate emotional stability score (0-1)."""
        calm_score = self.dominant_emotions.get("calm", 0)
        happy_score = self.dominant_emotions.get("happy", 0)
        negative_score = sum(
            [
                self.dominant_emotions.get("sad", 0),
                self.dominant_emotions.get("angry", 0),
                self.dominant_emotions.get("scared", 0),
            ]
        )

        stability = (calm_score + happy_score) - (negative_score * 0.5)
        return max(0, min(1, stability))

    @property
    def needs_attention(self) -> bool:
        """Determine if child needs emotional attention."""
        return (
            self.emotional_stability < 0.3
            or len(self.risk_factors) > 2
            or self.dominant_emotions.get("sad", 0) > 0.4
            or self.dominant_emotions.get("angry", 0) > 0.3
        )
