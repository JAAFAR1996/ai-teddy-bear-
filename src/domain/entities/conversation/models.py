import hashlib
import re
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    FUNCTION = "function"


class ContentType(str, Enum):
    TEXT = "text"
    AUDIO = "audio"
    IMAGE = "image"
    FUNCTION_CALL = "function_call"
    FUNCTION_RESULT = "function_result"


class InteractionType(str, Enum):
    CONVERSATION = "conversation"
    STORY = "story"
    GAME = "game"
    LEARNING = "learning"
    QUESTION_ANSWER = "question_answer"


class EmotionalState(BaseModel):
    primary_emotion: str = Field(..., description="Primary emotion detected")
    confidence: float = Field(..., ge=0.0, le=1.0)
    valence: float = Field(..., ge=-1.0, le=1.0)
    arousal: float = Field(..., ge=0.0, le=1.0)
    emotions: Dict[str, float] = Field(default_factory=dict)


class MessageMetadata(BaseModel):
    audio_duration: Optional[float] = None
    language: Optional[str] = None
    confidence: Optional[float] = None
    moderation_flags: List[str] = Field(default_factory=list)
    educational_content: Optional[Dict[str, Any]] = None
    function_name: Optional[str] = None
    function_args: Optional[Dict[str, Any]] = None


class Message(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: MessageRole
    content: str
    content_type: ContentType = Field(default=ContentType.TEXT)
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: MessageMetadata = Field(default_factory=MessageMetadata)
    tokens: Optional[int] = None
    sentiment: Optional[float] = None
    topics: List[str] = Field(default_factory=list)
    entities: List[Dict[str, Any]] = Field(default_factory=list)

    @validator("content")
    def validate_content(cls, content):
        content = re.sub(r"<script[^>]*>.*?</script>",
                         "", content, flags=re.DOTALL | re.IGNORECASE)
        content = re.sub(r"<[^>]+>", "", content)
        if len(content) > 2000:
            raise ValueError("Text message content exceeds maximum length")
        return content.strip()

    def get_word_count(self) -> int:
        return len(self.content.split()) if self.content_type == ContentType.TEXT else 0

    def to_llm_format(self) -> Dict[str, str]:
        return {"role": self.role.value, "content": self.content}


class TurnTaking(BaseModel):
    user_turns: int = 0
    assistant_turns: int = 0
    average_user_length: float = 0.0
    average_assistant_length: float = 0.0
    response_times: List[float] = Field(default_factory=list)
    interruptions: int = 0


class ConversationMetrics(BaseModel):
    total_messages: int = 0
    total_words: int = 0
    unique_words: int = 0
    questions_asked: int = 0
    questions_answered: int = 0
    topic_changes: int = 0
    engagement_score: float = 0.0
    educational_value: float = 0.0
    safety_incidents: int = 0
    moderation_flags: int = 0


class ConversationSummary(BaseModel):
    brief: str
    key_topics: List[str] = Field(default_factory=list)
    learning_outcomes: List[str] = Field(default_factory=list)
    emotional_journey: str = ""
    memorable_moments: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


class Conversation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    child_id: str
    messages: List[Message] = Field(default_factory=list)
    start_time: datetime = Field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    duration: timedelta = Field(default=timedelta())
    interaction_type: InteractionType = Field(
        default=InteractionType.CONVERSATION)
    topics: List[str] = Field(default_factory=list)
    emotional_states: List[EmotionalState] = Field(default_factory=list)
    turn_taking: TurnTaking = Field(default_factory=TurnTaking)
    metrics: ConversationMetrics = Field(default_factory=ConversationMetrics)
    safety_score: float = Field(default=1.0, ge=0.0, le=1.0)
    quality_score: float = Field(default=0.0, ge=0.0, le=1.0)
    educational_score: float = Field(default=0.0, ge=0.0, le=1.0)
    llm_provider: Optional[str] = None
    voice_profile: Optional[str] = None
    language: str = Field(default="en")
    summary: Optional[ConversationSummary] = None
    parent_visible: bool = Field(default=True)
    parent_notes: Optional[str] = None

    def add_message(
        self, role: MessageRole, content: str, content_type: ContentType = ContentType.TEXT,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Message:
        message = Message(
            role=role, content=content, content_type=content_type,
            metadata=MessageMetadata(
                **metadata) if metadata else MessageMetadata(),
        )
        self.messages.append(message)
        self.end_time = datetime.now()
        self.duration = self.end_time - self.start_time
        return message

    def get_context(self, max_messages: int = 10) -> str:
        recent_messages = self.messages[-max_messages:]
        context_parts = [f"{msg.role.value}: {msg.content}" for msg in recent_messages if msg.role in [
            MessageRole.USER, MessageRole.ASSISTANT]]
        return "\n".join(context_parts)

    def get_transcript(self, include_timestamps: bool = False) -> str:
        lines = []
        for msg in self.messages:
            if msg.role in [MessageRole.USER, MessageRole.ASSISTANT]:
                prefix = f"[{msg.timestamp.strftime('%H:%M:%S')}] " if include_timestamps else ""
                lines.append(f"{prefix}{msg.role.value}: {msg.content}")
        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        return self.dict()

    def generate_hash(self) -> str:
        content = "".join([f"{m.role}:{m.content}" for m in self.messages])
        return hashlib.sha256(content.encode()).hexdigest()

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            timedelta: lambda v: str(v)
        }
        use_enum_values = True
