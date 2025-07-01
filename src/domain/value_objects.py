"""
Basic Value Objects for AI Teddy Bear
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict


class EmotionalTone(Enum):
    HAPPY = "happy"
    SAD = "sad"
    NEUTRAL = "neutral"
    EXCITED = "excited"


class ConversationCategory(Enum):
    LEARNING = "learning"
    PLAY = "play"
    STORY = "story"
    GENERAL = "general"


@dataclass
class AIResponseModel:
    text: str
    confidence: float = 0.9
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ModelConfig:
    name: str
    provider: str
    temperature: float = 0.7
    max_tokens: int = 150

    def validate(self) -> bool:
        return True


class ResponseMode(Enum):
    NORMAL = "normal"
    EDUCATIONAL = "educational"
    PLAYFUL = "playful"
