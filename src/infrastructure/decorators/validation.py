"""
Input validation decorator.
"""

import asyncio
import inspect
from functools import wraps
from typing import Any, Callable, Dict, Optional

from src.domain.exceptions.validation import ValidationException


def validate_input(
    validators: Dict[str, Callable[[Any], bool]],
    error_messages: Optional[Dict[str, str]] = None,
):
    """
    Decorator للتحقق من صحة المدخلات

    Args:
        validators: قاموس من validators لكل parameter
        error_messages: رسائل خطأ مخصصة
    """

    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Get function signature
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            # Validate each parameter
            for param_name, validator in validators.items():
                if param_name in bound_args.arguments:
                    value = bound_args.arguments[param_name]

                    try:
                        is_valid = (
                            await validator(value)
                            if asyncio.iscoroutinefunction(validator)
                            else validator(value)
                        )
                        if not is_valid:
                            error_msg = (
                                error_messages.get(param_name)
                                if error_messages
                                else f"Invalid {param_name}"
                            )
                            raise ValidationException(
                                message=error_msg, field_name=param_name
                            )
                    except Exception as e:
                        if isinstance(e, ValidationException):
                            raise
                        raise ValidationException(
                            message=f"Validation failed for {param_name}: {str(e)}",
                            field_name=param_name,
                        )

            return await func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Get function signature
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            # Validate each parameter
            for param_name, validator in validators.items():
                if param_name in bound_args.arguments:
                    value = bound_args.arguments[param_name]

                    try:
                        is_valid = validator(value)
                        if not is_valid:
                            error_msg = (
                                error_messages.get(param_name)
                                if error_messages
                                else f"Invalid {param_name}"
                            )
                            raise ValidationException(
                                message=error_msg, field_name=param_name
                            )
                    except Exception as e:
                        if isinstance(e, ValidationException):
                            raise
                        raise ValidationException(
                            message=f"Validation failed for {param_name}: {str(e)}",
                            field_name=param_name,
                        )

            return func(*args, **kwargs)

        return async_wrapper if asyncio.iscoroutinefunction(
            func) else sync_wrapper

    return decorator
