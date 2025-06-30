"""
Exception Handler Decorators - Decorators لمعالجة الأخطاء
توفر طرق سهلة لمعالجة الأخطاء في الدوال والـ methods
"""
from functools import wraps
from typing import Type, Tuple, Optional, Callable, Any, Dict, List, Union
import asyncio
import time
from datetime import datetime
import structlog
from dataclasses import dataclass

from src.domain.exceptions.base import (
    AITeddyBearException, ErrorContext, ErrorSeverity,
    InappropriateContentException, ParentalConsentRequiredException,
    ValidationException, AuthenticationException, DatabaseException,
    ExternalServiceException, CircuitBreakerOpenException
)
from src.infrastructure.exception_handling.global_handler import (
    get_global_exception_handler, CircuitBreaker
)
from src.infrastructure.monitoring.metrics import (
    MetricsCollector, track_request_duration, exception_counter
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
                CircuitBreakerOpenException
            ]


def handle_exceptions(
    *exception_handlers: Tuple[Type[Exception], Callable[[Exception], Any]],
    fallback: Optional[Callable[[], Any]] = None,
    log_errors: bool = True,
    propagate: bool = False,
    use_global_handler: bool = True
):
    """
    Decorator للـ exception handling مع custom handlers
    
    Args:
        exception_handlers: أزواج من (نوع الاستثناء، معالج الاستثناء)
        fallback: دالة fallback في حالة عدم وجود معالج مناسب
        log_errors: تسجيل الأخطاء
        propagate: إعادة رمي الاستثناء بعد معالجته
        use_global_handler: استخدام المعالج العام للأخطاء غير المعالجة
    """
    
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                # Log error if enabled
                if log_errors:
                    logger.error(
                        f"Exception in {func.__name__}",
                        exception=type(e).__name__,
                        message=str(e),
                        exc_info=True
                    )
                    
                # Try custom handlers
                for exception_type, handler in exception_handlers:
                    if isinstance(e, exception_type):
                        try:
                            result = await handler(e) if asyncio.iscoroutinefunction(handler) else handler(e)
                            if not propagate:
                                return result
                            else:
                                raise
                        except Exception as handler_error:
                            logger.error(
                                f"Handler failed for {exception_type.__name__}",
                                handler_error=str(handler_error)
                            )
                            
                # Use global handler if enabled
                if use_global_handler:
                    global_handler = get_global_exception_handler()
                    result = await global_handler.handle_exception(e)
                    if not propagate:
                        return result.get("recovery_result", fallback() if fallback else None)
                        
                # Use fallback if available
                if fallback and not propagate:
                    return await fallback() if asyncio.iscoroutinefunction(fallback) else fallback()
                    
                # Re-raise if no handler found or propagate is True
                raise
                
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Log error if enabled
                if log_errors:
                    logger.error(
                        f"Exception in {func.__name__}",
                        exception=type(e).__name__,
                        message=str(e),
                        exc_info=True
                    )
                    
                # Try custom handlers
                for exception_type, handler in exception_handlers:
                    if isinstance(e, exception_type):
                        try:
                            result = handler(e)
                            if not propagate:
                                return result
                            else:
                                raise
                        except Exception as handler_error:
                            logger.error(
                                f"Handler failed for {exception_type.__name__}",
                                handler_error=str(handler_error)
                            )
                            
                # Use global handler if enabled
                if use_global_handler:
                    global_handler = get_global_exception_handler()
                    result = global_handler.handle_exception_sync(e)
                    if not propagate:
                        return result.get("recovery_result", fallback() if fallback else None)
                        
                # Use fallback if available
                if fallback and not propagate:
                    return fallback()
                    
                # Re-raise if no handler found or propagate is True
                raise
                
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


