# parent_dashboard_service.py - Enhanced parent dashboard with comprehensive features
import os
import asyncio
import logging
from typing import Dict, Any, Optional, List
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime, timedelta, time
from dataclasses import dataclass, field
from enum import Enum
import redis
import json
import uuid
from collections import defaultdict
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from io import BytesIO
import base64
from sqlalchemy import Column, String, Float, DateTime, Integer, JSON, Boolean, ForeignKey, Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import redis.asyncio as aioredis
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import aiosmtplib
from jinja2 import Template
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.domain.entities.child import Child
from src.domain.repositories.child_repository import ChildRepository
from src.domain.entities.conversation import Conversation, Message
from src.domain.repositories.conversation_repository import ConversationRepository
from src.infrastructure.config import get_config


Base = declarative_base()


class AlertType(Enum):
    """Types of parent alerts"""
    CONTENT_MODERATION = "content_moderation"
    TIME_LIMIT_WARNING = "time_limit_warning"
    TIME_LIMIT_EXCEEDED = "time_limit_exceeded"
    UNUSUAL_ACTIVITY = "unusual_activity"
    MILESTONE_REACHED = "milestone_reached"
    DAILY_SUMMARY = "daily_summary"
    WEEKLY_REPORT = "weekly_report"
    EMERGENCY = "emergency"

# Simple cache implementations


class InMemoryCache:
    """Simple in-memory cache implementation"""

    def __init__(self):
        self._cache = {}

    def get(self, key: str) -> Any:
        return self._cache.get(key)

    def set(self, key -> Any: str, value -> Any: Any, ttl -> Any: Optional[int] = None) -> Any:
        self._cache[key] = value

    def delete(self, key -> Any: str) -> Any:
        self._cache.pop(key, None)

    def clear(self) -> Any:
        self._cache.clear()


class RedisCache:
    def __init__(self, redis_url: str):
        self._client = redis.from_url(redis_url)

    def get(self, key -> Any: str) -> Any:
        value = self._client.get(key)
        return value.decode() if value else None

    def set(self, key -> Any: str, value -> Any: Any, ttl -> Any: Optional[int] = None) -> Any:
        self._client.set(key, value, ex=ttl)

    def delete(self, key -> Any: str) -> Any:
        self._client.delete(key)

    def clear(self) -> Any:
        self._client.flushdb()


class AccessScheduleType(Enum):
    """Types of access schedules"""
    ALWAYS = "always"
    SCHOOL_DAYS = "school_days"
    WEEKENDS = "weekends"
    CUSTOM = "custom"


@dataclass
class ParentalControl:
    """Comprehensive parental control settings"""
    child_id: str
    max_daily_minutes: int = 60
    max_session_minutes: int = 30
    allowed_topics: List[str] = field(default_factory=lambda: [
        'education', 'science', 'art', 'music', 'games', 'stories'
    ])
    blocked_topics: List[str] = field(default_factory=lambda: [
        'violence', 'adult_content', 'personal_info'
    ])
    content_filter_level: str = "strict"  # strict, moderate, relaxed
    require_parent_approval: bool = False
    enable_voice_recording: bool = True
    enable_transcripts: bool = True
    alert_settings: Dict[AlertType, bool] = field(default_factory=lambda: {
        AlertType.CONTENT_MODERATION: True,
        AlertType.TIME_LIMIT_WARNING: True,
        AlertType.TIME_LIMIT_EXCEEDED: True,
        AlertType.UNUSUAL_ACTIVITY: True
    })
    access_schedule: Dict[str, Any] = field(default_factory=dict)
    emergency_contacts: List[str] = field(default_factory=list)


@dataclass
class ConversationLog:
    """Detailed conversation log entry"""
    id: str
    child_id: str
    session_id: str
    timestamp: datetime
    duration_seconds: int
    message_count: int
    topics_discussed: List[str]
    sentiment_scores: Dict[str, float]
    moderation_flags: List[str]
    transcript: List[Dict[str, str]]
    audio_url: Optional[str] = None
    summary: Optional[str] = None


@dataclass
class AnalyticsData:
    """Analytics data structure"""
    total_conversations: int
    total_duration_minutes: float
    average_session_minutes: float
    topics_frequency: Dict[str, int]
    sentiment_breakdown: Dict[str, float]
    peak_usage_hours: List[int]
    learning_progress: Dict[str, float]
    vocabulary_growth: int
    interaction_quality_score: float


class ParentUser(Base):
    """Parent user model"""
    __tablename__ = 'parent_users'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    phone = Column(String)
    timezone = Column(String, default='UTC')
    notification_preferences = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)

    # Relationships
    children = relationship("ChildProfile", back_populates="parent")


