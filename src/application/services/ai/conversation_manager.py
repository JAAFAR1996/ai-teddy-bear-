"""
Conversation Manager
Handles conversation context and history
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

import structlog
from opentelemetry import trace

from src.application.services.core.service_registry import ServiceBase
from src.infrastructure.observability import trace_async

logger = structlog.get_logger()


@dataclass
class ConversationContext:
    """Enhanced conversation context"""

    child_id: str
    session_id: str
    conversation_history: List[Dict[str, str]] = field(default_factory=list)
    current_topic: Optional[str] = None
    mood_history: List[str] = field(default_factory=list)
    topics_discussed: List[str] = field(default_factory=list)
    learning_goals: List[str] = field(default_factory=list)
    time_of_day: str = "afternoon"
    interaction_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class ConversationManager(ServiceBase):
    """
    Manages conversation context and history
    """

    def __init__(self, registry, config: Dict):
        super().__init__(registry, config)
        self._tracer = trace.get_tracer(__name__)
        self._max_history_length = config.get("max_conversation_history", 20)

    async def initialize(self) -> None:
        """Initialize the conversation manager"""
        self.logger.info("Initializing conversation manager")

        # Get session manager from registry
        self.session_manager = await self.wait_for_service("session_manager")
        self.memory_service = await self.wait_for_service("memory")

        self._state = self.ServiceState.READY

    async def shutdown(self) -> None:
        """Shutdown the manager"""
        self._state = self.ServiceState.STOPPED

    async def health_check(self) -> Dict:
        """Health check"""
        return {
            "healthy": self._state == self.ServiceState.READY,
            "service": "conversation_manager",
        }

    @trace_async("get_conversation_context")
    async def get_context(self, session_id: str) -> ConversationContext:
        """Get or create conversation context for a session"""
        # Get from Redis first
        session = await self.session_manager.get_session(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        # Build context from session data
        context = ConversationContext(
            child_id=session.child_id,
            session_id=session_id,
            conversation_history=session.data.get("conversation_history", []),
            current_topic=session.data.get("current_topic"),
            mood_history=session.data.get("mood_history", []),
            topics_discussed=session.data.get("topics_discussed", []),
            learning_goals=session.data.get("learning_goals", []),
            time_of_day=self._get_time_of_day(),
            interaction_count=session.data.get("interaction_count", 0),
            metadata=session.metadata,
        )

        return context

    @trace_async("update_conversation")
    async def update_conversation(
        self,
        session_id: str,
        user_message: str,
        ai_response: str,
        emotion: Optional[str] = None,
        topic: Optional[str] = None,
    ) -> None:
        """Update conversation history and context"""
        context = await self.get_context(session_id)

        # Update conversation history
        self._update_conversation_history(context, user_message, ai_response)

        # Update context metadata
        self._update_context_metadata(context, emotion, topic)

        # Persist all updates
        await self._persist_conversation_updates(
            context, session_id, user_message, ai_response, emotion, topic
        )

    def _update_conversation_history(
        self, context: ConversationContext, user_message: str, ai_response: str
    ) -> None:
        """Update conversation history with new messages"""
        # Add to history
        context.conversation_history.append(
            {
                "role": "user",
                "content": user_message,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        context.conversation_history.append(
            {
                "role": "assistant",
                "content": ai_response,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        # Trim history if too long
        if len(context.conversation_history) > self._max_history_length:
            context.conversation_history = context.conversation_history[
                -self._max_history_length :
            ]

    def _update_context_metadata(
        self, context: ConversationContext, emotion: Optional[str], topic: Optional[str]
    ) -> None:
        """Update context metadata including mood, topic, and interaction count"""
        # Update mood history
        if emotion:
            context.mood_history.append(emotion)
            if len(context.mood_history) > 10:
                context.mood_history = context.mood_history[-10:]

        # Update topic
        if topic:
            context.current_topic = topic
            if topic not in context.topics_discussed:
                context.topics_discussed.append(topic)

        # Increment interaction count
        context.interaction_count += 1

    async def _persist_conversation_updates(
        self,
        context: ConversationContext,
        session_id: str,
        user_message: str,
        ai_response: str,
        emotion: Optional[str],
        topic: Optional[str],
    ) -> None:
        """Persist conversation updates to session manager and memory service"""
        # Save to session
        await self.session_manager.update_session(
            session_id,
            data={
                "conversation_history": context.conversation_history,
                "current_topic": context.current_topic,
                "mood_history": context.mood_history,
                "topics_discussed": context.topics_discussed,
                "interaction_count": context.interaction_count,
            },
        )

        # Also update memory service
        await self.memory_service.add_to_conversation(
            session_id=session_id,
            child_id=context.child_id,
            user_message=user_message,
            ai_response=ai_response,
            emotion=emotion,
            metadata={"topic": topic},
        )

    def _get_time_of_day(self) -> str:
        """Get current time of day"""
        hour = datetime.now().hour
        if 6 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 20:
            return "evening"
        else:
            return "night"

    async def get_recent_topics(self, session_id: str, limit: int = 5) -> List[str]:
        """Get recent topics discussed"""
        context = await self.get_context(session_id)
        return context.topics_discussed[-limit:] if context.topics_discussed else []

    async def get_mood_trend(self, session_id: str) -> Dict[str, Any]:
        """Analyze mood trend over conversation"""
        context = await self.get_context(session_id)

        if not context.mood_history:
            return {"trend": "neutral", "dominant_mood": None}

        # Count mood occurrences
        mood_counts = {}
        for mood in context.mood_history:
            mood_counts[mood] = mood_counts.get(mood, 0) + 1

        # Find dominant mood
        dominant_mood = max(mood_counts.items(), key=lambda x: x[1])[0]

        # Analyze trend (simple approach)
        recent_moods = (
            context.mood_history[-5:]
            if len(context.mood_history) > 5
            else context.mood_history
        )
        positive_moods = ["happy", "excited", "curious"]
        negative_moods = ["sad", "angry", "scared"]

        positive_count = sum(1 for m in recent_moods if m in positive_moods)
        negative_count = sum(1 for m in recent_moods if m in negative_moods)

        if positive_count > negative_count:
            trend = "positive"
        elif negative_count > positive_count:
            trend = "negative"
        else:
            trend = "neutral"

        return {
            "trend": trend,
            "dominant_mood": dominant_mood,
            "mood_counts": mood_counts,
            "recent_moods": recent_moods,
        }
