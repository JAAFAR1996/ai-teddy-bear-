"""
Enterprise-Grade Exception Handling System
Comprehensive error handling with structured logging, correlation IDs, and monitoring
"""

import asyncio
import logging
import traceback
import uuid
from contextvars import ContextVar
from datetime import datetime, timezone
from functools import wraps
from typing import Any, Callable, Dict, Optional, Type, Union

import structlog
from pydantic import BaseModel, Field

from domain.exceptions import (
    AITeddyBearException,
    ErrorCategory,
    ErrorContext,
    ErrorSeverity,
    SecurityException,
)

# Context variables for request tracking
correlation_id: ContextVar[str] = ContextVar("correlation_id", default="")
user_id: ContextVar[str] = ContextVar("user_id", default="")
session_id: ContextVar[str] = ContextVar("session_id", default="")
request_id: ContextVar[str] = ContextVar("request_id", default="")


class ErrorDetails(BaseModel):
    """Structured error details for logging and monitoring"""
    
    error_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    correlation_id: str = Field(default="")
    user_id: str = Field(default="")
    session_id: str = Field(default="")
    request_id: str = Field(default="")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    error_type: str = Field(description="Exception class name")
    error_message: str = Field(description="Human-readable error message")
    error_code: Optional[str] = Field(default=None, description="Business error code")
    severity: ErrorSeverity = Field(default=ErrorSeverity.ERROR)
    category: ErrorCategory = Field(default=ErrorCategory.UNKNOWN)
    context: ErrorContext = Field(default=ErrorContext.APPLICATION)
    stack_trace: Optional[str] = Field(default=None, description="Formatted stack trace")
    additional_data: Dict[str, Any] = Field(default_factory=dict)
    environment: str = Field(default="production")
    service_name: str = Field(default="ai-teddy-bear")
    version: str = Field(default="2.0.0")


class ExceptionHandlerConfig(BaseModel):
    """Configuration for exception handling"""
    
    enable_structured_logging: bool = Field(default=True, description="Use structured logging")
    enable_correlation_ids: bool = Field(default=True, description="Generate correlation IDs")
    enable_error_tracking: bool = Field(default=True, description="Send errors to monitoring")
    enable_circuit_breaker: bool = Field(default=True, description="Enable circuit breaker pattern")
    max_retry_attempts: int = Field(default=3, description="Maximum retry attempts")
    retry_delay_seconds: float = Field(default=1.0, description="Base retry delay")
    exponential_backoff: bool = Field(default=True, description="Use exponential backoff")
    log_sensitive_data: bool = Field(default=False, description="Log sensitive information")
    error_threshold_per_minute: int = Field(default=100, description="Error rate threshold")
    circuit_breaker_timeout_seconds: int = Field(default=60, description="Circuit breaker timeout")
    
    class Config:
        validate_assignment = True


class CircuitBreaker:
    """Circuit breaker pattern implementation"""
    
    def __init__(self, name: str, config: ExceptionHandlerConfig):
        self.name = name
        self.config = config
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.logger = logging.getLogger(f"circuit_breaker.{name}")
    
    def can_execute(self) -> bool:
        """Check if operation can be executed"""
        if self.state == "CLOSED":
            return True
        elif self.state == "OPEN":
            if self.last_failure_time:
                timeout_delta = datetime.now(timezone.utc) - self.last_failure_time
                if timeout_delta.total_seconds() >= self.config.circuit_breaker_timeout_seconds:
                    self.state = "HALF_OPEN"
                    return True
            return False
        else:  # HALF_OPEN
            return True
    
    def on_success(self):
        """Handle successful execution"""
        self.failure_count = 0
        self.state = "CLOSED"
        self.logger.info(f"✅ Circuit breaker {self.name} reset to CLOSED")
    
    def on_failure(self, error: Exception):
        """Handle failed execution"""
        self.failure_count += 1
        self.last_failure_time = datetime.now(timezone.utc)
        
        if self.failure_count >= self.config.error_threshold_per_minute:
            self.state = "OPEN"
            self.logger.warning(f"🚨 Circuit breaker {self.name} opened due to {self.failure_count} failures")
        
        if self.state == "HALF_OPEN":
            self.state = "OPEN"


