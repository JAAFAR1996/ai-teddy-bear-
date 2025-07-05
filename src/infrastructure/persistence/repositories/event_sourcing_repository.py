"""
🏛️ Event Sourcing Repository
============================

Repository that rebuilds aggregates from events with snapshots.
"""

import logging
from abc import ABC, abstractmethod
from typing import Optional, Type, TypeVar

from ...shared.kernel import AggregateRoot, DomainEvent
from .event_store import EventStore, StoredEvent, get_event_store
from .snapshot_store import Snapshot, SnapshotStore, get_snapshot_store

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=AggregateRoot)


class EventSourcingRepository(ABC):
    """Abstract event sourcing repository"""

    @abstractmethod
    async def save(self, aggregate: T) -> None:
        """Save aggregate by persisting events"""
        pass

    @abstractmethod
    async def load(self, aggregate_id: str) -> Optional[T]:
        """Load aggregate by replaying events"""
        pass


class EventSourcingRepositoryImpl(EventSourcingRepository):
    """Event sourcing repository implementation"""

    def __init__(
        self,
        aggregate_type: Type[T],
        event_store: Optional[EventStore] = None,
        snapshot_store: Optional[SnapshotStore] = None,
    ):
        self.aggregate_type = aggregate_type
        self.event_store = event_store or get_event_store()
        self.snapshot_store = snapshot_store or get_snapshot_store()

    async def save(self, aggregate: T) -> None:
        """Save aggregate by persisting uncommitted events"""

        if not aggregate.has_uncommitted_events():
            return

        events = aggregate.get_domain_events()
        stream_id = self._get_stream_id(aggregate)

        await self._persist_events(aggregate, events, stream_id)
        await self._handle_snapshotting(aggregate, stream_id)

        aggregate.clear_domain_events()
        logger.info(f"Saved {len(events)} events for {stream_id}")

    async def load(self, aggregate_id: str) -> Optional[T]:
        """Load aggregate by replaying events from snapshot"""

        stream_id = self._get_stream_id_from_id(aggregate_id)

        # Try snapshot-based loading first
        aggregate = await self._load_from_snapshot(stream_id)
        if not aggregate:
            aggregate = await self._load_from_events(stream_id)

        if aggregate:
            aggregate.clear_domain_events()
            logger.info(f"Loaded aggregate {stream_id}")

        return aggregate

    async def _persist_events(
            self,
            aggregate: T,
            events,
            stream_id: str) -> None:
        """Persist events to event store"""

        await self.event_store.append_events(
            stream_id=stream_id, events=events, expected_version=aggregate.version
        )

        # Update version after successful persistence
        for _ in events:
            aggregate.increment_version()

    async def _handle_snapshotting(self, aggregate: T, stream_id: str) -> None:
        """Handle snapshot creation if needed"""

        if await self.snapshot_store.should_create_snapshot(
            stream_id, aggregate.version
        ):
            await self.snapshot_store.save_snapshot(
                stream_id=stream_id, aggregate=aggregate, version=aggregate.version
            )

    async def _load_from_snapshot(self, stream_id: str) -> Optional[T]:
        """Load aggregate from snapshot + subsequent events"""

        snapshot = await self.snapshot_store.load_snapshot(stream_id)
        if not snapshot:
            return None

        aggregate = self._rebuild_from_snapshot(snapshot)

        # Apply events after snapshot
        events = await self.event_store.load_events(
            stream_id=stream_id, from_version=snapshot.metadata.version + 1
        )

        return self._apply_events_to_aggregate(aggregate, events)

    async def _load_from_events(self, stream_id: str) -> Optional[T]:
        """Load aggregate from all events"""

        events = await self.event_store.load_events(stream_id)
        if not events:
            return None

        aggregate_id = stream_id.split(".")[1]
        aggregate = self._create_empty_aggregate(aggregate_id)

        return self._apply_events_to_aggregate(aggregate, events)

    def _apply_events_to_aggregate(self, aggregate: T, events) -> T:
        """Apply events to rebuild aggregate state"""

        for stored_event in events:
            domain_event = self._deserialize_event(stored_event)
            if domain_event:
                self._apply_event_to_aggregate(aggregate, domain_event)
                aggregate.increment_version()

        return aggregate

    def _get_stream_id(self, aggregate: T) -> str:
        """Get stream ID from aggregate"""
        aggregate_name = type(aggregate).__name__.lower()
        return f"{aggregate_name}.{aggregate.id}"

    def _get_stream_id_from_id(self, aggregate_id: str) -> str:
        """Get stream ID from aggregate ID"""
        aggregate_name = self.aggregate_type.__name__.lower()
        return f"{aggregate_name}.{aggregate_id}"

    def _create_empty_aggregate(self, aggregate_id: str) -> T:
        """Create empty aggregate for event replay"""
        # Basic factory - extend based on aggregate type
        return self.aggregate_type(id=aggregate_id)

    def _rebuild_from_snapshot(self, snapshot: Snapshot[T]) -> T:
        """Rebuild aggregate from snapshot data"""
        return self.aggregate_type(**snapshot.data)

    def _deserialize_event(
            self,
            stored_event: StoredEvent) -> Optional[DomainEvent]:
        """Deserialize stored event back to domain event"""
        # Simple deserialization - extend with event registry in production
        return stored_event.data

    def _apply_event_to_aggregate(
            self,
            aggregate: T,
            event: DomainEvent) -> None:
        """Apply domain event to aggregate for replay"""
        if hasattr(aggregate, "apply_event"):
            aggregate.apply_event(event)
