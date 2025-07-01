"""Child profile management service for ESP32 teddy bear."""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

import structlog

from ....domain.esp32.models import (ChildProfile, InteractionType, SessionData)

logger = structlog.get_logger(__name__)


class ChildProfileService:
    """Service for managing child profiles and session data."""

    def __init__(self, device_id: str):
        self.device_id = device_id
        self.current_profile: Optional[ChildProfile] = None
        self.profiles_cache: Dict[str, ChildProfile] = {}

        logger.info(" Child profile service initialized")

    def create_profile(self, name: str, age: int) -> ChildProfile:
        """Create new child profile."""
        try:
            child_id = f"child_{uuid.uuid4().hex[:8]}"

            profile = ChildProfile(
                name=name, age=age, child_id=child_id, device_id=self.device_id
            )

            self.profiles_cache[child_id] = profile
            self.current_profile = profile

            logger.info(f" Created profile for {name}, age {age}")
            return profile

        except Exception as e:
            logger.error(f" Profile creation failed: {e}")
            raise

    def load_profile(self, child_id: str) -> Optional[ChildProfile]:
        """Load existing child profile."""
        try:
            if child_id in self.profiles_cache:
                profile = self.profiles_cache[child_id]
                self.current_profile = profile
                logger.info(f" Loaded profile for {profile.name}")
                return profile
            else:
                logger.warning(f"Profile not found: {child_id}")
                return None

        except Exception as e:
            logger.error(f" Profile loading failed: {e}")
            return None

    def start_session(self) -> Optional[SessionData]:
        """Start new session for current profile."""
        try:
            if not self.current_profile:
                logger.error("No current profile to start session")
                return None

            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            self.current_profile.start_session(session_id)

            logger.info(f" Started session: {session_id}")
            return self.current_profile.current_session

        except Exception as e:
            logger.error(f" Session start failed: {e}")
            return None

    def end_session(self) -> None:
        """End current session."""
        try:
            if self.current_profile and self.current_profile.current_session:
                session_duration = self.current_profile.current_session.duration_minutes
                self.current_profile.end_session()
                logger.info(f" Ended session (duration: {session_duration} minutes)")
            else:
                logger.warning("No active session to end")

        except Exception as e:
            logger.error(f" Session end failed: {e}")

    def record_conversation(
        self,
        child_input: str,
        ai_response: str,
        interaction_type: InteractionType = InteractionType.CONVERSATION,
    ) -> bool:
        """Record conversation in current profile."""
        try:
            if not self.current_profile:
                logger.error("No current profile to record conversation")
                return False

            self.current_profile.add_conversation(
                child_input, ai_response, interaction_type
            )

            # Update session if active
            if self.current_profile.current_session:
                self.current_profile.current_session.record_interaction()

            logger.debug(f" Recorded conversation: {child_input[:30]}...")
            return True

        except Exception as e:
            logger.error(f" Conversation recording failed: {e}")
            return False

    def update_learning_progress(self, subject: str, points: int) -> bool:
        """Update learning progress for current profile."""
        try:
            if not self.current_profile:
                logger.error("No current profile to update learning")
                return False

            self.current_profile.update_learning_progress(subject, points)
            logger.info(f" Learning progress updated: {subject} +{points} points")
            return True

        except Exception as e:
            logger.error(f" Learning progress update failed: {e}")
            return False

    def add_favorite_activity(self, activity: str) -> bool:
        """Add activity to favorites for current profile."""
        try:
            if not self.current_profile:
                logger.error("No current profile to add favorite")
                return False

            self.current_profile.add_favorite_activity(activity)
            logger.info(f" Added favorite activity: {activity}")
            return True

        except Exception as e:
            logger.error(f" Add favorite activity failed: {e}")
            return False

    def get_profile_summary(self) -> Optional[Dict[str, Any]]:
        """Get summary of current profile."""
        try:
            if not self.current_profile:
                return None

            summary = {
                "basic_info": {
                    "name": self.current_profile.name,
                    "age": self.current_profile.age,
                    "child_id": self.current_profile.child_id,
                    "created_at": self.current_profile.created_at.isoformat(),
                    "last_seen": (
                        self.current_profile.last_seen.isoformat()
                        if self.current_profile.last_seen
                        else None
                    ),
                },
                "current_session": {
                    "is_active": self.current_profile.is_active_session,
                    "session_id": (
                        self.current_profile.current_session.session_id
                        if self.current_profile.current_session
                        else None
                    ),
                    "duration_minutes": (
                        self.current_profile.current_session.duration_minutes
                        if self.current_profile.current_session
                        else 0
                    ),
                    "interaction_count": (
                        self.current_profile.current_session.interaction_count
                        if self.current_profile.current_session
                        else 0
                    ),
                },
                "statistics": self.current_profile.interaction_summary,
                "preferences": {
                    "preferred_language": self.current_profile.preferred_language,
                    "volume_preference": self.current_profile.volume_preference,
                },
            }

            return summary

        except Exception as e:
            logger.error(f" Profile summary failed: {e}")
            return None

    def get_conversation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversation history."""
        try:
            if not self.current_profile:
                return []

            recent_conversations = self.current_profile.conversation_history[-limit:]

            history = []
            for conv in recent_conversations:
                history.append(
                    {
                        "timestamp": conv.timestamp.isoformat(),
                        "child_input": conv.child_input,
                        "ai_response": conv.ai_response,
                        "interaction_type": conv.interaction_type.value,
                        "confidence": conv.confidence,
                        "language": conv.language,
                        "duration_text": conv.duration_text,
                    }
                )

            return history

        except Exception as e:
            logger.error(f" Conversation history failed: {e}")
            return []

    def get_learning_progress(self) -> Dict[str, Any]:
        """Get learning progress for current profile."""
        try:
            if not self.current_profile:
                return {}

            progress = {}
            for subject, learning in self.current_profile.learning_progress.items():
                progress[subject] = {
                    "level": learning.level,
                    "points": learning.points,
                    "total_sessions": learning.total_sessions,
                    "achievements": learning.achievements,
                    "last_activity": (
                        learning.last_activity.isoformat()
                        if learning.last_activity
                        else None
                    ),
                }

            return progress

        except Exception as e:
            logger.error(f" Learning progress failed: {e}")
            return {}

    def update_preferences(self, **preferences) -> bool:
        """Update profile preferences."""
        try:
            if not self.current_profile:
                logger.error("No current profile to update preferences")
                return False

            if "language" in preferences:
                self.current_profile.preferred_language = preferences["language"]

            if "volume" in preferences:
                volume = preferences["volume"]
                if 0 <= volume <= 100:
                    self.current_profile.volume_preference = volume
                else:
                    raise ValueError("Volume must be between 0 and 100")

            logger.info(f" Updated preferences: {preferences}")
            return True

        except Exception as e:
            logger.error(f" Preferences update failed: {e}")
            return False

    def get_all_profiles(self) -> List[Dict[str, Any]]:
        """Get list of all cached profiles."""
        try:
            profiles = []
            for profile in self.profiles_cache.values():
                profiles.append(
                    {
                        "child_id": profile.child_id,
                        "name": profile.name,
                        "age": profile.age,
                        "total_conversations": profile.total_conversations,
                        "last_seen": (
                            profile.last_seen.isoformat() if profile.last_seen else None
                        ),
                        "is_current": profile == self.current_profile,
                    }
                )

            return profiles

        except Exception as e:
            logger.error(f" Get all profiles failed: {e}")
            return []

    def switch_profile(self, child_id: str) -> bool:
        """Switch to different profile."""
        try:
            if child_id in self.profiles_cache:
                # End current session if active
                if self.current_profile and self.current_profile.is_active_session:
                    self.end_session()

                # Switch profile
                self.current_profile = self.profiles_cache[child_id]
                logger.info(f" Switched to profile: {self.current_profile.name}")
                return True
            else:
                logger.error(f"Profile not found: {child_id}")
                return False

        except Exception as e:
            logger.error(f" Profile switch failed: {e}")
            return False

    def delete_profile(self, child_id: str) -> bool:
        """Delete a profile."""
        try:
            if child_id in self.profiles_cache:
                profile = self.profiles_cache[child_id]

                # End session if this is the current profile
                if self.current_profile == profile:
                    if profile.is_active_session:
                        self.end_session()
                    self.current_profile = None

                # Remove from cache
                del self.profiles_cache[child_id]

                logger.info(f" Deleted profile: {profile.name}")
                return True
            else:
                logger.error(f"Profile not found: {child_id}")
                return False

        except Exception as e:
            logger.error(f" Profile deletion failed: {e}")
            return False
