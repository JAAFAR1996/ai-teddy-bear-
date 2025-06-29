# 🗄️ Event Sourcing Implementation Guide

## Overview

This guide covers the complete Event Sourcing implementation for the AI Teddy Bear system. Event Sourcing is a pattern where state changes are captured as a sequence of events, providing complete audit trails, temporal queries, and event replay capabilities.

## 🏗️ Architecture Components

### 1. Event Store
**Location**: `src/core/domain/events/event_store.py`

The Event Store is responsible for persisting domain events in Kafka topics with the following features:

- **Optimistic Concurrency Control**: Prevents concurrent modification conflicts
- **Stream Management**: Organizes events by aggregate streams
- **Metadata Tracking**: Maintains event versioning and correlation IDs
- **Kafka Integration**: Uses Kafka for scalable event persistence

```python
# Usage example
event_store = get_event_store()
await event_store.append_events(
    stream_id="child.child-123",
    events=[child_registered_event],
    expected_version=0
)
```

### 2. Snapshot Store
**Location**: `src/core/domain/events/snapshot_store.py`

Snapshots optimize performance by caching aggregate state at specific points:

- **Automatic Snapshotting**: Creates snapshots every 10 events (configurable)
- **Performance Optimization**: Reduces event replay overhead
- **Kafka Storage**: Persists snapshots to dedicated Kafka topics
- **Metadata Management**: Tracks snapshot versions and timestamps

```python
# Usage example
snapshot_store = get_snapshot_store()
await snapshot_store.save_snapshot(
    stream_id="child.child-123",
    aggregate=child,
    version=15
)
```

### 3. Event Sourcing Repository
**Location**: `src/core/domain/events/event_sourcing_repository.py`

The repository pattern for Event Sourcing with the following capabilities:

- **Aggregate Reconstruction**: Rebuilds aggregates from events
- **Snapshot Integration**: Uses snapshots for performance
- **Event Persistence**: Saves uncommitted events
- **Version Management**: Handles optimistic concurrency

```python
# Usage example
repository = EventSourcingRepositoryImpl(Child)
await repository.save(child_aggregate)
loaded_child = await repository.load("child-123")
```

### 4. Event Sourcing Service
**Location**: `src/core/domain/events/event_sourcing_service.py`

High-level service orchestrating Event Sourcing operations:

- **Repository Management**: Factory for aggregate repositories
- **Event Publishing**: Integrates with event bus for real-time processing
- **Stream Management**: Provides stream information and utilities
- **Snapshot Management**: Manual snapshot creation capabilities

## 📋 Implementation Details

### Event Stream Structure

Events are organized into streams by aggregate type and ID:

```
Stream ID Format: {aggregate_type}.{aggregate_id}
Examples:
- child.child-123
- conversation.conv-456
- parent.parent-789
```

### Kafka Topic Structure

```
Topics:
- eventstore.child        # Child aggregate events
- eventstore.conversation # Conversation events
- eventstore.parent       # Parent events
- snapshots.child         # Child snapshots
- snapshots.conversation  # Conversation snapshots
```

### Event Metadata

Each stored event includes comprehensive metadata:

```python
@dataclass(frozen=True)
class EventMetadata:
    event_id: str          # Unique event identifier
    stream_id: str         # Stream this event belongs to
    event_type: str        # Type of domain event
    version: int           # Event version in stream
    timestamp: datetime    # When event occurred
    correlation_id: str    # Request correlation ID
    causation_id: str      # Causal event ID
```

## 🚀 Usage Examples

### Basic Event Sourcing Flow

```python
# 1. Create aggregate
child = Child(
    id=ChildId("child-123"),
    parent_id=ParentId("parent-456"),
    device_id=DeviceId("device-789"),
    name="Alice",
    age=6,
    udid="unique-device-123"
)

# 2. Perform business operations (generates events)
child.register_child()
child.update_profile({"age": 7})

# 3. Save aggregate (persists events)
es_service = get_event_sourcing_service()
await es_service.save_aggregate(child)

# 4. Load aggregate (replays events)
loaded_child = await es_service.load_aggregate(Child, "child-123")
```

### Event Replay and Reconstruction

```python
# Load from specific version
events = await event_store.load_events("child.child-123", from_version=5)

# Reconstruct aggregate manually
child = Child.create_empty("child-123")
for stored_event in events:
    domain_event = deserialize_event(stored_event)
    child.apply_event(domain_event)
```

