"""
🎯 Domain Value Objects
Value objects for the AI Teddy Bear domain model
"""

from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass

# ================== EMOTIONAL TONE ENUM ==================

class EmotionalTone(Enum):
    """Emotional tone value object"""
    HAPPY = "happy"
    SAD = "sad"
    EXCITED = "excited"
    CALM = "calm"
    ANGRY = "angry"
    SCARED = "scared"
    CURIOUS = "curious"
    LOVE = "love"
    NEUTRAL = "neutral"
    JOY = "joy"
    SADNESS = "sadness"
    FEAR = "fear"
    ENCOURAGING = "encouraging"
    FRIENDLY = "friendly"

    @classmethod
    def from_string(cls, emotion_str: str) -> "EmotionalTone":
        """Create EmotionalTone from string"""
        try:
            return cls(emotion_str.lower())
        except ValueError:
            return cls.NEUTRAL

# ================== CONVERSATION CATEGORY ENUM ==================

class ConversationCategory(Enum):
    """Conversation category value object"""
    GREETING = "greeting"
    STORY_REQUEST = "story_request"
    PLAY_REQUEST = "play_request"
    LEARNING_INQUIRY = "learning_inquiry"
    MUSIC_REQUEST = "music_request"
    QUESTION = "question"
    EMOTIONAL_EXPRESSION = "emotional_expression"
    GENERAL_CONVERSATION = "general_conversation"
    SYSTEM_MESSAGE = "system_message"
    FALLBACK = "fallback"
    CONVERSATION = "conversation"

    @classmethod
    def from_string(cls, category_str: str) -> "ConversationCategory":
        """Create ConversationCategory from string"""
        try:
            return cls(category_str.lower())
        except ValueError:
            return cls.GENERAL_CONVERSATION

# ================== LEARNING LEVEL ENUM ==================

class LearningLevel(Enum):
    """Learning level value object"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

# ================== CHILD AGE GROUP ENUM ==================

class AgeGroup(Enum):
    """Age group classification"""
    TODDLER = "toddler"  # 2-3 years
    PRESCHOOL = "preschool"  # 4-5 years
    SCHOOL_AGE = "school_age"  # 6-12 years
    TEENAGER = "teenager"  # 13+ years

    @classmethod
    def from_age(cls, age: int) -> "AgeGroup":
        """Determine age group from age"""
        if age <= 3:
            return cls.TODDLER
        elif age <= 5:
            return cls.PRESCHOOL
        elif age <= 12:
            return cls.SCHOOL_AGE
        else:
            return cls.TEENAGER

# ================== DEVICE STATUS ENUM ==================

class DeviceStatus(Enum):
    """Device status value object"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    ERROR = "error"

# ================== INTERACTION TYPE ENUM ==================

class InteractionType(Enum):
    """Type of interaction value object"""
    VOICE = "voice"
    TEXT = "text"
    BUTTON = "button"
    GESTURE = "gesture"
    TOUCH = "touch"

# ================== VALUE OBJECT DATA CLASSES ==================

@dataclass(frozen=True)
class DeviceId:
    """Device identifier value object"""
    value: str
    
    def __post_init__(self):
        if not self.value or not isinstance(self.value, str):
            raise ValueError("Device ID must be a non-empty string")
    
    def __str__(self) -> str:
        return self.value

@dataclass(frozen=True)
class SessionId:
    """Session identifier value object"""
    value: str
    
    def __post_init__(self):
        if not self.value or not isinstance(self.value, str):
            raise ValueError("Session ID must be a non-empty string")
    
    def __str__(self) -> str:
        return self.value

@dataclass(frozen=True)
class ChildName:
    """Child name value object with validation"""
    value: str
    
    def __post_init__(self):
        if not self.value or not isinstance(self.value, str):
            raise ValueError("Child name must be a non-empty string")
        if len(self.value.strip()) < 2:
            raise ValueError("Child name must be at least 2 characters")
    
    def __str__(self) -> str:
        return self.value.strip()

@dataclass(frozen=True)
class Age:
    """Age value object with validation"""
    value: int
    
    def __post_init__(self):
        if not isinstance(self.value, int) or self.value < 1 or self.value > 18:
            raise ValueError("Age must be between 1 and 18 years")
    
    @property
    def age_group(self) -> AgeGroup:
        """Get age group classification"""
        return AgeGroup.from_age(self.value)

@dataclass(frozen=True)
class Confidence:
    """Confidence score value object"""
    value: float
    
    def __post_init__(self):
        if not isinstance(self.value, (int, float)) or self.value < 0.0 or self.value > 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
    
    @property
    def percentage(self) -> int:
        """Get confidence as percentage"""
        return int(self.value * 100)
    
    @property
    def is_high(self) -> bool:
        """Check if confidence is high (>= 0.8)"""
        return self.value >= 0.8
    
    @property
    def is_low(self) -> bool:
        """Check if confidence is low (< 0.5)"""
        return self.value < 0.5 