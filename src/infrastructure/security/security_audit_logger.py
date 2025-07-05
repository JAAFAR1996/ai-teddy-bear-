from typing import Any, Dict, List, Optional

"""
🔐 Security Audit Logger - Comprehensive Audit Trail
====================================================

Advanced audit logging for security operations with:
- Structured security event logging
- Real-time threat detection
- Compliance reporting
- Event correlation
- Automated alerting

Author: Jaafar Adeeb - Security Lead
"""

import asyncio
import hashlib
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

import structlog

logger = structlog.get_logger(__name__)


class SecurityEventType(Enum):
    """Security event types for audit logging"""

    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGOUT = "logout"
    PASSWORD_CHANGE = "password_change"
    PASSWORD_RESET = "password_reset"
    ACCOUNT_LOCKOUT = "account_lockout"
    ACCOUNT_UNLOCK = "account_unlock"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    PERMISSION_DENIED = "permission_denied"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    DATA_DELETION = "data_deletion"
    AUDIO_RECORDING = "audio_recording"
    AUDIO_PLAYBACK = "audio_playback"
    CONVERSATION_START = "conversation_start"
    CONVERSATION_END = "conversation_end"
    DEVICE_REGISTRATION = "device_registration"
    DEVICE_DEREGISTRATION = "device_deregistration"
    FAMILY_CREATION = "family_creation"
    FAMILY_MEMBER_ADDED = "family_member_added"
    FAMILY_MEMBER_REMOVED = "family_member_removed"
    PARENTAL_CONTROL_CHANGE = "parental_control_change"
    CHILD_INTERACTION = "child_interaction"
    ENCRYPTION_OPERATION = "encryption_operation"
    DECRYPTION_OPERATION = "decryption_operation"
    KEY_ROTATION = "key_rotation"
    TOKEN_ISSUED = "token_issued"
    TOKEN_REVOKED = "token_revoked"
    API_ACCESS = "api_access"
    CONFIGURATION_CHANGE = "configuration_change"
    SECURITY_POLICY_CHANGE = "security_policy_change"
    VULNERABILITY_DETECTED = "vulnerability_detected"
    INCIDENT_CREATED = "incident_created"
    INCIDENT_RESOLVED = "incident_resolved"


