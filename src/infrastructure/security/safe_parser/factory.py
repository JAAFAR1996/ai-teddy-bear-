"""
Factory and convenience functions for the safe expression parser.
"""
import json
from typing import Any, Dict, Optional, Union

from .models import ExpressionContext, ExpressionType
from .parser import SafeExpressionParser

_safe_parser: Optional[SafeExpressionParser] = None


def get_safe_parser() -> SafeExpressionParser:
    """
    Factory function to create and return a singleton instance of the
    SafeExpressionParser.
    """
    global _safe_parser
    if _safe_parser is None:
        _safe_parser = SafeExpressionParser()
    return _safe_parser


def safe_eval(expression: str, variables: Optional[Dict[str, Any]] = None) -> Any:
    """
    A safe replacement for `eval()` that evaluates a simple expression string.

    Args:
        expression: The arithmetic or logical expression to evaluate.
        variables: A dictionary of variables available to the expression.

    Returns:
        The result of the expression.
    """
    parser = get_safe_parser()
    context = ExpressionContext(variables=variables or {})
    return parser.evaluate(expression, context)


def safe_template(template: str, variables: Optional[Dict[str, Any]] = None) -> str:
    """
    Safely evaluates a template string, replacing `{{...}}` placeholders.

    Args:
        template: The template string.
        variables: A dictionary of variables available to the placeholders.

    Returns:
        The rendered string.
    """
    parser = get_safe_parser()
    context = ExpressionContext(variables=variables or {})
    return parser.evaluate(template, context, expression_type=ExpressionType.TEMPLATE)


def safe_json_logic(logic_rules: Union[str, dict], data: Optional[Dict[str, Any]] = None) -> Any:
    """
    Safely evaluates a set of rules written in JSONLogic format.

    Args:
        logic_rules: The JSONLogic rules as a dictionary or a JSON string.
        data: The data to apply the rules against.

    Returns:
        The result of the JSONLogic evaluation.
    """
    parser = get_safe_parser()
    context = ExpressionContext(variables=data or {})
    expression = json.dumps(logic_rules) if isinstance(
        logic_rules, dict) else logic_rules
    return parser.evaluate(expression, context, expression_type=ExpressionType.JSON_LOGIC)
