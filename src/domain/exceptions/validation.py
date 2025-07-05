"""
Validation Exception Classes
استثناءات التحقق من صحة البيانات
"""

from typing import Any, Dict, Optional

from .base import AITeddyBearException, ErrorCategory, ErrorSeverity


class ValidationException(AITeddyBearException):
    """Base validation exception"""

    def __init__(
            self,
            message: str,
            field_name: Optional[str] = None,
            **kwargs):
        super().__init__(
            message=message,
            error_code=kwargs.get("error_code", "VALIDATION_ERROR"),
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.VALIDATION,
            recoverable=True,
            **{k: v for k, v in kwargs.items() if k != "error_code"},
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
        **kwargs,
    ):
        message = f"Invalid input for field '{field_name}'"
        if expected_type:
            message += f", expected {expected_type}"

        super().__init__(
            message=message,
            field_name=field_name,
            error_code="INVALID_INPUT",
            **kwargs)
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
            **kwargs,
        )
