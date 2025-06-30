"""
Child Interaction Application Service

Application service for child interaction management.
"""

from typing import List, Dict, Any
import logging

from src.domain.entities.child import Child
from src.domain.child.services.child_interaction_service import ChildInteractionDomainService
from src.domain.repositories.child_repository import ChildRepository


class ChildInteractionService:
    """Application service for child interaction operations"""
    
    def __init__(
        self,
        child_repository: ChildRepository,
        interaction_domain_service: ChildInteractionDomainService
    ):
        self.child_repository = child_repository
        self.interaction_domain_service = interaction_domain_service
        self.logger = logging.getLogger(__name__)
    
    async def update_interaction_time(self, child_id: str, additional_time: int) -> bool:
        """Update child's interaction time"""
        child = await self.child_repository.get_by_id(child_id)
        if not child:
            return False
        
        # Validate interaction time
        if not self.interaction_domain_service.validate_interaction_time(child, additional_time):
            self.logger.warning(f"Interaction time validation failed for child {child_id}")
            return False
        
        return await self.child_repository.update_interaction_time(child_id, additional_time)
    
    async def get_remaining_time(self, child_id: str) -> int:
        """Get remaining interaction time for a child"""
        child = await self.child_repository.get_by_id(child_id)
        if not child:
            return 0
        
        return self.interaction_domain_service.calculate_remaining_interaction_time(child)
    
    async def get_children_over_limit(self) -> List[Child]:
        """Get children who have exceeded their time limit"""
        return await self.child_repository.get_children_over_time_limit()
    
    async def reset_daily_interaction_times(self) -> int:
        """Reset daily interaction times for all children"""
        return await self.child_repository.reset_daily_interaction_time()
    
    async def get_optimal_session_duration(self, child_id: str) -> int:
        """Get optimal session duration for a child"""
        child = await self.child_repository.get_by_id(child_id)
        if not child:
            return 900  # Default 15 minutes
        
        return self.interaction_domain_service.calculate_optimal_session_duration(child)
