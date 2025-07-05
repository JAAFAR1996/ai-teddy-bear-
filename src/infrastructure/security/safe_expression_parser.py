"""
Safe Expression Parser - Enterprise-Grade Security
Replaces dangerous eval/exec with AST-based parsing and restricted execution
"""

import ast
import json
import logging
import operator
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Union

import jsonlogic
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)


class ExpressionType(Enum):
    """Types of expressions that can be safely evaluated"""

    ARITHMETIC = "arithmetic"
    COMPARISON = "comparison"
    LOGICAL = "logical"
    STRING = "string"
    JSON_LOGIC = "json_logic"
    TEMPLATE = "template"


class SecurityLevel(Enum):
    """Security levels for expression evaluation"""

    RESTRICTED = "restricted"  # Only basic operations
    STANDARD = "standard"  # Common operations
    EXTENDED = "extended"  # Advanced operations with validation


@dataclass
class ExpressionContext:
    """Context for expression evaluation"""

    variables: Dict[str, Any] = field(default_factory=dict)
    functions: Dict[str, Callable] = field(default_factory=dict)
    security_level: SecurityLevel = SecurityLevel.RESTRICTED
    max_complexity: int = 10
    timeout_seconds: float = 5.0
    allowed_modules: Set[str] = field(default_factory=set)
    forbidden_patterns: List[str] = field(default_factory=list)


class SafeExpressionConfig(BaseModel):
    """Configuration for safe expression evaluation"""

    default_security_level: SecurityLevel = Field(
        default=SecurityLevel.RESTRICTED)
    max_complexity_score: int = Field(
        default=10, description="Maximum AST complexity")
    evaluation_timeout: float = Field(
        default=5.0, description="Evaluation timeout in seconds"
    )
    enable_json_logic: bool = Field(
        default=True, description="Enable JSONLogic support"
    )
    enable_templates: bool = Field(
        default=True, description="Enable template processing"
    )
    strict_validation: bool = Field(
        default=True, description="Strict input validation")

    # Allowed operations
    allowed_operators: Set[str] = Field(
        default_factory=lambda: {
            "Add",
            "Sub",
            "Mult",
            "Div",
            "FloorDiv",
            "Mod",
            "Pow",
            "Eq",
            "NotEq",
            "Lt",
            "LtE",
            "Gt",
            "GtE",
            "And",
            "Or",
            "Not",
            "In",
            "NotIn",
        }
    )

    # Forbidden patterns
    forbidden_patterns: List[str] = Field(
        default_factory=lambda: [
            r"__import__",
            r"eval\s*\(",
            r"exec\s*\(",
            r"compile\s*\(",
            r"open\s*\(",
            r"file\s*\(",
            r"input\s*\(",
            r"raw_input\s*\(",
            r"execfile\s*\(",
            r"reload\s*\(",
            r"getattr\s*\(",
            r"setattr\s*\(",
            r"delattr\s*\(",
            r"hasattr\s*\(",
            r"globals\s*\(",
            r"locals\s*\(",
            r"vars\s*\(",
            r"dir\s*\(",
            r"help\s*\(",
            r"breakpoint\s*\(",
        ]
    )

    class Config:
        validate_assignment = True


class ExpressionValidationError(Exception):
    """Raised when expression validation fails"""

    pass


class ExpressionSecurityError(Exception):
    """Raised when expression security check fails"""

    pass


class ExpressionTimeoutError(Exception):
    """Raised when expression evaluation times out"""

    pass


class IExpressionParser(ABC):
    """Interface for expression parsers"""

    @abstractmethod
    def validate(self, expression: str) -> bool:
        """Validate expression for security"""
        pass

    @abstractmethod
    def evaluate(
        self, expression: str, context: Optional[ExpressionContext] = None
    ) -> Any:
        """Evaluate expression safely"""
        pass


