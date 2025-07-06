"""
JSONLogic expression parser.
"""
import json
from typing import Any, Optional

import jsonlogic

from .exceptions import ExpressionValidationError
from .interfaces import IExpressionParser
from .models import ExpressionContext, SafeExpressionConfig


class JSONLogicParser(IExpressionParser):
    """
    A parser for evaluating expressions written in JSONLogic, a safe and
    standardized format for business rules.
    """

    def __init__(self, config: SafeExpressionConfig):
        self.config = config

    def validate(self, expression: str) -> bool:
        """Validates that the expression is a valid JSON object."""
        try:
            json.loads(expression)
            return True
        except (json.JSONDecodeError, TypeError):
            return False

    def evaluate(self, expression: str, context: Optional[ExpressionContext] = None) -> Any:
        """Evaluates a JSONLogic expression string."""
        try:
            logic_rules = json.loads(expression)
        except json.JSONDecodeError as e:
            raise ExpressionValidationError(
                f"Invalid JSON format for JSONLogic: {e}") from e

        data = context.variables if context else {}
        # You can add safe functions to the context if needed for jsonlogic
        # For example: data['safe_functions'] = {'min': min, 'max': max}

        try:
            return jsonlogic.apply(logic_rules, data)
        except Exception as e:
            raise ExpressionValidationError(
                f"JSONLogic evaluation failed: {e}") from e
