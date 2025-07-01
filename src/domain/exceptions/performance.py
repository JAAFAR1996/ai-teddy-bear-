"""
Performance Exception Classes
استثناءات الأداء ومعدلات التحديد
"""

from .base import AITeddyBearException, ErrorCategory, ErrorSeverity


class PerformanceException(AITeddyBearException):
    """Base performance exception"""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            error_code=kwargs.get("error_code", "PERFORMANCE_ERROR"),
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.PERFORMANCE,
            recoverable=True,
            **{k: v for k, v in kwargs.items() if k != "error_code"},
        )


class TimeoutException(PerformanceException):
    """انتهاء وقت العملية"""

    def __init__(self, operation: str, timeout_seconds: float, **kwargs):
        super().__init__(
            message=f"Operation '{operation}' timed out after {timeout_seconds} seconds",
            error_code="OPERATION_TIMEOUT",
            suggested_actions=["Retry with longer timeout", "Check system performance"],
            **kwargs,
        )
        self.operation = operation
        self.timeout_seconds = timeout_seconds


class RateLimitException(PerformanceException):
    """تجاوز معدل الطلبات المسموح"""

    def __init__(self, limit_type: str, current_rate: float, max_rate: float, window_seconds: int = 60, **kwargs):
        retry_after = window_seconds
        super().__init__(
            message=f"Rate limit exceeded for {limit_type}: {current_rate}/{max_rate} per {window_seconds}s",
            error_code="RATE_LIMIT_EXCEEDED",
            retry_after=retry_after,
            suggested_actions=["Wait before retrying", "Reduce request rate"],
            **kwargs,
        )
        self.limit_type = limit_type
        self.current_rate = current_rate
        self.max_rate = max_rate
        self.window_seconds = window_seconds
