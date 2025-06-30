#!/usr/bin/env python3
"""
🏗️ Notification Domain - DDD Implementation
Auto-generated from God Class refactoring
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import uuid

# Original imports
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path

class NotificationChannel(Enum):
    """قنوات الإشعارات المدعومة"""


class NotificationPriority(Enum):
    """مستويات أولوية الإشعارات"""


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


class NotificationStats:
    """إحصائيات الإشعارات"""
    emails_sent: int = 0
    push_sent: int = 0
    sms_sent: int = 0
    in_app_sent: int = 0
    errors_count: int = 0
    children_notified: int = 0
    execution_time_seconds: float = 0.0


class NotificationService:
    """
    🛎️ خدمة الإشعارات الشاملة
    
    الميزات:
    - إشعارات متعددة القنوات (Email, Push, SMS, In-App)
    - قوالب HTML جميلة ومخصصة
    - جدولة ذكية للإشعارات
    - تتبع حالة الإرسال
    - معالجة شاملة للأخطاء
    - دعم اللغات المتعددة
    """
    