"""
Data models for observability and metrics.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List


class SafetyViolationType(Enum):
    """Types of child safety violations"""

    INAPPROPRIATE_CONTENT = "inappropriate_content"
    PERSONAL_INFO_REQUEST = "personal_info_request"
    TOXIC_LANGUAGE = "toxic_language"
    AGE_INAPPROPRIATE = "age_inappropriate"
    EMERGENCY_TRIGGER = "emergency_trigger"
    PARENTAL_BYPASS_ATTEMPT = "parental_bypass_attempt"
    UNKNOWN_ADULT_CONTACT = "unknown_adult_contact"


class SeverityLevel(Enum):
    """Severity levels for violations and alerts"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class ChildInteractionMetrics:
    """Metrics for a single child interaction"""

    child_id: str
    age_group: str
    interaction_type: str
    duration_ms: float
    safety_score: float
    toxicity_score: float
    sentiment_score: float
    response_time_ms: float
    success: bool
    violations: List[SafetyViolationType]


@dataclass
class AIInteractionMetrics:
    """Metrics for a single AI interaction"""
    response_time_ms: float
    tokens_used: int
    model_name: str
    temperature: float
    accuracy_score: float
    quality_score: float
    context_utilization: float
    cost_usd: float
    child_context: Dict[str, Any]
