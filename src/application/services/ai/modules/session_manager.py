#!/usr/bin/env python3
"""
Session Manager Module - Extracted from main_service.py
Handles all session-related logic for AI Teddy Bear
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from src.domain.entities.child import Child


@dataclass
class SessionContext:
    """Enhanced session context with full tracking"""

    child_id: str
    session_id: str
    start_time: datetime
    interactions: List[Dict] = field(default_factory=list)
    emotions: List["EmotionResult"] = field(default_factory=list)
    current_activity: Optional["ActivityType"] = None
    language_preference: str = "en"
    voice_preference: str = "default"
    metadata: Dict = field(default_factory=dict)

    @property
    def duration(self) -> timedelta:
        return datetime.utcnow() - self.start_time

    @property
    def interaction_count(self) -> int:
        return len(self.interactions)

    def get_emotion_summary(self) -> Dict:
        """Get summary of emotions during session"""
        if not self.emotions:
            return {}

        emotion_counts = {}
        for emotion in self.emotions:
            emotion_counts[emotion.primary_emotion] = (
                emotion_counts.get(emotion.primary_emotion, 0) + 1
            )

        return {
            "dominant": max(emotion_counts, key=emotion_counts.get),
            "distribution": emotion_counts,
            "average_valence": sum(e.valence for e in self.emotions)
            / len(self.emotions),
            "average_arousal": sum(e.arousal for e in self.emotions)
            / len(self.emotions),
        }


class SessionManager:
    """Manages user sessions for AI Teddy Bear interactions"""

    def __init__(self, redis_client=None, session_repository=None):
        self.active_sessions: Dict[str, SessionContext] = {}
        self.redis_client = redis_client
        self.session_repository = session_repository

    async def create_session(
        self, child_id: str, metadata: Optional[Dict] = None
    ) -> SessionContext:
        """Create a new session for a child"""
        session_id = str(uuid.uuid4())

        session = SessionContext(
            child_id=child_id,
            session_id=session_id,
            start_time=datetime.utcnow(),
            metadata=metadata or {},
        )

        # Store in memory
        self.active_sessions[session_id] = session

        # Store in Redis if available
        if self.redis_client:
            await self._store_session_in_redis(session)

        return session

    async def get_session(self, session_id: str) -> Optional[SessionContext]:
        """Get an active session by ID"""
        # Check memory first
        if session_id in self.active_sessions:
            return self.active_sessions[session_id]

        # Try Redis if not in memory
        if self.redis_client:
            return await self._load_session_from_redis(session_id)

        return None

    async def update_session(self, session: SessionContext) -> None:
        """Update session data"""
        self.active_sessions[session.session_id] = session

        if self.redis_client:
            await self._store_session_in_redis(session)

    async def end_session(self, session_id: str) -> Optional[SessionContext]:
        """End a session and return final state"""
        session = self.active_sessions.pop(session_id, None)

        if session and self.redis_client:
            await self._remove_session_from_redis(session_id)

        return session

    async def add_interaction(
            self,
            session_id: str,
            interaction: Dict) -> None:
        """Add interaction to session history"""
        session = await self.get_session(session_id)
        if session:
            session.interactions.append(interaction)
            await self.update_session(session)

    async def get_active_sessions_count(self) -> int:
        """Get count of active sessions"""
        return len(self.active_sessions)

    async def cleanup_old_sessions(self, max_age_hours: int = 24) -> int:
        """Clean up sessions older than max_age_hours"""
        current_time = datetime.utcnow()
        cleaned_count = 0

        for session_id in list(self.active_sessions.keys()):
            session = self.active_sessions[session_id]
            age = current_time - session.start_time

            if age.total_seconds() > max_age_hours * 3600:
                await self.end_session(session_id)
                cleaned_count += 1

        return cleaned_count

    # Redis integration methods
    async def _store_session_in_redis(self, session: SessionContext) -> None:
        """Store session in Redis"""
        # Implementation depends on redis client
        pass

    async def _load_session_from_redis(
        self, session_id: str
    ) -> Optional[SessionContext]:
        """Load session from Redis"""
        # Implementation depends on redis client
        return None

    async def _remove_session_from_redis(self, session_id: str) -> None:
        """Remove session from Redis"""
        # Implementation depends on redis client
        pass
