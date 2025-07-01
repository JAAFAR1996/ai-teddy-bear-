"""
Safe Expression Parser - Secure alternative to eval/exec
Supports mathematical operations and whitelisted functions only
"""

import ast
import logging
import math
import operator
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Dict, Optional, Set, Union

logger = logging.getLogger(__name__)


class ExpressionType(Enum):
    """Types of expressions that can be parsed"""

    MATHEMATICAL = auto()
    LOGICAL = auto()
    STRING_TEMPLATE = auto()
    JSON_PATH = auto()
    CONDITIONAL = auto()


class SecurityLevel(Enum):
    """Security levels for expression parsing"""

    STRICT = auto()  # Only basic math operations
    MODERATE = auto()  # Math + safe string operations
    RELAXED = auto()  # Math + strings + limited functions


@dataclass
class ParseResult:
    """Result of expression parsing"""

    success: bool
    value: Any = None
    error: Optional[str] = None
    expression_type: Optional[ExpressionType] = None
    execution_time_ms: float = 0


@dataclass
class ExpressionContext:
    """Context for expression evaluation"""

    variables: Dict[str, Any]
    allowed_names: Set[str]
    max_string_length: int = 1000
    max_list_length: int = 100
    max_recursion_depth: int = 10
    timeout_seconds: float = 1.0


