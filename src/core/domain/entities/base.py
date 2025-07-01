from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Dict, Any, List
import uuid

class DomainEvent(ABC):
    """Base domain event"""
    def __init__(self):
        self.occurred_at = datetime.utcnow()
        self.event_id = str(uuid.uuid4())

class AggregateRoot:
    """Base aggregate root"""
    def __init__(self, entity_id: Optional[uuid.UUID] = None):
        self.id = entity_id or uuid.uuid4()
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self._domain_events: List[DomainEvent] = []
        self._is_modified = False
    
    def add_domain_event(self, event: DomainEvent) -> None:
        """Add domain event"""
        self._domain_events.append(event)
    
    def clear_domain_events(self) -> None:
        """Clear domain events"""
        self._domain_events.clear()
    
    def get_domain_events(self) -> List[DomainEvent]:
        """Get domain events"""
        return self._domain_events.copy()
    
    def mark_as_modified(self) -> None:
        """Mark as modified"""
        self._is_modified = True
        self.updated_at = datetime.utcnow()

class Entity(ABC):
    """Base entity with common properties"""
    def __init__(self, id: Optional[str] = None):
        self.id = id or str(uuid.uuid4())
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def update_timestamp(self) -> None:
        """تحديث وقت التعديل"""
        self.updated_at = datetime.utcnow()
    
    def __eq__(self, other):
        if not isinstance(other, Entity):
            return False
        return self.id == other.id
    
    def __hash__(self):
        return hash(self.id) 