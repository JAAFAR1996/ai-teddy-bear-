"""
Enterprise-Grade Global Exception Handling System
Comprehensive exception hierarchy with recovery strategies
"""

import sys
import asyncio
import logging
import traceback
import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional, List, Type, Callable, Union
from dataclasses import dataclass, field
from enum import Enum, auto
from abc import ABC, abstractmethod
import uuid
from functools import wraps
import contextvars

# Structured logging setup
import structlog
from pythonjsonlogger import jsonlogger

# For alerts
import aiohttp
from prometheus_client import Counter, Histogram, Gauge

# Setup structured logger
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Context variables for correlation
correlation_id_var = contextvars.ContextVar('correlation_id', default=None)
user_id_var = contextvars.ContextVar('user_id', default=None)
child_id_var = contextvars.ContextVar('child_id', default=None)

# Metrics
exception_counter = Counter(
    'app_exceptions_total',
    'Total number of exceptions',
    ['exception_type', 'severity', 'domain']
)

exception_histogram = Histogram(
    'app_exception_handling_duration_seconds',
    'Exception handling duration',
    ['exception_type']
)

active_circuit_breakers = Gauge(
    'app_circuit_breakers_active',
    'Number of active circuit breakers',
    ['service']
)


class ExceptionSeverity(Enum):
    """Exception severity levels"""
    LOW = auto()        # Log and continue
    MEDIUM = auto()     # Log, alert team, continue with degradation
    HIGH = auto()       # Log, alert team, implement recovery
    CRITICAL = auto()   # Log, alert everyone, emergency response


class ExceptionDomain(Enum):
    """Exception domains for categorization"""
    AUTHENTICATION = auto()
    AUTHORIZATION = auto()
    CHILD_SAFETY = auto()
    DATA_PROCESSING = auto()
    EXTERNAL_SERVICE = auto()
    DATABASE = auto()
    VALIDATION = auto()
    BUSINESS_LOGIC = auto()
    INFRASTRUCTURE = auto()
    SECURITY = auto()
    PERFORMANCE = auto()


@dataclass
class ExceptionContext:
    """Context information for exceptions"""
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    child_id: Optional[str] = None
    request_id: Optional[str] = None
    service_name: str = "ai-teddy-bear"
    environment: str = "production"
    additional_data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging"""
        return {
            "correlation_id": self.correlation_id,
            "user_id": self.user_id,
            "child_id": self.child_id,
            "request_id": self.request_id,
            "service_name": self.service_name,
            "environment": self.environment,
            "timestamp": self.timestamp.isoformat(),
            "additional_data": self.additional_data
        }


# Base Exception Classes
class TeddyBearException(Exception):
    """Base exception for all Teddy Bear application exceptions"""
    
    severity: ExceptionSeverity = ExceptionSeverity.MEDIUM
    domain: ExceptionDomain = ExceptionDomain.BUSINESS_LOGIC
    error_code: str = "TB_GENERIC_ERROR"
    should_alert: bool = True
    is_retryable: bool = False
    max_retries: int = 3
    
    def __init__(
        self,
        message: str,
        context: Optional[ExceptionContext] = None,
        cause: Optional[Exception] = None,
        **kwargs
    ):
        super().__init__(message)
        self.message = message
        self.context = context or ExceptionContext()
        self.cause = cause
        self.details = kwargs
        self.timestamp = datetime.now(timezone.utc)
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging/serialization"""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "severity": self.severity.name,
            "domain": self.domain.name,
            "context": self.context.to_dict(),
            "details": self.details,
            "is_retryable": self.is_retryable,
            "timestamp": self.timestamp.isoformat(),
            "cause": str(self.cause) if self.cause else None
        }
    
    def sanitize_for_child_logs(self) -> Dict[str, Any]:
        """Sanitize exception data for child-safe logging"""
        sanitized = self.to_dict()
        # Remove sensitive data
        sanitized.pop('details', None)
        sanitized['context'].pop('additional_data', None)
        # Simplify message
        sanitized['message'] = "An error occurred. Please try again."
        return sanitized


# Domain-Specific Exception Hierarchy

# Child Safety Exceptions
class ChildSafetyException(TeddyBearException):
    """Base for all child safety related exceptions"""
    domain = ExceptionDomain.CHILD_SAFETY
    severity = ExceptionSeverity.HIGH
    error_code = "TB_CHILD_SAFETY"


