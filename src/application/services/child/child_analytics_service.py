"""
Child Analytics Application Service

Application service for child analytics and insights.
"""

from typing import List, Dict, Any
import logging

from src.domain.entities.child import Child
from src.domain.child.models.child_analytics import ChildEngagementInsight, ChildStatistics
from src.domain.child.services.child_analytics_service import ChildAnalyticsDomainService
from src.domain.repositories.child_repository import ChildRepository


class ChildAnalyticsService:
    """Application service for child analytics operations"""
    
    def __init__(
        self,
        child_repository: ChildRepository,
        analytics_domain_service: ChildAnalyticsDomainService
    ):
        self.child_repository = child_repository
        self.analytics_domain_service = analytics_domain_service
        self.logger = logging.getLogger(__name__)
    
    async def get_child_engagement_insights(self, child_id: str) -> ChildEngagementInsight:
        """Get comprehensive engagement insights for a child"""
        child = await self.child_repository.get_by_id(child_id)
        if not child:
            raise ValueError(f"Child with ID {child_id} not found")
        
        from datetime import datetime
        total_days = (datetime.now() - child.created_at).days if child.created_at else 30
        
        return self.analytics_domain_service.calculate_engagement_insights(child, total_days)
    
    async def get_system_statistics(self) -> ChildStatistics:
        """Get comprehensive system statistics"""
        children = await self.child_repository.list()
        active_children = await self.child_repository.get_children_with_recent_interactions(7)
        
        return self.analytics_domain_service.calculate_statistics(
            children, 
            len(active_children)
        )
    
    async def identify_at_risk_children(self) -> List[Child]:
        """Identify children at risk of disengagement"""
        children = await self.child_repository.list()
        return self.analytics_domain_service.identify_at_risk_children(children)
    
    async def get_learning_progress_scores(self) -> Dict[str, float]:
        """Get learning progress scores for all children"""
        children = await self.child_repository.list()
        scores = {}
        
        for child in children:
            try:
                score = self.analytics_domain_service.calculate_learning_progress_score(child)
                scores[child.id] = score
            except Exception as e:
                self.logger.warning(f"Failed to calculate score for child {child.id}: {e}")
                scores[child.id] = 0.0
        
        return scores
