from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List


class EmotionCategory(Enum):
    """Enhanced emotion categories for comprehensive analysis"""
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    SCARED = "scared"
    EXCITED = "excited"
    CURIOUS = "curious"
    CONFUSED = "confused"
    TIRED = "tired"
    NEUTRAL = "neutral"
    JOY = "joy"
    FEAR = "fear"
    LOVE = "love"
    SURPRISE = "surprise"


@dataclass
class EmotionAnalysis:
    """Comprehensive emotion analysis result"""
    primary_emotion: EmotionCategory
    confidence: float
    secondary_emotions: Dict[EmotionCategory,
                             float] = field(default_factory=dict)
    sentiment_score: float = 0.0  # -1 to 1
    arousal_level: float = 0.5  # 0 to 1
    keywords: List[str] = field(default_factory=list)
    language: str = "ar"
    analysis_method: str = "text"  # text, audio, or hybrid
    processing_time_ms: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
