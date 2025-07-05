"""
Child Domain Module

This module contains all child-related domain logic, entities, and services
following Clean Architecture principles.
"""

from src.domain.child.models.child_analytics import (ChildEngagementInsight,
                                                     ChildStatistics,
                                                     InteractionMetrics)
from src.domain.child.models.child_search_criteria import (AgeRange,
                                                           ChildSearchCriteria,
                                                           SearchFilters)
from src.domain.child.services.child_analytics_service import \
    ChildAnalyticsDomainService
from src.domain.child.services.child_family_service import \
    ChildFamilyDomainService
from src.domain.child.services.child_interaction_service import \
    ChildInteractionDomainService

__all__ = [
    # Models
    "ChildEngagementInsight",
    "ChildStatistics",
    "InteractionMetrics",
    "ChildSearchCriteria",
    "AgeRange",
    "SearchFilters",
    # Services
    "ChildAnalyticsDomainService",
    "ChildInteractionDomainService",
    "ChildFamilyDomainService",
]
