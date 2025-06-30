"""
Comprehensive Audit Logging System
Provides tamper-proof audit logs for security and compliance
"""

import asyncio
import hashlib
import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set

import structlog
from sqlalchemy import Column, String, DateTime, Text, Integer, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

logger = structlog.get_logger()

Base = declarative_base()


class AuditEventType(Enum):
    """Types of audit events"""
    # Authentication
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGOUT = "logout"
    SESSION_TIMEOUT = "session_timeout"
    
    # Authorization
    ACCESS_GRANTED = "access_granted"
    ACCESS_DENIED = "access_denied"
    PERMISSION_CHANGED = "permission_changed"
    
    # Data Access
    DATA_READ = "data_read"
    DATA_WRITE = "data_write"
    DATA_DELETE = "data_delete"
    DATA_EXPORT = "data_export"
    
    # Child Data
    CHILD_DATA_ACCESS = "child_data_access"
    CHILD_DATA_MODIFIED = "child_data_modified"
    CHILD_AUDIO_PLAYED = "child_audio_played"
    CHILD_CONVERSATION = "child_conversation"
    
    # Security
    ENCRYPTION_KEY_USED = "encryption_key_used"
    DECRYPTION_PERFORMED = "decryption_performed"
    SECURITY_ALERT = "security_alert"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    
    # System
    SYSTEM_START = "system_start"
    SYSTEM_STOP = "system_stop"
    CONFIG_CHANGE = "config_change"
    ERROR_OCCURRED = "error_occurred"


