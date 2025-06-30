"""
User Domain Models
=================

Domain models for parent users, child profiles, and conversation log entries.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy import Column, String, Integer, DateTime, JSON, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid

Base = declarative_base()


class ParentUser(Base):
    """Parent user domain entity with business logic"""
    __tablename__ = 'parent_users'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    phone = Column(String)
    timezone = Column(String, default='UTC')
    notification_preferences = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True)

    # Relationships
    children = relationship("ChildProfile", back_populates="parent")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.notification_preferences:
            self.notification_preferences = self.get_default_notification_settings()
    
    @staticmethod
    def get_default_notification_settings() -> Dict[str, Any]:
        """Get default notification preferences"""
        return {
            'email': True,
            'sms': False,
            'push': True,
            'daily_summary': True,
            'weekly_report': True,
            'alerts': {
                'content_moderation': True,
                'time_limits': True,
                'unusual_activity': True,
                'emergency': True
            }
        }
    
    def update_last_login(self) -> None:
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()
    
    def wants_notification(self, notification_type: str) -> bool:
        """Check if parent wants specific notification type"""
        return self.notification_preferences.get(notification_type, False)
    
    def get_active_children(self) -> List['ChildProfile']:
        """Get list of active children"""
        return [child for child in self.children if child.is_active]
    
    def has_emergency_contacts(self) -> bool:
        """Check if parent has emergency contacts configured"""
        return bool(self.phone) or bool(self.email)
    
    def validate_email_format(self) -> bool:
        """Validate email format (simplified)"""
        return '@' in self.email and '.' in self.email.split('@')[1]


class ChildProfile(Base):
    """Enhanced child profile domain entity"""
    __tablename__ = 'child_profiles'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    parent_id = Column(String, ForeignKey('parent_users.id'), nullable=False)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    interests = Column(JSON, default=list)
    learning_level = Column(String)
    language_preference = Column(String, default='en')
    avatar_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Parental controls as JSON
    parental_controls = Column(JSON, default=dict)

    # Relationships
    parent = relationship("ParentUser", back_populates="children")
    conversation_logs = relationship("ConversationLogEntry", back_populates="child")

    def get_age_group(self) -> str:
        """Get age group classification"""
        if self.age < 5:
            return "preschool"
        elif self.age < 8:
            return "early_elementary"
        elif self.age < 11:
            return "elementary"
        elif self.age < 14:
            return "middle_school"
        else:
            return "high_school"
    
    def get_recommended_daily_limit(self) -> int:
        """Get recommended daily time limit based on age"""
        age_limits = {
            range(0, 5): 30,
            range(5, 8): 45,
            range(8, 11): 60,
            range(11, 14): 90,
            range(14, 18): 120
        }
        
        for age_range, limit in age_limits.items():
            if self.age in age_range:
                return limit
        return 60  # Default
    
    def is_topic_age_appropriate(self, topic: str) -> bool:
        """Check if topic is age-appropriate"""
        age_inappropriate = {
            range(0, 8): ['dating', 'politics', 'complex_science'],
            range(0, 11): ['dating', 'adult_relationships'],
            range(0, 14): ['adult_content']
        }
        
        for age_range, blocked_topics in age_inappropriate.items():
            if self.age in age_range and topic in blocked_topics:
                return False
        return True
    
    def update_interests(self, new_interests: List[str]) -> None:
        """Update child's interests with validation"""
        # Filter age-appropriate interests
        appropriate_interests = [
            interest for interest in new_interests
            if self.is_topic_age_appropriate(interest)
        ]
        self.interests = appropriate_interests
    
    def get_personalization_data(self) -> Dict[str, Any]:
        """Get data for personalizing interactions"""
        return {
            'name': self.name,
            'age': self.age,
            'age_group': self.get_age_group(),
            'interests': self.interests,
            'learning_level': self.learning_level,
            'language': self.language_preference
        }


class ConversationLogEntry(Base):
    """Database model for conversation logs with business logic"""
    __tablename__ = 'conversation_logs'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    child_id = Column(String, ForeignKey('child_profiles.id'), nullable=False)
    session_id = Column(String)
    started_at = Column(DateTime, nullable=False)
    ended_at = Column(DateTime)
    duration_seconds = Column(Integer, default=0)
    message_count = Column(Integer, default=0)
    topics = Column(JSON, default=list)
    sentiment_scores = Column(JSON, default=dict)
    moderation_flags = Column(JSON, default=list)
    transcript = Column(JSON, default=list)
    audio_url = Column(String)
    summary = Column(String)
    quality_score = Column(Integer)  # 0-100

    # Relationships
    child = relationship("ChildProfile", back_populates="conversation_logs")

    def calculate_duration(self) -> None:
        """Calculate and set duration if end time is available"""
        if self.ended_at and self.started_at:
            self.duration_seconds = int(
                (self.ended_at - self.started_at).total_seconds()
            )
    
    def get_duration_minutes(self) -> float:
        """Get duration in minutes"""
        return self.duration_seconds / 60.0 if self.duration_seconds else 0.0
    
    def is_long_session(self) -> bool:
        """Check if this was a long conversation session"""
        return self.get_duration_minutes() > 30
    
    def get_dominant_topic(self) -> Optional[str]:
        """Get the most discussed topic"""
        if not self.topics:
            return None
        # In a real implementation, this might analyze frequency
        return self.topics[0] if self.topics else None
    
    def has_concerning_content(self) -> bool:
        """Check if conversation had concerning content"""
        concerning_flags = {
            'inappropriate_content', 'emotional_distress', 
            'safety_concern', 'bullying', 'violence'
        }
        return bool(set(self.moderation_flags) & concerning_flags)
    
    def get_sentiment_summary(self) -> str:
        """Get human-readable sentiment summary"""
        if not self.sentiment_scores:
            return "neutral"
        
        dominant = max(self.sentiment_scores.items(), key=lambda x: x[1])
        return f"{dominant[0]} ({dominant[1]:.1%})"
    
    def needs_parent_attention(self) -> bool:
        """Check if this conversation needs parent attention"""
        return (
            self.has_concerning_content() or
            self.sentiment_scores.get('negative', 0) > 0.7 or
            self.is_long_session()
        )
    
    def generate_summary_if_needed(self) -> None:
        """Generate summary if not already present"""
        if not self.summary and self.transcript:
            # Simple summary generation
            topics_str = ", ".join(self.topics) if self.topics else "various topics"
            self.summary = (
                f"Conversation lasting {self.get_duration_minutes():.1f} minutes "
                f"with {self.message_count} messages about {topics_str}"
            ) 