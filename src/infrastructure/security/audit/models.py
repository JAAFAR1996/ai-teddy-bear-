"""
Data models for the security audit logging system.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import hashlib


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
