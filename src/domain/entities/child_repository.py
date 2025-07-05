# child_repository.py - Enhanced repository for child profiles

from abc import abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from src.core.domain.entities.child import (Child, ChildPreferences,
                                            DevelopmentMilestone,
                                            Language,
                                            LearningLevel)
from src.infrastructure.persistence.base import (BaseRepository,
                                                 BulkOperationResult,
                                                 QueryOptions, SearchCriteria,
                                                 SortOrder)


class ChildRepository(BaseRepository[Child, str]):
    """
    Enhanced repository for managing child profiles with advanced features
    """

    def __init__(self):
        super().__init__(Child)

    # Basic Search Methods

    @abstractmethod
    async def find_by_name(self, name: str, fuzzy: bool = False) -> List[Child]:
        """
        Find children by name with optional fuzzy matching

        Args:
            name: Child's name or partial name
            fuzzy: Enable fuzzy/partial matching

        Returns:
            List of matching children
        """
        pass

    @abstractmethod
    async def find_by_parent(self, parent_id: str) -> List[Child]:
        """
        Find all children belonging to a parent

        Args:
            parent_id: Parent's unique identifier

        Returns:
            List of children
        """
        pass

    @abstractmethod
    async def find_by_age_range(
        self, min_age: int, max_age: int, include_boundaries: bool = True
    ) -> List[Child]:
        """
        Find children within a specific age range

        Args:
            min_age: Minimum age
            max_age: Maximum age
            include_boundaries: Include min and max ages

        Returns:
            List of children in age range
        """
        pass

    @abstractmethod
    async def find_by_learning_level(self, level: LearningLevel) -> List[Child]:
        """
        Find children by learning level

        Args:
            level: Learning level

        Returns:
            List of children at specified level
        """
        pass

    @abstractmethod
    async def find_by_language(self, language: Language) -> List[Child]:
        """
        Find children by preferred language

        Args:
            language: Preferred language

        Returns:
            List of children with language preference
        """
        pass

    # Interest-based Queries

    @abstractmethod
    async def find_by_interests(
        self,
        interests: List[str],
        match_all: bool = False,
        min_match_count: Optional[int] = None,
    ) -> List[Child]:
        """
        Find children with matching interests

        Args:
            interests: List of interests to match
            match_all: Require all interests to match
            min_match_count: Minimum number of interests to match

        Returns:
            List of children with matching interests
        """
        pass

    async def find_with_similar_interests(
        self, child_id: str, min_similarity: float = 0.5
    ) -> List[Tuple[Child, float]]:
        """
        Find children with similar interests to a given child

        Args:
            child_id: Reference child ID
            min_similarity: Minimum similarity score (0-1)

        Returns:
            List of (child, similarity_score) tuples
        """
        reference_child = await self.get(child_id)
        if not reference_child:
            return []

        all_children = await self.list()
        similar_children = []

        for child in all_children:
            if child.id == child_id:
                continue

            similarity = self._calculate_interest_similarity(
                reference_child.interests, child.interests
            )

            if similarity >= min_similarity:
                similar_children.append((child, similarity))

        # Sort by similarity descending
        similar_children.sort(key=lambda x: x[1], reverse=True)
        return similar_children

    # Activity and Interaction Queries

    @abstractmethod
    async def get_children_with_recent_interactions(
        self, days: int = 7, min_interactions: Optional[int] = None
    ) -> List[Child]:
        """
        Get children who have had recent interactions

        Args:
            days: Number of days to look back
            min_interactions: Minimum number of interactions

        Returns:
            List of active children
        """
        pass

    @abstractmethod
    async def get_inactive_children(self, days: int = 30) -> List[Child]:
        """
        Get children who haven't interacted recently

        Args:
            days: Days of inactivity threshold

        Returns:
            List of inactive children
        """
        pass

    async def get_children_by_interaction_time(
        self, min_time: Optional[int] = None, max_time: Optional[int] = None
    ) -> List[Child]:
        """
        Get children by daily interaction time limits

        Args:
            min_time: Minimum daily time in seconds
            max_time: Maximum daily time in seconds

        Returns:
            List of children within time constraints
        """
        criteria = []

        if min_time is not None:
            criteria.append(
                SearchCriteria(
                    field="max_daily_interaction_time", operator="gte", value=min_time
                )
            )

        if max_time is not None:
            criteria.append(
                SearchCriteria(
                    field="max_daily_interaction_time", operator="lte", value=max_time
                )
            )

        return await self.search(criteria) if criteria else []

    async def get_children_exceeding_time_limit(
        self, current_usage: Dict[str, int]
    ) -> List[Tuple[Child, int]]:
        """
        Get children who have exceeded their time limits

        Args:
            current_usage: Dict of child_id -> seconds used today

        Returns:
            List of (child, excess_seconds) tuples
        """
        exceeding = []

        for child_id, used_seconds in current_usage.items():
            child = await self.get(child_id)
            if child and used_seconds > child.max_daily_interaction_time:
                excess = used_seconds - child.max_daily_interaction_time
                exceeding.append((child, excess))

        return exceeding

    # Learning and Development Queries

    async def get_children_by_milestone(
        self, milestone_name: str, achieved: bool = True
    ) -> List[Child]:
        """
        Get children who have/haven't achieved a milestone

        Args:
            milestone_name: Name of the milestone
            achieved: Whether to find those who achieved it

        Returns:
            List of children
        """
        all_children = await self.list()
        matching = []

        for child in all_children:
            has_milestone = any(m.name == milestone_name for m in child.milestones)

            if has_milestone == achieved:
                matching.append(child)

        return matching

    async def get_children_ready_for_level_up(self) -> List[Child]:
        """
        Get children who might be ready for next learning level

        Returns:
            List of children ready for advancement
        """
        candidates = []

        all_children = await self.list()
        for child in all_children:
            # Check if child has many concepts learned for their level
            if len(child.known_concepts) > 20:  # Threshold
                # Check if age appropriate for next level
                if self._should_advance_level(child):
                    candidates.append(child)

        return candidates

    # Update Methods

    async def update_child_preferences(
        self, child_id: str, preferences: ChildPreferences
    ) -> Optional[Child]:
        """
        Update child's preferences

        Args:
            child_id: Child's ID
            preferences: New preferences

        Returns:
            Updated child or None
        """
        child = await self.get(child_id)
        if child:
            child.preferences = preferences
            child.updated_at = datetime.now()
            return await self.update(child)
        return None

    async def add_milestone(
        self, child_id: str, milestone: DevelopmentMilestone
    ) -> Optional[Child]:
        """
        Add a milestone achievement

        Args:
            child_id: Child's ID
            milestone: Milestone to add

        Returns:
            Updated child or None
        """
        child = await self.get(child_id)
        if child:
            child.milestones.append(milestone)
            child.updated_at = datetime.now()
            return await self.update(child)
        return None

    async def update_learning_progress(
        self, child_id: str, new_concepts: List[str], completed_goals: List[str]
    ) -> Optional[Child]:
        """
        Update child's learning progress

        Args:
            child_id: Child's ID
            new_concepts: Newly learned concepts
            completed_goals: Completed learning goals

        Returns:
            Updated child or None
        """
        child = await self.get(child_id)
        if not child:
            return None

        # Add new concepts
        for concept in new_concepts:
            if concept not in child.known_concepts:
                child.known_concepts.append(concept)

        # Remove completed goals
        child.learning_goals = [
            goal for goal in child.learning_goals if goal not in completed_goals
        ]

        child.updated_at = datetime.now()
        return await self.update(child)

    async def record_interaction(
        self, child_id: str, duration_seconds: int, activity_type: Optional[str] = None
    ) -> Optional[Child]:
        """
        Record an interaction session

        Args:
            child_id: Child's ID
            duration_seconds: Session duration
            activity_type: Type of activity

        Returns:
            Updated child or None
        """
        child = await self.get(child_id)
        if not child:
            return None

        child.total_interaction_time += duration_seconds
        child.total_sessions += 1
        child.last_interaction = datetime.now()

        if activity_type:
            child.track_activity(activity_type)

        return await self.update(child)

    # Bulk Operations

    async def bulk_update_age(self) -> BulkOperationResult:
        """
        Update ages for all children based on birthdate

        Returns:
            Bulk operation result
        """
        children = await self.list()
        updated_children = []

        for child in children:
            if child.date_of_birth:
                old_age = child.age
                new_age = child.calculate_age()

                if old_age != new_age:
                    updated_children.append(child)

        return await self.bulk_update(updated_children)

    async def reset_daily_usage(self) -> int:
        """
        Reset daily usage for all children

        Returns:
            Number of children reset
        """
        # This would typically be implemented in the concrete repository
        # to efficiently update all records
        pass

    # Statistics and Analytics

    async def get_statistics(self) -> Dict[str, Any]:
        """
        Get repository statistics

        Returns:
            Statistics dictionary
        """
        total_children = await self.count()

        # Age distribution
        age_groups = {"0-5": 0, "6-10": 0, "11-15": 0, "16+": 0}

        # Language distribution
        language_dist = {}

        # Learning level distribution
        level_dist = {}

        # Activity statistics
        total_interaction_time = 0
        total_sessions = 0

        all_children = await self.list()
        for child in all_children:
            # Age groups
            if child.age <= 5:
                age_groups["0-5"] += 1
            elif child.age <= 10:
                age_groups["6-10"] += 1
            elif child.age <= 15:
                age_groups["11-15"] += 1
            else:
                age_groups["16+"] += 1

            # Languages
            lang = child.preferences.language.value
            language_dist[lang] = language_dist.get(lang, 0) + 1

            # Learning levels
            level = child.learning_level.value
            level_dist[level] = level_dist.get(level, 0) + 1

            # Activity
            total_interaction_time += child.total_interaction_time
            total_sessions += child.total_sessions

        return {
            "total_children": total_children,
            "age_distribution": age_groups,
            "language_distribution": language_dist,
            "learning_level_distribution": level_dist,
            "total_interaction_hours": total_interaction_time / 3600,
            "total_sessions": total_sessions,
            "average_sessions_per_child": total_sessions / max(total_children, 1),
            "active_children_7d": len(
                await self.get_children_with_recent_interactions(7)
            ),
            "inactive_children_30d": len(await self.get_inactive_children(30)),
        }

    async def get_trending_interests(self, limit: int = 10) -> List[Tuple[str, int]]:
        """
        Get most popular interests

        Args:
            limit: Number of top interests

        Returns:
            List of (interest, count) tuples
        """
        interest_counts = {}

        all_children = await self.list()
        for child in all_children:
            for interest in child.interests:
                interest_counts[interest] = interest_counts.get(interest, 0) + 1

        # Sort by count descending
        sorted_interests = sorted(
            interest_counts.items(), key=lambda x: x[1], reverse=True
        )

        return sorted_interests[:limit]

    # Search and Filter Builders

    async def search_children(
        self,
        query: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: str = "name",
        sort_order: SortOrder = SortOrder.ASC,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        """
        Advanced search with pagination

        Args:
            query: Search query for name
            filters: Additional filters
            sort_by: Sort field
            sort_order: Sort direction
            page: Page number
            page_size: Items per page

        Returns:
            Paginated search results
        """
        # Build search criteria
        criteria = []

        if query:
            criteria.append(
                SearchCriteria(field="name", operator="ilike", value=f"%{query}%")
            )

        if filters:
            for field, value in filters.items():
                if isinstance(value, dict):
                    # Range query
                    if "min" in value:
                        criteria.append(
                            SearchCriteria(
                                field=field, operator="gte", value=value["min"]
                            )
                        )
                    if "max" in value:
                        criteria.append(
                            SearchCriteria(
                                field=field, operator="lte", value=value["max"]
                            )
                        )
                else:
                    criteria.append(
                        SearchCriteria(field=field, operator="eq", value=value)
                    )

        # Create query options
        options = QueryOptions(
            limit=page_size,
            offset=(page - 1) * page_size,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        # Execute search
        if criteria:
            results = await self.search(criteria, options)
            total_count = await self.count(criteria=criteria)
        else:
            results = await self.list(options=options)
            total_count = await self.count()

        total_pages = (total_count + page_size - 1) // page_size

        return {
            "items": results,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_count": total_count,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1,
            },
        }

    # Helper Methods

    def _calculate_interest_similarity(
        self, interests1: List[str], interests2: List[str]
    ) -> float:
        """Calculate Jaccard similarity between interest sets"""
        if not interests1 and not interests2:
            return 1.0
        if not interests1 or not interests2:
            return 0.0

        set1 = set(interests1)
        set2 = set(interests2)

        intersection = len(set1 & set2)
        union = len(set1 | set2)

        return intersection / union if union > 0 else 0.0

    def _should_advance_level(self, child: Child) -> bool:
        """Check if child should advance to next learning level"""
        age_level_map = {
            LearningLevel.PRESCHOOL: (3, 5),
            LearningLevel.EARLY_ELEMENTARY: (6, 7),
            LearningLevel.ELEMENTARY: (8, 10),
            LearningLevel.MIDDLE_SCHOOL: (11, 13),
            LearningLevel.HIGH_SCHOOL: (14, 18),
        }

        current_range = age_level_map.get(child.learning_level)
        if not current_range:
            return False

        # Check if age exceeds current level range
        return child.age > current_range[1]

    # Maintenance Methods

    async def cleanup_old_data(self, days: int = 365) -> int:
        """
        Clean up old inactive profiles

        Args:
            days: Days of inactivity before cleanup

        Returns:
            Number of profiles cleaned
        """
        inactive = await self.get_inactive_children(days)

        # Soft delete inactive profiles
        count = 0
        for child in inactive:
            if await self.soft_delete(child.id):
                count += 1

        return count

    async def validate_all_profiles(self) -> List[Tuple[str, List[str]]]:
        """
        Validate all child profiles

        Returns:
            List of (child_id, errors) tuples
        """
        validation_errors = []

        all_children = await self.list()
        for child in all_children:
            errors = await self.validate(child)
            if errors:
                validation_errors.append((child.id, list(errors.keys())))

        return validation_errors
