"""
Base classes for Domain-Driven Design implementation
Provides foundation for Entities, Value Objects, Aggregates, and Domain Events
"""

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar
from uuid import UUID, uuid4

# Type variables for generic types
T = TypeVar("T")
TId = TypeVar("TId", bound="EntityId")
TEntity = TypeVar("TEntity", bound="Entity")
TAggregate = TypeVar("TAggregate", bound="AggregateRoot")


class DomainException(Exception):
    """Base exception for domain logic violations"""

    def __init__(self, message: str, code: str = "DOMAIN_ERROR"):
        super().__init__(message)
        self.message = message
        self.code = code
        self.timestamp = datetime.now(timezone.utc)


class EntityId(ABC):
    """Base class for strongly-typed entity IDs"""

    def __init__(self, value: UUID = None):
        self.value = value or uuid4()

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.value == other.value

    def __hash__(self):
        return hash(self.value)

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.value})"


@dataclass(frozen=True)
class ValueObject(ABC):
    """
    Base class for value objects
    Value objects are immutable and compared by value
    """

    def __post_init__(self):
        """Validate value object after initialization"""
        self.validate()

    @abstractmethod
    def validate(self):
        """Validate the value object's state"""
        pass


class Entity(ABC, Generic[TId]):
    """
    Base class for domain entities
    Entities have identity and lifecycle
    """

    def __init__(self, id: TId):
        self.id = id
        self._domain_events: List["DomainEvent"] = []

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def add_domain_event(self, event: "DomainEvent"):
        """Add a domain event to be dispatched"""
        self._domain_events.append(event)

    def clear_events(self):
        """Clear all pending domain events"""
        self._domain_events.clear()

    def get_events(self) -> List["DomainEvent"]:
        """Get all pending domain events"""
        return self._domain_events.copy()


class AggregateRoot(Entity[TId], Generic[TId]):
    """
    Base class for aggregate roots
    Aggregate roots are the entry point to the aggregate
    """

    def __init__(self, id: TId):
        super().__init__(id)
        self._version = 0

    def increment_version(self):
        """Increment the aggregate version for optimistic locking"""
        self._version += 1

    def get_version(self) -> int:
        """Get current aggregate version"""
        return self._version

    def raise_event(self, event: "DomainEvent"):
        """Raise a domain event and add it to pending events"""
        self.add_domain_event(event)
        self.increment_version()