def with_retry(
    config: Optional[RetryConfig] = None,
    on_retry: Optional[Callable[[Exception, int], None]] = None
):
    """
    Decorator لإعادة المحاولة مع exponential backoff
    
    Args:
        config: إعدادات إعادة المحاولة
        on_retry: دالة يتم استدعاؤها عند كل إعادة محاولة
    """
    if config is None:
        config = RetryConfig()
        
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
                    
                    # Check if we should retry this exception
                    should_retry = any(
                        isinstance(e, exc_type) 
                        for exc_type in config.exceptions_to_retry
                    )
                    
                    if not should_retry or attempt == config.max_attempts:
                        raise
                        
                    # Call on_retry callback if provided
                    if on_retry:
                        if asyncio.iscoroutinefunction(on_retry):
                            await on_retry(e, attempt)
                        else:
                            on_retry(e, attempt)
                            
                    # Log retry attempt
                    logger.warning(
                        f"Retrying {func.__name__}",
                        attempt=attempt,
                        max_attempts=config.max_attempts,
                        delay=delay,
                        exception=type(e).__name__
                    )
                    
                    # Wait before retry
                    await asyncio.sleep(delay)
                    
                    # Calculate next delay
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
                    
                    # Check if we should retry this exception
                    should_retry = any(
                        isinstance(e, exc_type) 
                        for exc_type in config.exceptions_to_retry
                    )
                    
                    if not should_retry or attempt == config.max_attempts:
                        raise
                        
                    # Call on_retry callback if provided
                    if on_retry:
                        on_retry(e, attempt)
                        
                    # Log retry attempt
                    logger.warning(
                        f"Retrying {func.__name__}",
                        attempt=attempt,
                        max_attempts=config.max_attempts,
                        delay=delay,
                        exception=type(e).__name__
                    )
                    
                    # Wait before retry
                    time.sleep(delay)
                    
                    # Calculate next delay
                    if config.exponential_backoff:
                        delay = min(delay * 2, config.max_delay)
                        
            raise last_exception
            
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


def with_circuit_breaker(
    service_name: str,
    failure_threshold: int = 5,
    timeout_seconds: int = 60,
    fallback: Optional[Callable[[], Any]] = None
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
            timeout_seconds=timeout_seconds
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
                    retry_after=e.retry_after
                )
                if fallback:
                    return await fallback() if asyncio.iscoroutinefunction(fallback) else fallback()
                raise
                
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return circuit_breaker.call_sync(func, *args, **kwargs)
            except CircuitBreakerOpenException as e:
                logger.warning(
                    f"Circuit breaker open for {service_name}",
                    retry_after=e.retry_after
                )
                if fallback:
                    return fallback()
                raise
                
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


