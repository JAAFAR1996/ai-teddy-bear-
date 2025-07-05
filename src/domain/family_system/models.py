from dataclasses import dataclass
from datetime import datetime, time
from enum import Enum
from typing import Any, Dict, List, Optional


class MessageType(Enum):
    MOTIVATION = "تحفيزية"
    ACHIEVEMENT = "إنجاز"
    REMINDER = "تذكير"
    ENCOURAGEMENT = "تشجيع"
    LEARNING = "تعليمية"
    BEDTIME = "نوم"
    WAKE_UP = "استيقاظ"


class TimeRestrictionType(Enum):
    DAILY_LIMIT = "حد_يومي"
    TIME_WINDOW = "نافذة_زمنية"
    BEDTIME_RESTRICTION = "قيد_النوم"
    STUDY_TIME = "وقت_الدراسة"
    BREAK_INTERVALS = "فترات_راحة"


@dataclass
class ScheduledMessage:
    id: str
    child_name: str
    device_id: str
    message_type: MessageType
    content: str
    scheduled_time: time
    days_of_week: List[int]
    is_active: bool
    created_by_parent: str
    created_at: datetime
    last_sent: Optional[datetime] = None


@dataclass
class TimeRestriction:
    id: str
    child_name: str
    device_id: str
    restriction_type: TimeRestrictionType
    start_time: Optional[time]
    end_time: Optional[time]
    daily_limit_minutes: Optional[int]
    days_of_week: List[int]
    is_active: bool
    set_by_parent: str
    reason: str
    created_at: datetime


@dataclass
class FamilyMember:
    id: str
    name: str
    role: str
    age: Optional[int]
    relationship: str
    device_ids: List[str]
    preferences: Dict[str, Any]
    created_at: datetime


@dataclass
class FamilyProfile:
    family_id: str
    family_name: str
    members: List[FamilyMember]
    shared_settings: Dict[str, Any]
    time_zone: str
    language: str
    cultural_settings: Dict[str, Any]
    subscription_type: str
    created_at: datetime
    updated_at: datetime


@dataclass
class ChildComparison:
    family_id: str
    comparison_date: datetime
    children_data: Dict[str, Dict]
    insights: List[str]
    recommendations: List[str]


@dataclass
class MessageScheduleDetails:
    child_name: str
    device_id: str
    message_type: MessageType
    content: str
    scheduled_time: time
    days_of_week: List[int]


@dataclass
class TimeRestrictionDetails:
    child_name: str
    device_id: str
    restriction_type: TimeRestrictionType
    reason: str
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    daily_limit_minutes: Optional[int] = None
    days_of_week: Optional[List[int]] = None