class ChildProfile(Base):
    """Enhanced child profile model"""
    __tablename__ = 'child_profiles'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    parent_id = Column(String, ForeignKey('parent_users.id'))
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    interests = Column(JSON)
    learning_level = Column(String)
    language_preference = Column(String, default='en')
    avatar_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Parental controls
    parental_controls = Column(JSON)

    # Relationships
    parent = relationship("ParentUser", back_populates="children")
    conversation_logs = relationship(
        "ConversationLogEntry", back_populates="child")


class ConversationLogEntry(Base):
    """Database model for conversation logs"""
    __tablename__ = 'conversation_logs'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    child_id = Column(String, ForeignKey('child_profiles.id'))
    session_id = Column(String)
    started_at = Column(DateTime)
    ended_at = Column(DateTime)
    duration_seconds = Column(Integer)
    message_count = Column(Integer)
    topics = Column(JSON)
    sentiment_scores = Column(JSON)
    moderation_flags = Column(JSON)
    transcript = Column(JSON)
    audio_url = Column(String)
    summary = Column(String)

    # Relationships
    child = relationship("ChildProfile", back_populates="conversation_logs")


class AccessSchedule(Base):
    """Access schedule model"""
    __tablename__ = 'access_schedules'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    child_id = Column(String, ForeignKey('child_profiles.id'))
    day_of_week = Column(Integer)  # 0=Monday, 6=Sunday
    start_time = Column(Time)
    end_time = Column(Time)
    enabled = Column(Boolean, default=True)


class Alert(Base):
    """Alert model"""
    __tablename__ = 'alerts'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    parent_id = Column(String, ForeignKey('parent_users.id'))
    child_id = Column(String, ForeignKey('child_profiles.id'))
    alert_type = Column(String)
    severity = Column(String)
    title = Column(String)
    message = Column(String)
    details = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    read_at = Column(DateTime)
    resolved_at = Column(DateTime)