class InappropriateContentException(ChildSafetyException):
    """Raised when inappropriate content is detected"""
    error_code = "TB_INAPPROPRIATE_CONTENT"
    severity = ExceptionSeverity.CRITICAL
    
    def __init__(self, content_type: str, content_snippet: str, **kwargs):
        super().__init__(
            f"Inappropriate {content_type} detected",
            content_type=content_type,
            **kwargs
        )


class AgeInappropriateException(ChildSafetyException):
    """Raised when content is not age-appropriate"""
    error_code = "TB_AGE_INAPPROPRIATE"
    
    def __init__(self, child_age: int, content_age_rating: int, **kwargs):
        super().__init__(
            f"Content requires age {content_age_rating}, child is {child_age}",
            child_age=child_age,
            content_age_rating=content_age_rating,
            **kwargs
        )


class ChildDataProtectionException(ChildSafetyException):
    """Raised for child data protection violations"""
    error_code = "TB_CHILD_DATA_PROTECTION"
    severity = ExceptionSeverity.CRITICAL


# Security Exceptions
class SecurityException(TeddyBearException):
    """Base for security related exceptions"""
    domain = ExceptionDomain.SECURITY
    severity = ExceptionSeverity.HIGH
    error_code = "TB_SECURITY"


class AuthenticationException(SecurityException):
    """Authentication failures"""
    domain = ExceptionDomain.AUTHENTICATION
    error_code = "TB_AUTH_FAILED"
    is_retryable = False


class AuthorizationException(SecurityException):
    """Authorization failures"""
    domain = ExceptionDomain.AUTHORIZATION
    error_code = "TB_AUTHZ_FAILED"
    is_retryable = False


class TokenExpiredException(AuthenticationException):
    """Token has expired"""
    error_code = "TB_TOKEN_EXPIRED"
    is_retryable = True  # Can retry with refresh


class SuspiciousActivityException(SecurityException):
    """Suspicious activity detected"""
    error_code = "TB_SUSPICIOUS_ACTIVITY"
    severity = ExceptionSeverity.CRITICAL


# External Service Exceptions
class ExternalServiceException(TeddyBearException):
    """Base for external service failures"""
    domain = ExceptionDomain.EXTERNAL_SERVICE
    error_code = "TB_EXTERNAL_SERVICE"
    is_retryable = True
    
    def __init__(self, service_name: str, **kwargs):
        super().__init__(
            f"External service error: {service_name}",
            service_name=service_name,
            **kwargs
        )


class AIServiceException(ExternalServiceException):
    """AI service specific exceptions"""
    error_code = "TB_AI_SERVICE"
    
    def __init__(self, ai_provider: str, **kwargs):
        super().__init__(
            service_name=f"AI-{ai_provider}",
            ai_provider=ai_provider,
            **kwargs
        )


class RateLimitException(ExternalServiceException):
    """Rate limit exceeded"""
    error_code = "TB_RATE_LIMIT"
    severity = ExceptionSeverity.MEDIUM
    
    def __init__(self, service_name: str, reset_time: Optional[datetime] = None, **kwargs):
        super().__init__(
            service_name=service_name,
            reset_time=reset_time,
            **kwargs
        )


# Data Exceptions
class DataException(TeddyBearException):
    """Base for data related exceptions"""
    domain = ExceptionDomain.DATA_PROCESSING
    error_code = "TB_DATA_ERROR"


class ValidationException(DataException):
    """Data validation failures"""
    domain = ExceptionDomain.VALIDATION
    error_code = "TB_VALIDATION_ERROR"
    severity = ExceptionSeverity.LOW
    is_retryable = False
    
    def __init__(self, field: str, value: Any, reason: str, **kwargs):
        super().__init__(
            f"Validation failed for {field}: {reason}",
            field=field,
            value=str(value)[:100],  # Truncate for safety
            reason=reason,
            **kwargs
        )


class DatabaseException(DataException):
    """Database operation failures"""
    domain = ExceptionDomain.DATABASE
    error_code = "TB_DATABASE_ERROR"
    is_retryable = True


# Performance Exceptions
class PerformanceException(TeddyBearException):
    """Performance related exceptions"""
    domain = ExceptionDomain.PERFORMANCE
    error_code = "TB_PERFORMANCE"
    severity = ExceptionSeverity.MEDIUM


