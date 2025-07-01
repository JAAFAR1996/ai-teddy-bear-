"""
Moderation Types and Data Classes
Contains all type definitions for the moderation system
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple

from sqlalchemy import JSON, Boolean, Column, DateTime, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class ModerationSeverity(Enum):
    """Severity levels for moderation"""

    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ContentCategory(Enum):
    """Content categories for moderation"""

    VIOLENCE = "violence"
    SEXUAL = "sexual"
    HATE_SPEECH = "hate_speech"
    SELF_HARM = "self_harm"
    PROFANITY = "profanity"
    PERSONAL_INFO = "personal_info"
    BULLYING = "bullying"
    DRUGS = "drugs"
    WEAPONS = "weapons"
    SCARY_CONTENT = "scary_content"
    AGE_INAPPROPRIATE = "age_inappropriate"
    SPAM = "spam"
    PHISHING = "phishing"


@dataclass
class ModerationResult:
    """Enhanced moderation result with detailed information"""

    is_safe: bool
    severity: ModerationSeverity
    flagged_categories: List[ContentCategory] = field(default_factory=list)
    confidence_scores: Dict[ContentCategory, float] = field(default_factory=dict)
    matched_rules: List[str] = field(default_factory=list)
    context_notes: List[str] = field(default_factory=list)
    alternative_response: Optional[str] = None
    should_alert_parent: bool = False
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def overall_score(self) -> float:
        """Calculate overall moderation score"""
        if not self.confidence_scores:
            return 0.0
        return max(self.confidence_scores.values())


@dataclass
class ModerationRule:
    """Custom moderation rule"""

    id: str
    name: str
    description: str
    pattern: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    category: ContentCategory = ContentCategory.AGE_INAPPROPRIATE
    severity: ModerationSeverity = ModerationSeverity.MEDIUM
    age_range: Tuple[int, int] = (0, 18)
    languages: List[str] = field(default_factory=lambda: ["en", "ar"])
    is_regex: bool = False
    context_required: bool = False
    enabled: bool = True
    parent_override: bool = False
    action: str = "block"  # block, warn, log


class ModerationLog(Base):
    """Database model for moderation logs"""

    __tablename__ = "moderation_logs"

    id = Column(String, primary_key=True)
    session_id = Column(String)
    user_id = Column(String)
    timestamp = Column(DateTime, default=datetime.now)
    content = Column(String)
    result = Column(JSON)
    severity = Column(String)
    categories = Column(JSON)
    action_taken = Column(String)
    parent_notified = Column(Boolean, default=False)


# Helper functions for creating rules
def create_age_appropriate_rule(
    name: str,
    keywords: List[str],
    min_age: int,
    max_age: int = 18,
    severity: ModerationSeverity = ModerationSeverity.MEDIUM,
) -> ModerationRule:
    """Create an age-appropriate content rule"""
    return ModerationRule(
        id=f"age_rule_{name.lower().replace(' ', '_')}",
        name=name,
        description=f"Age-appropriate rule for {min_age}-{max_age} years",
        keywords=keywords,
        category=ContentCategory.AGE_INAPPROPRIATE,
        severity=severity,
        age_range=(min_age, max_age),
    )


def create_topic_filter_rule(
    topic: str,
    keywords: List[str],
    category: ContentCategory,
    severity: ModerationSeverity = ModerationSeverity.MEDIUM,
) -> ModerationRule:
    """Create a topic-based filter rule"""
    return ModerationRule(
        id=f"topic_rule_{topic.lower().replace(' ', '_')}",
        name=f"{topic} Filter",
        description=f"Filter content related to {topic}",
        keywords=keywords,
        category=category,
        severity=severity,
    ) 