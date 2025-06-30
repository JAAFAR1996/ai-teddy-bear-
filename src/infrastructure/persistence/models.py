from typing import Dict, List, Any, Optional

import logging

logger = logging.getLogger(__name__)

#!/usr/bin/env python3
"""
SQLAlchemy Models for AI Teddy Bear Project
Includes Child, Conversation, Message, and related entities with optimized relationships and indexes
"""

from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
import json
import uuid

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Date, Text, 
    ForeignKey, Index, CheckConstraint, UniqueConstraint, Table
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, validates, Session
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import func
from sqlalchemy.event import listens_for

Base = declarative_base()


class TimestampMixin:
    """Mixin to add created_at and updated_at timestamps"""
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class UUIDMixin:
    """Mixin to add UUID primary key"""
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))


# Association table for child interests (many-to-many)
child_interests_table = Table(
    'child_interests',
    Base.metadata,
    Column('child_id', String(36), ForeignKey('children.id'), primary_key=True),
    Column('interest_id', String(36), ForeignKey('interests.id'), primary_key=True)
)


class Interest(Base, UUIDMixin, TimestampMixin):
    """Interest entity for many-to-many relationship with children"""
    __tablename__ = 'interests'
    
    name = Column(String(100), nullable=False, unique=True)
    category = Column(String(50))
    description = Column(Text)
    age_range_min = Column(Integer, default=3)
    age_range_max = Column(Integer, default=18)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_interest_name', 'name'),
        Index('idx_interest_category', 'category'),
        Index('idx_interest_age_range', 'age_range_min', 'age_range_max'),
    )