class TimeoutException(PerformanceException):
    """Operation timeout"""
    error_code = "TB_TIMEOUT"
    
    def __init__(self, operation: str, timeout_seconds: float, **kwargs):
        super().__init__(
            f"Operation {operation} timed out after {timeout_seconds}s",
            operation=operation,
            timeout_seconds=timeout_seconds,
            **kwargs
        )


# Recovery Strategies
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
                delay = self.base_delay * (2 ** attempt)
                await asyncio.sleep(delay)
                # Retry operation here
                return None
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                continue


class CircuitBreakerStrategy(RecoveryStrategy):
    """Circuit breaker pattern"""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        half_open_max_calls: int = 3
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
            if (datetime.now(timezone.utc) - self.last_failure_time).total_seconds() > self.recovery_timeout:
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
            active_circuit_breakers.labels(
                service=exception.details.get('service_name', 'unknown')
            ).inc()
        
        raise exception


class FallbackStrategy(RecoveryStrategy):
    """Fallback to alternative implementation"""
    
    def __init__(self, fallback_func: Callable):
        self.fallback_func = fallback_func
        
    async def recover(self, exception: TeddyBearException) -> Any:
        """Execute fallback function"""
        logger.warning(
            "Executing fallback strategy",
            exception=exception.to_dict()
        )
        return await self.fallback_func()


# Global Exception Handler
class GlobalExceptionHandler:
    """Central exception handling system"""
    
    def __init__(self):
        self.recovery_strategies: Dict[Type[Exception], RecoveryStrategy] = {}
        self.alert_manager = AlertManager()
        self._setup_default_strategies()
        
    def _setup_default_strategies(self):
        """Setup default recovery strategies"""
        self.recovery_strategies[ExternalServiceException] = RetryStrategy()
        self.recovery_strategies[DatabaseException] = RetryStrategy(max_retries=5)
        self.recovery_strategies[TimeoutException] = CircuitBreakerStrategy()
        
    def register_strategy(
        self,
        exception_type: Type[Exception],
        strategy: RecoveryStrategy
    ):
        """Register a recovery strategy for an exception type"""
        self.recovery_strategies[exception_type] = strategy
        
    async def handle_exception(self, exception: Exception) -> Optional[Any]:
        """Handle an exception with appropriate strategies"""
        with exception_histogram.labels(
            exception_type=type(exception).__name__
        ).time():
            # Convert to TeddyBearException if needed
            if not isinstance(exception, TeddyBearException):
                exception = self._wrap_exception(exception)
            
            # Log the exception
            await self._log_exception(exception)
            
            # Update metrics
            exception_counter.labels(
                exception_type=type(exception).__name__,
                severity=exception.severity.name,
                domain=exception.domain.name
            ).inc()
            
            # Send alerts if needed
            if exception.should_alert:
                await self.alert_manager.send_alert(exception)
            
            # Attempt recovery
            strategy = self.recovery_strategies.get(type(exception))
            if strategy:
                try:
                    return await strategy.recover(exception)
                except Exception as recovery_error:
                    logger.error(
                        "Recovery strategy failed",
                        original_exception=exception.to_dict(),
                        recovery_error=str(recovery_error)
                    )
            
            # Re-raise if no recovery possible
            raise exception
    
    def _wrap_exception(self, exception: Exception) -> TeddyBearException:
        """Wrap standard exceptions in TeddyBearException"""
        context = ExceptionContext(
            correlation_id=correlation_id_var.get() or str(uuid.uuid4()),
            user_id=user_id_var.get(),
            child_id=child_id_var.get()
        )
        
        # Map common exceptions
        if isinstance(exception, ValueError):
            return ValidationException(
                field="unknown",
                value="unknown",
                reason=str(exception),
                context=context,
                cause=exception
            )
        elif isinstance(exception, TimeoutError):
            return TimeoutException(
                operation="unknown",
                timeout_seconds=0,
                context=context,
                cause=exception
            )
        else:
            return TeddyBearException(
                message=str(exception),
                context=context,
                cause=exception
            )
    
    async def _log_exception(self, exception: TeddyBearException):
        """Log exception with appropriate detail level"""
        log_data = exception.to_dict()
        
        # Sanitize for child safety if needed
        if exception.context.child_id:
            log_data = exception.sanitize_for_child_logs()
        
        # Log based on severity
        if exception.severity == ExceptionSeverity.CRITICAL:
            logger.critical("Critical exception occurred", **log_data)
        elif exception.severity == ExceptionSeverity.HIGH:
            logger.error("High severity exception", **log_data)
        elif exception.severity == ExceptionSeverity.MEDIUM:
            logger.warning("Medium severity exception", **log_data)
        else:
            logger.info("Low severity exception", **log_data)


