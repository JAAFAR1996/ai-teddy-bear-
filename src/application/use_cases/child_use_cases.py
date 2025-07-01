"""
👶 Child Use Cases
==================

Application use cases for child management.
These orchestrate business operations while keeping the domain pure.
"""

from dataclasses import dataclass
from datetime import date
from typing import Optional

from ...domain.entities import Child
from ...domain.value_objects import ChildId, ParentId
from ...shared.kernel import DomainEvent
from ..dto import (ChildProfileResponse, RegisterChildRequest,
                   RegisterChildResponse, UpdateChildProfileRequest)
from ..ports.outbound import ChildRepositoryPort, EventPublisherPort


@dataclass
class RegisterChildUseCase:
    """Use case for registering a new child"""

    child_repository: ChildRepositoryPort
    event_publisher: EventPublisherPort

    async def execute(self, request: RegisterChildRequest) -> RegisterChildResponse:
        """
        Register a new child in the system.

        Business Rules:
        - Child name must be provided and valid
        - Age must be between 3 and 12
        - Parent must exist and be verified
        """

        # Create new child entity
        child = Child(
            name=request.name,
            age=request.age,
            date_of_birth=request.date_of_birth,
            gender=request.gender,
            parent_id=request.parent_id,
            language_preference=request.language_preference or "en",
        )

        # Save to repository
        await self.child_repository.save(child)

        # Publish domain events
        events = child.clear_events()
        for event in events:
            await self.event_publisher.publish(event)

        return RegisterChildResponse(
            child_id=child.id,
            name=child.name,
            status=child.status,
            created_at=child.created_at,
        )


@dataclass
class UpdateChildProfileUseCase:
    """Use case for updating child profile"""

    child_repository: ChildRepositoryPort
    event_publisher: EventPublisherPort

    async def execute(self, request: UpdateChildProfileRequest) -> ChildProfileResponse:
        """Update child profile information"""

        # Get existing child
        child = await self.child_repository.get_by_id(request.child_id)
        if not child:
            raise ValueError(f"Child not found: {request.child_id}")

        # Update profile
        update_data = {}
        if request.name is not None:
            update_data["name"] = request.name
        if request.favorite_topics is not None:
            update_data["favorite_topics"] = request.favorite_topics
        if request.learning_level is not None:
            update_data["learning_level"] = request.learning_level
        if request.language_preference is not None:
            update_data["language_preference"] = request.language_preference

        child.update_profile(**update_data)

        # Save changes
        await self.child_repository.save(child)

        # Publish events
        events = child.clear_events()
        for event in events:
            await self.event_publisher.publish(event)

        return ChildProfileResponse.from_entity(child)


@dataclass
class GetChildProfileUseCase:
    """Use case for retrieving child profile"""

    child_repository: ChildRepositoryPort

    async def execute(self, child_id: ChildId) -> Optional[ChildProfileResponse]:
        """Get child profile by ID"""

        child = await self.child_repository.get_by_id(child_id)
        if not child:
            return None

        return ChildProfileResponse.from_entity(child)


@dataclass
class ActivateChildUseCase:
    """Use case for activating a child account"""

    child_repository: ChildRepositoryPort
    event_publisher: EventPublisherPort

    async def execute(self, child_id: ChildId) -> bool:
        """Activate child account"""

        child = await self.child_repository.get_by_id(child_id)
        if not child:
            raise ValueError(f"Child not found: {child_id}")

        child.activate()

        await self.child_repository.save(child)

        # Publish events
        events = child.clear_events()
        for event in events:
            await self.event_publisher.publish(event)

        return True


@dataclass
class DeactivateChildUseCase:
    """Use case for deactivating a child account"""

    child_repository: ChildRepositoryPort
    event_publisher: EventPublisherPort

    async def execute(self, child_id: ChildId, reason: str = "") -> bool:
        """Deactivate child account"""

        child = await self.child_repository.get_by_id(child_id)
        if not child:
            raise ValueError(f"Child not found: {child_id}")

        child.deactivate()

        await self.child_repository.save(child)

        # Publish events
        events = child.clear_events()
        for event in events:
            await self.event_publisher.publish(event)

        return True
