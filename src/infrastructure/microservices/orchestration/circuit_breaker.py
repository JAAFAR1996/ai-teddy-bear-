"""
Circuit breaker implementation to prevent repeated calls to failing services.
"""
import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Callable, Optional

from .models import CircuitBreakerState

logger = logging.getLogger(__name__)


class CircuitBreaker:
    """Circuit breaker implementation"""

    def __init__(self, threshold: int = 5, timeout: int = 60):
        self.threshold = threshold
        self.timeout = timeout
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker"""
        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
                logger.info(
                    "Circuit breaker is now HALF_OPEN. Attempting a call.")
            else:
                logger.warning("Circuit breaker is OPEN. Call rejected.")
                raise Exception("Circuit breaker is OPEN")

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            logger.error(
                f"Call failed. Circuit breaker recorded failure. Error: {e}", exc_info=True)
            raise e

    def _on_success(self):
        """Handle successful call"""
        if self.state == CircuitBreakerState.HALF_OPEN:
            logger.info(
                "Call successful in HALF_OPEN state. Circuit breaker is now CLOSED.")
        self.failure_count = 0
        self.state = CircuitBreakerState.CLOSED

    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.now(timezone.utc)

        if self.state == CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.OPEN
            logger.warning(
                "Call failed in HALF_OPEN state. Circuit breaker is OPEN again.")
        elif self.failure_count >= self.threshold:
            self.state = CircuitBreakerState.OPEN
            logger.warning(
                f"Failure threshold reached ({self.threshold}). Circuit breaker is now OPEN.")

    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt reset"""
        if not self.last_failure_time:
            return True

        time_since_failure = (
            datetime.now(timezone.utc) - self.last_failure_time
        ).total_seconds()
        return time_since_failure >= self.timeout
