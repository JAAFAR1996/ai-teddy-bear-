"""
Child Interaction Domain Entities
Core entities for managing child interactions with the teddy bear
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from ..shared.base import (AggregateRoot, DomainEvent, DomainException, Entity,
                           EntityId, ValueObject)


# Entity IDs
class ChildId(EntityId):
    """Strongly-typed ID for Child entity"""

    pass


class ConversationId(EntityId):
    """Strongly-typed ID for Conversation entity"""

    pass


class VoiceInteractionId(EntityId):
    """Strongly-typed ID for VoiceInteraction entity"""

    pass


class ParentId(EntityId):
    """Strongly-typed ID for Parent reference"""

    pass


# Enums
class ChildAgeGroup(Enum):
    """Age groups for content filtering"""

    TODDLER = "3-5"
    EARLY_CHILDHOOD = "6-8"
    MIDDLE_CHILDHOOD = "9-12"

    @classmethod
    def from_age(cls, age: int) -> "ChildAgeGroup":
        """Get age group from age"""
        if 3 <= age <= 5:
            return cls.TODDLER
        elif 6 <= age <= 8:
            return cls.EARLY_CHILDHOOD
        elif 9 <= age <= 12:
            return cls.MIDDLE_CHILDHOOD
        else:
            raise DomainException(
                f"Age {age} is not within supported range (3-12)", "INVALID_AGE_RANGE"
            )


class InteractionMode(Enum):
    """Types of interaction modes"""

    VOICE = "voice"
    BUTTON = "button"
    SCHEDULED = "scheduled"
    PARENT_INITIATED = "parent_initiated"


class ConversationStatus(Enum):
    """Status of a conversation"""

    ACTIVE = "active"
    COMPLETED = "completed"
    INTERRUPTED = "interrupted"
    FAILED = "failed"


# Value Objects
@dataclass(frozen=True)
class ChildName(ValueObject):
    """Child's name value object with validation"""

    first_name: str
    nickname: Optional[str] = None

    def validate(self):
        if not self.first_name or len(self.first_name.strip()) < 2:
            raise DomainException(
                "Child name must be at least 2 characters", "INVALID_NAME"
            )

        if len(self.first_name) > 50:
            raise DomainException("Child name too long", "NAME_TOO_LONG")

        # Check for inappropriate content in name
        inappropriate_words = ["admin", "system", "test", "null"]
        if any(word in self.first_name.lower() for word in inappropriate_words):
            raise DomainException("Invalid name", "INAPPROPRIATE_NAME")

    @property
    def display_name(self) -> str:
        """Get the name to use when addressing the child"""
        return self.nickname or self.first_name


@dataclass(frozen=True)
class ChildPreferences(ValueObject):
    """Child's preferences and interests"""

    favorite_topics: List[str] = field(default_factory=list)
    favorite_games: List[str] = field(default_factory=list)
    favorite_characters: List[str] = field(default_factory=list)
    learning_style: str = "interactive"
    voice_preference: str = "friendly"
    language: str = "en"

    def validate(self):
        if self.language not in ["en", "ar", "es", "fr"]:
            raise DomainException(
                f"Unsupported language: {self.language}", "INVALID_LANGUAGE"
            )

        if len(self.favorite_topics) > 10:
            raise DomainException("Too many favorite topics", "TOO_MANY_TOPICS")


@dataclass(frozen=True)
class SafetySettings(ValueObject):
    """Safety settings for a child"""

    content_filter_level: str = "strict"
    max_conversation_minutes: int = 30
    allowed_hours_start: int = 8  # 8 AM
    allowed_hours_end: int = 20  # 8 PM
    require_parent_approval: bool = False
    blocked_topics: List[str] = field(default_factory=list)

    def validate(self):
        if self.content_filter_level not in ["strict", "moderate", "relaxed"]:
            raise DomainException(
                "Invalid content filter level", "INVALID_FILTER_LEVEL"
            )

        if not 0 <= self.allowed_hours_start <= 23:
            raise DomainException("Invalid start hour", "INVALID_START_HOUR")

        if not 0 <= self.allowed_hours_end <= 23:
            raise DomainException("Invalid end hour", "INVALID_END_HOUR")

        if self.allowed_hours_start >= self.allowed_hours_end:
            raise DomainException(
                "Start hour must be before end hour", "INVALID_HOUR_RANGE"
            )

        if self.max_conversation_minutes < 5 or self.max_conversation_minutes > 120:
            raise DomainException(
                "Conversation limit must be between 5-120 minutes", "INVALID_TIME_LIMIT"
            )


