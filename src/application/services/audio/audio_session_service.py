"""Audio session management service for AI Teddy Bear."""

import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from ....domain.audio.models import (
    AudioQualityMode,
    AudioSession,
    AudioSessionType,
    AudioSystemConfig,
    PerformanceMetrics,
)


class AudioSessionService:
    """Specialized service for audio session management."""

    def __init__(self, config: AudioSystemConfig, metrics: PerformanceMetrics):
        """Initialize audio session service."""
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.metrics = metrics

        # Session storage
        self.active_sessions: Dict[str, AudioSession] = {}
        self.current_session: Optional[AudioSession] = None
        self._session_lock = threading.Lock()

        # Session callbacks
        self.session_callbacks = {"session_start": [], "session_end": [], "session_timeout": []}

    def start_session(
        self,
        child_id: str,
        session_type: AudioSessionType = AudioSessionType.CONVERSATION,
        quality_mode: AudioQualityMode = AudioQualityMode.BALANCED,
    ) -> str:
        """
        Start a new audio session.

        Args:
            child_id: Child identifier
            session_type: Type of audio session
            quality_mode: Audio quality mode

        Returns:
            Session ID
        """
        try:
            with self._session_lock:
                # Check concurrent session limit
                if len(self.active_sessions) >= self.config.max_concurrent_sessions:
                    # End oldest session
                    self._end_oldest_session()

                # Create new session
                session_id = f"session_{child_id}_{int(time.time())}"
                session = AudioSession(
                    session_id=session_id,
                    session_type=session_type,
                    child_id=child_id,
                    start_time=datetime.now(),
                    quality_mode=quality_mode,
                )

                self.active_sessions[session_id] = session
                self.current_session = session

                # Update metrics
                self.metrics.start_session()

                # Trigger callbacks
                self._trigger_callback(
                    "session_start",
                    {
                        "session_id": session_id,
                        "child_id": child_id,
                        "session_type": session_type.value,
                        "quality_mode": quality_mode.value,
                    },
                )

                self.logger.info(f"Started audio session {session_id} for child {child_id}")
                return session_id

        except Exception as e:
            self.logger.error(f"Error starting session: {e}")
            raise

    def end_session(self, session_id: str) -> bool:
        """
        End an audio session.

        Args:
            session_id: Session to end

        Returns:
            Success status
        """
        try:
            with self._session_lock:
                if session_id not in self.active_sessions:
                    self.logger.warning(f"Session {session_id} not found")
                    return False

                session = self.active_sessions[session_id]
                session.end_time = datetime.now()

                # Save session data if configured
                if self.config.auto_save_sessions:
                    self._save_session_data(session)

                # Update metrics
                self.metrics.complete_session()

                # Remove from active sessions
                del self.active_sessions[session_id]

                # Update current session
                if self.current_session and self.current_session.session_id == session_id:
                    self.current_session = None

                # Trigger callbacks
                self._trigger_callback(
                    "session_end",
                    {
                        "session_id": session_id,
                        "duration": session.duration_seconds,
                        "recordings": session.total_recordings,
                    },
                )

                self.logger.info(f"Ended audio session {session_id}")
                return True

        except Exception as e:
            self.logger.error(f"Error ending session: {e}")
            return False

    def get_session(self, session_id: str) -> Optional[AudioSession]:
        """Get session by ID."""
        return self.active_sessions.get(session_id)

    def get_current_session(self) -> Optional[AudioSession]:
        """Get current active session."""
        return self.current_session

    def get_active_sessions(self) -> List[AudioSession]:
        """Get all active sessions."""
        return list(self.active_sessions.values())

    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed session information.

        Args:
            session_id: Session identifier

        Returns:
            Session information dictionary or None
        """
        session = self.active_sessions.get(session_id)
        if not session:
            return None

        return {
            "session_id": session.session_id,
            "session_type": session.session_type.value,
            "child_id": session.child_id,
            "start_time": session.start_time.isoformat(),
            "duration": session.duration_seconds,
            "total_recordings": session.total_recordings,
            "total_duration": session.total_duration,
            "quality_mode": session.quality_mode.value,
            "is_active": session.is_active,
            "metadata": session.metadata,
        }

    def check_session_timeouts(self) -> List[str]:
        """
        Check for and handle session timeouts.

        Returns:
            List of timed out session IDs
        """
        timed_out_sessions = []
        timeout_duration = timedelta(minutes=self.config.session_timeout_minutes)
        current_time = datetime.now()

        with self._session_lock:
            for session_id, session in list(self.active_sessions.items()):
                if current_time - session.start_time > timeout_duration:
                    self.logger.info(f"Session {session_id} timed out")

                    # Trigger timeout callback
                    self._trigger_callback(
                        "session_timeout", {"session_id": session_id, "duration": session.duration_seconds}
                    )

                    # End the session
                    self.end_session(session_id)
                    timed_out_sessions.append(session_id)

        return timed_out_sessions

    def update_session_quality(self, session_id: str, quality_mode: AudioQualityMode) -> bool:
        """Update session quality mode."""
        session = self.active_sessions.get(session_id)
        if not session:
            return False

        session.quality_mode = quality_mode
        session.metadata["quality_updated"] = datetime.now().isoformat()

        self.logger.info(f"Updated session {session_id} quality to {quality_mode.value}")
        return True

    def add_session_metadata(self, session_id: str, key: str, value: Any) -> bool:
        """Add metadata to session."""
        session = self.active_sessions.get(session_id)
        if not session:
            return False

        session.metadata[key] = value
        return True

    def get_session_statistics(self) -> Dict[str, Any]:
        """Get session management statistics."""
        active_count = len(self.active_sessions)
        session_types = {}
        total_duration = 0.0
        total_recordings = 0

        for session in self.active_sessions.values():
            session_type = session.session_type.value
            session_types[session_type] = session_types.get(session_type, 0) + 1
            total_duration += session.duration_seconds
            total_recordings += session.total_recordings

        return {
            "active_sessions": active_count,
            "max_concurrent": self.config.max_concurrent_sessions,
            "session_types": session_types,
            "total_active_duration": total_duration,
            "total_recordings": total_recordings,
            "timeout_minutes": self.config.session_timeout_minutes,
            "current_session_id": self.current_session.session_id if self.current_session else None,
        }

    def cleanup_old_sessions(self) -> int:
        """Clean up old session data and return count of cleaned sessions."""
        # This would implement cleanup of persisted session data
        # For now, just check for timeouts
        timed_out = self.check_session_timeouts()
        return len(timed_out)

    def _end_oldest_session(self) -> None:
        """End the oldest active session."""
        if not self.active_sessions:
            return

        oldest_session_id = min(self.active_sessions.keys(), key=lambda sid: self.active_sessions[sid].start_time)

        self.logger.info(f"Ending oldest session {oldest_session_id} due to limit")
        self.end_session(oldest_session_id)

    def _save_session_data(self, session: AudioSession) -> None:
        """Save session data for persistence."""
        try:
            # This would implement actual session data persistence
            # For now, just log the session info
            session_data = session.to_dict()
            self.logger.info(f"Saving session data: {session_data}")

            # Could save to database, file, or other storage

        except Exception as e:
            self.logger.error(f"Error saving session data: {e}")

    def _trigger_callback(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Trigger session event callbacks."""
        for callback in self.session_callbacks.get(event_type, []):
            try:
                callback(event_data)
            except Exception as e:
                self.logger.error(f"Session callback error: {e}")

    def add_session_callback(self, event_type: str, callback: callable) -> None:
        """Add session event callback."""
        if event_type in self.session_callbacks:
            self.session_callbacks[event_type].append(callback)

    def remove_session_callback(self, event_type: str, callback: callable) -> None:
        """Remove session event callback."""
        if event_type in self.session_callbacks and callback in self.session_callbacks[event_type]:
            self.session_callbacks[event_type].remove(callback)

    def force_end_all_sessions(self) -> int:
        """Force end all active sessions."""
        session_ids = list(self.active_sessions.keys())
        count = 0

        for session_id in session_ids:
            if self.end_session(session_id):
                count += 1

        self.logger.info(f"Force ended {count} sessions")
        return count

    def get_child_sessions(self, child_id: str) -> List[AudioSession]:
        """Get all active sessions for a specific child."""
        return [session for session in self.active_sessions.values() if session.child_id == child_id]

    def switch_current_session(self, session_id: str) -> bool:
        """Switch to a different active session."""
        session = self.active_sessions.get(session_id)
        if not session:
            return False

        self.current_session = session
        self.logger.info(f"Switched to session {session_id}")
        return True
