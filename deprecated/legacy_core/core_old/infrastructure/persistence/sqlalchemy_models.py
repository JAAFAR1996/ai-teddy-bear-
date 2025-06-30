#!/usr/bin/env python3
"""
SQLAlchemy Models for AI Teddy Bear Project
Comprehensive data models with relationships, constraints, and optimizations
"""

from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
import json
import uuid

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Date, Text, 
    ForeignKey, Index, CheckConstraint, UniqueConstraint, Table,
    create_engine, event
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, validates, Session, sessionmaker
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import func

Base = declarative_base()


class TimestampMixin:
    """Mixin for automatic timestamp management"""
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class UUIDMixin:
    """Mixin for UUID primary keys"""
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))


# Association table for many-to-many relationships
child_interests_table = Table(
    'child_interests',
    Base.metadata,
    Column('child_id', String(36), ForeignKey('children.id'), primary_key=True),
    Column('interest_id', String(36), ForeignKey('interests.id'), primary_key=True)
)


class Interest(Base, UUIDMixin, TimestampMixin):
    """Interest categories for children"""
    __tablename__ = 'interests'
    
    name = Column(String(100), nullable=False, unique=True)
    category = Column(String(50))
    description = Column(Text)
    age_range_min = Column(Integer, default=3)
    age_range_max = Column(Integer, default=18)
    
    __table_args__ = (
        Index('idx_interest_name', 'name'),
        Index('idx_interest_category', 'category'),
    )


