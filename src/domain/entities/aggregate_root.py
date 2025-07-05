"""
🏗️ Aggregate Root Base Class
============================

Base class for all aggregate roots in the domain.
Provides event sourcing capabilities and maintains domain event collection.
"""

from abc import ABC
from dataclasses import dataclass, field
from typing import Generic, List, TypeVar

from .base_entity import Entity
from .domain_event import DomainEvent

T = TypeVar("T")


@dataclass
class AggregateRoot(Entity, Generic[T], ABC):
    """
    Base class for aggregate roots.

    An aggregate root is the only member of its aggregate
    through which external objects are allowed to hold references.
    It ensures the integrity of the aggregate boundary.
    """

    _domain_events: List[DomainEvent] = field(default_factory=list, init=False)
    _version: int = field(default=0, init=False)

    def add_domain_event(self, event: DomainEvent) -> None:
        """Add a domain event to be published"""
        if event not in self._domain_events:
            self._domain_events.append(event)

    def remove_domain_event(self, event: DomainEvent) -> None:
        """Remove a domain event"""
        if event in self._domain_events:
            self._domain_events.remove(event)

    def get_domain_events(self) -> List[DomainEvent]:
        """Get all pending domain events"""
        return self._domain_events.copy()

    def clear_domain_events(self) -> List[DomainEvent]:
        """Clear and return all domain events"""
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events

    def mark_events_as_committed(self) -> None:
        """Mark all events as committed (remove them)"""
        self._domain_events.clear()

    def increment_version(self) -> None:
        """Increment the aggregate version for optimistic locking"""
        self._version += 1

    @property
    def version(self) -> int:
        """Get the current aggregate version"""
        return self._version

    def has_uncommitted_events(self) -> bool:
        """Check if there are uncommitted domain events"""
        return len(self._domain_events) > 0

    def __post_init__(self):
        """Post initialization hook for subclasses"""
        super().__post_init__()
        if hasattr(self, "_initialize_aggregate"):
            self._initialize_aggregate()
