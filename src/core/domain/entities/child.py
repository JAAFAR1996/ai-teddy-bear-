"""
👶 Child Entity - Core Business Entity
=====================================

The Child entity serves as the main aggregate root in our domain model.
It encapsulates all business rules related to a child user of the AI Teddy Bear system.

This follows DDD principles with:
- Strong identity (ChildId)
- Business invariants enforcement
- Domain events emission
- Aggregate boundary protection
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from enum import Enum

from ..value_objects import (
    ChildId, ParentId, EmotionScore, LearningLevel, 
    InteractionPreferences, SafetySettings
)
from ..events import ChildRegistered, ChildProfileUpdated, ConversationStarted
from ...shared.kernel import AggregateRoot, DomainEvent


class ChildStatus(Enum):
    """Child account status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive" 
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"


class Gender(Enum):
    """Gender options for child profile"""
    MALE = "male"
    FEMALE = "female"
    NON_BINARY = "non_binary"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


@dataclass
class Child(AggregateRoot):
    """
    Child aggregate root representing a child user.
    
    This is the main entity that manages child's profile, preferences,
    learning progress, and interaction history while maintaining all
    business invariants.
    """
    
    # Identity
    id: ChildId = field(default_factory=lambda: ChildId(uuid4()))
    parent_id: ParentId = field(default_factory=lambda: ParentId(uuid4()))
    
    # Basic Information
    name: str = ""
    age: int = 0
    date_of_birth: Optional[date] = None
    gender: Optional[Gender] = None
    
    # Profile Information
    nickname: Optional[str] = None
    favorite_topics: List[str] = field(default_factory=list)
    learning_level: LearningLevel = field(default_factory=LearningLevel.beginner)
    language_preference: str = "en"
    
    # Interaction Settings
    interaction_preferences: InteractionPreferences = field(
        default_factory=InteractionPreferences
    )
    safety_settings: SafetySettings = field(default_factory=SafetySettings)
    
    # State Management
    status: ChildStatus = ChildStatus.PENDING_VERIFICATION
    is_active: bool = True
    current_emotion_score: Optional[EmotionScore] = None
    
    # Metrics & Progress
    total_conversations: int = 0
    total_interaction_time: int = 0  # in minutes
    learning_progress: Dict[str, float] = field(default_factory=dict)
    achievements: List[str] = field(default_factory=list)
    
    # Audit Fields
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_interaction_at: Optional[datetime] = None
    
    # Domain Event Management
    _events: List[DomainEvent] = field(default_factory=list, init=False)

    def __post_init__(self):
        """Post-initialization validation and setup"""
        self._validate_child_data()
        if self._is_new_child():
            self._emit_child_registered_event()

    def _validate_child_data(self) -> None:
        """Validate child data according to business rules"""
        if not self.name or len(self.name.strip()) < 2:
            raise ValueError("Child name must be at least 2 characters long")
        
        if self.age < 3 or self.age > 12:
            raise ValueError("Child age must be between 3 and 12 years")
        
        if self.date_of_birth and self._calculate_age_from_birth() != self.age:
            raise ValueError("Age and date of birth don't match")

    def _is_new_child(self) -> bool:
        """Check if this is a newly created child"""
        return self.created_at == self.updated_at

    def _calculate_age_from_birth(self) -> int:
        """Calculate age from date of birth"""
        if not self.date_of_birth:
            return self.age
        
        today = date.today()
        return (
            today.year - self.date_of_birth.year - 
            ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        )

    def update_profile(self, **kwargs) -> None:
        """Update child profile with validation"""
        updated_fields = {}
        
        for key, value in kwargs.items():
            if hasattr(self, key) and getattr(self, key) != value:
                setattr(self, key, value)
                updated_fields[key] = value
        
        if updated_fields:
            self.updated_at = datetime.utcnow()
            self._emit_profile_updated_event(updated_fields)

    def start_conversation(self) -> None:
        """Start a new conversation session"""
        if not self.is_active:
            raise ValueError("Cannot start conversation for inactive child")
        
        if self.status != ChildStatus.ACTIVE:
            raise ValueError(f"Cannot start conversation. Child status: {self.status}")
        
        self.last_interaction_at = datetime.utcnow()
        self.total_conversations += 1
        
        self._emit_conversation_started_event()

    def update_emotion_score(self, emotion_score: EmotionScore) -> None:
        """Update child's current emotional state"""
        if not isinstance(emotion_score, EmotionScore):
            raise TypeError("emotion_score must be an EmotionScore value object")
        
        self.current_emotion_score = emotion_score
        self.updated_at = datetime.utcnow()

    def add_interaction_time(self, minutes: int) -> None:
        """Add interaction time to child's total"""
        if minutes < 0:
            raise ValueError("Interaction time cannot be negative")
        
        self.total_interaction_time += minutes
        self.last_interaction_at = datetime.utcnow()

    def update_learning_progress(self, subject: str, progress: float) -> None:
        """Update learning progress for a specific subject"""
        if not 0 <= progress <= 1:
            raise ValueError("Progress must be between 0 and 1")
        
        self.learning_progress[subject] = progress
        self.updated_at = datetime.utcnow()

    def add_achievement(self, achievement: str) -> None:
        """Add new achievement to child's collection"""
        if achievement not in self.achievements:
            self.achievements.append(achievement)
            self.updated_at = datetime.utcnow()

    def activate(self) -> None:
        """Activate child account"""
        self.status = ChildStatus.ACTIVE
        self.is_active = True
        self.updated_at = datetime.utcnow()

    def deactivate(self) -> None:
        """Deactivate child account"""
        self.is_active = False
        self.updated_at = datetime.utcnow()

    def suspend(self, reason: str = "") -> None:
        """Suspend child account"""
        self.status = ChildStatus.SUSPENDED
        self.is_active = False
        self.updated_at = datetime.utcnow()

    def get_safety_restrictions(self) -> Dict[str, Any]:
        """Get child's safety restrictions"""
        return {
            "content_filter_level": self.safety_settings.content_filter_level,
            "interaction_time_limit": self.safety_settings.daily_time_limit,
            "allowed_topics": self.safety_settings.allowed_topics,
            "blocked_topics": self.safety_settings.blocked_topics,
        }

    def can_interact(self) -> bool:
        """Check if child can currently interact"""
        return (
            self.is_active and 
            self.status == ChildStatus.ACTIVE and
            self._within_time_limits()
        )

    def _within_time_limits(self) -> bool:
        """Check if child is within daily interaction time limits"""
        if not self.safety_settings.daily_time_limit:
            return True
        
        # This would need to be implemented with daily tracking
        # For now, we'll assume it's within limits
        return True

    def _emit_child_registered_event(self) -> None:
        """Emit child registered domain event"""
        event = ChildRegistered(
            child_id=self.id,
            parent_id=self.parent_id,
            name=self.name,
            age=self.age,
            occurred_at=datetime.utcnow()
        )
        self._events.append(event)

    def _emit_profile_updated_event(self, updated_fields: Dict[str, Any]) -> None:
        """Emit profile updated domain event"""
        event = ChildProfileUpdated(
            child_id=self.id,
            updated_fields=updated_fields,
            occurred_at=datetime.utcnow()
        )
        self._events.append(event)

    def _emit_conversation_started_event(self) -> None:
        """Emit conversation started domain event"""
        event = ConversationStarted(
            child_id=self.id,
            conversation_count=self.total_conversations,
            occurred_at=datetime.utcnow()
        )
        self._events.append(event)

    def clear_events(self) -> List[DomainEvent]:
        """Clear and return all pending domain events"""
        events = self._events.copy()
        self._events.clear()
        return events

    def __str__(self) -> str:
        return f"Child(id={self.id}, name='{self.name}', age={self.age})"

    def __repr__(self) -> str:
        return (
            f"Child(id={self.id}, name='{self.name}', age={self.age}, "
            f"status={self.status}, conversations={self.total_conversations})"
        ) 