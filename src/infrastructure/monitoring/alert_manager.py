"""
Alert Manager - نظام إدارة التنبيهات والإشعارات
يرسل تنبيهات فورية عند حدوث أخطاء critical أو مشاكل في النظام
"""

import asyncio
import os
import smtplib
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import Enum
from typing import Any, Dict, List, Optional

import aiohttp
import structlog

from src.domain.exceptions.base import ErrorCategory

logger = structlog.get_logger(__name__)


class AlertChannel(Enum):
    """قنوات إرسال التنبيهات"""

    EMAIL = "email"
    SMS = "sms"
    SLACK = "slack"
    WEBHOOK = "webhook"
    PUSH_NOTIFICATION = "push_notification"
    PAGERDUTY = "pagerduty"


class AlertPriority(Enum):
    """أولوية التنبيه"""

    P1 = "p1"  # Critical - يحتاج تدخل فوري
    P2 = "p2"  # High - يحتاج تدخل خلال ساعة
    P3 = "p3"  # Medium - يحتاج تدخل خلال يوم
    P4 = "p4"  # Low - معلومات فقط


@dataclass
class Alert:
    """نموذج التنبيه"""

    id: str
    title: str
    message: str
    priority: AlertPriority
    channels: List[AlertChannel]
    error_data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None
    deduplication_key: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """تحويل لـ dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "message": self.message,
            "priority": self.priority.value,
            "channels": [c.value for c in self.channels],
            "error_data": self.error_data,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class AlertThrottle:
    """معلومات throttling للتنبيهات"""

    last_sent: datetime
    count: int
    reset_time: datetime


class AlertManager:
    """مدير التنبيهات المركزي"""

    def __init__(self):
        self.alert_throttles: Dict[str, AlertThrottle] = {}
        self.alert_rules = self._load_alert_rules()
        self.channel_configs = self._load_channel_configs()
        self._session: Optional[aiohttp.ClientSession] = None

    def _load_alert_rules(self) -> Dict[str, Dict[str, Any]]:
        """تحميل قواعد التنبيهات"""
        return {
            ErrorCategory.CHILD_SAFETY.value: {
                "priority": AlertPriority.P1,
                "channels": [
                    AlertChannel.EMAIL,
                    AlertChannel.SMS,
                    AlertChannel.PUSH_NOTIFICATION,
                ],
                "throttle_minutes": 0,  # لا throttling لأمان الأطفال
                "escalation_enabled": True,
            },
            ErrorCategory.SECURITY.value: {
                "priority": AlertPriority.P1,
                "channels": [
                    AlertChannel.EMAIL,
                    AlertChannel.SLACK,
                    AlertChannel.PAGERDUTY,
                ],
                "throttle_minutes": 5,
                "escalation_enabled": True,
            },
            ErrorCategory.INFRASTRUCTURE.value: {
                "priority": AlertPriority.P2,
                "channels": [AlertChannel.SLACK, AlertChannel.WEBHOOK],
                "throttle_minutes": 15,
                "escalation_enabled": False,
            },
            ErrorCategory.PERFORMANCE.value: {
                "priority": AlertPriority.P3,
                "channels": [AlertChannel.SLACK],
                "throttle_minutes": 30,
                "escalation_enabled": False,
            },
        }

    def _load_channel_configs(self) -> Dict[str, Dict[str, Any]]:
        """تحميل إعدادات القنوات"""
        return {
            AlertChannel.EMAIL.value: {
                "smtp_host": os.getenv("SMTP_HOST", "smtp.gmail.com"),
                "smtp_port": int(os.getenv("SMTP_PORT", "587")),
                "smtp_user": os.getenv("SMTP_USER"),
                "smtp_password": os.getenv("SMTP_PASSWORD"),
                "from_email": os.getenv("ALERT_FROM_EMAIL", "alerts@teddybear.ai"),
                "to_emails": os.getenv("ALERT_TO_EMAILS", "").split(","),
            },
            AlertChannel.SLACK.value: {
                "webhook_url": os.getenv("SLACK_WEBHOOK_URL"),
                "channel": os.getenv("SLACK_ALERT_CHANNEL", "#alerts"),
                "username": "AI Teddy Bear Alerts",
            },
            AlertChannel.WEBHOOK.value: {
                "url": os.getenv("ALERT_WEBHOOK_URL"),
                "headers": {"Content-Type": "application/json"},
                "auth_token": os.getenv("ALERT_WEBHOOK_TOKEN"),
            },
            AlertChannel.PUSH_NOTIFICATION.value: {
                "fcm_server_key": os.getenv("FCM_SERVER_KEY"),
                "topic": "alerts",
            },
            AlertChannel.PAGERDUTY.value: {
                "integration_key": os.getenv("PAGERDUTY_INTEGRATION_KEY"),
                "api_url": "https://events.pagerduty.com/v2/enqueue",
            },
        }

    async def send_critical_alert(self, error_data: Dict[str, Any]) -> None:
        """إرسال تنبيه critical"""
        try:
            category = error_data.get("category", ErrorCategory.INFRASTRUCTURE.value)
            rule = self.alert_rules.get(
                category, self.alert_rules[ErrorCategory.INFRASTRUCTURE.value]
            )

            # Create alert
            alert = Alert(
                id=f"alert_{datetime.utcnow().timestamp()}",
                title=f"Critical Error: {error_data.get('error_code', 'UNKNOWN')}",
                message=self._format_alert_message(error_data),
                priority=rule["priority"],
                channels=[AlertChannel(c) for c in rule["channels"]],
                error_data=error_data,
                deduplication_key=self._generate_dedup_key(error_data),
            )

            # Check throttling
            if self._should_throttle(alert, rule.get("throttle_minutes", 15)):
                logger.info("Alert throttled", alert_id=alert.id)
                return

            # Send to all channels
            await self._send_to_channels(alert)

            # Update throttle
            self._update_throttle(alert)

            # Handle escalation if needed
            if rule.get("escalation_enabled", False):
                asyncio.create_task(self._handle_escalation(alert))

        except Exception as e:
            logger.error("Failed to send alert", error=str(e), exc_info=True)

    def _format_alert_message(self, error_data: Dict[str, Any]) -> str:
        """تنسيق رسالة التنبيه"""
        context = error_data.get("context", {})
        message = f"""
