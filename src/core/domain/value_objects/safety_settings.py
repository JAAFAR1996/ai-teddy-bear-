"""
🛡️ Safety Settings Value Object
===============================

Safety settings encapsulate all safety-related configurations and rules
for child interactions with the AI Teddy Bear system.
"""

from dataclasses import dataclass
from typing import List, Dict, Set, Optional
from datetime import datetime, time, timedelta
from enum import Enum


class ContentFilterLevel(Enum):
    """Content filtering strictness levels"""
    MINIMAL = "minimal"      # Ages 11-12, basic filtering
    MODERATE = "moderate"    # Ages 7-10, standard filtering  
    STRICT = "strict"        # Ages 5-6, enhanced filtering
    MAXIMUM = "maximum"      # Ages 3-4, maximum protection


class TimeRestrictionType(Enum):
    """Types of time-based restrictions"""
    DAILY_LIMIT = "daily_limit"
    SESSION_LIMIT = "session_limit"
    QUIET_HOURS = "quiet_hours"
    BEDTIME = "bedtime"


@dataclass(frozen=True)
class TimeRestriction:
    """Value object for time-based restrictions"""
    restriction_type: TimeRestrictionType
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    duration_minutes: Optional[int] = None
    days_of_week: Set[int] = None  # 0=Monday, 6=Sunday
    
    def __post_init__(self):
        """Validate time restriction parameters"""
        if self.restriction_type in [TimeRestrictionType.QUIET_HOURS, TimeRestrictionType.BEDTIME]:
            if not (self.start_time and self.end_time):
                raise ValueError(f"{self.restriction_type.value} requires start_time and end_time")
        
        if self.restriction_type in [TimeRestrictionType.DAILY_LIMIT, TimeRestrictionType.SESSION_LIMIT]:
            if not self.duration_minutes or self.duration_minutes <= 0:
                raise ValueError(f"{self.restriction_type.value} requires positive duration_minutes")