class AlertManager:
    """Manages alerts for exceptions"""
    
    def __init__(self):
        self.webhook_url = None  # Configure with actual webhook
        self.email_service = None  # Configure with email service
        
    async def send_alert(self, exception: TeddyBearException):
        """Send appropriate alerts based on exception severity"""
        if exception.severity == ExceptionSeverity.CRITICAL:
            # Send to all channels
            await self._send_webhook_alert(exception)
            await self._send_email_alert(exception)
            await self._send_pager_alert(exception)
        elif exception.severity == ExceptionSeverity.HIGH:
            # Send to webhook and email
            await self._send_webhook_alert(exception)
            await self._send_email_alert(exception)
        else:
            # Just webhook
            await self._send_webhook_alert(exception)
    
    async def _send_webhook_alert(self, exception: TeddyBearException):
        """Send alert to webhook (Slack, Discord, etc.)"""
        if not self.webhook_url:
            return
        
        payload = {
            "text": f"🚨 Exception Alert: {exception.error_code}",
            "attachments": [{
                "color": self._get_severity_color(exception.severity),
                "fields": [
                    {"title": "Error Code", "value": exception.error_code, "short": True},
                    {"title": "Severity", "value": exception.severity.name, "short": True},
                    {"title": "Domain", "value": exception.domain.name, "short": True},
                    {"title": "Message", "value": exception.message, "short": False},
                    {"title": "Correlation ID", "value": exception.context.correlation_id, "short": True},
                    {"title": "Environment", "value": exception.context.environment, "short": True},
                ]
            }]
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                await session.post(self.webhook_url, json=payload)
        except Exception as e:
            logger.error("Failed to send webhook alert", error=str(e))
    
    async def _send_email_alert(self, exception: TeddyBearException):
        """Send email alert"""
        # Implementation depends on email service
        pass
    
    async def _send_pager_alert(self, exception: TeddyBearException):
        """Send pager alert for critical issues"""
        # Implementation depends on pager service (PagerDuty, etc.)
        pass
    
    def _get_severity_color(self, severity: ExceptionSeverity) -> str:
        """Get color for severity level"""
        return {
            ExceptionSeverity.CRITICAL: "#FF0000",  # Red
            ExceptionSeverity.HIGH: "#FF8C00",      # Dark Orange
            ExceptionSeverity.MEDIUM: "#FFD700",    # Gold
            ExceptionSeverity.LOW: "#90EE90"        # Light Green
        }.get(severity, "#808080")  # Gray default


# Decorators for exception handling
def handle_exceptions(
    recovery_strategy: Optional[RecoveryStrategy] = None,
    fallback_value: Any = None
):
    """Decorator for automatic exception handling"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            handler = GlobalExceptionHandler()
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if recovery_strategy:
                    handler.register_strategy(type(e), recovery_strategy)
                
                try:
                    return await handler.handle_exception(e)
                except Exception:
                    if fallback_value is not None:
                        return fallback_value
                    raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            handler = GlobalExceptionHandler()
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Sync version would need different handling
                raise
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Context managers for correlation
class CorrelationContext:
    """Context manager for correlation ID"""
    
    def __init__(self, correlation_id: Optional[str] = None):
        self.correlation_id = correlation_id or str(uuid.uuid4())
        self.token = None
        
    def __enter__(self):
        self.token = correlation_id_var.set(self.correlation_id)
        return self.correlation_id
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        correlation_id_var.reset(self.token)


# Initialize global handler
global_exception_handler = GlobalExceptionHandler()


# Helper functions
def set_child_context(child_id: str):
    """Set child context for exception handling"""
    child_id_var.set(child_id)


def set_user_context(user_id: str):
    """Set user context for exception handling"""
    user_id_var.set(user_id)


def get_current_correlation_id() -> Optional[str]:
    """Get current correlation ID"""
    return correlation_id_var.get() 