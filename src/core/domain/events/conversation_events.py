"""
📧 Conversation Domain Events
============================

Domain events related to conversation lifecycle and interactions.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from ..value_objects import ChildId, ConversationId, MessageId
from ...shared.kernel import DomainEvent
from ..entities.conversation import MessageType, EmotionDetection


@dataclass(frozen=True)
class ConversationStarted(DomainEvent):
    """Event fired when a conversation is started"""
    
    conversation_id: ConversationId
    child_id: ChildId
    started_at: datetime
    initial_topic: Optional[str] = None
    
    @property
    def event_type(self) -> str:
        return "conversation.started"


@dataclass(frozen=True)
class ConversationEnded(DomainEvent):
    """Event fired when a conversation ends"""
    
    conversation_id: ConversationId
    child_id: ChildId
    reason: str
    duration_minutes: float
    message_count: int
    engagement_score: float
    quality_score: float
    ended_at: datetime
    
    @property
    def event_type(self) -> str:
        return "conversation.ended"


@dataclass(frozen=True)
class ConversationPaused(DomainEvent):
    """Event fired when a conversation is paused"""
    
    conversation_id: ConversationId
    child_id: ChildId
    reason: str
    paused_at: datetime
    
    @property
    def event_type(self) -> str:
        return "conversation.paused"


@dataclass(frozen=True)
class ConversationResumed(DomainEvent):
    """Event fired when a conversation is resumed"""
    
    conversation_id: ConversationId
    child_id: ChildId
    resumed_at: datetime
    
    @property
    def event_type(self) -> str:
        return "conversation.resumed"


@dataclass(frozen=True)
class ConversationEscalated(DomainEvent):
    """Event fired when a conversation is escalated to human oversight"""
    
    conversation_id: ConversationId
    child_id: ChildId
    reason: str
    escalation_level: str = "standard"
    occurred_at: datetime = None
    
    def __post_init__(self):
        if self.occurred_at is None:
            object.__setattr__(self, 'occurred_at', datetime.utcnow())
    
    @property
    def event_type(self) -> str:
        return "conversation.escalated"


@dataclass(frozen=True)
class MessageReceived(DomainEvent):
    """Event fired when a message is received from child"""
    
    conversation_id: ConversationId
    child_id: ChildId
    message_id: MessageId
    message_type: MessageType
    emotion_detected: Optional[EmotionDetection] = None
    emotion_confidence: float = 0.0
    occurred_at: datetime = None
    
    def __post_init__(self):
        if self.occurred_at is None:
            object.__setattr__(self, 'occurred_at', datetime.utcnow())
    
    @property
    def event_type(self) -> str:
        return "message.received"


@dataclass(frozen=True)
class ResponseGenerated(DomainEvent):
    """Event fired when AI response is generated"""
    
    conversation_id: ConversationId
    child_id: ChildId
    message_id: MessageId
    processing_time_ms: int
    ai_model_version: str = "v2025.1"
    occurred_at: datetime = None
    
    def __post_init__(self):
        if self.occurred_at is None:
            object.__setattr__(self, 'occurred_at', datetime.utcnow())
    
    @property
    def event_type(self) -> str:
        return "response.generated"


@dataclass(frozen=True)
class EmotionDetected(DomainEvent):
    """Event fired when emotion is detected in child's message"""
    
    conversation_id: ConversationId
    child_id: ChildId
    emotion: EmotionDetection
    confidence: float
    context: str = ""
    occurred_at: datetime = None
    
    def __post_init__(self):
        if self.occurred_at is None:
            object.__setattr__(self, 'occurred_at', datetime.utcnow())
    
    @property
    def event_type(self) -> str:
        return "emotion.detected"


@dataclass(frozen=True)
class SafetyViolationInConversation(DomainEvent):
    """Event fired when safety violation occurs in conversation"""
    
    conversation_id: ConversationId
    child_id: ChildId
    message_id: MessageId
    violation_type: str
    severity: str  # "low", "medium", "high", "critical"
    details: str
    action_taken: str
    occurred_at: datetime = None
    
    def __post_init__(self):
        if self.occurred_at is None:
            object.__setattr__(self, 'occurred_at', datetime.utcnow())
    
    @property
    def event_type(self) -> str:
        return "safety.violation" 