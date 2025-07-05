"""
Enterprise-Grade Audit Logging System
Comprehensive audit trail for child safety and compliance
"""

import asyncio
import hashlib
import json
import logging
import os
import time
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiofiles
import structlog
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from pydantic import BaseModel, Field, validator

from domain.exceptions import SecurityException

logger = logging.getLogger(__name__)


class AuditEventType(Enum):
    """Types of audit events"""

    # Authentication events
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGOUT = "logout"
    PASSWORD_CHANGE = "password_change"
    PASSWORD_RESET = "password_reset"

    # Child interaction events
    CHILD_INTERACTION_START = "child_interaction_start"
    CHILD_INTERACTION_END = "child_interaction_end"
    VOICE_CAPTURE = "voice_capture"
    AI_RESPONSE = "ai_response"
    CONTENT_MODERATION = "content_moderation"

    # Safety events
    SAFETY_INCIDENT = "safety_incident"
    INAPPROPRIATE_CONTENT = "inappropriate_content"
    EMERGENCY_ALERT = "emergency_alert"
    PARENT_NOTIFICATION = "parent_notification"

    # Data events
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    DATA_DELETION = "data_deletion"
    DATA_EXPORT = "data_export"

    # System events
    SYSTEM_STARTUP = "system_startup"
    SYSTEM_SHUTDOWN = "system_shutdown"
    CONFIGURATION_CHANGE = "configuration_change"
    SECURITY_ALERT = "security_alert"

    # Compliance events
    COPPA_CONSENT = "coppa_consent"
    GDPR_REQUEST = "gdpr_request"
    DATA_RETENTION = "data_retention"
    AUDIT_REPORT = "audit_report"


