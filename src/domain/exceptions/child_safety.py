"""
Child Safety Exception Classes
استثناءات خاصة بأمان الأطفال
"""
from typing import Optional
from .base import AITeddyBearException, ErrorSeverity, ErrorCategory


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
