"""
Child Search Criteria Domain Models

Contains domain models for child search and filtering operations.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, List, Optional, Tuple
import re


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
            raise ValueError(
                "Maximum age must be greater than or equal to minimum age")
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
        """Get count of active filters by summing up boolean checks."""
        active_filters = [
            bool(self.name_query),
            bool(self.age_range),
            bool(self.languages),
            bool(self.interests),
            self.has_special_needs is not None,
            bool(self.communication_style),
            bool(self.learning_level),
            bool(self.family_code),
            bool(self.parent_id),
            bool(self.interaction_time_filter),
            bool(self.cultural_background),
        ]
        return sum(active_filters)


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
        """
        Return SQL WHERE clause and params by delegating to a ConditionBuilder.
        All columns are validated and only parameterized queries are allowed.
        """
        builder = self._ConditionBuilder(self)
        return builder.build()

    class _ConditionBuilder:
        """Inner class to build SQL conditions for ChildSearchCriteria."""

        def __init__(self, criteria: "ChildSearchCriteria"):
            self.criteria = criteria
            self.filters = criteria.filters
            self.conditions: List[str] = []
            self.params: List[Any] = []
            self._validate_columns()

        def _validate_columns(self):
            """Validate all column names that will be used in conditions."""
            for name in [
                "parent_id", "cultural_background", "max_daily_interaction_time",
                "last_interaction", "interests", "name", "age",
                "language_preference", "special_needs", "communication_style",
                "educational_level", "family_code", "is_active",
            ]:
                if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", name):
                    raise ValueError(f"Unsafe column name: {name}")

        def build(self) -> Tuple[str, List[Any]]:
            """Constructs and returns the final WHERE clause and parameters."""
            if not self.criteria.include_inactive:
                self.conditions.append("is_active = 1")

            self._add_simple_conditions()
            self._add_language_condition()
            self._add_special_needs_condition()
            self._add_interaction_time_conditions()

            main_where_clause = " AND ".join(self.conditions)
            interests_clause = self._get_interests_condition()

            if interests_clause:
                if main_where_clause:
                    return f"{main_where_clause} AND {interests_clause}", self.params
                return interests_clause, self.params
            return main_where_clause, self.params

        def _add_simple_conditions(self):
            """Adds conditions for simple, direct-mapping filters."""
            simple_filters = {
                "name_query": f"name LIKE ?",
                "communication_style": "communication_style = ?",
                "learning_level": "educational_level = ?",
                "family_code": "family_code = ?",
                "parent_id": "parent_id = ?",
                "cultural_background": "cultural_background = ?",
            }
            for attr, condition in simple_filters.items():
                value = getattr(self.filters, attr)
                if value:
                    self.conditions.append(condition)
                    param = f"%{value}%" if "LIKE" in condition else value
                    self.params.append(param)

            if self.filters.age_range:
                self.conditions.append("age BETWEEN ? AND ?")
                self.params.extend(
                    [self.filters.age_range.min_age, self.filters.age_range.max_age])

        def _add_language_condition(self):
            """Adds the condition for language preferences."""
            if self.filters.languages:
                lang_conditions = " OR ".join(
                    ["language_preference = ?" for _ in self.filters.languages])
                self.conditions.append(f"({lang_conditions})")
                self.params.extend(self.filters.languages)

        def _add_special_needs_condition(self):
            """Adds the condition for special needs."""
            if self.filters.has_special_needs is not None:
                if self.filters.has_special_needs:
                    self.conditions.append(
                        "special_needs != '[]' AND special_needs IS NOT NULL")
                else:
                    self.conditions.append(
                        "(special_needs = '[]' OR special_needs IS NULL)")

        def _add_interaction_time_conditions(self):
            """Adds conditions for interaction time filters."""
            time_filter = self.filters.interaction_time_filter
            if not time_filter:
                return

            if time_filter.max_time is not None:
                self.conditions.append("max_daily_interaction_time <= ?")
                self.params.append(time_filter.max_time)

            if time_filter.recent_activity_days is not None:
                cutoff = time_filter.get_cutoff_date_for_recent_activity()
                self.conditions.append("last_interaction >= ?")
                self.params.append(cutoff.isoformat())

            if time_filter.inactive_days is not None:
                cutoff = time_filter.get_cutoff_date_for_inactive()
                self.conditions.append(
                    "(last_interaction IS NULL OR last_interaction < ?)")
                self.params.append(cutoff.isoformat())

        def _get_interests_condition(self) -> str:
            """Builds the sub-clause for searching interests in a JSON field."""
            if not self.filters.interests:
                return ""

            interest_conditions = []
            for interest in self.filters.interests:
                interest_conditions.append(
                    "JSON_EXTRACT(interests, '$') LIKE ?")
                self.params.append(f'%"{interest}"%')

            separator = " AND " if self.criteria.match_all_interests else " OR "
            return f"({separator.join(interest_conditions)})"