@dataclass(frozen=True)
class VoiceData(ValueObject):
    """Voice data for an interaction"""

    audio_bytes: bytes
    duration_seconds: float
    format: str = "wav"
    sample_rate: int = 16000

    def validate(self):
        if not self.audio_bytes:
            raise DomainException("Voice data cannot be empty", "EMPTY_VOICE_DATA")

        if self.duration_seconds <= 0 or self.duration_seconds > 300:
            raise DomainException("Invalid voice duration", "INVALID_DURATION")

        if self.format not in ["wav", "mp3", "opus"]:
            raise DomainException(
                f"Unsupported audio format: {self.format}", "INVALID_FORMAT"
            )


# Entities
class VoiceInteraction(Entity[VoiceInteractionId]):
    """Entity representing a single voice interaction"""

    def __init__(
        self,
        id: VoiceInteractionId,
        child_message: str,
        child_voice_data: Optional[VoiceData],
        teddy_response: Optional[str] = None,
        safety_score: float = 1.0,
        timestamp: Optional[datetime] = None,
    ):
        super().__init__(id)
        self.child_message = child_message
        self.child_voice_data = child_voice_data
        self.teddy_response = teddy_response
        self.safety_score = safety_score
        self.timestamp = timestamp or datetime.now(timezone.utc)
        self.metadata: Dict[str, Any] = {}

    def set_response(self, response: str, safety_score: float):
        """Set the teddy's response after safety check"""
        if safety_score < 0 or safety_score > 1:
            raise DomainException(
                "Safety score must be between 0 and 1", "INVALID_SAFETY_SCORE"
            )

        self.teddy_response = response
        self.safety_score = safety_score

        self.add_domain_event(
            ResponseGeneratedEvent(
                interaction_id=self.id, response=response, safety_score=safety_score
            )
        )

    def mark_as_inappropriate(self, reason: str):
        """Mark interaction as inappropriate"""
        self.safety_score = 0.0
        self.metadata["inappropriate_reason"] = reason
        self.teddy_response = "Let's talk about something else!"

        self.add_domain_event(
            InappropriateContentDetectedEvent(
                interaction_id=self.id,
                reason=reason,
                original_message=self.child_message,
            )
        )


class Conversation(Entity[ConversationId]):
    """Entity representing a conversation session"""

    def __init__(
        self,
        id: ConversationId,
        child_id: ChildId,
        started_at: Optional[datetime] = None,
        interaction_mode: InteractionMode = InteractionMode.VOICE,
    ):
        super().__init__(id)
        self.child_id = child_id
        self.started_at = started_at or datetime.now(timezone.utc)
        self.ended_at: Optional[datetime] = None
        self.interaction_mode = interaction_mode
        self.status = ConversationStatus.ACTIVE
        self.interactions: List[VoiceInteraction] = []
        self.total_duration_seconds: float = 0
        self.learning_topics_covered: List[str] = []

    def add_interaction(self, interaction: VoiceInteraction):
        """Add an interaction to the conversation"""
        if self.status != ConversationStatus.ACTIVE:
            raise DomainException(
                "Cannot add interaction to non-active conversation",
                "CONVERSATION_NOT_ACTIVE",
            )

        self.interactions.append(interaction)

        # Update duration if voice data available
        if interaction.child_voice_data:
            self.total_duration_seconds += interaction.child_voice_data.duration_seconds

        self.add_domain_event(
            InteractionAddedEvent(
                conversation_id=self.id,
                interaction_id=interaction.id,
                message=interaction.child_message,
            )
        )

    def end_conversation(self, reason: str = "normal"):
        """End the conversation"""
        if self.status != ConversationStatus.ACTIVE:
            raise DomainException(
                "Conversation already ended", "CONVERSATION_ALREADY_ENDED"
            )

        self.ended_at = datetime.now(timezone.utc)
        self.status = ConversationStatus.COMPLETED

        duration = (self.ended_at - self.started_at).total_seconds()

        self.add_domain_event(
            ConversationEndedEvent(
                conversation_id=self.id,
                child_id=self.child_id,
                duration_seconds=duration,
                interaction_count=len(self.interactions),
                reason=reason,
            )
        )

    def interrupt_conversation(self, reason: str):
        """Interrupt the conversation"""
        self.ended_at = datetime.now(timezone.utc)
        self.status = ConversationStatus.INTERRUPTED

        self.add_domain_event(
            ConversationInterruptedEvent(
                conversation_id=self.id, child_id=self.child_id, reason=reason
            )
        )

    @property
    def duration(self) -> float:
        """Get conversation duration in seconds"""
        if self.ended_at:
            return (self.ended_at - self.started_at).total_seconds()
        return (datetime.now(timezone.utc) - self.started_at).total_seconds()


