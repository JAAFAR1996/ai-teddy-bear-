"""
Global Exception Handler - معالج مركزي للـ exceptions
يتضمن Circuit Breaker pattern و monitoring و alerting
"""

import asyncio
import traceback
from collections import defaultdict
from typing import Any, Callable, Dict, Optional, Type

import structlog

from src.domain.exceptions.base import (
    AITeddyBearException,
    ErrorCategory,
    ErrorContext,
    ErrorSeverity,
)
from src.infrastructure.monitoring.alert_manager import AlertManager
from src.infrastructure.monitoring.metrics import error_counter
from .circuit_breaker import CircuitBreaker, CircuitState

logger = structlog.get_logger(__name__)


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

    def register_error_handler(self,
                               exception_type: Type[Exception],
                               handler: Callable[[Exception],
                                                 Any]) -> None:
        """تسجيل معالج خاص لنوع معين من الأخطاء"""
        self.error_handlers[exception_type] = handler

    def register_recovery_strategy(self, error_code: str, strategy: Callable[[
            Exception, ErrorContext], Any]) -> None:
        """تسجيل استراتيجية استرداد لكود خطأ معين"""
        self.recovery_strategies[error_code] = strategy

    def _extract_error_data(self, exception: Exception) -> Dict[str, Any]:
        """Extracts structured data from an exception."""
        if isinstance(exception, AITeddyBearException):
            return {
                **exception.to_dict(),
                "severity": exception.severity,
                "category": exception.category,
                "error_code": exception.error_code,
                "recoverable": exception.recoverable,
            }
        else:
            return {
                "error_code": "UNEXPECTED_ERROR",
                "message": str(exception),
                "severity": ErrorSeverity.HIGH,
                "category": ErrorCategory.INFRASTRUCTURE,
                "exception_type": type(exception).__name__,
                "stack_trace": traceback.format_exc(),
                "recoverable": False,
            }

    async def _process_error(
        self, error_data: Dict[str, Any], context: ErrorContext
    ) -> Dict[str, Any]:
        """Processes the extracted error data."""
        self._add_to_history(error_data["error_code"], error_data)

        log_method = self._get_log_method(error_data["severity"])
        log_method("Exception occurred", **error_data, exc_info=True)

        self._update_metrics(
            error_data["error_code"],
            error_data["category"],
            error_data["severity"])

        if error_data["severity"] == ErrorSeverity.CRITICAL:
            await self.alert_manager.send_critical_alert(error_data)

        self._check_circuit_breaker(
            error_data["error_code"],
            error_data["category"])
        return error_data

    async def _attempt_recovery(
        self, exception: Exception, context: ErrorContext, error_data: Dict
    ) -> Any:
        """Attempts to apply a recovery strategy."""
        if (
            error_data["recoverable"]
            and error_data["error_code"] in self.recovery_strategies
        ):
            try:
                return await self._apply_recovery_strategy(
                    exception, context, error_data["error_code"]
                )
            except Exception as recovery_error:
                logger.error(
                    "Recovery strategy failed",
                    error_code=error_data["error_code"],
                    recovery_error=str(recovery_error),
                )
        return None

    async def handle_exception(
        self,
        exception: Exception,
        context: Optional[ErrorContext] = None,
        apply_recovery: bool = True,
    ) -> Dict[str, Any]:
        """معالجة exception مع logging و monitoring و alerting"""
        context = context or ErrorContext()
        error_data = self._extract_error_data(exception)

        processed_data = await self._process_error(error_data, context)

        custom_result = await self._apply_custom_handler(exception)
        if custom_result is not None:
            return custom_result

        recovery_result = None
        if apply_recovery:
            recovery_result = await self._attempt_recovery(
                exception, context, processed_data
            )

        return {
            **processed_data,
            "handled": True,
            "recovery_attempted": recovery_result is not None,
            "recovery_result": recovery_result,
            "user_message": self._get_user_friendly_message(
                exception if isinstance(
                    exception,
                    AITeddyBearException) else None,
                processed_data["category"],
                processed_data["severity"],
            ),
        }

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
            error_code=error_code,
            category=category.value,
            severity=severity.value).inc()

    def _check_circuit_breaker(
            self,
            error_code: str,
            category: ErrorCategory) -> None:
        """التحقق من circuit breaker"""
        # Circuit breakers للخدمات الحرجة فقط
        if category in [
                ErrorCategory.EXTERNAL_SERVICE,
                ErrorCategory.INFRASTRUCTURE]:
            breaker_key = f"{category.value}_{error_code}"
            if breaker_key not in self.circuit_breakers:
                self.circuit_breakers[breaker_key] = CircuitBreaker(
                    service_name=breaker_key, failure_threshold=5, timeout_seconds=60)

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
                        "Custom handler failed",
                        handler=handler.__name__,
                        error=str(e))
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

    def _add_to_history(self, error_code: str,
                        error_data: Dict[str, Any]) -> None:
        """إضافة خطأ للتاريخ"""
        history = self._error_history[error_code]
        history.append(
            {"timestamp": datetime.utcnow().isoformat(), **error_data})

        # Keep only recent errors
        if len(history) > self._max_history_size:
            self._error_history[error_code] = history[-self._max_history_size:]

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

    def get_circuit_breaker(
            self,
            service_name: str) -> Optional[CircuitBreaker]:
        """الحصول على circuit breaker لخدمة معينة"""
        return self.circuit_breakers.get(service_name)

    def get_error_statistics(
            self, time_window_minutes: int = 60) -> Dict[str, Any]:
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
