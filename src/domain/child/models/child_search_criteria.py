"""
Child Search Criteria Domain Models

Contains domain models for child search and filtering operations.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, List, Optional, Tuple


class AgeGroup(Enum):
    """Predefined age groups"""

    PRESCHOOL = "preschool"
    ELEMENTARY = "elementary"
    MIDDLE = "middle"
    HIGH = "high"


@dataclass
class AgeRange:
    """Age range value object"""

    min_age: int
    max_age: int

    def __post_init__(self):
        """Validate age range"""
        if self.min_age < 0:
            raise ValueError("Minimum age cannot be negative")
        if self.max_age < self.min_age:
            raise ValueError("Maximum age must be greater than or equal to minimum age")
        if self.max_age > 100:
            raise ValueError("Maximum age seems unrealistic")

    def contains_age(self, age: int) -> bool:
        """Check if age falls within this range"""
        return self.min_age <= age <= self.max_age

    def overlaps_with(self, other: "AgeRange") -> bool:
        """Check if this range overlaps with another"""
        return not (self.max_age < other.min_age or self.min_age > other.max_age)

    def get_age_group(self) -> AgeGroup:
        """Get corresponding age group"""
        if self.max_age <= 5:
            return AgeGroup.PRESCHOOL
        elif self.max_age <= 11:
            return AgeGroup.ELEMENTARY
        elif self.max_age <= 14:
            return AgeGroup.MIDDLE
        else:
            return AgeGroup.HIGH

    @classmethod
    def from_age_group(cls, age_group: AgeGroup) -> "AgeRange":
        """Create age range from predefined age group"""
        age_ranges = {
            AgeGroup.PRESCHOOL: (3, 5),
            AgeGroup.ELEMENTARY: (6, 11),
            AgeGroup.MIDDLE: (12, 14),
            AgeGroup.HIGH: (15, 18),
        }
        min_age, max_age = age_ranges[age_group]
        return cls(min_age=min_age, max_age=max_age)


@dataclass
class InteractionTimeFilter:
    """Interaction time filter value object"""

    max_time: Optional[int] = None
    inactive_days: Optional[int] = None
    recent_activity_days: Optional[int] = None

    def get_cutoff_date_for_recent_activity(self) -> Optional[datetime]:
        """Get cutoff date for recent activity"""
        if self.recent_activity_days is None:
            return None
        return datetime.now() - timedelta(days=self.recent_activity_days)

    def get_cutoff_date_for_inactive(self) -> Optional[datetime]:
        """Get cutoff date for inactive children"""
        if self.inactive_days is None:
            return None
        return datetime.now() - timedelta(days=self.inactive_days)


@dataclass
class SearchFilters:
    """Search filters value object"""

    name_query: Optional[str] = None
    age_range: Optional[AgeRange] = None
    languages: Optional[List[str]] = None
    interests: Optional[List[str]] = None
    has_special_needs: Optional[bool] = None
    communication_style: Optional[str] = None
    learning_level: Optional[str] = None
    family_code: Optional[str] = None
    parent_id: Optional[str] = None
    interaction_time_filter: Optional[InteractionTimeFilter] = None
    cultural_background: Optional[str] = None

    def has_filters(self) -> bool:
        """Check if any filters are applied"""
        return any(
            [
                self.name_query,
                self.age_range,
                self.languages,
                self.interests,
                self.has_special_needs is not None,
                self.communication_style,
                self.learning_level,
                self.family_code,
                self.parent_id,
                self.interaction_time_filter,
                self.cultural_background,
            ]
        )

    def get_active_filter_count(self) -> int:
        """Get count of active filters"""
        count = 0
        if self.name_query:
            count += 1
        if self.age_range:
            count += 1
        if self.languages:
            count += 1
        if self.interests:
            count += 1
        if self.has_special_needs is not None:
            count += 1
        if self.communication_style:
            count += 1
        if self.learning_level:
            count += 1
        if self.family_code:
            count += 1
        if self.parent_id:
            count += 1
        if self.interaction_time_filter:
            count += 1
        if self.cultural_background:
            count += 1
        return count


@dataclass
class ChildSearchCriteria:
    """Child search criteria domain entity"""

    filters: SearchFilters
    match_all_interests: bool = False
    include_inactive: bool = False
    limit: Optional[int] = None
    offset: Optional[int] = None
    sort_by: Optional[str] = None
    sort_ascending: bool = True

    def __post_init__(self):
        """Validate search criteria"""
        if self.limit is not None and self.limit <= 0:
            raise ValueError("Limit must be positive")
        if self.offset is not None and self.offset < 0:
            raise ValueError("Offset cannot be negative")

    def is_complex_search(self) -> bool:
        """Check if this is a complex search with multiple criteria"""
        return self.filters.get_active_filter_count() > 2

    def requires_full_text_search(self) -> bool:
        """Check if full-text search is needed"""
        return bool(self.filters.name_query and len(self.filters.name_query) > 2)

    def get_search_complexity_score(self) -> int:
        """Get search complexity score for optimization"""
        score = 0
        score += self.filters.get_active_filter_count()
        if self.filters.interests and len(self.filters.interests) > 3:
            score += 2
        if self.match_all_interests:
            score += 1
        if self.requires_full_text_search():
            score += 2
        return score

    def to_sql_conditions(self) -> Tuple[str, List[Any]]:
        """Convert to SQL conditions and parameters"""
        conditions = []
        params = []

        # Base condition for active children
        if not self.include_inactive:
            conditions.append("is_active = 1")

        # Name search
        if self.filters.name_query:
            conditions.append("name LIKE ?")
            params.append(f"%{self.filters.name_query}%")

        # Age range
        if self.filters.age_range:
            conditions.append("age BETWEEN ? AND ?")
            params.extend(
                [self.filters.age_range.min_age, self.filters.age_range.max_age]
            )

        # Languages
        if self.filters.languages:
            lang_conditions = []
            for lang in self.filters.languages:
                lang_conditions.append("language_preference = ?")
                params.append(lang)
            if lang_conditions:
                conditions.append(f"({' OR '.join(lang_conditions)})")

        # Special needs
        if self.filters.has_special_needs is not None:
            if self.filters.has_special_needs:
                conditions.append("special_needs != '[]' AND special_needs IS NOT NULL")
            else:
                conditions.append("(special_needs = '[]' OR special_needs IS NULL)")

        # Communication style
        if self.filters.communication_style:
            conditions.append("communication_style = ?")
            params.append(self.filters.communication_style)

        # Learning level
        if self.filters.learning_level:
            conditions.append("educational_level = ?")
            params.append(self.filters.learning_level)

        # Family code
        if self.filters.family_code:
            conditions.append("family_code = ?")
            params.append(self.filters.family_code)

        # Parent ID
        if self.filters.parent_id:
            conditions.append("parent_id = ?")
            params.append(self.filters.parent_id)

        # Cultural background
        if self.filters.cultural_background:
            conditions.append("cultural_background = ?")
            params.append(self.filters.cultural_background)

        # Interaction time filters
        if self.filters.interaction_time_filter:
            time_filter = self.filters.interaction_time_filter

            if time_filter.max_time is not None:
                conditions.append("max_daily_interaction_time <= ?")
                params.append(time_filter.max_time)

            if time_filter.recent_activity_days is not None:
                cutoff = time_filter.get_cutoff_date_for_recent_activity()
                conditions.append("last_interaction >= ?")
                params.append(cutoff.isoformat())

            if time_filter.inactive_days is not None:
                cutoff = time_filter.get_cutoff_date_for_inactive()
                conditions.append("(last_interaction IS NULL OR last_interaction < ?)")
                params.append(cutoff.isoformat())

        # Handle interests separately due to JSON complexity
        interests_condition = ""
        if self.filters.interests:
            interest_conditions = []
            for interest in self.filters.interests:
                interest_conditions.append("JSON_EXTRACT(interests, '$') LIKE ?")
                params.append(f'%"{interest}"%')

            if self.match_all_interests:
                interests_condition = " AND ".join(interest_conditions)
            else:
                interests_condition = f"({' OR '.join(interest_conditions)})"

        # Combine all conditions
        where_clause = " AND ".join(conditions)
        if interests_condition:
            if where_clause:
                where_clause += f" AND {interests_condition}"
            else:
                where_clause = interests_condition

        return where_clause, params
