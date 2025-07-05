# conversation.py - Enhanced conversation entity with complete features

import hashlib
import re
import statistics
import uuid
from collections import defaultdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


class MessageRole(str, Enum):
    """Message roles in a conversation"""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    FUNCTION = "function"  # For function/tool responses


class ContentType(str, Enum):
    """Types of content in messages"""

    TEXT = "text"
    AUDIO = "audio"
    IMAGE = "image"
    FUNCTION_CALL = "function_call"
    FUNCTION_RESULT = "function_result"


class InteractionType(str, Enum):
    """Types of interactions"""

    CONVERSATION = "conversation"
    STORY = "story"
    GAME = "game"
    LEARNING = "learning"
    QUESTION_ANSWER = "question_answer"


class EmotionalState(BaseModel):
    """Emotional state analysis"""

    primary_emotion: str = Field(..., description="Primary emotion detected")
    confidence: float = Field(..., ge=0.0, le=1.0,
                              description="Confidence score")
    valence: float = Field(
        ..., ge=-1.0, le=1.0, description="Emotional valence (-1 to 1)"
    )
    arousal: float = Field(
        ..., ge=0.0, le=1.0, description="Emotional arousal (0 to 1)"
    )
    emotions: Dict[str, float] = Field(
        default_factory=dict, description="All detected emotions"
    )


class MessageMetadata(BaseModel):
    """Metadata for a message"""

    audio_duration: Optional[float] = Field(
        None, description="Audio duration in seconds"
    )
    language: Optional[str] = Field(None, description="Detected language")
    confidence: Optional[float] = Field(None, description="STT/TTS confidence")
    moderation_flags: List[str] = Field(
        default_factory=list, description="Content moderation flags"
    )
    educational_content: Optional[Dict[str, Any]] = Field(
        None, description="Educational content metadata"
    )
    function_name: Optional[str] = Field(
        None, description="Function name if function call"
    )
    function_args: Optional[Dict[str, Any]] = Field(
        None, description="Function arguments"
    )


class Message(BaseModel):
    """Enhanced message in a conversation"""

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), description="Unique message ID"
    )
    role: MessageRole = Field(..., description="Role of the message sender")
    content: str = Field(..., description="Message content")
    content_type: ContentType = Field(
        default=ContentType.TEXT, description="Type of content"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Message timestamp"
    )
    metadata: MessageMetadata = Field(
        default_factory=MessageMetadata, description="Message metadata"
    )

    # Analysis results
    tokens: Optional[int] = Field(None, description="Number of tokens")
    sentiment: Optional[float] = Field(
        None, ge=-1.0, le=1.0, description="Sentiment score"
    )
    topics: List[str] = Field(default_factory=list,
                              description="Detected topics")
    entities: List[Dict[str, Any]] = Field(
        default_factory=list, description="Named entities"
    )

    @validator("content")
    def validate_content(cls, content, values) -> Any:
        """Validate message content"""
        # Remove potential XSS or injection attempts
        content = re.sub(
            r"<script[^>]*>.*?</script>", "", content, flags=re.DOTALL | re.IGNORECASE
        )
        content = re.sub(r"<[^>]+>", "", content)

        # Validate length based on content type
        content_type = values.get("content_type", ContentType.TEXT)
        if content_type == ContentType.TEXT and len(content) > 2000:
            raise ValueError(
                "Text message content exceeds maximum length of 2000 characters"
            )
        elif content_type == ContentType.AUDIO and len(content) > 5000:
            raise ValueError("Audio reference exceeds maximum length")

        return content.strip()

    def get_word_count(self) -> int:
        """Get word count of the message"""
        if self.content_type == ContentType.TEXT:
            return len(self.content.split())
        return 0

    def extract_questions(self) -> List[str]:
        """Extract questions from the message"""
        if self.content_type != ContentType.TEXT:
            return []

        # Simple question extraction
        sentences = re.split(r"[.!?]+", self.content)
        questions = [
            s.strip()
            for s in sentences
            if "?" in s
            or s.strip().startswith(
                (
                    "What",
                    "Who",
                    "Where",
                    "When",
                    "Why",
                    "How",
                    "Is",
                    "Are",
                    "Can",
                    "Will",
                )
            )
        ]
        return questions

    def to_llm_format(self) -> Dict[str, str]:
        """Convert to LLM-compatible format"""
        return {"role": self.role.value, "content": self.content}


