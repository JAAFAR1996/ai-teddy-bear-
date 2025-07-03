"""
🎯 Moderation Service - High Cohesion Components
Refactored moderation service with EXTRACT CLASS pattern applied
"""

from .models import (
    ModerationSeverity,
    ContentCategory,
    ModerationRequest,
    ModerationContext,
    ModerationResult,
    ModerationResultData,
    ModerationRule
)

from .cache_manager import ModerationCache
from .content_analyzer import ContentAnalyzer
from .statistics import ModerationStatistics, ModerationStatsEntry
from .legacy_adapter import (
    LegacyModerationAdapter,
    LegacyModerationParams,
    ModerationMetadata
)

__all__ = [
    # Models
    "ModerationSeverity",
    "ContentCategory", 
    "ModerationRequest",
    "ModerationContext",
    "ModerationResult",
    "ModerationResultData",
    "ModerationRule",
    
    # Core Components
    "ModerationCache",
    "ContentAnalyzer",
    "ModerationStatistics",
    "ModerationStatsEntry",
    
    # Legacy Support
    "LegacyModerationAdapter",
    "LegacyModerationParams", 
    "ModerationMetadata"
]

# Version info
__version__ = "2.0.0"
__author__ = "AI Teddy Bear Team"
__description__ = "High-cohesion moderation service with EXTRACT CLASS refactoring" 