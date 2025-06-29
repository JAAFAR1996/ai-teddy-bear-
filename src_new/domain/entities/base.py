"""
Base Entity Classes
"""

from abc import ABC
from datetime import datetime
from typing import List, Any, Optional
from uuid import UUID, uuid4

class DomainEvent:
    """Base domain event"""
    def __init__(self):
        self.event_id = uuid4()
        self.occurred_at = datetime.utcnow()

class Entity(ABC):
    """Base entity with identity"""
    
    def __init__(self, entity_id: Optional[UUID] = None):
        self.id = entity_id or uuid4()
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self._domain_events: List[DomainEvent] = []
    
    def add_domain_event(self, event: DomainEvent) -> None:
        """Add domain event"""
        self._domain_events.append(event)
    
    def clear_domain_events(self) -> List[DomainEvent]:
        """Clear and return events"""
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Entity):
            return False
        return self.id == other.id

class AggregateRoot(Entity):
    """Base aggregate root"""
    
    def __init__(self, entity_id: Optional[UUID] = None):
        super().__init__(entity_id)
        self.version = 1
