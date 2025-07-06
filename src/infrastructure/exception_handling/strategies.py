"""
Recovery strategies for handling exceptions.
"""

import asyncio
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Callable

import structlog

from .exceptions import TeddyBearException

logger = structlog.get_logger(__name__)


class RecoveryStrategy(ABC):
    """Base class for recovery strategies"""

    @abstractmethod
    async def recover(self, exception: TeddyBearException) -> Any:
        """Attempt to recover from the exception"""
        pass


class RetryStrategy(RecoveryStrategy):
    """Retry with exponential backoff"""

    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay

    async def recover(self, exception: TeddyBearException) -> Any:
        """Retry the operation"""
        if not exception.is_retryable:
            raise exception

        for attempt in range(self.max_retries):
            try:
                # This would need the original operation
                # For now, just demonstrate the pattern
                delay = self.base_delay * (2**attempt)
                await asyncio.sleep(delay)
                # Retry operation here
                return None

            except Exception:
                if attempt == self.max_retries - 1:
                    raise
                continue


class CircuitBreakerStrategy(RecoveryStrategy):
    """Circuit breaker pattern"""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        half_open_max_calls: int = 3,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
        self.half_open_calls = 0

    async def recover(self, exception: TeddyBearException) -> Any:
        """Implement circuit breaker logic"""
        if self.state == "open":
            # Check if we should transition to half-open
            if (
                datetime.now(timezone.utc) - self.last_failure_time
            ).total_seconds() > self.recovery_timeout:
                self.state = "half-open"
                self.half_open_calls = 0
            else:
                raise exception

        if self.state == "half-open":
            self.half_open_calls += 1
            if self.half_open_calls > self.half_open_max_calls:
                # Success threshold reached, close circuit
                self.state = "closed"
                self.failure_count = 0

        # Record failure
        self.failure_count += 1
        self.last_failure_time = datetime.now(timezone.utc)

        if self.failure_count >= self.failure_threshold:
            self.state = "open"
            # active_circuit_breakers.labels(
            #     service=exception.details.get("service_name", "unknown")
            # ).inc()

        raise exception


class FallbackStrategy(RecoveryStrategy):
    """Fallback to alternative implementation"""

    def __init__(self, fallback_func: Callable):
        self.fallback_func = fallback_func

    async def recover(self, exception: TeddyBearException) -> Any:
        """Execute fallback function"""
        logger.warning("Executing fallback strategy",
                       exception=exception.to_dict())
        return await self.fallback_func()