def child_safe(
    content_filter: Optional[Callable[[Any], bool]] = None,
    notify_parent: bool = True,
    log_violations: bool = True
):
    """
    Decorator لضمان أمان المحتوى للأطفال
    
    Args:
        content_filter: دالة لفحص المحتوى
        notify_parent: إرسال إشعار للوالدين عند انتهاك
        log_violations: تسجيل الانتهاكات
    """
    
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                
                # Apply content filter if provided
                if content_filter:
                    is_safe = await content_filter(result) if asyncio.iscoroutinefunction(content_filter) else content_filter(result)
                    if not is_safe:
                        raise InappropriateContentException(
                            content_type="response",
                            violation_reason="Content filter violation"
                        )
                        
                return result
                
            except InappropriateContentException as e:
                if log_violations:
                    logger.error(
                        "Child safety violation",
                        function=func.__name__,
                        violation_type=e.content_type,
                        reason=e.violation_reason
                    )
                    
                # Record metric
                MetricsCollector.record_content_filtered(
                    filter_type="function_decorator",
                    reason=e.violation_reason or "unknown"
                )
                
                # Return safe response
                return {
                    "error": "Content not appropriate for children",
                    "safe": True,
                    "filtered": True
                }
                
            except ParentalConsentRequiredException as e:
                if log_violations:
                    logger.warning(
                        "Parental consent required",
                        function=func.__name__,
                        action=e.action,
                        reason=e.reason
                    )
                    
                # Record metric
                MetricsCollector.record_parental_consent(
                    action=e.action,
                    status="required"
                )
                
                # Return response requiring parent action
                return {
                    "error": "Parent approval needed",
                    "action": "notify_parent",
                    "consent_required": True,
                    "details": {
                        "action": e.action,
                        "reason": e.reason
                    }
                }
                
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                
                # Apply content filter if provided
                if content_filter:
                    is_safe = content_filter(result)
                    if not is_safe:
                        raise InappropriateContentException(
                            content_type="response",
                            violation_reason="Content filter violation"
                        )
                        
                return result
                
            except InappropriateContentException as e:
                if log_violations:
                    logger.error(
                        "Child safety violation",
                        function=func.__name__,
                        violation_type=e.content_type,
                        reason=e.violation_reason
                    )
                    
                # Record metric
                MetricsCollector.record_content_filtered(
                    filter_type="function_decorator",
                    reason=e.violation_reason or "unknown"
                )
                
                # Return safe response
                return {
                    "error": "Content not appropriate for children",
                    "safe": True,
                    "filtered": True
                }
                
            except ParentalConsentRequiredException as e:
                if log_violations:
                    logger.warning(
                        "Parental consent required",
                        function=func.__name__,
                        action=e.action,
                        reason=e.reason
                    )
                    
                # Record metric
                MetricsCollector.record_parental_consent(
                    action=e.action,
                    status="required"
                )
                
                # Return response requiring parent action
                return {
                    "error": "Parent approval needed",
                    "action": "notify_parent",
                    "consent_required": True,
                    "details": {
                        "action": e.action,
                        "reason": e.reason
                    }
                }
                
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


