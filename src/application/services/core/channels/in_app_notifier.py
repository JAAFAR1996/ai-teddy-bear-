import logging
from datetime import datetime, timedelta
from ..notification_models import NotificationData

logger = logging.getLogger(__name__)


class InAppNotifier:
    """Handles sending in-app notifications."""

    async def send(self, notification: NotificationData) -> bool:
        """Sends an in-app notification."""
        try:
            in_app_data = {
                "type": "data_cleanup_warning",
                "title": "🧸 تنبيه مهم من AI Teddy",
                "message": f"بيانات {notification.child_name} ستحذف خلال {notification.days_until_deletion} أيام",
                "child_udid": notification.child_udid,
                "created_at": datetime.utcnow().isoformat(),
                "is_read": False,
                "priority": "high",
                "action_url": "/data-export",
                "expires_at": (datetime.utcnow() + timedelta(days=3)).isoformat(),
            }

            logger.info(
                "In-app notification created",
                child_udid=notification.child_udid,
                notification_data=in_app_data,
            )
            return True
        except Exception as e:
            logger.error(
                "Failed to create in-app notification",
                child_udid=notification.child_udid,
                error=str(e),
            )
            return False
