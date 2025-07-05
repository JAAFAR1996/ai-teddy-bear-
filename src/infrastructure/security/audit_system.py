from typing import Any, Dict, List, Optional

"""
🔐 Security Audit System - Comprehensive Logging
===============================================

Author: Jaafar Adeeb - Security Lead
"""

import asyncio
import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

import structlog

logger = structlog.get_logger(__name__)


class SecurityEventType(Enum):
    """Security event types"""

    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    PERMISSION_DENIED = "permission_denied"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    AUDIO_RECORDING = "audio_recording"
    CHILD_INTERACTION = "child_interaction"
    DEVICE_REGISTRATION = "device_registration"
    FAMILY_CREATION = "family_creation"
    PARENTAL_CONTROL_CHANGE = "parental_control_change"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    TOKEN_ISSUED = "token_issued"
    TOKEN_REVOKED = "token_revoked"


class ThreatLevel(Enum):
    """Threat level classification"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityEvent:
    """Security event structure"""

    event_id: str
    event_type: SecurityEventType
    timestamp: datetime
    user_id: Optional[str] = None
    username: Optional[str] = None
    device_id: Optional[str] = None
    ip_address: Optional[str] = None
    resource: Optional[str] = None
    action: Optional[str] = None
    result: str = "success"
    threat_level: ThreatLevel = ThreatLevel.LOW
    details: Dict[str, Any] = field(default_factory=dict)
    sensitive_data: bool = False

    def __post_init__(self):
        if not self.event_id:
            # Generate unique event ID
            data = f"{self.timestamp.isoformat()}:{self.event_type.value}:{self.user_id or 'anon'}"
            self.event_id = hashlib.sha256(data.encode()).hexdigest()[:16]


class SecurityAuditLogger:
    """Security audit logging system"""

    def __init__(self):
        self.events: List[SecurityEvent] = []
        self.event_buffer: List[SecurityEvent] = []
        self.buffer_size = 100
        self.buffer_lock = asyncio.Lock()

        # Threat detection patterns
        self.threat_patterns = {
            "login_brute_force": {
                "event_type": SecurityEventType.LOGIN_FAILURE,
                "threshold": 5,
                "window_seconds": 300,
                "threat_level": ThreatLevel.HIGH,
            },
            "unauthorized_access_pattern": {
                "event_type": SecurityEventType.UNAUTHORIZED_ACCESS,
                "threshold": 3,
                "window_seconds": 60,
                "threat_level": ThreatLevel.HIGH,
            },
        }

        # Start background tasks
        self._start_monitoring()

    async def log_event(
        self,
        event_type: SecurityEventType,
        user_id: Optional[str] = None,
        username: Optional[str] = None,
        device_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        resource: Optional[str] = None,
        action: Optional[str] = None,
        result: str = "success",
        details: Optional[Dict[str, Any]] = None,
        sensitive_data: bool = False,
    ) -> str:
        """Log a security event"""

        event = SecurityEvent(
            event_id="",  # Will be generated
            event_type=event_type,
            timestamp=datetime.utcnow(),
            user_id=user_id,
            username=username,
            device_id=device_id,
            ip_address=ip_address,
            resource=resource,
            action=action,
            result=result,
            details=details or {},
            sensitive_data=sensitive_data,
        )

        # Determine threat level
        event.threat_level = self._assess_threat_level(event)

        # Add to buffer
        async with self.buffer_lock:
            self.event_buffer.append(event)

            if len(self.event_buffer) >= self.buffer_size:
                await self._flush_buffer()

        # Real-time threat detection
        await self._detect_threats(event)

        # Log to structured logger
        logger.info(
            "Security event",
            event_id=event.event_id,
            event_type=event_type.value,
            user_id=user_id,
            threat_level=event.threat_level.value,
            result=result,
        )

        return event.event_id

    def _assess_threat_level(self, event: SecurityEvent) -> ThreatLevel:
        """Assess threat level for event"""

        # High threat events
        if event.event_type in [
            SecurityEventType.UNAUTHORIZED_ACCESS,
            SecurityEventType.SUSPICIOUS_ACTIVITY,
        ]:
            return ThreatLevel.HIGH

        # Medium threat events
        if event.event_type in [
            SecurityEventType.LOGIN_FAILURE,
            SecurityEventType.PERMISSION_DENIED,
            SecurityEventType.RATE_LIMIT_EXCEEDED,
        ]:
            return ThreatLevel.MEDIUM

        # Child-related events get special handling
        if event.event_type in [
            SecurityEventType.CHILD_INTERACTION,
            SecurityEventType.AUDIO_RECORDING,
        ]:
            return ThreatLevel.MEDIUM if event.sensitive_data else ThreatLevel.LOW

        return ThreatLevel.LOW

    async def _detect_threats(self, event: SecurityEvent):
        """Real-time threat detection"""

        for pattern_name, pattern in self.threat_patterns.items():
            if event.event_type == pattern["event_type"]:
                # Count recent similar events
                recent_count = await self._count_recent_events(
                    event.ip_address or event.user_id,
                    pattern["event_type"],
                    pattern["window_seconds"],
                )

                if recent_count >= pattern["threshold"]:
                    # Threat detected
                    await self.log_event(
                        event_type=SecurityEventType.SUSPICIOUS_ACTIVITY,
                        user_id=event.user_id,
                        ip_address=event.ip_address,
                        details={
                            "threat_pattern": pattern_name,
                            "trigger_event_id": event.event_id,
                            "event_count": recent_count,
                        },
                    )

                    logger.warning(
                        "Threat pattern detected",
                        pattern=pattern_name,
                        user_id=event.user_id,
                        ip_address=event.ip_address,
                        count=recent_count,
                    )

    async def _count_recent_events(
        self, identifier: str, event_type: SecurityEventType, window_seconds: int
    ) -> int:
        """Count recent events for threat detection"""

        if not identifier:
            return 0

        cutoff_time = datetime.utcnow() - timedelta(seconds=window_seconds)
        count = 0

        # Check buffer
        for event in self.event_buffer:
            if (
                event.timestamp >= cutoff_time
                and event.event_type == event_type
                and (event.user_id == identifier or event.ip_address == identifier)
            ):
                count += 1

        # Check stored events
        for event in self.events[-1000:]:  # Check last 1000 events
            if (
                event.timestamp >= cutoff_time
                and event.event_type == event_type
                and (event.user_id == identifier or event.ip_address == identifier)
            ):
                count += 1

        return count

    async def _flush_buffer(self):
        """Flush event buffer to storage"""

        if not self.event_buffer:
            return

        events_to_store = self.event_buffer.copy()
        self.event_buffer.clear()

        # Store events
        self.events.extend(events_to_store)

        # Keep only recent events in memory (last 10,000)
        if len(self.events) > 10000:
            self.events = self.events[-10000:]

        logger.debug("Audit events flushed", count=len(events_to_store))

    def _start_monitoring(self) -> Any:
        """Start background monitoring tasks"""

        async def periodic_flush():
            """Periodically flush buffer"""
            while True:
                await asyncio.sleep(60)  # Every minute
                async with self.buffer_lock:
                    await self._flush_buffer()

        asyncio.create_task(periodic_flush())

    async def get_events(
        self,
        user_id: Optional[str] = None,
        event_type: Optional[SecurityEventType] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1000,
    ) -> List[SecurityEvent]:
        """Get filtered events"""

        filtered_events = []
        all_events = self.events + self.event_buffer

        for event in all_events:
            # Apply filters
            if user_id and event.user_id != user_id:
                continue
            if event_type and event.event_type != event_type:
                continue
            if start_time and event.timestamp < start_time:
                continue
            if end_time and event.timestamp > end_time:
                continue

            filtered_events.append(event)

            if len(filtered_events) >= limit:
                break

        return sorted(filtered_events, key=lambda e: e.timestamp, reverse=True)

    async def get_security_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get security summary for specified hours"""

        start_time = datetime.utcnow() - timedelta(hours=hours)
        recent_events = await self.get_events(start_time=start_time)

        # Count by event type
        event_counts = {}
        threat_counts = {}

        for event in recent_events:
            event_type = event.event_type.value
            threat_level = event.threat_level.value

            event_counts[event_type] = event_counts.get(event_type, 0) + 1
            threat_counts[threat_level] = threat_counts.get(threat_level, 0) + 1

        return {
            "period_hours": hours,
            "total_events": len(recent_events),
            "event_types": event_counts,
            "threat_levels": threat_counts,
            "unique_users": len(set(e.user_id for e in recent_events if e.user_id)),
            "unique_ips": len(set(e.ip_address for e in recent_events if e.ip_address)),
            "failed_events": len([e for e in recent_events if e.result != "success"]),
        }


