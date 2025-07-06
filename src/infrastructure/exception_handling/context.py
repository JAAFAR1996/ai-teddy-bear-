"""
Context management for exception handling.
"""

import contextvars
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional


@dataclass
class ExceptionContext:
    """Context information for exceptions"""

    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    child_id: Optional[str] = None
    request_id: Optional[str] = None
    service_name: str = "ai-teddy-bear"
    environment: str = "production"
    additional_data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging"""
        return {
            "correlation_id": self.correlation_id,
            "user_id": self.user_id,
            "child_id": self.child_id,
            "request_id": self.request_id,
            "service_name": self.service_name,
            "environment": self.environment,
            "timestamp": self.timestamp.isoformat(),
            "additional_data": self.additional_data,
        }


# Context variables for correlation
correlation_id_var = contextvars.ContextVar("correlation_id", default=None)
user_id_var = contextvars.ContextVar("user_id", default=None)
child_id_var = contextvars.ContextVar("child_id", default=None)


# Context managers for correlation
class CorrelationContext:
    """Context manager for correlation ID"""

    def __init__(self, correlation_id: Optional[str] = None):
        self.correlation_id = correlation_id or str(uuid.uuid4())
        self.token = None

    def __enter__(self):
        self.token = correlation_id_var.set(self.correlation_id)
        return self.correlation_id

    def __exit__(self, exc_type, exc_val, exc_tb):
        correlation_id_var.reset(self.token)


# Helper functions
def set_child_context(child_id: str):
    """Set child context for exception handling"""
    child_id_var.set(child_id)


def set_user_context(user_id: str):
    """Set user context for exception handling"""
    user_id_var.set(user_id)


def get_current_correlation_id() -> Optional[str]:
    """Get current correlation ID"""
    return correlation_id_var.get()