class ParentDashboardService:
    """
    Enhanced parent dashboard service with comprehensive features
    """

    def __init__(
        self,
        child_repo: ChildRepository,
        conversation_repo: ConversationRepository,
        config=None
    ):
        """Initialize parent dashboard service"""
        self.config = config or get_config()
        self.logger = logging.getLogger(self.__class__.__name__)

        self.child_repository = child_repo
        self.conversation_repository = conversation_repo

        # Initialize components
        self.redis_client = None
        self.scheduler = AsyncIOScheduler()
        self.email_templates = self._load_email_templates()

        # Real-time tracking
        self.active_sessions: Dict[str, Dict] = {}
        self.usage_tracker: Dict[str, List[Dict]] = defaultdict(list)

        # Initialize cache
        self._init_cache()

        # Start scheduler
        self._init_scheduler()

    def _init_cache(self) -> Any:
        """Initialize cache if Redis is available"""
        try:
            # Check if config is dictionary or object
            redis_url = None

            if isinstance(self.config, dict):
                redis_url = self.config.get('REDIS_URL') or self.config.get(
                    'DATABASE', {}).get('REDIS_URL')
            else:
                # AppConfig object
                redis_url = getattr(self.config.database,
                                    'REDIS_URL', None) or os.getenv('REDIS_URL')

            if redis_url:
                self.cache = RedisCache(redis_url)
            else:
                self.cache = InMemoryCache()
        except Exception as e:
            self.logger.warning(f"Cache initialization failed: {e}")
            self.cache = InMemoryCache()

    def _init_scheduler(self) -> Any:
        """Initialize scheduled tasks"""
        # Daily summary at 8 PM
        self.scheduler.add_job(
            self._send_daily_summaries,
            'cron',
            hour=20,
            minute=0
        )

        # Weekly report on Sundays at 6 PM
        self.scheduler.add_job(
            self._send_weekly_reports,
            'cron',
            day_of_week=6,
            hour=18,
            minute=0
        )

        self.scheduler.start()

    def _load_email_templates(self) -> Dict[str, Template]:
        """Load email templates"""
        templates = {
            'daily_summary': Template("""
                <h2>Daily Summary for {{ child_name }}</h2>
                <p>Date: {{ date }}</p>
                <h3>Activity Overview</h3>
                <ul>
                    <li>Total conversations: {{ total_conversations }}</li>
                    <li>Total time: {{ total_time }} minutes</li>
                    <li>Topics discussed: {{ topics|join(', ') }}</li>
                </ul>
                <h3>Highlights</h3>
                {{ highlights }}
            """),
            'alert': Template("""
                <h2>Alert: {{ alert_title }}</h2>
                <p>Child: {{ child_name }}</p>
                <p>Time: {{ timestamp }}</p>
                <p>{{ alert_message }}</p>
                <h3>Details</h3>
                {{ alert_details }}
            """)
        }
        return templates

    async def create_parent_account(
        self,
        email: str,
        name: str,
        phone: Optional[str] = None,
        timezone: str = 'UTC'
    ) -> ParentUser:
        """Create a new parent account"""
        try:
            parent = ParentUser(
                email=email,
                name=name,
                phone=phone,
                timezone=timezone,
                notification_preferences={
                    'email': True,
                    'sms': False,
                    'push': True
                }
            )

            # Save to database
            # await self.db_session.add(parent)
            # await self.db_session.commit()

            self.logger.info(f"Created parent account for {email}")
            return parent

        except Exception as e:
            self.logger.error(f"Error creating parent account: {e}")
            raise

    async def create_child_profile(
        self,
        parent_id: str,
        name: str,
        age: int,
        interests: List[str],
        language: str = 'en'
    ) -> ChildProfile:
        """Create a new child profile with default controls"""
        try:
            # Create child profile
            child = ChildProfile(
                parent_id=parent_id,
                name=name,
                age=age,
                interests=interests,
                language_preference=language,
                learning_level=self._determine_learning_level(age)
            )

            # Set default parental controls
            default_controls = ParentalControl(
                child_id=child.id,
                max_daily_minutes=self._get_age_appropriate_time_limit(age),
                content_filter_level="strict" if age < 10 else "moderate"
            )

            child.parental_controls = default_controls.__dict__

            # Save to database
            # await self.db_session.add(child)
            # await self.db_session.commit()

            self.logger.info(f"Created child profile for {name}")
            return child

        except Exception as e:
            self.logger.error(f"Error creating child profile: {e}")
            raise

    async def update_parental_controls(
        self,
        child_id: str,
        controls: ParentalControl
    ) -> bool:
        """Update parental control settings"""
        try:
            # Get child profile
            # child = await self.db_session.get(ChildProfile, child_id)

            # Update controls
            # child.parental_controls = controls.__dict__
            # await self.db_session.commit()

            # Clear cache
            if self.redis_client:
                await self.redis_client.delete(f"controls:{child_id}")

            self.logger.info(f"Updated parental controls for child {child_id}")
            return True

        except Exception as e:
            self.logger.error(f"Error updating parental controls: {e}")
            return False

    async def log_interaction(
        self,
        user_id: str,
        child_message: str,
        assistant_message: str,
        timestamp: datetime,
        session_id: Optional[str] = None,
        audio_url: Optional[str] = None
    ):
        from src.application.services.moderation_service import ModerationService, ModerationSeverity
        """Log a conversation interaction"""
        try:
            if not session_id:
                session_id = str(uuid.uuid4())

            # Track in active sessions
            if session_id not in self.active_sessions:
                self.active_sessions[session_id] = {
                    'child_id': user_id,
                    'started_at': timestamp,
                    'messages': [],
                    'topics': set()
                }

            # Add message to session
            self.active_sessions[session_id]['messages'].append({
                'timestamp': timestamp.isoformat(),
                'child': child_message,
                'assistant': assistant_message
            })

            # Extract topics (simplified)
            topics = self._extract_topics(
                child_message + " " + assistant_message)
            self.active_sessions[session_id]['topics'].update(topics)

            # Real-time usage tracking
            self.usage_tracker[user_id].append({
                'timestamp': timestamp,
                'session_id': session_id,
                'duration': 1  # Will be updated on session end
            })

            # Check for alerts
            await self._check_real_time_alerts(user_id, child_message, assistant_message)

        except Exception as e:
            self.logger.error(f"Error logging interaction: {e}")

    async def end_conversation_session(self, session_id: str):
        """End a conversation session and save logs"""
        try:
            if session_id not in self.active_sessions:
                return

            session = self.active_sessions[session_id]
            child_id = session['child_id']

            # Calculate duration
            started_at = session['started_at']
            ended_at = datetime.now()
            duration_seconds = (ended_at - started_at).total_seconds()

            # Analyze conversation
            sentiment_scores = await self._analyze_sentiment(session['messages'])
            summary = await self._generate_conversation_summary(session['messages'])

            # Create log entry
            log_entry = ConversationLogEntry(
                child_id=child_id,
                session_id=session_id,
                started_at=started_at,
                ended_at=ended_at,
                duration_seconds=int(duration_seconds),
                message_count=len(session['messages']),
                topics=list(session['topics']),
                sentiment_scores=sentiment_scores,
                transcript=session['messages'],
                summary=summary
            )

            # Save to database
            # await self.db_session.add(log_entry)
            # await self.db_session.commit()

            # Update usage tracker
            for entry in self.usage_tracker[child_id]:
                if entry['session_id'] == session_id:
                    entry['duration'] = duration_seconds

            # Check time limits
            await self._check_time_limits(child_id)

            # Remove from active sessions
            del self.active_sessions[session_id]

        except Exception as e:
            self.logger.error(f"Error ending session: {e}")

    async def get_analytics(
        self,
        child_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        include_charts: bool = False
    ) -> Dict[str, Any]:
        """Get comprehensive analytics for a child"""
        try:
            if not start_date:
                start_date = datetime.now() - timedelta(days=30)
            if not end_date:
                end_date = datetime.now()

            # Get conversation logs
            # logs = await self.db_session.query(ConversationLogEntry).filter(...)

            # For demo, generate sample data
            logs = self._generate_sample_logs(child_id, start_date, end_date)

            # Calculate analytics
            analytics = AnalyticsData(
                total_conversations=len(logs),
                total_duration_minutes=sum(
                    log.duration_seconds for log in logs) / 60,
                average_session_minutes=sum(
                    log.duration_seconds for log in logs) / 60 / len(logs) if logs else 0,
                topics_frequency=self._calculate_topic_frequency(logs),
                sentiment_breakdown=self._calculate_sentiment_breakdown(logs),
                peak_usage_hours=self._calculate_peak_hours(logs),
                learning_progress=self._calculate_learning_progress(logs),
                vocabulary_growth=self._calculate_vocabulary_growth(logs),
                interaction_quality_score=self._calculate_quality_score(logs)
            )

            result = {
                'analytics': analytics.__dict__,
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                }
            }

            # Generate charts if requested
            if include_charts:
                result['charts'] = await self._generate_charts(analytics, logs)

            return result

        except Exception as e:
            self.logger.error(f"Error getting analytics: {e}")
            return {}

    async def set_access_schedule(
        self,
        child_id: str,
        schedule_type: AccessScheduleType,
        custom_schedule: Optional[List[Dict]] = None
    ):
        """Set access schedule for a child"""
        try:
            # Clear existing schedule
            # await self.db_session.query(AccessSchedule).filter_by(child_id=child_id).delete()

            if schedule_type == AccessScheduleType.ALWAYS:
                # No restrictions
                pass
            elif schedule_type == AccessScheduleType.SCHOOL_DAYS:
                # Monday-Friday 3PM-8PM
                for day in range(5):  # 0-4 (Mon-Fri)
                    schedule = AccessSchedule(
                        child_id=child_id,
                        day_of_week=day,
                        start_time=time(15, 0),  # 3 PM
                        end_time=time(20, 0)     # 8 PM
                    )
                    # await self.db_session.add(schedule)
            elif schedule_type == AccessScheduleType.WEEKENDS:
                # Saturday-Sunday 9AM-9PM
                for day in [5, 6]:  # Sat, Sun
                    schedule = AccessSchedule(
                        child_id=child_id,
                        day_of_week=day,
                        start_time=time(9, 0),   # 9 AM
                        end_time=time(21, 0)     # 9 PM
                    )
                    # await self.db_session.add(schedule)
            elif schedule_type == AccessScheduleType.CUSTOM and custom_schedule:
                # Custom schedule
                for entry in custom_schedule:
                    schedule = AccessSchedule(
                        child_id=child_id,
                        day_of_week=entry['day'],
                        start_time=time(
                            entry['start_hour'], entry['start_minute']),
                        end_time=time(entry['end_hour'], entry['end_minute'])
                    )
                    # await self.db_session.add(schedule)

            # await self.db_session.commit()

        except Exception as e:
            self.logger.error(f"Error setting access schedule: {e}")

    async def check_access_allowed(self, child_id: str) -> Tuple[bool, Optional[str]]:
        """Check if access is allowed based on schedule"""
        try:
            now = datetime.now()
            current_day = now.weekday()
            current_time = now.time()

            # Get schedules for current day
            # schedules = await self.db_session.query(AccessSchedule).filter_by(
            #     child_id=child_id,
            #     day_of_week=current_day,
            #     enabled=True
            # ).all()

            # For demo
            schedules = []

            if not schedules:
                # No schedule means always allowed
                return True, None

            # Check if current time is within any allowed period
            for schedule in schedules:
                if schedule.start_time <= current_time <= schedule.end_time:
                    return True, None

            # Not within allowed time
            next_allowed = self._get_next_allowed_time(
                schedules, current_day, current_time)
            return False, f"Access not allowed. Next available time: {next_allowed}"

        except Exception as e:
            self.logger.error(f"Error checking access: {e}")
            return True, None  # Allow on error

    async def send_moderation_alert(
        self,
        user_id: str,
        alert_type: str,
        severity: str,
        details: Dict[str, Any]
    ):
        """Send moderation alert to parent"""
        try:
            # Get child and parent info
            # child = await self.db_session.get(ChildProfile, user_id)
            # parent = await self.db_session.get(ParentUser, child.parent_id)

            # Create alert
            alert = Alert(
                parent_id="parent_id",  # Would come from child.parent_id
                child_id=user_id,
                alert_type=alert_type,
                severity=severity,
                title=f"Content Moderation Alert - {severity.upper()}",
                message=f"Inappropriate content detected in {user_id}'s conversation",
                details=details
            )

            # Save alert
            # await self.db_session.add(alert)
            # await self.db_session.commit()

            # Send notifications
            await self._send_alert_notifications(alert)

        except Exception as e:
            self.logger.error(f"Error sending moderation alert: {e}")

    async def export_conversation_history(
        self,
        child_id: str,
        format: str = 'pdf',
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> bytes:
        """Export conversation history in specified format"""
        try:
            # Get conversation logs
            # logs = await self.db_session.query(ConversationLogEntry).filter(...)
            # For demo, generate sample data
            if not start_date:
                start_date = datetime.now() - timedelta(days=30)
            if not end_date:
                end_date = datetime.now()
            logs = self._generate_sample_logs(child_id, start_date, end_date)

            if format == 'pdf':
                return await self._export_as_pdf(logs)
            elif format == 'excel':
                return await self._export_as_excel(logs)
            elif format == 'json':
                return await self._export_as_json(logs)
            else:
                raise ValueError(f"Unsupported format: {format}")

        except Exception as e:
            self.logger.error(f"Error exporting history: {e}")
            return b""

    async def get_recommendations(self, child_id: str) -> Dict[str, Any]:
        """Get AI-powered recommendations for the child"""
        try:
            # Get recent analytics
            analytics = await self.get_analytics(child_id)

            recommendations = {
                'content_suggestions': [],
                'time_management': [],
                'learning_activities': [],
                'safety_tips': []
            }

            # Content suggestions based on interests and age
            # ...

            # Time management based on usage patterns
            if analytics['analytics']['average_session_minutes'] > 30:
                recommendations['time_management'].append(
                    "Consider shorter sessions with breaks"
                )

            # Learning activities based on progress
            # ...

            # Safety tips based on moderation logs
            # ...

            return recommendations

        except Exception as e:
            self.logger.error(f"Error getting recommendations: {e}")
            return {}

    # Helper methods

    def _determine_learning_level(self, age: int) -> str:
        """Determine learning level based on age"""
        if age < 5:
            return "preschool"
        elif age < 8:
            return "early_elementary"
        elif age < 11:
            return "elementary"
        elif age < 14:
            return "middle_school"
        else:
            return "high_school"

    def _get_age_appropriate_time_limit(self, age: int) -> int:
        """Get age-appropriate daily time limit in minutes"""
        if age < 5:
            return 30
        elif age < 8:
            return 45
        elif age < 11:
            return 60
        elif age < 14:
            return 90
        else:
            return 120

    def _extract_topics(self, text: str) -> List[str]:
        """Extract topics from text"""
        # Simplified topic extraction
        topic_keywords = {
            'education': ['learn', 'study', 'school', 'math', 'science'],
            'games': ['play', 'game', 'fun', 'puzzle'],
            'stories': ['story', 'tale', 'book', 'read'],
            'art': ['draw', 'paint', 'color', 'create'],
            'music': ['song', 'sing', 'music', 'instrument']
        }

        text_lower = text.lower()
        topics = []

        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(topic)

        return topics

    async def _analyze_sentiment(self, messages: List[Dict]) -> Dict[str, float]:
        """Analyze sentiment of messages"""
        # Simplified sentiment analysis
        return {
            'positive': 0.7,
            'neutral': 0.2,
            'negative': 0.1
        }

    async def _generate_conversation_summary(self, messages: List[Dict]) -> str:
        """Generate summary of conversation"""
        # Simplified summary
        return f"Discussed {len(messages)} messages covering various topics"

    async def _check_real_time_alerts(
        self,
        user_id: str,
        child_message: str,
        assistant_message: str
    ):
        """Check for real-time alerts"""
        # Check for emergency keywords
        emergency_keywords = ['help', 'emergency', 'hurt', 'scared', 'danger']
        if any(keyword in child_message.lower() for keyword in emergency_keywords):
            await self.send_moderation_alert(
                user_id,
                AlertType.EMERGENCY.value,
                'high',
                {
                    'message': child_message,
                    'detected_keywords': [k for k in emergency_keywords if k in child_message.lower()]
                }
            )

    async def _check_time_limits(self, child_id: str):
        """Check if time limits are exceeded"""
        try:
            # Get today's usage
            today_start = datetime.now().replace(hour=0, minute=0, second=0)
            today_usage = [
                entry for entry in self.usage_tracker[child_id]
                if entry['timestamp'] >= today_start
            ]

            total_minutes = sum(entry['duration']
                                for entry in today_usage) / 60

            # Get limits
            # controls = await self._get_parental_controls(child_id)
            controls = ParentalControl(child_id=child_id)  # Demo

            # Warning at 80%
            if total_minutes >= controls.max_daily_minutes * 0.8:
                await self.send_moderation_alert(
                    child_id,
                    AlertType.TIME_LIMIT_WARNING.value,
                    'medium',
                    {
                        'usage_minutes': total_minutes,
                        'limit_minutes': controls.max_daily_minutes,
                        'percentage': (total_minutes / controls.max_daily_minutes) * 100
                    }
                )

            # Exceeded
            if total_minutes >= controls.max_daily_minutes:
                await self.send_moderation_alert(
                    child_id,
                    AlertType.TIME_LIMIT_EXCEEDED.value,
                    'high',
                    {
                        'usage_minutes': total_minutes,
                        'limit_minutes': controls.max_daily_minutes,
                        'overage_minutes': total_minutes - controls.max_daily_minutes
                    }
                )

        except Exception as e:
            self.logger.error(f"Error checking time limits: {e}")

    def _calculate_topic_frequency(self, logs: List[ConversationLogEntry]) -> Dict[str, int]:
        """Calculate topic frequency from logs"""
        topic_freq = defaultdict(int)
        for log in logs:
            for topic in log.topics:
                topic_freq[topic] += 1
        return dict(topic_freq)

    def _calculate_sentiment_breakdown(self, logs: List[ConversationLogEntry]) -> Dict[str, float]:
        """Calculate average sentiment breakdown"""
        if not logs:
            return {'positive': 0, 'neutral': 0, 'negative': 0}

        sentiment_totals = defaultdict(float)
        for log in logs:
            for sentiment, score in log.sentiment_scores.items():
                sentiment_totals[sentiment] += score

        count = len(logs)
        return {k: v/count for k, v in sentiment_totals.items()}

    def _calculate_peak_hours(self, logs: List[ConversationLogEntry]) -> List[int]:
        """Calculate peak usage hours"""
        hour_counts = defaultdict(int)
        for log in logs:
            hour = log.started_at.hour
            hour_counts[hour] += 1

        # Get top 3 hours
        sorted_hours = sorted(hour_counts.items(),
                              key=lambda x: x[1], reverse=True)
        return [hour for hour, count in sorted_hours[:3]]

    def _calculate_learning_progress(self, logs: List[ConversationLogEntry]) -> Dict[str, float]:
        """Calculate learning progress metrics"""
        # Simplified progress calculation
        educational_topics = ['education', 'science', 'math', 'reading']
        total_educational = sum(
            1 for log in logs
            if any(topic in educational_topics for topic in log.topics)
        )

        return {
            'educational_engagement': total_educational / len(logs) if logs else 0,
            'topic_diversity': len(set(topic for log in logs for topic in log.topics)),
            # Daily usage over 30 days
            'consistency_score': min(len(logs) / 30, 1.0)
        }

    def _calculate_vocabulary_growth(self, logs: List[ConversationLogEntry]) -> int:
        """Calculate vocabulary growth"""
        # Simplified - count unique words used
        all_words = set()
        for log in logs:
            for message in log.transcript:
                if message.get('child'):
                    words = message['child'].lower().split()
                    all_words.update(words)
        return len(all_words)

    def _calculate_quality_score(self, logs: List[ConversationLogEntry]) -> float:
        """Calculate interaction quality score"""
        if not logs:
            return 0.0

        factors = {
            'positive_sentiment': self._calculate_sentiment_breakdown(logs).get('positive', 0) * 0.3,
            'topic_diversity': min(len(self._calculate_topic_frequency(logs)) / 10, 1.0) * 0.2,
            'appropriate_duration': sum(1 for log in logs if 5 <= log.duration_seconds/60 <= 30) / len(logs) * 0.3,
            'educational_content': self._calculate_learning_progress(logs)['educational_engagement'] * 0.2
        }

        return sum(factors.values())

    async def _generate_charts(self, analytics: AnalyticsData, logs: List[ConversationLogEntry]) -> Dict[str, str]:
        """Generate analytics charts"""
        charts = {}

        # Usage over time chart
        plt.figure(figsize=(10, 6))
        dates = [log.started_at.date() for log in logs]
        date_counts = pd.Series(dates).value_counts().sort_index()
        plt.plot(date_counts.index, date_counts.values)
        plt.title('Daily Usage Trend')
        plt.xlabel('Date')
        plt.ylabel('Number of Conversations')

        # Save to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        charts['usage_trend'] = base64.b64encode(buffer.read()).decode()
        plt.close()

        # Topic distribution pie chart
        plt.figure(figsize=(8, 8))
        topics = list(analytics.topics_frequency.keys())
        counts = list(analytics.topics_frequency.values())
        plt.pie(counts, labels=topics, autopct='%1.1f%%')
        plt.title('Topics Discussed')

        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        charts['topic_distribution'] = base64.b64encode(buffer.read()).decode()
        plt.close()

        # Sentiment breakdown
        plt.figure(figsize=(8, 6))
        sentiments = list(analytics.sentiment_breakdown.keys())
        scores = list(analytics.sentiment_breakdown.values())
        plt.bar(sentiments, scores)
        plt.title('Conversation Sentiment')
        plt.ylabel('Average Score')

        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        charts['sentiment_breakdown'] = base64.b64encode(
            buffer.read()).decode()
        plt.close()

        return charts

    def _get_next_allowed_time(self, schedules: List[AccessSchedule], current_day: int, current_time: time) -> str:
        """Get next allowed access time"""
        # Find next allowed time slot
        for schedule in schedules:
            if schedule.start_time > current_time:
                return f"Today at {schedule.start_time.strftime('%I:%M %p')}"

        # Check next days
        for days_ahead in range(1, 8):
            next_day = (current_day + days_ahead) % 7
            # Would query schedules for next_day
            # For now, return a default
            return "Tomorrow at 3:00 PM"

    async def _send_alert_notifications(self, alert: Alert):
        """Send alert notifications via configured channels"""
        try:
            # Get parent preferences
            # parent = await self.db_session.get(ParentUser, alert.parent_id)

            # Email notification
            if True:  # parent.notification_preferences.get('email')
                await self._send_email_alert(alert)

            # SMS notification (if configured)
            # if parent.notification_preferences.get('sms'):
            #     await self._send_sms_alert(alert, parent.phone)

            # Push notification (if configured)
            # if parent.notification_preferences.get('push'):
            #     await self._send_push_notification(alert)

        except Exception as e:
            self.logger.error(f"Error sending notifications: {e}")

    async def _send_email_alert(self, alert: Alert):
        """Send email alert"""
        try:
            # Get email template
            template = self.email_templates['alert']

            # Render HTML
            html_content = template.render(
                alert_title=alert.title,
                child_name="Child Name",  # Would get from database
                timestamp=alert.created_at.strftime('%Y-%m-%d %I:%M %p'),
                alert_message=alert.message,
                alert_details=json.dumps(alert.details, indent=2)
            )

            # Create email
            msg = MIMEMultipart('alternative')
            msg['Subject'] = alert.title
            msg['From'] = self.config.get('EMAIL_FROM', 'noreply@ai-teddy.com')
            msg['To'] = "parent@example.com"  # Would get from parent record

            # Attach HTML
            msg.attach(MIMEText(html_content, 'html'))

            # Send email
            async with aiosmtplib.SMTP(
                hostname=self.config.get('SMTP_HOST'),
                port=self.config.get('SMTP_PORT', 587)
            ) as smtp:
                await smtp.login(
                    self.config.get('SMTP_USER'),
                    self.config.get('SMTP_PASS')
                )
                await smtp.send_message(msg)

        except Exception as e:
            self.logger.error(f"Error sending email: {e}")

    async def _send_daily_summaries(self):
        """Send daily summaries to all parents"""
        try:
            # Get all active parents
            # parents = await self.db_session.query(ParentUser).all()

            for parent in []:  # Would iterate through parents
                for child in parent.children:
                    # Get today's data
                    analytics = await self.get_analytics(
                        child.id,
                        start_date=datetime.now().replace(hour=0, minute=0, second=0),
                        end_date=datetime.now()
                    )

                    if analytics['analytics']['total_conversations'] > 0:
                        # Send summary
                        await self._send_daily_summary_email(parent, child, analytics)

        except Exception as e:
            self.logger.error(f"Error sending daily summaries: {e}")

    async def _send_weekly_reports(self):
        """Send weekly reports to all parents"""
        try:
            # Similar to daily summaries but with weekly data
            pass
        except Exception as e:
            self.logger.error(f"Error sending weekly reports: {e}")

    def _generate_sample_logs(self, child_id: str, start_date: datetime, end_date: datetime) -> List[ConversationLogEntry]:
        """Generate sample logs for demo"""
        logs = []
        current = start_date

        while current <= end_date:
            # 1-3 conversations per day
            num_conversations = np.random.randint(1, 4)

            for i in range(num_conversations):
                # Random time during the day
                hour = np.random.randint(15, 20)  # 3PM to 8PM
                minute = np.random.randint(0, 60)

                log = ConversationLogEntry(
                    id=str(uuid.uuid4()),
                    child_id=child_id,
                    session_id=str(uuid.uuid4()),
                    started_at=current.replace(hour=hour, minute=minute),
                    duration_seconds=np.random.randint(
                        300, 1800),  # 5-30 minutes
                    message_count=np.random.randint(10, 50),
                    topics=np.random.choice(
                        ['education', 'games', 'stories', 'science', 'art'],
                        size=np.random.randint(1, 4),
                        replace=False
                    ).tolist(),
                    sentiment_scores={
                        'positive': np.random.random() * 0.7 + 0.3,
                        'neutral': np.random.random() * 0.3,
                        'negative': np.random.random() * 0.1
                    },
                    moderation_flags=[],
                    transcript=[
                        {
                            'timestamp': (current + timedelta(seconds=i*30)).isoformat(),
                            'child': f"Sample child message {i}",
                            'assistant': f"Sample assistant response {i}"
                        }
                        for i in range(5)
                    ]
                )

                logs.append(log)

            current += timedelta(days=1)

        return logs

    async def _export_as_pdf(self, logs: List[ConversationLogEntry]) -> bytes:
        """Export logs as PDF"""
        # Would use reportlab or similar
        return b"PDF content"

    async def _export_as_excel(self, logs: List[ConversationLogEntry]) -> bytes:
        """Export logs as Excel"""
        # Create DataFrame
        data = []
        for log in logs:
            data.append({
                'Date': log.started_at.date(),
                'Time': log.started_at.time(),
                'Duration (minutes)': log.duration_seconds / 60,
                'Messages': log.message_count,
                'Topics': ', '.join(log.topics),
                'Sentiment': log.sentiment_scores.get('positive', 0)
            })

        df = pd.DataFrame(data)

        # Write to Excel
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Conversation History', index=False)

        buffer.seek(0)
        return buffer.read()

    async def _export_as_json(self, logs: List[ConversationLogEntry]) -> bytes:
        """Export logs as JSON"""
        data = [
            {
                'id': log.id,
                'started_at': log.started_at.isoformat(),
                'duration_seconds': log.duration_seconds,
                'topics': log.topics,
                'transcript': log.transcript
            }
            for log in logs
        ]

        return json.dumps(data, indent=2).encode()

    async def get_parent_by_id(self, parent_id: str) -> Optional[Any]:
        """Get parent user from DB with input validation"""
        if not isinstance(parent_id, str) or not parent_id:
            self.logger.error("Invalid parent_id for get_parent_by_id")
            return None
        # Example: Use ORM or repository
        if hasattr(self, 'parent_repository'):
            return await self.parent_repository.get(parent_id)
        self.logger.error("parent_repository not configured")
        return None


# API endpoints for dashboard
class ParentDashboardAPI:
    """REST API for parent dashboard"""

    def __init__(self, dashboard_service: ParentDashboardService):
        self.service = dashboard_service

    async def get_dashboard_data(self, parent_id: str) -> Dict[str, Any]:
        """Get dashboard data for parent"""
        # Get all children
        # children = await self.service.get_children_for_parent(parent_id)

        dashboard_data = {
            'children': [],
            'alerts': [],
            'quick_stats': {},
            'recent_activity': []
        }

        # Populate data
        # ...

        return dashboard_data

    async def update_settings(self, child_id: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Update child settings"""
        controls = ParentalControl(
            child_id=child_id,
            **settings
        )

        success = await self.service.update_parental_controls(child_id, controls)

        return {'success': success}

    async def get_real_time_status(self, child_id: str) -> Dict[str, Any]:
        """Get real-time status for a child"""
        # Check if currently active
        active_session = None
        for session_id, session in self.service.active_sessions.items():
            if session['child_id'] == child_id:
                active_session = session
                break

        return {
            'is_active': active_session is not None,
            'session_duration': (datetime.now() - active_session['started_at']).seconds if active_session else 0,
            'current_topics': list(active_session['topics']) if active_session else [],
            'message_count': len(active_session['messages']) if active_session else 0
        }