# Aggregate Root
class Child(AggregateRoot[ChildId]):
    """Child aggregate root - main entry point for child-related operations"""

    def __init__(
        self,
        id: ChildId,
        name: ChildName,
        age: int,
        parent_id: ParentId,
        preferences: Optional[ChildPreferences] = None,
        safety_settings: Optional[SafetySettings] = None,
    ):
        super().__init__(id)
        self.name = name
        self._age = age
        self.age_group = ChildAgeGroup.from_age(age)
        self.parent_id = parent_id
        self.preferences = preferences or ChildPreferences()
        self.safety_settings = safety_settings or SafetySettings()
        self.created_at = datetime.now(timezone.utc)
        self.last_interaction_at: Optional[datetime] = None
        self.total_interaction_count = 0
        self.active_conversation: Optional[ConversationId] = None
        self.device_id: Optional[str] = None

        # Raise creation event
        self.raise_event(
            ChildRegisteredEvent(
                child_id=id, parent_id=parent_id, name=name.display_name, age=age
            )
        )

    @property
    def age(self) -> int:
        """Get child's age"""
        return self._age

    def update_age(self, new_age: int):
        """Update child's age and adjust age group"""
        if new_age == self._age:
            return

        if new_age < 3 or new_age > 12:
            raise DomainException("Age must be between 3 and 12", "INVALID_AGE")

        old_age = self._age
        old_group = self.age_group

        self._age = new_age
        self.age_group = ChildAgeGroup.from_age(new_age)

        self.raise_event(
            ChildAgeUpdatedEvent(
                child_id=self.id,
                old_age=old_age,
                new_age=new_age,
                old_age_group=old_group.value,
                new_age_group=self.age_group.value,
            )
        )

    def start_conversation(
        self, mode: InteractionMode = InteractionMode.VOICE
    ) -> Conversation:
        """Start a new conversation"""
        if self.active_conversation:
            raise DomainException(
                "Child already has an active conversation",
                "CONVERSATION_ALREADY_ACTIVE",
            )

        # Check time restrictions
        current_hour = datetime.now(timezone.utc).hour
        if not (
            self.safety_settings.allowed_hours_start
            <= current_hour
            < self.safety_settings.allowed_hours_end
        ):
            raise DomainException(
                "Outside allowed conversation hours", "OUTSIDE_ALLOWED_HOURS"
            )

        conversation = Conversation(
            id=ConversationId(), child_id=self.id, interaction_mode=mode
        )

        self.active_conversation = conversation.id
        self.last_interaction_at = datetime.now(timezone.utc)

        self.raise_event(
            ConversationStartedEvent(
                child_id=self.id, conversation_id=conversation.id, mode=mode.value
            )
        )

        return conversation

    def end_active_conversation(self):
        """End the active conversation"""
        if not self.active_conversation:
            raise DomainException("No active conversation", "NO_ACTIVE_CONVERSATION")

        self.active_conversation = None
        self.total_interaction_count += 1

    def update_preferences(self, new_preferences: ChildPreferences):
        """Update child's preferences"""
        old_preferences = self.preferences
        self.preferences = new_preferences

        self.raise_event(
            ChildPreferencesUpdatedEvent(
                child_id=self.id,
                old_preferences=old_preferences,
                new_preferences=new_preferences,
            )
        )

    def update_safety_settings(self, new_settings: SafetySettings):
        """Update safety settings"""
        self.safety_settings = new_settings

        self.raise_event(
            SafetySettingsUpdatedEvent(child_id=self.id, new_settings=new_settings)
        )

    def register_device(self, device_id: str):
        """Register a device for this child"""
        self.device_id = device_id

        self.raise_event(DeviceRegisteredEvent(child_id=self.id, device_id=device_id))