class EnterpriseExceptionHandler:
    """Enterprise-grade exception handling with comprehensive features"""
    
    def __init__(self, config: Optional[ExceptionHandlerConfig] = None):
        self.config = config or ExceptionHandlerConfig()
        self.logger = self._setup_logger()
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.error_counters: Dict[str, int] = {}
        self.last_error_reset = datetime.now(timezone.utc)
    
    def _setup_logger(self) -> structlog.BoundLogger:
        """Setup structured logger"""
        if self.config.enable_structured_logging:
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
                wrapper_class=structlog.stdlib.BoundLogger,
                cache_logger_on_first_use=True,
            )
            return structlog.get_logger("exception_handler")
        else:
            return logging.getLogger("exception_handler")
    
    def _generate_correlation_id(self) -> str:
        """Generate unique correlation ID"""
        if not self.config.enable_correlation_ids:
            return ""
        
        corr_id = f"corr-{uuid.uuid4().hex[:16]}"
        correlation_id.set(corr_id)
        return corr_id
    
    def _get_context_data(self) -> Dict[str, str]:
        """Get current context data"""
        return {
            "correlation_id": correlation_id.get(),
            "user_id": user_id.get(),
            "session_id": session_id.get(),
            "request_id": request_id.get(),
        }
    
    def _create_error_details(
        self,
        error: Exception,
        error_code: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None,
    ) -> ErrorDetails:
        """Create structured error details"""
        context_data = self._get_context_data()
        
        # Determine error category and severity
        if isinstance(error, SecurityException):
            category = ErrorCategory.SECURITY
            severity = ErrorSeverity.CRITICAL
        elif isinstance(error, AITeddyBearException):
            category = error.category
            severity = error.severity
        else:
            category = ErrorCategory.UNKNOWN
            severity = ErrorSeverity.ERROR
        
        return ErrorDetails(
            correlation_id=context_data["correlation_id"],
            user_id=context_data["user_id"],
            session_id=context_data["session_id"],
            request_id=context_data["request_id"],
            error_type=error.__class__.__name__,
            error_message=str(error),
            error_code=error_code,
            severity=severity,
            category=category,
            context=ErrorContext.APPLICATION,
            stack_trace=traceback.format_exc() if self.config.log_sensitive_data else None,
            additional_data=additional_data or {},
        )
    
    def _log_error(self, error_details: ErrorDetails):
        """Log error with structured format"""
        log_data = error_details.dict()
        
        if error_details.severity == ErrorSeverity.CRITICAL:
            self.logger.critical("🚨 CRITICAL ERROR", **log_data)
        elif error_details.severity == ErrorSeverity.ERROR:
            self.logger.error("❌ ERROR", **log_data)
        elif error_details.severity == ErrorSeverity.WARNING:
            self.logger.warning("⚠️ WARNING", **log_data)
        else:
            self.logger.info("ℹ️ INFO", **log_data)
    
    def _update_error_counters(self, error_details: ErrorDetails):
        """Update error rate counters"""
        current_time = datetime.now(timezone.utc)
        
        # Reset counters every minute
        if (current_time - self.last_error_reset).total_seconds() >= 60:
            self.error_counters.clear()
            self.last_error_reset = current_time
        
        error_type = error_details.error_type
        self.error_counters[error_type] = self.error_counters.get(error_type, 0) + 1
    
    def _should_trigger_circuit_breaker(self, error_details: ErrorDetails) -> bool:
        """Check if circuit breaker should be triggered"""
        error_type = error_details.error_type
        error_count = self.error_counters.get(error_type, 0)
        return error_count >= self.config.error_threshold_per_minute
    
    def handle_exception(
        self,
        error: Exception,
        error_code: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None,
        reraise: bool = True,
    ) -> ErrorDetails:
        """Handle exception with comprehensive logging and monitoring"""
        try:
            # Create error details
            error_details = self._create_error_details(error, error_code, additional_data)
            
            # Log error
            self._log_error(error_details)
            
            # Update counters
            self._update_error_counters(error_details)
            
            # Check circuit breaker
            if self._should_trigger_circuit_breaker(error_details):
                self.logger.warning(f"🚨 High error rate detected for {error_details.error_type}")
            
            # Send to monitoring (placeholder for Sentry/Rollbar integration)
            if self.config.enable_error_tracking:
                self._send_to_monitoring(error_details)
            
            return error_details
            
        except Exception as logging_error:
            # Fallback logging if error handling fails
            self.logger.error(f"❌ Error in exception handler: {logging_error}")
            
        finally:
            if reraise:
                raise
    
    def _send_to_monitoring(self, error_details: ErrorDetails):
        """Send error to monitoring service (placeholder)"""
        # TODO: Integrate with Sentry, Rollbar, or other monitoring services
        pass
    
    def get_circuit_breaker(self, name: str) -> CircuitBreaker:
        """Get or create circuit breaker"""
        if name not in self.circuit_breakers:
            self.circuit_breakers[name] = CircuitBreaker(name, self.config)
        return self.circuit_breakers[name]
    
    def with_correlation_id(self, corr_id: Optional[str] = None):
        """Context manager for correlation ID"""
        if not corr_id:
            corr_id = self._generate_correlation_id()
        
        token = correlation_id.set(corr_id)
        return token
    
    def with_user_context(self, user_id: str, session_id: Optional[str] = None):
        """Context manager for user context"""
        user_token = user_id.set(user_id)
        session_token = None
        if session_id:
            session_token = session_id.set(session_id)
        return user_token, session_token


# Global exception handler instance
exception_handler = EnterpriseExceptionHandler()


