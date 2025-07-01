"""
Global Exception Handler - معالج مركزي للـ exceptions
يتضمن Circuit Breaker pattern و monitoring و alerting
"""

import asyncio
import traceback
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Type, Union

import structlog

from src.domain.exceptions.base import (AITeddyBearException,
                                        CircuitBreakerOpenException,
                                        ErrorCategory, ErrorContext,
                                        ErrorSeverity)
from src.infrastructure.monitoring.alert_manager import AlertManager
from src.infrastructure.monitoring.metrics import (MetricsCollector,
                                                   circuit_breaker_state,
                                                   error_counter)

logger = structlog.get_logger(__name__)


class CircuitState(Enum):
    """حالات Circuit Breaker"""

    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


@dataclass
class CircuitStats:
    """إحصائيات Circuit Breaker"""

    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    last_state_change: datetime = field(default_factory=datetime.utcnow)
    consecutive_successes: int = 0
    error_percentages: Dict[str, float] = field(default_factory=dict)


class CircuitBreaker:
    """Circuit Breaker pattern لحماية النظام من الفشل المتكرر"""

    def __init__(
        self,
        service_name: str,
        failure_threshold: int = 5,
        success_threshold: int = 3,
        timeout_seconds: int = 60,
        half_open_requests: int = 3,
        error_threshold_percentage: float = 50.0,
        expected_exceptions: Optional[List[Type[Exception]]] = None,
    ):
        self.service_name = service_name
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout_seconds = timeout_seconds
        self.half_open_requests = half_open_requests
        self.error_threshold_percentage = error_threshold_percentage
        self.expected_exceptions = expected_exceptions or [Exception]

        self.state = CircuitState.CLOSED
        self.stats = CircuitStats()
        self._half_open_counter = 0
        self._request_history = defaultdict(int)
        self._lock = asyncio.Lock()

        # Update metrics
        self._update_metrics()

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """تنفيذ الدالة مع حماية Circuit Breaker"""
        async with self._lock:
            if self.state == CircuitState.OPEN:
                if await self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                    self.stats.last_state_change = datetime.utcnow()
                    self._half_open_counter = 0
                    logger.info(
                        "Circuit breaker moving to HALF_OPEN", service=self.service_name
                    )
                else:
                    raise CircuitBreakerOpenException(
                        service_name=self.service_name,
                        failure_count=self.stats.failure_count,
                        last_failure_time=self.stats.last_failure_time,
                        retry_after=self.timeout_seconds,
                    )

        # Execute function based on state
        try:
            if self.state == CircuitState.HALF_OPEN:
                async with self._lock:
                    if self._half_open_counter >= self.half_open_requests:
                        # Already processed allowed half-open requests
                        raise CircuitBreakerOpenException(
                            service_name=self.service_name,
                            failure_count=self.stats.failure_count,
                            last_failure_time=self.stats.last_failure_time,
                        )
                    self._half_open_counter += 1

            # Call the function
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = await asyncio.get_event_loop().run_in_executor(
                    None, func, *args, **kwargs
                )

            await self._on_success()
            return result

        except Exception as e:
            if self._is_expected_exception(e):
                await self._on_failure(e)
            raise

    def call_sync(self, func: Callable, *args, **kwargs) -> Any:
        """نسخة synchronous من call"""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset_sync():
                self.state = CircuitState.HALF_OPEN
                self.stats.last_state_change = datetime.utcnow()
                self._half_open_counter = 0
            else:
                raise CircuitBreakerOpenException(
                    service_name=self.service_name,
                    failure_count=self.stats.failure_count,
                    last_failure_time=self.stats.last_failure_time,
                    retry_after=self.timeout_seconds,
                )

        try:
            result = func(*args, **kwargs)
            self._on_success_sync()
            return result
        except Exception as e:
            if self._is_expected_exception(e):
                self._on_failure_sync(e)
            raise

    async def _on_success(self) -> None:
        """معالجة النجاح"""
        async with self._lock:
            self.stats.success_count += 1
            self.stats.last_success_time = datetime.utcnow()
            self.stats.consecutive_successes += 1

            if self.state == CircuitState.HALF_OPEN:
                if self.stats.consecutive_successes >= self.success_threshold:
                    self.state = CircuitState.CLOSED
                    self.stats.failure_count = 0
                    self.stats.consecutive_successes = 0
                    self.stats.last_state_change = datetime.utcnow()
                    logger.info("Circuit breaker CLOSED", service=self.service_name)

            self._update_metrics()

    def _on_success_sync(self) -> None:
        """معالجة النجاح synchronous"""
        self.stats.success_count += 1
        self.stats.last_success_time = datetime.utcnow()
        self.stats.consecutive_successes += 1

        if self.state == CircuitState.HALF_OPEN:
            if self.stats.consecutive_successes >= self.success_threshold:
                self.state = CircuitState.CLOSED
                self.stats.failure_count = 0
                self.stats.consecutive_successes = 0

        self._update_metrics()

    async def _on_failure(self, exception: Exception) -> None:
        """معالجة الفشل"""
        async with self._lock:
            self.stats.failure_count += 1
            self.stats.last_failure_time = datetime.utcnow()
            self.stats.consecutive_successes = 0

            # Track error types
            error_type = type(exception).__name__
            self._request_history[error_type] += 1

            # Calculate error percentage
            total_requests = self.stats.success_count + self.stats.failure_count
            if total_requests > 0:
                error_percentage = (self.stats.failure_count / total_requests) * 100
                self.stats.error_percentages[error_type] = error_percentage

                # Check if we should open the circuit
                if (
                    self.stats.failure_count >= self.failure_threshold
                    or error_percentage >= self.error_threshold_percentage
                ):
                    if self.state != CircuitState.OPEN:
                        self.state = CircuitState.OPEN
                        self.stats.last_state_change = datetime.utcnow()
                        logger.error(
                            "Circuit breaker OPEN",
                            service=self.service_name,
                            failure_count=self.stats.failure_count,
                            error_percentage=error_percentage,
                        )

            elif self.state == CircuitState.HALF_OPEN:
                # Single failure in half-open state reopens circuit
                self.state = CircuitState.OPEN
                self.stats.last_state_change = datetime.utcnow()

            self._update_metrics()

    def _on_failure_sync(self, exception: Exception) -> None:
        """معالجة الفشل synchronous"""
        self.stats.failure_count += 1
        self.stats.last_failure_time = datetime.utcnow()
        self.stats.consecutive_successes = 0

        if self.stats.failure_count >= self.failure_threshold:
            if self.state != CircuitState.OPEN:
                self.state = CircuitState.OPEN
                self.stats.last_state_change = datetime.utcnow()

        elif self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            self.stats.last_state_change = datetime.utcnow()

        self._update_metrics()

    async def _should_attempt_reset(self) -> bool:
        """التحقق من إمكانية محاولة إعادة التعيين"""
        if not self.stats.last_failure_time:
            return True

        time_since_failure = datetime.utcnow() - self.stats.last_failure_time
        return time_since_failure > timedelta(seconds=self.timeout_seconds)

    def _should_attempt_reset_sync(self) -> bool:
        """التحقق من إمكانية محاولة إعادة التعيين synchronous"""
        if not self.stats.last_failure_time:
            return True

        time_since_failure = datetime.utcnow() - self.stats.last_failure_time
        return time_since_failure > timedelta(seconds=self.timeout_seconds)

    def _is_expected_exception(self, exception: Exception) -> bool:
        """التحقق من أن الاستثناء متوقع"""
        return any(
            isinstance(exception, exc_type) for exc_type in self.expected_exceptions
        )

    def _update_metrics(self) -> None:
        """تحديث metrics"""
        state_map = {
            CircuitState.CLOSED: 0,
            CircuitState.OPEN: 1,
            CircuitState.HALF_OPEN: 2,
        }
        circuit_breaker_state.labels(service=self.service_name).set(
            state_map[self.state]
        )

    def get_status(self) -> Dict[str, Any]:
        """الحصول على حالة Circuit Breaker"""
        return {
            "service": self.service_name,
            "state": self.state.value,
            "stats": {
                "failure_count": self.stats.failure_count,
                "success_count": self.stats.success_count,
                "consecutive_successes": self.stats.consecutive_successes,
                "last_failure": (
                    self.stats.last_failure_time.isoformat()
                    if self.stats.last_failure_time
                    else None
                ),
                "last_success": (
                    self.stats.last_success_time.isoformat()
                    if self.stats.last_success_time
                    else None
                ),
                "last_state_change": self.stats.last_state_change.isoformat(),
                "error_percentages": self.stats.error_percentages,
            },
            "config": {
                "failure_threshold": self.failure_threshold,
                "success_threshold": self.success_threshold,
                "timeout_seconds": self.timeout_seconds,
                "error_threshold_percentage": self.error_threshold_percentage,
            },
        }

    async def reset(self) -> None:
        """إعادة تعيين Circuit Breaker"""
        async with self._lock:
            self.state = CircuitState.CLOSED
            self.stats = CircuitStats()
            self._half_open_counter = 0
            self._request_history.clear()
            self._update_metrics()
            logger.info("Circuit breaker reset", service=self.service_name)


