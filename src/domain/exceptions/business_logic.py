"""
Business Logic Exception Classes
استثناءات منطق الأعمال
"""

from datetime import datetime
from typing import Any, Optional

from .base import AITeddyBearException, ErrorCategory, ErrorSeverity


class BusinessLogicException(AITeddyBearException):
    """Base business logic exception"""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            error_code=kwargs.get("error_code", "BUSINESS_LOGIC_ERROR"),
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUSINESS_LOGIC,
            **{k: v for k, v in kwargs.items() if k != "error_code"},
        )


class ResourceNotFoundException(BusinessLogicException):
    """المورد غير موجود"""

    def __init__(self, resource_type: str, resource_id: str, **kwargs):
        super().__init__(
            message=f"{resource_type} with ID '{resource_id}' not found", error_code="RESOURCE_NOT_FOUND", **kwargs
        )
        self.resource_type = resource_type
        self.resource_id = resource_id


class DuplicateResourceException(BusinessLogicException):
    """مورد مكرر"""

    def __init__(self, resource_type: str, duplicate_field: str, duplicate_value: Any, **kwargs):
        super().__init__(
            message=f"{resource_type} with {duplicate_field}='{duplicate_value}' already exists",
            error_code="DUPLICATE_RESOURCE",
            **kwargs,
        )
        self.resource_type = resource_type
        self.duplicate_field = duplicate_field
        self.duplicate_value = duplicate_value


class QuotaExceededException(BusinessLogicException):
    """تجاوز الحصة المسموحة"""

    def __init__(
        self, quota_type: str, current_usage: int, quota_limit: int, reset_time: Optional[datetime] = None, **kwargs
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
            **kwargs,
        )
        self.quota_type = quota_type
        self.current_usage = current_usage
        self.quota_limit = quota_limit
        self.reset_time = reset_time
