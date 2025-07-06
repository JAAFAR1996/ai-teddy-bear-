"""
Data models for the advanced content filter.
"""
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class RiskLevel(Enum):
    """Defines the assessed risk level of a piece of content."""
    SAFE = "safe"
    LOW_RISK = "low_risk"
    MEDIUM_RISK = "medium_risk"
    HIGH_RISK = "high_risk"
    CRITICAL = "critical"


class ContentCategory(Enum):
    """Categorizes content by its primary nature."""
    EDUCATIONAL = "educational"
    ENTERTAINMENT = "entertainment"
    PERSONAL = "personal"
    INAPPROPRIATE = "inappropriate"
    HARMFUL = "harmful"


@dataclass
class SafetyViolation:
    """Represents a single detected safety violation in a piece of content."""
    violation_type: str
    severity: RiskLevel
    description: str
    content_excerpt: str
    timestamp: float = field(default_factory=time.time)
    requires_parent_notification: bool = False


@dataclass
class ContentAnalysisResult:
    """Encapsulates the complete result of a content safety analysis."""
    is_safe: bool
    risk_level: RiskLevel
    confidence_score: float
    content_category: ContentCategory
    violations: List[SafetyViolation]
    modifications: List[str]
    safe_alternative: Optional[str]
    safety_recommendations: List[str]
    parent_notification_required: bool
    processing_time_ms: float