class AuditSeverity(Enum):
    """Audit event severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class AuditEvent:
    """Audit event data structure"""
    event_id: str
    timestamp: datetime
    event_type: AuditEventType
    severity: AuditSeverity
    user_id: Optional[str]
    child_id: Optional[str]
    session_id: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    resource: Optional[str]
    action: str
    result: str
    details: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    hash_chain: Optional[str] = None
    signature: Optional[str] = None


class AuditLogEntry(Base):
    """Database model for audit logs"""
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True)
    event_id = Column(String(64), unique=True, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    event_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    user_id = Column(String(64), index=True)
    child_id = Column(String(64), index=True)
    session_id = Column(String(64), index=True)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    resource = Column(String(255))
    action = Column(String(100), nullable=False)
    result = Column(String(50), nullable=False)
    details = Column(Text)
    meta_data = Column(Text)  # Renamed to avoid SQLAlchemy reserved word
    hash_chain = Column(String(64), nullable=False)
    signature = Column(Text)
    is_verified = Column(Boolean, default=True)
    
    __table_args__ = (
        Index('idx_timestamp', 'timestamp'),
        Index('idx_event_type', 'event_type'),
        Index('idx_user_child', 'user_id', 'child_id'),
    )


class AuditLogger:
    """
    Tamper-proof audit logging system with blockchain-like integrity
    """
    
    def __init__(self, config: Dict[str, Any], db_session):
        self.config = config
        self.db_session = db_session
        self._buffer: List[AuditEvent] = []
        self._buffer_size = config.get("audit_buffer_size", 100)
        self._flush_interval = config.get("audit_flush_interval", 10)
        self._retention_days = config.get("audit_retention_days", 365)
        
        # Cryptographic setup for tamper-proof logs
        self._private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self._public_key = self._private_key.public_key()
        self._last_hash = self._get_last_hash()
        
        # Event filters
        self._sensitive_events = {
            AuditEventType.CHILD_DATA_ACCESS,
            AuditEventType.CHILD_DATA_MODIFIED,
            AuditEventType.CHILD_AUDIO_PLAYED,
            AuditEventType.CHILD_CONVERSATION
        }
        
        # Start background tasks
        self._flush_task = asyncio.create_task(self._flush_loop())
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
    
    async def log_event(
        self,
        event_type: AuditEventType,
        action: str,
        result: str,
        user_id: Optional[str] = None,
        child_id: Optional[str] = None,
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        resource: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        severity: Optional[AuditSeverity] = None
    ) -> str:
        """Log an audit event"""
        # Auto-determine severity if not provided
        if severity is None:
            severity = self._determine_severity(event_type, result)
        
        # Generate event ID
        event_id = self._generate_event_id()
        
        # Create event
        event = AuditEvent(
            event_id=event_id,
            timestamp=datetime.utcnow(),
            event_type=event_type,
            severity=severity,
            user_id=user_id,
            child_id=child_id,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            resource=resource,
            action=action,
            result=result,
            details=details or {},
            metadata={
                "version": "1.0",
                "service": self.config.get("service_name", "ai_teddy")
            }
        )
        
        # Add to buffer
        await self._add_to_buffer(event)
        
        # Log sensitive events immediately
        if event_type in self._sensitive_events:
            await self._flush_buffer()
        
        logger.info(
            "Audit event logged",
            event_id=event_id,
            event_type=event_type.value,
            severity=severity.value
        )
        
        return event_id
    
    async def _add_to_buffer(self, event: AuditEvent) -> None:
        """Add event to buffer with integrity protection"""
        # Calculate hash chain
        event.hash_chain = self._calculate_hash(event, self._last_hash)
        
        # Sign event
        event.signature = self._sign_event(event)
        
        # Update last hash
        self._last_hash = event.hash_chain
        
        # Add to buffer
        self._buffer.append(event)
        
        # Flush if buffer is full
        if len(self._buffer) >= self._buffer_size:
            await self._flush_buffer()
    
    async def _flush_buffer(self) -> None:
        """Flush buffer to database"""
        if not self._buffer:
            return
        
        try:
            # Convert events to DB entries
            entries = []
            for event in self._buffer:
                entry = AuditLogEntry(
                    event_id=event.event_id,
                    timestamp=event.timestamp,
                    event_type=event.event_type.value,
                    severity=event.severity.value,
                    user_id=event.user_id,
                    child_id=event.child_id,
                    session_id=event.session_id,
                    ip_address=event.ip_address,
                    user_agent=event.user_agent,
                    resource=event.resource,
                    action=event.action,
                    result=event.result,
                    details=json.dumps(event.details),
                    meta_data=json.dumps(event.metadata),
                    hash_chain=event.hash_chain,
                    signature=event.signature
                )
                entries.append(entry)
            
            # Bulk insert
            self.db_session.bulk_save_objects(entries)
            self.db_session.commit()
            
            # Clear buffer
            self._buffer.clear()
            
            logger.info(f"Flushed {len(entries)} audit events to database")
            
        except Exception as e:
            logger.error("Failed to flush audit buffer", error=str(e))
            # Don't clear buffer on error
    
    async def _flush_loop(self) -> None:
        """Background task to periodically flush buffer"""
        while True:
            try:
                await asyncio.sleep(self._flush_interval)
                await self._flush_buffer()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Flush loop error", error=str(e))
    
    async def _cleanup_loop(self) -> None:
        """Background task to clean up old logs"""
        while True:
            try:
                await asyncio.sleep(86400)  # Daily
                await self._cleanup_old_logs()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Cleanup loop error", error=str(e))
    
    async def _cleanup_old_logs(self) -> None:
        """Remove logs older than retention period"""
        cutoff_date = datetime.utcnow() - timedelta(days=self._retention_days)
        
        # Archive before deletion
        await self._archive_logs(cutoff_date)
        
        # Delete old logs
        deleted = self.db_session.query(AuditLogEntry).filter(
            AuditLogEntry.timestamp < cutoff_date
        ).delete()
        
        self.db_session.commit()
        
        logger.info(f"Cleaned up {deleted} old audit logs")
    
    async def _archive_logs(self, cutoff_date: datetime) -> None:
        """Archive logs before deletion"""
        # Implementation depends on archive strategy
        # Could be S3, cold storage, etc.
        pass
    
    def _generate_event_id(self) -> str:
        """Generate unique event ID"""
        timestamp = str(time.time_ns())
        random_bytes = os.urandom(8).hex()
        return hashlib.sha256(f"{timestamp}:{random_bytes}".encode()).hexdigest()
    
    def _calculate_hash(self, event: AuditEvent, previous_hash: str) -> str:
        """Calculate hash for blockchain-like integrity"""
        data = {
            "event_id": event.event_id,
            "timestamp": event.timestamp.isoformat(),
            "event_type": event.event_type.value,
            "user_id": event.user_id,
            "child_id": event.child_id,
            "action": event.action,
            "result": event.result,
            "previous_hash": previous_hash
        }
        
        serialized = json.dumps(data, sort_keys=True)
        return hashlib.sha256(serialized.encode()).hexdigest()
    
    def _sign_event(self, event: AuditEvent) -> str:
        """Digitally sign event for non-repudiation"""
        message = f"{event.event_id}:{event.hash_chain}".encode()
        
        signature = self._private_key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        return base64.b64encode(signature).decode()
    
    def _get_last_hash(self) -> str:
        """Get last hash from database"""
        last_entry = self.db_session.query(AuditLogEntry).order_by(
            AuditLogEntry.id.desc()
        ).first()
        
        if last_entry:
            return last_entry.hash_chain
        
        # Genesis hash
        return "0" * 64
    
    def _determine_severity(self, event_type: AuditEventType, result: str) -> AuditSeverity:
        """Auto-determine event severity"""
        if result == "failure" or result == "denied":
            return AuditSeverity.WARNING
        
        if event_type in [
            AuditEventType.SECURITY_ALERT,
            AuditEventType.SUSPICIOUS_ACTIVITY
        ]:
            return AuditSeverity.CRITICAL
        
        if event_type == AuditEventType.ERROR_OCCURRED:
            return AuditSeverity.ERROR
        
        return AuditSeverity.INFO
    
    async def verify_integrity(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Verify audit log integrity for a date range"""
        entries = self.db_session.query(AuditLogEntry).filter(
            AuditLogEntry.timestamp.between(start_date, end_date)
        ).order_by(AuditLogEntry.id).all()
        
        if not entries:
            return {"verified": True, "total": 0, "errors": []}
        
        errors = []
        previous_hash = self._get_previous_hash(entries[0].id)
        
        for entry in entries:
            # Reconstruct event
            event = AuditEvent(
                event_id=entry.event_id,
                timestamp=entry.timestamp,
                event_type=AuditEventType(entry.event_type),
                severity=AuditSeverity(entry.severity),
                user_id=entry.user_id,
                child_id=entry.child_id,
                action=entry.action,
                result=entry.result
            )
            
            # Verify hash chain
            expected_hash = self._calculate_hash(event, previous_hash)
            if expected_hash != entry.hash_chain:
                errors.append({
                    "event_id": entry.event_id,
                    "error": "Hash chain mismatch"
                })
            
            # Verify signature
            if not self._verify_signature(entry):
                errors.append({
                    "event_id": entry.event_id,
                    "error": "Invalid signature"
                })
            
            previous_hash = entry.hash_chain
        
        return {
            "verified": len(errors) == 0,
            "total": len(entries),
            "errors": errors
        }
    
    def _get_previous_hash(self, entry_id: int) -> str:
        """Get hash of previous entry"""
        previous = self.db_session.query(AuditLogEntry).filter(
            AuditLogEntry.id < entry_id
        ).order_by(AuditLogEntry.id.desc()).first()
        
        return previous.hash_chain if previous else "0" * 64
    
    def _verify_signature(self, entry: AuditLogEntry) -> bool:
        """Verify digital signature"""
        try:
            message = f"{entry.event_id}:{entry.hash_chain}".encode()
            signature = base64.b64decode(entry.signature)
            
            self._public_key.verify(
                signature,
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            return True
        except:
            return False
    
    async def query_logs(
        self,
        event_types: Optional[List[AuditEventType]] = None,
        user_id: Optional[str] = None,
        child_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Query audit logs with filters"""
        query = self.db_session.query(AuditLogEntry)
        
        if event_types:
            query = query.filter(
                AuditLogEntry.event_type.in_([e.value for e in event_types])
            )
        
        if user_id:
            query = query.filter(AuditLogEntry.user_id == user_id)
        
        if child_id:
            query = query.filter(AuditLogEntry.child_id == child_id)
        
        if start_date:
            query = query.filter(AuditLogEntry.timestamp >= start_date)
        
        if end_date:
            query = query.filter(AuditLogEntry.timestamp <= end_date)
        
        entries = query.order_by(AuditLogEntry.timestamp.desc()).limit(limit).all()
        
        return [self._entry_to_dict(entry) for entry in entries]
    
    def _entry_to_dict(self, entry: AuditLogEntry) -> Dict[str, Any]:
        """Convert DB entry to dictionary"""
        return {
            "event_id": entry.event_id,
            "timestamp": entry.timestamp.isoformat(),
            "event_type": entry.event_type,
            "severity": entry.severity,
            "user_id": entry.user_id,
            "child_id": entry.child_id,
            "session_id": entry.session_id,
            "ip_address": entry.ip_address,
            "resource": entry.resource,
            "action": entry.action,
            "result": entry.result,
            "details": json.loads(entry.details) if entry.details else {},
            "is_verified": entry.is_verified
        }
    
    def get_public_key(self) -> str:
        """Get public key for external verification"""
        return self._public_key.public_bytes(
            encoding=Encoding.PEM,
            format=PublicFormat.SubjectPublicKeyInfo
        ).decode()
    
    async def shutdown(self) -> None:
        """Graceful shutdown"""
        # Cancel background tasks
        self._flush_task.cancel()
        self._cleanup_task.cancel()
        
        # Final flush
        await self._flush_buffer()
        
        logger.info("Audit logger shut down")


# Convenience decorator for automatic audit logging
def audit_log(event_type: AuditEventType, resource_param: str = None):
    """
    Decorator for automatic audit logging
    
    Example:
        @audit_log(AuditEventType.CHILD_DATA_ACCESS, resource_param="child_id")
        async def get_child_data(child_id: str):
            ...
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Get audit logger from somewhere (e.g., dependency injection)
            audit_logger = kwargs.get('audit_logger')
            
            if audit_logger:
                # Extract resource if specified
                resource = None
                if resource_param:
                    resource = kwargs.get(resource_param)
                
                try:
                    # Execute function
                    result = await func(*args, **kwargs)
                    
                    # Log success
                    await audit_logger.log_event(
                        event_type=event_type,
                        action=func.__name__,
                        result="success",
                        resource=resource
                    )
                    
                    return result
                    
                except Exception as e:
                    # Log failure
                    await audit_logger.log_event(
                        event_type=event_type,
                        action=func.__name__,
                        result="failure",
                        resource=resource,
                        details={"error": str(e)}
                    )
                    raise
            
            # No audit logger, just execute
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator 