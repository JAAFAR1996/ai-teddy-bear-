# child_repository.py - Enhanced repository for child profiles

from abc import abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from src.core.domain.entities.child import (
    Child,
    ChildPreferences,
    DevelopmentMilestone,
    Language,
    LearningLevel,
)
from src.infrastructure.persistence.base import (
    BaseRepository,
    BulkOperationResult,
    QueryOptions,
    SearchCriteria,
    SortOrder,
)


class ChildRepository(BaseRepository[Child, str]):
    """
    Abstract repository interface for managing child profiles.
    Defines the contract for all child repository implementations.
    """

    @abstractmethod
    async def find_by_name(self, name: str, fuzzy: bool = False) -> List[Child]:
        """Find children by name with optional fuzzy matching."""
        pass

    @abstractmethod
    async def find_by_parent(self, parent_id: str) -> List[Child]:
        """Find all children belonging to a parent."""
        pass

    @abstractmethod
    async def find_by_age_range(
        self, min_age: int, max_age: int, include_boundaries: bool = True
    ) -> List[Child]:
        """Find children within a specific age range."""
        pass

    @abstractmethod
    async def find_by_learning_level(self, level: LearningLevel) -> List[Child]:
        """Find children by learning level."""
        pass

    @abstractmethod
    async def find_by_language(self, language: Language) -> List[Child]:
        """Find children by preferred language."""
        pass

    @abstractmethod
    async def find_by_interests(
        self,
        interests: List[str],
        match_all: bool = False,
        min_match_count: Optional[int] = None,
    ) -> List[Child]:
        """Find children with matching interests."""
        pass

    @abstractmethod
    async def get_children_with_recent_interactions(
        self, days: int = 7, min_interactions: Optional[int] = None
    ) -> List[Child]:
        """Get children who have had recent interactions."""
        pass

    @abstractmethod
    async def get_inactive_children(self, days: int = 30) -> List[Child]:
        """Get children who haven't interacted recently."""
        pass

    @abstractmethod
    async def get_children_by_milestone(
        self, milestone_name: str, achieved: bool = True
    ) -> List[Child]:
        """Get children who have or have not achieved a specific milestone."""
        pass

    @abstractmethod
    async def update_child_preferences(
        self, child_id: str, preferences: ChildPreferences
    ) -> Optional[Child]:
        """Update a child's preferences."""
        pass

    @abstractmethod
    async def add_milestone(
        self, child_id: str, milestone: DevelopmentMilestone
    ) -> Optional[Child]:
        """Add a developmental milestone to a child's record."""
        pass

    @abstractmethod
    async def update_learning_progress(
        self,
        child_id: str,
        new_concepts: List[str],
        completed_goals: List[str],
    ) -> Optional[Child]:
        """Update a child's learning progress."""
        pass

    @abstractmethod
    async def record_interaction(
        self,
        child_id: str,
        duration_seconds: int,
        activity_type: Optional[str] = None,
    ) -> Optional[Child]:
        """Record an interaction session for a child."""
        pass

    @abstractmethod
    async def bulk_update_age(self) -> BulkOperationResult:
        """Update ages for all children based on their date of birth."""
        pass

    @abstractmethod
    async def search_children(
        self,
        query: Optional[str] = None,
        filters: Optional[dict[str, Any]] = None,
        sort_by: str = "name",
        sort_order: SortOrder = SortOrder.ASC,
        page: int = 1,
        page_size: int = 20,
    ) -> dict[str, Any]:
        """Perform a comprehensive search for children with filtering, sorting, and pagination."""
        pass

    # The following methods are considered business logic or analytics
    # and have been removed from the repository interface. They should be
    # implemented in domain or application services.
    # - find_with_similar_interests
    # - get_children_by_interaction_time
    # - get_children_exceeding_time_limit
    # - get_children_ready_for_level_up
    # - get_statistics
    # - get_trending_interests
    # - cleanup_old_data
    # - validate_all_profiles