class SafeExpressionParser:
    """Main parser for safe expression evaluation"""

    # Safe operators mapping
    OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.LShift: operator.lshift,
        ast.RShift: operator.rshift,
        ast.BitOr: operator.or_,
        ast.BitXor: operator.xor,
        ast.BitAnd: operator.and_,
        ast.Eq: operator.eq,
        ast.NotEq: operator.ne,
        ast.Lt: operator.lt,
        ast.LtE: operator.le,
        ast.Gt: operator.gt,
        ast.GtE: operator.ge,
        ast.Is: operator.is_,
        ast.IsNot: operator.is_not,
        ast.In: lambda x, y: x in y,
        ast.NotIn: lambda x, y: x not in y,
    }

    # Unary operators
    UNARY_OPERATORS = {
        ast.UAdd: operator.pos,
        ast.USub: operator.neg,
        ast.Not: operator.not_,
        ast.Invert: operator.invert,
    }

    # Safe math functions whitelist
    SAFE_MATH_FUNCTIONS = {
        "abs": abs,
        "round": round,
        "min": min,
        "max": max,
        "sum": sum,
        "len": len,
        "int": int,
        "float": float,
        "str": str,
        "bool": bool,
        # Math module functions
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "sqrt": math.sqrt,
        "log": math.log,
        "log10": math.log10,
        "exp": math.exp,
        "pow": math.pow,
        "ceil": math.ceil,
        "floor": math.floor,
        "pi": math.pi,
        "e": math.e,
    }

    # Safe string operations
    SAFE_STRING_METHODS = {
        "upper",
        "lower",
        "strip",
        "lstrip",
        "rstrip",
        "startswith",
        "endswith",
        "replace",
        "split",
        "join",
        "find",
        "count",
        "isdigit",
        "isalpha",
        "isalnum",
        "isspace",
        "capitalize",
        "title",
    }

    def __init__(self, security_level: SecurityLevel = SecurityLevel.MODERATE):
        self.security_level = security_level
        self._setup_allowed_operations()

    def _setup_allowed_operations(self):
        """Setup allowed operations based on security level"""
        self.allowed_functions = set()
        self.allowed_attributes = set()

        if self.security_level == SecurityLevel.STRICT:
            # Only basic math
            self.allowed_functions = {
                "abs",
                "round",
                "min",
                "max",
                "sum",
                "int",
                "float",
            }
        elif self.security_level == SecurityLevel.MODERATE:
            # Math + safe string operations
            self.allowed_functions = set(self.SAFE_MATH_FUNCTIONS.keys())
            self.allowed_attributes = self.SAFE_STRING_METHODS
        else:  # RELAXED
            # All safe operations
            self.allowed_functions = set(self.SAFE_MATH_FUNCTIONS.keys())
            self.allowed_attributes = self.SAFE_STRING_METHODS
            # Add additional safe operations
            self.allowed_functions.update(
                {"sorted", "reversed", "enumerate", "zip", "range"}
            )

    def parse(
        self, expression: str, context: Optional[ExpressionContext] = None
    ) -> ParseResult:
        """Parse and evaluate an expression safely"""
        import time

        start_time = time.time()

        try:
            # Input validation
            if not expression or not isinstance(expression, str):
                return ParseResult(
                    success=False, error="Invalid expression: must be non-empty string"
                )

            if len(expression) > 10000:  # Max expression length
                return ParseResult(success=False, error="Expression too long")

            # Create default context if not provided
            if context is None:
                context = ExpressionContext(variables={}, allowed_names=set())

            # Parse AST
            try:
                tree = ast.parse(expression, mode="eval")
            except SyntaxError as e:
                return ParseResult(success=False, error=f"Syntax error: {e}")

            # Validate AST
            validator = ASTValidator(
                self.allowed_functions, self.allowed_attributes, context
            )

            is_valid, error = validator.validate(tree)
            if not is_valid:
                return ParseResult(success=False, error=error)

            # Evaluate expression
            evaluator = SafeEvaluator(
                self.OPERATORS, self.UNARY_OPERATORS, self.SAFE_MATH_FUNCTIONS, context
            )

            result = evaluator.evaluate(tree.body)

            execution_time = (time.time() - start_time) * 1000

            return ParseResult(
                success=True,
                value=result,
                expression_type=self._detect_expression_type(tree),
                execution_time_ms=execution_time,
            )

        except Exception as e:
            logger.error(f"Error parsing expression: {e}")
            return ParseResult(success=False, error=f"Evaluation error: {str(e)}")

    def _detect_expression_type(self, tree: ast.AST) -> ExpressionType:
        """Detect the type of expression"""
        if self._is_mathematical(tree):
            return ExpressionType.MATHEMATICAL
        elif self._is_logical(tree):
            return ExpressionType.LOGICAL
        elif self._is_string_template(tree):
            return ExpressionType.STRING_TEMPLATE
        elif self._is_conditional(tree):
            return ExpressionType.CONDITIONAL
        else:
            return ExpressionType.MATHEMATICAL

    def _is_mathematical(self, tree: ast.AST) -> bool:
        """Check if expression is mathematical"""
        for node in ast.walk(tree):
            if isinstance(node, (ast.Num, ast.BinOp, ast.UnaryOp)):
                return True
        return False

    def _is_logical(self, tree: ast.AST) -> bool:
        """Check if expression is logical"""
        for node in ast.walk(tree):
            if isinstance(node, (ast.Compare, ast.BoolOp)):
                return True
        return False

    def _is_string_template(self, tree: ast.AST) -> bool:
        """Check if expression is string template"""
        for node in ast.walk(tree):
            if isinstance(node, (ast.Str, ast.JoinedStr)):
                return True
        return False

    def _is_conditional(self, tree: ast.AST) -> bool:
        """Check if expression is conditional"""
        for node in ast.walk(tree):
            if isinstance(node, ast.IfExp):
                return True
        return False


