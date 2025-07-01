"""
Security Exception Classes
استثناءات الأمان والمصادقة
"""

from typing import Optional

from .base import AITeddyBearException, ErrorCategory, ErrorSeverity


class SecurityException(AITeddyBearException):
    """Base security exception"""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            error_code=kwargs.get("error_code", "SECURITY_ERROR"),
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.SECURITY,
            recoverable=False,
            **{k: v for k, v in kwargs.items() if k != "error_code"},
        )


class AuthenticationException(SecurityException):
    """فشل المصادقة"""

    def __init__(self, reason: str, auth_method: Optional[str] = None, **kwargs):
        super().__init__(
            message=f"Authentication failed: {reason}",
            error_code="AUTHENTICATION_FAILED",
            category=ErrorCategory.AUTHENTICATION,
            suggested_actions=["Re-authenticate", "Check credentials"],
            **kwargs,
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
        **kwargs,
    ):
        message = f"Unauthorized action: {action}"
        if resource:
            message += f" on resource: {resource}"

        super().__init__(
            message=message,
            error_code="AUTHORIZATION_FAILED",
            category=ErrorCategory.AUTHORIZATION,
            suggested_actions=["Request permission", "Contact administrator"],
            **kwargs,
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
            **kwargs,
        )
        self.token_type = token_type
