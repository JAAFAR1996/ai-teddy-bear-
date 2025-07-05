"""
🔒 Access Control & Alerts Service
High cohesion component for access control, alerts, and notification operations
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from .models import AlertRequest


class AccessControlAlertsService:
    """
    Dedicated service for access control and alert management.
    High cohesion: all methods work with access control and alert operations.
    """

    def __init__(
            self,
            orchestrator,
            alert_service,
            notification_service,
            access_control_service):
        """Initialize access control and alerts service"""
        self.orchestrator = orchestrator
        self.alert_service = alert_service
        self.notification_service = notification_service
        self.access_control_service = access_control_service
        self.logger = logging.getLogger(__name__)

    async def check_access_allowed(
            self, child_id: str) -> Tuple[bool, Optional[str]]:
        """Check if child can access the system with detailed reason"""
        try:
            access_result = await self.orchestrator.check_child_access(child_id)

            allowed = access_result.get("allowed", False)
            reason = access_result.get("reason")

            if not allowed:
                self.logger.info(
                    f"Access denied for child {child_id}: {reason}")
            else:
                self.logger.debug(f"Access granted for child {child_id}")

            return allowed, reason

        except Exception as e:
            self.logger.error(
                f"Failed to check access for child {child_id}: {e}")
            # Fail safe - deny access on error
            return False, f"Access check failed: {str(e)}"

    async def update_parental_controls(
        self, child_id: str, controls: Dict[str, Any]
    ) -> bool:
        """Update parental control settings with validation"""
        try:
            # Validate control settings
            if not self._validate_parental_controls(controls):
                self.logger.warning(
                    f"Invalid parental controls for child {child_id}")
                return False

            success = await self.orchestrator.update_parental_controls(
                child_id, controls
            )

            if success:
                self.logger.info(
                    f"Successfully updated parental controls for child {child_id}"
                )

                # Create audit log for control changes
                await self._log_control_changes(child_id, controls)
            else:
                self.logger.warning(
                    f"Failed to update parental controls for child {child_id}"
                )

            return success

        except Exception as e:
            self.logger.error(
                f"Error updating parental controls for child {child_id}: {e}"
            )
            return False

    async def set_access_schedule(
        self,
        child_id: str,
        schedule_type: str,
        custom_schedule: Optional[List[Dict]] = None,
    ) -> bool:
        """Set access schedule for a child with time restrictions"""
        try:
            # Create schedule using access control service
            if schedule_type == "custom" and custom_schedule:
                schedules = custom_schedule
            else:
                schedules = self.access_control_service.create_default_schedule(
                    child_id, schedule_type)

            # Apply the schedule
            success = await self._apply_access_schedule(child_id, schedules)

            if success:
                self.logger.info(
                    f"Successfully set {schedule_type} schedule for child {child_id}"
                )
            else:
                self.logger.warning(
                    f"Failed to set schedule for child {child_id}")

            return success

        except Exception as e:
            self.logger.error(
                f"Error setting access schedule for child {child_id}: {e}"
            )
            return False

    async def create_alert(self, alert_request: AlertRequest) -> bool:
        """Create and send an alert using parameter object"""
        try:
            # Create the alert
            alert = await self.alert_service.create_alert(
                parent_id=alert_request.parent_id,
                child_id=alert_request.child_id,
                alert_type=alert_request.alert_type,
                severity=alert_request.severity,
                title=alert_request.title,
                message=alert_request.message,
                details=alert_request.details or {},
            )

            if alert:
                # Send notification
                await self._send_alert_notification(alert, alert_request)

                self.logger.info(
                    f"Successfully created and sent alert for child {alert_request.child_id}"
                )
                return True
            else:
                self.logger.warning(
                    f"Failed to create alert for child {alert_request.child_id}"
                )
                return False

        except Exception as e:
            self.logger.error(f"Error creating alert: {e}")
            return False

    async def send_moderation_alert(
        self, user_id: str, alert_type: str, severity: str, details: Dict[str, Any]
    ) -> bool:
        """Send moderation alert to parent - legacy interface"""
        try:
            # Get parent info (simplified)
            parent_id = await self._get_parent_id_for_child(user_id)

            if not parent_id:
                self.logger.warning(f"No parent found for child {user_id}")
                return False

            # Create alert request
            alert_request = AlertRequest(
                parent_id=parent_id,
                child_id=user_id,
                alert_type=alert_type,
                severity=severity,
                title=f"Moderation Alert - {severity.upper()}",
                message="Content moderation issue detected",
                details=details,
            )

            return await self.create_alert(alert_request)

        except Exception as e:
            self.logger.error(f"Error sending moderation alert: {e}")
            return False

    async def get_active_alerts(self, parent_id: str) -> List[Dict[str, Any]]:
        """Get active alerts for a parent"""
        try:
            alerts = await self.alert_service.get_active_alerts(parent_id)

            self.logger.debug(
                f"Retrieved {len(alerts)} active alerts for parent {parent_id}"
            )
            return alerts

        except Exception as e:
            self.logger.error(
                f"Failed to get active alerts for parent {parent_id}: {e}"
            )
            return []

    async def acknowledge_alert(self, alert_id: str, parent_id: str) -> bool:
        """Acknowledge an alert (mark as read)"""
        try:
            success = await self.alert_service.acknowledge_alert(alert_id, parent_id)

            if success:
                self.logger.info(
                    f"Alert {alert_id} acknowledged by parent {parent_id}")
            else:
                self.logger.warning(f"Failed to acknowledge alert {alert_id}")

            return success

        except Exception as e:
            self.logger.error(f"Error acknowledging alert {alert_id}: {e}")
            return False

    async def dismiss_alert(self, alert_id: str, parent_id: str) -> bool:
        """Dismiss an alert (remove from active list)"""
        try:
            success = await self.alert_service.dismiss_alert(alert_id, parent_id)

            if success:
                self.logger.info(
                    f"Alert {alert_id} dismissed by parent {parent_id}")
            else:
                self.logger.warning(f"Failed to dismiss alert {alert_id}")

            return success

        except Exception as e:
            self.logger.error(f"Error dismissing alert {alert_id}: {e}")
            return False

    async def get_alert_history(
        self, parent_id: str, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get alert history for a parent"""
        try:
            alerts = await self.alert_service.get_alert_history(parent_id, limit)

            self.logger.debug(
                f"Retrieved {len(alerts)} historical alerts for parent {parent_id}"
            )
            return alerts

        except Exception as e:
            self.logger.error(
                f"Failed to get alert history for parent {parent_id}: {e}"
            )
            return []

    async def update_notification_preferences(
        self, parent_id: str, preferences: Dict[str, Any]
    ) -> bool:
        """Update parent's notification preferences"""
        try:
            success = await self.notification_service.update_preferences(
                parent_id, preferences
            )

            if success:
                self.logger.info(
                    f"Updated notification preferences for parent {parent_id}"
                )
            else:
                self.logger.warning(
                    f"Failed to update preferences for parent {parent_id}"
                )

            return success

        except Exception as e:
            self.logger.error(f"Error updating notification preferences: {e}")
            return False

    def _validate_parental_controls(self, controls: Dict[str, Any]) -> bool:
        """Validate parental control settings"""
        required_fields = ["time_limits", "content_filters", "access_schedule"]

        for field in required_fields:
            if field not in controls:
                self.logger.warning(f"Missing required control field: {field}")
                return False

        # Validate time limits
        time_limits = controls.get("time_limits", {})
        if not isinstance(time_limits, dict):
            return False

        # Validate content filters
        content_filters = controls.get("content_filters", {})
        if not isinstance(content_filters, dict):
            return False

        return True

    async def _log_control_changes(
        self, child_id: str, controls: Dict[str, Any]
    ) -> None:
        """Log parental control changes for audit purposes"""
        try:
            # This would typically log to an audit trail
            self.logger.info(
                f"Parental controls updated for child {child_id}: "
                f"{list(controls.keys())}"
            )

            # Could also send to audit service if available

        except Exception as e:
            self.logger.error(f"Failed to log control changes: {e}")

    async def _apply_access_schedule(
        self, child_id: str, schedules: List[Dict]
    ) -> bool:
        """Apply access schedule to child account"""
        try:
            # This would typically update the database with schedule rules
            # For now, just log the action
            self.logger.info(
                f"Applied access schedule for child {child_id}: {len(schedules)} rules"
            )
            return True

        except Exception as e:
            self.logger.error(f"Failed to apply access schedule: {e}")
            return False

    async def _send_alert_notification(
        self, alert: Any, alert_request: AlertRequest
    ) -> None:
        """Send notification for the created alert"""
        try:
            # Get parent contact info (simplified)
            parent_email = "parent@example.com"  # Would get from database
            child_name = "Child Name"  # Would get from profile

            # Send email notification
            await self.notification_service.send_email_alert(
                recipient_email=parent_email,
                alert_title=alert_request.title,
                alert_message=alert_request.message,
                child_name=child_name,
                alert_details=alert_request.details or {},
            )

            self.logger.info(f"Sent email notification for alert {alert.id}")

        except Exception as e:
            self.logger.error(f"Failed to send alert notification: {e}")
            # Don't raise - notification failure shouldn't prevent alert
            # creation

    async def _get_parent_id_for_child(self, child_id: str) -> Optional[str]:
        """Get parent ID for a given child ID"""
        try:
            # This would typically query the database
            # For now, return a placeholder
            return "parent_id"  # Would get from child repository

        except Exception as e:
            self.logger.error(
                f"Failed to get parent ID for child {child_id}: {e}")
            return None

    def get_access_control_stats(self) -> Dict[str, Any]:
        """Get access control and alerts statistics"""
        return {
            "service_name": "AccessControlAlertsService",
            "operations": [
                "check_access_allowed",
                "update_parental_controls",
                "set_access_schedule",
                "create_alert",
                "send_moderation_alert",
                "get_active_alerts",
                "acknowledge_alert",
                "dismiss_alert",
                "get_alert_history",
                "update_notification_preferences",
            ],
            "high_cohesion": True,
            "responsibility": "Access control, alerts, and notification operations",
        }
