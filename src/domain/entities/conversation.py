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
        default_factory=lambda: str(
            uuid.uuid4()),
        description="Unique message ID")
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
    topics: List[str] = Field(
        default_factory=list,
        description="Detected topics")
    entities: List[Dict[str, Any]] = Field(
        default_factory=list, description="Named entities"
    )

    @validator("content")
    def validate_content(cls, content, values) -> Any:
        """Validate message content"""
        # Remove potential XSS or injection attempts
        content = re.sub(
            r"<script[^>]*>.*?</script>",
            "",
            content,
            flags=re.DOTALL | re.IGNORECASE)
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
        default_factory=lambda: str(
            uuid.uuid4()),
        description="Unique conversation ID")
    session_id: str = Field(..., description="Session identifier")
    child_id: str = Field(..., description="ID of the child")

    # Messages
    messages: List[Message] = Field(
        default_factory=list, description="List of messages"
    )

    # Timing
    start_time: datetime = Field(
        default_factory=datetime.now,
        description="Start time")
    end_time: Optional[datetime] = Field(None, description="End time")
    duration: timedelta = Field(default=timedelta(), description="Duration")

    # Classification
    interaction_type: InteractionType = Field(
        default=InteractionType.CONVERSATION, description="Type of interaction"
    )

    # Analysis
    topics: List[str] = Field(
        default_factory=list,
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
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Safety score")
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
        self._update_metrics(message)

        # Update end time and duration
        self.end_time = datetime.now()
        self.duration = self.end_time - self.start_time

        return message

    def _update_metrics(self, message: Message) -> None:
        """Update conversation metrics with a new message."""
        self.metrics.total_messages += 1
        self._update_turn_taking_metrics(message)
        self._update_word_and_question_metrics(message)

        if message.metadata.moderation_flags:
            self.metrics.moderation_flags += 1

    def _update_turn_taking_metrics(self, message: Message) -> None:
        """Update turn-taking specific metrics."""
        if message.role == MessageRole.USER:
            self.turn_taking.user_turns += 1
            if len(self.messages) > 1:
                last_assistant_message = next(
                    (
                        m
                        for m in reversed(self.messages[:-1])
                        if m.role == MessageRole.ASSISTANT
                    ),
                    None,
                )
                if last_assistant_message:
                    self.turn_taking.response_times.append(
                        (message.timestamp - last_assistant_message.timestamp).total_seconds())
        elif message.role == MessageRole.ASSISTANT:
            self.turn_taking.assistant_turns += 1

    def _update_word_and_question_metrics(self, message: Message) -> None:
        """Update word count and question related metrics."""
        word_count = message.get_word_count()
        if word_count > 0:
            self.metrics.total_words += word_count
            all_words = " ".join(m.content for m in self.messages).lower()
            self.metrics.unique_words = len(set(all_words.split()))

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

    def get_messages_for_llm(
            self, include_system: bool = True) -> List[Dict[str, str]]:
        """Get messages formatted for LLM input"""
        return [
            m.to_llm_format()
            for m in self.messages
            if include_system or m.role != MessageRole.SYSTEM
        ]

    def extract_topics(self) -> List[str]:
        """Extract topics from conversation using keyword matching."""
        full_text = " ".join(
            m.content.lower()
            for m in self.messages
            if m.content_type == ContentType.TEXT
        )
        if not full_text:
            return []

        topic_keywords = self._get_topic_keywords()
        detected_topics = defaultdict(int)

        for topic, keywords in topic_keywords.items():
            for keyword in keywords:
                if re.search(r"\b" + re.escape(keyword) + r"\b", full_text):
                    detected_topics[topic] += 1

        if not detected_topics:
            return ["general"]

        # Sort by frequency and return top topics
        sorted_topics = sorted(
            detected_topics.items(), key=lambda item: item[1], reverse=True
        )
        self.topics = [topic for topic, count in sorted_topics]
        return self.topics

    def _get_topic_keywords(self) -> Dict[str, List[str]]:
        """Returns a dictionary of topic keywords for extraction."""
        return {
            "science": [
                "science",
                "space",
                "planet",
                "star",
                "animal",
                "nature",
                "dinosaur",
                "experiment",
            ],
            "art": ["art", "draw", "paint", "color", "music", "sing", "dance", "story"],
            "feelings": [
                "happy",
                "sad",
                "angry",
                "scared",
                "love",
                "friend",
                "feeling",
            ],
            "learning": [
                "learn",
                "school",
                "book",
                "read",
                "number",
                "letter",
                "teacher",
            ],
            "play": ["game", "play", "toy", "fun", "hide and seek"],
            "family": ["mom", "dad", "family", "brother", "sister", "home"],
            "food": ["eat", "food", "fruit", "vegetable", "hungry", "tasty"],
            "daily_routine": [
                "bedtime",
                "sleep",
                "morning",
                "night",
                "bath",
                "brush teeth",
            ],
        }

    def analyze_emotional_journey(self) -> List[EmotionalState]:
        """Analyze emotional progression and identify key moments."""
        if not self.emotional_states:
            return []

        significant_moments = []
        for i, state in enumerate(self.emotional_states):
            if i > 0:
                prev_state = self.emotional_states[i - 1]
                shift = self._calculate_emotional_shift(prev_state, state)
                if self._is_significant_emotional_moment(state, shift):
                    significant_moments.append(state)
            elif self._is_significant_emotional_moment(state):
                significant_moments.append(state)

        # This is a simplified analysis. A real implementation would be more complex.
        # For now, we just return the identified significant moments.
        return significant_moments

    def _calculate_emotional_shift(
        self, prev_state: EmotionalState, current_state: EmotionalState
    ) -> float:
        """Calculate the magnitude of emotional shift between two states."""
        return abs(current_state.valence - prev_state.valence) + abs(
            current_state.arousal - prev_state.arousal
        )

    def _is_significant_emotional_moment(
        self, state: EmotionalState, shift: Optional[float] = None
    ) -> bool:
        """Determines if an emotional state or shift is significant."""
        # Significant if strong negative emotion
        if state.valence < -0.5 and state.arousal > 0.6:
            return True
        # Significant if a large positive shift occurred
        if shift and shift > 0.8:
            return True
        return False

    def calculate_engagement_score(self) -> float:
        """Calculate overall engagement score from different metrics."""
        if not self.messages:
            return 0.0

        weights = {"interaction": 0.4, "turn_taking": 0.3, "questions": 0.3}

        interaction_score = self._calculate_interaction_score()
        turn_taking_score = self._calculate_turn_taking_score()
        question_score = self._calculate_question_score()

        final_score = (
            interaction_score * weights["interaction"]
            + turn_taking_score * weights["turn_taking"]
            + question_score * weights["questions"]
        )

        self.metrics.engagement_score = final_score
        return final_score

    def _calculate_interaction_score(self) -> float:
        """Calculate score based on interaction frequency and duration."""
        if self.duration.total_seconds() == 0:
            return 0.0

        messages_per_minute = len(self.messages) / \
            (self.duration.total_seconds() / 60)

        if messages_per_minute > 5:
            return 1.0
        elif messages_per_minute > 2:
            return 0.7
        else:
            return 0.4

    def _calculate_turn_taking_score(self) -> float:
        """Calculate score based on turn-taking balance."""
        total_turns = self.turn_taking.user_turns + self.turn_taking.assistant_turns
        if total_turns == 0:
            return 0.0

        balance = (1.0 - abs(self.turn_taking.user_turns -
                             self.turn_taking.assistant_turns) / total_turns)
        return balance

    def _calculate_question_score(self) -> float:
        """Calculate score based on questions asked."""
        if self.turn_taking.user_turns == 0:
            return 0.0

        questions_per_turn = self.metrics.questions_asked / self.turn_taking.user_turns

        if questions_per_turn > 0.5:
            return 1.0
        elif questions_per_turn > 0.2:
            return 0.7
        else:
            return 0.3

    def calculate_educational_score(self) -> float:
        """Calculate the educational score of the conversation."""
        if not self.messages:
            return 0.0

        weights = {"topics": 0.4, "content": 0.4, "inquiry": 0.2}

        topic_score = self._calculate_topic_diversity_score()
        content_score = self._calculate_content_quality_score()
        inquiry_score = self._calculate_inquiry_score()

        final_score = (
            topic_score * weights["topics"]
            + content_score * weights["content"]
            + inquiry_score * weights["inquiry"]
        )

        self.educational_score = final_score
        return final_score

    def _calculate_topic_diversity_score(self) -> float:
        """Calculate score based on the diversity of educational topics."""
        educational_topics = {"science", "learning", "art"}
        covered_topics = set(self.topics).intersection(educational_topics)

        if len(covered_topics) >= 3:
            return 1.0
        elif len(covered_topics) > 0:
            return 0.6
        else:
            return 0.1

    def _calculate_content_quality_score(self) -> float:
        """Calculate score based on explicit educational content markers."""
        educational_messages = sum(
            1 for m in self.messages if m.metadata.educational_content
        )
        if not self.messages:
            return 0.0

        return min(educational_messages / (len(self.messages) / 2), 1.0)

    def _calculate_inquiry_score(self) -> float:
        """Calculate score based on question-answer dynamics."""
        if self.metrics.questions_asked == 0:
            return 0.2  # Neutral score if no questions

        # A simple proxy for answered questions
        # A better implementation would track specific question-answer pairs
        answered_ratio = self.turn_taking.assistant_turns / self.metrics.questions_asked
        return min(answered_ratio, 1.0)

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

        json_encoders = {
            datetime: lambda v: v.isoformat(),
            timedelta: lambda v: str(v)}