### Snapshot Management

```python
# Check if snapshot should be created
should_snapshot = await snapshot_store.should_create_snapshot(
    "child.child-123", 
    current_version=25
)

# Create snapshot manually
if should_snapshot:
    await snapshot_store.save_snapshot(
        stream_id="child.child-123",
        aggregate=child,
        version=25
    )
```

## 🔧 Integration with DDD

### Aggregate Requirements

Aggregates must implement the following interface for Event Sourcing:

```python
class EventSourcedAggregate:
    def has_uncommitted_events(self) -> bool:
        """Check if aggregate has uncommitted events"""
        
    def get_domain_events(self) -> List[DomainEvent]:
        """Get all uncommitted domain events"""
        
    def clear_domain_events(self) -> None:
        """Clear uncommitted events after persistence"""
        
    def increment_version(self) -> None:
        """Increment aggregate version"""
        
    def apply_event(self, event: DomainEvent) -> None:
        """Apply event for reconstruction"""
        
    @property
    def version(self) -> int:
        """Get current aggregate version"""
```

### Event Application Pattern

Each aggregate should implement event application methods:

```python
def apply_event(self, event: DomainEvent) -> None:
    """Apply event for reconstruction"""
    if isinstance(event, ChildRegistered):
        self._apply_child_registered(event)
    elif isinstance(event, ChildProfileUpdated):
        self._apply_profile_updated(event)
    # ... other event types

def _apply_child_registered(self, event: ChildRegistered) -> None:
    """Apply child registered event"""
    self.name = event.name
    self.age = event.age
    self.registered_at = event.registered_at
```

## 📊 Performance Considerations

### Snapshot Strategy

- **Frequency**: Snapshots created every 10 events (configurable)
- **Storage**: Separate Kafka topics for snapshots
- **Cleanup**: Old snapshots can be cleaned up periodically
- **Performance**: Reduces event replay from O(n) to O(snapshot_frequency)

### Kafka Configuration

Recommended Kafka settings for Event Sourcing:

```python
# Producer settings
producer_config = {
    'acks': 'all',                    # Wait for all replicas
    'retries': 3,                     # Retry failed sends
    'max_in_flight_requests_per_connection': 1,  # Maintain order
    'compression_type': 'snappy',     # Compress events
    'batch_size': 16384,             # Batch for efficiency
}

# Consumer settings
consumer_config = {
    'auto_offset_reset': 'earliest',  # Start from beginning
    'enable_auto_commit': False,      # Manual commit control
    'isolation_level': 'read_committed',  # Transactional consistency
}
```

### Stream Partitioning

Events are partitioned by stream ID to ensure:
- **Ordering**: Events within a stream are ordered
- **Scalability**: Multiple partitions for parallel processing
- **Locality**: Related events are co-located

## 🔒 Security and Compliance

### Event Encryption

Sensitive events should be encrypted:

```python
# Example: Encrypt sensitive fields
encrypted_event = encrypt_sensitive_fields(
    event=child_registered,
    sensitive_fields=['name', 'age'],
    encryption_key=get_encryption_key()
)
```

### Audit Trail

Event Sourcing provides complete audit trail:
- **Who**: Correlation with user/system actions
- **When**: Precise timestamps on all events
- **What**: Complete record of state changes
- **Why**: Business context through event types

### Data Retention

Configure retention policies:

```python
# Kafka retention settings
retention_config = {
    'events': '365 days',      # Keep events for 1 year
    'snapshots': '90 days',    # Keep snapshots for 3 months
    'cleanup_policy': 'compact'  # Compact old events
}
```

## 🧪 Testing Event Sourcing

### Unit Tests

Test aggregate behavior with events:

```python
def test_child_registration():
    # Given
    child = Child.create_empty("child-123")
    
    # When
    event = ChildRegistered(...)
    child.apply_event(event)
    
    # Then
    assert child.name == "Alice"
    assert child.age == 6
```

### Integration Tests

Test complete Event Sourcing flow:

```python
async def test_event_sourcing_flow():
    # Given
    child = create_test_child()
    
    # When
    child.register_child()
    await es_service.save_aggregate(child)
    loaded_child = await es_service.load_aggregate(Child, child.id)
    
    # Then
    assert loaded_child.name == child.name
    assert loaded_child.version > 0
```