class Child(Base, UUIDMixin, TimestampMixin):
    """Enhanced Child model with comprehensive profile management"""
    __tablename__ = 'children'
    
    # Basic Information
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    date_of_birth = Column(Date)
    gender = Column(String(20))
    
    # Profile & Preferences
    personality_traits = Column(JSON, default=list)  # ['curious', 'shy', 'energetic']
    learning_preferences = Column(JSON, default=dict)  # {'visual': 0.8, 'auditory': 0.6}
    communication_style = Column(String(50), default='friendly')  # 'formal', 'casual', 'playful'
    
    # Time & Interaction Management
    max_daily_interaction_time = Column(Integer, default=3600)  # seconds
    total_interaction_time = Column(Integer, default=0)  # cumulative seconds
    last_interaction = Column(DateTime)
    daily_interaction_reset = Column(Date, default=date.today)
    
    # Content & Safety
    allowed_topics = Column(JSON, default=list)
    restricted_topics = Column(JSON, default=list)
    content_rating = Column(String(10), default='E')  # 'E', 'E10+', 'T'
    
    # Language & Culture
    language_preference = Column(String(10), default='en')
    cultural_background = Column(String(100))
    secondary_languages = Column(JSON, default=list)
    
    # Parental Controls & Safety
    parental_controls = Column(JSON, default=dict)
    emergency_contacts = Column(JSON, default=list)
    medical_notes = Column(Text)
    special_needs = Column(JSON, default=list)
    
    # Educational Profile
    educational_level = Column(String(50))
    learning_goals = Column(JSON, default=list)
    achievement_badges = Column(JSON, default=list)
    progress_metrics = Column(JSON, default=dict)
    
    # Status & Settings
    is_active = Column(Boolean, default=True, nullable=False)
    privacy_settings = Column(JSON, default=dict)
    custom_settings = Column(JSON, default=dict)
    
    # Parent Information
    parent_id = Column(String(36), ForeignKey('parents.id'))
    family_code = Column(String(20))  # For family grouping
    
    # Relationships
    parent = relationship("Parent", back_populates="children")
    conversations = relationship("Conversation", back_populates="child", cascade="all, delete-orphan")
    interests = relationship("Interest", secondary=child_interests_table, back_populates="children")
    learning_sessions = relationship("LearningSession", back_populates="child")
    emotion_profiles = relationship("EmotionProfile", back_populates="child")
    
    # Validation
    @validates('age')
    def validate_age(self, key, age) -> Any:
        if age < 3 or age > 18:
            raise ValueError("Age must be between 3 and 18")
        return age
    
    @validates('max_daily_interaction_time')
    def validate_interaction_time(self, key, time) -> Any:
        if time < 300 or time > 14400:  # 5 minutes to 4 hours
            raise ValueError("Daily interaction time must be between 5 minutes and 4 hours")
        return time
    
    # Hybrid properties for calculated fields
    @hybrid_property
    def daily_time_remaining(self) -> Any:
        """Calculate remaining interaction time for today"""
        if self.daily_interaction_reset != date.today():
            return self.max_daily_interaction_time
        return max(0, self.max_daily_interaction_time - self.total_interaction_time)
    
    @hybrid_property
    def interaction_streak_days(self) -> Any:
        """Calculate consecutive days of interaction"""
        if not self.last_interaction:
            return 0
        days_since = (datetime.utcnow() - self.last_interaction).days
        return max(0, 7 - days_since)  # Example calculation
    
    # Indexes and constraints
    __table_args__ = (
        Index('idx_child_name', 'name'),
        Index('idx_child_age', 'age'),
        Index('idx_child_active', 'is_active'),
        Index('idx_child_parent', 'parent_id'),
        Index('idx_child_family', 'family_code'),
        Index('idx_child_language', 'language_preference'),
        Index('idx_child_last_interaction', 'last_interaction'),
        CheckConstraint('age >= 3 AND age <= 18', name='check_age_range'),
        CheckConstraint('max_daily_interaction_time >= 300', name='check_min_interaction_time'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'gender': self.gender,
            'personality_traits': self.personality_traits,
            'learning_preferences': self.learning_preferences,
            'communication_style': self.communication_style,
            'language_preference': self.language_preference,
            'cultural_background': self.cultural_background,
            'is_active': self.is_active,
            'daily_time_remaining': self.daily_time_remaining,
            'interaction_streak_days': self.interaction_streak_days,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Parent(Base, UUIDMixin, TimestampMixin):
    """Parent/Guardian model"""
    __tablename__ = 'parents'
    
    email = Column(String(255), unique=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone_number = Column(String(20))
    
    # Preferences
    notification_preferences = Column(JSON, default=dict)
    dashboard_settings = Column(JSON, default=dict)
    privacy_settings = Column(JSON, default=dict)
    
    # Status
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    children = relationship("Child", back_populates="parent")
    
    # Indexes
    __table_args__ = (
        Index('idx_parent_email', 'email'),
        Index('idx_parent_active', 'is_active'),
    )


class Conversation(Base, UUIDMixin, TimestampMixin):
    """Enhanced Conversation model with comprehensive tracking"""
    __tablename__ = 'conversations'
    
    # Identifiers
    session_id = Column(String(100))
    child_id = Column(String(36), ForeignKey('children.id'), nullable=False)
    parent_id = Column(String(36), ForeignKey('parents.id'))
    
    # Timing
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    duration_seconds = Column(Integer, default=0)
    
    # Classification
    interaction_type = Column(String(50), default='general')  # 'educational', 'play', 'emotional_support'
    topics = Column(JSON, default=list)
    primary_language = Column(String(10), default='en')
    
    # Quality Metrics
    quality_score = Column(Float, default=0.0)  # 0.0 - 1.0
    safety_score = Column(Float, default=1.0)   # 0.0 - 1.0
    educational_score = Column(Float, default=0.0)  # 0.0 - 1.0
    engagement_score = Column(Float, default=0.0)   # 0.0 - 1.0
    
    # Technical Details
    llm_provider = Column(String(50))  # 'openai', 'anthropic', 'local'
    model_version = Column(String(50))
    context_window_size = Column(Integer)
    
    # Content Summary
    context_summary = Column(Text)
    key_insights = Column(JSON, default=list)
    learning_outcomes = Column(JSON, default=list)
    
    # Metadata
    metadata = Column(JSON, default=dict)
    
    # Message Statistics
    total_messages = Column(Integer, default=0)
    child_messages = Column(Integer, default=0)
    assistant_messages = Column(Integer, default=0)
    questions_asked = Column(Integer, default=0)
    
    # Moderation & Safety
    moderation_flags = Column(Integer, default=0)
    safety_interventions = Column(JSON, default=list)
    
    # Visibility & Archival
    parent_visible = Column(Boolean, default=True)
    archived = Column(Boolean, default=False)
    archive_reason = Column(String(100))
    
    # Relationships
    child = relationship("Child", back_populates="conversations")
    parent = relationship("Parent")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    emotional_states = relationship("EmotionalState", back_populates="conversation", cascade="all, delete-orphan")
    
    # Hybrid properties
    @hybrid_property
    def duration_minutes(self) -> Any:
        """Duration in minutes"""
        return self.duration_seconds / 60 if self.duration_seconds else 0
    
    @hybrid_property
    def average_response_time(self) -> Any:
        """Calculate average response time from messages"""
        # This would be calculated from message timestamps
        return 2.5  # Placeholder
    
    @hybrid_property
    def dominant_emotion(self) -> Any:
        """Get the most frequent emotion from emotional states"""
        if not self.emotional_states:
            return 'neutral'
        emotions = [state.primary_emotion for state in self.emotional_states]
        return max(set(emotions), key=emotions.count) if emotions else 'neutral'
    
    # Indexes and constraints
    __table_args__ = (
        Index('idx_conversation_child', 'child_id'),
        Index('idx_conversation_session', 'session_id'),
        Index('idx_conversation_start_time', 'start_time'),
        Index('idx_conversation_type', 'interaction_type'),
        Index('idx_conversation_archived', 'archived'),
        Index('idx_conversation_parent_visible', 'parent_visible'),
        Index('idx_conversation_safety_score', 'safety_score'),
        CheckConstraint('quality_score >= 0.0 AND quality_score <= 1.0', name='check_quality_score'),
        CheckConstraint('safety_score >= 0.0 AND safety_score <= 1.0', name='check_safety_score'),
    )


class Message(Base, UUIDMixin, TimestampMixin):
    """Individual message within a conversation"""
    __tablename__ = 'messages'
    
    conversation_id = Column(String(36), ForeignKey('conversations.id'), nullable=False)
    
    # Content
    role = Column(String(20), nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    content_type = Column(String(20), default='text')  # 'text', 'audio', 'image'
    
    # Ordering
    sequence_number = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Processing
    tokens_used = Column(Integer, default=0)
    processing_time_ms = Column(Integer, default=0)
    
    # Metadata & Analysis
    metadata = Column(JSON, default=dict)
    sentiment_score = Column(Float, default=0.0)  # -1.0 to 1.0
    confidence_score = Column(Float, default=0.0)  # 0.0 to 1.0
    
    # Moderation
    moderation_flags = Column(JSON, default=list)
    is_flagged = Column(Boolean, default=False)
    
    # Embedding for semantic search (stored as JSON for SQLite compatibility)
    embedding_vector = Column(JSON)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    
    # Indexes
    __table_args__ = (
        Index('idx_message_conversation', 'conversation_id'),
        Index('idx_message_role', 'role'),
        Index('idx_message_timestamp', 'timestamp'),
        Index('idx_message_sequence', 'conversation_id', 'sequence_number'),
        Index('idx_message_flagged', 'is_flagged'),
        UniqueConstraint('conversation_id', 'sequence_number', name='uq_conversation_sequence'),
    )


class EmotionalState(Base, UUIDMixin, TimestampMixin):
    """Emotional state tracking within conversations"""
    __tablename__ = 'emotional_states'
    
    conversation_id = Column(String(36), ForeignKey('conversations.id'), nullable=False)
    
    # Primary emotion detection
    primary_emotion = Column(String(50), nullable=False)
    confidence = Column(Float, default=0.0)  # 0.0 to 1.0
    
    # Secondary emotions
    secondary_emotions = Column(JSON, default=list)  # [{'emotion': 'happy', 'confidence': 0.3}]
    
    # Emotion dimensions
    arousal_level = Column(Float, default=0.0)  # -1.0 (calm) to 1.0 (excited)
    valence_level = Column(Float, default=0.0)  # -1.0 (negative) to 1.0 (positive)
    dominance_level = Column(Float, default=0.0)  # -1.0 (submissive) to 1.0 (dominant)
    
    # Context
    emotional_context = Column(Text)
    trigger_words = Column(JSON, default=list)
    
    # Analysis metadata
    analysis_method = Column(String(50))  # 'hume', 'local', 'hybrid'
    raw_analysis_data = Column(JSON, default=dict)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="emotional_states")
    
    # Indexes
    __table_args__ = (
        Index('idx_emotion_conversation', 'conversation_id'),
        Index('idx_emotion_primary', 'primary_emotion'),
        Index('idx_emotion_confidence', 'confidence'),
        Index('idx_emotion_valence', 'valence_level'),
        Index('idx_emotion_timestamp', 'created_at'),
    )


class LearningSession(Base, UUIDMixin, TimestampMixin):
    """Educational learning session tracking"""
    __tablename__ = 'learning_sessions'
    
    child_id = Column(String(36), ForeignKey('children.id'), nullable=False)
    conversation_id = Column(String(36), ForeignKey('conversations.id'))
    
    # Session details
    subject = Column(String(100), nullable=False)
    topic = Column(String(200))
    difficulty_level = Column(String(20))  # 'beginner', 'intermediate', 'advanced'
    
    # Duration and progress
    duration_minutes = Column(Integer, default=0)
    completion_percentage = Column(Float, default=0.0)
    
    # Performance metrics
    questions_attempted = Column(Integer, default=0)
    questions_correct = Column(Integer, default=0)
    hints_used = Column(Integer, default=0)
    
    # Outcomes
    learning_objectives_met = Column(JSON, default=list)
    knowledge_gained = Column(JSON, default=list)
    areas_for_improvement = Column(JSON, default=list)
    
    # Relationships
    child = relationship("Child", back_populates="learning_sessions")
    conversation = relationship("Conversation")
    
    # Indexes
    __table_args__ = (
        Index('idx_learning_child', 'child_id'),
        Index('idx_learning_subject', 'subject'),
        Index('idx_learning_date', 'created_at'),
    )


class EmotionProfile(Base, UUIDMixin, TimestampMixin):
    """Long-term emotional profile for children"""
    __tablename__ = 'emotion_profiles'
    
    child_id = Column(String(36), ForeignKey('children.id'), nullable=False)
    
    # Profile period
    profile_date = Column(Date, default=date.today)
    profile_type = Column(String(20), default='daily')  # 'daily', 'weekly', 'monthly'
    
    # Dominant emotions
    dominant_emotions = Column(JSON, default=list)  # [{'emotion': 'happy', 'percentage': 65}]
    
    # Emotional patterns
    emotional_stability = Column(Float, default=0.0)  # 0.0 to 1.0
    emotional_range = Column(Float, default=0.0)      # 0.0 to 1.0
    mood_swings_count = Column(Integer, default=0)
    
    # Triggers and contexts
    positive_triggers = Column(JSON, default=list)
    negative_triggers = Column(JSON, default=list)
    emotional_contexts = Column(JSON, default=dict)
    
    # Recommendations
    support_recommendations = Column(JSON, default=list)
    intervention_needed = Column(Boolean, default=False)
    
    # Relationships
    child = relationship("Child", back_populates="emotion_profiles")
    
    # Indexes
    __table_args__ = (
        Index('idx_emotion_profile_child', 'child_id'),
        Index('idx_emotion_profile_date', 'profile_date'),
        Index('idx_emotion_profile_type', 'profile_type'),
        UniqueConstraint('child_id', 'profile_date', 'profile_type', name='uq_child_profile_date'),
    )


# Relationship setup for many-to-many
Interest.children = relationship("Child", secondary=child_interests_table, back_populates="interests")


# Event listeners for automatic updates

@listens_for(Child, 'before_update')
def child_before_update(mapper, connection, target) -> Any:
    """Update child's daily interaction reset if date changed"""
    if target.daily_interaction_reset != date.today():
        target.total_interaction_time = 0
        target.daily_interaction_reset = date.today()


@listens_for(Conversation, 'before_update')
def conversation_before_update(mapper, connection, target) -> Any:
    """Calculate conversation duration when end_time is set"""
    if target.end_time and target.start_time:
        duration = target.end_time - target.start_time
        target.duration_seconds = int(duration.total_seconds())


@listens_for(Message, 'after_insert')
def message_after_insert(mapper, connection, target) -> Any:
    """Update conversation statistics when message is added"""
    # This would be implemented with direct SQL for performance
    pass


# Database initialization function
def create_tables(engine) -> Any:
    """Create all tables with indexes and constraints"""
    Base.metadata.create_all(engine)


def get_session_factory(engine) -> Any:
    """Get SQLAlchemy session factory"""
    from sqlalchemy.orm import sessionmaker
    return sessionmaker(bind=engine)


# Example usage and validation
if __name__ == "__main__":
    from sqlalchemy import create_engine
    
    # Create in-memory SQLite database for testing
    engine = create_engine('sqlite:///:memory:', echo=True)
    create_tables(engine)
    
    SessionFactory = get_session_factory(engine)
    session = SessionFactory()
    
    # Example data creation
    parent = Parent(
        email="parent@example.com",
        first_name="John",
        last_name="Doe"
    )
    session.add(parent)
    session.flush()  # Get parent ID
    
    child = Child(
        name="Alice",
        age=8,
        date_of_birth=date(2015, 5, 15),
        parent_id=parent.id,
        personality_traits=['curious', 'creative'],
        learning_preferences={'visual': 0.8, 'auditory': 0.6}
    )
    session.add(child)
    session.commit()
    
    logger.info(f"Created child: {child.to_dict()}")
    
    session.close() 