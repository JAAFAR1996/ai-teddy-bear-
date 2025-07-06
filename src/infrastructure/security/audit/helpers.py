"""
Helper functions and a global instance for the security audit logger.
"""
from typing import Any, Optional

from .logger import SecurityAuditLogger
from .models import SecurityEventContext, SecurityEventType

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
