"""
Alerting system for exception management.
"""

import aiohttp
import structlog

from .exceptions import ExceptionSeverity, TeddyBearException

logger = structlog.get_logger(__name__)


class AlertManager:
    """Manages alerts for exceptions"""

    def __init__(self):
        self.webhook_url = None  # Configure with actual webhook
        self.email_service = None  # Configure with email service

    async def send_alert(self, exception: TeddyBearException):
        """Send appropriate alerts based on exception severity"""
        if exception.severity == ExceptionSeverity.CRITICAL:
            # Send to all channels
            await self._send_webhook_alert(exception)
            await self._send_email_alert(exception)
            await self._send_pager_alert(exception)
        elif exception.severity == ExceptionSeverity.HIGH:
            # Send to webhook and email
            await self._send_webhook_alert(exception)
            await self._send_email_alert(exception)
        else:
            # Just webhook
            await self._send_webhook_alert(exception)

    async def _send_webhook_alert(self, exception: TeddyBearException):
        """Send alert to webhook (Slack, Discord, etc.)"""
        if not self.webhook_url:
            return

        payload = {
            "text": f"🚨 Exception Alert: {exception.error_code}",
            "attachments": [
                {
                    "color": self._get_severity_color(exception.severity),
                    "fields": [
                        {
                            "title": "Error Code",
                            "value": exception.error_code,
                            "short": True,
                        },
                        {
                            "title": "Severity",
                            "value": exception.severity.name,
                            "short": True,
                        },
                        {
                            "title": "Domain",
                            "value": exception.domain.name,
                            "short": True,
                        },
                        {
                            "title": "Message",
                            "value": exception.message,
                            "short": False,
                        },
                        {
                            "title": "Correlation ID",
                            "value": exception.context.correlation_id,
                            "short": True,
                        },
                        {
                            "title": "Environment",
                            "value": exception.context.environment,
                            "short": True,
                        },
                    ],
                }
            ],
        }

        try:
            async with aiohttp.ClientSession() as session:
                await session.post(self.webhook_url, json=payload)
        except Exception as e:
            logger.error("Failed to send webhook alert", error=str(e))

    async def _send_email_alert(self, exception: TeddyBearException):
        """Send email alert"""
        # Implementation depends on email service
        pass

    async def _send_pager_alert(self, exception: TeddyBearException):
        """Send pager alert for critical issues"""
        # Implementation depends on pager service (PagerDuty, etc.)
        pass

    def _get_severity_color(self, severity: ExceptionSeverity) -> str:
        """Get color for severity level"""
        return {
            ExceptionSeverity.CRITICAL: "#FF0000",  # Red
            ExceptionSeverity.HIGH: "#FF8C00",  # Dark Orange
            ExceptionSeverity.MEDIUM: "#FFD700",  # Gold
            ExceptionSeverity.LOW: "#90EE90",  # Light Green
        }.get(
            severity, "#808080"
        )  # Gray default
