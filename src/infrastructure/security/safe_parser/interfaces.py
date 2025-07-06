"""
Interfaces for expression parsers.
"""
from abc import ABC, abstractmethod
from typing import Any, Optional

from .models import ExpressionContext


class IExpressionParser(ABC):
    """
    Defines the contract for an expression parser, ensuring that it provides
    both validation and evaluation methods.
    """

    @abstractmethod
    def validate(self, expression: str) -> bool:
        """
        Validates the expression for syntax and security.

        Returns:
            True if the expression is valid and safe, False otherwise.
        """
        pass

    @abstractmethod
    def evaluate(self, expression: str, context: Optional[ExpressionContext] = None) -> Any:
        """
        Safely evaluates the expression within a given context.

        Args:
            expression: The expression string to evaluate.
            context: The context containing variables and functions available to the expression.

        Returns:
            The result of the evaluation.

        Raises:
            ExpressionValidationError: If the expression is invalid.
            ExpressionSecurityError: If the expression poses a security risk.
        """
        pass
