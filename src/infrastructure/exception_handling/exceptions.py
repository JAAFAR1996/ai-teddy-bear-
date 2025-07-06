"""
Custom exception hierarchy for the AI Teddy Bear project.
"""

import uuid
from dataclasses import field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any, Dict, Optional

from .context import ExceptionContext


class ExceptionSeverity(Enum):
    """Exception severity levels"""

    LOW = auto()  # Log and continue
    MEDIUM = auto()  # Log, alert team, continue with degradation
    HIGH = auto()  # Log, alert team, implement recovery
    CRITICAL = auto()  # Log, alert everyone, emergency response


class ExceptionDomain(Enum):
    """Exception domains for categorization"""

    AUTHENTICATION = auto()
    AUTHORIZATION = auto()
    CHILD_SAFETY = auto()
    DATA_PROCESSING = auto()
    EXTERNAL_SERVICE = auto()
    DATABASE = auto()
    VALIDATION = auto()
    BUSINESS_LOGIC = auto()
    INFRASTRUCTURE = auto()
    SECURITY = auto()
    PERFORMANCE = auto()


class TeddyBearException(Exception):
    """Base exception for all Teddy Bear application exceptions"""

    severity: ExceptionSeverity = ExceptionSeverity.MEDIUM
    domain: ExceptionDomain = ExceptionDomain.BUSINESS_LOGIC
    error_code: str = "TB_GENERIC_ERROR"
    should_alert: bool = True
    is_retryable: bool = False
    max_retries: int = 3

    def __init__(
        self,
        message: str,
        context: Optional[ExceptionContext] = None,
        cause: Optional[Exception] = None,
        **kwargs,
    ):
        super().__init__(message)
        self.message = message
        self.context = context or ExceptionContext()
        self.cause = cause
        self.details = kwargs
        self.timestamp = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging/serialization"""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "severity": self.severity.name,
            "domain": self.domain.name,
            "context": self.context.to_dict(),
            "details": self.details,
            "is_retryable": self.is_retryable,
            "timestamp": self.timestamp.isoformat(),
            "cause": str(self.cause) if self.cause else None,
        }

    def sanitize_for_child_logs(self) -> Dict[str, Any]:
        """Sanitize exception data for child-safe logging"""
        sanitized = self.to_dict()
        # Remove sensitive data
        sanitized.pop("details", None)
        sanitized["context"].pop("additional_data", None)
        # Simplify message
        sanitized["message"] = "An error occurred. Please try again."
        return sanitized


# Child Safety Exceptions
class ChildSafetyException(TeddyBearException):
    """Base for all child safety related exceptions"""

    domain = ExceptionDomain.CHILD_SAFETY
    severity = ExceptionSeverity.HIGH
    error_code = "TB_CHILD_SAFETY"


class InappropriateContentException(ChildSafetyException):
    """Raised when inappropriate content is detected"""

    error_code = "TB_INAPPROPRIATE_CONTENT"
    severity = ExceptionSeverity.CRITICAL

    def __init__(self, content_type: str, content_snippet: str, **kwargs):
        super().__init__(
            f"Inappropriate {content_type} detected",
            content_type=content_type,
            **kwargs,
        )


class AgeInappropriateException(ChildSafetyException):
    """Raised when content is not age-appropriate"""

    error_code = "TB_AGE_INAPPROPRIATE"

    def __init__(self, child_age: int, content_age_rating: int, **kwargs):
        super().__init__(
            f"Content requires age {content_age_rating}, child is {child_age}",
            child_age=child_age,
            content_age_rating=content_age_rating,
            **kwargs,
        )


class ChildDataProtectionException(ChildSafetyException):
    """Raised for child data protection violations"""

    error_code = "TB_CHILD_DATA_PROTECTION"
    severity = ExceptionSeverity.CRITICAL


# Security Exceptions
class SecurityException(TeddyBearException):
    """Base for security related exceptions"""

    domain = ExceptionDomain.SECURITY
    severity = ExceptionSeverity.HIGH
    error_code = "TB_SECURITY"


class AuthenticationException(SecurityException):
    """Authentication failures"""

    domain = ExceptionDomain.AUTHENTICATION
    error_code = "TB_AUTH_FAILED"
    is_retryable = False


class AuthorizationException(SecurityException):
    """Authorization failures"""

    domain = ExceptionDomain.AUTHORIZATION
    error_code = "TB_AUTHZ_FAILED"
    is_retryable = False


class TokenExpiredException(AuthenticationException):
    """Token has expired"""

    error_code = "TB_TOKEN_EXPIRED"
    is_retryable = True  # Can retry with refresh


class SuspiciousActivityException(SecurityException):
    """Suspicious activity detected"""

    error_code = "TB_SUSPICIOUS_ACTIVITY"
    severity = ExceptionSeverity.CRITICAL


# External Service Exceptions
class ExternalServiceException(TeddyBearException):
    """Base for external service failures"""

    domain = ExceptionDomain.EXTERNAL_SERVICE
    error_code = "TB_EXTERNAL_SERVICE"
    is_retryable = True

    def __init__(self, service_name: str, **kwargs):
        super().__init__(
            f"External service error: {service_name}",
            service_name=service_name,
            **kwargs,
        )


class AIServiceException(ExternalServiceException):
    """AI service specific exceptions"""

    error_code = "TB_AI_SERVICE"

    def __init__(self, ai_provider: str, **kwargs):
        super().__init__(
            service_name=f"AI-{ai_provider}", ai_provider=ai_provider, **kwargs
        )


class RateLimitException(ExternalServiceException):
    """Rate limit exceeded"""

    error_code = "TB_RATE_LIMIT"
    severity = ExceptionSeverity.MEDIUM

    def __init__(
        self, service_name: str, reset_time: Optional[datetime] = None, **kwargs
    ):
        super().__init__(service_name=service_name, reset_time=reset_time, **kwargs)


# Data Exceptions
class DataException(TeddyBearException):
    """Base for data related exceptions"""

    domain = ExceptionDomain.DATA_PROCESSING
    error_code = "TB_DATA_ERROR"


class ValidationException(DataException):
    """Data validation failures"""

    domain = ExceptionDomain.VALIDATION
    error_code = "TB_VALIDATION_ERROR"
    severity = ExceptionSeverity.LOW
    is_retryable = False

    def __init__(self, field: str, value: Any, reason: str, **kwargs):
        super().__init__(
            f"Validation failed for {field}: {reason}",
            field=field,
            value=str(value)[:100],  # Truncate for safety
            reason=reason,
            **kwargs,
        )


class DatabaseException(DataException):
    """Database operation failures"""

    domain = ExceptionDomain.DATABASE
    error_code = "TB_DATABASE_ERROR"
    is_retryable = True


# Performance Exceptions
class PerformanceException(TeddyBearException):
    """Performance related exceptions"""

    domain = ExceptionDomain.PERFORMANCE
    error_code = "TB_PERFORMANCE"
    severity = ExceptionSeverity.MEDIUM


class TimeoutException(PerformanceException):
    """Operation timeout"""

    error_code = "TB_TIMEOUT"

    def __init__(self, operation: str, timeout_seconds: float, **kwargs):
        super().__init__(
            f"Operation {operation} timed out after {timeout_seconds}s",
            operation=operation,
            timeout_seconds=timeout_seconds,
            **kwargs,
        )