# Global audit logger
_audit_logger: Optional[SecurityAuditLogger] = None


def get_audit_logger() -> SecurityAuditLogger:
    """Get global security audit logger"""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = SecurityAuditLogger()
    return _audit_logger


# Convenience functions


async def log_child_interaction(
    user_id: str, device_id: str, interaction_type: str, **kwargs
) -> str:
    """Log child interaction"""
    audit_logger = get_audit_logger()

    return await audit_logger.log_event(
        event_type=SecurityEventType.CHILD_INTERACTION,
        user_id=user_id,
        device_id=device_id,
        action=interaction_type,
        details=kwargs,
        sensitive_data=True,
    )


async def log_audio_recording(
    user_id: str, device_id: str, duration: int, **kwargs
) -> str:
    """Log audio recording"""
    audit_logger = get_audit_logger()

    return await audit_logger.log_event(
        event_type=SecurityEventType.AUDIO_RECORDING,
        user_id=user_id,
        device_id=device_id,
        details={"duration_seconds": duration, **kwargs},
        sensitive_data=True,
    )


async def log_login_attempt(
    user_id: str, username: str, ip_address: str, result: str, **kwargs
) -> str:
    """Log login attempt"""
    audit_logger = get_audit_logger()

    event_type = (
        SecurityEventType.LOGIN_SUCCESS
        if result == "success"
        else SecurityEventType.LOGIN_FAILURE
    )

    return await audit_logger.log_event(
        event_type=event_type,
        user_id=user_id,
        username=username,
        ip_address=ip_address,
        result=result,
        details=kwargs,
    )