### Event Store Tests

Test event persistence and loading:

```python
async def test_event_persistence():
    # Given
    events = [create_test_event()]
    
    # When
    await event_store.append_events("test.stream", events)
    loaded_events = await event_store.load_events("test.stream")
    
    # Then
    assert len(loaded_events) == 1
    assert loaded_events[0].metadata.event_type == events[0].event_type
```

## 📈 Monitoring and Observability

### Key Metrics

Monitor the following Event Sourcing metrics:

- **Event Throughput**: Events persisted per second
- **Snapshot Frequency**: How often snapshots are created
- **Replay Performance**: Time to reconstruct aggregates
- **Stream Growth**: Number of events per stream
- **Error Rates**: Failed event persistence or loading

### Logging

Comprehensive logging for debugging:

```python
logger.info(f"Saved {len(events)} events to stream {stream_id}")
logger.warning(f"Snapshot threshold reached for {stream_id}")
logger.error(f"Failed to load events from {stream_id}: {error}")
```

### Health Checks

Implement health checks for Event Sourcing components:

```python
async def check_event_store_health():
    """Check if event store is healthy"""
    try:
        await event_store.get_stream_version("health.check")
        return {"status": "healthy", "component": "event_store"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

## 🔄 Migration and Versioning

### Event Schema Evolution

Handle event schema changes:

```python
# Version 1
@dataclass
class ChildRegisteredV1(DomainEvent):
    child_id: ChildId
    name: str
    age: int

# Version 2 - Added parent_id
@dataclass  
class ChildRegisteredV2(DomainEvent):
    child_id: ChildId
    parent_id: ParentId  # New field
    name: str
    age: int
    
    @classmethod
    def from_v1(cls, v1_event: ChildRegisteredV1):
        """Migrate from V1 to V2"""
        return cls(
            child_id=v1_event.child_id,
            parent_id=ParentId("unknown"),  # Default value
            name=v1_event.name,
            age=v1_event.age
        )
```

### Stream Migration

Migrate event streams when needed:

```python
async def migrate_stream(old_stream_id: str, new_stream_id: str):
    """Migrate events from old stream to new stream"""
    events = await event_store.load_events(old_stream_id)
    migrated_events = [migrate_event(e) for e in events]
    await event_store.append_events(new_stream_id, migrated_events)
```

## 🎯 Best Practices

### 1. Event Design
- **Immutable**: Events should never change once persisted
- **Granular**: Capture fine-grained business events
- **Meaningful**: Event names should reflect business language
- **Complete**: Include all necessary data for reconstruction

### 2. Aggregate Design
- **Small**: Keep aggregates focused and bounded
- **Consistent**: Maintain invariants within aggregate boundaries
- **Eventual**: Accept eventual consistency between aggregates
- **Stateless Commands**: Commands should be stateless

### 3. Performance
- **Snapshots**: Use snapshots for aggregates with many events
- **Caching**: Cache frequently accessed aggregates
- **Batching**: Batch events when possible
- **Partitioning**: Partition streams for scalability

### 4. Monitoring
- **Metrics**: Track event volumes and performance
- **Alerting**: Alert on event store failures
- **Logging**: Log all Event Sourcing operations
- **Health Checks**: Monitor system health continuously

## 🔗 Integration Points

### With Kafka Event Streaming
Event Sourcing integrates seamlessly with the existing Kafka infrastructure:
- **Shared Infrastructure**: Uses same Kafka cluster
- **Event Publishing**: Publishes to real-time event streams
- **Topic Management**: Dedicated topics for event store vs. event streaming

### With DDD Architecture
Event Sourcing enhances the DDD implementation:
- **Aggregate Roots**: Natural fit for event sourcing
- **Domain Events**: First-class citizens in event sourcing
- **Bounded Contexts**: Event streams provide clear boundaries

### With CQRS Pattern
Event Sourcing pairs naturally with CQRS:
- **Command Side**: Event sourcing for writes
- **Query Side**: Read models from event projections
- **Consistency**: Eventual consistency between sides

This Event Sourcing implementation provides a robust, scalable foundation for the AI Teddy Bear system with complete audit trails, temporal queries, and reliable event replay capabilities. 