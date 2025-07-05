"""
💬 Conversation Session Service
High cohesion component for conversation session and interaction management
"""

import logging
from typing import Optional, Dict, Any
from .models import InteractionLogData


class ConversationSessionService:
    """
    Dedicated service for conversation session management.
    High cohesion: all methods work with sessions and interactions.
    """

    def __init__(
            self,
            session_service,
            content_analysis_service,
            cache_service):
        """Initialize conversation session service"""
        self.session_service = session_service
        self.content_analysis_service = content_analysis_service
        self.cache_service = cache_service
        self.logger = logging.getLogger(__name__)

    async def start_conversation_session(self, user_id: str) -> Dict[str, Any]:
        """Start a new conversation session for a child"""
        try:
            session_result = await self.session_service.start_session(user_id)

            self.logger.info(
                f"Started conversation session for user {user_id}")
            return session_result

        except Exception as e:
            self.logger.error(
                f"Failed to start session for user {user_id}: {e}")
            raise

    async def log_interaction(self, interaction_data: InteractionLogData):
        """
        Log a conversation interaction with validation and analysis.
        Handles session management and content analysis.
        """
        try:
            session_id = interaction_data.session_id

            # Start new session if needed
            if not session_id:
                session_result = await self.start_conversation_session(
                    interaction_data.user_id
                )
                session_id = session_result.get("session_id")
                interaction_data.session_id = session_id

            # Log the interaction
            log_result = await self.session_service.log_interaction(
                session_id,
                interaction_data.child_message,
                interaction_data.assistant_message,
                interaction_data.audio_url,
            )

            # Perform content analysis for safety
            await self._analyze_interaction_content(interaction_data)

            self.logger.info(
                f"Successfully logged interaction for session {session_id}"
            )

            return log_result

        except Exception as e:
            self.logger.error(
                f"Failed to log interaction for user {interaction_data.user_id}: {e}"
            )
            raise

    async def end_conversation_session(self, session_id: str):
        """End a conversation session and perform cleanup"""
        try:
            conversation_log = await self.session_service.end_session(session_id)

            if conversation_log:
                # Invalidate analytics cache since new data is available
                if hasattr(conversation_log, "child_id"):
                    self.cache_service.invalidate_child_cache(
                        conversation_log.child_id)

                # Process any conversation-level alerts
                await self._process_session_alerts(conversation_log)

                self.logger.info(f"Successfully ended session {session_id}")
            else:
                self.logger.warning(
                    f"No conversation log found for session {session_id}"
                )

            return conversation_log

        except Exception as e:
            self.logger.error(f"Failed to end session {session_id}: {e}")
            raise

    async def get_active_sessions(self, child_id: str) -> list:
        """Get active conversation sessions for a child"""
        try:
            active_sessions = await self.session_service.get_active_sessions(child_id)

            self.logger.debug(
                f"Found {len(active_sessions)} active sessions for child {child_id}"
            )
            return active_sessions

        except Exception as e:
            self.logger.error(
                f"Failed to get active sessions for child {child_id}: {e}"
            )
            return []

    async def get_session_history(
            self,
            child_id: str,
            limit: int = 50) -> list:
        """Get conversation session history for a child"""
        try:
            sessions = await self.session_service.get_session_history(child_id, limit)

            self.logger.debug(
                f"Retrieved {len(sessions)} sessions for child {child_id}"
            )
            return sessions

        except Exception as e:
            self.logger.error(
                f"Failed to get session history for child {child_id}: {e}"
            )
            return []

    async def get_session_details(
            self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific session"""
        try:
            session_details = await self.session_service.get_session_details(session_id)

            if session_details:
                self.logger.debug(
                    f"Retrieved details for session {session_id}")
            else:
                self.logger.warning(f"Session not found: {session_id}")

            return session_details

        except Exception as e:
            self.logger.error(
                f"Failed to get session details {session_id}: {e}")
            return None

    async def update_session_metadata(
        self, session_id: str, metadata: Dict[str, Any]
    ) -> bool:
        """Update session metadata (tags, notes, etc.)"""
        try:
            success = await self.session_service.update_session_metadata(
                session_id, metadata
            )

            if success:
                self.logger.info(
                    f"Successfully updated metadata for session {session_id}"
                )
            else:
                self.logger.warning(
                    f"Failed to update metadata for session {session_id}"
                )

            return success

        except Exception as e:
            self.logger.error(
                f"Error updating session metadata {session_id}: {e}")
            return False

    async def get_real_time_session_status(
            self, child_id: str) -> Dict[str, Any]:
        """Get real-time status for active sessions"""
        try:
            active_sessions = await self.get_active_sessions(child_id)

            if active_sessions:
                session = active_sessions[0]  # Most recent active session
                return {
                    "is_active": True,
                    "session_id": session.get("session_id"),
                    "session_duration": session.get("duration_seconds", 0),
                    "current_topics": session.get("current_topics", []),
                    "message_count": session.get("message_count", 0),
                    "last_activity": session.get("last_activity"),
                    "session_mood": session.get("session_mood", "neutral"),
                }

            return {
                "is_active": False,
                "session_duration": 0,
                "current_topics": [],
                "message_count": 0,
            }

        except Exception as e:
            self.logger.error(
                f"Failed to get real-time status for child {child_id}: {e}"
            )
            return {"is_active": False, "error": str(e)}

    async def _analyze_interaction_content(
            self, interaction_data: InteractionLogData):
        """Analyze interaction content for safety and quality"""
        try:
            # Analyze child message for safety concerns
            child_analysis = self.content_analysis_service.analyze_child_message(
                interaction_data.child_message, interaction_data.user_id)

            # Analyze assistant response for appropriateness
            assistant_analysis = (
                self.content_analysis_service.analyze_assistant_response(
                    interaction_data.assistant_message,
                    interaction_data.child_message))

            # Log any concerns
            if child_analysis.get("concerns"):
                self.logger.warning(
                    f"Content concerns detected in child message: "
                    f"{child_analysis['concerns']}"
                )

            if assistant_analysis.get("quality_score", 1.0) < 0.7:
                self.logger.warning(
                    f"Low quality assistant response detected: "
                    f"score {assistant_analysis['quality_score']}"
                )

        except Exception as e:
            self.logger.error(f"Failed to analyze interaction content: {e}")
            # Don't raise - content analysis failure shouldn't block logging

    async def _process_session_alerts(self, conversation_log):
        """Process any alerts that should be generated from the session"""
        try:
            # This would typically involve checking for patterns across the session
            # such as negative sentiment, inappropriate topics, etc.
            session_analysis = self.content_analysis_service.analyze_session_content(
                conversation_log)

            alerts_needed = session_analysis.get("alerts_needed", [])
            if alerts_needed:
                self.logger.info(
                    f"Session {conversation_log.session_id} generated "
                    f"{len(alerts_needed)} alerts"
                )
                # Alerts would be created by the AccessControlAlertsService

        except Exception as e:
            self.logger.error(f"Failed to process session alerts: {e}")
            # Don't raise - alert processing failure shouldn't block session
            # ending

    def get_session_stats(self) -> Dict[str, Any]:
        """Get conversation session statistics"""
        return {
            "service_name": "ConversationSessionService",
            "operations": [
                "start_conversation_session",
                "log_interaction",
                "end_conversation_session",
                "get_active_sessions",
                "get_session_history",
                "get_session_details",
                "update_session_metadata",
                "get_real_time_session_status",
            ],
            "high_cohesion": True,
            "responsibility": "Conversation session and interaction management",
        }
