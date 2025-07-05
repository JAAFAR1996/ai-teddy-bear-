"""
Alert Domain Models
==================

Domain models for alert system including types, severity levels, and alert entities.
"""

import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from sqlalchemy import JSON, Column, DateTime, ForeignKey, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class AlertType(Enum):
    """Types of parent alerts with business meaning"""

    CONTENT_MODERATION = "content_moderation"
    TIME_LIMIT_WARNING = "time_limit_warning"
    TIME_LIMIT_EXCEEDED = "time_limit_exceeded"
    UNUSUAL_ACTIVITY = "unusual_activity"
    MILESTONE_REACHED = "milestone_reached"
    DAILY_SUMMARY = "daily_summary"
    WEEKLY_REPORT = "weekly_report"
    EMERGENCY = "emergency"

    def get_display_name(self) -> str:
        """Get user-friendly display name"""
        display_names = {
            self.CONTENT_MODERATION: "Content Moderation Alert",
            self.TIME_LIMIT_WARNING: "Time Limit Warning",
            self.TIME_LIMIT_EXCEEDED: "Time Limit Exceeded",
            self.UNUSUAL_ACTIVITY: "Unusual Activity Detected",
            self.MILESTONE_REACHED: "Milestone Achievement",
            self.DAILY_SUMMARY: "Daily Summary",
            self.WEEKLY_REPORT: "Weekly Report",
            self.EMERGENCY: "Emergency Alert",
        }
        return display_names.get(self, self.value)

    def get_default_severity(self) -> "AlertSeverity":
        """Get default severity for alert type"""
        severity_map = {
            self.CONTENT_MODERATION: AlertSeverity.HIGH,
            self.TIME_LIMIT_WARNING: AlertSeverity.MEDIUM,
            self.TIME_LIMIT_EXCEEDED: AlertSeverity.HIGH,
            self.UNUSUAL_ACTIVITY: AlertSeverity.MEDIUM,
            self.MILESTONE_REACHED: AlertSeverity.LOW,
            self.DAILY_SUMMARY: AlertSeverity.LOW,
            self.WEEKLY_REPORT: AlertSeverity.LOW,
            self.EMERGENCY: AlertSeverity.CRITICAL,
        }
        return severity_map.get(self, AlertSeverity.MEDIUM)


class AlertSeverity(Enum):
    """Alert severity levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    def get_priority_score(self) -> int:
        """Get numeric priority for sorting"""
        scores = {self.LOW: 1, self.MEDIUM: 2, self.HIGH: 3, self.CRITICAL: 4}
        return scores[self]


class Alert(Base):
    """Alert domain entity with business logic"""

    __tablename__ = "alerts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    parent_id = Column(String, ForeignKey("parent_users.id"), nullable=False)
    child_id = Column(String, ForeignKey("child_profiles.id"), nullable=False)
    alert_type = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    details = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    read_at = Column(DateTime)
    resolved_at = Column(DateTime)

    def is_read(self) -> bool:
        """Check if alert has been read"""
        return self.read_at is not None

    def is_resolved(self) -> bool:
        """Check if alert has been resolved"""
        return self.resolved_at is not None

    def mark_as_read(self) -> None:
        """Mark alert as read"""
        if not self.is_read():
            self.read_at = datetime.utcnow()

    def resolve(self) -> None:
        """Resolve the alert"""
        if not self.is_resolved():
            self.resolved_at = datetime.utcnow()
            if not self.is_read():
                self.mark_as_read()

    def get_age_hours(self) -> float:
        """Get age of alert in hours"""
        return (datetime.utcnow() - self.created_at).total_seconds() / 3600

    def is_urgent(self) -> bool:
        """Check if alert requires urgent attention"""
        severity = AlertSeverity(self.severity)
        return severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]

    def should_escalate(self, hours_threshold: float = 24) -> bool:
        """Check if unread alert should be escalated"""
        return not self.is_read() and self.get_age_hours() > hours_threshold


@dataclass
class AlertSummary:
    """Summary of alerts for dashboard display"""

    total_alerts: int
    unread_count: int
    critical_count: int
    high_priority_count: int
    recent_alerts: int
    escalation_needed: int = 0

    def get_urgency_level(self) -> str:
        """Get overall urgency level"""
        if self.critical_count > 0:
            return "critical"
        elif self.high_priority_count > 3:
            return "high"
        elif self.unread_count > 5:
            return "medium"
        else:
            return "normal"
