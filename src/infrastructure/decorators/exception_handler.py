"""
Exception Handler Decorator.
"""

import asyncio
from functools import wraps
from typing import Any, Callable, Optional, Tuple, Type

import structlog

from src.infrastructure.exception_handling.global_handler import get_global_exception_handler

logger = structlog.get_logger(__name__)


def handle_exceptions(
    *exception_handlers: Tuple[Type[Exception], Callable[[Exception], Any]],
    fallback: Optional[Callable[[], Any]] = None,
    log_errors: bool = True,
    propagate: bool = False,
    use_global_handler: bool = True,
):
    """
    Decorator for exception handling with custom handlers.

    Args:
        exception_handlers: Tuples of (exception_type, handler).
        fallback: Fallback function if no specific handler is found.
        log_errors: Whether to log errors.
        propagate: Whether to re-raise the exception after handling.
        use_global_handler: Use the global handler for unhandled exceptions.
    """

    def decorator(func):
        def _handle_custom_exception(
                e, exception_handlers, propagate) -> (bool, Any):
            """Handles a custom exception if a handler is registered."""
            for exception_type, handler in exception_handlers:
                if isinstance(e, exception_type):
                    try:
                        result = handler(e)
                        return True, result if not propagate else e
                    except Exception as handler_error:
                        logger.error(
                            f"Handler failed for {exception_type.__name__}",
                            handler_error=str(handler_error),
                        )
            return False, e

        async def _handle_custom_exception_async(
            e, exception_handlers, propagate
        ) -> (bool, Any):
            """Asynchronously handles a custom exception."""
            for exception_type, handler in exception_handlers:
                if isinstance(e, exception_type):
                    try:
                        result = (
                            await handler(e)
                            if asyncio.iscoroutinefunction(handler)
                            else handler(e)
                        )
                        return True, result if not propagate else e
                    except Exception as handler_error:
                        logger.error(
                            f"Handler failed for {exception_type.__name__}",
                            handler_error=str(handler_error),
                        )
            return False, e

        def _handle_global_exception(e, fallback, propagate) -> Any:
            """Handles an exception using the global handler."""
            global_handler = get_global_exception_handler()
            result = global_handler.handle_exception_sync(e)
            if not propagate:
                return result.get(
                    "recovery_result",
                    fallback() if fallback else None)
            return e  # Re-raise

        async def _handle_global_exception_async(
                e, fallback, propagate) -> Any:
            """Asynchronously handles an exception using the global handler."""
            global_handler = get_global_exception_handler()
            result = await global_handler.handle_exception(e)
            if not propagate:
                recovery_result = result.get("recovery_result")
                if recovery_result:
                    return recovery_result
                if fallback:
                    return (
                        await fallback()
                        if asyncio.iscoroutinefunction(fallback)
                        else fallback()
                    )
                return None
            return e  # Re-raise

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if log_errors:
                    logger.error(
                        f"Exception in {func.__name__}",
                        exc_info=True)

                handled, result = await _handle_custom_exception_async(
                    e, exception_handlers, propagate
                )
                if handled:
                    if propagate:
                        raise result
                    return result

                if use_global_handler:
                    result = await _handle_global_exception_async(
                        e, fallback, propagate
                    )
                    if propagate:
                        raise result
                    return result

                if fallback and not propagate:
                    return (
                        await fallback()
                        if asyncio.iscoroutinefunction(fallback)
                        else fallback()
                    )

                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_errors:
                    logger.error(
                        f"Exception in {func.__name__}",
                        exc_info=True)

                handled, result = _handle_custom_exception(
                    e, exception_handlers, propagate
                )
                if handled:
                    if propagate:
                        raise result
                    return result

                if use_global_handler:
                    result = _handle_global_exception(e, fallback, propagate)
                    if propagate:
                        raise result
                    return result

                if fallback and not propagate:
                    return fallback()

                raise

        return async_wrapper if asyncio.iscoroutinefunction(
            func) else sync_wrapper

    return decorator
