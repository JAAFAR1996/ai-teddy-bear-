"""
Custom exceptions for the safe expression parser.
"""


class ExpressionError(Exception):
    """Base class for all expression-related errors."""
    pass


class ExpressionValidationError(ExpressionError):
    """Raised when an expression fails syntax or structural validation."""
    pass


class ExpressionSecurityError(ExpressionError):
    """Raised when an expression poses a security risk."""
    pass


class ExpressionTimeoutError(ExpressionError):
    """Raised when the evaluation of an expression exceeds the configured timeout."""
    pass


class UnsupportedFeatureError(ExpressionSecurityError):
    """Raised when an expression uses a language feature that is not supported for security reasons."""

    def __init__(self, feature_name: str):
        self.feature_name = feature_name
        super().__init__(
            f"The feature '{feature_name}' is not supported for security reasons.")