# Domain Events
@dataclass
class ChildRegisteredEvent(DomainEvent):
    """Event raised when a new child is registered"""

    child_id: ChildId
    parent_id: ParentId
    name: str
    age: int

    def get_event_data(self) -> Dict[str, Any]:
        return {
            "child_id": str(self.child_id),
            "parent_id": str(self.parent_id),
            "name": self.name,
            "age": self.age,
        }


@dataclass
class ChildAgeUpdatedEvent(DomainEvent):
    """Event raised when child's age is updated"""

    child_id: ChildId
    old_age: int
    new_age: int
    old_age_group: str
    new_age_group: str

    def get_event_data(self) -> Dict[str, Any]:
        return {
            "child_id": str(self.child_id),
            "old_age": self.old_age,
            "new_age": self.new_age,
            "old_age_group": self.old_age_group,
            "new_age_group": self.new_age_group,
        }


@dataclass
class ConversationStartedEvent(DomainEvent):
    """Event raised when a conversation starts"""

    child_id: ChildId
    conversation_id: ConversationId
    mode: str

    def get_event_data(self) -> Dict[str, Any]:
        return {
            "child_id": str(self.child_id),
            "conversation_id": str(self.conversation_id),
            "mode": self.mode,
        }


@dataclass
class ConversationEndedEvent(DomainEvent):
    """Event raised when a conversation ends"""

    conversation_id: ConversationId
    child_id: ChildId
    duration_seconds: float
    interaction_count: int
    reason: str

    def get_event_data(self) -> Dict[str, Any]:
        return {
            "conversation_id": str(self.conversation_id),
            "child_id": str(self.child_id),
            "duration_seconds": self.duration_seconds,
            "interaction_count": self.interaction_count,
            "reason": self.reason,
        }


@dataclass
class ConversationInterruptedEvent(DomainEvent):
    """Event raised when a conversation is interrupted"""

    conversation_id: ConversationId
    child_id: ChildId
    reason: str

    def get_event_data(self) -> Dict[str, Any]:
        return {
            "conversation_id": str(self.conversation_id),
            "child_id": str(self.child_id),
            "reason": self.reason,
        }


@dataclass
class InteractionAddedEvent(DomainEvent):
    """Event raised when an interaction is added to a conversation"""

    conversation_id: ConversationId
    interaction_id: VoiceInteractionId
    message: str

    def get_event_data(self) -> Dict[str, Any]:
        return {
            "conversation_id": str(self.conversation_id),
            "interaction_id": str(self.interaction_id),
            "message": self.message,
        }


@dataclass
class ResponseGeneratedEvent(DomainEvent):
    """Event raised when a response is generated"""

    interaction_id: VoiceInteractionId
    response: str
    safety_score: float

    def get_event_data(self) -> Dict[str, Any]:
        return {
            "interaction_id": str(self.interaction_id),
            "response": self.response,
            "safety_score": self.safety_score,
        }


@dataclass
class InappropriateContentDetectedEvent(DomainEvent):
    """Event raised when inappropriate content is detected"""

    interaction_id: VoiceInteractionId
    reason: str
    original_message: str

    def get_event_data(self) -> Dict[str, Any]:
        return {
            "interaction_id": str(self.interaction_id),
            "reason": self.reason,
            "original_message": self.original_message,
        }


@dataclass
class ChildPreferencesUpdatedEvent(DomainEvent):
    """Event raised when child preferences are updated"""

    child_id: ChildId
    old_preferences: ChildPreferences
    new_preferences: ChildPreferences

    def get_event_data(self) -> Dict[str, Any]:
        return {
            "child_id": str(self.child_id),
            "changes": {
                "favorite_topics": self.new_preferences.favorite_topics,
                "language": self.new_preferences.language,
                "learning_style": self.new_preferences.learning_style,
            },
        }


@dataclass
class SafetySettingsUpdatedEvent(DomainEvent):
    """Event raised when safety settings are updated"""

    child_id: ChildId
    new_settings: SafetySettings

    def get_event_data(self) -> Dict[str, Any]:
        return {
            "child_id": str(self.child_id),
            "content_filter_level": self.new_settings.content_filter_level,
            "max_conversation_minutes": self.new_settings.max_conversation_minutes,
            "blocked_topics": self.new_settings.blocked_topics,
        }


@dataclass
class DeviceRegisteredEvent(DomainEvent):
    """Event raised when a device is registered for a child"""

    child_id: ChildId
    device_id: str

    def get_event_data(self) -> Dict[str, Any]:
        return {"child_id": str(self.child_id), "device_id": self.device_id}
