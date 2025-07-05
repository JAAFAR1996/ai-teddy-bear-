"""
Dashboard Alert Service
======================

Application service for managing alerts and notifications.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.domain.parentdashboard.models.alert_models import (Alert,
                                                            AlertSeverity,
                                                            AlertType)
from src.domain.parentdashboard.services.content_analysis_service import \
    ContentAnalysisService


class DashboardAlertService:
    """Application service for alert management"""

    def __init__(self, content_analysis_service: ContentAnalysisService):
        self.content_service = content_analysis_service
        self.logger = logging.getLogger(self.__class__.__name__)

    async def create_alert(
        self,
        parent_id: str,
        child_id: str,
        alert_type: AlertType,
        severity: AlertSeverity,
        title: str,
        message: str,
        details: Dict[str, Any] = None,
    ) -> Alert:
        """Create a new alert"""

        alert = Alert(
            parent_id=parent_id,
            child_id=child_id,
            alert_type=alert_type.value,
            severity=severity.value,
            title=title,
            message=message,
            details=details or {},
        )

        self.logger.info(
            f"Created {severity.value} alert for child {child_id}: {title}"
        )
        return alert

    async def process_moderation_alert(
        self,
        child_id: str,
        parent_id: str,
        conversation_content: str,
        detected_issues: List[str],
    ) -> Optional[Alert]:
        """Process and create moderation alerts"""

        if not detected_issues:
            return None

        # Determine severity based on issues
        severity = AlertSeverity.LOW
        if "emergency" in detected_issues:
            severity = AlertSeverity.CRITICAL
        elif any(
            issue in ["inappropriate_content", "bullying_concern"]
            for issue in detected_issues
        ):
            severity = AlertSeverity.HIGH
        elif "emotional_distress" in detected_issues:
            severity = AlertSeverity.MEDIUM

        # Create alert
        alert = await self.create_alert(
            parent_id=parent_id,
            child_id=child_id,
            alert_type=AlertType.CONTENT_MODERATION,
            severity=severity,
            title=f"Content Moderation - {severity.value.title()}",
            message=f"Issues detected: {', '.join(detected_issues)}",
            details={
                "detected_issues": detected_issues,
                "conversation_excerpt": (
                    conversation_content[:200] + "..."
                    if len(conversation_content) > 200
                    else conversation_content
                ),
                "timestamp": datetime.now().isoformat(),
            },
        )

        return alert

    async def process_time_limit_alert(
        self,
        child_id: str,
        parent_id: str,
        alert_type: AlertType,
        usage_minutes: int,
        limit_minutes: int,
    ) -> Alert:
        """Process time limit related alerts"""

        if alert_type == AlertType.TIME_LIMIT_WARNING:
            severity = AlertSeverity.MEDIUM
            title = "Time Limit Warning"
            message = f"Child approaching daily limit ({usage_minutes}/{limit_minutes} minutes)"
        else:  # TIME_LIMIT_EXCEEDED
            severity = AlertSeverity.HIGH
            title = "Time Limit Exceeded"
            message = (
                f"Daily time limit exceeded ({usage_minutes}/{limit_minutes} minutes)"
            )

        alert = await self.create_alert(
            parent_id=parent_id,
            child_id=child_id,
            alert_type=alert_type,
            severity=severity,
            title=title,
            message=message,
            details={
                "usage_minutes": usage_minutes,
                "limit_minutes": limit_minutes,
                "overage_minutes": max(0, usage_minutes - limit_minutes),
                "percentage_used": (
                    (usage_minutes / limit_minutes) * 100 if limit_minutes > 0 else 0
                ),
            },
        )

        return alert

    async def get_alerts_for_parent(
        self, parent_id: str, include_resolved: bool = False, limit: int = 50
    ) -> List[Alert]:
        """Get alerts for a parent"""

        # In real implementation, would query database
        # For now, return empty list
        return []

    async def mark_alert_as_read(self, alert_id: str) -> bool:
        """Mark alert as read"""

        try:
            # In real implementation, would update database
            self.logger.info(f"Marked alert {alert_id} as read")
            return True
        except Exception as e:
            self.logger.error(f"Error marking alert as read: {e}")
            return False

    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert"""

        try:
            # In real implementation, would update database
            self.logger.info(f"Resolved alert {alert_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error resolving alert: {e}")
            return False

    async def get_alert_summary(self, parent_id: str) -> Dict[str, Any]:
        """Get summary of alerts for dashboard"""

        # In real implementation, would aggregate from database
        return {
            "total_alerts": 0,
            "unread_count": 0,
            "critical_count": 0,
            "high_priority_count": 0,
            "recent_alerts": 0,
            "escalation_needed": 0,
        }
