# 🗄️ Event Sourcing Implementation Guide

## Overview

Complete Event Sourcing implementation for AI Teddy Bear system using Kafka as the persistence layer.

## 🏗️ Core Components

### 1. Event Store (`event_store.py`)
- Persists domain events to Kafka
- Supports optimistic concurrency control
- Organizes events by aggregate streams
- Handles event versioning and metadata

### 2. Snapshot Store (`snapshot_store.py`)
- Creates snapshots every 10 events for performance
- Stores snapshots in dedicated Kafka topics
- Reduces event replay overhead
- Automatic snapshot management

### 3. Event Sourcing Repository (`event_sourcing_repository.py`)
- Rebuilds aggregates from events
- Integrates snapshots for performance
- Manages aggregate lifecycle
- Handles event persistence

### 4. Event Sourcing Service (`event_sourcing_service.py`)
- High-level API for Event Sourcing operations
- Repository factory and management
- Event publishing integration
- Stream management utilities

## 🚀 Usage Examples

### Basic Usage

```python
# Get service
es_service = get_event_sourcing_service()

# Create and save aggregate
child = ChildAggregateExample(...)
child.register_child()  # Generates domain events
await es_service.save_aggregate(child)

# Load aggregate (rebuilds from events)
loaded_child = await es_service.load_aggregate(ChildAggregateExample, "child-123")
```

### Stream Management

```python
# Get stream information
stream_info = await es_service.get_stream_info("child.child-123")
print(f"Stream version: {stream_info['version']}")

# Create snapshot manually
await es_service.create_snapshot_for_stream("child.child-123", child)
```

## 📋 Aggregate Implementation

Aggregates must implement Event Sourcing interface:

```python
class EventSourcedAggregate:
    def has_uncommitted_events(self) -> bool:
        return len(self._domain_events) > 0
    
    def get_domain_events(self) -> List[DomainEvent]:
        return self._domain_events.copy()
    
    def clear_domain_events(self) -> None:
        self._domain_events.clear()
    
    def increment_version(self) -> None:
        self._version += 1
    
    def apply_event(self, event: DomainEvent) -> None:
        # Apply event for reconstruction
        if isinstance(event, ChildRegistered):
            self._apply_child_registered(event)
```

## 🔧 Configuration

### Kafka Topics
- `eventstore.child` - Child aggregate events
- `eventstore.conversation` - Conversation events
- `snapshots.child` - Child snapshots
- `snapshots.conversation` - Conversation snapshots

### Performance Settings
- Snapshot frequency: 10 events
- Kafka compression: Snappy
- Batch size: 16KB
- Retention: 365 days for events, 90 days for snapshots

## 📊 Integration Points

### With Kafka Event Streaming
- Shares Kafka infrastructure
- Publishes to real-time event streams
- Separate topics for persistence vs streaming

### With DDD Architecture
- Natural fit for aggregate roots
- Domain events as first-class citizens
- Clear bounded contexts through streams

## 🧪 Testing

Run the provided examples:

```bash
python src/core/domain/events/event_sourcing_examples.py
```

Examples include:
1. Basic Event Sourcing operations
2. Load and modify aggregates
3. Safety violation handling
4. Stream management
5. Conversation events

## 🔒 Security Features

- Event encryption for sensitive data
- Complete audit trail with timestamps
- Correlation IDs for request tracking
- Optimistic concurrency control

## 📈 Monitoring

Key metrics to monitor:
- Event throughput (events/second)
- Snapshot creation frequency
- Aggregate reconstruction time
- Stream growth rate
- Error rates

## 🎯 Best Practices

1. **Event Design**: Immutable, granular, meaningful names
2. **Aggregate Design**: Small, consistent, eventual consistency
3. **Performance**: Use snapshots, caching, batching
4. **Monitoring**: Track metrics, health checks, logging

## 🔄 Event Schema Evolution

Handle schema changes with versioning:

```python
@dataclass
class ChildRegisteredV2(DomainEvent):
    # New fields with defaults
    parent_id: ParentId = ParentId("unknown")
    
    @classmethod
    def from_v1(cls, v1_event):
        return cls(
            child_id=v1_event.child_id,
            parent_id=ParentId("unknown"),
            name=v1_event.name,
            age=v1_event.age
        )
```

This Event Sourcing implementation provides complete audit trails, temporal queries, and reliable event replay for the AI Teddy Bear system. 