class ASTComplexityAnalyzer:
    """Analyze AST complexity for security"""

    def __init__(self, config: SafeExpressionConfig):
        self.config = config
        self.complexity_weights = {
            ast.BinOp: 1,
            ast.UnaryOp: 1,
            ast.Compare: 1,
            ast.BoolOp: 1,
            ast.Call: 3,
            ast.Attribute: 2,
            ast.Subscript: 2,
            ast.ListComp: 5,
            ast.DictComp: 5,
            ast.GeneratorExp: 5,
            ast.Lambda: 3,
            ast.IfExp: 2,
        }

    def analyze_complexity(self, node: ast.AST) -> int:
        """Calculate complexity score for AST node"""
        complexity = 0

        for child in ast.walk(node):
            node_type = type(child)
            if node_type in self.complexity_weights:
                complexity += self.complexity_weights[node_type]

        return complexity

    def is_complexity_acceptable(self, node: ast.AST) -> bool:
        """Check if AST complexity is within acceptable limits"""
        complexity = self.analyze_complexity(node)
        return complexity <= self.config.max_complexity_score


class SecurityValidator:
    """Validate expressions for security risks"""

    def __init__(self, config: SafeExpressionConfig):
        self.config = config
        self.forbidden_patterns = [
            re.compile(
                pattern,
                re.IGNORECASE) for pattern in config.forbidden_patterns]

    def validate_expression(self, expression: str) -> bool:
        """Validate expression for security risks"""
        # Check for forbidden patterns
        for pattern in self.forbidden_patterns:
            if pattern.search(expression):
                logger.warning(
                    f"🚨 Forbidden pattern detected: {pattern.pattern}")
                return False

        # Check for suspicious imports
        if "__import__" in expression or "import" in expression:
            logger.warning("🚨 Import statement detected")
            return False

        # Check for function calls that might be dangerous
        dangerous_functions = ["eval", "exec", "compile", "open", "file"]
        for func in dangerous_functions:
            if f"{func}(" in expression:
                logger.warning(f"🚨 Dangerous function call detected: {func}")
                return False

        return True

    def _validate_node(self, node: ast.AST) -> bool:
        """Validate a single AST node for security risks."""
        # Check for dangerous node types
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            logger.warning("🚨 Import statement in AST")
            return False

        # Check for dangerous function calls
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
                if func_name in ["eval", "exec", "compile", "open", "file"]:
                    logger.warning(f"🚨 Dangerous function call: {func_name}")
                    return False

            if isinstance(node.func, ast.Attribute):
                if (
                    isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "__builtins__"
                ):
                    logger.warning("🚨 Builtins access detected")
                    return False
        return True

    def validate_ast(self, node: ast.AST) -> bool:
        """Validate AST for security risks"""
        for child in ast.walk(node):
            if not self._validate_node(child):
                return False
        return True


class SafeASTEvaluator:
    """Safe AST-based expression evaluator"""

    def __init__(self, config: SafeExpressionConfig):
        self.config = config
        self.complexity_analyzer = ASTComplexityAnalyzer(config)
        self.security_validator = SecurityValidator(config)

        self._operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.FloorDiv: operator.floordiv,
            ast.Mod: operator.mod,
            ast.Pow: operator.pow,
            ast.Eq: operator.eq,
            ast.NotEq: operator.ne,
            ast.Lt: operator.lt,
            ast.LtE: operator.le,
            ast.Gt: operator.gt,
            ast.GtE: operator.ge,
            ast.And: all,
            ast.Or: any,
            ast.Not: operator.not_,
            ast.In: self._operator_in,
            ast.NotIn: self._operator_not_in,
        }

        self._node_evaluators = {
            ast.Constant: self._evaluate_constant,
            ast.Name: self._evaluate_name,
            ast.BinOp: self._evaluate_binop,
            ast.UnaryOp: self._evaluate_unaryop,
            ast.Compare: self._evaluate_compare,
            ast.BoolOp: self._evaluate_boolop,
            ast.Call: self._evaluate_call,
            ast.List: self._evaluate_list,
            ast.Dict: self._evaluate_dict,
            ast.Tuple: self._evaluate_tuple,
            ast.Subscript: self._evaluate_subscript,
            ast.IfExp: self._evaluate_ifexp,
            ast.Lambda: self._unsupported_feature,
            ast.ListComp: self._unsupported_feature,
            ast.GeneratorExp: self._unsupported_feature,
            ast.DictComp: self._unsupported_feature,
        }

        self.safe_functions = {
            "abs": abs,
            "round": round,
            "min": min,
            "max": max,
            "sum": sum,
            "len": len,
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
            "list": list,
            "dict": dict,
            "set": set,
            "tuple": tuple,
        }

    def evaluate(
        self, expression: str, context: Optional[ExpressionContext] = None
    ) -> Any:
        """Evaluate expression safely using AST"""
        try:
            if not self.security_validator.validate_expression(expression):
                raise ExpressionSecurityError(
                    "Expression contains security risks")

            tree = ast.parse(expression, mode="eval")

            if not self.security_validator.validate_ast(tree):
                raise ExpressionSecurityError("AST contains security risks")

            if not self.complexity_analyzer.is_complexity_acceptable(tree):
                raise ExpressionSecurityError("Expression too complex")

            return self._evaluate_node(
                tree.body, context or ExpressionContext())

        except SyntaxError as e:
            raise ExpressionValidationError(f"Invalid syntax: {e}") from e
        except Exception as e:
            if isinstance(e, (ExpressionSecurityError,
                          ExpressionValidationError)):
                raise
            raise ExpressionValidationError(f"Evaluation error: {e}") from e

    def _evaluate_node(self, node: ast.AST, context: ExpressionContext) -> Any:
        """Evaluate AST node safely by dispatching to the correct handler."""
        node_type = type(node)
        evaluator = self._node_evaluators.get(node_type)

        if evaluator:
            return evaluator(node, context)
        raise ExpressionSecurityError(
            f"Unsafe or unsupported node type: {node_type.__name__}"
        )

    def _operator_in(self, a, b):
        return operator.contains(b, a)

    def _operator_not_in(self, a, b):
        return not operator.contains(b, a)

    def _evaluate_constant(
            self,
            node: ast.Constant,
            context: ExpressionContext) -> Any:
        return node.value

    def _evaluate_name(
            self,
            node: ast.Name,
            context: ExpressionContext) -> Any:
        if node.id in context.variables:
            return context.variables[node.id]
        if node.id in self.safe_functions:
            return self.safe_functions[node.id]
        raise ExpressionValidationError(
            f"Undefined or unsafe variable: {node.id}")

    def _evaluate_binop(
            self,
            node: ast.BinOp,
            context: ExpressionContext) -> Any:
        left = self._evaluate_node(node.left, context)
        right = self._evaluate_node(node.right, context)
        op_type = type(node.op)

        if op_type in self._operators:
            return self._operators[op_type](left, right)
        raise ExpressionSecurityError(
            f"Unsafe binary operator: {op_type.__name__}")

    def _evaluate_unaryop(
            self,
            node: ast.UnaryOp,
            context: ExpressionContext) -> Any:
        operand = self._evaluate_node(node.operand, context)
        op_type = type(node.op)

        if op_type in self._operators:
            return self._operators[op_type](operand)
        raise ExpressionSecurityError(
            f"Unsafe unary operator: {op_type.__name__}")

    def _evaluate_compare(
            self,
            node: ast.Compare,
            context: ExpressionContext) -> Any:
        left = self._evaluate_node(node.left, context)
        for op, comparator in zip(node.ops, node.comparators):
            right = self._evaluate_node(comparator, context)
            op_type = type(op)

            if op_type not in self._operators or not self._operators[op_type](
                left, right
            ):
                return False
            left = right
        return True

    def _evaluate_boolop(
            self,
            node: ast.BoolOp,
            context: ExpressionContext) -> Any:
        values = (self._evaluate_node(value, context) for value in node.values)
        op_type = type(node.op)

        if op_type in self._operators:
            return self._operators[op_type](values)
        raise ExpressionSecurityError(
            f"Unsafe boolean operator: {op_type.__name__}")

    def _evaluate_call(
            self,
            node: ast.Call,
            context: ExpressionContext) -> Any:
        func_node = self._evaluate_node(node.func, context)

        if not callable(func_node):
            raise ExpressionValidationError(
                "Expression tries to call a non-callable object"
            )

        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            if (
                func_name not in self.safe_functions
                and func_name not in context.functions
            ):
                raise ExpressionSecurityError(
                    f"Unsafe function call: {func_name}")

        args = [self._evaluate_node(arg, context) for arg in node.args]
        kwargs = {
            kw.arg: self._evaluate_node(
                kw.value,
                context) for kw in node.keywords}

        return func_node(*args, **kwargs)

    def _evaluate_list(
            self,
            node: ast.List,
            context: ExpressionContext) -> list:
        return [self._evaluate_node(elt, context) for elt in node.elts]

    def _evaluate_dict(
            self,
            node: ast.Dict,
            context: ExpressionContext) -> dict:
        return {
            self._evaluate_node(k, context): self._evaluate_node(v, context)
            for k, v in zip(node.keys, node.values)
            if k is not None
        }

    def _evaluate_tuple(
            self,
            node: ast.Tuple,
            context: ExpressionContext) -> tuple:
        return tuple(self._evaluate_node(elt, context) for elt in node.elts)

    def _evaluate_subscript(
        self, node: ast.Subscript, context: ExpressionContext
    ) -> Any:
        value = self._evaluate_node(node.value, context)
        slice_val = self._evaluate_node(node.slice, context)
        return value[slice_val]

    def _evaluate_ifexp(
            self,
            node: ast.IfExp,
            context: ExpressionContext) -> Any:
        test = self._evaluate_node(node.test, context)
        return (
            self._evaluate_node(node.body, context)
            if test
            else self._evaluate_node(node.orelse, context)
        )

    def _unsupported_feature(self, node: ast.AST, context: ExpressionContext):
        raise ExpressionSecurityError(
            f"{type(node).__name__} is not supported for security reasons"
        )


class JSONLogicParser(IExpressionParser):
    """JSONLogic expression parser for business rules"""

    def __init__(self, config: SafeExpressionConfig):
        self.config = config

    def validate(self, expression: str) -> bool:
        """Validate JSONLogic expression"""
        try:
            if isinstance(expression, str):
                json_logic = json.loads(expression)
            else:
                json_logic = expression

            # Basic validation - ensure it's a valid JSONLogic structure
            if not isinstance(json_logic, dict):
                return False

            return True
        except (json.JSONDecodeError, TypeError):
            return False

    def evaluate(
        self, expression: str, context: Optional[ExpressionContext] = None
    ) -> Any:
        """Evaluate JSONLogic expression"""
        try:
            if isinstance(expression, str):
                json_logic = json.loads(expression)
            else:
                json_logic = expression

            variables = context.variables if context else {}
            return jsonlogic.apply(json_logic, variables)

        except Exception as e:
            raise ExpressionValidationError(f"JSONLogic evaluation error: {e}")


class TemplateParser(IExpressionParser):
    """Safe template parser for dynamic content"""

    def __init__(self, config: SafeExpressionConfig):
        self.config = config
        self.ast_evaluator = SafeASTEvaluator(config)

    def validate(self, expression: str) -> bool:
        """Validate template expression"""
        # Check for template placeholders
        placeholder_pattern = r"\{\{.*?\}\}"
        placeholders = re.findall(placeholder_pattern, expression)

        for placeholder in placeholders:
            # Extract expression inside placeholder
            expr = placeholder[2:-2].strip()
            if not self.ast_evaluator.security_validator.validate_expression(
                    expr):
                return False

        return True

    def evaluate(
        self, expression: str, context: Optional[ExpressionContext] = None
    ) -> str:
        """Evaluate template expression"""
        if not context:
            context = ExpressionContext()

        def replace_placeholder(match):
            expr = match.group(1).strip()
            try:
                result = self.ast_evaluator.evaluate(expr, context)
                return str(result)
            except Exception as e:
                logger.warning(f"Template evaluation error: {e}")
                return match.group(0)  # Return original placeholder

        # Replace placeholders safely
        pattern = r"\{\{(.*?)\}\}"
        return re.sub(pattern, replace_placeholder, expression)


class SafeExpressionParser:
    """Main safe expression parser with multiple backends"""

    def __init__(self, config: Optional[SafeExpressionConfig] = None):
        self.config = config or SafeExpressionConfig()
        self.ast_evaluator = SafeASTEvaluator(self.config)
        self.json_logic_parser = JSONLogicParser(self.config)
        self.template_parser = TemplateParser(self.config)

    def detect_expression_type(self, expression: str) -> ExpressionType:
        """Detect expression type automatically"""
        expression = expression.strip()

        # Check for JSONLogic
        if expression.startswith("{") and expression.endswith("}"):
            try:
                json.loads(expression)
                return ExpressionType.JSON_LOGIC
            except json.JSONDecodeError:
                pass

        # Check for template
        if "{{" in expression and "}}" in expression:
            return ExpressionType.TEMPLATE

        # Default to arithmetic
        return ExpressionType.ARITHMETIC

    def validate(
        self, expression: str, expression_type: Optional[ExpressionType] = None
    ) -> bool:
        """Validate expression for security"""
        if not expression_type:
            expression_type = self.detect_expression_type(expression)

        try:
            if expression_type == ExpressionType.JSON_LOGIC:
                return self.json_logic_parser.validate(expression)
            elif expression_type == ExpressionType.TEMPLATE:
                return self.template_parser.validate(expression)
            else:
                return self.ast_evaluator.security_validator.validate_expression(
                    expression)
        except Exception:
            return False

    def evaluate(
        self,
        expression: str,
        context: Optional[ExpressionContext] = None,
        expression_type: Optional[ExpressionType] = None,
    ) -> Any:
        """Evaluate expression safely"""
        if not context:
            context = ExpressionContext()

        if not expression_type:
            expression_type = self.detect_expression_type(expression)

        # Validate first
        if not self.validate(expression, expression_type):
            raise ExpressionSecurityError("Expression validation failed")

        try:
            if expression_type == ExpressionType.JSON_LOGIC:
                return self.json_logic_parser.evaluate(expression, context)
            elif expression_type == ExpressionType.TEMPLATE:
                return self.template_parser.evaluate(expression, context)
            else:
                return self.ast_evaluator.evaluate(expression, context)
        except Exception as e:
            if isinstance(e, (ExpressionSecurityError,
                          ExpressionValidationError)):
                raise
            raise ExpressionValidationError(f"Evaluation failed: {e}")


# Global safe expression parser instance
safe_parser = SafeExpressionParser()


def safe_eval(expression: str,
              variables: Optional[Dict[str, Any]] = None) -> Any:
    """Safe evaluation function - replacement for eval()"""
    context = ExpressionContext(variables=variables or {})
    return safe_parser.evaluate(expression, context)


def safe_template(
        template: str, variables: Optional[Dict[str, Any]] = None) -> str:
    """Safe template processing"""
    context = ExpressionContext(variables=variables or {})
    return safe_parser.evaluate(template, context, ExpressionType.TEMPLATE)


def safe_json_logic(
    logic: Union[str, dict], variables: Optional[Dict[str, Any]] = None
) -> Any:
    """Safe JSONLogic evaluation"""
    context = ExpressionContext(variables=variables or {})
    if isinstance(logic, dict):
        logic = json.dumps(logic)
    return safe_parser.evaluate(logic, context, ExpressionType.JSON_LOGIC)
