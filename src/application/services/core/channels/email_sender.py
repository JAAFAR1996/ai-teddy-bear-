import logging
from typing import Any
from jinja2 import Template
from ..notification_models import NotificationData

logger = logging.getLogger(__name__)


class EmailSender:
    """Handles sending email notifications."""

    def __init__(self, email_service: Any, email_template_html: str):
        self.email_service = email_service
        self.email_template_html = email_template_html

    async def send(self, notification: NotificationData) -> bool:
        """Sends an email notification."""
        try:
            template = Template(self.email_template_html)
            html_content = template.render(
                child_name=notification.child_name,
                sessions_count=notification.sessions_count,
                oldest_date=notification.oldest_date,
                newest_date=notification.newest_date,
                days_until_deletion=notification.days_until_deletion,
            )

            subject = f"🧸 تنبيه مهم: بيانات {notification.child_name} ستحذف خلال {notification.days_until_deletion} أيام"

            if self.email_service:
                success = await self.email_service.send_html_email(
                    to_email=notification.parent_email,
                    subject=subject,
                    html_content=html_content,
                )
            else:
                success = True
                logger.info(
                    "Email notification simulated",
                    to=notification.parent_email,
                    child=notification.child_name,
                )
            return success
        except Exception as e:
            logger.error(
                "Failed to send email notification",
                child_udid=notification.child_udid,
                error=str(e),
            )
            return False