class TurnTaking(BaseModel):
    """Analysis of conversation turn-taking patterns"""

    user_turns: int = 0
    assistant_turns: int = 0
    average_user_length: float = 0.0
    average_assistant_length: float = 0.0
    response_times: List[float] = Field(default_factory=list)
    interruptions: int = 0


class ConversationMetrics(BaseModel):
    """Detailed conversation metrics"""

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
    """AI-generated conversation summary"""

    brief: str = Field(..., description="Brief summary (1-2 sentences)")
    key_topics: List[str] = Field(
        default_factory=list, description="Main topics discussed"
    )
    learning_outcomes: List[str] = Field(
        default_factory=list, description="What was learned"
    )
    emotional_journey: str = Field("", description="Emotional progression")
    memorable_moments: List[str] = Field(
        default_factory=list, description="Notable moments"
    )
    recommendations: List[str] = Field(
        default_factory=list, description="Recommendations for future"
    )


class Conversation(BaseModel):
    """Enhanced conversation entity"""

    # Basic Information
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), description="Unique conversation ID"
    )
    session_id: str = Field(..., description="Session identifier")
    child_id: str = Field(..., description="ID of the child")

    # Messages
    messages: List[Message] = Field(
        default_factory=list, description="List of messages"
    )

    # Timing
    start_time: datetime = Field(
        default_factory=datetime.now, description="Start time")
    end_time: Optional[datetime] = Field(None, description="End time")
    duration: timedelta = Field(default=timedelta(), description="Duration")

    # Classification
    interaction_type: InteractionType = Field(
        default=InteractionType.CONVERSATION, description="Type of interaction"
    )

    # Analysis
    topics: List[str] = Field(default_factory=list,
                              description="Conversation topics")
    emotional_states: List[EmotionalState] = Field(
        default_factory=list, description="Emotional journey"
    )
    turn_taking: TurnTaking = Field(
        default_factory=TurnTaking, description="Turn-taking analysis"
    )
    metrics: ConversationMetrics = Field(
        default_factory=ConversationMetrics, description="Conversation metrics"
    )

    # Quality & Safety
    safety_score: float = Field(
        default=1.0, ge=0.0, le=1.0, description="Safety score")
    quality_score: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Quality score"
    )
    educational_score: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Educational value"
    )

    # Context
    llm_provider: Optional[str] = Field(None, description="LLM provider used")
    voice_profile: Optional[str] = Field(
        None, description="Voice profile used")
    language: str = Field(default="en", description="Primary language")

    # Summary
    summary: Optional[ConversationSummary] = Field(
        None, description="AI-generated summary"
    )

    # Parent visibility
    parent_visible: bool = Field(
        default=True, description="Visible to parents")
    parent_notes: Optional[str] = Field(None, description="Notes from parents")

    def add_message(
        self,
        role: MessageRole,
        content: str,
        content_type: ContentType = ContentType.TEXT,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Message:
        """Add a message to the conversation"""
        message = Message(
            role=role,
            content=content,
            content_type=content_type,
            metadata=MessageMetadata(
                **metadata) if metadata else MessageMetadata(),
        )

        self.messages.append(message)

        # Update metrics
        self._update_metrics(message)

        # Update end time and duration
        self.end_time = datetime.now()
        self.duration = self.end_time - self.start_time

        return message

    def _update_metrics(self, message) -> None:
        """Update conversation metrics"""
        self.metrics.total_messages += 1

        if hasattr(message, 'content_type') and message.content_type == ContentType.TEXT:
            words = message.content.split()
            self.metrics.total_words += len(words)

            # Update turn taking
            if hasattr(message, 'role') and message.role == MessageRole.USER:
                self.turn_taking.user_turns += 1
            elif hasattr(message, 'role') and message.role == MessageRole.ASSISTANT:
                self.turn_taking.assistant_turns += 1

            # Count questions
            if hasattr(message, 'extract_questions'):
                questions = message.extract_questions()
                if questions:
                    self.metrics.questions_asked += len(questions)

    def get_context(self, max_messages: int = 10) -> str:
        """Get conversation context for LLM"""
        recent_messages = self.messages[-max_messages:]
        context_parts = []

        for msg in recent_messages:
            if msg.role in [MessageRole.USER, MessageRole.ASSISTANT]:
                context_parts.append(f"{msg.role.value}: {msg.content}")

        return "\n".join(context_parts)

    def get_messages_for_llm(self, include_system: bool = True) -> List[Dict[str, str]]:
        """Get messages formatted for LLM input"""
        llm_messages = []

        for msg in self.messages:
            if msg.role == MessageRole.SYSTEM and not include_system:
                continue
            if msg.content_type == ContentType.TEXT:
                llm_messages.append(msg.to_llm_format())

        return llm_messages

    def extract_topics(self) -> List[str]:
        """Extract topics from conversation messages"""
        # Enhanced topic extraction
        topic_keywords = {
            "education": [
                "learn",
                "school",
                "study",
                "homework",
                "teach",
                "تعلم",
                "مدرسة",
            ],
            "science": [
                "science",
                "biology",
                "physics",
                "chemistry",
                "space",
                "علم",
                "فيزياء",
            ],
            "math": ["math", "number", "count", "calculate", "رياضيات", "رقم"],
            "art": ["art", "draw", "paint", "color", "create", "فن", "رسم"],
            "music": ["music", "song", "sing", "instrument", "موسيقى", "أغنية"],
            "games": ["game", "play", "fun", "puzzle", "لعبة", "لعب"],
            "stories": ["story", "tale", "book", "read", "قصة", "حكاية"],
            "animals": ["animal", "pet", "dog", "cat", "bird", "حيوان", "قطة"],
            "nature": ["nature", "tree", "flower", "weather", "طبيعة", "شجرة"],
            "emotions": ["feel", "happy", "sad", "angry", "شعور", "سعيد", "حزين"],
            "family": [
                "family",
                "mom",
                "dad",
                "brother",
                "sister",
                "عائلة",
                "أم",
                "أب",
            ],
        }

        found_topics = set()
        all_text = " ".join(
            [
                msg.content.lower()
                for msg in self.messages
                if msg.content_type == ContentType.TEXT
            ]
        )

        for topic, keywords in topic_keywords.items():
            if any(keyword in all_text for keyword in keywords):
                found_topics.add(topic)

        # Also check message topics
        for msg in self.messages:
            found_topics.update(msg.topics)

        self.topics = list(found_topics)
        return self.topics

    def analyze_emotional_journey(self) -> List[EmotionalState]:
        """Analyze emotional progression throughout conversation"""
        emotional_states = []

        # Group messages by time windows (e.g., every 5 messages)
        window_size = 5
        for i in range(0, len(self.messages), window_size):
            window_messages = self.messages[i: i + window_size]

            # Analyze emotions in this window
            emotions = defaultdict(float)
            total_weight = 0

            for msg in window_messages:
                if msg.role == MessageRole.USER and msg.sentiment is not None:
                    # Weight user messages more heavily
                    weight = 1.5
                    emotions["valence"] += msg.sentiment * weight
                    total_weight += weight

            if total_weight > 0:
                avg_valence = emotions["valence"] / total_weight

                # Determine primary emotion based on valence
                if avg_valence > 0.5:
                    primary = "happy"
                elif avg_valence > 0.2:
                    primary = "content"
                elif avg_valence < -0.5:
                    primary = "sad"
                elif avg_valence < -0.2:
                    primary = "frustrated"
                else:
                    primary = "neutral"

                state = EmotionalState(
                    primary_emotion=primary,
                    confidence=0.8,
                    valence=avg_valence,
                    arousal=0.5,  # Would need more analysis
                    emotions={primary: abs(avg_valence)},
                )

                emotional_states.append(state)

        self.emotional_states = emotional_states
        return emotional_states

    def calculate_engagement_score(self) -> float:
        """Calculate user engagement score"""
        if not self.messages:
            return 0.0

        factors = []

        # Response rate
        if self.turn_taking.assistant_turns > 0:
            response_rate = (
                self.turn_taking.user_turns / self.turn_taking.assistant_turns
            )
            factors.append(min(response_rate, 1.0))

        # Message length consistency
        user_messages = [
            m for m in self.messages if m.role == MessageRole.USER]
        if len(user_messages) > 1:
            lengths = [m.get_word_count() for m in user_messages]
            avg_length = statistics.mean(lengths)
            if avg_length > 5:  # More than just "yes/no" answers
                factors.append(min(avg_length / 20, 1.0))

        # Question asking
        if self.metrics.total_messages > 0:
            question_rate = self.metrics.questions_asked / self.metrics.total_messages
            factors.append(question_rate * 2)  # Weight questions highly

        # Topic diversity
        if len(self.topics) > 0:
            topic_score = min(len(self.topics) / 5, 1.0)
            factors.append(topic_score)

        # Calculate final score
        if factors:
            self.metrics.engagement_score = statistics.mean(factors)
        else:
            self.metrics.engagement_score = 0.0

        return self.metrics.engagement_score

    def calculate_educational_score(self) -> float:
        """Calculate educational value score"""
        edu_factors = []

        # Check for educational topics
        edu_topics = ["education", "science", "math", "learning", "history"]
        edu_topic_count = sum(
            1 for topic in self.topics if topic in edu_topics)
        if self.topics:
            edu_factors.append(edu_topic_count / len(self.topics))

        # Check for learning-related keywords
        learning_keywords = [
            "learn",
            "understand",
            "know",
            "discover",
            "explore",
            "why",
            "how",
        ]
        all_text = " ".join([m.content.lower() for m in self.messages])
        keyword_count = sum(
            1 for keyword in learning_keywords if keyword in all_text)
        edu_factors.append(min(keyword_count / 10, 1.0))

        # Check for educational content in metadata
        edu_content_count = sum(
            1 for m in self.messages if m.metadata.educational_content is not None
        )
        if self.messages:
            edu_factors.append(edu_content_count / len(self.messages))

        # Calculate final score
        if edu_factors:
            self.educational_score = statistics.mean(edu_factors)
        else:
            self.educational_score = 0.0

        return self.educational_score

    def calculate_quality_score(self) -> float:
        """Calculate overall conversation quality score"""
        quality_factors = []

        # Engagement
        quality_factors.append(self.calculate_engagement_score())

        # Educational value
        quality_factors.append(
            self.calculate_educational_score() * 0.8
        )  # Weight slightly less

        # Safety
        quality_factors.append(self.safety_score)

        # Emotional positivity
        positive_emotions = sum(
            1 for state in self.emotional_states if state.valence > 0.2
        )
        if self.emotional_states:
            emotion_score = positive_emotions / len(self.emotional_states)
            quality_factors.append(emotion_score)

        # Response quality (no very short responses)
        assistant_messages = [
            m for m in self.messages if m.role == MessageRole.ASSISTANT
        ]
        if assistant_messages:
            good_responses = sum(
                1 for m in assistant_messages if m.get_word_count() > 10
            )
            response_quality = good_responses / len(assistant_messages)
            quality_factors.append(response_quality)

        # Calculate final score
        if quality_factors:
            self.quality_score = statistics.mean(quality_factors)
        else:
            self.quality_score = 0.0

        return self.quality_score

    def get_transcript(self, include_timestamps: bool = False) -> str:
        """Get conversation transcript"""
        transcript_lines = []

        for msg in self.messages:
            if msg.role in [MessageRole.USER, MessageRole.ASSISTANT]:
                if include_timestamps:
                    line = f"[{msg.timestamp.strftime('%H:%M:%S')}] {msg.role.value}: {msg.content}"
                else:
                    line = f"{msg.role.value}: {msg.content}"
                transcript_lines.append(line)

        return "\n".join(transcript_lines)

    def to_dict(self) -> Dict[str, Any]:
        """Convert conversation to dictionary"""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "child_id": self.child_id,
            "messages": [msg.dict() for msg in self.messages],
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": str(self.duration),
            "interaction_type": self.interaction_type.value,
            "topics": self.topics,
            "emotional_states": [state.dict() for state in self.emotional_states],
            "turn_taking": self.turn_taking.dict(),
            "metrics": self.metrics.dict(),
            "safety_score": self.safety_score,
            "quality_score": self.quality_score,
            "educational_score": self.educational_score,
            "llm_provider": self.llm_provider,
            "voice_profile": self.voice_profile,
            "language": self.language,
            "summary": self.summary.dict() if self.summary else None,
            "parent_visible": self.parent_visible,
            "parent_notes": self.parent_notes,
        }

    def generate_hash(self) -> str:
        """Generate a hash of the conversation for deduplication"""
        content = "".join([f"{m.role}:{m.content}" for m in self.messages])
        return hashlib.sha256(content.encode()).hexdigest()

    class Config:
        """Pydantic configuration"""

        json_encoders = {datetime: lambda v: v.isoformat(),
                         timedelta: lambda v: str(v)}