@dataclass(frozen=True)
class SafetySettings:
    """
    Value Object representing comprehensive safety settings for a child.
    
    This encapsulates all safety rules, restrictions, and configurations
    to ensure appropriate and safe interactions.
    """
    
    # Content filtering
    content_filter_level: ContentFilterLevel
    blocked_topics: Set[str]
    allowed_topics: Set[str]
    custom_content_rules: Dict[str, bool]
    
    # Time restrictions
    time_restrictions: List[TimeRestriction]
    max_daily_minutes: int
    max_session_minutes: int
    
    # Interaction limits
    max_conversations_per_day: int
    cooldown_between_sessions: int  # minutes
    require_parent_approval: bool
    
    # Privacy settings
    record_conversations: bool
    share_analytics: bool
    data_retention_days: int
    
    # Emergency settings
    emergency_contact_enabled: bool
    parent_notification_triggers: Set[str]
    auto_escalation_keywords: Set[str]
    
    # Customization limits
    allow_voice_changes: bool
    allow_personality_adjustments: bool
    restrict_advanced_features: bool
    
    # Metadata
    created_by_parent: bool
    last_updated: Optional[datetime] = None
    settings_version: str = "v2025.1"

    def __post_init__(self):
        """Validate safety settings"""
        if self.max_daily_minutes <= 0:
            raise ValueError("Daily time limit must be positive")
        
        if self.max_session_minutes <= 0:
            raise ValueError("Session time limit must be positive")
        
        if self.max_session_minutes > self.max_daily_minutes:
            raise ValueError("Session limit cannot exceed daily limit")
        
        if self.data_retention_days < 0:
            raise ValueError("Data retention days cannot be negative")

    @classmethod
    def create_for_age(cls, age: int, parent_preferences: Optional[Dict] = None) -> 'SafetySettings':
        """Create age-appropriate safety settings"""
        
        # Age-based default settings
        age_settings = {
            (3, 4): {
                "content_filter_level": ContentFilterLevel.MAXIMUM,
                "max_daily_minutes": 30,
                "max_session_minutes": 10,
                "max_conversations_per_day": 3,
                "require_parent_approval": True,
                "restrict_advanced_features": True
            },
            (5, 6): {
                "content_filter_level": ContentFilterLevel.STRICT,
                "max_daily_minutes": 45,
                "max_session_minutes": 15,
                "max_conversations_per_day": 4,
                "require_parent_approval": True,
                "restrict_advanced_features": True
            },
            (7, 10): {
                "content_filter_level": ContentFilterLevel.MODERATE,
                "max_daily_minutes": 60,
                "max_session_minutes": 20,
                "max_conversations_per_day": 6,
                "require_parent_approval": False,
                "restrict_advanced_features": False
            },
            (11, 12): {
                "content_filter_level": ContentFilterLevel.MINIMAL,
                "max_daily_minutes": 90,
                "max_session_minutes": 30,
                "max_conversations_per_day": 8,
                "require_parent_approval": False,
                "restrict_advanced_features": False
            }
        }
        
        # Find age-appropriate settings
        settings = age_settings.get((11, 12))  # Default to oldest
        for age_range, config in age_settings.items():
            if age_range[0] <= age <= age_range[1]:
                settings = config
                break
        
        # Apply parent preferences if provided
        if parent_preferences:
            settings.update(parent_preferences)
        
        # Create default time restrictions
        default_restrictions = [
            TimeRestriction(
                restriction_type=TimeRestrictionType.QUIET_HOURS,
                start_time=time(21, 0),  # 9 PM
                end_time=time(7, 0),     # 7 AM
                days_of_week={0, 1, 2, 3, 4}  # Weekdays
            ),
            TimeRestriction(
                restriction_type=TimeRestrictionType.BEDTIME,
                start_time=time(20, 0),  # 8 PM
                end_time=time(8, 0),     # 8 AM
                days_of_week={5, 6}      # Weekends
            )
        ]
        
        return cls(
            content_filter_level=settings["content_filter_level"],
            blocked_topics=cls._get_blocked_topics_for_age(age),
            allowed_topics=cls._get_allowed_topics_for_age(age),
            custom_content_rules={},
            time_restrictions=default_restrictions,
            max_daily_minutes=settings["max_daily_minutes"],
            max_session_minutes=settings["max_session_minutes"],
            max_conversations_per_day=settings["max_conversations_per_day"],
            cooldown_between_sessions=5,
            require_parent_approval=settings["require_parent_approval"],
            record_conversations=True,
            share_analytics=False,
            data_retention_days=90,
            emergency_contact_enabled=True,
            parent_notification_triggers={"inappropriate_content", "distress_detected", "safety_violation"},
            auto_escalation_keywords={"help", "scared", "hurt", "emergency"},
            allow_voice_changes=not settings["restrict_advanced_features"],
            allow_personality_adjustments=not settings["restrict_advanced_features"],
            restrict_advanced_features=settings["restrict_advanced_features"],
            created_by_parent=True,
            last_updated=datetime.utcnow()
        )

    @classmethod
    def create_custom(
        cls,
        content_filter_level: ContentFilterLevel,
        max_daily_minutes: int,
        max_session_minutes: int,
        **kwargs
    ) -> 'SafetySettings':
        """Create custom safety settings with validation"""
        
        defaults = {
            "blocked_topics": set(),
            "allowed_topics": set(),
            "custom_content_rules": {},
            "time_restrictions": [],
            "max_conversations_per_day": 10,
            "cooldown_between_sessions": 5,
            "require_parent_approval": False,
            "record_conversations": True,
            "share_analytics": False,
            "data_retention_days": 90,
            "emergency_contact_enabled": True,
            "parent_notification_triggers": {"safety_violation"},
            "auto_escalation_keywords": {"help", "emergency"},
            "allow_voice_changes": True,
            "allow_personality_adjustments": True,
            "restrict_advanced_features": False,
            "created_by_parent": True,
            "last_updated": datetime.utcnow()
        }
        
        defaults.update(kwargs)
        
        return cls(
            content_filter_level=content_filter_level,
            max_daily_minutes=max_daily_minutes,
            max_session_minutes=max_session_minutes,
            **defaults
        )

    @staticmethod
    def _get_blocked_topics_for_age(age: int) -> Set[str]:
        """Get age-appropriate blocked topics"""
        
        base_blocked = {
            "violence", "weapons", "drugs", "alcohol", "gambling", 
            "adult_content", "horror", "death", "politics"
        }
        
        if age <= 6:
            base_blocked.update({
                "scary_stories", "monsters", "dark_themes", 
                "complex_emotions", "relationship_drama"
            })
        
        if age <= 8:
            base_blocked.update({
                "romantic_content", "dating", "advanced_science"
            })
        
        return base_blocked

    @staticmethod
    def _get_allowed_topics_for_age(age: int) -> Set[str]:
        """Get age-appropriate allowed topics"""
        
        base_allowed = {
            "animals", "nature", "colors", "shapes", "numbers",
            "family", "friends", "school", "games", "toys"
        }
        
        if age >= 5:
            base_allowed.update({
                "basic_science", "simple_history", "geography",
                "art", "music", "sports"
            })
        
        if age >= 7:
            base_allowed.update({
                "advanced_science", "technology", "space",
                "different_cultures", "environmental_topics"
            })
        
        if age >= 10:
            base_allowed.update({
                "current_events", "social_issues", "philosophy",
                "career_topics", "life_skills"
            })
        
        return base_allowed

    def can_start_conversation(self, current_time: datetime = None) -> bool:
        """Check if child can start a new conversation"""
        if current_time is None:
            current_time = datetime.utcnow()
        
        # Check time restrictions
        current_time_only = current_time.time()
        current_weekday = current_time.weekday()
        
        for restriction in self.time_restrictions:
            if restriction.restriction_type in [TimeRestrictionType.QUIET_HOURS, TimeRestrictionType.BEDTIME]:
                if restriction.days_of_week and current_weekday not in restriction.days_of_week:
                    continue
                
                # Handle time ranges that cross midnight
                if restriction.start_time > restriction.end_time:
                    # Range crosses midnight (e.g., 21:00 to 07:00)
                    if current_time_only >= restriction.start_time or current_time_only <= restriction.end_time:
                        return False
                else:
                    # Normal range (e.g., 08:00 to 17:00)
                    if restriction.start_time <= current_time_only <= restriction.end_time:
                        return False
        
        return True

    def is_topic_allowed(self, topic: str) -> bool:
        """Check if a topic is allowed based on safety settings"""
        topic_lower = topic.lower()
        
        # Check explicitly blocked topics
        if any(blocked in topic_lower for blocked in self.blocked_topics):
            return False
        
        # Check custom content rules
        for rule_topic, is_allowed in self.custom_content_rules.items():
            if rule_topic.lower() in topic_lower:
                return is_allowed
        
        # Check explicitly allowed topics
        if any(allowed in topic_lower for allowed in self.allowed_topics):
            return True
        
        # Default based on content filter level
        if self.content_filter_level == ContentFilterLevel.MAXIMUM:
            return False  # Only explicitly allowed topics
        
        return True  # Allow by default for less strict levels

    def should_notify_parent(self, trigger: str) -> bool:
        """Check if parent should be notified for given trigger"""
        return trigger in self.parent_notification_triggers

    def should_escalate(self, message: str) -> bool:
        """Check if conversation should be escalated to human oversight"""
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in self.auto_escalation_keywords)

    def with_updated_time_limits(self, daily_minutes: int, session_minutes: int) -> 'SafetySettings':
        """Create new SafetySettings with updated time limits"""
        return self.__class__(
            content_filter_level=self.content_filter_level,
            blocked_topics=self.blocked_topics,
            allowed_topics=self.allowed_topics,
            custom_content_rules=self.custom_content_rules,
            time_restrictions=self.time_restrictions,
            max_daily_minutes=daily_minutes,
            max_session_minutes=session_minutes,
            max_conversations_per_day=self.max_conversations_per_day,
            cooldown_between_sessions=self.cooldown_between_sessions,
            require_parent_approval=self.require_parent_approval,
            record_conversations=self.record_conversations,
            share_analytics=self.share_analytics,
            data_retention_days=self.data_retention_days,
            emergency_contact_enabled=self.emergency_contact_enabled,
            parent_notification_triggers=self.parent_notification_triggers,
            auto_escalation_keywords=self.auto_escalation_keywords,
            allow_voice_changes=self.allow_voice_changes,
            allow_personality_adjustments=self.allow_personality_adjustments,
            restrict_advanced_features=self.restrict_advanced_features,
            created_by_parent=self.created_by_parent,
            last_updated=datetime.utcnow(),
            settings_version=self.settings_version
        )

    def __str__(self) -> str:
        return (f"SafetySettings(filter={self.content_filter_level.value}, "
                f"daily_limit={self.max_daily_minutes}min, "
                f"session_limit={self.max_session_minutes}min)")

    def __repr__(self) -> str:
        return (f"SafetySettings(content_filter_level={self.content_filter_level}, "
                f"max_daily_minutes={self.max_daily_minutes}, "
                f"max_session_minutes={self.max_session_minutes}, "
                f"require_parent_approval={self.require_parent_approval})") 