"""
Circuit Breaker pattern implementation.
"""

import asyncio
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Type

import structlog

from src.domain.exceptions.base import CircuitBreakerOpenException
from src.infrastructure.monitoring.metrics import circuit_breaker_state

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
                        "Circuit breaker moving to HALF_OPEN",
                        service=self.service_name)
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
                    logger.info(
                        "Circuit breaker CLOSED",
                        service=self.service_name)

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
                error_percentage = (
                    self.stats.failure_count / total_requests) * 100
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
        return any(isinstance(exception, exc_type)
                   for exc_type in self.expected_exceptions)

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
