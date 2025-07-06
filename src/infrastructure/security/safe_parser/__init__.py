"""
A safe, modular expression parsing and evaluation engine.
"""

from .exceptions import (
    ExpressionError,
    ExpressionSecurityError,
    ExpressionValidationError,
)
from .factory import get_safe_parser, safe_eval, safe_json_logic, safe_template
from .models import ExpressionContext, ExpressionType, SecurityLevel
from .parser import SafeExpressionParser

__all__ = [
    # Main Parser and Factory
    "SafeExpressionParser",
    "get_safe_parser",
    # Convenience Functions
    "safe_eval",
    "safe_json_logic",
    "safe_template",
    # Models and Enums
    "ExpressionContext",
    "ExpressionType",
    "SecurityLevel",
    # Exceptions
    "ExpressionError",
    "ExpressionSecurityError",
    "ExpressionValidationError",
]