class ASTValidator:
    """Validates AST nodes for safety"""

    def __init__(
        self,
        allowed_functions: Set[str],
        allowed_attributes: Set[str],
        context: ExpressionContext,
    ):
        self.allowed_functions = allowed_functions
        self.allowed_attributes = allowed_attributes
        self.context = context
        self.recursion_depth = 0

    def validate(self, tree: ast.AST) -> tuple[bool, Optional[str]]:
        """Validate an AST tree for safety"""
        try:
            self._validate_node(tree)
            return True, None
        except ValidationError as e:
            return False, str(e)

    def _validate_node(self, node: ast.AST):
        """Recursively validate AST node"""
        self.recursion_depth += 1

        if self.recursion_depth > self.context.max_recursion_depth:
            raise ValidationError("Maximum recursion depth exceeded")

        try:
            # Check node type
            node_type = type(node)

            # Disallow dangerous nodes
            if node_type in DANGEROUS_NODES:
                raise ValidationError(f"Dangerous node type: {node_type.__name__}")

            # Validate specific node types
            if isinstance(node, ast.Name):
                self._validate_name(node)
            elif isinstance(node, ast.Call):
                self._validate_call(node)
            elif isinstance(node, ast.Attribute):
                self._validate_attribute(node)
            elif isinstance(node, ast.Import):
                raise ValidationError("Import statements not allowed")
            elif isinstance(node, ast.ImportFrom):
                raise ValidationError("Import statements not allowed")

            # Recursively validate child nodes
            for child in ast.iter_child_nodes(node):
                self._validate_node(child)

        finally:
            self.recursion_depth -= 1

    def _validate_name(self, node: ast.Name):
        """Validate name access"""
        if node.id.startswith("_"):
            raise ValidationError(f"Private names not allowed: {node.id}")

        if (
            node.id not in self.allowed_functions
            and node.id not in self.context.variables
            and node.id not in self.context.allowed_names
        ):
            raise ValidationError(f"Name not allowed: {node.id}")

    def _validate_call(self, node: ast.Call):
        """Validate function calls"""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            if func_name not in self.allowed_functions:
                raise ValidationError(f"Function not allowed: {func_name}")
        elif isinstance(node.func, ast.Attribute):
            # Method calls will be validated in _validate_attribute
            pass
        else:
            raise ValidationError("Complex function calls not allowed")

    def _validate_attribute(self, node: ast.Attribute):
        """Validate attribute access"""
        if node.attr.startswith("_"):
            raise ValidationError(f"Private attributes not allowed: {node.attr}")

        if node.attr not in self.allowed_attributes:
            # Check if it's a valid method on allowed types
            if not self._is_safe_builtin_method(node):
                raise ValidationError(f"Attribute not allowed: {node.attr}")

    def _is_safe_builtin_method(self, node: ast.Attribute) -> bool:
        """Check if attribute is a safe builtin method"""
        # This would need more sophisticated type inference
        # For now, we'll be conservative
        return node.attr in self.allowed_attributes