def handle_exceptions(
    error_code: Optional[str] = None,
    additional_data: Optional[Dict[str, Any]] = None,
    reraise: bool = True,
    circuit_breaker_name: Optional[str] = None,
):
    """Decorator for automatic exception handling"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Setup correlation ID if not present
            if not correlation_id.get():
                exception_handler._generate_correlation_id()
            
            # Check circuit breaker
            if circuit_breaker_name and exception_handler.config.enable_circuit_breaker:
                cb = exception_handler.get_circuit_breaker(circuit_breaker_name)
                if not cb.can_execute():
                    raise AITeddyBearException(
                        message="Service temporarily unavailable",
                        category=ErrorCategory.INFRASTRUCTURE,
                        severity=ErrorSeverity.WARNING,
                    )
            
            try:
                result = await func(*args, **kwargs)
                
                # Record success in circuit breaker
                if circuit_breaker_name and exception_handler.config.enable_circuit_breaker:
                    cb = exception_handler.get_circuit_breaker(circuit_breaker_name)
                    cb.on_success()
                
                return result
                
            except Exception as e:
                # Record failure in circuit breaker
                if circuit_breaker_name and exception_handler.config.enable_circuit_breaker:
                    cb = exception_handler.get_circuit_breaker(circuit_breaker_name)
                    cb.on_failure(e)
                
                # Handle exception
                exception_handler.handle_exception(
                    e, error_code, additional_data, reraise
                )
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Setup correlation ID if not present
            if not correlation_id.get():
                exception_handler._generate_correlation_id()
            
            # Check circuit breaker
            if circuit_breaker_name and exception_handler.config.enable_circuit_breaker:
                cb = exception_handler.get_circuit_breaker(circuit_breaker_name)
                if not cb.can_execute():
                    raise AITeddyBearException(
                        message="Service temporarily unavailable",
                        category=ErrorCategory.INFRASTRUCTURE,
                        severity=ErrorSeverity.WARNING,
                    )
            
            try:
                result = func(*args, **kwargs)
                
                # Record success in circuit breaker
                if circuit_breaker_name and exception_handler.config.enable_circuit_breaker:
                    cb = exception_handler.get_circuit_breaker(circuit_breaker_name)
                    cb.on_success()
                
                return result
                
            except Exception as e:
                # Record failure in circuit breaker
                if circuit_breaker_name and exception_handler.config.enable_circuit_breaker:
                    cb = exception_handler.get_circuit_breaker(circuit_breaker_name)
                    cb.on_failure(e)
                
                # Handle exception
                exception_handler.handle_exception(
                    e, error_code, additional_data, reraise
                )
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def with_retry(
    max_attempts: Optional[int] = None,
    delay_seconds: Optional[float] = None,
    exponential_backoff: Optional[bool] = None,
    retry_on: Optional[Type[Exception]] = None,
):
    """Decorator for retry logic with exponential backoff"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            config = exception_handler.config
            max_attempts_actual = max_attempts or config.max_retry_attempts
            delay_actual = delay_seconds or config.retry_delay_seconds
            backoff_actual = exponential_backoff if exponential_backoff is not None else config.exponential_backoff
            retry_exception = retry_on or Exception
            
            last_exception = None
            
            for attempt in range(max_attempts_actual):
                try:
                    return await func(*args, **kwargs)
                except retry_exception as e:
                    last_exception = e
                    
                    if attempt < max_attempts_actual - 1:
                        # Calculate delay
                        if backoff_actual:
                            current_delay = delay_actual * (2 ** attempt)
                        else:
                            current_delay = delay_actual
                        
                        exception_handler.logger.warning(
                            f"🔄 Retry attempt {attempt + 1}/{max_attempts_actual} after {current_delay}s",
                            error=str(e),
                            attempt=attempt + 1,
                            max_attempts=max_attempts_actual,
                        )
                        
                        await asyncio.sleep(current_delay)
                    else:
                        exception_handler.logger.error(
                            f"❌ All retry attempts failed",
                            error=str(e),
                            max_attempts=max_attempts_actual,
                        )
            
            # Re-raise the last exception
            raise last_exception
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            config = exception_handler.config
            max_attempts_actual = max_attempts or config.max_retry_attempts
            delay_actual = delay_seconds or config.retry_delay_seconds
            backoff_actual = exponential_backoff if exponential_backoff is not None else config.exponential_backoff
            retry_exception = retry_on or Exception
            
            last_exception = None
            
            for attempt in range(max_attempts_actual):
                try:
                    return func(*args, **kwargs)
                except retry_exception as e:
                    last_exception = e
                    
                    if attempt < max_attempts_actual - 1:
                        # Calculate delay
                        if backoff_actual:
                            current_delay = delay_actual * (2 ** attempt)
                        else:
                            current_delay = delay_actual
                        
                        exception_handler.logger.warning(
                            f"🔄 Retry attempt {attempt + 1}/{max_attempts_actual} after {current_delay}s",
                            error=str(e),
                            attempt=attempt + 1,
                            max_attempts=max_attempts_actual,
                        )
                        
                        import time
                        time.sleep(current_delay)
                    else:
                        exception_handler.logger.error(
                            f"❌ All retry attempts failed",
                            error=str(e),
                            max_attempts=max_attempts_actual,
                        )
            
            # Re-raise the last exception
            raise last_exception
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator 