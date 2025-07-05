import logging
from typing import Any, Dict
from jinja2 import Template
from ..notification_models import NotificationData

logger = logging.getLogger(__name__)


class PushSender:
    """Handles sending push notifications."""

    def __init__(self, push_service: Any, push_template: Dict):
        self.push_service = push_service
        self.push_template = push_template

    async def send(self, notification: NotificationData) -> bool:
        """Sends a push notification."""
        try:
            template = Template(self.push_template["body"])
            body = template.render(
                child_name=notification.child_name,
                days_until_deletion=notification.days_until_deletion,
            )

            push_data = {
                "title": self.push_template["title"],
                "body": body,
                "data": {
                    "type": "data_cleanup_warning",
                    "child_udid": notification.child_udid,
                    "child_name": notification.child_name,
                    "days_until_deletion": str(notification.days_until_deletion),
                },
            }

            if self.push_service and notification.parent_device_id:
                success = await self.push_service.send_notification(
                    device_id=notification.parent_device_id, notification=push_data
                )
            else:
                success = True
                logger.info(
                    "Push notification simulated",
                    device_id=notification.parent_device_id,
                    child=notification.child_name,
                )
            return success
        except Exception as e:
            logger.error(
                "Failed to send push notification",
                child_udid=notification.child_udid,
                error=str(e),
            )
            return False