class SafeEvaluator:
    """Safely evaluates validated AST"""

    def __init__(
        self,
        operators: Dict,
        unary_operators: Dict,
        safe_functions: Dict,
        context: ExpressionContext,
    ):
        self.operators = operators
        self.unary_operators = unary_operators
        self.safe_functions = safe_functions
        self.context = context

    def evaluate(self, node: ast.AST) -> Any:
        """Evaluate an AST node"""
        # Dispatch based on node type
        method_name = f"_eval_{type(node).__name__.lower()}"
        method = getattr(self, method_name, None)

        if method is None:
            raise EvaluationError(f"Cannot evaluate node type: {type(node).__name__}")

        return method(node)

    def _eval_expression(self, node: ast.Expression) -> Any:
        """Evaluate expression node"""
        return self.evaluate(node.body)

    def _eval_num(self, node: ast.Num) -> Union[int, float]:
        """Evaluate number literal"""
        return node.n

    def _eval_constant(self, node: ast.Constant) -> Any:
        """Evaluate constant (Python 3.8+)"""
        return node.value

    def _eval_str(self, node: ast.Str) -> str:
        """Evaluate string literal"""
        if len(node.s) > self.context.max_string_length:
            raise EvaluationError("String too long")
        return node.s

    def _eval_name(self, node: ast.Name) -> Any:
        """Evaluate name lookup"""
        if node.id in self.context.variables:
            return self.context.variables[node.id]
        elif node.id in self.safe_functions:
            return self.safe_functions[node.id]
        else:
            raise EvaluationError(f"Unknown name: {node.id}")

    def _eval_binop(self, node: ast.BinOp) -> Any:
        """Evaluate binary operation"""
        left = self.evaluate(node.left)
        right = self.evaluate(node.right)

        op_func = self.operators.get(type(node.op))
        if op_func is None:
            raise EvaluationError(f"Unknown operator: {type(node.op).__name__}")

        try:
            return op_func(left, right)
        except ZeroDivisionError:
            raise EvaluationError("Division by zero")
        except Exception as e:
            raise EvaluationError(f"Operation error: {e}")

    def _eval_unaryop(self, node: ast.UnaryOp) -> Any:
        """Evaluate unary operation"""
        operand = self.evaluate(node.operand)

        op_func = self.unary_operators.get(type(node.op))
        if op_func is None:
            raise EvaluationError(f"Unknown unary operator: {type(node.op).__name__}")

        return op_func(operand)

    def _eval_compare(self, node: ast.Compare) -> bool:
        """Evaluate comparison"""
        left = self.evaluate(node.left)

        for op, comparator in zip(node.ops, node.comparators):
            right = self.evaluate(comparator)

            op_func = self.operators.get(type(op))
            if op_func is None:
                raise EvaluationError(f"Unknown comparison: {type(op).__name__}")

            if not op_func(left, right):
                return False

            left = right

        return True

    def _eval_boolop(self, node: ast.BoolOp) -> bool:
        """Evaluate boolean operation"""
        if isinstance(node.op, ast.And):
            for value in node.values:
                if not self.evaluate(value):
                    return False
            return True
        elif isinstance(node.op, ast.Or):
            for value in node.values:
                if self.evaluate(value):
                    return True
            return False
        else:
            raise EvaluationError(f"Unknown boolean operator: {type(node.op).__name__}")

    def _eval_ifexp(self, node: ast.IfExp) -> Any:
        """Evaluate if expression (ternary operator)"""
        test = self.evaluate(node.test)
        if test:
            return self.evaluate(node.body)
        else:
            return self.evaluate(node.orelse)

    def _eval_call(self, node: ast.Call) -> Any:
        """Evaluate function call"""
        if isinstance(node.func, ast.Name):
            func = self.safe_functions.get(node.func.id)
            if func is None:
                raise EvaluationError(f"Unknown function: {node.func.id}")

            # Evaluate arguments
            args = [self.evaluate(arg) for arg in node.args]

            # We don't support keyword arguments for simplicity
            if node.keywords:
                raise EvaluationError("Keyword arguments not supported")

            return func(*args)
        elif isinstance(node.func, ast.Attribute):
            # Method call
            obj = self.evaluate(node.func.value)
            method_name = node.func.attr

            if not hasattr(obj, method_name):
                raise EvaluationError(f"No method {method_name}")

            method = getattr(obj, method_name)
            args = [self.evaluate(arg) for arg in node.args]

            return method(*args)
        else:
            raise EvaluationError("Complex function calls not supported")

    def _eval_list(self, node: ast.List) -> list:
        """Evaluate list literal"""
        items = [self.evaluate(item) for item in node.elts]
        if len(items) > self.context.max_list_length:
            raise EvaluationError("List too long")
        return items

    def _eval_dict(self, node: ast.Dict) -> dict:
        """Evaluate dict literal"""
        result = {}
        for key_node, value_node in zip(node.keys, node.values):
            key = self.evaluate(key_node)
            value = self.evaluate(value_node)
            result[key] = value
        return result

    def _eval_tuple(self, node: ast.Tuple) -> tuple:
        """Evaluate tuple literal"""
        return tuple(self.evaluate(item) for item in node.elts)

    def _eval_subscript(self, node: ast.Subscript) -> Any:
        """Evaluate subscript (indexing)"""
        obj = self.evaluate(node.value)

        if isinstance(node.slice, ast.Index):
            # Simple indexing
            index = self.evaluate(node.slice.value)
            return obj[index]
        elif isinstance(node.slice, ast.Slice):
            # Slicing
            lower = self.evaluate(node.slice.lower) if node.slice.lower else None
            upper = self.evaluate(node.slice.upper) if node.slice.upper else None
            step = self.evaluate(node.slice.step) if node.slice.step else None
            return obj[lower:upper:step]
        else:
            raise EvaluationError("Complex slicing not supported")

    def _eval_attribute(self, node: ast.Attribute) -> Any:
        """Evaluate attribute access"""
        obj = self.evaluate(node.value)

        if not hasattr(obj, node.attr):
            raise EvaluationError(f"No attribute {node.attr}")

        return getattr(obj, node.attr)


