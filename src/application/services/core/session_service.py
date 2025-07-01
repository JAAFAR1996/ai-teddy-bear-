"""
Dashboard Session Service
========================

Application service for managing conversation sessions and real-time tracking.
"""

import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from src.domain.parentdashboard.models.analytics_models import ConversationLog
from src.domain.parentdashboard.services.access_control_service import \
    AccessControlService
from src.domain.parentdashboard.services.content_analysis_service import \
    ContentAnalysisService


class DashboardSessionService:
    """Application service for session management"""

    def __init__(
        self,
        content_service: ContentAnalysisService,
        access_service: AccessControlService,
    ):
        self.content_service = content_service
        self.access_service = access_service
        self.logger = logging.getLogger(self.__class__.__name__)

        # In-memory session tracking (would use Redis in production)
        self.active_sessions: Dict[str, Dict] = {}
        self.usage_tracker: Dict[str, List[Dict]] = defaultdict(list)

    async def start_session(
        self, child_id: str, session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Start a new conversation session"""

        try:
            if not session_id:
                session_id = f"session_{child_id}_{int(datetime.now().timestamp())}"

            session_data = {
                "session_id": session_id,
                "child_id": child_id,
                "started_at": datetime.now(),
                "messages": [],
                "topics": set(),
                "last_activity": datetime.now(),
            }

            self.active_sessions[session_id] = session_data

            self.logger.info(f"Started session {session_id} for child {child_id}")

            return {
                "session_id": session_id,
                "started_at": session_data["started_at"].isoformat(),
                "status": "active",
            }

        except Exception as e:
            self.logger.error(f"Error starting session: {e}")
            return {"error": str(e)}

    async def log_interaction(
        self,
        session_id: str,
        child_message: str,
        assistant_message: str,
        audio_url: Optional[str] = None,
    ) -> bool:
        """Log a conversation interaction"""

        try:
            if session_id not in self.active_sessions:
                self.logger.warning(f"Session {session_id} not found")
                return False

            session = self.active_sessions[session_id]
            timestamp = datetime.now()

            # Add message to session
            interaction = {
                "timestamp": timestamp.isoformat(),
                "child": child_message,
                "assistant": assistant_message,
                "audio_url": audio_url,
            }

            session["messages"].append(interaction)
            session["last_activity"] = timestamp

            # Extract topics from conversation
            combined_text = f"{child_message} {assistant_message}"
            topics = self.content_service.extract_topics_from_text(combined_text)
            session["topics"].update(topics)

            # Update usage tracker
            self.usage_tracker[session["child_id"]].append(
                {
                    "timestamp": timestamp,
                    "session_id": session_id,
                    "duration": 1,
                }  # Will be updated on session end
            )

            return True

        except Exception as e:
            self.logger.error(f"Error logging interaction: {e}")
            return False

    async def end_session(self, session_id: str) -> Optional[ConversationLog]:
        """End a conversation session and create log"""

        try:
            if session_id not in self.active_sessions:
                self.logger.warning(f"Session {session_id} not found")
                return None

            session = self.active_sessions[session_id]
            ended_at = datetime.now()

            # Calculate session metrics
            duration_seconds = int((ended_at - session["started_at"]).total_seconds())
            message_count = len(session["messages"])

            # Analyze sentiment (simplified)
            sentiment_scores = {"positive": 0.7, "neutral": 0.2, "negative": 0.1}

            # Create conversation log
            conversation_log = ConversationLog(
                id=f"log_{session_id}",
                child_id=session["child_id"],
                session_id=session_id,
                timestamp=session["started_at"],
                duration_seconds=duration_seconds,
                message_count=message_count,
                topics_discussed=list(session["topics"]),
                sentiment_scores=sentiment_scores,
                moderation_flags=[],  # Would be populated by content analysis
                transcript=session["messages"],
            )

            # Update usage tracker
            for entry in self.usage_tracker[session["child_id"]]:
                if entry["session_id"] == session_id:
                    entry["duration"] = duration_seconds

            # Remove from active sessions
            del self.active_sessions[session_id]

            self.logger.info(
                f"Ended session {session_id}, duration: {duration_seconds}s"
            )

            return conversation_log

        except Exception as e:
            self.logger.error(f"Error ending session: {e}")
            return None

    async def get_active_sessions(
        self, child_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get currently active sessions"""

        active = []

        for session_id, session in self.active_sessions.items():
            if child_id is None or session["child_id"] == child_id:
                duration = int((datetime.now() - session["started_at"]).total_seconds())

                active.append(
                    {
                        "session_id": session_id,
                        "child_id": session["child_id"],
                        "started_at": session["started_at"].isoformat(),
                        "duration_seconds": duration,
                        "message_count": len(session["messages"]),
                        "current_topics": list(session["topics"]),
                        "last_activity": session["last_activity"].isoformat(),
                    }
                )

        return active

    async def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific session"""

        if session_id not in self.active_sessions:
            return None

        session = self.active_sessions[session_id]
        duration = int((datetime.now() - session["started_at"]).total_seconds())

        return {
            "session_id": session_id,
            "child_id": session["child_id"],
            "is_active": True,
            "started_at": session["started_at"].isoformat(),
            "duration_seconds": duration,
            "message_count": len(session["messages"]),
            "topics": list(session["topics"]),
            "last_activity": session["last_activity"].isoformat(),
        }

    async def get_usage_stats(
        self, child_id: str, period_hours: int = 24
    ) -> Dict[str, Any]:
        """Get usage statistics for a child"""

        cutoff_time = datetime.now() - timedelta(hours=period_hours)

        # Filter recent usage
        recent_usage = [
            entry
            for entry in self.usage_tracker[child_id]
            if entry["timestamp"] >= cutoff_time
        ]

        if not recent_usage:
            return {
                "total_sessions": 0,
                "total_minutes": 0,
                "average_session_minutes": 0,
                "period_hours": period_hours,
            }

        total_duration = sum(entry["duration"] for entry in recent_usage)
        unique_sessions = len(set(entry["session_id"] for entry in recent_usage))

        return {
            "total_sessions": unique_sessions,
            "total_minutes": total_duration / 60,
            "average_session_minutes": (
                (total_duration / unique_sessions / 60) if unique_sessions > 0 else 0
            ),
            "period_hours": period_hours,
            "sessions": recent_usage,
        }

    def cleanup_expired_sessions(self, max_idle_hours: int = 2) -> int:
        """Clean up expired/idle sessions"""

        cutoff_time = datetime.now() - timedelta(hours=max_idle_hours)
        expired_sessions = []

        for session_id, session in self.active_sessions.items():
            if session["last_activity"] < cutoff_time:
                expired_sessions.append(session_id)

        # Remove expired sessions
        for session_id in expired_sessions:
            del self.active_sessions[session_id]
            self.logger.info(f"Cleaned up expired session: {session_id}")

        return len(expired_sessions)
