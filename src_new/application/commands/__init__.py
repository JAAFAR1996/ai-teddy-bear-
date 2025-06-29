"""
Application Commands - CQRS Pattern
"""

from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

@dataclass
class Command(ABC):
    """Base command"""
    pass

@dataclass
class RegisterChildCommand(Command):
    """Register new child command"""
    name: str
    age: int
    device_id: str
    parent_id: UUID

@dataclass
class StartConversationCommand(Command):
    """Start conversation command"""
    child_id: UUID
    initial_message: str

class CommandHandler(ABC):
    """Base command handler"""
    
    @abstractmethod
    async def handle(self, command: Command) -> Any:
        """Handle command"""
        pass

class RegisterChildHandler(CommandHandler):
    """Handle child registration"""
    
    async def handle(self, command: RegisterChildCommand) -> UUID:
        """Register a new child"""
        # Import here to avoid circular dependencies
        from ..domain.entities.child import Child
        
        # Create child entity
        child = Child(
            name=command.name,
            age=command.age,
            device_id=command.device_id
        )
        
        # Save to repository (interface)
        # await self.child_repository.save(child)
        
        # Publish events
        events = child.clear_domain_events()
        for event in events:
            # await self.event_publisher.publish(event)
            print(f"Event published: {event.__class__.__name__}")
        
        return child.id