@dataclass
class DomainEvent(ABC):
    """Base class for domain events"""

    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    aggregate_id: UUID = None
    aggregate_type: str = None
    event_type: str = None

    def __post_init__(self):
        if not self.event_type:
            self.event_type = self.__class__.__name__

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization"""
        return {
            "event_id": str(self.event_id),
            "occurred_at": self.occurred_at.isoformat(),
            "aggregate_id": str(self.aggregate_id) if self.aggregate_id else None,
            "aggregate_type": self.aggregate_type,
            "event_type": self.event_type,
            "data": self.get_event_data(),
        }

    @abstractmethod
    def get_event_data(self) -> Dict[str, Any]:
        """Get event-specific data"""
        pass


class DomainService(ABC):
    """
    Base class for domain services
    Used for business logic that doesn't belong to a specific entity
    """

    pass


class Repository(ABC, Generic[TAggregate, TId]):
    """Base interface for repositories"""

    @abstractmethod
    async def get_by_id(self, id: TId) -> Optional[TAggregate]:
        """Get aggregate by ID"""
        pass

    @abstractmethod
    async def save(self, aggregate: TAggregate) -> None:
        """Save aggregate"""
        pass

    @abstractmethod
    async def delete(self, aggregate: TAggregate) -> None:
        """Delete aggregate"""
        pass


class Specification(ABC, Generic[T]):
    """
    Base class for specifications (domain-specific query criteria)
    Used to encapsulate business rules for querying
    """

    @abstractmethod
    def is_satisfied_by(self, candidate: T) -> bool:
        """Check if the candidate satisfies the specification"""
        pass

    def and_(self, other: "Specification[T]") -> "AndSpecification[T]":
        """Combine with another specification using AND"""
        return AndSpecification(self, other)

    def or_(self, other: "Specification[T]") -> "OrSpecification[T]":
        """Combine with another specification using OR"""
        return OrSpecification(self, other)

    def not_(self) -> "NotSpecification[T]":
        """Negate the specification"""
        return NotSpecification(self)


class AndSpecification(Specification[T]):
    """AND combination of specifications"""

    def __init__(self, left: Specification[T], right: Specification[T]):
        self.left = left
        self.right = right

    def is_satisfied_by(self, candidate: T) -> bool:
        return self.left.is_satisfied_by(candidate) and self.right.is_satisfied_by(candidate)


class OrSpecification(Specification[T]):
    """OR combination of specifications"""

    def __init__(self, left: Specification[T], right: Specification[T]):
        self.left = left
        self.right = right

    def is_satisfied_by(self, candidate: T) -> bool:
        return self.left.is_satisfied_by(candidate) or self.right.is_satisfied_by(candidate)


class NotSpecification(Specification[T]):
    """NOT specification"""

    def __init__(self, spec: Specification[T]):
        self.spec = spec

    def is_satisfied_by(self, candidate: T) -> bool:
        return not self.spec.is_satisfied_by(candidate)


# Command and Query base classes for CQRS


class Command(ABC):
    """Base class for commands in CQRS"""

    def __init__(self):
        self.command_id = uuid4()
        self.timestamp = datetime.now(timezone.utc)


class Query(ABC):
    """Base class for queries in CQRS"""

    def __init__(self):
        self.query_id = uuid4()
        self.timestamp = datetime.now(timezone.utc)


class CommandHandler(ABC, Generic[T]):
    """Base class for command handlers"""

    @abstractmethod
    async def handle(self, command: T) -> Any:
        """Handle the command"""
        pass


class QueryHandler(ABC, Generic[T]):
    """Base class for query handlers"""

    @abstractmethod
    async def handle(self, query: T) -> Any:
        """Handle the query"""
        pass


# Event sourcing support


class EventStore(ABC):
    """Base interface for event store"""

    @abstractmethod
    async def save_events(self, aggregate_id: UUID, events: List[DomainEvent], expected_version: int) -> None:
        """Save events for an aggregate"""
        pass

    @abstractmethod
    async def get_events(self, aggregate_id: UUID) -> List[DomainEvent]:
        """Get all events for an aggregate"""
        pass


class EventSourcedAggregate(AggregateRoot[TId], Generic[TId]):
    """Base class for event-sourced aggregates"""

    def __init__(self, id: TId):
        super().__init__(id)
        self._uncommitted_events: List[DomainEvent] = []

    def apply_event(self, event: DomainEvent):
        """Apply an event to the aggregate"""
        handler_name = f"_handle_{event.__class__.__name__}"
        handler = getattr(self, handler_name, None)
        if handler:
            handler(event)
        self._version += 1

    def raise_event(self, event: DomainEvent):
        """Raise a new event"""
        event.aggregate_id = self.id.value
        event.aggregate_type = self.__class__.__name__
        self._uncommitted_events.append(event)
        self.apply_event(event)
        super().add_domain_event(event)

    def mark_events_as_committed(self):
        """Mark all uncommitted events as committed"""
        self._uncommitted_events.clear()

    def get_uncommitted_events(self) -> List[DomainEvent]:
        """Get all uncommitted events"""
        return self._uncommitted_events.copy()

    def load_from_history(self, events: List[DomainEvent]):
        """Rebuild aggregate state from event history"""
        for event in events:
            self.apply_event(event)


# Common value objects


@dataclass(frozen=True)
class EmailAddress(ValueObject):
    """Email address value object"""

    value: str

    def validate(self):
        if not self.value or "@" not in self.value:
            raise DomainException("Invalid email address", "INVALID_EMAIL")

        local, domain = self.value.rsplit("@", 1)
        if not local or not domain or "." not in domain:
            raise DomainException("Invalid email address format", "INVALID_EMAIL_FORMAT")


@dataclass(frozen=True)
class PhoneNumber(ValueObject):
    """Phone number value object"""

    value: str
    country_code: str

    def validate(self):
        # Remove all non-digits
        digits = "".join(filter(str.isdigit, self.value))
        if len(digits) < 10:
            raise DomainException("Invalid phone number", "INVALID_PHONE")


@dataclass(frozen=True)
class Money(ValueObject):
    """Money value object"""

    amount: float
    currency: str

    def validate(self):
        if self.amount < 0:
            raise DomainException("Money amount cannot be negative", "NEGATIVE_MONEY")
        if not self.currency or len(self.currency) != 3:
            raise DomainException("Invalid currency code", "INVALID_CURRENCY")

    def add(self, other: "Money") -> "Money":
        """Add two money values"""
        if self.currency != other.currency:
            raise DomainException("Cannot add different currencies", "CURRENCY_MISMATCH")
        return Money(self.amount + other.amount, self.currency)

    def subtract(self, other: "Money") -> "Money":
        """Subtract two money values"""
        if self.currency != other.currency:
            raise DomainException("Cannot subtract different currencies", "CURRENCY_MISMATCH")
        return Money(self.amount - other.amount, self.currency)


@dataclass(frozen=True)
class DateRange(ValueObject):
    """Date range value object"""

    start_date: datetime
    end_date: datetime

    def validate(self):
        if self.start_date > self.end_date:
            raise DomainException("Start date must be before end date", "INVALID_DATE_RANGE")

    def contains(self, date: datetime) -> bool:
        """Check if a date is within the range"""
        return self.start_date <= date <= self.end_date

    def overlaps_with(self, other: "DateRange") -> bool:
        """Check if this range overlaps with another"""
        return not (self.end_date < other.start_date or self.start_date > other.end_date)
