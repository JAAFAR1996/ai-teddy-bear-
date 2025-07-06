"""
Security-related decorators.
"""

import asyncio
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Dict, Optional

import structlog

from src.domain.exceptions.child_safety import (
    InappropriateContentException,
    ParentalConsentRequiredException,
)
from src.domain.exceptions.security import (
    AuthenticationException,
    AuthorizationException,
)
from src.infrastructure.monitoring.metrics import MetricsCollector

logger = structlog.get_logger(__name__)


def child_safe(
    content_filter: Optional[Callable[[Any], bool]] = None,
    notify_parent: bool = True,
    log_violations: bool = True,
):
    """
    Decorator لضمان أمان المحتوى للأطفال

    Args:
        content_filter: دالة لفحص المحتوى
        notify_parent: إرسال إشعار للوالدين عند انتهاك
        log_violations: تسجيل الانتهاكات
    """

    async def _filter_content_async(content_filter, result):
        """Filters content asynchronously."""
        if content_filter:
            is_safe = (
                await content_filter(result)
                if asyncio.iscoroutinefunction(content_filter)
                else content_filter(result)
            )
            if not is_safe:
                raise InappropriateContentException(
                    content_type="response",
                    violation_reason="Content filter violation")

    def _filter_content_sync(content_filter, result):
        """Filters content synchronously."""
        if content_filter and not content_filter(result):
            raise InappropriateContentException(
                content_type="response",
                violation_reason="Content filter violation")

    def _handle_safety_violation(
        e: InappropriateContentException, func_name: str, log_violations: bool
    ):
        """Handles InappropriateContentException."""
        if log_violations:
            logger.error(
                "Child safety violation",
                function=func_name,
                violation_type=e.content_type,
                reason=e.violation_reason,
            )
        MetricsCollector.record_content_filtered(
            filter_type="function_decorator",
            reason=e.violation_reason or "unknown")
        return {
            "error": "Content not appropriate for children",
            "safe": True,
            "filtered": True,
        }

    def _handle_consent_exception(
            e: ParentalConsentRequiredException,
            func_name: str,
            log_violations: bool):
        """Handles ParentalConsentRequiredException."""
        if log_violations:
            logger.warning(
                "Parental consent required",
                function=func_name,
                action=e.action,
                reason=e.reason,
            )
        MetricsCollector.record_parental_consent(
            action=e.action, status="required")
        return {
            "error": "Parent approval needed",
            "action": "notify_parent",
            "consent_required": True,
            "details": {"action": e.action, "reason": e.reason},
        }

    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                await _filter_content_async(content_filter, result)
                return result
            except InappropriateContentException as e:
                return _handle_safety_violation(
                    e, func.__name__, log_violations)
            except ParentalConsentRequiredException as e:
                return _handle_consent_exception(
                    e, func.__name__, log_violations)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                _filter_content_sync(content_filter, result)
                return result
            except InappropriateContentException as e:
                return _handle_safety_violation(
                    e, func.__name__, log_violations)
            except ParentalConsentRequiredException as e:
                return _handle_consent_exception(
                    e, func.__name__, log_violations)

        return async_wrapper if asyncio.iscoroutinefunction(
            func) else sync_wrapper

    return decorator


def authenticated(
    required_role: Optional[str] = None,
    check_token_expiry: bool = True,
):
    """
    Decorator للتحقق من المصادقة والصلاحيات

    Args:
        required_role: الدور المطلوب
        check_token_expiry: التحقق من انتهاء صلاحية التوكن
    """

    def _get_auth_context(args, kwargs) -> Optional[Dict]:
        """Extracts the authentication context from function arguments."""
        if args and hasattr(args[0], "auth_context"):
            return args[0].auth_context
        return kwargs.get("auth_context")

    def _validate_authentication(auth_context: Optional[Dict]):
        """Validates that the user is authenticated."""
        if not auth_context or not auth_context.get("authenticated", False):
            raise AuthenticationException(reason="User not authenticated")

    def _validate_token_expiry(auth_context: Dict):
        """Validates the token's expiration date."""
        token_expiry = auth_context.get("token_expiry")
        if token_expiry and datetime.fromisoformat(
                token_expiry) < datetime.utcnow():
            raise AuthenticationException(
                reason="Token expired", auth_method="jwt")

    def _validate_role(auth_context: Dict, required_role: str, func_name: str):
        """Validates the user's role."""
        if required_role and required_role not in auth_context.get("roles", []):
            raise AuthorizationException(
                action=func_name, required_role=required_role)

    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            auth_context = _get_auth_context(args, kwargs)
            _validate_authentication(auth_context)

            if check_token_expiry:
                _validate_token_expiry(auth_context)

            if required_role:
                _validate_role(auth_context, required_role, func.__name__)

            return await func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            auth_context = _get_auth_context(args, kwargs)
            _validate_authentication(auth_context)

            if check_token_expiry:
                _validate_token_expiry(auth_context)

            if required_role:
                _validate_role(auth_context, required_role, func.__name__)

            return func(*args, **kwargs)

        return async_wrapper if asyncio.iscoroutinefunction(
            func) else sync_wrapper

    return decorator
