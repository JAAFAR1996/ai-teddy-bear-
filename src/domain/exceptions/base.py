"""
Base Exception Classes - الأساسيات فقط
تعريف الأنواع والكلاسات الأساسية لنظام الأخطاء
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