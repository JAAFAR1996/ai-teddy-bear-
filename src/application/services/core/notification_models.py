from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class NotificationChannel(Enum):
    """قنوات الإشعارات المدعومة"""
    EMAIL = "email"
    PUSH = "push"
    SMS = "sms"
    IN_APP = "in_app"


class NotificationPriority(Enum):
    """مستويات أولوية الإشعارات"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class NotificationData:
    """بيانات الإشعار"""
    child_udid: str
    child_name: str
    parent_email: str
    parent_device_id: Optional[str] = None
    parent_phone: Optional[str] = None
    sessions_count: int = 0
    oldest_date: Optional[datetime] = None
    newest_date: Optional[datetime] = None
    days_until_deletion: int = 2


@dataclass
class NotificationStats:
    """إحصائيات الإشعارات"""
    emails_sent: int = 0
    push_sent: int = 0
    sms_sent: int = 0
    in_app_sent: int = 0
    errors_count: int = 0
    children_notified: int = 0
    execution_time_seconds: float = 0.0