def validate_input(
    validators: Dict[str, Callable[[Any], bool]],
    error_messages: Optional[Dict[str, str]] = None
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
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # Validate each parameter
            for param_name, validator in validators.items():
                if param_name in bound_args.arguments:
                    value = bound_args.arguments[param_name]
                    
                    try:
                        is_valid = await validator(value) if asyncio.iscoroutinefunction(validator) else validator(value)
                        if not is_valid:
                            error_msg = error_messages.get(param_name) if error_messages else f"Invalid {param_name}"
                            raise ValidationException(
                                message=error_msg,
                                field_name=param_name
                            )
                    except Exception as e:
                        if isinstance(e, ValidationException):
                            raise
                        raise ValidationException(
                            message=f"Validation failed for {param_name}: {str(e)}",
                            field_name=param_name
                        )
                        
            return await func(*args, **kwargs)
            
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Get function signature
            import inspect
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
                            error_msg = error_messages.get(param_name) if error_messages else f"Invalid {param_name}"
                            raise ValidationException(
                                message=error_msg,
                                field_name=param_name
                            )
                    except Exception as e:
                        if isinstance(e, ValidationException):
                            raise
                        raise ValidationException(
                            message=f"Validation failed for {param_name}: {str(e)}",
                            field_name=param_name
                        )
                        
            return func(*args, **kwargs)
            
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


def authenticated(
    required_role: Optional[str] = None,
    check_token_expiry: bool = True
):
    """
    Decorator للتحقق من المصادقة والصلاحيات
    
    Args:
        required_role: الدور المطلوب
        check_token_expiry: التحقق من انتهاء صلاحية التوكن
    """
    
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Get auth context from args (assuming first arg is self or request)
            auth_context = None
            if args and hasattr(args[0], 'auth_context'):
                auth_context = args[0].auth_context
            elif 'auth_context' in kwargs:
                auth_context = kwargs['auth_context']
                
            if not auth_context:
                raise AuthenticationException(
                    reason="No authentication context found"
                )
                
            # Check if authenticated
            if not auth_context.get('authenticated', False):
                raise AuthenticationException(
                    reason="User not authenticated"
                )
                
            # Check token expiry
            if check_token_expiry:
                token_expiry = auth_context.get('token_expiry')
                if token_expiry and datetime.fromisoformat(token_expiry) < datetime.utcnow():
                    raise AuthenticationException(
                        reason="Token expired",
                        auth_method="jwt"
                    )
                    
            # Check role if required
            if required_role:
                user_roles = auth_context.get('roles', [])
                if required_role not in user_roles:
                    from src.domain.exceptions.base import AuthorizationException
                    raise AuthorizationException(
                        action=func.__name__,
                        required_role=required_role
                    )
                    
            return await func(*args, **kwargs)
            
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Similar logic for sync version
            auth_context = None
            if args and hasattr(args[0], 'auth_context'):
                auth_context = args[0].auth_context
            elif 'auth_context' in kwargs:
                auth_context = kwargs['auth_context']
                
            if not auth_context:
                raise AuthenticationException(
                    reason="No authentication context found"
                )
                
            if not auth_context.get('authenticated', False):
                raise AuthenticationException(
                    reason="User not authenticated"
                )
                
            if check_token_expiry:
                token_expiry = auth_context.get('token_expiry')
                if token_expiry and datetime.fromisoformat(token_expiry) < datetime.utcnow():
                    raise AuthenticationException(
                        reason="Token expired",
                        auth_method="jwt"
                    )
                    
            if required_role:
                user_roles = auth_context.get('roles', [])
                if required_role not in user_roles:
                    from src.domain.exceptions.base import AuthorizationException
                    raise AuthorizationException(
                        action=func.__name__,
                        required_role=required_role
                    )
                    
            return func(*args, **kwargs)
            
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


# استخدام عملي - مثال من الكود المطلوب
class ChildInteractionService:
    """خدمة تفاعل الأطفال مع معالجة الأخطاء المتقدمة"""
    
    def __init__(self, content_filter, ai_service):
        self.content_filter = content_filter
        self.ai_service = ai_service
        
    @handle_exceptions(
        (InappropriateContentException, lambda e: {"error": "Content filtered", "safe": True}),
        (ParentalConsentRequiredException, lambda e: {"error": "Parent approval needed", "action": "notify_parent"}),
        (ValidationException, lambda e: {"error": f"Invalid input: {str(e)}", "retry": True})
    )
    @validate_input(
        validators={
            "message": lambda m: m and 0 < len(m) <= 1000,
            "child_id": lambda c: c and len(c) > 0
        },
        error_messages={
            "message": "Message must be between 1 and 1000 characters",
            "child_id": "Child ID is required"
        }
    )
    @child_safe(notify_parent=True)
    @with_retry(config=RetryConfig(max_attempts=3, exceptions_to_retry=[ExternalServiceException]))
    @with_circuit_breaker(service_name="ai_service", fallback=lambda: {"response": "عذراً، حاول مرة أخرى لاحقاً"})
    @track_request_duration(endpoint="/child/message")
    async def process_child_message(self, child_id: str, message: str) -> Dict[str, Any]:
        """معالجة رسالة الطفل مع جميع الحمايات"""
        
        # Check content safety
        safety_result = await self.content_filter.check(message)
        if not safety_result.is_safe:
            raise InappropriateContentException(
                content_type=safety_result.violation_type,
                violation_reason=safety_result.reason,
                context=ErrorContext(child_id=child_id)
            )
            
        # Process message with AI
        response = await self.ai_service.generate_response(message)
        
        return {
            "response": response,
            "safe": True,
            "child_id": child_id,
            "timestamp": datetime.utcnow().isoformat()
        }


# Export all decorators
__all__ = [
    'handle_exceptions',
    'with_retry',
    'with_circuit_breaker',
    'child_safe',
    'validate_input',
    'authenticated',
    'RetryConfig',
    'ChildInteractionService'
]
