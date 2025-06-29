"""
👶 Child Aggregate Root
======================

Child is the main aggregate root in our domain, representing a child user
of the AI Teddy Bear system with all associated behavior and business rules.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import uuid4

from ..value_objects import (
    ChildId, ParentId, DeviceId, VoiceProfile, SafetySettings
)
from ..entities import Conversation
from ..events import (
    ChildRegistered, ChildProfileUpdated, SafetyViolationDetected,
    ConversationStarted, ConversationEnded
)
from ...shared.kernel import AggregateRoot, DomainEvent


class SafetyViolation(Exception):
    """Domain exception for safety violations"""
    pass


class ConversationLimitExceeded(Exception):
    """Domain exception for conversation limits"""
    pass


@dataclass
class Child(AggregateRoot):
    """
    Child Aggregate Root - Central domain entity representing a child user.
    
    This aggregate encapsulates all child-related business rules, safety constraints,
    and interaction management.
    """
    
    # Identity
    id: ChildId = field(default_factory=lambda: ChildId(uuid4()))
    parent_id: ParentId = field(default_factory=lambda: ParentId(uuid4()))
    device_id: DeviceId = field(default_factory=lambda: DeviceId(uuid4()))
    
    # Basic profile
    name: str = ""
    age: int = 0
    udid: str = ""
    
    # Preferences and settings
    voice_profile: Optional[VoiceProfile] = None
    safety_settings: Optional[SafetySettings] = None
    
    # Interaction history
    active_conversations: List[Conversation] = field(default_factory=list)
    total_conversations_today: int = 0
    daily_usage_minutes: float = 0.0
    last_interaction_at: Optional[datetime] = None
    
    # Learning and development tracking
    learning_preferences: Dict[str, Any] = field(default_factory=dict)
    emotional_state_history: List[Dict[str, Any]] = field(default_factory=list)
    development_milestones: List[str] = field(default_factory=list)
    
    # Safety tracking
    safety_violations_count: int = 0
    escalation_count: int = 0
    last_safety_check: Optional[datetime] = None
    
    # Metadata
    registered_at: datetime = field(default_factory=datetime.utcnow)
    last_updated_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True

    def __post_init__(self):
        """Post-initialization setup"""
        super().__post_init__()
        if self.is_newly_registered():
            self._emit_child_registered()

    @classmethod
    def register_new_child(
        cls,
        name: str,
        age: int,
        udid: str,
        parent_id: ParentId,
        device_id: DeviceId
    ) -> 'Child':
        """Factory method to register a new child"""
        
        if not name or not name.strip():
            raise ValueError("Child name cannot be empty")
        
        if not 3 <= age <= 12:
            raise ValueError("Child age must be between 3 and 12")
        
        if not udid:
            raise ValueError("Device UDID is required")
        
        child = cls(
            name=name.strip(),
            age=age,
            udid=udid,
            parent_id=parent_id,
            device_id=device_id,
            voice_profile=VoiceProfile.create_default(age),
            safety_settings=SafetySettings.create_for_age(age)
        )
        
        return child

    def update_profile(
        self,
        name: Optional[str] = None,
        age: Optional[int] = None,
        learning_preferences: Optional[Dict[str, Any]] = None
    ) -> None:
        """Update child profile with validation"""
        
        changes = {}
        
        if name is not None and name.strip() != self.name:
            if not name.strip():
                raise ValueError("Name cannot be empty")
            self.name = name.strip()
            changes["name"] = self.name
        
        if age is not None and age != self.age:
            if not 3 <= age <= 12:
                raise ValueError("Age must be between 3 and 12")
            
            old_age = self.age
            self.age = age
            changes["age"] = {"old": old_age, "new": age}
            
            # Update age-dependent settings
            self._update_age_dependent_settings()
        
        if learning_preferences is not None:
            self.learning_preferences.update(learning_preferences)
            changes["learning_preferences"] = learning_preferences
        
        if changes:
            self.last_updated_at = datetime.utcnow()
            self._emit_profile_updated(changes)

    def start_conversation(self, initial_topic: Optional[str] = None) -> Conversation:
        """Start a new conversation with comprehensive safety checks"""
        
        # Check if child can start conversation
        self._validate_conversation_start()
        
        # Create new conversation
        conversation = Conversation.create(
            child_id=self.id,
            max_duration_minutes=self.safety_settings.max_session_minutes,
            initial_topic=initial_topic
        )
        
        # Add to active conversations
        self.active_conversations.append(conversation)
        self.total_conversations_today += 1
        self.last_interaction_at = datetime.utcnow()
        
        # Emit domain event
        self._emit_conversation_started(conversation)
        
        return conversation

    def end_conversation(self, conversation_id: str, reason: str = "Natural ending") -> None:
        """End an active conversation"""
        
        conversation = self._find_active_conversation(conversation_id)
        if not conversation:
            return
        
        # End the conversation
        conversation.end_conversation(reason)
        
        # Update usage tracking
        duration = conversation.get_duration_minutes()
        self.daily_usage_minutes += duration
        
        # Remove from active conversations
        self.active_conversations = [
            c for c in self.active_conversations if str(c.id) != conversation_id
        ]
        
        # Emit domain event
        self._emit_conversation_ended(conversation, reason)

    def update_voice_profile(self, voice_profile: VoiceProfile) -> None:
        """Update voice profile with age-appropriateness check"""
        
        if not voice_profile.is_age_appropriate(self.age):
            raise ValueError("Voice profile not appropriate for child's age")
        
        if not self.safety_settings.allow_voice_changes:
            raise SafetyViolation("Voice changes not allowed by safety settings")
        
        self.voice_profile = voice_profile
        self.last_updated_at = datetime.utcnow()

    def update_safety_settings(self, safety_settings: SafetySettings) -> None:
        """Update safety settings with parent verification"""
        
        if not safety_settings.created_by_parent:
            raise SafetyViolation("Safety settings must be created by parent")
        
        self.safety_settings = safety_settings
        self.last_updated_at = datetime.utcnow()

    def report_safety_violation(self, violation_type: str, details: str) -> None:
        """Report a safety violation"""
        
        self.safety_violations_count += 1
        self.last_safety_check = datetime.utcnow()
        
        # Check if escalation is needed
        if self.safety_violations_count >= 3:
            self.escalation_count += 1
            self._emit_safety_escalation(violation_type, details)
        
        # Emit safety violation event
        self._emit_safety_violation(violation_type, details)

    def track_emotional_state(self, emotion: str, confidence: float, context: str = "") -> None:
        """Track child's emotional state for analysis"""
        
        emotional_entry = {
            "emotion": emotion,
            "confidence": confidence,
            "context": context,
            "timestamp": datetime.utcnow().isoformat(),
            "conversation_count": len(self.active_conversations)
        }
        
        self.emotional_state_history.append(emotional_entry)
        
        # Keep only last 100 entries
        if len(self.emotional_state_history) > 100:
            self.emotional_state_history = self.emotional_state_history[-100:]

    def add_development_milestone(self, milestone: str) -> None:
        """Add a development milestone achievement"""
        
        if milestone not in self.development_milestones:
            self.development_milestones.append(milestone)
            self.last_updated_at = datetime.utcnow()

    def can_start_conversation(self) -> bool:
        """Check if child can start a new conversation"""
        
        try:
            self._validate_conversation_start()
            return True
        except (SafetyViolation, ConversationLimitExceeded):
            return False

    def get_daily_usage_summary(self) -> Dict[str, Any]:
        """Get summary of daily usage"""
        
        return {
            "conversations_today": self.total_conversations_today,
            "minutes_used": self.daily_usage_minutes,
            "minutes_remaining": max(0, self.safety_settings.max_daily_minutes - self.daily_usage_minutes),
            "active_conversations": len(self.active_conversations),
            "last_interaction": self.last_interaction_at.isoformat() if self.last_interaction_at else None,
            "can_start_new": self.can_start_conversation()
        }

    def is_newly_registered(self) -> bool:
        """Check if child was just registered"""
        return len(self.active_conversations) == 0 and self.total_conversations_today == 0

    def _validate_conversation_start(self) -> None:
        """Validate if child can start a new conversation"""
        
        # Check safety settings
        if not self.safety_settings.can_start_conversation():
            raise SafetyViolation("Conversation not allowed due to time restrictions")
        
        # Check daily conversation limit
        if self.total_conversations_today >= self.safety_settings.max_conversations_per_day:
            raise ConversationLimitExceeded("Daily conversation limit exceeded")
        
        # Check daily time limit
        if self.daily_usage_minutes >= self.safety_settings.max_daily_minutes:
            raise ConversationLimitExceeded("Daily time limit exceeded")
        
        # Check active conversation limit (max 1 active conversation)
        if len(self.active_conversations) > 0:
            raise ConversationLimitExceeded("Another conversation is already active")

    def _find_active_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Find active conversation by ID"""
        
        for conversation in self.active_conversations:
            if str(conversation.id) == conversation_id:
                return conversation
        return None

    def _update_age_dependent_settings(self) -> None:
        """Update settings that depend on age"""
        
        # Update voice profile for new age
        if self.voice_profile:
            self.voice_profile = VoiceProfile.create_default(self.age)
        
        # Update safety settings for new age
        if self.safety_settings:
            self.safety_settings = SafetySettings.create_for_age(self.age)

    def _emit_child_registered(self) -> None:
        """Emit child registered event"""
        
        self._events.append(
            ChildRegistered(
                child_id=self.id,
                parent_id=self.parent_id,
                device_id=self.device_id,
                name=self.name,
                age=self.age,
                udid=self.udid,
                registered_at=self.registered_at
            )
        )

    def _emit_profile_updated(self, changes: Dict[str, Any]) -> None:
        """Emit profile updated event"""
        
        self._events.append(
            ChildProfileUpdated(
                child_id=self.id,
                changes=changes,
                updated_at=self.last_updated_at
            )
        )

    def _emit_conversation_started(self, conversation: Conversation) -> None:
        """Emit conversation started event"""
        
        self._events.append(
            ConversationStarted(
                conversation_id=conversation.id,
                child_id=self.id,
                started_at=conversation.started_at
            )
        )

    def _emit_conversation_ended(self, conversation: Conversation, reason: str) -> None:
        """Emit conversation ended event"""
        
        self._events.append(
            ConversationEnded(
                conversation_id=conversation.id,
                child_id=self.id,
                reason=reason,
                duration_minutes=conversation.get_duration_minutes(),
                message_count=len(conversation.messages),
                engagement_score=conversation.child_engagement_score,
                quality_score=conversation.conversation_quality_score,
                ended_at=conversation.ended_at or datetime.utcnow()
            )
        )

    def _emit_safety_violation(self, violation_type: str, details: str) -> None:
        """Emit safety violation event"""
        
        self._events.append(
            SafetyViolationDetected(
                child_id=self.id,
                violation_type=violation_type,
                details=details,
                violation_count=self.safety_violations_count,
                occurred_at=datetime.utcnow()
            )
        )

    def _emit_safety_escalation(self, violation_type: str, details: str) -> None:
        """Emit safety escalation event"""
        
        # This would be handled by a separate escalation event
        pass

    def __str__(self) -> str:
        return f"Child(id={self.id}, name={self.name}, age={self.age})"

    def __repr__(self) -> str:
        return (f"Child(id={self.id}, name='{self.name}', age={self.age}, "
                f"active_conversations={len(self.active_conversations)})") 