class Child(Base, UUIDMixin, TimestampMixin):
    """Child profile with comprehensive tracking"""
    __tablename__ = 'children'
    
    # Core Information
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    date_of_birth = Column(Date)
    gender = Column(String(20))
    
    # Profile Data
    personality_traits = Column(JSON, default=list)
    learning_preferences = Column(JSON, default=dict)
    communication_style = Column(String(50), default='friendly')
    
    # Time Management
    max_daily_interaction_time = Column(Integer, default=3600)
    total_interaction_time = Column(Integer, default=0)
    last_interaction = Column(DateTime)
    
    # Content Control
    allowed_topics = Column(JSON, default=list)
    restricted_topics = Column(JSON, default=list)
    language_preference = Column(String(10), default='en')
    
    # Parental Information
    parent_id = Column(String(36), ForeignKey('parents.id'))
    parental_controls = Column(JSON, default=dict)
    emergency_contacts = Column(JSON, default=list)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    privacy_settings = Column(JSON, default=dict)
    custom_settings = Column(JSON, default=dict)
    
    # Relationships
    parent = relationship("Parent", back_populates="children")
    conversations = relationship("Conversation", back_populates="child")
    interests = relationship("Interest", secondary=child_interests_table)
    
    # Validation
    @validates('age')
    def validate_age(self, key, age):
        if age < 3 or age > 18:
            raise ValueError("Age must be between 3 and 18")
        return age
    
    # Hybrid properties
    @hybrid_property
    def daily_time_remaining(self):
        return max(0, self.max_daily_interaction_time - self.total_interaction_time)
    
    __table_args__ = (
        Index('idx_child_name', 'name'),
        Index('idx_child_age', 'age'), 
        Index('idx_child_active', 'is_active'),
        Index('idx_child_parent', 'parent_id'),
        CheckConstraint('age >= 3 AND age <= 18', name='check_age_range'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'gender': self.gender,
            'personality_traits': self.personality_traits,
            'communication_style': self.communication_style,
            'language_preference': self.language_preference,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Parent(Base, UUIDMixin, TimestampMixin):
    """Parent/Guardian profile"""
    __tablename__ = 'parents'
    
    email = Column(String(255), unique=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone_number = Column(String(20))
    
    # Settings
    notification_preferences = Column(JSON, default=dict)
    dashboard_settings = Column(JSON, default=dict)
    privacy_settings = Column(JSON, default=dict)
    
    # Status
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    children = relationship("Child", back_populates="parent")
    
    __table_args__ = (
        Index('idx_parent_email', 'email'),
    )


class Conversation(Base, UUIDMixin, TimestampMixin):
    """Conversation tracking with comprehensive metrics"""
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
    interaction_type = Column(String(50), default='general')
    topics = Column(JSON, default=list)
    primary_language = Column(String(10), default='en')
    
    # Quality Metrics
    quality_score = Column(Float, default=0.0)
    safety_score = Column(Float, default=1.0)
    educational_score = Column(Float, default=0.0)
    engagement_score = Column(Float, default=0.0)
    
    # Technical
    llm_provider = Column(String(50))
    model_version = Column(String(50))
    context_summary = Column(Text)
    metadata = Column(JSON, default=dict)
    
    # Statistics
    total_messages = Column(Integer, default=0)
    child_messages = Column(Integer, default=0)
    assistant_messages = Column(Integer, default=0)
    questions_asked = Column(Integer, default=0)
    moderation_flags = Column(Integer, default=0)
    
    # Status
    parent_visible = Column(Boolean, default=True)
    archived = Column(Boolean, default=False)
    
    # Relationships
    child = relationship("Child", back_populates="conversations")
    parent = relationship("Parent")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    emotional_states = relationship("EmotionalState", back_populates="conversation", cascade="all, delete-orphan")
    
    # Hybrid properties
    @hybrid_property
    def duration_minutes(self):
        return self.duration_seconds / 60 if self.duration_seconds else 0
    
    __table_args__ = (
        Index('idx_conversation_child', 'child_id'),
        Index('idx_conversation_session', 'session_id'),
        Index('idx_conversation_start_time', 'start_time'),
        Index('idx_conversation_archived', 'archived'),
        CheckConstraint('quality_score >= 0.0 AND quality_score <= 1.0', name='check_quality_score'),
    )


class Message(Base, UUIDMixin, TimestampMixin):
    """Individual message in conversations"""
    __tablename__ = 'messages'
    
    conversation_id = Column(String(36), ForeignKey('conversations.id'), nullable=False)
    
    # Content
    role = Column(String(20), nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    content_type = Column(String(20), default='text')
    
    # Ordering and timing
    sequence_number = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Analysis
    sentiment_score = Column(Float, default=0.0)
    confidence_score = Column(Float, default=0.0)
    metadata = Column(JSON, default=dict)
    
    # Moderation
    moderation_flags = Column(JSON, default=list)
    is_flagged = Column(Boolean, default=False)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    
    __table_args__ = (
        Index('idx_message_conversation', 'conversation_id'),
        Index('idx_message_timestamp', 'timestamp'),
        Index('idx_message_sequence', 'conversation_id', 'sequence_number'),
        UniqueConstraint('conversation_id', 'sequence_number', name='uq_conversation_sequence'),
    )


class EmotionalState(Base, UUIDMixin, TimestampMixin):
    """Emotional state tracking"""
    __tablename__ = 'emotional_states'
    
    conversation_id = Column(String(36), ForeignKey('conversations.id'), nullable=False)
    
    # Emotion data
    primary_emotion = Column(String(50), nullable=False)
    confidence = Column(Float, default=0.0)
    secondary_emotions = Column(JSON, default=list)
    
    # Dimensions
    arousal_level = Column(Float, default=0.0)
    valence_level = Column(Float, default=0.0)
    
    # Context
    emotional_context = Column(Text)
    analysis_method = Column(String(50))
    
    # Relationships
    conversation = relationship("Conversation", back_populates="emotional_states")
    
    __table_args__ = (
        Index('idx_emotion_conversation', 'conversation_id'),
        Index('idx_emotion_primary', 'primary_emotion'),
        Index('idx_emotion_timestamp', 'created_at'),
    )


# Database initialization
def create_database_engine(database_url: str = "sqlite:///data/teddyai.db"):
    """Create SQLAlchemy engine"""
    engine = create_engine(database_url, echo=False)
    return engine


def create_tables(engine):
    """Create all tables"""
    Base.metadata.create_all(engine)


def get_session_factory(engine):
    """Get session factory"""
    return sessionmaker(bind=engine)


# Example usage
if __name__ == "__main__":
    engine = create_database_engine("sqlite:///test.db")
    create_tables(engine)
    print("Database tables created successfully!") 