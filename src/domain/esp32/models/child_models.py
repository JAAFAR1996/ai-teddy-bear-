"""ESP32 child profile domain models."""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum


class InteractionType(Enum):
    """Types of child interactions."""
    CONVERSATION = "conversation"
    GAME = "game"
    STORY = "story"
    SONG = "song"
    LEARNING = "learning"
    EMOTION = "emotion"


@dataclass
class ConversationEntry:
    """Single conversation entry."""
    timestamp: datetime
    child_input: str
    ai_response: str
    interaction_type: InteractionType = InteractionType.CONVERSATION
    confidence: float = 1.0
    language: str = "ar-SA"
    
    @property
    def duration_text(self) -> str:
        """Get human-readable duration."""
        now = datetime.now()
        diff = now - self.timestamp
        
        if diff.seconds < 60:
            return "Just now"
        elif diff.seconds < 3600:
            return f"{diff.seconds // 60} minutes ago"
        else:
            return f"{diff.seconds // 3600} hours ago"


@dataclass
class LearningProgress:
    """Child learning progress tracking."""
    subject: str
    level: int = 1  # 1-10
    points: int = 0
    achievements: List[str] = None
    last_activity: Optional[datetime] = None
    total_sessions: int = 0
    
    def __post_init__(self):
        """Initialize achievements if not provided."""
        if self.achievements is None:
            self.achievements = []
    
    def add_points(self, points: int) -> None:
        """Add learning points."""
        self.points += points
        self.last_activity = datetime.now()
        
        # Level up logic
        points_for_next_level = self.level * 100
        if self.points >= points_for_next_level:
            self.level += 1
            self.achievements.append(f"Reached level {self.level} in {self.subject}")
    
    def complete_session(self) -> None:
        """Mark session as completed."""
        self.total_sessions += 1
        self.last_activity = datetime.now()


@dataclass
class SessionData:
    """Current session information."""
    session_id: str
    started_at: datetime
    device_id: str
    child_id: Optional[str] = None
    interaction_count: int = 0
    last_interaction: Optional[datetime] = None
    
    @property
    def duration_minutes(self) -> int:
        """Get session duration in minutes."""
        now = datetime.now()
        return int((now - self.started_at).total_seconds() / 60)
    
    @property
    def is_active(self) -> bool:
        """Check if session is still active."""
        if self.last_interaction is None:
            return False
        
        now = datetime.now()
        return (now - self.last_interaction).total_seconds() < 300  # 5 minutes timeout
    
    def record_interaction(self) -> None:
        """Record new interaction."""
        self.interaction_count += 1
        self.last_interaction = datetime.now()


@dataclass
class ChildProfile:
    """Complete child profile."""
    name: str
    age: int
    child_id: str
    device_id: str
    created_at: datetime = None
    last_seen: Optional[datetime] = None
    
    # Conversations
    conversation_history: List[ConversationEntry] = None
    total_conversations: int = 0
    
    # Learning
    learning_progress: Dict[str, LearningProgress] = None
    favorite_activities: List[str] = None
    
    # Current session
    current_session: Optional[SessionData] = None
    
    # Preferences
    preferred_language: str = "ar-SA"
    volume_preference: int = 50
    
    def __post_init__(self):
        """Initialize default values."""
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.conversation_history is None:
            self.conversation_history = []
        if self.learning_progress is None:
            self.learning_progress = {}
        if self.favorite_activities is None:
            self.favorite_activities = []
    
    @property
    def is_active_session(self) -> bool:
        """Check if child has active session."""
        return (
            self.current_session is not None and
            self.current_session.is_active
        )
    
    @property
    def interaction_summary(self) -> Dict[str, Any]:
        """Get interaction summary."""
        today_conversations = [
            conv for conv in self.conversation_history
            if conv.timestamp.date() == datetime.now().date()
        ]
        
        return {
            "total_conversations": self.total_conversations,
            "today_conversations": len(today_conversations),
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
            "session_duration": self.current_session.duration_minutes if self.current_session else 0,
            "learning_subjects": list(self.learning_progress.keys()),
            "favorite_activities": self.favorite_activities[:3]  # Top 3
        }
    
    def add_conversation(self, child_input: str, ai_response: str, interaction_type: InteractionType = InteractionType.CONVERSATION) -> None:
        """Add new conversation entry."""
        entry = ConversationEntry(
            timestamp=datetime.now(),
            child_input=child_input,
            ai_response=ai_response,
            interaction_type=interaction_type,
            language=self.preferred_language
        )
        
        self.conversation_history.append(entry)
        self.total_conversations += 1
        self.last_seen = datetime.now()
        
        # Keep only last 100 conversations to prevent memory issues
        if len(self.conversation_history) > 100:
            self.conversation_history = self.conversation_history[-100:]
    
    def start_session(self, session_id: str) -> None:
        """Start new session."""
        self.current_session = SessionData(
            session_id=session_id,
            started_at=datetime.now(),
            device_id=self.device_id,
            child_id=self.child_id
        )
    
    def end_session(self) -> None:
        """End current session."""
        if self.current_session:
            self.last_seen = datetime.now()
            self.current_session = None
    
    def update_learning_progress(self, subject: str, points: int) -> None:
        """Update learning progress for subject."""
        if subject not in self.learning_progress:
            self.learning_progress[subject] = LearningProgress(subject=subject)
        
        self.learning_progress[subject].add_points(points)
        self.learning_progress[subject].complete_session()
    
    def add_favorite_activity(self, activity: str) -> None:
        """Add activity to favorites."""
        if activity not in self.favorite_activities:
            self.favorite_activities.append(activity)
            
        # Move to front if already exists
        elif activity in self.favorite_activities:
            self.favorite_activities.remove(activity)
            self.favorite_activities.insert(0, activity)
        
        # Keep only top 10 favorites
        self.favorite_activities = self.favorite_activities[:10]