class ThreatLevel(Enum):
    """Threat level classification"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ComplianceStandard(Enum):
    """Compliance standards"""

    COPPA = "coppa"
    GDPR = "gdpr"
    CCPA = "ccpa"
    SOX = "sox"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"


@dataclass
class SecurityEvent:
    """Security event data structure"""

    event_id: str
    event_type: SecurityEventType
    timestamp: datetime
    user_id: Optional[str] = None
    username: Optional[str] = None
    session_id: Optional[str] = None
    device_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    resource: Optional[str] = None
    action: Optional[str] = None
    result: str = "success"
    threat_level: ThreatLevel = ThreatLevel.LOW
    details: Dict[str, Any] = field(default_factory=dict)
    compliance_flags: List[ComplianceStandard] = field(default_factory=list)
    correlation_id: Optional[str] = None
    parent_event_id: Optional[str] = None
    child_event_ids: List[str] = field(default_factory=list)
    sensitive_data_involved: bool = False
    data_retention_days: int = 2555  # 7 years default

    def __post_init__(self):
        if not self.event_id:
            # Generate unique event ID
            timestamp_str = self.timestamp.isoformat()
            event_data = (
                f"{timestamp_str}:{self.event_type.value}:{self.user_id or 'anonymous'}"
            )
            self.event_id = hashlib.sha256(
                event_data.encode()).hexdigest()[:16]


@dataclass
class AuditLogEntry:
    """Audit log entry with enriched metadata"""

    event: SecurityEvent
    enriched_data: Dict[str, Any] = field(default_factory=dict)
    risk_score: float = 0.0
    automated_response: Optional[str] = None
    investigation_status: str = "none"  # none, pending, in_progress, resolved
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SecurityEventContext:
    """Context for a security event, to reduce parameter count."""

    user_id: Optional[str] = None
    username: Optional[str] = None
    session_id: Optional[str] = None
    device_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    resource: Optional[str] = None
    action: Optional[str] = None
    result: str = "success"
    details: Optional[Dict[str, Any]] = None
    correlation_id: Optional[str] = None
    sensitive_data_involved: bool = False


class SecurityAuditLogger:
    """Comprehensive security audit logging system"""

    def __init__(self, storage_backend: Optional[Any] = None):
        self.storage_backend = storage_backend
        self.event_buffer: List[AuditLogEntry] = []
        self.buffer_size = 1000
        self.buffer_lock = asyncio.Lock()

        # Event correlation
        self.correlation_map: Dict[str, List[str]] = {}
        self.session_events: Dict[str, List[str]] = {}

        # Threat detection patterns
        self.threat_patterns = self._initialize_threat_patterns()

        # Compliance mapping
        self.compliance_event_mapping = self._initialize_compliance_mapping()

        # Real-time monitoring
        self.alerting_rules = self._initialize_alerting_rules()
        self.event_counts: Dict[str, int] = {}

        # Background tasks
        self._monitoring_tasks: List[asyncio.Task] = []
        self._start_background_tasks()

    def _initialize_threat_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize threat detection patterns"""
        return {
            "brute_force_login": {
                "event_types": [SecurityEventType.LOGIN_FAILURE],
                "threshold": 5,
                "time_window": 300,  # 5 minutes
                "threat_level": ThreatLevel.HIGH,
            },
            "suspicious_data_access": {
                "event_types": [SecurityEventType.DATA_ACCESS],
                "threshold": 100,
                "time_window": 3600,  # 1 hour
                "threat_level": ThreatLevel.MEDIUM,
            },
            "unauthorized_access_pattern": {
                "event_types": [
                    SecurityEventType.UNAUTHORIZED_ACCESS,
                    SecurityEventType.PERMISSION_DENIED,
                ],
                "threshold": 3,
                "time_window": 60,  # 1 minute
                "threat_level": ThreatLevel.HIGH,
            },
            "child_safety_concern": {
                "event_types": [SecurityEventType.CHILD_INTERACTION],
                "threshold": 50,
                "time_window": 3600,
                "threat_level": ThreatLevel.MEDIUM,
            },
        }

    def _initialize_compliance_mapping(
        self,
    ) -> Dict[SecurityEventType, List[ComplianceStandard]]:
        """Initialize compliance standard mapping"""
        return {
            SecurityEventType.CHILD_INTERACTION: [ComplianceStandard.COPPA],
            SecurityEventType.AUDIO_RECORDING: [
                ComplianceStandard.COPPA,
                ComplianceStandard.GDPR,
            ],
            SecurityEventType.DATA_ACCESS: [
                ComplianceStandard.GDPR,
                ComplianceStandard.CCPA,
            ],
            SecurityEventType.DATA_MODIFICATION: [
                ComplianceStandard.GDPR,
                ComplianceStandard.CCPA,
            ],
            SecurityEventType.DATA_DELETION: [
                ComplianceStandard.GDPR,
                ComplianceStandard.CCPA,
            ],
            SecurityEventType.FAMILY_CREATION: [
                ComplianceStandard.COPPA,
                ComplianceStandard.GDPR,
            ],
            SecurityEventType.DEVICE_REGISTRATION: [ComplianceStandard.COPPA],
            SecurityEventType.LOGIN_SUCCESS: [ComplianceStandard.SOX],
            SecurityEventType.CONFIGURATION_CHANGE: [ComplianceStandard.SOX],
        }

    def _initialize_alerting_rules(self) -> List[Dict[str, Any]]:
        """Initialize real-time alerting rules"""
        return [
            {
                "name": "critical_security_event",
                "condition": lambda event: event.threat_level == ThreatLevel.CRITICAL,
                "alert_immediately": True,
                "notification_channels": ["security_team", "soc"],
            },
            {
                "name": "child_safety_alert",
                "condition": lambda event: event.event_type
                == SecurityEventType.CHILD_INTERACTION
                and event.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL],
                "alert_immediately": True,
                "notification_channels": ["parent", "child_safety_team"],
            },
            {
                "name": "data_breach_indicator",
                "condition": lambda event: event.event_type
                in [
                    SecurityEventType.UNAUTHORIZED_ACCESS,
                    SecurityEventType.DATA_ACCESS,
                ]
                and event.threat_level == ThreatLevel.HIGH,
                "alert_immediately": True,
                "notification_channels": ["security_team", "legal", "ciso"],
            },
        ]

    def _create_event_from_context(
        self, event_type: SecurityEventType, context: SecurityEventContext
    ) -> SecurityEvent:
        """Create a SecurityEvent object from the given context."""
        return SecurityEvent(
            event_id="",  # Will be generated in __post_init__
            event_type=event_type,
            timestamp=datetime.utcnow(),
            user_id=context.user_id,
            username=context.username,
            session_id=context.session_id,
            device_id=context.device_id,
            ip_address=context.ip_address,
            user_agent=context.user_agent,
            resource=context.resource,
            action=context.action,
            result=context.result,
            details=context.details or {},
            correlation_id=context.correlation_id,
            sensitive_data_involved=context.sensitive_data_involved,
        )

    async def _process_event(self, event: SecurityEvent) -> AuditLogEntry:
        """Enrich, score, and respond to an event, returning an AuditLogEntry."""
        await self._enrich_event(event)
        log_entry = AuditLogEntry(event=event)
        log_entry.risk_score = await self._calculate_risk_score(event)
        log_entry.automated_response = await self._check_automated_response(event)
        return log_entry

    async def _finalize_event_logging(
        self, event: SecurityEvent, log_entry: AuditLogEntry
    ):
        """Handle event buffering, threat detection, alerting, and correlations."""
        async with self.buffer_lock:
            self.event_buffer.append(log_entry)
            if len(self.event_buffer) >= self.buffer_size:
                await self._flush_buffer()

        await self._detect_threats(event)
        await self._check_alerting_rules(event)
        await self._update_correlations(event)

    async def log_security_event(
        self,
        event_type: SecurityEventType,
        context: SecurityEventContext,
    ) -> str:
        """Log a security event using a context object."""
        event = self._create_event_from_context(event_type, context)
        log_entry = await self._process_and_finalize_event(event)
        self._log_event_info(event, log_entry)
        return event.event_id

    async def _process_and_finalize_event(self, event: SecurityEvent) -> AuditLogEntry:
        """Process and finalize a single security event."""
        log_entry = await self._process_event(event)
        await self._finalize_event_logging(event, log_entry)
        return log_entry

    def _log_event_info(self, event: SecurityEvent, log_entry: AuditLogEntry):
        """Log informational message about the event."""
        logger.info(
            "Security event logged",
            event_id=event.event_id,
            event_type=event.event_type.value,
            user_id=event.user_id,
            threat_level=event.threat_level.value,
            risk_score=log_entry.risk_score,
        )

    async def _enrich_event(self, event: SecurityEvent):
        """Enrich event with additional metadata"""

        # Add compliance flags
        if event.event_type in self.compliance_event_mapping:
            event.compliance_flags = self.compliance_event_mapping[event.event_type]

        # Determine threat level based on event type and context
        if event.result != "success":
            if event.event_type in [
                SecurityEventType.LOGIN_FAILURE,
                SecurityEventType.UNAUTHORIZED_ACCESS,
            ]:
                event.threat_level = ThreatLevel.MEDIUM
            elif event.event_type == SecurityEventType.PERMISSION_DENIED:
                event.threat_level = ThreatLevel.LOW

        # Special handling for child-related events
        if event.event_type in [
            SecurityEventType.CHILD_INTERACTION,
            SecurityEventType.AUDIO_RECORDING,
        ]:
            event.sensitive_data_involved = True
            event.data_retention_days = 2555  # 7 years for child data

        # Add geolocation if IP address provided
        if event.ip_address:
            event.details["geolocation"] = await self._get_geolocation(event.ip_address)

        # Add device information
        if event.device_id:
            event.details["device_info"] = await self._get_device_info(event.device_id)

    async def _calculate_risk_score(self, event: SecurityEvent) -> float:
        """Calculate risk score for the event"""

        score = 0.0

        # Base score by event type
        event_scores = {
            SecurityEventType.LOGIN_FAILURE: 2.0,
            SecurityEventType.UNAUTHORIZED_ACCESS: 8.0,
            SecurityEventType.PERMISSION_DENIED: 3.0,
            SecurityEventType.DATA_ACCESS: 1.0,
            SecurityEventType.DATA_MODIFICATION: 5.0,
            SecurityEventType.DATA_DELETION: 7.0,
            SecurityEventType.CHILD_INTERACTION: 2.0,
            SecurityEventType.AUDIO_RECORDING: 3.0,
            SecurityEventType.VULNERABILITY_DETECTED: 9.0,
        }

        score += event_scores.get(event.event_type, 0.0)

        # Threat level multiplier
        threat_multipliers = {
            ThreatLevel.LOW: 1.0,
            ThreatLevel.MEDIUM: 2.0,
            ThreatLevel.HIGH: 5.0,
            ThreatLevel.CRITICAL: 10.0,
        }

        score *= threat_multipliers[event.threat_level]

        # Failed operations get higher score
        if event.result != "success":
            score *= 1.5

        # Sensitive data involvement
        if event.sensitive_data_involved:
            score *= 1.3

        # Anonymous/unknown user
        if not event.user_id:
            score *= 1.2

        return min(score, 10.0)  # Cap at 10.0

    async def _check_automated_response(
            self, event: SecurityEvent) -> Optional[str]:
        """Check if automated response is needed"""

        if event.threat_level == ThreatLevel.CRITICAL:
            return "immediate_lockdown"
        elif (
            event.event_type == SecurityEventType.RATE_LIMIT_EXCEEDED
            and event.threat_level == ThreatLevel.HIGH
        ):
            return "temporary_ip_block"
        elif event.event_type == SecurityEventType.LOGIN_FAILURE:
            # Check recent failures
            recent_failures = await self._count_recent_events(
                event.user_id or event.ip_address,
                SecurityEventType.LOGIN_FAILURE,
                300,  # 5 minutes
            )
            if recent_failures >= 5:
                return "account_lockout"

        return None

    async def _detect_threats(self, event: SecurityEvent):
        """Real-time threat detection"""

        for pattern_name, pattern in self.threat_patterns.items():
            if event.event_type in pattern["event_types"]:
                # Count recent events matching this pattern
                count = await self._count_recent_events(
                    event.user_id or event.ip_address,
                    event.event_type,
                    pattern["time_window"],
                )

                if count >= pattern["threshold"]:
                    # Threat detected
                    threat_event = SecurityEvent(
                        event_id="",
                        event_type=SecurityEventType.SUSPICIOUS_ACTIVITY,
                        timestamp=datetime.utcnow(),
                        user_id=event.user_id,
                        ip_address=event.ip_address,
                        threat_level=pattern["threat_level"],
                        details={
                            "threat_pattern": pattern_name,
                            "triggering_event_id": event.event_id,
                            "event_count": count,
                            "time_window": pattern["time_window"],
                        },
                        correlation_id=event.correlation_id,
                    )

                    # Log threat detection event
                    threat_context = SecurityEventContext(
                        user_id=event.user_id,
                        ip_address=event.ip_address,
                        details=threat_event.details,
                        correlation_id=event.correlation_id,
                    )
                    await self.log_security_event(
                        event_type=SecurityEventType.SUSPICIOUS_ACTIVITY,
                        context=threat_context,
                    )

    async def _check_alerting_rules(self, event: SecurityEvent):
        """Check real-time alerting rules"""

        for rule in self.alerting_rules:
            try:
                if rule["condition"](event):
                    await self._send_alert(rule, event)
            except Exception as e:
                logger.error(
                    "Alerting rule error",
                    rule=rule["name"],
                    error=str(e))

    async def _send_alert(self, rule: Dict[str, Any], event: SecurityEvent):
        """Send security alert"""

        alert_data = {
            "rule_name": rule["name"],
            "event_id": event.event_id,
            "event_type": event.event_type.value,
            "timestamp": event.timestamp.isoformat(),
            "user_id": event.user_id,
            "threat_level": event.threat_level.value,
            "details": event.details,
            "immediate": rule.get("alert_immediately", False),
            "channels": rule.get("notification_channels", []),
        }

        # In production, this would integrate with alerting systems
        logger.critical("SECURITY ALERT", **alert_data)

        # Store alert for tracking
        alert_context = SecurityEventContext(
            details={
                "alert_rule": rule["name"],
                "original_event_id": event.event_id})
        await self.log_security_event(
            event_type=SecurityEventType.INCIDENT_CREATED, context=alert_context
        )

    async def _update_correlations(self, event: SecurityEvent):
        """Update event correlations"""

        # Correlation by session
        if event.session_id:
            if event.session_id not in self.session_events:
                self.session_events[event.session_id] = []
            self.session_events[event.session_id].append(event.event_id)

        # Correlation by correlation_id
        if event.correlation_id:
            if event.correlation_id not in self.correlation_map:
                self.correlation_map[event.correlation_id] = []
            self.correlation_map[event.correlation_id].append(event.event_id)

    async def _count_recent_events(
        self, identifier: str, event_type: SecurityEventType, time_window: int
    ) -> int:
        """Count recent events for threat detection"""

        # This is a simplified implementation
        # In production, this would query the storage backend
        cutoff_time = datetime.utcnow() - timedelta(seconds=time_window)

        count = 0
        for entry in self.event_buffer:
            if (
                entry.event.timestamp >= cutoff_time
                and entry.event.event_type == event_type
                and (
                    entry.event.user_id == identifier
                    or entry.event.ip_address == identifier
                )
            ):
                count += 1

        return count

    async def _flush_buffer(self):
        """Flush event buffer to storage"""

        if not self.event_buffer:
            return

        events_to_flush = self.event_buffer.copy()
        self.event_buffer.clear()

        try:
            if self.storage_backend:
                await self._store_events(events_to_flush)
            else:
                # Fallback: log to structured logger
                for entry in events_to_flush:
                    logger.info("Security audit event", **asdict(entry.event))

        except Exception as e:
            logger.error("Failed to flush audit events", error=str(e))
            # Re-add events to buffer for retry
            self.event_buffer.extend(events_to_flush)

    async def _store_events(self, events: List[AuditLogEntry]):
        """Store events in backend storage"""

        # This would integrate with your chosen storage backend
        # (Database, Elasticsearch, etc.)
        pass

    async def _get_geolocation(self, ip_address: str) -> Dict[str, str]:
        """Get geolocation for IP address"""

        # Placeholder - would integrate with geolocation service
        return {"country": "Unknown", "city": "Unknown", "coordinates": "0,0"}

    async def _get_device_info(self, device_id: str) -> Dict[str, Any]:
        """Get device information"""

        # Placeholder - would fetch from device registry
        return {
            "device_type": "teddy_bear",
            "model": "v2.0",
            "last_seen": datetime.utcnow().isoformat(),
        }

    def _start_background_tasks(self) -> Any:
        """Start background monitoring tasks"""

        async def buffer_flush_task():
            """Periodically flush buffer"""
            while True:
                await asyncio.sleep(60)  # Every minute
                if self.event_buffer:
                    async with self.buffer_lock:
                        await self._flush_buffer()

        async def cleanup_task():
            """Clean up old correlation data"""
            while True:
                await asyncio.sleep(3600)  # Every hour
                cutoff = datetime.utcnow() - timedelta(hours=24)

                # Cleanup would happen here
                # This is a placeholder

        self._monitoring_tasks.append(asyncio.create_task(buffer_flush_task()))
        self._monitoring_tasks.append(asyncio.create_task(cleanup_task()))

    def _filter_events_for_report(
            self,
            standard: ComplianceStandard,
            start_date: datetime,
            end_date: datetime) -> List[AuditLogEntry]:
        """Filter events based on compliance standard and date range."""
        return [
            entry
            for entry in self.event_buffer
            if standard in entry.event.compliance_flags
            and start_date <= entry.event.timestamp <= end_date
        ]

    def _summarize_event_types(
        self, relevant_events: List[AuditLogEntry]
    ) -> Dict[str, int]:
        """Summarize event types from a list of audit log entries."""
        summary = {}
        for event_type in SecurityEventType:
            count = sum(
                1 for e in relevant_events if e.event.event_type == event_type)
            if count > 0:
                summary[event_type.value] = count
        return summary

    def _calculate_risk_summary(
        self, relevant_events: List[AuditLogEntry]
    ) -> Dict[str, float]:
        """Calculate the risk summary for a list of audit log entries."""
        if not relevant_events:
            return {
                "total_risk_score": 0.0,
                "average_risk_score": 0.0,
                "high_risk_events": 0.0,
            }

        total_risk_score = sum(e.risk_score for e in relevant_events)
        high_risk_events = sum(
            1 for e in relevant_events if e.risk_score >= 7.0)

        return {
            "total_risk_score": total_risk_score,
            "average_risk_score": total_risk_score / len(relevant_events),
            "high_risk_events": float(high_risk_events),
        }

    async def get_compliance_report(
        self, standard: ComplianceStandard, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """Generate compliance report by orchestrating helper methods."""
        relevant_events = self._filter_events_for_report(
            standard, start_date, end_date)
        event_type_summary = self._summarize_event_types(relevant_events)
        risk_summary = self._calculate_risk_summary(relevant_events)

        return {
            "standard": standard.value,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()},
            "total_events": len(relevant_events),
            "event_types": event_type_summary,
            "risk_summary": risk_summary,
        }


