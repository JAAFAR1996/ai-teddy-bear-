"""
📧 Domain Event Base Class
==========================

Base class for all domain events in the AI Teddy Bear system.
"""

import uuid
from abc import ABC
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class DomainEvent(ABC):
    """
    Base class for all domain events.

    Domain events represent something important that happened
    in the domain that domain experts care about.
    """

    event_id: str = None
    occurred_on: datetime = None
    aggregate_id: Optional[str] = None

    def __post_init__(self):
        if self.event_id is None:
            self.event_id = str(uuid.uuid4())
        if self.occurred_on is None:
            self.occurred_on = datetime.now()

    @property
    def event_name(self) -> str:
        """Get the event name (class name)"""
        return self.__class__.__name__

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "event_id": self.event_id,
            "event_name": self.event_name,
            "occurred_on": self.occurred_on.isoformat(),
            "aggregate_id": self.aggregate_id,
        }
