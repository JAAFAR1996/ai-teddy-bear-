"""
Child Entity - Main Aggregate Root
"""

from .base import AggregateRoot, DomainEvent
from typing import Optional
from uuid import UUID

class ChildRegistered(DomainEvent):
    """Child registration event"""
    def __init__(self, child_id: UUID, name: str):
        super().__init__()
        self.child_id = child_id
        self.name = name

class Child(AggregateRoot):
    """Child entity - main aggregate root"""
    
    def __init__(self, name: str, age: int, device_id: str, entity_id: Optional[UUID] = None):
        super().__init__(entity_id)
        self.name = name
        self.age = age
        self.device_id = device_id
        self.is_active = True
        
        # Add domain event
        self.add_domain_event(ChildRegistered(self.id, name))
    
    def start_conversation(self, initial_message -> Any: str) -> Any:
        """Start a new conversation"""
        if not self.can_interact():
            raise ValueError("Child cannot interact at this time")
        
        # Business logic here
        return f"Conversation started by {self.name}: {initial_message}"
    
    def can_interact(self) -> bool:
        """Check if child can interact"""
        return self.is_active and 3 <= self.age <= 12
    
    def deactivate(self) -> Any:
        """Deactivate child account"""
        self.is_active = False
        self.mark_as_modified()