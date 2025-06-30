"""
Base entities for Domain Layer
"""

from typing import Optional, List
from uuid import UUID, uuid4
from datetime import datetime

class DomainEvent:
    """Base domain event"""
    def __init__(self):
        self.occurred_at = datetime.utcnow()
        self.event_id = uuid4()

class AggregateRoot:
    """Base aggregate root"""
    def __init__(self, entity_id: Optional[UUID] = None):
        self.id = entity_id or uuid4()
        self._events: List[DomainEvent] = []
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def add_domain_event(self, event: DomainEvent):
        """Add domain event"""
        self._events.append(event)
    
    def clear_events(self) -> List[DomainEvent]:
        """Clear and return events"""
        events = self._events.copy()
        self._events.clear()
        return events
    
    def mark_as_modified(self):
        """Mark entity as modified"""
        self.updated_at = datetime.utcnow() 