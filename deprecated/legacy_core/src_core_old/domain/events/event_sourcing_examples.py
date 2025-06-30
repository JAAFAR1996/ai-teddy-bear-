"""
📚 Event Sourcing Usage Examples
================================

Comprehensive examples showing how to use Event Sourcing
for the AI Teddy Bear system.
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional

from ...shared.kernel import DomainEvent
from .event_sourcing_service import get_event_sourcing_service
from ..events.child_events import (
    ChildRegistered, ChildProfileUpdated, SafetyViolationDetected
)
from ..events.conversation_events import (
    ConversationStarted, MessageReceived, ResponseGenerated
)
from ..value_objects import ChildId, ParentId, DeviceId, ConversationId


logger = logging.getLogger(__name__)


class ChildAggregateExample:
    """Example Child aggregate for Event Sourcing"""
    
    def __init__(self, id: ChildId, parent_id: ParentId, device_id: DeviceId, 
                 name: str, age: int, udid: str):
        self.id = id
        self.parent_id = parent_id
        self.device_id = device_id
        self.name = name
        self.age = age
        self.udid = udid
        self._domain_events = []
        self._version = 0
    
    def register_child(self) -> None:
        """Register child and add domain event"""
        
        event = ChildRegistered(
            child_id=self.id,
            parent_id=self.parent_id,
            device_id=self.device_id,
            name=self.name,
            age=self.age,
            udid=self.udid,
            registered_at=datetime.utcnow()
        )
        
        self._domain_events.append(event)
    
    def update_profile(self, changes: dict) -> None:
        """Update child profile"""
        
        for key, value in changes.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        event = ChildProfileUpdated(
            child_id=self.id,
            changes=changes,
            updated_at=datetime.utcnow()
        )
        
        self._domain_events.append(event)
    
    def detect_safety_violation(self, violation_type: str, details: str) -> None:
        """Handle safety violation"""
        
        event = SafetyViolationDetected(
            child_id=self.id,
            violation_type=violation_type,
            details=details,
            violation_count=1,
            severity="high"
        )
        
        self._domain_events.append(event)
    
    def apply_event(self, event: DomainEvent) -> None:
        """Apply event for event sourcing replay"""
        
        if isinstance(event, ChildRegistered):
            self._apply_child_registered(event)
        elif isinstance(event, ChildProfileUpdated):
            self._apply_profile_updated(event)
        elif isinstance(event, SafetyViolationDetected):
            self._apply_safety_violation(event)
    
    def _apply_child_registered(self, event: ChildRegistered) -> None:
        """Apply child registered event"""
        self.name = event.name
        self.age = event.age
        self.udid = event.udid
    
    def _apply_profile_updated(self, event: ChildProfileUpdated) -> None:
        """Apply profile updated event"""
        for key, value in event.changes.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def _apply_safety_violation(self, event: SafetyViolationDetected) -> None:
        """Apply safety violation event"""
        # Could track violation history
        pass
    
    # Required methods for Event Sourcing
    def has_uncommitted_events(self) -> bool:
        return len(self._domain_events) > 0
    
    def get_domain_events(self) -> list:
        return self._domain_events.copy()
    
    def clear_domain_events(self) -> None:
        self._domain_events.clear()
    
    def increment_version(self) -> None:
        self._version += 1
    
    @property
    def version(self) -> int:
        return self._version


async def example_1_basic_event_sourcing():
    """Example 1: Basic Event Sourcing operations"""
    
    print("🔄 Example 1: Basic Event Sourcing")
    
    # Get event sourcing service
    es_service = get_event_sourcing_service()
    
    # Create a child aggregate
    child = ChildAggregateExample(
        id=ChildId("child-123"),
        parent_id=ParentId("parent-456"),
        device_id=DeviceId("device-789"),
        name="Alice",
        age=6,
        udid="unique-device-123"
    )
    
    # Register child (generates domain event)
    child.register_child()
    
    # Save aggregate (persists events)
    await es_service.save_aggregate(child)
    
    print(f"✅ Saved child aggregate with version: {child.version}")


async def example_2_load_and_modify():
    """Example 2: Load aggregate and modify"""
    
    print("🔄 Example 2: Load and Modify Aggregate")
    
    es_service = get_event_sourcing_service()
    
    # Load existing child
    child = await es_service.load_aggregate(ChildAggregateExample, "child-123")
    
    if child:
        print(f"✅ Loaded child: {child.name}, age: {child.age}")
        
        # Update profile
        child.update_profile({"age": 7, "name": "Alice Smith"})
        
        # Save changes
        await es_service.save_aggregate(child)
        
        print(f"✅ Updated child profile, new version: {child.version}")
    else:
        print("❌ Child not found")


async def example_3_safety_violation_handling():
    """Example 3: Handle safety violations with events"""
    
    print("🔄 Example 3: Safety Violation Handling")
    
    es_service = get_event_sourcing_service()
    
    # Load child
    child = await es_service.load_aggregate(ChildAggregateExample, "child-123")
    
    if child:
        # Detect safety violation
        child.detect_safety_violation(
            violation_type="inappropriate_content",
            details="Child used inappropriate language"
        )
        
        # Save with safety event
        await es_service.save_aggregate(child)
        
        print(f"⚠️ Safety violation recorded for {child.name}")
    else:
        print("❌ Child not found")


async def example_4_stream_information():
    """Example 4: Get stream information and manage snapshots"""
    
    print("🔄 Example 4: Stream Management")
    
    es_service = get_event_sourcing_service()
    
    # Get stream info
    stream_id = "childaggregateexample.child-123"
    stream_info = await es_service.get_stream_info(stream_id)
    
    print(f"📊 Stream info: {stream_info}")
    
    # Load child for snapshot
    child = await es_service.load_aggregate(ChildAggregateExample, "child-123")
    
    if child:
        # Create snapshot
        snapshot_created = await es_service.create_snapshot_for_stream(stream_id, child)
        
        if snapshot_created:
            print("📸 Snapshot created successfully")
        else:
            print("❌ Failed to create snapshot")


async def example_5_conversation_events():
    """Example 5: Conversation events with Event Sourcing"""
    
    print("🔄 Example 5: Conversation Events")
    
    # Create conversation events
    conversation_started = ConversationStarted(
        conversation_id=ConversationId("conv-123"),
        child_id=ChildId("child-123"),
        started_at=datetime.utcnow(),
        initial_topic="bedtime_story"
    )
    
    message_received = MessageReceived(
        conversation_id=ConversationId("conv-123"),
        child_id=ChildId("child-123"),
        message_id="msg-001",
        content="Tell me a story about dragons",
        received_at=datetime.utcnow()
    )
    
    response_generated = ResponseGenerated(
        conversation_id=ConversationId("conv-123"),
        child_id=ChildId("child-123"),
        response_id="resp-001",
        content="Once upon a time, there was a friendly dragon..."
    )
    
    print("✅ Created conversation events")
    print(f"  - {conversation_started.event_type}")
    print(f"  - {message_received.event_type}")
    print(f"  - {response_generated.event_type}")


async def run_all_examples():
    """Run all Event Sourcing examples"""
    
    print("🚀 Starting Event Sourcing Examples")
    print("=" * 50)
    
    try:
        await example_1_basic_event_sourcing()
        print()
        
        await example_2_load_and_modify()
        print()
        
        await example_3_safety_violation_handling()
        print()
        
        await example_4_stream_information()
        print()
        
        await example_5_conversation_events()
        print()
        
        print("✅ All examples completed successfully!")
        
    except Exception as e:
        print(f"❌ Error running examples: {e}")
        logger.error(f"Event Sourcing examples failed: {e}")


if __name__ == "__main__":
    # Run examples
    asyncio.run(run_all_examples()) 