# Global audit logger
_audit_logger: Optional[SecurityAuditLogger] = None


def get_security_audit_logger(
    storage_backend: Optional[Any] = None,
) -> SecurityAuditLogger:
    """Get global security audit logger"""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = SecurityAuditLogger(storage_backend)
    return _audit_logger


# Convenience functions for common events


async def log_child_interaction(
    user_id: str,
    device_id: str,
    interaction_type: str,
    duration: Optional[int] = None,
    **kwargs,
) -> str:
    """Log child interaction event"""
    audit_logger = get_security_audit_logger()

    details = {
        "interaction_type": interaction_type,
        "duration_seconds": duration,
        **kwargs,
    }

    context = SecurityEventContext(
        user_id=user_id,
        device_id=device_id,
        details=details,
        sensitive_data_involved=True,
    )
    return await audit_logger.log_security_event(
        event_type=SecurityEventType.CHILD_INTERACTION, context=context
    )


async def log_audio_recording(
        user_id: str,
        device_id: str,
        session_id: str,
        audio_duration: int,
        **kwargs) -> str:
    """Log audio recording event"""
    audit_logger = get_security_audit_logger()

    details = {
        "audio_duration_seconds": audio_duration,
        "audio_encrypted": True,
        **kwargs,
    }

    context = SecurityEventContext(
        user_id=user_id,
        device_id=device_id,
        session_id=session_id,
        details=details,
        sensitive_data_involved=True,
    )
    return await audit_logger.log_security_event(
        event_type=SecurityEventType.AUDIO_RECORDING, context=context
    )


async def log_login_attempt(
        user_id: str,
        username: str,
        result: str,
        ip_address: str,
        user_agent: str,
        **kwargs) -> str:
    """Log login attempt"""
    audit_logger = get_security_audit_logger()

    event_type = (
        SecurityEventType.LOGIN_SUCCESS
        if result == "success"
        else SecurityEventType.LOGIN_FAILURE
    )

    context = SecurityEventContext(
        user_id=user_id,
        username=username,
        ip_address=ip_address,
        user_agent=user_agent,
        result=result,
        details=kwargs,
    )
    return await audit_logger.log_security_event(event_type=event_type, context=context)
