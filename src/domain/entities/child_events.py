"""
👶 Child Domain Events
=====================

Domain events related to child lifecycle, registration, and profile management.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any

from ..value_objects import ChildId, ParentId, DeviceId
from ...shared.kernel import DomainEvent


@dataclass(frozen=True)
class ChildRegistered(DomainEvent):
    """Event fired when a new child is registered in the system"""
    
    child_id: ChildId
    parent_id: ParentId
    device_id: DeviceId
    name: str
    age: int
    udid: str
    registered_at: datetime
    
    @property
    def event_type(self) -> str:
        return "child.registered"


@dataclass(frozen=True)
class ChildProfileUpdated(DomainEvent):
    """Event fired when child profile is updated"""
    
    child_id: ChildId
    changes: Dict[str, Any]
    updated_at: datetime
    updated_by: str = "system"
    
    @property
    def event_type(self) -> str:
        return "child.profile_updated"


@dataclass(frozen=True)
class ChildDeactivated(DomainEvent):
    """Event fired when child account is deactivated"""
    
    child_id: ChildId
    reason: str
    deactivated_at: datetime
    deactivated_by: str
    
    @property
    def event_type(self) -> str:
        return "child.deactivated"


@dataclass(frozen=True)
class ChildReactivated(DomainEvent):
    """Event fired when child account is reactivated"""
    
    child_id: ChildId
    reactivated_at: datetime
    reactivated_by: str
    
    @property
    def event_type(self) -> str:
        return "child.reactivated"


@dataclass(frozen=True)
class SafetyViolationDetected(DomainEvent):
    """Event fired when safety violation is detected for a child"""
    
    child_id: ChildId
    violation_type: str
    details: str
    violation_count: int
    severity: str = "medium"
    occurred_at: datetime = None
    
    def __post_init__(self):
        if self.occurred_at is None:
            object.__setattr__(self, 'occurred_at', datetime.utcnow())
    
    @property
    def event_type(self) -> str:
        return "child.safety_violation"


@dataclass(frozen=True)
class SafetySettingsUpdated(DomainEvent):
    """Event fired when child safety settings are updated"""
    
    child_id: ChildId
    previous_settings: Dict[str, Any]
    new_settings: Dict[str, Any]
    updated_by: str  # parent_id or system
    updated_at: datetime
    
    @property
    def event_type(self) -> str:
        return "child.safety_settings_updated"


@dataclass(frozen=True)
class VoiceProfileUpdated(DomainEvent):
    """Event fired when child voice profile is updated"""
    
    child_id: ChildId
    previous_profile: Dict[str, Any]
    new_profile: Dict[str, Any]
    updated_at: datetime
    
    @property
    def event_type(self) -> str:
        return "child.voice_profile_updated"


@dataclass(frozen=True)
class DevelopmentMilestoneAchieved(DomainEvent):
    """Event fired when child achieves a development milestone"""
    
    child_id: ChildId
    milestone: str
    milestone_category: str  # "language", "social", "cognitive", "emotional"
    achieved_at: datetime
    context: str = ""
    
    @property
    def event_type(self) -> str:
        return "child.milestone_achieved"


@dataclass(frozen=True)
class UsageLimitReached(DomainEvent):
    """Event fired when child reaches usage limits"""
    
    child_id: ChildId
    limit_type: str  # "daily_time", "daily_conversations", "session_time"
    current_usage: int
    limit_value: int
    occurred_at: datetime
    
    @property
    def event_type(self) -> str:
        return "child.usage_limit_reached"


@dataclass(frozen=True)
class EmotionalStateTracked(DomainEvent):
    """Event fired when child's emotional state is tracked"""
    
    child_id: ChildId
    emotion: str
    confidence: float
    context: str
    conversation_id: str = ""
    tracked_at: datetime = None
    
    def __post_init__(self):
        if self.tracked_at is None:
            object.__setattr__(self, 'tracked_at', datetime.utcnow())
    
    @property
    def event_type(self) -> str:
        return "child.emotional_state_tracked" 