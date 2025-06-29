"""
💬 Conversation Entity
=====================

Conversation entity represents a dialogue session between a child and the AI Teddy Bear.
It maintains the conversation state, messages, and enforces conversation-specific business rules.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from enum import Enum
from uuid import UUID, uuid4

from ..value_objects import ChildId, ConversationId, MessageId
from ..events import (
    ConversationStarted, ConversationEnded, MessageReceived, 
    ResponseGenerated, EmotionDetected
)
from ...shared.kernel import Entity, DomainEvent


class ConversationStatus(Enum):
    """Conversation status enumeration"""
    ACTIVE = "active"
    PAUSED = "paused"
    ENDED = "ended"
    ESCALATED = "escalated"
    SAFETY_STOPPED = "safety_stopped"


class MessageType(Enum):
    """Message type enumeration"""
    CHILD_VOICE = "child_voice"
    CHILD_TEXT = "child_text"
    AI_RESPONSE = "ai_response"
    SYSTEM_MESSAGE = "system_message"
    SAFETY_ALERT = "safety_alert"


class EmotionDetection(Enum):
    """Detected emotions"""
    HAPPY = "happy"
    SAD = "sad"
    EXCITED = "excited"
    FRUSTRATED = "frustrated"
    CALM = "calm"
    CONFUSED = "confused"
    TIRED = "tired"
    ANXIOUS = "anxious"


@dataclass
class Message:
    """Message value object within conversation"""
    id: MessageId = field(default_factory=lambda: MessageId(uuid4()))
    content: str = ""
    message_type: MessageType = MessageType.CHILD_TEXT
    timestamp: datetime = field(default_factory=datetime.utcnow)
    emotion_detected: Optional[EmotionDetection] = None
    emotion_confidence: float = 0.0
    safety_checked: bool = False
    processing_time_ms: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate message content"""
        if not self.content or not self.content.strip():
            raise ValueError("Message content cannot be empty")
        
        if len(self.content) > 5000:  # Max message length
            raise ValueError("Message content too long (max 5000 characters)")
        
        if not 0.0 <= self.emotion_confidence <= 1.0:
            raise ValueError("Emotion confidence must be between 0.0 and 1.0")

    def is_child_message(self) -> bool:
        """Check if message is from child"""
        return self.message_type in [MessageType.CHILD_VOICE, MessageType.CHILD_TEXT]

    def is_ai_response(self) -> bool:
        """Check if message is AI response"""
        return self.message_type == MessageType.AI_RESPONSE

    def has_strong_emotion(self, threshold: float = 0.7) -> bool:
        """Check if message has strong emotional content"""
        return self.emotion_confidence >= threshold

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for serialization"""
        return {
            "id": str(self.id),
            "content": self.content,
            "message_type": self.message_type.value,
            "timestamp": self.timestamp.isoformat(),
            "emotion_detected": self.emotion_detected.value if self.emotion_detected else None,
            "emotion_confidence": self.emotion_confidence,
            "safety_checked": self.safety_checked,
            "processing_time_ms": self.processing_time_ms,
            "metadata": self.metadata
        }


@dataclass
class Conversation(Entity):
    """
    Conversation entity representing a dialogue session.
    
    This entity manages the conversation lifecycle, messages,
    and enforces conversation-specific business rules.
    """
    
    # Identity
    id: ConversationId = field(default_factory=lambda: ConversationId(uuid4()))
    child_id: ChildId = field(default_factory=lambda: ChildId(uuid4()))
    
    # Conversation state
    status: ConversationStatus = ConversationStatus.ACTIVE
    title: str = ""
    
    # Messages and content
    messages: List[Message] = field(default_factory=list)
    current_topic: Optional[str] = None
    detected_emotions: List[EmotionDetection] = field(default_factory=list)
    
    # Timing and limits
    started_at: datetime = field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    last_activity_at: datetime = field(default_factory=datetime.utcnow)
    max_duration_minutes: int = 30
    
    # Quality metrics
    child_engagement_score: float = 0.0
    conversation_quality_score: float = 0.0
    safety_violations: int = 0
    
    # Technical metadata
    session_metadata: Dict[str, Any] = field(default_factory=dict)
    ai_model_version: str = "v2025.1"
    
    # Domain events
    _events: List[DomainEvent] = field(default_factory=list, init=False)

    def __post_init__(self):
        """Post-initialization setup"""
        if self.is_new_conversation():
            self._emit_conversation_started()

    @classmethod
    def create(
        cls, 
        child_id: ChildId, 
        max_duration_minutes: int = 30,
        initial_topic: Optional[str] = None
    ) -> 'Conversation':
        """Create a new conversation"""
        
        conversation = cls(
            child_id=child_id,
            max_duration_minutes=max_duration_minutes,
            current_topic=initial_topic,
            title=cls._generate_conversation_title(initial_topic)
        )
        
        return conversation

    def is_new_conversation(self) -> bool:
        """Check if this is a newly created conversation"""
        return len(self.messages) == 0 and self.status == ConversationStatus.ACTIVE

    def can_add_message(self) -> bool:
        """Check if new messages can be added"""
        if self.status != ConversationStatus.ACTIVE:
            return False
        
        if self.has_exceeded_time_limit():
            return False
        
        if self.safety_violations >= 3:  # Max safety violations
            return False
        
        return True

    def add_child_message(
        self, 
        content: str, 
        message_type: MessageType = MessageType.CHILD_TEXT,
        emotion_detected: Optional[EmotionDetection] = None,
        emotion_confidence: float = 0.0
    ) -> Message:
        """Add a message from the child"""
        
        if not self.can_add_message():
            raise ValueError(f"Cannot add message. Conversation status: {self.status}")
        
        message = Message(
            content=content,
            message_type=message_type,
            emotion_detected=emotion_detected,
            emotion_confidence=emotion_confidence
        )
        
        self.messages.append(message)
        self.last_activity_at = datetime.utcnow()
        
        # Update engagement and emotions
        self._update_engagement_score(message)
        if emotion_detected:
            self._track_emotion(emotion_detected)
        
        # Emit domain event
        self._emit_message_received(message)
        
        return message

    def add_ai_response(
        self, 
        content: str, 
        processing_time_ms: int = 0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Message:
        """Add an AI response message"""
        
        if not self.can_add_message():
            raise ValueError(f"Cannot add response. Conversation status: {self.status}")
        
        message = Message(
            content=content,
            message_type=MessageType.AI_RESPONSE,
            processing_time_ms=processing_time_ms,
            metadata=metadata or {}
        )
        
        self.messages.append(message)
        self.last_activity_at = datetime.utcnow()
        
        # Update conversation quality
        self._update_quality_score(message)
        
        # Emit domain event
        self._emit_response_generated(message)
        
        return message

    def add_system_message(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> Message:
        """Add a system message"""
        
        message = Message(
            content=content,
            message_type=MessageType.SYSTEM_MESSAGE,
            metadata=metadata or {}
        )
        
        self.messages.append(message)
        return message

    def pause_conversation(self, reason: str = "") -> None:
        """Pause the conversation"""
        if self.status == ConversationStatus.ACTIVE:
            self.status = ConversationStatus.PAUSED
            self.add_system_message(f"Conversation paused: {reason}")

    def resume_conversation(self) -> None:
        """Resume a paused conversation"""
        if self.status == ConversationStatus.PAUSED:
            if not self.has_exceeded_time_limit():
                self.status = ConversationStatus.ACTIVE
                self.add_system_message("Conversation resumed")
            else:
                self.end_conversation("Time limit exceeded")

    def end_conversation(self, reason: str = "Natural ending") -> None:
        """End the conversation"""
        if self.status in [ConversationStatus.ACTIVE, ConversationStatus.PAUSED]:
            self.status = ConversationStatus.ENDED
            self.ended_at = datetime.utcnow()
            self.add_system_message(f"Conversation ended: {reason}")
            
            # Calculate final scores
            self._calculate_final_scores()
            
            # Emit domain event
            self._emit_conversation_ended(reason)

    def escalate_conversation(self, reason: str) -> None:
        """Escalate conversation to human oversight"""
        self.status = ConversationStatus.ESCALATED
        self.add_system_message(f"Conversation escalated: {reason}")
        
        # Emit escalation event
        self._events.append(
            ConversationEscalated(
                conversation_id=self.id,
                child_id=self.child_id,
                reason=reason,
                occurred_at=datetime.utcnow()
            )
        )

    def report_safety_violation(self, violation_type: str, details: str) -> None:
        """Report a safety violation"""
        self.safety_violations += 1
        
        safety_message = f"Safety violation detected: {violation_type} - {details}"
        message = Message(
            content=safety_message,
            message_type=MessageType.SAFETY_ALERT,
            metadata={"violation_type": violation_type, "details": details}
        )
        
        self.messages.append(message)
        
        # Stop conversation if too many violations
        if self.safety_violations >= 3:
            self.status = ConversationStatus.SAFETY_STOPPED
            self.end_conversation("Multiple safety violations")

    def has_exceeded_time_limit(self) -> bool:
        """Check if conversation has exceeded time limit"""
        if not self.started_at:
            return False
        
        duration = datetime.utcnow() - self.started_at
        return duration > timedelta(minutes=self.max_duration_minutes)

    def get_duration_minutes(self) -> float:
        """Get conversation duration in minutes"""
        end_time = self.ended_at or datetime.utcnow()
        duration = end_time - self.started_at
        return duration.total_seconds() / 60.0

    def get_child_messages(self) -> List[Message]:
        """Get only child messages"""
        return [msg for msg in self.messages if msg.is_child_message()]

    def get_ai_responses(self) -> List[Message]:
        """Get only AI response messages"""
        return [msg for msg in self.messages if msg.is_ai_response()]

    def get_last_message(self) -> Optional[Message]:
        """Get the last message in conversation"""
        return self.messages[-1] if self.messages else None

    def get_dominant_emotion(self) -> Optional[EmotionDetection]:
        """Get the most frequently detected emotion"""
        if not self.detected_emotions:
            return None
        
        emotion_counts = {}
        for emotion in self.detected_emotions:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        return max(emotion_counts.items(), key=lambda x: x[1])[0]

    def _update_engagement_score(self, message: Message) -> None:
        """Update child engagement score based on message"""
        if not message.is_child_message():
            return
        
        # Simple engagement scoring based on message length and emotion
        length_score = min(len(message.content) / 100.0, 1.0)  # Normalize to 0-1
        emotion_score = message.emotion_confidence if message.emotion_detected else 0.5
        
        new_score = (length_score + emotion_score) / 2.0
        
        # Running average with previous scores
        message_count = len(self.get_child_messages())
        self.child_engagement_score = (
            (self.child_engagement_score * (message_count - 1) + new_score) / message_count
        )

    def _update_quality_score(self, message: Message) -> None:
        """Update conversation quality score based on AI response"""
        if not message.is_ai_response():
            return
        
        # Simple quality scoring based on processing time and response length
        time_score = max(0, 1.0 - (message.processing_time_ms / 10000.0))  # Penalty for slow responses
        length_score = min(len(message.content) / 200.0, 1.0)  # Normalize to 0-1
        
        new_score = (time_score + length_score) / 2.0
        
        # Running average
        response_count = len(self.get_ai_responses())
        self.conversation_quality_score = (
            (self.conversation_quality_score * (response_count - 1) + new_score) / response_count
        )

    def _track_emotion(self, emotion: EmotionDetection) -> None:
        """Track detected emotion"""
        self.detected_emotions.append(emotion)
        
        # Emit emotion detected event
        self._events.append(
            EmotionDetected(
                conversation_id=self.id,
                child_id=self.child_id,
                emotion=emotion,
                occurred_at=datetime.utcnow()
            )
        )

    def _calculate_final_scores(self) -> None:
        """Calculate final conversation scores"""
        # Adjust scores based on conversation completion
        duration_ratio = self.get_duration_minutes() / self.max_duration_minutes
        
        # Bonus for conversations that end naturally (not due to time limits)
        if self.status == ConversationStatus.ENDED and duration_ratio < 0.9:
            self.conversation_quality_score = min(1.0, self.conversation_quality_score * 1.1)
        
        # Penalty for safety violations
        if self.safety_violations > 0:
            violation_penalty = self.safety_violations * 0.1
            self.conversation_quality_score = max(0, self.conversation_quality_score - violation_penalty)

    @staticmethod
    def _generate_conversation_title(topic: Optional[str] = None) -> str:
        """Generate a conversation title"""
        if topic:
            return f"Chat about {topic}"
        
        timestamp = datetime.utcnow().strftime("%B %d, %H:%M")
        return f"Conversation - {timestamp}"

    def _emit_conversation_started(self) -> None:
        """Emit conversation started event"""
        self._events.append(
            ConversationStarted(
                conversation_id=self.id,
                child_id=self.child_id,
                started_at=self.started_at
            )
        )

    def _emit_message_received(self, message: Message) -> None:
        """Emit message received event"""
        self._events.append(
            MessageReceived(
                conversation_id=self.id,
                child_id=self.child_id,
                message_id=message.id,
                message_type=message.message_type,
                emotion_detected=message.emotion_detected,
                occurred_at=message.timestamp
            )
        )

    def _emit_response_generated(self, message: Message) -> None:
        """Emit response generated event"""
        self._events.append(
            ResponseGenerated(
                conversation_id=self.id,
                child_id=self.child_id,
                message_id=message.id,
                processing_time_ms=message.processing_time_ms,
                occurred_at=message.timestamp
            )
        )

    def _emit_conversation_ended(self, reason: str) -> None:
        """Emit conversation ended event"""
        self._events.append(
            ConversationEnded(
                conversation_id=self.id,
                child_id=self.child_id,
                reason=reason,
                duration_minutes=self.get_duration_minutes(),
                message_count=len(self.messages),
                engagement_score=self.child_engagement_score,
                quality_score=self.conversation_quality_score,
                ended_at=self.ended_at or datetime.utcnow()
            )
        )

    def clear_events(self) -> List[DomainEvent]:
        """Clear and return all pending domain events"""
        events = self._events.copy()
        self._events.clear()
        return events

    def __str__(self) -> str:
        return f"Conversation(id={self.id}, child={self.child_id}, status={self.status.value})"

    def __repr__(self) -> str:
        return (f"Conversation(id={self.id}, child_id={self.child_id}, "
                f"status={self.status}, messages={len(self.messages)}, "
                f"duration={self.get_duration_minutes():.1f}min)") 