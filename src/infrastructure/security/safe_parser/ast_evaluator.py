"""
Safe, AST-based expression evaluator.
"""
import ast
import logging
import operator
from typing import Any, Callable, Dict

from .ast_analyzer import ASTComplexityAnalyzer, SecurityValidator
from .exceptions import (
    ExpressionSecurityError,
    ExpressionValidationError,
    UnsupportedFeatureError,
)
from .models import ExpressionContext, SafeExpressionConfig

logger = logging.getLogger(__name__)


class SafeASTEvaluator:
    """
    Evaluates an expression by safely walking its Abstract Syntax Tree (AST),
    only allowing a whitelisted set of operations and nodes.
    """

    def __init__(self, config: SafeExpressionConfig):
        self.config = config
        self.complexity_analyzer = ASTComplexityAnalyzer(config)
        self.security_validator = SecurityValidator(config)
        self._operators: Dict[type, Callable] = self._get_operator_map()
        self._node_evaluators: Dict[type,
                                    Callable] = self._get_node_evaluator_map()
        self.safe_functions: Dict[str, Callable] = self._get_safe_functions()

    def evaluate(self, expression: str, context: ExpressionContext) -> Any:
        """Parses, validates, and evaluates an expression string."""
        if not self.security_validator.validate_expression_string(expression):
            raise ExpressionSecurityError(
                "Expression contains forbidden patterns.")

        try:
            tree = ast.parse(expression, mode="eval")
        except SyntaxError as e:
            raise ExpressionValidationError(
                f"Invalid expression syntax: {e}") from e

        if not self.security_validator.validate_ast(tree):
            raise ExpressionSecurityError(
                "Expression AST contains unsafe nodes.")

        if not self.complexity_analyzer.is_complexity_acceptable(tree):
            raise ExpressionSecurityError(
                "Expression exceeds maximum complexity.")

        return self._evaluate_node(tree.body, context)

    def _evaluate_node(self, node: ast.AST, context: ExpressionContext) -> Any:
        """Recursively evaluates a single AST node."""
        node_type = type(node)
        evaluator = self._node_evaluators.get(node_type)
        if evaluator:
            return evaluator(node, context)
        raise UnsupportedFeatureError(node_type.__name__)

    def _evaluate_name(self, node: ast.Name, context: ExpressionContext) -> Any:
        if node.id in context.variables:
            return context.variables[node.id]
        if node.id in self.safe_functions:
            return self.safe_functions[node.id]
        if node.id in context.functions:
            return context.functions[node.id]
        raise ExpressionValidationError(
            f"Undefined or disallowed variable/function: {node.id}")

    def _evaluate_call(self, node: ast.Call, context: ExpressionContext) -> Any:
        func = self._evaluate_node(node.func, context)
        if not callable(func):
            raise ExpressionValidationError(
                "Attempted to call a non-callable object.")

        args = [self._evaluate_node(arg, context) for arg in node.args]
        kwargs = {kw.arg: self._evaluate_node(
            kw.value, context) for kw in node.keywords}

        # Security check on the function itself
        if func not in self.safe_functions.values() and func not in context.functions.values():
            raise ExpressionSecurityError(
                f"Function call '{getattr(func, '__name__', 'unknown')}' is not allowed.")

        return func(*args, **kwargs)

    # Helper methods for individual node types
    def _evaluate_constant(self, node: ast.Constant,
                           context: ExpressionContext) -> Any: return node.value

    def _evaluate_list(self, node: ast.List, context: ExpressionContext) -> list: return [
        self._evaluate_node(elt, context) for elt in node.elts]

    def _evaluate_tuple(self, node: ast.Tuple, context: ExpressionContext) -> tuple: return tuple(
        self._evaluate_node(elt, context) for elt in node.elts)

    def _evaluate_dict(self, node: ast.Dict, context: ExpressionContext) -> dict: return {
        self._evaluate_node(k, context): self._evaluate_node(v, context) for k, v in zip(node.keys, node.values)}

    def _evaluate_subscript(self, node: ast.Subscript, context: ExpressionContext) -> Any: return self._evaluate_node(
        node.value, context)[self._evaluate_node(node.slice, context)]

    def _evaluate_ifexp(self, node: ast.IfExp, context: ExpressionContext) -> Any: return self._evaluate_node(
        node.body, context) if self._evaluate_node(node.test, context) else self._evaluate_node(node.orelse, context)

    def _evaluate_binop(self, node: ast.BinOp, context: ExpressionContext) -> Any:
        op = self._operators.get(type(node.op))
        if not op:
            raise UnsupportedFeatureError(type(node.op).__name__)
        return op(self._evaluate_node(node.left, context), self._evaluate_node(node.right, context))

    def _evaluate_unaryop(self, node: ast.UnaryOp, context: ExpressionContext) -> Any:
        op = self._operators.get(type(node.op))
        if not op:
            raise UnsupportedFeatureError(type(node.op).__name__)
        return op(self._evaluate_node(node.operand, context))

    def _evaluate_boolop(self, node: ast.BoolOp, context: ExpressionContext) -> bool:
        op = self._operators.get(type(node.op))
        if not op:
            raise UnsupportedFeatureError(type(node.op).__name__)
        return op(self._evaluate_node(v, context) for v in node.values)

    def _evaluate_compare(self, node: ast.Compare, context: ExpressionContext) -> bool:
        left = self._evaluate_node(node.left, context)
        for op_node, comp_node in zip(node.ops, node.comparators):
            op = self._operators.get(type(op_node))
            if not op:
                raise UnsupportedFeatureError(type(op_node).__name__)
            right = self._evaluate_node(comp_node, context)
            if not op(left, right):
                return False
            left = right
        return True

    def _get_operator_map(self) -> Dict[type, Callable]:
        return {
            ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
            ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv, ast.Mod: operator.mod,
            ast.Pow: operator.pow, ast.Eq: operator.eq, ast.NotEq: operator.ne,
            ast.Lt: operator.lt, ast.LtE: operator.le, ast.Gt: operator.gt, ast.GtE: operator.ge,
            ast.And: all, ast.Or: any, ast.Not: operator.not_,
            ast.In: lambda a, b: operator.contains(b, a),
            ast.NotIn: lambda a, b: not operator.contains(b, a),
        }

    def _get_node_evaluator_map(self) -> Dict[type, Callable]:
        return {
            ast.Constant: self._evaluate_constant, ast.Name: self._evaluate_name,
            ast.BinOp: self._evaluate_binop, ast.UnaryOp: self._evaluate_unaryop,
            ast.Compare: self._evaluate_compare, ast.BoolOp: self._evaluate_boolop,
            ast.Call: self._evaluate_call, ast.List: self._evaluate_list,
            ast.Dict: self._evaluate_dict, ast.Tuple: self._evaluate_tuple,
            ast.Subscript: self._evaluate_subscript, ast.IfExp: self._evaluate_ifexp,
        }

    def _get_safe_functions(self) -> Dict[str, Callable]:
        return {
            "abs": abs, "round": round, "min": min, "max": max, "sum": sum,
            "len": len, "str": str, "int": int, "float": float, "bool": bool,
        }
