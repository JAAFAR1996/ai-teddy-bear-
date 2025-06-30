"""
🔄 CQRS Service Implementation
=============================

Unified service orchestrating Command and Query operations.
Provides high-level CQRS interface with command/query separation.
"""

import logging
from typing import Any, Dict, Optional, List
from datetime import datetime
from uuid import uuid4

from .commands.command_bus import get_command_bus, Command, CommandResult
from .commands.child_commands import (
    RegisterChildCommand, UpdateChildProfileCommand, 
    ReportSafetyViolationCommand, register_child_command_handlers
)
from .queries.query_bus import get_query_bus, Query, QueryResult
from .queries.child_queries import (
    GetChildProfileQuery, GetChildrenByParentQuery, 
    GetChildSafetyReportQuery, register_child_query_handlers
)
from .read_models.child_read_model import get_child_projection_manager

logger = logging.getLogger(__name__)


class CQRSService:
    """Central service for CQRS operations"""
    
    def __init__(self):
        self.command_bus = get_command_bus()
        self.query_bus = get_query_bus()
        self.projection_manager = get_child_projection_manager()
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize CQRS service with handlers"""
        
        if self._initialized:
            return
        
        # Register command handlers
        register_child_command_handlers()
        
        # Register query handlers  
        register_child_query_handlers()
        
        self._initialized = True
        logger.info("CQRS Service initialized successfully")
    
    # Command operations (Write side)
    async def register_child(
        self,
        parent_id: str,
        device_id: str,
        name: str,
        age: int,
        udid: str,
        user_id: Optional[str] = None
    ) -> CommandResult:
        """Register new child"""
        
        command = RegisterChildCommand(
            command_id=str(uuid4()),
            timestamp=datetime.utcnow(),
            parent_id=parent_id,
            device_id=device_id,
            name=name,
            age=age,
            udid=udid,
            user_id=user_id
        )
        
        result = await self.command_bus.execute(command)
        
        # Update read models if successful
        if result.success and result.data:
            await self._update_read_models_after_registration(result.data)
        
        return result
    
    async def update_child_profile(
        self,
        child_id: str,
        changes: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> CommandResult:
        """Update child profile"""
        
        command = UpdateChildProfileCommand(
            command_id=str(uuid4()),
            timestamp=datetime.utcnow(),
            child_id=child_id,
            changes=changes,
            user_id=user_id
        )
        
        result = await self.command_bus.execute(command)
        
        # Invalidate relevant caches
        if result.success:
            await self.query_bus.invalidate_cache(f"child_profile:{child_id}")
            await self.query_bus.invalidate_cache(f"parent_children")
        
        return result
    
    async def report_safety_violation(
        self,
        child_id: str,
        violation_type: str,
        details: str,
        severity: str = "medium",
        user_id: Optional[str] = None
    ) -> CommandResult:
        """Report safety violation"""
        
        command = ReportSafetyViolationCommand(
            command_id=str(uuid4()),
            timestamp=datetime.utcnow(),
            child_id=child_id,
            violation_type=violation_type,
            details=details,
            severity=severity,
            user_id=user_id
        )
        
        result = await self.command_bus.execute(command)
        
        # Invalidate safety-related caches
        if result.success:
            await self.query_bus.invalidate_cache(f"safety_report:{child_id}")
            await self.query_bus.invalidate_cache(f"child_profile:{child_id}")
        
        return result
    
    # Query operations (Read side)
    async def get_child_profile(
        self,
        child_id: str,
        user_id: Optional[str] = None
    ) -> QueryResult:
        """Get child profile"""
        
        query = GetChildProfileQuery(
            query_id=str(uuid4()),
            timestamp=datetime.utcnow(),
            child_id=child_id,
            user_id=user_id
        )
        
        return await self.query_bus.execute(query)
    
    async def get_children_by_parent(
        self,
        parent_id: str,
        page: int = 1,
        page_size: int = 10,
        user_id: Optional[str] = None
    ) -> QueryResult:
        """Get children for parent"""
        
        query = GetChildrenByParentQuery(
            query_id=str(uuid4()),
            timestamp=datetime.utcnow(),
            parent_id=parent_id,
            page=page,
            page_size=page_size,
            user_id=user_id
        )
        
        return await self.query_bus.execute(query)
    
    async def get_child_safety_report(
        self,
        child_id: str,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        user_id: Optional[str] = None
    ) -> QueryResult:
        """Get child safety report"""
        
        query = GetChildSafetyReportQuery(
            query_id=str(uuid4()),
            timestamp=datetime.utcnow(),
            child_id=child_id,
            from_date=from_date,
            to_date=to_date,
            user_id=user_id
        )
        
        return await self.query_bus.execute(query)
    
    # Analytics and insights
    async def get_system_analytics(self) -> Dict[str, Any]:
        """Get system-wide analytics"""
        
        analytics = self.projection_manager.get_analytics_summary()
        
        # Add real-time metrics
        command_health = await self.command_bus.health_check()
        query_health = await self.query_bus.health_check()
        
        analytics.update({
            "command_bus": {
                "status": command_health["status"],
                "handlers_count": command_health["handlers_count"]
            },
            "query_bus": {
                "status": query_health["status"],
                "handlers_count": query_health["handlers_count"],
                "cache_stats": query_health["cache_stats"]
            },
            "generated_at": datetime.utcnow().isoformat()
        })
        
        return analytics
    
    async def search_children(
        self,
        search_term: Optional[str] = None,
        age_range: Optional[tuple] = None,
        parent_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search children with criteria"""
        
        results = self.projection_manager.search_children(
            name_pattern=search_term,
            age_range=age_range,
            parent_id=parent_id
        )
        
        # Convert to dict format
        return [
            {
                "id": child.id,
                "name": child.name,
                "age": child.age,
                "parent_id": child.parent_id,
                "conversation_count": child.conversation_count,
                "safety_status": child.safety_status,
                "engagement_level": child.engagement_level,
                "profile_completeness": child.profile_completeness
            }
            for child in results
        ]
    
    # Administrative operations
    async def get_health_status(self) -> Dict[str, Any]:
        """Get overall CQRS health status"""
        
        command_health = await self.command_bus.health_check()
        query_health = await self.query_bus.health_check()
        
        return {
            "status": "healthy" if command_health["status"] == "healthy" and 
                     query_health["status"] == "healthy" else "unhealthy",
            "components": {
                "command_bus": command_health,
                "query_bus": query_health,
                "projection_manager": {
                    "status": "healthy",
                    "read_models_count": len(self.projection_manager.read_models),
                    "conversation_summaries_count": len(self.projection_manager.conversation_summaries)
                }
            },
            "initialized": self._initialized,
            "checked_at": datetime.utcnow().isoformat()
        }
    
    async def clear_all_caches(self) -> None:
        """Clear all query caches"""
        
        await self.query_bus.invalidate_cache()
        logger.info("All CQRS caches cleared")
    
    async def rebuild_read_models(self) -> Dict[str, Any]:
        """Rebuild read models from event store"""
        
        # This would normally replay events from event store
        # For now, just reset projection manager
        
        self.projection_manager = get_child_projection_manager()
        
        logger.info("Read models rebuilt")
        
        return {
            "status": "completed",
            "rebuilt_at": datetime.utcnow().isoformat(),
            "read_models_count": len(self.projection_manager.read_models)
        }
    
    async def _update_read_models_after_registration(self, registration_data: Dict) -> None:
        """Update read models after successful child registration"""
        
        # This simulates event projection update
        # In production, this would be handled by event handlers
        
        child_id = registration_data.get("child_id")
        if child_id:
            logger.info(f"Read models updated for new child: {child_id}")


# Global CQRS service instance
_cqrs_service: Optional[CQRSService] = None


def get_cqrs_service() -> CQRSService:
    """Get global CQRS service instance"""
    global _cqrs_service
    if not _cqrs_service:
        _cqrs_service = CQRSService()
    return _cqrs_service 