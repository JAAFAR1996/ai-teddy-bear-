"""
Data models for the safe expression parser.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Set

from pydantic import BaseModel, Field


class ExpressionType(Enum):
    """Enumeration for the types of expressions that can be safely evaluated."""
    ARITHMETIC = "arithmetic"
    COMPARISON = "comparison"
    LOGICAL = "logical"
    STRING = "string"
    JSON_LOGIC = "json_logic"
    TEMPLATE = "template"


class SecurityLevel(Enum):
    """Defines the security level for expression evaluation, controlling allowed operations."""
    RESTRICTED = "restricted"
    STANDARD = "standard"
    EXTENDED = "extended"


@dataclass
class ExpressionContext:
    """Provides the context for an expression evaluation, including variables and functions."""
    variables: Dict[str, Any] = field(default_factory=dict)
    functions: Dict[str, Callable] = field(default_factory=dict)
    security_level: SecurityLevel = SecurityLevel.RESTRICTED
    max_complexity: int = 10
    timeout_seconds: float = 5.0
    allowed_modules: Set[str] = field(default_factory=set)


class SafeExpressionConfig(BaseModel):
    """Configuration model for the safe expression parser."""
    default_security_level: SecurityLevel = Field(
        default=SecurityLevel.RESTRICTED)
    max_complexity_score: int = Field(
        default=10, description="Maximum allowed AST complexity score.")
    evaluation_timeout: float = Field(
        default=5.0, description="Timeout in seconds for a single evaluation.")
    enable_json_logic: bool = Field(
        default=True, description="Enable or disable the JSONLogic engine.")
    enable_templates: bool = Field(
        default=True, description="Enable or disable the template engine.")
    strict_validation: bool = Field(
        default=True, description="Enable strict validation of expressions and ASTs.")
    allowed_operators: Set[str] = Field(default_factory=lambda: {
        "Add", "Sub", "Mult", "Div", "FloorDiv", "Mod", "Pow",
        "Eq", "NotEq", "Lt", "LtE", "Gt", "GtE",
        "And", "Or", "Not", "In", "NotIn",
    })
    forbidden_patterns: List[str] = Field(default_factory=lambda: [
        r"__import__", r"eval\s*\(", r"exec\s*\(", r"open\s*\("
    ])

    class Config:
        validate_assignment = True
