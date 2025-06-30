"""
Child Search Application Service

Application service for child search and filtering operations.
"""

from typing import List, Optional, Tuple
import logging

from src.domain.entities.child import Child
from src.domain.child.models.child_search_criteria import (
    ChildSearchCriteria,
    SearchFilters,
    AgeRange,
    AgeGroup
)
from src.domain.repositories.child_repository import ChildRepository


class ChildSearchService:
    """Application service for child search operations"""
    
    def __init__(self, child_repository: ChildRepository):
        self.child_repository = child_repository
        self.logger = logging.getLogger(__name__)
    
    async def search_children(self, criteria: ChildSearchCriteria) -> List[Child]:
        """Search children based on criteria"""
        try:
            if not criteria.filters.has_filters():
                from src.domain.repositories.base import QueryOptions
                options = QueryOptions(
                    limit=criteria.limit,
                    offset=criteria.offset,
                    sort_by=criteria.sort_by
                )
                return await self.child_repository.list(options)
            
            return await self._execute_advanced_search(criteria)
            
        except Exception as e:
            self.logger.error(f"Error searching children: {e}")
            raise
    
    async def _execute_advanced_search(self, criteria: ChildSearchCriteria) -> List[Child]:
        """Execute advanced search with multiple criteria"""
        filters = criteria.filters
        
        name_query = filters.name_query
        age_range = None
        if filters.age_range:
            age_range = (filters.age_range.min_age, filters.age_range.max_age)
        
        languages = filters.languages
        interests = filters.interests
        has_special_needs = filters.has_special_needs
        
        return await self.child_repository.search_by_multiple_criteria(
            name_query=name_query,
            age_range=age_range,
            languages=languages,
            interests=interests,
            has_special_needs=has_special_needs
        )
    
    async def search_by_name(self, name: str) -> Optional[Child]:
        """Search for a child by exact name"""
        return await self.child_repository.find_by_name(name)
    
    async def search_by_age_group(self, age_group: AgeGroup) -> List[Child]:
        """Search children by predefined age group"""
        age_range = AgeRange.from_age_group(age_group)
        return await self.child_repository.find_by_age_range(
            age_range.min_age, 
            age_range.max_age
        )
    
    async def full_text_search(self, query: str) -> List[Child]:
        """Perform full-text search across child profiles"""
        return await self.child_repository.search_children(query)
