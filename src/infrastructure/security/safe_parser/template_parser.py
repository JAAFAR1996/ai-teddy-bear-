"""
Safe template parser for dynamic content generation.
"""
import logging
import re
from typing import Any, Optional

from .ast_evaluator import SafeASTEvaluator
from .exceptions import ExpressionValidationError
from .interfaces import IExpressionParser
from .models import ExpressionContext, SafeExpressionConfig

logger = logging.getLogger(__name__)


class TemplateParser(IExpressionParser):
    """
    A parser for safely evaluating simple string templates with embedded expressions.
    Example: "Hello, {{ user.name }}!"
    """

    def __init__(self, config: SafeExpressionConfig):
        self.config = config
        self.ast_evaluator = SafeASTEvaluator(config)
        # Simple regex to find {{ ... }} placeholders
        self.placeholder_pattern = re.compile(r"\{\{(.*?)\}\}")

    def validate(self, expression: str) -> bool:
        """
        Validates the security of all embedded expressions within the template string.
        """
        placeholders = self.placeholder_pattern.findall(expression)
        for expr in placeholders:
            try:
                # Use the AST evaluator's internal validation logic
                self.ast_evaluator.evaluate(expr.strip(), ExpressionContext())
            except (ExpressionValidationError, Exception):
                # We can be more granular here, but for a simple bool, False is enough
                return False
        return True

    def evaluate(self, expression: str, context: Optional[ExpressionContext] = None) -> Any:
        """
        Evaluates the template by replacing all embedded expression placeholders
        with their evaluated values.
        """
        if context is None:
            context = ExpressionContext()

        def replace_match(match):
            expr = match.group(1).strip()
            try:
                return str(self.ast_evaluator.evaluate(expr, context))
            except Exception as e:
                logger.warning(
                    "Template placeholder evaluation failed",
                    expression=expr,
                    error=str(e),
                    exc_info=True
                )
                # On failure, leave the placeholder as is
                return match.group(0)

        return self.placeholder_pattern.sub(replace_match, expression)
