"""
📋 Shared Moderation Models
Common data structures used across moderation components
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from enum import Enum


class ModerationSeverity(Enum):
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ContentCategory(Enum):
    PROFANITY = "profanity"
    VIOLENCE = "violence"
    ADULT_CONTENT = "adult_content"
    PERSONAL_INFO = "personal_info"
    SCARY_CONTENT = "scary_content"
    AGE_INAPPROPRIATE = "age_inappropriate"
    HARMFUL_CONTENT = "harmful_content"
    CYBERBULLYING = "cyberbullying"


@dataclass
class ModerationRequest:
    """Request object for content moderation"""

    content: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    age: int = 10
    language: str = "en"
    context: Optional[List] = None


@dataclass
class ModerationContext:
    """Context settings for moderation request"""

    use_cache: bool = True
    enable_openai: bool = True
    enable_azure: bool = False
    enable_google: bool = False
    strict_mode: bool = False


@dataclass
class ModerationResultData:
    """Parameter object for ModerationResult construction"""

    is_safe: bool = True
    severity: ModerationSeverity = ModerationSeverity.SAFE
    flagged_categories: Optional[List] = None
    confidence_scores: Optional[Dict] = None
    matched_rules: Optional[List] = None

    def get_flagged_categories(self) -> List:
        return self.flagged_categories or []

    def get_confidence_scores(self) -> Dict:
        return self.confidence_scores or {}

    def get_matched_rules(self) -> List:
        return self.matched_rules or []


class ModerationResult:
    """Result object for moderation analysis"""

    def __init__(self, data: Optional[ModerationResultData] = None):
        """Initialize with parameter object"""
        if data is None:
            data = ModerationResultData()

        self.is_safe = data.is_safe
        self.severity = data.severity
        self.flagged_categories = data.get_flagged_categories()
        self.confidence_scores = data.get_confidence_scores()
        self.matched_rules = data.get_matched_rules()


@dataclass
class ModerationRule:
    """Rule definition for content moderation"""

    name: str
    pattern: str
    severity: ModerationSeverity
    category: ContentCategory
    enabled: bool = True
    description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "pattern": self.pattern,
            "severity": self.severity.value,
            "category": self.category.value,
            "enabled": self.enabled,
            "description": self.description,
        }
