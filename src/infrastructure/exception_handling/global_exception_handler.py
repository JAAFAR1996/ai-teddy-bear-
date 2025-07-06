"""
Enterprise-Grade Global Exception Handling System
"""

import asyncio
from typing import Any, Dict, Optional, Type

import structlog
from .alerting import AlertManager
from .context import (
    ExceptionContext,
    child_id_var,
    correlation_id_var,
    user_id_var,
)
from .exceptions import (
    DatabaseException,
    ExternalServiceException,
    TeddyBearException,
    TimeoutException,
    ValidationException,
)
from .metrics import exception_counter, exception_histogram
from .strategies import (
    CircuitBreakerStrategy,
    RecoveryStrategy,
    RetryStrategy,
)

# Setup structured logger
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


class GlobalExceptionHandler:
    """Central exception handling system"""

    def __init__(self):
        self.recovery_strategies: Dict[Type[Exception], RecoveryStrategy] = {}
        self.alert_manager = AlertManager()
        self._setup_default_strategies()

    def _setup_default_strategies(self):
        """Setup default recovery strategies"""
        self.recovery_strategies[ExternalServiceException] = RetryStrategy()
        self.recovery_strategies[DatabaseException] = RetryStrategy(
            max_retries=5)
        self.recovery_strategies[TimeoutException] = CircuitBreakerStrategy()

    def register_strategy(
        self, exception_type: Type[Exception], strategy: RecoveryStrategy
    ):
        """Register a recovery strategy for an exception type"""
        self.recovery_strategies[exception_type] = strategy

    async def handle_exception(self, exception: Exception) -> Optional[Any]:
        """Handle an exception with appropriate strategies"""
        with exception_histogram.labels(exception_type=type(exception).__name__).time():
            # Convert to TeddyBearException if needed
            if not isinstance(exception, TeddyBearException):
                exception = self._wrap_exception(exception)

            # Log the exception
            await self._log_exception(exception)

            # Update metrics
            exception_counter.labels(
                exception_type=type(exception).__name__,
                severity=exception.severity.name,
                domain=exception.domain.name,
            ).inc()

            # Send alerts if needed
            if exception.should_alert:
                await self.alert_manager.send_alert(exception)

            # Attempt recovery
            strategy = self.recovery_strategies.get(type(exception))
            if strategy:
                try:
                    return await strategy.recover(exception)
                except Exception as recovery_error:
                    logger.error(
                        "Recovery strategy failed",
                        original_exception=exception.to_dict(),
                        recovery_error=str(recovery_error),
                    )

            # Re-raise if no recovery possible
            raise exception

    def _wrap_exception(self, exception: Exception) -> TeddyBearException:
        """Wrap standard exceptions in TeddyBearException"""
        context = ExceptionContext(
            correlation_id=correlation_id_var.get(),
            user_id=user_id_var.get(),
            child_id=child_id_var.get(),
        )

        # Map common exceptions
        if isinstance(exception, ValueError):
            return ValidationException(
                field="unknown",
                value="unknown",
                reason=str(exception),
                context=context,
                cause=exception,
            )
        elif isinstance(exception, TimeoutError):
            return TimeoutException(
                operation="unknown", timeout_seconds=0, context=context, cause=exception
            )
        else:
            return TeddyBearException(
                message=str(exception), context=context, cause=exception
            )

    async def _log_exception(self, exception: TeddyBearException):
        """Log exception with appropriate detail level"""
        log_data = exception.to_dict()

        # Sanitize for child safety if needed
        if exception.context.child_id:
            log_data = exception.sanitize_for_child_logs()

        # Log based on severity
        if exception.severity.value >= 4:  # CRITICAL
            logger.critical("Critical exception occurred", **log_data)
        elif exception.severity.value == 3:  # HIGH
            logger.error("High severity exception", **log_data)
        elif exception.severity.value == 2:  # MEDIUM
            logger.warning("Medium severity exception", **log_data)
        else:  # LOW
            logger.info("Low severity exception", **log_data)


# Initialize global handler
global_exception_handler = GlobalExceptionHandler()
