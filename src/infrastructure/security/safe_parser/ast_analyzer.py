"""
AST analysis and validation for security and complexity.
"""
import ast
import logging
import re
from typing import List

from .models import SafeExpressionConfig

logger = logging.getLogger(__name__)


class ASTComplexityAnalyzer:
    """Analyzes the complexity of an AST to prevent resource exhaustion attacks."""

    def __init__(self, config: SafeExpressionConfig):
        self.config = config
        self.complexity_weights = {
            ast.BinOp: 1, ast.UnaryOp: 1, ast.Compare: 1, ast.BoolOp: 1,
            ast.Call: 3, ast.Attribute: 2, ast.Subscript: 2,
            ast.ListComp: 5, ast.DictComp: 5, ast.GeneratorExp: 5,
            ast.Lambda: 3, ast.IfExp: 2,
        }

    def analyze_complexity(self, node: ast.AST) -> int:
        """Calculates a complexity score for a given AST node."""
        return sum(self.complexity_weights.get(type(child), 0) for child in ast.walk(node))

    def is_complexity_acceptable(self, node: ast.AST) -> bool:
        """Checks if the AST's complexity is within the configured limit."""
        complexity = self.analyze_complexity(node)
        is_acceptable = complexity <= self.config.max_complexity_score
        if not is_acceptable:
            logger.warning("Expression complexity exceeded",
                           score=complexity,
                           limit=self.config.max_complexity_score)
        return is_acceptable


class SecurityValidator:
    """Validates expressions and their ASTs for potential security risks."""

    def __init__(self, config: SafeExpressionConfig):
        self.config = config
        self.forbidden_patterns = [re.compile(
            p, re.IGNORECASE) for p in config.forbidden_patterns]
        self.dangerous_call_names = {"eval", "exec",
                                     "compile", "open", "file", "__import__"}

    def validate_expression_string(self, expression: str) -> bool:
        """Performs a preliminary security check on the raw expression string."""
        if any(pattern.search(expression) for pattern in self.forbidden_patterns):
            logger.warning("Forbidden pattern detected in expression string.")
            return False
        return True

    def validate_ast(self, node: ast.AST) -> bool:
        """Recursively validates an entire AST for disallowed nodes."""
        for child_node in ast.walk(node):
            if isinstance(child_node, (ast.Import, ast.ImportFrom)):
                logger.warning("Import statement detected in AST.")
                return False
            if isinstance(child_node, ast.Call) and self._is_dangerous_call(child_node):
                return False
            if isinstance(child_node, ast.Attribute) and self._is_dangerous_attribute(child_node):
                return False
        return True

    def _is_dangerous_call(self, node: ast.Call) -> bool:
        """Checks if a function call is on the denylist."""
        if isinstance(node.func, ast.Name) and node.func.id in self.dangerous_call_names:
            logger.warning(
                f"Dangerous function call detected in AST: {node.func.id}")
            return True
        return False

    def _is_dangerous_attribute(self, node: ast.Attribute) -> bool:
        """Checks for access to potentially dangerous attributes like '__' methods."""
        if node.attr.startswith("__") and node.attr.endswith("__"):
            logger.warning(f"Access to dunder method detected: {node.attr}")
            return True
        return False