class AuditSeverity(Enum):
    """Audit event severity levels"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AuditCategory(Enum):
    """Audit event categories"""

    AUTHENTICATION = "authentication"
    CHILD_SAFETY = "child_safety"
    DATA_PROTECTION = "data_protection"
    SYSTEM_SECURITY = "system_security"
    COMPLIANCE = "compliance"
    PERFORMANCE = "performance"


@dataclass
class AuditContext:
    """Context information for audit events"""

    user_id: Optional[str] = None
    child_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    correlation_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    device_id: Optional[str] = None
    location: Optional[str] = None
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(
            timezone.utc))


@dataclass
class AuditEvent:
    """Audit event structure"""

    event_id: str
    event_type: AuditEventType
    severity: AuditSeverity
    category: AuditCategory
    timestamp: datetime
    context: AuditContext
    description: str
    details: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    hash: Optional[str] = None

    def __post_init__(self):
        """Generate hash for tamper detection"""
        if not self.hash:
            self.hash = self._generate_hash()

    def _generate_hash(self) -> str:
        """Generate SHA-256 hash for tamper detection"""
        data = {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "severity": self.severity.value,
            "category": self.category.value,
            "timestamp": self.timestamp.isoformat(),
            "description": self.description,
            "details": json.dumps(self.details, sort_keys=True),
        }

        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()


class AuditConfig(BaseModel):
    """Configuration for audit logging"""

    # Storage settings
    log_directory: Path = Field(
        default=Path("./audit_logs"), description="Audit log directory"
    )
    max_file_size_mb: int = Field(
        default=100, description="Maximum log file size in MB"
    )
    max_files: int = Field(
        default=100,
        description="Maximum number of log files")
    retention_days: int = Field(
        default=2555, description="Log retention period in days"
    )  # 7 years for COPPA

    # Security settings
    enable_encryption: bool = Field(
        default=True, description="Encrypt audit logs")
    enable_tamper_detection: bool = Field(
        default=True, description="Enable tamper detection"
    )
    enable_compression: bool = Field(
        default=True, description="Compress old logs")

    # Performance settings
    batch_size: int = Field(
        default=100,
        description="Batch size for log writes")
    flush_interval_seconds: float = Field(
        default=5.0, description="Log flush interval")
    async_writing: bool = Field(
        default=True,
        description="Use async log writing")

    # Monitoring settings
    enable_real_time_monitoring: bool = Field(
        default=True, description="Enable real-time monitoring"
    )
    alert_threshold_events_per_minute: int = Field(
        default=1000, description="Alert threshold"
    )
    critical_event_types: List[str] = Field(
        default_factory=lambda: [
            "safety_incident",
            "emergency_alert",
            "security_alert"])

    class Config:
        validate_assignment = True


class AuditLogWriter:
    """Thread-safe audit log writer with encryption"""

    def __init__(self, config: AuditConfig):
        self.config = config
        self.log_directory = config.log_directory
        self.log_directory.mkdir(parents=True, exist_ok=True)

        # Encryption key
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)

        # Log file management
        self.current_file = None
        self.current_file_path = None
        self.event_count = 0

        # Batch processing
        self.event_buffer: List[AuditEvent] = []
        self.last_flush = time.time()

        # Thread safety
        self._lock = asyncio.Lock()

        logger.info(f"🔐 Audit log writer initialized at {self.log_directory}")

    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for audit logs"""
        key_file = self.log_directory / ".audit_key"

        if key_file.exists():
            with open(key_file, "rb") as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, "wb") as f:
                f.write(key)
            # Set restrictive permissions
            os.chmod(key_file, 0o600)
            return key

    def _get_current_log_file(self) -> Path:
        """Get current log file path based on date"""
        today = datetime.now().date()
        return self.log_directory / f"audit_{today.isoformat()}.log.enc"

    async def write_event(self, event: AuditEvent):
        """Write audit event to log file"""
        async with self._lock:
            self.event_buffer.append(event)
            self.event_count += 1

            # Check if we need to flush
            if (len(self.event_buffer) >= self.config.batch_size or time.time(
            ) - self.last_flush >= self.config.flush_interval_seconds):
                await self._flush_buffer()

    async def _flush_buffer(self):
        """Flush event buffer to log file"""
        if not self.event_buffer:
            return

        try:
            # Get current log file
            log_file = self._get_current_log_file()

            # Rotate file if needed
            if (log_file.exists() and log_file.stat().st_size >
                    self.config.max_file_size_mb * 1024 * 1024):
                await self._rotate_log_file(log_file)

            # Write events
            events_data = []
            for event in self.event_buffer:
                event_dict = asdict(event)
                event_dict["timestamp"] = event.timestamp.isoformat()
                events_data.append(event_dict)

            # Encrypt and write
            data = json.dumps(
                events_data,
                ensure_ascii=False,
                separators=(
                    ",",
                    ":"))
            encrypted_data = self.cipher_suite.encrypt(data.encode())

            async with aiofiles.open(log_file, "ab") as f:
                await f.write(encrypted_data + b"\n")

            # Clear buffer
            self.event_buffer.clear()
            self.last_flush = time.time()

        except Exception as e:
            logger.error(f"❌ Failed to flush audit buffer: {e}")
            # Don't lose events - keep them in buffer for retry

    async def _rotate_log_file(self, current_file: Path):
        """Rotate log file when it gets too large"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_file = current_file.parent / \
            f"{current_file.stem}_{timestamp}.log.enc"
        current_file.rename(new_file)

        # Clean up old files
        await self._cleanup_old_files()

    async def _cleanup_old_files(self):
        """Clean up old log files based on retention policy"""
        cutoff_date = datetime.now() - timedelta(days=self.config.retention_days)

        for log_file in self.log_directory.glob("audit_*.log.enc"):
            try:
                file_date_str = log_file.stem.split("_")[
                    1
                ]  # Extract date from filename
                file_date = datetime.strptime(file_date_str, "%Y-%m-%d").date()

                if file_date < cutoff_date.date():
                    log_file.unlink()
                    logger.info(f"🗑️ Deleted old audit log: {log_file}")
            except Exception as e:
                logger.warning(
                    f"⚠️ Failed to process log file {log_file}: {e}")


class AuditMonitor:
    """Real-time audit monitoring and alerting"""

    def __init__(self, config: AuditConfig):
        self.config = config
        self.event_counters: Dict[str, int] = {}
        self.last_reset = time.time()
        self.alert_handlers: List[callable] = []

        logger.info("🔍 Audit monitor initialized")

    def register_alert_handler(self, handler: callable):
        """Register alert handler function"""
        self.alert_handlers.append(handler)

    async def process_event(self, event: AuditEvent):
        """Process audit event for monitoring"""
        current_time = time.time()

        # Reset counters every minute
        if current_time - self.last_reset >= 60:
            self.event_counters.clear()
            self.last_reset = current_time

        # Update counters
        event_type = event.event_type.value
        self.event_counters[event_type] = self.event_counters.get(
            event_type, 0) + 1

        # Check for critical events
        if event.event_type.value in self.config.critical_event_types:
            await self._handle_critical_event(event)

        # Check rate limits
        total_events = sum(self.event_counters.values())
        if total_events > self.config.alert_threshold_events_per_minute:
            await self._handle_rate_limit_exceeded(total_events)

    async def _handle_critical_event(self, event: AuditEvent):
        """Handle critical audit events"""
        alert_message = f"🚨 CRITICAL AUDIT EVENT: {event.event_type.value}"
        alert_data = {
            "event_id": event.event_id,
            "event_type": event.event_type.value,
            "severity": event.severity.value,
            "timestamp": event.timestamp.isoformat(),
            "description": event.description,
            "context": asdict(event.context),
        }

        logger.critical(alert_message, **alert_data)

        # Send alerts to all handlers
        for handler in self.alert_handlers:
            try:
                await handler(alert_message, alert_data)
            except Exception as e:
                logger.error(f"❌ Alert handler failed: {e}")

    async def _handle_rate_limit_exceeded(self, total_events: int):
        """Handle rate limit exceeded"""
        alert_message = f"⚠️ AUDIT RATE LIMIT EXCEEDED: {total_events} events/minute"

        logger.warning(alert_message, total_events=total_events)

        for handler in self.alert_handlers:
            try:
                await handler(alert_message, {"total_events": total_events})
            except Exception as e:
                logger.error(f"❌ Rate limit alert handler failed: {e}")


class AuditLogger:
    """Main audit logging system"""

    def __init__(self, config: Optional[AuditConfig] = None):
        self.config = config or AuditConfig()
        self.writer = AuditLogWriter(self.config)
        self.monitor = AuditMonitor(self.config)
        self.structured_logger = self._setup_structured_logger()

        # Register default alert handlers
        self.monitor.register_alert_handler(self._default_alert_handler)

        logger.info("📋 Audit logger initialized")

    def _setup_structured_logger(self) -> structlog.BoundLogger:
        """Setup structured logger for audit events"""
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer(),
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        return structlog.get_logger("audit")

    async def _default_alert_handler(self, message: str, data: Dict[str, Any]):
        """Default alert handler"""
        # TODO: Integrate with external alerting systems (Slack, email, etc.)
        logger.warning(f"🚨 AUDIT ALERT: {message}", **data)

    async def log_event(
        self,
        event_type: AuditEventType,
        severity: AuditSeverity,
        category: AuditCategory,
        description: str,
        context: Optional[AuditContext] = None,
        details: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Log audit event"""
        # Generate event ID
        event_id = f"audit_{int(time.time() * 1000000)}"

        # Create context
        if not context:
            context = AuditContext()

        # Create event
        event = AuditEvent(
            event_id=event_id,
            event_type=event_type,
            severity=severity,
            category=category,
            timestamp=datetime.now(timezone.utc),
            context=context,
            description=description,
            details=details or {},
            metadata=metadata or {},
        )

        # Write to log
        await self.writer.write_event(event)

        # Process for monitoring
        await self.monitor.process_event(event)

        # Log to structured logger
        self.structured_logger.info(
            "📋 Audit event logged",
            event_id=event_id,
            event_type=event_type.value,
            severity=severity.value,
            category=category.value,
            description=description,
            **details or {},
        )

        return event_id

    async def log_child_interaction(
        self,
        child_id: str,
        interaction_type: str,
        content: Optional[str] = None,
        response: Optional[str] = None,
        safety_score: Optional[float] = None,
        context: Optional[AuditContext] = None,
    ) -> str:
        """Log child interaction event"""
        if not context:
            context = AuditContext(child_id=child_id)
        else:
            context.child_id = child_id

        details = {
            "interaction_type": interaction_type,
            "content_length": len(content) if content else 0,
            "response_length": len(response) if response else 0,
            "safety_score": safety_score,
        }

        if safety_score and safety_score < 0.7:
            event_type = AuditEventType.SAFETY_INCIDENT
            severity = AuditSeverity.WARNING
        else:
            event_type = AuditEventType.CHILD_INTERACTION_START
            severity = AuditSeverity.INFO

        return await self.log_event(
            event_type=event_type,
            severity=severity,
            category=AuditCategory.CHILD_SAFETY,
            description=f"Child interaction: {interaction_type}",
            context=context,
            details=details,
        )

    async def log_safety_incident(
        self,
        child_id: str,
        incident_type: str,
        severity: AuditSeverity,
        description: str,
        details: Optional[Dict[str, Any]] = None,
        context: Optional[AuditContext] = None,
    ) -> str:
        """Log safety incident"""
        if not context:
            context = AuditContext(child_id=child_id)
        else:
            context.child_id = child_id

        incident_details = {
            "incident_type": incident_type,
            "child_id": child_id,
            **(details or {}),
        }

        return await self.log_event(
            event_type=AuditEventType.SAFETY_INCIDENT,
            severity=severity,
            category=AuditCategory.CHILD_SAFETY,
            description=description,
            context=context,
            details=incident_details,
        )

    async def log_data_access(
        self,
        user_id: str,
        data_type: str,
        operation: str,
        resource_id: Optional[str] = None,
        context: Optional[AuditContext] = None,
    ) -> str:
        """Log data access event"""
        if not context:
            context = AuditContext(user_id=user_id)
        else:
            context.user_id = user_id

        details = {
            "data_type": data_type,
            "operation": operation,
            "resource_id": resource_id,
        }

        return await self.log_event(
            event_type=AuditEventType.DATA_ACCESS,
            severity=AuditSeverity.INFO,
            category=AuditCategory.DATA_PROTECTION,
            description=f"Data {operation}: {data_type}",
            context=context,
            details=details,
        )

    async def generate_compliance_report(
        self,
        start_date: datetime,
        end_date: datetime,
        report_type: str = "coppa",
    ) -> Dict[str, Any]:
        """Generate compliance report"""
        # TODO: Implement compliance report generation
        # This would read from audit logs and generate structured reports
        return {
            "report_type": report_type,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "total_events": 0,
                "safety_incidents": 0,
                "data_access_events": 0,
                "authentication_events": 0,
            },
            "details": [],
        }


# Global audit logger instance
audit_logger = AuditLogger()


# Convenience functions
async def log_audit_event(
    event_type: AuditEventType,
    severity: AuditSeverity,
    category: AuditCategory,
    description: str,
    **kwargs,
) -> str:
    """Convenience function for logging audit events"""
    return await audit_logger.log_event(
        event_type=event_type,
        severity=severity,
        category=category,
        description=description,
        **kwargs,
    )


async def log_child_safety_incident(
    child_id: str,
    incident_type: str,
    description: str,
    severity: AuditSeverity = AuditSeverity.WARNING,
    **kwargs,
) -> str:
    """Convenience function for logging child safety incidents"""
    return await audit_logger.log_safety_incident(
        child_id=child_id,
        incident_type=incident_type,
        severity=severity,
        description=description,
        **kwargs,
    )
