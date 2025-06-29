from dataclasses import dataclass
from typing import Optional, List
from .base import Entity

@dataclass
class ChildProfile(Entity):
    """Child aggregate root - the main entity"""
    name: str
    age: int
    parent_id: str
    language_preference: str = "ar"
    safety_level: str = "high"
    active_sessions: List[str] = None
    
    def __post_init__(self):
        super().__init__()
        self.active_sessions = self.active_sessions or []
        
    def can_start_session(self) -> bool:
        """Business rule: max 1 active session per child"""
        return len(self.active_sessions) == 0
    
    def start_session(self, session_id: str):
        if not self.can_start_session():
            raise ValueError("Child already has an active session")
        self.active_sessions.append(session_id)
        self.add_domain_event({
            "type": "SessionStarted",
            "child_id": self.id,
            "session_id": session_id
        }) 