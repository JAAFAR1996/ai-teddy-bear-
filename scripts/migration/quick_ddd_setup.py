#!/usr/bin/env python3
"""
Quick DDD Structure Setup
Lead Architect: Jaafar Adeeb
Simplified Domain-Driven Design structure creation
"""

import os
from pathlib import Path


class QuickDDDSetup:
    """Quick setup for DDD structure"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)

    def create_structure(self):
        """Create the basic DDD structure"""
        print("Creating DDD Structure...")

        # Create directories
        directories = [
            "src_new",
            "src_new/domain",
            "src_new/domain/entities",
            "src_new/domain/value_objects",
            "src_new/domain/services",
            "src_new/application",
            "src_new/application/commands",
            "src_new/application/queries",
            "src_new/application/handlers",
            "src_new/infrastructure",
            "src_new/infrastructure/persistence",
            "src_new/infrastructure/ai",
            "src_new/presentation",
            "src_new/presentation/api",
            "tests_new",
            "tests_new/unit",
            "tests_new/integration",
        ]

        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(parents=True, exist_ok=True)

            # Create simple __init__.py
            init_file = dir_path / "__init__.py"
            if not init_file.exists():
                init_file.write_text('"""DDD Module"""')

        # Create base entity class
        self._create_base_entity()

        # Create example child entity
        self._create_child_entity()

        # Create command example
        self._create_commands()

        print("DDD Structure created successfully!")

    def _create_base_entity(self):
        """Create base entity class"""
        content = '''"""
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
'''

        file_path = self.project_root / "src_new/domain/entities/base.py"
        file_path.write_text(content)

    def _create_child_entity(self):
        """Create child entity example"""
        content = '''"""
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
    
    def start_conversation(self, initial_message: str):
        """Start a new conversation"""
        if not self.can_interact():
            raise ValueError("Child cannot interact at this time")
        
        # Business logic here
        return f"Conversation started by {self.name}: {initial_message}"
    
    def can_interact(self) -> bool:
        """Check if child can interact"""
        return self.is_active and 3 <= self.age <= 12
    
    def deactivate(self):
        """Deactivate child account"""
        self.is_active = False
        self.mark_as_modified()
'''

        file_path = self.project_root / "src_new/domain/entities/child.py"
        file_path.write_text(content)

    def _create_commands(self):
        """Create command examples"""
        content = '''"""
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
'''

        file_path = self.project_root / "src_new/application/commands/__init__.py"
        file_path.write_text(content)


def main():
    """Main execution"""
    print("Quick DDD Structure Setup")
    print("Lead Architect: Jaafar Adeeb")
    print("=" * 40)

    setup = QuickDDDSetup()
    setup.create_structure()

    print("\nDDD Structure created!")
    print("New structure available in src_new/ directory")
    print("\nNext steps:")
    print("1. Review the created structure")
    print("2. Migrate existing code gradually")
    print("3. Update imports and dependencies")
    print("4. Run tests to validate")


if __name__ == "__main__":
    main()
