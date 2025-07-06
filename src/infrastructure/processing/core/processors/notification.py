"""
Task processor for sending notifications.
"""
import asyncio

from ..models import ProcessingTask


async def process_notification(task: ProcessingTask) -> dict:
    """
    Processes a notification task. In a real implementation, this would
    integrate with an email, SMS, or push notification service.
    """
    recipient = task.payload.get("recipient")
    message = task.payload.get("message")
    if not recipient or not message:
        raise ValueError(
            "Recipient and message are required for notifications.")

    # Mock notification sending
    await asyncio.sleep(0.15)

    return {
        "status": "sent",
        "recipient": recipient,
        "channel": task.payload.get("channel", "email"),
    }
