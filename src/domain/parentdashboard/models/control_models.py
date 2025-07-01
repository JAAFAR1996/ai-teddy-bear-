"""
Parental Control Domain Models
=============================

Domain models for parental controls including access schedules, content filters,
and time management settings.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, time
from enum import Enum
from typing import Any, Dict, List, Optional

from sqlalchemy import JSON, Boolean, Column, ForeignKey, Integer, String, Time
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class AccessScheduleType(Enum):
    """Types of access schedules with business logic"""

    ALWAYS = "always"
    SCHOOL_DAYS = "school_days"
    WEEKENDS = "weekends"
    CUSTOM = "custom"

    def get_default_schedule(self) -> List[Dict[str, Any]]:
        """Get default schedule configuration"""
        if self == AccessScheduleType.ALWAYS:
            return []  # No restrictions
        elif self == AccessScheduleType.SCHOOL_DAYS:
            # Monday-Friday 3PM-8PM
            return [
                {
                    "day": day,
                    "start_hour": 15,
                    "start_minute": 0,
                    "end_hour": 20,
                    "end_minute": 0,
                }
                for day in range(5)  # 0-4 (Mon-Fri)
            ]
        elif self == AccessScheduleType.WEEKENDS:
            # Saturday-Sunday 9AM-9PM
            return [
                {
                    "day": day,
                    "start_hour": 9,
                    "start_minute": 0,
                    "end_hour": 21,
                    "end_minute": 0,
                }
                for day in [5, 6]  # Sat, Sun
            ]
        return []


class ContentFilterLevel(Enum):
    """Content filtering levels"""

    STRICT = "strict"
    MODERATE = "moderate"
    RELAXED = "relaxed"

    def get_blocked_topics(self) -> List[str]:
        """Get topics blocked at this level"""
        if self == ContentFilterLevel.STRICT:
            return [
                "violence",
                "adult_content",
                "personal_info",
                "social_media",
                "dating",
                "politics",
            ]
        elif self == ContentFilterLevel.MODERATE:
            return ["violence", "adult_content", "personal_info"]
        else:  # RELAXED
            return ["adult_content", "personal_info"]


@dataclass
class ParentalControl:
    """Comprehensive parental control settings with business validation"""

    child_id: str
    max_daily_minutes: int = 60
    max_session_minutes: int = 30
    allowed_topics: List[str] = field(
        default_factory=lambda: [
            "education",
            "science",
            "art",
            "music",
            "games",
            "stories",
        ]
    )
    blocked_topics: List[str] = field(
        default_factory=lambda: ["violence", "adult_content", "personal_info"]
    )
    content_filter_level: str = "strict"
    require_parent_approval: bool = False
    enable_voice_recording: bool = True
    enable_transcripts: bool = True
    alert_settings: Dict[str, bool] = field(
        default_factory=lambda: {
            "content_moderation": True,
            "time_limit_warning": True,
            "time_limit_exceeded": True,
            "unusual_activity": True,
        }
    )
    access_schedule: Dict[str, Any] = field(default_factory=dict)
    emergency_contacts: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate settings after initialization"""
        self.validate_time_limits()
        self.validate_topics()

    def validate_time_limits(self) -> None:
        """Validate time limit settings"""
        if self.max_daily_minutes <= 0 or self.max_daily_minutes > 480:  # Max 8 hours
            raise ValueError("Daily time limit must be between 1-480 minutes")

        if (
            self.max_session_minutes <= 0 or self.max_session_minutes > 120
        ):  # Max 2 hours
            raise ValueError("Session time limit must be between 1-120 minutes")

        if self.max_session_minutes > self.max_daily_minutes:
            raise ValueError("Session limit cannot exceed daily limit")

    def validate_topics(self) -> None:
        """Validate topic settings"""
        blocked_set = set(self.blocked_topics)
        allowed_set = set(self.allowed_topics)

        overlap = blocked_set & allowed_set
        if overlap:
            raise ValueError(f"Topics cannot be both allowed and blocked: {overlap}")

    def is_topic_allowed(self, topic: str) -> bool:
        """Check if topic is allowed based on settings"""
        if topic in self.blocked_topics:
            return False
        return topic in self.allowed_topics if self.allowed_topics else True

    def get_warning_threshold_minutes(self) -> int:
        """Get time when warning should be triggered (80% of daily limit)"""
        return int(self.max_daily_minutes * 0.8)

    def should_alert_for_topic(self, topic: str) -> bool:
        """Check if should alert for this topic"""
        return self.alert_settings.get(
            "content_moderation", True
        ) and not self.is_topic_allowed(topic)


class AccessSchedule(Base):
    """Access schedule domain entity"""

    __tablename__ = "access_schedules"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    child_id = Column(String, ForeignKey("child_profiles.id"), nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    enabled = Column(Boolean, default=True)

    def is_access_allowed_now(self) -> bool:
        """Check if access is allowed at current time"""
        if not self.enabled:
            return False

        now = datetime.now()
        current_day = now.weekday()
        current_time = now.time()

        return (
            current_day == self.day_of_week
            and self.start_time <= current_time <= self.end_time
        )

    def get_minutes_until_access(self) -> Optional[int]:
        """Get minutes until access is allowed"""
        now = datetime.now()
        current_day = now.weekday()
        current_time = now.time()

        if current_day == self.day_of_week:
            if current_time < self.start_time:
                # Same day, before start time
                start_datetime = datetime.combine(now.date(), self.start_time)
                return int((start_datetime - now).total_seconds() / 60)
            elif current_time > self.end_time:
                # Same day, after end time - check next occurrence
                pass

        # Calculate next occurrence
        days_ahead = (self.day_of_week - current_day) % 7
        if days_ahead == 0:
            days_ahead = 7  # Next week

        next_date = now.date()
        next_datetime = datetime.combine(next_date, self.start_time)
        next_datetime = next_datetime.replace(day=next_datetime.day + days_ahead)

        return int((next_datetime - now).total_seconds() / 60)

    def get_remaining_access_minutes(self) -> Optional[int]:
        """Get remaining access minutes if currently in allowed period"""
        if not self.is_access_allowed_now():
            return None

        now = datetime.now()
        end_datetime = datetime.combine(now.date(), self.end_time)

        return max(0, int((end_datetime - now).total_seconds() / 60))


@dataclass
class TimeUsageStats:
    """Time usage statistics for parental controls"""

    daily_minutes_used: int
    session_minutes_used: int
    daily_limit: int
    session_limit: int
    warning_threshold: int

    def is_approaching_daily_limit(self) -> bool:
        """Check if approaching daily time limit"""
        return self.daily_minutes_used >= self.warning_threshold

    def is_daily_limit_exceeded(self) -> bool:
        """Check if daily limit is exceeded"""
        return self.daily_minutes_used >= self.daily_limit

    def is_session_limit_exceeded(self) -> bool:
        """Check if session limit is exceeded"""
        return self.session_minutes_used >= self.session_limit

    def get_remaining_daily_minutes(self) -> int:
        """Get remaining daily minutes"""
        return max(0, self.daily_limit - self.daily_minutes_used)

    def get_remaining_session_minutes(self) -> int:
        """Get remaining session minutes"""
        return max(0, self.session_limit - self.session_minutes_used)

    def get_usage_percentage(self) -> float:
        """Get daily usage percentage"""
        return (
            (self.daily_minutes_used / self.daily_limit) * 100
            if self.daily_limit > 0
            else 0
        )