🚨 CRITICAL ALERT 🚨

Error Code: {error_data.get('error_code')}
Category: {error_data.get('category')}
Severity: {error_data.get('severity')}
Time: {error_data.get('timestamp', datetime.utcnow().isoformat())}

Message: {error_data.get('message')}

Context:
- Child ID: {context.get('child_id', 'N/A')}
- User ID: {context.get('user_id', 'N/A')}
- Session ID: {context.get('session_id', 'N/A')}
- Request ID: {context.get('request_id', 'N/A')}

Actions Required:
{self._format_actions(error_data.get('suggested_actions', []))}
"""
        return message.strip()

    def _format_actions(self, actions: List[str]) -> str:
        """تنسيق الإجراءات المطلوبة"""
        if not actions:
            return "- Review logs for more details"
        return "\n".join(f"- {action}" for action in actions)

    def _generate_dedup_key(self, error_data: Dict[str, Any]) -> str:
        """توليد مفتاح deduplication"""
        parts = [
            error_data.get("error_code", "UNKNOWN"),
            error_data.get("category", "unknown"),
            error_data.get("context", {}).get("child_id", ""),
            error_data.get("context", {}).get("user_id", ""),
        ]
        return "_".join(filter(None, parts))

    def _should_throttle(self, alert: Alert, throttle_minutes: int) -> bool:
        """التحقق من throttling"""
        if throttle_minutes == 0:
            return False

        key = alert.deduplication_key
        if not key:
            return False

        throttle = self.alert_throttles.get(key)
        if not throttle:
            return False

        if datetime.utcnow() > throttle.reset_time:
            # Reset throttle
            del self.alert_throttles[key]
            return False

        return throttle.count >= 3  # Max 3 alerts per throttle period

    def _update_throttle(self, alert: Alert) -> None:
        """تحديث throttle info"""
        key = alert.deduplication_key
        if not key:
            return

        throttle = self.alert_throttles.get(key)
        if not throttle:
            throttle = AlertThrottle(
                last_sent=datetime.utcnow(),
                count=1,
                reset_time=datetime.utcnow() + timedelta(minutes=15),
            )
            self.alert_throttles[key] = throttle
        else:
            throttle.count += 1
            throttle.last_sent = datetime.utcnow()

    async def _send_to_channels(self, alert: Alert) -> None:
        """إرسال التنبيه لجميع القنوات"""
        tasks = []
        for channel in alert.channels:
            if channel == AlertChannel.EMAIL:
                tasks.append(self._send_email(alert))
            elif channel == AlertChannel.SLACK:
                tasks.append(self._send_slack(alert))
            elif channel == AlertChannel.WEBHOOK:
                tasks.append(self._send_webhook(alert))
            elif channel == AlertChannel.PUSH_NOTIFICATION:
                tasks.append(self._send_push_notification(alert))
            elif channel == AlertChannel.PAGERDUTY:
                tasks.append(self._send_pagerduty(alert))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _send_email(self, alert: Alert) -> None:
        """إرسال email"""
        try:
            config = self.channel_configs[AlertChannel.EMAIL.value]
            if not config.get("smtp_user") or not config.get("to_emails"):
                logger.warning("Email not configured")
                return

            msg = MIMEMultipart()
            msg["From"] = config["from_email"]
            msg["To"] = ", ".join(config["to_emails"])
            msg["Subject"] = f"[{alert.priority.value.upper()}] {alert.title}"

            body = MIMEText(alert.message, "plain")
            msg.attach(body)

            # Send email in thread to avoid blocking
            await asyncio.get_event_loop().run_in_executor(
                None, self._send_email_sync, config, msg
            )

            logger.info("Email alert sent", alert_id=alert.id)

        except Exception as e:
            logger.error("Failed to send email alert", error=str(e))

    def _send_email_sync(self, config: Dict[str, Any], msg: MIMEMultipart) -> None:
        """إرسال email بشكل synchronous"""
        with smtplib.SMTP(config["smtp_host"], config["smtp_port"]) as server:
            server.starttls()
            server.login(config["smtp_user"], config["smtp_password"])
            server.send_message(msg)

    async def _send_slack(self, alert: Alert) -> None:
        """إرسال Slack notification"""
        try:
            config = self.channel_configs[AlertChannel.SLACK.value]
            webhook_url = config.get("webhook_url")
            if not webhook_url:
                logger.warning("Slack webhook not configured")
                return

            # Format message for Slack
            slack_message = {
                "channel": config["channel"],
                "username": config["username"],
                "icon_emoji": self._get_priority_emoji(alert.priority),
                "attachments": [
                    {
                        "color": self._get_priority_color(alert.priority),
                        "title": alert.title,
                        "text": alert.message,
                        "fields": [
                            {
                                "title": "Priority",
                                "value": alert.priority.value.upper(),
                                "short": True,
                            },
                            {
                                "title": "Category",
                                "value": alert.error_data.get("category", "Unknown"),
                                "short": True,
                            },
                            {
                                "title": "Error Code",
                                "value": alert.error_data.get("error_code", "Unknown"),
                                "short": True,
                            },
                            {
                                "title": "Time",
                                "value": alert.timestamp.strftime(
                                    "%Y-%m-%d %H:%M:%S UTC"
                                ),
                                "short": True,
                            },
                        ],
                        "footer": "AI Teddy Bear Alert System",
                        "ts": int(alert.timestamp.timestamp()),
                    }
                ],
            }

            if not self._session:
                self._session = aiohttp.ClientSession()

            async with self._session.post(webhook_url, json=slack_message) as response:
                if response.status == 200:
                    logger.info("Slack alert sent", alert_id=alert.id)
                else:
                    logger.error("Failed to send Slack alert", status=response.status)

        except Exception as e:
            logger.error("Failed to send Slack alert", error=str(e))

    def _get_priority_emoji(self, priority: AlertPriority) -> str:
        """الحصول على emoji حسب الأولوية"""
        mapping = {
            AlertPriority.P1: ":rotating_light:",
            AlertPriority.P2: ":warning:",
            AlertPriority.P3: ":information_source:",
            AlertPriority.P4: ":speech_balloon:",
        }
        return mapping.get(priority, ":bell:")

    def _get_priority_color(self, priority: AlertPriority) -> str:
        """الحصول على لون حسب الأولوية"""
        mapping = {
            AlertPriority.P1: "danger",
            AlertPriority.P2: "warning",
            AlertPriority.P3: "good",
            AlertPriority.P4: "#439FE0",
        }
        return mapping.get(priority, "warning")

    async def _send_webhook(self, alert: Alert) -> None:
        """إرسال webhook عام"""
        try:
            config = self.channel_configs[AlertChannel.WEBHOOK.value]
            url = config.get("url")
            if not url:
                logger.warning("Webhook URL not configured")
                return

            headers = config.get("headers", {})
            if config.get("auth_token"):
                headers["Authorization"] = f"Bearer {config['auth_token']}"

            if not self._session:
                self._session = aiohttp.ClientSession()

            async with self._session.post(
                url, json=alert.to_dict(), headers=headers
            ) as response:
                if response.status in (200, 201, 202):
                    logger.info("Webhook alert sent", alert_id=alert.id)
                else:
                    logger.error("Failed to send webhook alert", status=response.status)

        except Exception as e:
            logger.error("Failed to send webhook alert", error=str(e))

    async def _send_push_notification(self, alert: Alert) -> None:
        """إرسال push notification للوالدين"""
        try:
            config = self.channel_configs[AlertChannel.PUSH_NOTIFICATION.value]
            fcm_key = config.get("fcm_server_key")
            if not fcm_key:
                logger.warning("FCM not configured")
                return

            # Get parent tokens from context
            context = alert.error_data.get("context", {})
            child_id = context.get("child_id")
            if not child_id:
                return

            # TODO: Get parent FCM tokens from database
            parent_tokens = []  # await self._get_parent_tokens(child_id)

            if not parent_tokens:
                logger.warning("No parent tokens found", child_id=child_id)
                return

            # Send FCM notification
            fcm_data = {
                "registration_ids": parent_tokens,
                "notification": {
                    "title": f"⚠️ {alert.title}",
                    "body": alert.error_data.get("message", ""),
                    "icon": "notification_icon",
                    "sound": "default",
                },
                "data": {
                    "alert_id": alert.id,
                    "priority": alert.priority.value,
                    "category": alert.error_data.get("category"),
                    "child_id": child_id,
                },
                "priority": (
                    "high"
                    if alert.priority in (AlertPriority.P1, AlertPriority.P2)
                    else "normal"
                ),
            }

            if not self._session:
                self._session = aiohttp.ClientSession()

            async with self._session.post(
                "https://fcm.googleapis.com/fcm/send",
                json=fcm_data,
                headers={
                    "Authorization": f"key={fcm_key}",
                    "Content-Type": "application/json",
                },
            ) as response:
                if response.status == 200:
                    logger.info("Push notification sent", alert_id=alert.id)
                else:
                    logger.error(
                        "Failed to send push notification", status=response.status
                    )

        except Exception as e:
            logger.error("Failed to send push notification", error=str(e))

    async def _send_pagerduty(self, alert: Alert) -> None:
        """إرسال PagerDuty alert"""
        try:
            config = self.channel_configs[AlertChannel.PAGERDUTY.value]
            integration_key = config.get("integration_key")
            if not integration_key:
                logger.warning("PagerDuty not configured")
                return

            # Map our priority to PagerDuty severity
            severity_map = {
                AlertPriority.P1: "critical",
                AlertPriority.P2: "error",
                AlertPriority.P3: "warning",
                AlertPriority.P4: "info",
            }

            pd_event = {
                "routing_key": integration_key,
                "event_action": "trigger",
                "dedup_key": alert.deduplication_key,
                "payload": {
                    "summary": alert.title,
                    "source": "AI Teddy Bear",
                    "severity": severity_map.get(alert.priority, "error"),
                    "custom_details": {
                        "message": alert.message,
                        "error_code": alert.error_data.get("error_code"),
                        "category": alert.error_data.get("category"),
                        "context": alert.error_data.get("context", {}),
                    },
                },
            }

            if not self._session:
                self._session = aiohttp.ClientSession()

            async with self._session.post(
                config["api_url"],
                json=pd_event,
                headers={"Content-Type": "application/json"},
            ) as response:
                if response.status == 202:
                    logger.info("PagerDuty alert sent", alert_id=alert.id)
                else:
                    logger.error(
                        "Failed to send PagerDuty alert", status=response.status
                    )

        except Exception as e:
            logger.error("Failed to send PagerDuty alert", error=str(e))

    async def _handle_escalation(self, alert: Alert) -> None:
        """معالجة escalation للتنبيهات"""
        try:
            # Wait for initial response time
            await asyncio.sleep(300)  # 5 minutes

            # Check if alert is acknowledged
            # TODO: Implement acknowledgment checking

            # If not acknowledged, escalate
            logger.warning("Alert not acknowledged, escalating", alert_id=alert.id)

            # Send to additional channels or higher priority
            # TODO: Implement escalation logic

        except Exception as e:
            logger.error("Failed to handle escalation", error=str(e))

    async def close(self) -> None:
        """إغلاق الموارد"""
        if self._session:
            await self._session.close()