# Dangerous node types that should never be allowed
DANGEROUS_NODES = {
    ast.Import,
    ast.ImportFrom,
    ast.FunctionDef,
    ast.ClassDef,
    ast.AsyncFunctionDef,
    ast.Global,
    ast.Nonlocal,
    ast.Exec,  # Python 2 only but check anyway
    ast.Delete,
    ast.With,
    ast.AsyncWith,
    ast.Raise,
    ast.Try,
    ast.Assert,
    ast.YieldFrom,
    ast.Yield,
    ast.Lambda,  # Could be used for code injection
}


class ValidationError(Exception):
    """Raised when AST validation fails"""

    pass


class EvaluationError(Exception):
    """Raised when expression evaluation fails"""

    pass


# Template engine for safe code generation
class SafeTemplateEngine:
    """Safe template engine using Jinja2"""

    def __init__(self):
        from jinja2 import BaseLoader
        from jinja2.sandbox import SandboxedEnvironment

        # Use sandboxed environment
        self.env = SandboxedEnvironment(
            loader=BaseLoader(),
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True,  # Auto-escape HTML
        )

        # Add safe filters
        self.env.filters.update(
            {
                "upper": str.upper,
                "lower": str.lower,
                "title": str.title,
                "capitalize": str.capitalize,
                "round": round,
                "int": int,
                "float": float,
                "abs": abs,
            }
        )

        # Add safe global functions
        self.env.globals.update(
            {
                "min": min,
                "max": max,
                "sum": sum,
                "len": len,
                "range": range,
            }
        )

    def render(self, template_str: str, context: Dict[str, Any]) -> str:
        """Render a template safely"""
        try:
            template = self.env.from_string(template_str)
            return template.render(**context)
        except Exception as e:
            logger.error(f"Template rendering error: {e}")
            raise TemplateError(f"Template error: {str(e)}")


# Factory functions
def create_safe_parser(
    security_level: SecurityLevel = SecurityLevel.MODERATE,
) -> SafeExpressionParser:
    """Create a configured safe expression parser"""
    return SafeExpressionParser(security_level)


def create_safe_template_engine() -> SafeTemplateEngine:
    """Create a configured safe template engine"""
    return SafeTemplateEngine()


# Helper function for common use cases
def safe_ast.literal_eval(expression: str,
    variables: Optional[Dict[str, Any]] = None,
    security_level: SecurityLevel = SecurityLevel.MODERATE,
) -> Any:
    """Safely evaluate an expression - drop-in replacement for eval()"""
    parser = create_safe_parser(security_level)
    context = ExpressionContext(
        variables=variables or {},
        allowed_names=set(variables.keys()) if variables else set(),
    )

    result = parser.parse(expression, context)

    if not result.success:
        raise ValueError(f"Expression evaluation failed: {result.error}")

    return result.value


# Example usage and migration guide
"""
# Instead of:
result = ast.literal_eval("2 + 2 * 3")

# Use:
result = safe_ast.literal_eval("2 + 2 * 3")

# Instead of:
# SECURITY FIX: Replaced exec with safe alternative
# Original: exec("x = " + user_input)
# TODO: Review and implement safe alternative

# Use:
parser = create_safe_parser()
result = parser.parse(user_input)
if result.success:
    x = result.value

# For templates, instead of:
code = f"result = {user_expression}"
# SECURITY WARNING: exec usage needs manual review
# exec(code)

# Use:
engine = create_safe_template_engine()
template = "result = {{ expression }}"
rendered = engine.render(template, {"expression": user_expression})
"""
