"""
Infrastructure Exception Classes
استثناءات البنية التحتية والخدمات الخارجية
"""

from datetime import datetime
from typing import Optional

from .base import AITeddyBearException, ErrorCategory, ErrorSeverity


class InfrastructureException(AITeddyBearException):
    """Base infrastructure exception"""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            error_code=kwargs.get("error_code", "INFRASTRUCTURE_ERROR"),
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.INFRASTRUCTURE,
            recoverable=True,
            **{k: v for k, v in kwargs.items() if k != "error_code"},
        )


class DatabaseException(InfrastructureException):
    """خطأ في قاعدة البيانات"""

    def __init__(
        self,
        operation: str,
        table_name: Optional[str] = None,
        original_error: Optional[Exception] = None,
        **kwargs,
    ):
        message = f"Database error during {operation}"
        if table_name:
            message += f" on table {table_name}"

        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            suggested_actions=["Retry operation", "Check database connection"],
            **kwargs,
        )
        self.operation = operation
        self.table_name = table_name
        self.original_error = original_error


class ExternalServiceException(InfrastructureException):
    """خطأ في خدمة خارجية"""

    def __init__(
        self,
        service_name: str,
        status_code: Optional[int] = None,
        response_body: Optional[str] = None,
        **kwargs,
    ):
        message = f"External service '{service_name}' error"
        if status_code:
            message += f" - Status: {status_code}"

        super().__init__(
            message=message,
            error_code="EXTERNAL_SERVICE_ERROR",
            category=ErrorCategory.EXTERNAL_SERVICE,
            retry_after=kwargs.get("retry_after", 60),
            **kwargs,
        )
        self.service_name = service_name
        self.status_code = status_code
        self.response_body = response_body


class CircuitBreakerOpenException(InfrastructureException):
    """Circuit breaker مفتوح"""

    def __init__(
        self,
        service_name: str,
        failure_count: int,
        last_failure_time: datetime,
        **kwargs,
    ):
        super().__init__(
            message=f"Circuit breaker is OPEN for service '{service_name}'",
            error_code="CIRCUIT_BREAKER_OPEN",
            retry_after=kwargs.get("retry_after", 60),
            suggested_actions=["Wait before retry", "Use fallback service"],
            **kwargs,
        )
        self.service_name = service_name
        self.failure_count = failure_count
        self.last_failure_time = last_failure_time
