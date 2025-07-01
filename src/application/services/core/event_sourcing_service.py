"""
⚡ Event Sourcing Service
========================

High-level service for event sourcing operations including
event replay, projections, and stream management.
"""

import logging
from typing import Any, AsyncIterator, Dict, List, Optional, Type, TypeVar

from ...infrastructure.messaging.event_bus_integration import EventBus
from ...shared.kernel import AggregateRoot, DomainEvent
from .event_sourcing_repository import (EventSourcingRepository,
                                        EventSourcingRepositoryImpl)
from .event_store import EventStore, StoredEvent, get_event_store
from .snapshot_store import SnapshotStore, get_snapshot_store

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=AggregateRoot)


class EventSourcingService:
    """High-level service for event sourcing operations"""

    def __init__(
        self,
        event_store: Optional[EventStore] = None,
        snapshot_store: Optional[SnapshotStore] = None,
        event_bus: Optional[EventBus] = None,
    ):
        self.event_store = event_store or get_event_store()
        self.snapshot_store = snapshot_store or get_snapshot_store()
        self.event_bus = event_bus or EventBus()
        self._repositories: Dict[Type, EventSourcingRepository] = {}

    def get_repository(self, aggregate_type: Type[T]) -> EventSourcingRepository:
        """Get or create repository for aggregate type"""

        if aggregate_type not in self._repositories:
            self._repositories[aggregate_type] = EventSourcingRepositoryImpl(
                aggregate_type=aggregate_type,
                event_store=self.event_store,
                snapshot_store=self.snapshot_store,
            )

        return self._repositories[aggregate_type]

    async def save_aggregate(self, aggregate: T) -> None:
        """Save aggregate and publish domain events"""

        repository = self.get_repository(type(aggregate))

        # Get events before saving
        events = aggregate.get_domain_events()

        # Save aggregate
        await repository.save(aggregate)

        # Publish events to event bus
        await self._publish_domain_events(events)

        logger.info(
            f"Saved aggregate {aggregate.id} and published {len(events)} events"
        )

    async def load_aggregate(
        self, aggregate_type: Type[T], aggregate_id: str
    ) -> Optional[T]:
        """Load aggregate by ID"""

        repository = self.get_repository(aggregate_type)
        aggregate = await repository.load(aggregate_id)

        if aggregate:
            logger.info(
                f"Loaded aggregate {aggregate_id} of type {aggregate_type.__name__}"
            )

        return aggregate

    async def replay_events(
        self, stream_id: str, from_version: int = 0
    ) -> AsyncIterator[StoredEvent]:
        """Replay events from stream"""

        events = await self.event_store.load_events(stream_id, from_version)

        for event in events:
            yield event

        logger.info(f"Replayed {len(events)} events from {stream_id}")

    async def create_projection(
        self, stream_pattern: str, projection_handler: callable
    ) -> Dict[str, Any]:
        """Create projection from event streams"""

        projection_data = {}

        # Simple projection - in production use proper projection infrastructure
        events = await self.event_store.load_events(stream_pattern)

        for stored_event in events:
            projection_data = await projection_handler(projection_data, stored_event)

        logger.info(f"Created projection with {len(events)} events")

        return projection_data

    async def get_stream_info(self, stream_id: str) -> Dict[str, Any]:
        """Get information about event stream"""

        exists = await self.event_store.stream_exists(stream_id)
        if not exists:
            return {"exists": False}

        version = await self.event_store.get_stream_version(stream_id)
        events = await self.event_store.load_events(stream_id)

        first_event = events[0] if events else None
        last_event = events[-1] if events else None

        return {
            "exists": True,
            "version": version,
            "event_count": len(events),
            "first_event_timestamp": (
                first_event.metadata.timestamp if first_event else None
            ),
            "last_event_timestamp": (
                last_event.metadata.timestamp if last_event else None
            ),
        }

    async def backup_stream(self, stream_id: str) -> List[Dict[str, Any]]:
        """Backup event stream to serializable format"""

        events = await self.event_store.load_events(stream_id)

        backup_data = []
        for stored_event in events:
            backup_data.append(
                {
                    "metadata": {
                        "event_id": stored_event.metadata.event_id,
                        "stream_id": stored_event.metadata.stream_id,
                        "event_type": stored_event.metadata.event_type,
                        "version": stored_event.metadata.version,
                        "timestamp": stored_event.metadata.timestamp.isoformat(),
                    },
                    "data": stored_event.data,
                }
            )

        logger.info(f"Backed up {len(backup_data)} events from {stream_id}")

        return backup_data

    async def restore_stream(
        self, stream_id: str, backup_data: List[Dict[str, Any]]
    ) -> None:
        """Restore event stream from backup"""

        # Create domain events from backup
        events = []
        for item in backup_data:
            # Simple restoration - in production use proper event registry
            event_data = item["data"]
            event_data["event_type"] = item["metadata"]["event_type"]
            events.append(event_data)

        # Append events to stream
        await self.event_store.append_events(stream_id, events)

        logger.info(f"Restored {len(events)} events to {stream_id}")

    async def create_snapshot_for_stream(self, stream_id: str, aggregate: T) -> bool:
        """Create snapshot for aggregate"""

        try:
            version = await self.event_store.get_stream_version(stream_id)
            await self.snapshot_store.save_snapshot(stream_id, aggregate, version)

            logger.info(f"Created snapshot for {stream_id} at version {version}")
            return True

        except Exception as e:
            logger.error(f"Failed to create snapshot for {stream_id}: {e}")
            return False

    async def _publish_domain_events(self, events: List[DomainEvent]) -> None:
        """Publish domain events to event bus"""

        for event in events:
            try:
                await self.event_bus.publish_domain_event(event)
            except Exception as e:
                logger.error(f"Failed to publish event {event.event_type}: {e}")


# Singleton instance
_event_sourcing_service: Optional[EventSourcingService] = None


def get_event_sourcing_service() -> EventSourcingService:
    """Get event sourcing service singleton"""
    global _event_sourcing_service
    if not _event_sourcing_service:
        _event_sourcing_service = EventSourcingService()
    return _event_sourcing_service
