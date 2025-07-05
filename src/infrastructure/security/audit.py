import enum
from datetime import datetime
from typing import Any, Dict, Optional

# src/infrastructure/security/audit.py
from sqlalchemy import JSON, Column, DateTime, Enum, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class AuditEventType(enum.Enum):
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    CHILD_CREATED = "child_created"
    SESSION_STARTED = "session_started"
    AUDIO_PROCESSED = "audio_processed"
    DATA_ACCESSED = "data_accessed"
    PERMISSION_CHANGED = "permission_changed"
    SECURITY_ALERT = "security_alert"


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    event_type = Column(Enum(AuditEventType), nullable=False)
    user_id = Column(String, nullable=True)
    child_id = Column(String, nullable=True)
    ip_address = Column(String, nullable=False)
    user_agent = Column(String, nullable=True)
    details = Column(JSON, nullable=False)
    risk_score = Column(String, nullable=True)


class AuditService:
    """Comprehensive audit logging service"""

    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def log_event(
        self,
        event_type: AuditEventType,
        ip_address: str,
        user_id: Optional[str] = None,
        child_id: Optional[str] = None,
        details: Dict[str, Any] = None,
        user_agent: Optional[str] = None,
    ):
        async with self.session_factory() as session:
            audit_log = AuditLog(
                id=str(uuid.uuid4()),
                event_type=event_type,
                user_id=user_id,
                child_id=child_id,
                ip_address=ip_address,
                user_agent=user_agent,
                details=details or {},
                risk_score=self._calculate_risk_score(event_type, details),
            )
            session.add(audit_log)
            await session.commit()

            # Alert on high-risk events
            if audit_log.risk_score == "HIGH":
                await self._send_security_alert(audit_log)

    def _calculate_risk_score(
            self,
            event_type: AuditEventType,
            details: Dict) -> str:
        """Calculate risk score based on event type and details"""
        high_risk_events = [
            AuditEventType.PERMISSION_CHANGED,
            AuditEventType.SECURITY_ALERT,
        ]

        if event_type in high_risk_events:
            return "HIGH"

        # Check for suspicious patterns
        if details:
            if details.get("failed_attempts", 0) > 3:
                return "MEDIUM"
            if details.get("unusual_location", False):
                return "MEDIUM"

        return "LOW"
