from datetime import datetime
from typing import Any, Dict, List, Optional


class SessionManagementService:
    """
    Dedicated service for session management operations.
    EXTRACTED CLASS to resolve Low Cohesion - Single Responsibility: Session Management
    """

    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.session_history: Dict[str, List[Dict]] = {}

    def create_session(self, session_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Create new session with validation"""
        if not session_id or not session_id.strip():
            raise ValueError("session_id cannot be empty")
        
        session = {
            'id': session_id,
            'user_id': user_id,
            'created_at': datetime.now(),
            'last_activity': datetime.now(),
            'status': 'active'
        }
        self.sessions[session_id] = session
        self.session_history[session_id] = []
        return session

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID with validation"""
        if not session_id:
            return None
        return self.sessions.get(session_id)

    def add_message(self, session_id: str, message_type: str, content: str, metadata: Optional[Dict] = None) -> None:
        """Add message to session history with validation"""
        if not session_id or not message_type or not content:
            return
            
        if session_id not in self.session_history:
            self.session_history[session_id] = []

        message = {
            'type': message_type,
            'content': content,
            'timestamp': datetime.now(),
            'metadata': metadata or {}
        }

        self.session_history[session_id].append(message)
        self._update_session_activity(session_id)

    def get_recent_messages(self, session_id: str, limit: int = 5) -> List[Dict]:
        """Get recent messages for a session"""
        if not session_id or session_id not in self.session_history:
            return []
        
        return self.session_history[session_id][-limit:]

    def end_session(self, session_id: str) -> None:
        """End session with cleanup"""
        if session_id in self.sessions:
            self.sessions[session_id]['ended_at'] = datetime.now()
            self.sessions[session_id]['status'] = 'ended'

    def cleanup_old_sessions(self, max_age_hours: int = 24) -> int:
        """Clean up old inactive sessions"""
        current_time = datetime.now()
        sessions_to_remove = []
        
        for session_id, session in self.sessions.items():
            last_activity = session.get('last_activity', session.get('created_at'))
            age_hours = (current_time - last_activity).total_seconds() / 3600
            
            if age_hours > max_age_hours:
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            self._remove_session(session_id)
        
        return len(sessions_to_remove)

    def get_session_stats(self) -> Dict[str, Any]:
        """Get comprehensive session statistics"""
        active_sessions = sum(1 for s in self.sessions.values() if s.get('status') == 'active')
        total_messages = sum(len(history) for history in self.session_history.values())
        
        return {
            "total_sessions": len(self.sessions),
            "active_sessions": active_sessions,
            "total_messages": total_messages,
            "sessions_with_history": len(self.session_history)
        }

    def _update_session_activity(self, session_id: str) -> None:
        """Update session last activity timestamp"""
        if session_id in self.sessions:
            self.sessions[session_id]['last_activity'] = datetime.now()

    def _remove_session(self, session_id: str) -> None:
        """Remove session and its history"""
        self.sessions.pop(session_id, None)
        self.session_history.pop(session_id, None) 