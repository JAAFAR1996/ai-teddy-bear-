import logging
from typing import Any
from jinja2 import Template
from ..notification_models import NotificationData

logger = logging.getLogger(__name__)


class SmsSender:
    """Handles sending SMS notifications."""

    def __init__(self, sms_service: Any, sms_template: str):
        self.sms_service = sms_service
        self.sms_template = sms_template

    async def send(self, notification: NotificationData) -> bool:
        """Sends an SMS notification."""
        try:
            template = Template(self.sms_template)
            message = template.render(
                child_name=notification.child_name,
                days_until_deletion=notification.days_until_deletion,
            )

            if self.sms_service and notification.parent_phone:
                success = await self.sms_service.send_sms(
                    phone_number=notification.parent_phone, message=message
                )
            else:
                success = True
                logger.info(
                    "SMS notification simulated",
                    phone=notification.parent_phone,
                    child=notification.child_name,
                )
            return success
        except Exception as e:
            logger.error(
                "Failed to send SMS notification",
                child_udid=notification.child_udid,
                error=str(e),
            )
            return False
