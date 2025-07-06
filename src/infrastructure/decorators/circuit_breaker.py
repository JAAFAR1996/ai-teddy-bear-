"""
Circuit Breaker decorator.
"""

import asyncio
from functools import wraps
from typing import Any, Callable, Optional

import structlog

from src.domain.exceptions.infrastructure import CircuitBreakerOpenException
from src.infrastructure.exception_handling.global_handler import (
    CircuitBreaker,
    get_global_exception_handler,
)

logger = structlog.get_logger(__name__)


def with_circuit_breaker(
    service_name: str,
    failure_threshold: int = 5,
    timeout_seconds: int = 60,
    fallback: Optional[Callable[[], Any]] = None,
):
    """
    Decorator لحماية الدوال بـ Circuit Breaker

    Args:
        service_name: اسم الخدمة
        failure_threshold: عدد الفشل المسموح قبل فتح الدائرة
        timeout_seconds: وقت الانتظار قبل محاولة إعادة التعيين
        fallback: دالة بديلة عند فتح الدائرة
    """

    # Create or get circuit breaker
    global_handler = get_global_exception_handler()
    circuit_breaker = global_handler.get_circuit_breaker(service_name)

    if not circuit_breaker:
        circuit_breaker = CircuitBreaker(
            service_name=service_name,
            failure_threshold=failure_threshold,
            timeout_seconds=timeout_seconds,
        )
        global_handler.circuit_breakers[service_name] = circuit_breaker

    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await circuit_breaker.call(func, *args, **kwargs)
            except CircuitBreakerOpenException as e:
                logger.warning(
                    f"Circuit breaker open for {service_name}",
                    retry_after=e.retry_after,
                )
                if fallback:
                    return (
                        await fallback()
                        if asyncio.iscoroutinefunction(fallback)
                        else fallback()
                    )
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return circuit_breaker.call_sync(func, *args, **kwargs)
            except CircuitBreakerOpenException as e:
                logger.warning(
                    f"Circuit breaker open for {service_name}",
                    retry_after=e.retry_after,
                )
                if fallback:
                    return fallback()
                raise

        return async_wrapper if asyncio.iscoroutinefunction(
            func) else sync_wrapper

    return decorator