class GlobalExceptionHandler:
    """معالج مركزي لجميع الـ exceptions مع monitoring و alerting"""

    def __init__(self):
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.error_metrics = defaultdict(int)
        self.alert_manager = AlertManager()
        self.error_handlers: Dict[Type[Exception], Callable] = {}
        self.recovery_strategies: Dict[str, Callable] = {}
        self._error_history = defaultdict(list)
        self._max_history_size = 1000

    def register_error_handler(
        self, exception_type: Type[Exception], handler: Callable[[Exception], Any]
    ) -> None:
        """تسجيل معالج خاص لنوع معين من الأخطاء"""
        self.error_handlers[exception_type] = handler

    def register_recovery_strategy(
        self, error_code: str, strategy: Callable[[Exception, ErrorContext], Any]
    ) -> None:
        """تسجيل استراتيجية استرداد لكود خطأ معين"""
        self.recovery_strategies[error_code] = strategy

    async def handle_exception(
        self,
        exception: Exception,
        context: Optional[ErrorContext] = None,
        apply_recovery: bool = True,
    ) -> Dict[str, Any]:
        """معالجة exception مع logging و monitoring و alerting"""

        # Create context if not provided
        if not context:
            context = ErrorContext()

        # Extract exception details
        if isinstance(exception, AITeddyBearException):
            error_data = exception.to_dict()
            severity = exception.severity
            category = exception.category
            error_code = exception.error_code
            recoverable = exception.recoverable
        else:
            # Handle unexpected exceptions
            error_data = {
                "error_code": "UNEXPECTED_ERROR",
                "message": str(exception),
                "severity": ErrorSeverity.HIGH.value,
                "category": ErrorCategory.INFRASTRUCTURE.value,
                "exception_type": type(exception).__name__,
                "stack_trace": traceback.format_exc(),
            }
            severity = ErrorSeverity.HIGH
            category = ErrorCategory.INFRASTRUCTURE
            error_code = "UNEXPECTED_ERROR"
            recoverable = False

        # Add to error history
        self._add_to_history(error_code, error_data)

        # Log with appropriate level
        log_method = self._get_log_method(severity)
        log_method("Exception occurred", **error_data, exc_info=True)

        # Update metrics
        self._update_metrics(error_code, category, severity)

        # Check for custom handler
        custom_result = await self._apply_custom_handler(exception)
        if custom_result is not None:
            return custom_result

        # Send alerts for critical errors
        if severity == ErrorSeverity.CRITICAL:
            await self.alert_manager.send_critical_alert(error_data)

        # Check circuit breaker
        self._check_circuit_breaker(error_code, category)

        # Apply recovery strategy if available and requested
        recovery_result = None
        if apply_recovery and recoverable and error_code in self.recovery_strategies:
            try:
                recovery_result = await self._apply_recovery_strategy(
                    exception, context, error_code
                )
            except Exception as recovery_error:
                logger.error(
                    "Recovery strategy failed",
                    error_code=error_code,
                    recovery_error=str(recovery_error),
                )

        # Build response
        response = {
            **error_data,
            "handled": True,
            "recovery_attempted": recovery_result is not None,
            "recovery_result": recovery_result,
            "user_message": self._get_user_friendly_message(
                exception if isinstance(exception, AITeddyBearException) else None,
                category,
                severity,
            ),
        }

        return response

    def handle_exception_sync(
        self, exception: Exception, context: Optional[ErrorContext] = None
    ) -> Dict[str, Any]:
        """نسخة synchronous من handle_exception"""
        # Similar logic but without async/await
        if isinstance(exception, AITeddyBearException):
            error_data = exception.to_dict()
            severity = exception.severity
            category = exception.category
            error_code = exception.error_code
        else:
            error_data = {
                "error_code": "UNEXPECTED_ERROR",
                "message": str(exception),
                "severity": ErrorSeverity.HIGH.value,
                "category": ErrorCategory.INFRASTRUCTURE.value,
            }
            severity = ErrorSeverity.HIGH
            category = ErrorCategory.INFRASTRUCTURE
            error_code = "UNEXPECTED_ERROR"

        log_method = self._get_log_method(severity)
        log_method("Exception occurred", **error_data, exc_info=True)

        self._update_metrics(error_code, category, severity)

        return error_data

    def _get_log_method(self, severity: ErrorSeverity):
        """الحصول على طريقة logging المناسبة"""
        mapping = {
            ErrorSeverity.LOW: logger.debug,
            ErrorSeverity.MEDIUM: logger.info,
            ErrorSeverity.HIGH: logger.warning,
            ErrorSeverity.CRITICAL: logger.error,
        }
        return mapping.get(severity, logger.error)

    def _update_metrics(
        self, error_code: str, category: ErrorCategory, severity: ErrorSeverity
    ) -> None:
        """تحديث metrics للـ monitoring"""
        self.error_metrics[f"error.{category.value}.{error_code}"] += 1

        # Prometheus metrics
        error_counter.labels(
            error_code=error_code, category=category.value, severity=severity.value
        ).inc()

    def _check_circuit_breaker(self, error_code: str, category: ErrorCategory) -> None:
        """التحقق من circuit breaker"""
        # Circuit breakers للخدمات الحرجة فقط
        if category in [ErrorCategory.EXTERNAL_SERVICE, ErrorCategory.INFRASTRUCTURE]:
            breaker_key = f"{category.value}_{error_code}"
            if breaker_key not in self.circuit_breakers:
                self.circuit_breakers[breaker_key] = CircuitBreaker(
                    service_name=breaker_key, failure_threshold=5, timeout_seconds=60
                )

    async def _apply_custom_handler(
        self, exception: Exception
    ) -> Optional[Dict[str, Any]]:
        """تطبيق معالج مخصص إن وجد"""
        for exc_type, handler in self.error_handlers.items():
            if isinstance(exception, exc_type):
                try:
                    if asyncio.iscoroutinefunction(handler):
                        return await handler(exception)
                    else:
                        return handler(exception)
                except Exception as e:
                    logger.error(
                        "Custom handler failed", handler=handler.__name__, error=str(e)
                    )
        return None

    async def _apply_recovery_strategy(
        self, exception: Exception, context: ErrorContext, error_code: str
    ) -> Any:
        """تطبيق استراتيجية الاسترداد"""
        strategy = self.recovery_strategies.get(error_code)
        if strategy:
            if asyncio.iscoroutinefunction(strategy):
                return await strategy(exception, context)
            else:
                return strategy(exception, context)
        return None

    def _add_to_history(self, error_code: str, error_data: Dict[str, Any]) -> None:
        """إضافة خطأ للتاريخ"""
        history = self._error_history[error_code]
        history.append({"timestamp": datetime.utcnow().isoformat(), **error_data})

        # Keep only recent errors
        if len(history) > self._max_history_size:
            self._error_history[error_code] = history[-self._max_history_size :]

    def _get_user_friendly_message(
        self,
        exception: Optional[AITeddyBearException],
        category: ErrorCategory,
        severity: ErrorSeverity,
    ) -> str:
        """الحصول على رسالة صديقة للمستخدم"""
        if exception and hasattr(exception, "get_user_friendly_message"):
            return exception.get_user_friendly_message()

        if category == ErrorCategory.CHILD_SAFETY:
            return "عذراً، لا يمكن إتمام هذا الإجراء لحماية الطفل"
        elif category == ErrorCategory.SECURITY:
            return "عذراً، حدث خطأ في الأمان. يرجى المحاولة مرة أخرى"
        elif severity == ErrorSeverity.CRITICAL:
            return "عذراً، حدث خطأ في النظام. يرجى التواصل مع الدعم الفني"
        else:
            return "عذراً، حدث خطأ. يرجى المحاولة مرة أخرى"

    def get_circuit_breaker(self, service_name: str) -> Optional[CircuitBreaker]:
        """الحصول على circuit breaker لخدمة معينة"""
        return self.circuit_breakers.get(service_name)

    def get_error_statistics(self, time_window_minutes: int = 60) -> Dict[str, Any]:
        """الحصول على إحصائيات الأخطاء"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=time_window_minutes)

        stats = {
            "time_window_minutes": time_window_minutes,
            "total_errors": sum(self.error_metrics.values()),
            "errors_by_category": defaultdict(int),
            "errors_by_code": dict(self.error_metrics),
            "recent_errors": [],
            "circuit_breakers": {},
        }

        # Recent errors
        for error_code, history in self._error_history.items():
            recent = [
                err
                for err in history
                if datetime.fromisoformat(err["timestamp"]) > cutoff_time
            ]
            if recent:
                stats["recent_errors"].extend(recent[-5:])  # Last 5 errors

        # Circuit breaker status
        for name, breaker in self.circuit_breakers.items():
            stats["circuit_breakers"][name] = breaker.get_status()

        return stats

    async def health_check(self) -> Dict[str, Any]:
        """فحص صحة نظام معالجة الأخطاء"""
        return {
            "status": "healthy",
            "total_circuit_breakers": len(self.circuit_breakers),
            "open_circuit_breakers": sum(
                1
                for cb in self.circuit_breakers.values()
                if cb.state == CircuitState.OPEN
            ),
            "total_errors_handled": sum(self.error_metrics.values()),
            "alert_manager_status": "active",
        }


# Global instance
_global_handler = GlobalExceptionHandler()


def get_global_exception_handler() -> GlobalExceptionHandler:
    """الحصول على المعالج العام"""
    return _global_handler


# Convenience functions
async def handle_exception(
    exception: Exception, context: Optional[ErrorContext] = None
) -> Dict[str, Any]:
    """دالة مساعدة لمعالجة الأخطاء"""
    return await _global_handler.handle_exception(exception, context)


def handle_exception_sync(
    exception: Exception, context: Optional[ErrorContext] = None
) -> Dict[str, Any]:
    """دالة مساعدة synchronous لمعالجة الأخطاء"""
    return _global_handler.handle_exception_sync(exception, context)
