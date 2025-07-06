"""
Retry decorator with exponential backoff.
"""

import asyncio
import time
from dataclasses import dataclass
from functools import wraps
from typing import Callable, List, Optional, Type

import structlog

from src.domain.exceptions.infrastructure import (
    CircuitBreakerOpenException,
    DatabaseException,
    ExternalServiceException,
)

logger = structlog.get_logger(__name__)


@dataclass
class RetryConfig:
    """إعدادات إعادة المحاولة"""

    max_attempts: int = 3
    initial_delay: float = 1.0
    exponential_backoff: bool = True
    max_delay: float = 60.0
    exceptions_to_retry: Optional[List[Type[Exception]]] = None

    def __post_init__(self):
        if self.exceptions_to_retry is None:
            self.exceptions_to_retry = [
                DatabaseException,
                ExternalServiceException,
                CircuitBreakerOpenException,
            ]


def with_retry(
    config: Optional[RetryConfig] = None,
    on_retry: Optional[Callable[[Exception, int], None]] = None,
):
    """
    Decorator لإعادة المحاولة مع exponential backoff

    Args:
        config: إعدادات إعادة المحاولة
        on_retry: دالة يتم استدعاؤها عند كل إعادة محاولة
    """
    if config is None:
        config = RetryConfig()

    def _should_retry(e: Exception, attempt: int, config: RetryConfig) -> bool:
        """Determines if a retry should be attempted."""
        should_retry_exception = any(
            isinstance(e, exc_type) for exc_type in config.exceptions_to_retry
        )
        return should_retry_exception and attempt < config.max_attempts

    async def _handle_retry(
        e: Exception,
        attempt: int,
        func_name: str,
        delay: float,
        on_retry: Optional[Callable],
    ):
        """Handles the logging and delay for a retry attempt."""
        if on_retry:
            if asyncio.iscoroutinefunction(on_retry):
                await on_retry(e, attempt)
            else:
                on_retry(e, attempt)

        logger.warning(
            f"Retrying {func_name}",
            attempt=attempt,
            max_attempts=config.max_attempts,
            delay=delay,
            exception=type(e).__name__,
        )
        await asyncio.sleep(delay)

    def _handle_retry_sync(
        e: Exception,
        attempt: int,
        func_name: str,
        delay: float,
        on_retry: Optional[Callable],
    ):
        """Handles the logging and delay for a synchronous retry attempt."""
        if on_retry:
            on_retry(e, attempt)

        logger.warning(
            f"Retrying {func_name}",
            attempt=attempt,
            max_attempts=config.max_attempts,
            delay=delay,
            exception=type(e).__name__,
        )
        time.sleep(delay)

    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None
            delay = config.initial_delay

            for attempt in range(1, config.max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if not _should_retry(e, attempt, config):
                        raise

                    await _handle_retry(e, attempt, func.__name__, delay, on_retry)

                    if config.exponential_backoff:
                        delay = min(delay * 2, config.max_delay)

            raise last_exception

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exception = None
            delay = config.initial_delay

            for attempt in range(1, config.max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if not _should_retry(e, attempt, config):
                        raise

                    _handle_retry_sync(
                        e, attempt, func.__name__, delay, on_retry)

                    if config.exponential_backoff:
                        delay = min(delay * 2, config.max_delay)

            raise last_exception

        return async_wrapper if asyncio.iscoroutinefunction(
            func) else sync_wrapper

    return decorator
