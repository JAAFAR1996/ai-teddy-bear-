"""Child service implementing child-specific business logic."""

from typing import List, Optional
from uuid import UUID
import logging
from datetime import datetime, timedelta

from .base_service import BaseService
from ...domain.entities.child import Child, ChildPreferences, ParentalConsent
from ...domain.repositories.child_repository import ChildRepository

class ChildService(BaseService[Child]):
    """Service for managing child-related operations."""

    def __init__(
        self,
        repository: ChildRepository,
        logger: logging.Logger = None,
        consent_expiry_days: int = 365
    ):
        """Initialize child service."""
        super().__init__(repository, logger)
        self._repository: ChildRepository = repository
        self.consent_expiry_days = consent_expiry_days

    async def create_child(
        self,
        name: str,
        age: int,
        preferences: Optional[ChildPreferences] = None
    ) -> Child:
        """Create a new child profile."""
        child = Child(name=name, age=age, preferences=preferences)
        await self._log_operation(
            "create_child",
            details={"name": name, "age": age}
        )
        return await self.create(child)

    async def update_preferences(
        self,
        child_id: UUID,
        preferences: dict
    ) -> Child:
        """Update child preferences."""
        child = await self.get(child_id)
        if not child:
            raise ValueError(f"Child not found: {child_id}")

        new_preferences = ChildPreferences(**preferences)
        child.update_preferences(new_preferences)
        
        await self._log_operation(
            "update_preferences",
            child_id,
            {"preferences": preferences}
        )
        return await self.update(child)

    async def grant_consent(
        self,
        child_id: UUID,
        parent_id: UUID,
        consent_data: dict
    ) -> Child:
        """Grant parental consent for child activities."""
        child = await self.get(child_id)
        if not child:
            raise ValueError(f"Child not found: {child_id}")

        # Create consent record
        consent = ParentalConsent(
            data_collection=consent_data.get('data_collection', False),
            audio_recording=consent_data.get('audio_recording', False),
            ai_interaction=consent_data.get('ai_interaction', False),
            granted_at=datetime.utcnow(),
            granted_by=parent_id
        )
        
        child.parental_consent = consent
        await self._log_operation(
            "grant_consent",
            child_id,
            {
                "parent_id": str(parent_id),
                "consent": consent_data
            }
        )
        return await self.update(child)

    async def revoke_consent(self, child_id: UUID) -> Child:
        """Revoke all parental consent."""
        child = await self.get(child_id)
        if not child:
            raise ValueError(f"Child not found: {child_id}")

        child.revoke_consent()
        await self._log_operation("revoke_consent", child_id)
        return await self.update(child)

    async def delete_child_data(
        self,
        child_id: UUID,
        data_types: List[str]
    ) -> bool:
        """Delete specific types of child data (GDPR right to erasure)."""
        result = await self._repository.delete_data(child_id, data_types)
        await self._log_operation(
            "delete_data",
            child_id,
            {"data_types": data_types}
        )
        return result

    async def export_child_data(self, child_id: UUID) -> dict:
        """Export all child data (GDPR right to data portability)."""
        data = await self._repository.export_data(child_id)
        await self._log_operation(
            "export_data",
            child_id
        )
        return data

    async def anonymize_child(self, child_id: UUID) -> bool:
        """Anonymize child's data (GDPR compliance)."""
        result = await self._repository.anonymize(child_id)
        await self._log_operation(
            "anonymize",
            child_id
        )
        return result

    async def get_interaction_history(
        self,
        child_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> dict:
        """Get child's interaction history with metrics."""
        stats = await self._repository.get_interaction_stats(child_id)
        await self._log_operation(
            "get_interaction_history",
            child_id,
            {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            }
        )
        return stats

    async def check_consent_expiry(self) -> List[Child]:
        """Check for children whose consent is expiring soon."""
        expiry_threshold = datetime.utcnow() - timedelta(days=self.consent_expiry_days)
        children = await self._repository.find_requiring_consent_renewal()
        
        for child in children:
            await self._log_operation(
                "consent_expiring",
                child.id,
                {"expiry_date": expiry_threshold.isoformat()}
            )
        
        return children

    async def bulk_update_preferences(
        self,
        updates: List[dict]
    ) -> List[Child]:
        """Bulk update preferences for multiple children."""
        result = await self._repository.bulk_update_preferences(updates)
        await self._log_operation(
            "bulk_update_preferences",
            details={"update_count": len(updates)}
        )
        return result

    async def get_active_children(
        self,
        since: Optional[datetime] = None
    ) -> List[Child]:
        """Get children who have been active since the given time."""
        if not since:
            since = datetime.utcnow() - timedelta(days=7)
        
        children = await self._repository.find_active(since)
        await self._log_operation(
            "get_active_children",
            details={"since": since.isoformat()}
        )
        return children