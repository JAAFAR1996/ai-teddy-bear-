"""
Main SafeExpressionParser class.
"""
import json
import logging
from typing import Any, Optional

from .ast_evaluator import SafeASTEvaluator
from .exceptions import ExpressionSecurityError, ExpressionValidationError
from .interfaces import IExpressionParser
from .json_logic_parser import JSONLogicParser
from .models import ExpressionContext, ExpressionType, SafeExpressionConfig
from .template_parser import TemplateParser

logger = logging.getLogger(__name__)


class SafeExpressionParser(IExpressionParser):
    """
    A facade that orchestrates multiple secure parsing engines (AST, JSONLogic, Template)
    to provide a single, safe evaluation interface.
    """

    def __init__(self, config: Optional[SafeExpressionConfig] = None):
        self.config = config or SafeExpressionConfig()
        self.ast_evaluator = SafeASTEvaluator(self.config)
        self.json_logic_parser = JSONLogicParser(self.config)
        self.template_parser = TemplateParser(self.config)

    def evaluate(
        self,
        expression: str,
        context: Optional[ExpressionContext] = None,
        expression_type: Optional[ExpressionType] = None,
    ) -> Any:
        """
        Detects the expression type if not provided, validates it, and then
        evaluates it using the appropriate secure engine.
        """
        context = context or ExpressionContext()
        expression_type = expression_type or self._detect_expression_type(
            expression)

        if not self.validate(expression, expression_type):
            raise ExpressionSecurityError(
                "Expression failed validation and will not be evaluated.")

        try:
            if expression_type == ExpressionType.JSON_LOGIC:
                return self.json_logic_parser.evaluate(expression, context)
            if expression_type == ExpressionType.TEMPLATE:
                return self.template_parser.evaluate(expression, context)

            # Default to AST evaluator for arithmetic, comparison, logical, etc.
            return self.ast_evaluator.evaluate(expression, context)

        except (ExpressionValidationError, ExpressionSecurityError):
            # Re-raise known, specific errors
            raise
        except Exception as e:
            # Wrap unexpected errors
            logger.error(
                "An unexpected error occurred during evaluation", exc_info=True)
            raise ExpressionValidationError(
                f"Evaluation failed with an unexpected error: {e}")

    def validate(self, expression: str, expression_type: Optional[ExpressionType] = None) -> bool:
        """Validates an expression using the appropriate engine."""
        expression_type = expression_type or self._detect_expression_type(
            expression)

        try:
            if expression_type == ExpressionType.JSON_LOGIC:
                return self.json_logic_parser.validate(expression)
            if expression_type == ExpressionType.TEMPLATE:
                return self.template_parser.validate(expression)

            # For AST-based evaluations, validation is part of the evaluate call
            # but we can do a preliminary check.
            self.ast_evaluator.evaluate(expression, ExpressionContext())
            return True
        except (ExpressionValidationError, ExpressionSecurityError):
            return False
        except Exception:
            # Any other exception during a dry-run validation means it's not valid.
            return False

    def _detect_expression_type(self, expression: str) -> ExpressionType:
        """Automatically detects the most likely type of an expression."""
        expression = expression.strip()

        if self.config.enable_json_logic and expression.startswith("{") and expression.endswith("}"):
            try:
                json.loads(expression)
                return ExpressionType.JSON_LOGIC
            except json.JSONDecodeError:
                pass

        if self.config.enable_templates and "{{" in expression and "}}" in expression:
            return ExpressionType.TEMPLATE

        # Default to a general-purpose type handled by the AST evaluator
        return ExpressionType.ARITHMETIC
