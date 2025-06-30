"""
Base Exception Classes - نظام Exception Hierarchy الشامل
تنفيذ كامل لنظام الأخطاء مع severity levels و categories
"""
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum
import traceback
from datetime import datetime
import json


class ErrorSeverity(Enum):
    """مستويات الخطورة للأخطاء"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """تصنيفات الأخطاء"""
    VALIDATION = "validation"
    BUSINESS_LOGIC = "business_logic"
    INFRASTRUCTURE = "infrastructure"
    SECURITY = "security"
    CHILD_SAFETY = "child_safety"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    EXTERNAL_SERVICE = "external_service"
    DATA_INTEGRITY = "data_integrity"
    PERFORMANCE = "performance"


@dataclass
class ErrorContext:
    """Context معلومات للـ debugging والـ monitoring"""
    user_id: Optional[str] = None
    child_id: Optional[str] = None
    device_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    correlation_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    additional_data: Optional[Dict[str, Any]] = None
    stack_trace: Optional[str] = None
    environment: Optional[str] = None
    service_name: Optional[str] = None
    api_endpoint: Optional[str] = None
    
    def __post_init__(self):
        if self.stack_trace is None:
            self.stack_trace = traceback.format_exc()
            
    def to_dict(self) -> Dict[str, Any]:
        """تحويل context لـ dictionary"""
        return {
            "user_id": self.user_id,
            "child_id": self.child_id,
            "device_id": self.device_id,
            "session_id": self.session_id,
            "request_id": self.request_id,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp.isoformat(),
            "additional_data": self.additional_data,
            "environment": self.environment,
            "service_name": self.service_name,
            "api_endpoint": self.api_endpoint
        }


class AITeddyBearException(Exception):
    """Base exception لكل exceptions المشروع"""
    
    def __init__(
        self,
        message: str,
        error_code: str,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        category: ErrorCategory = ErrorCategory.BUSINESS_LOGIC,
        context: Optional[ErrorContext] = None,
        recoverable: bool = True,
        retry_after: Optional[int] = None,
        suggested_actions: Optional[List[str]] = None,
        internal_message: Optional[str] = None
    ):
        super().__init__(message)
        self.error_code = error_code
        self.severity = severity
        self.category = category
        self.context = context or ErrorContext()
        self.recoverable = recoverable
        self.retry_after = retry_after
        self.suggested_actions = suggested_actions or []
        self.internal_message = internal_message or message
        self.timestamp = datetime.utcnow()
        
    def to_dict(self) -> Dict[str, Any]:
        """تحويل الـ exception لـ dict للـ logging والـ API responses"""
        return {
            "error_code": self.error_code,
            "message": str(self),
            "internal_message": self.internal_message,
            "severity": self.severity.value,
            "category": self.category.value,
            "recoverable": self.recoverable,
            "retry_after": self.retry_after,
            "suggested_actions": self.suggested_actions,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context.to_dict() if self.context else None
        }
        
    def to_json(self) -> str:
        """تحويل لـ JSON string"""
        return json.dumps(self.to_dict(), default=str)
        
    def get_user_friendly_message(self) -> str:
        """رسالة صديقة للمستخدم"""
        if self.category == ErrorCategory.CHILD_SAFETY:
            return "عذراً، لا يمكن إتمام هذا الإجراء لحماية الطفل"
        elif self.category == ErrorCategory.SECURITY:
            return "عذراً، حدث خطأ في الأمان. يرجى المحاولة مرة أخرى"
        elif self.recoverable:
            return f"{str(self)}. يرجى المحاولة مرة أخرى"
        else:
            return "عذراً، حدث خطأ في النظام. يرجى التواصل مع الدعم الفني"


# Child Safety Exceptions
class ChildSafetyException(AITeddyBearException):
    """Base exception لكل مشاكل أمان الأطفال"""
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            error_code=kwargs.get("error_code", "CHILD_SAFETY_ERROR"),
            severity=ErrorSeverity.CRITICAL,
            category=ErrorCategory.CHILD_SAFETY,
            recoverable=False,
            **{k: v for k, v in kwargs.items() if k != "error_code"}
        )


class InappropriateContentException(ChildSafetyException):
    """محتوى غير مناسب للأطفال"""
    def __init__(
        self, 
        content_type: str, 
        content_snippet: Optional[str] = None,
        violation_reason: Optional[str] = None,
        **kwargs
    ):
        message = f"Inappropriate {content_type} content detected"
        if violation_reason:
            message += f": {violation_reason}"
            
        super().__init__(
            message=message,
            error_code="INAPPROPRIATE_CONTENT",
            suggested_actions=[
                "Review content filtering settings",
                "Report this incident to parent",
                "Block similar content"
            ],
            **kwargs
        )
        self.content_type = content_type
        self.content_snippet = content_snippet
        self.violation_reason = violation_reason


class ParentalConsentRequiredException(ChildSafetyException):
    """مطلوب موافقة الوالدين"""
    def __init__(
        self, 
        action: str,
        reason: Optional[str] = None,
        required_permission_level: Optional[str] = None,
        **kwargs
    ):
        message = f"Parental consent required for action: {action}"
        if reason:
            message += f" - Reason: {reason}"
            
        super().__init__(
            message=message,
            error_code="PARENTAL_CONSENT_REQUIRED",
            suggested_actions=[
                "Request parent approval",
                "Send notification to parent app",
                "Log request for later review"
            ],
            **kwargs
        )
        self.action = action
        self.reason = reason
        self.required_permission_level = required_permission_level


class AgeInappropriateException(ChildSafetyException):
    """محتوى غير مناسب لعمر الطفل"""
    def __init__(
        self,
        child_age: int,
        content_age_rating: int,
        content_description: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message=f"Content requires age {content_age_rating}+, child is {child_age}",
            error_code="AGE_INAPPROPRIATE_CONTENT",
            suggested_actions=[
                "Suggest age-appropriate alternative",
                "Notify parent of attempt"
            ],
            **kwargs
        )
        self.child_age = child_age
        self.content_age_rating = content_age_rating
        self.content_description = content_description


# Validation Exceptions
class ValidationException(AITeddyBearException):
    """Base validation exception"""
    def __init__(self, message: str, field_name: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            error_code=kwargs.get("error_code", "VALIDATION_ERROR"),
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.VALIDATION,
            recoverable=True,
            **{k: v for k, v in kwargs.items() if k != "error_code"}
        )
        self.field_name = field_name


class InvalidInputException(ValidationException):
    """إدخال غير صالح"""
    def __init__(
        self,
        field_name: str,
        invalid_value: Any,
        expected_type: Optional[str] = None,
        constraints: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        message = f"Invalid input for field '{field_name}'"
        if expected_type:
            message += f", expected {expected_type}"
            
        super().__init__(
            message=message,
            field_name=field_name,
            error_code="INVALID_INPUT",
            **kwargs
        )
        self.invalid_value = invalid_value
        self.expected_type = expected_type
        self.constraints = constraints


class MissingRequiredFieldException(ValidationException):
    """حقل مطلوب مفقود"""
    def __init__(self, field_name: str, **kwargs):
        super().__init__(
            message=f"Required field '{field_name}' is missing",
            field_name=field_name,
            error_code="MISSING_REQUIRED_FIELD",
            **kwargs
        )


# Security Exceptions
class SecurityException(AITeddyBearException):
    """Base security exception"""
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            error_code=kwargs.get("error_code", "SECURITY_ERROR"),
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.SECURITY,
            recoverable=False,
            **{k: v for k, v in kwargs.items() if k != "error_code"}
        )


class AuthenticationException(SecurityException):
    """فشل المصادقة"""
    def __init__(
        self,
        reason: str,
        auth_method: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message=f"Authentication failed: {reason}",
            error_code="AUTHENTICATION_FAILED",
            category=ErrorCategory.AUTHENTICATION,
            suggested_actions=["Re-authenticate", "Check credentials"],
            **kwargs
        )
        self.reason = reason
        self.auth_method = auth_method


class AuthorizationException(SecurityException):
    """عدم وجود صلاحية"""
    def __init__(
        self,
        action: str,
        resource: Optional[str] = None,
        required_role: Optional[str] = None,
        **kwargs
    ):
        message = f"Unauthorized action: {action}"
        if resource:
            message += f" on resource: {resource}"
            
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_FAILED",
            category=ErrorCategory.AUTHORIZATION,
            suggested_actions=["Request permission", "Contact administrator"],
            **kwargs
        )
        self.action = action
        self.resource = resource
        self.required_role = required_role


class TokenExpiredException(AuthenticationException):
    """انتهاء صلاحية التوكن"""
    def __init__(self, token_type: str = "access", **kwargs):
        super().__init__(
            reason=f"{token_type} token expired",
            error_code="TOKEN_EXPIRED",
            recoverable=True,
            suggested_actions=["Refresh token", "Re-login"],
            **kwargs
        )
        self.token_type = token_type


# Infrastructure Exceptions
class InfrastructureException(AITeddyBearException):
    """Base infrastructure exception"""
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            error_code=kwargs.get("error_code", "INFRASTRUCTURE_ERROR"),
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.INFRASTRUCTURE,
            recoverable=True,
            **{k: v for k, v in kwargs.items() if k != "error_code"}
        )


class DatabaseException(InfrastructureException):
    """خطأ في قاعدة البيانات"""
    def __init__(
        self,
        operation: str,
        table_name: Optional[str] = None,
        original_error: Optional[Exception] = None,
        **kwargs
    ):
        message = f"Database error during {operation}"
        if table_name:
            message += f" on table {table_name}"
            
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            suggested_actions=["Retry operation", "Check database connection"],
            **kwargs
        )
        self.operation = operation
        self.table_name = table_name
        self.original_error = original_error


class ExternalServiceException(InfrastructureException):
    """خطأ في خدمة خارجية"""
    def __init__(
        self,
        service_name: str,
        status_code: Optional[int] = None,
        response_body: Optional[str] = None,
        **kwargs
    ):
        message = f"External service '{service_name}' error"
        if status_code:
            message += f" - Status: {status_code}"
            
        super().__init__(
            message=message,
            error_code="EXTERNAL_SERVICE_ERROR",
            category=ErrorCategory.EXTERNAL_SERVICE,
            retry_after=kwargs.get("retry_after", 60),
            **kwargs
        )
        self.service_name = service_name
        self.status_code = status_code
        self.response_body = response_body


class CircuitBreakerOpenException(InfrastructureException):
    """Circuit breaker مفتوح"""
    def __init__(
        self,
        service_name: str,
        failure_count: int,
        last_failure_time: datetime,
        **kwargs
    ):
        super().__init__(
            message=f"Circuit breaker is OPEN for service '{service_name}'",
            error_code="CIRCUIT_BREAKER_OPEN",
            retry_after=kwargs.get("retry_after", 60),
            suggested_actions=["Wait before retry", "Use fallback service"],
            **kwargs
        )
        self.service_name = service_name
        self.failure_count = failure_count
        self.last_failure_time = last_failure_time


# Business Logic Exceptions
class BusinessLogicException(AITeddyBearException):
    """Base business logic exception"""
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            error_code=kwargs.get("error_code", "BUSINESS_LOGIC_ERROR"),
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUSINESS_LOGIC,
            **{k: v for k, v in kwargs.items() if k != "error_code"}
        )


class ResourceNotFoundException(BusinessLogicException):
    """المورد غير موجود"""
    def __init__(
        self,
        resource_type: str,
        resource_id: str,
        **kwargs
    ):
        super().__init__(
            message=f"{resource_type} with ID '{resource_id}' not found",
            error_code="RESOURCE_NOT_FOUND",
            **kwargs
        )
        self.resource_type = resource_type
        self.resource_id = resource_id


class DuplicateResourceException(BusinessLogicException):
    """مورد مكرر"""
    def __init__(
        self,
        resource_type: str,
        duplicate_field: str,
        duplicate_value: Any,
        **kwargs
    ):
        super().__init__(
            message=f"{resource_type} with {duplicate_field}='{duplicate_value}' already exists",
            error_code="DUPLICATE_RESOURCE",
            **kwargs
        )
        self.resource_type = resource_type
        self.duplicate_field = duplicate_field
        self.duplicate_value = duplicate_value


class QuotaExceededException(BusinessLogicException):
    """تجاوز الحصة المسموحة"""
    def __init__(
        self,
        quota_type: str,
        current_usage: int,
        quota_limit: int,
        reset_time: Optional[datetime] = None,
        **kwargs
    ):
        message = f"Quota exceeded for {quota_type}: {current_usage}/{quota_limit}"
        retry_after = None
        if reset_time:
            retry_after = int((reset_time - datetime.utcnow()).total_seconds())
            
        super().__init__(
            message=message,
            error_code="QUOTA_EXCEEDED",
            retry_after=retry_after,
            suggested_actions=["Wait for quota reset", "Upgrade plan"],
            **kwargs
        )
        self.quota_type = quota_type
        self.current_usage = current_usage
        self.quota_limit = quota_limit
        self.reset_time = reset_time


# Performance Exceptions
class PerformanceException(AITeddyBearException):
    """Base performance exception"""
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            error_code=kwargs.get("error_code", "PERFORMANCE_ERROR"),
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.PERFORMANCE,
            **{k: v for k, v in kwargs.items() if k != "error_code"}
        )


class TimeoutException(PerformanceException):
    """انتهاء الوقت المحدد"""
    def __init__(
        self,
        operation: str,
        timeout_seconds: float,
        **kwargs
    ):
        super().__init__(
            message=f"Operation '{operation}' timed out after {timeout_seconds}s",
            error_code="OPERATION_TIMEOUT",
            recoverable=True,
            suggested_actions=["Retry with longer timeout", "Check system load"],
            **kwargs
        )
        self.operation = operation
        self.timeout_seconds = timeout_seconds


class RateLimitException(PerformanceException):
    """تجاوز حد المعدل"""
    def __init__(
        self,
        limit_type: str,
        current_rate: float,
        max_rate: float,
        window_seconds: int = 60,
        **kwargs
    ):
        retry_after = kwargs.get("retry_after", window_seconds)
        super().__init__(
            message=f"Rate limit exceeded for {limit_type}: {current_rate}/{max_rate} per {window_seconds}s",
            error_code="RATE_LIMIT_EXCEEDED",
            retry_after=retry_after,
            suggested_actions=["Reduce request rate", "Implement backoff"],
            **kwargs
        )
        self.limit_type = limit_type
        self.current_rate = current_rate
        self.max_rate = max_rate
        self.window_seconds = window_seconds 