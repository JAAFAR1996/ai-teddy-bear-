"""
Event-Driven Architecture with CQRS and Event Sourcing
Advanced messaging system with Redis Streams, saga pattern, and distributed transactions
"""

import asyncio
import json
import logging
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Type, TypeVar, Union

import redis.asyncio as redis
from pydantic import BaseModel, Field
from typing_extensions import Protocol

logger = logging.getLogger(__name__)

T = TypeVar('T')


class EventType(Enum):
    """Event types for categorization"""
    DOMAIN = "domain"
    INTEGRATION = "integration"
    COMMAND = "command"
    QUERY = "query"
    SYSTEM = "system"
    AUDIT = "audit"


class EventStatus(Enum):
    """Event processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY = "retry"


@dataclass
class EventMetadata:
    """Metadata for events"""
    event_id: str
    event_type: EventType
    timestamp: datetime
    correlation_id: str
    causation_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    version: int = 1
    source: str = "teddy_bear"
    tags: Set[str] = field(default_factory=set)


class Event(BaseModel):
    """Base event class"""
    metadata: EventMetadata
    data: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        arbitrary_types_allowed = True


class Command(BaseModel):
    """Base command class"""
    command_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user_id: Optional[str] = None
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    data: Dict[str, Any] = Field(default_factory=dict)


class Query(BaseModel):
    """Base query class"""
    query_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user_id: Optional[str] = None
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    parameters: Dict[str, Any] = Field(default_factory=dict)


class EventHandler(Protocol):
    """Protocol for event handlers"""
    
    async def handle(self, event: Event) -> None:
        """Handle event"""
        ...


class CommandHandler(Protocol):
    """Protocol for command handlers"""
    
    async def handle(self, command: Command) -> Any:
        """Handle command"""
        ...


class QueryHandler(Protocol):
    """Protocol for query handlers"""
    
    async def handle(self, query: Query) -> Any:
        """Handle query"""
        ...


class IEventStore(ABC):
    """Interface for event store"""
    
    @abstractmethod
    async def append(self, stream_name: str, events: List[Event]) -> None:
        """Append events to stream"""
        pass
    
    @abstractmethod
    async def read(self, stream_name: str, from_position: int = 0) -> List[Event]:
        """Read events from stream"""
        pass
    
    @abstractmethod
    async def read_all(self, from_position: int = 0) -> List[Event]:
        """Read all events"""
        pass


class IEventBus(ABC):
    """Interface for event bus"""
    
    @abstractmethod
    async def publish(self, event: Event) -> None:
        """Publish event"""
        pass
    
    @abstractmethod
    async def subscribe(self, event_type: EventType, handler: EventHandler) -> None:
        """Subscribe to event type"""
        pass
    
    @abstractmethod
    async def unsubscribe(self, event_type: EventType, handler: EventHandler) -> None:
        """Unsubscribe from event type"""
        pass


class ICommandBus(ABC):
    """Interface for command bus"""
    
    @abstractmethod
    async def send(self, command: Command) -> Any:
        """Send command"""
        pass
    
    @abstractmethod
    async def register_handler(self, command_type: Type[Command], handler: CommandHandler) -> None:
        """Register command handler"""
        pass


class IQueryBus(ABC):
    """Interface for query bus"""
    
    @abstractmethod
    async def ask(self, query: Query) -> Any:
        """Ask query"""
        pass
    
    @abstractmethod
    async def register_handler(self, query_type: Type[Query], handler: QueryHandler) -> None:
        """Register query handler"""
        pass


class RedisEventStore(IEventStore):
    """Redis-based event store using Redis Streams"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.stream_prefix = "events:"
    
    async def append(self, stream_name: str, events: List[Event]) -> None:
        """Append events to Redis stream"""
        full_stream_name = f"{self.stream_prefix}{stream_name}"
        
        for event in events:
            # Convert event to Redis stream format
            event_data = {
                "event_id": event.metadata.event_id,
                "event_type": event.metadata.event_type.value,
                "timestamp": event.metadata.timestamp.isoformat(),
                "correlation_id": event.metadata.correlation_id,
                "causation_id": event.metadata.causation_id or "",
                "user_id": event.metadata.user_id or "",
                "version": str(event.metadata.version),
                "source": event.metadata.source,
                "tags": ",".join(event.metadata.tags),
                "data": json.dumps(event.data)
            }
            
            # Add to Redis stream
            await self.redis.xadd(full_stream_name, event_data)
        
        logger.info(f"📝 Appended {len(events)} events to stream {stream_name}")
    
    async def read(self, stream_name: str, from_position: int = 0) -> List[Event]:
        """Read events from Redis stream"""
        full_stream_name = f"{self.stream_prefix}{stream_name}"
        
        # Read from stream
        stream_data = await self.redis.xread({full_stream_name: from_position})
        
        events = []
        for stream_name, messages in stream_data:
            for message_id, data in messages:
                # Convert Redis data back to Event
                event = self._redis_data_to_event(data)
                events.append(event)
        
        return events
    
    async def read_all(self, from_position: int = 0) -> List[Event]:
        """Read all events from all streams"""
        # Get all stream names
        stream_keys = await self.redis.keys(f"{self.stream_prefix}*")
        
        all_events = []
        for stream_key in stream_keys:
            stream_name = stream_key.decode().replace(self.stream_prefix, "")
            events = await self.read(stream_name, from_position)
            all_events.extend(events)
        
        # Sort by timestamp
        all_events.sort(key=lambda e: e.metadata.timestamp)
        return all_events
    
    def _redis_data_to_event(self, data: Dict[str, bytes]) -> Event:
        """Convert Redis data to Event"""
        metadata = EventMetadata(
            event_id=data[b"event_id"].decode(),
            event_type=EventType(data[b"event_type"].decode()),
            timestamp=datetime.fromisoformat(data[b"timestamp"].decode()),
            correlation_id=data[b"correlation_id"].decode(),
            causation_id=data[b"causation_id"].decode() if data[b"causation_id"] else None,
            user_id=data[b"user_id"].decode() if data[b"user_id"] else None,
            version=int(data[b"version"].decode()),
            source=data[b"source"].decode(),
            tags=set(data[b"tags"].decode().split(",")) if data[b"tags"] else set()
        )
        
        event_data = json.loads(data[b"data"].decode())
        
        return Event(metadata=metadata, data=event_data)


class RedisEventBus(IEventBus):
    """Redis-based event bus with pub/sub and streams"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.handlers: Dict[EventType, List[EventHandler]] = {}
        self.pubsub = self.redis.pubsub()
        self._running = False
        self._task: Optional[asyncio.Task] = None
    
    async def publish(self, event: Event) -> None:
        """Publish event to Redis"""
        # Publish to Redis pub/sub
        channel = f"events:{event.metadata.event_type.value}"
        message = event.json()
        await self.redis.publish(channel, message)
        
        # Also store in event store
        event_store = RedisEventStore(self.redis)
        await event_store.append("global", [event])
        
        logger.info(f"📢 Published event {event.metadata.event_id} to {channel}")
    
    async def subscribe(self, event_type: EventType, handler: EventHandler) -> None:
        """Subscribe to event type"""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
            # Subscribe to Redis channel
            await self.pubsub.subscribe(f"events:{event_type.value}")
        
        self.handlers[event_type].append(handler)
        logger.info(f"📡 Subscribed to {event_type.value} events")
    
    async def unsubscribe(self, event_type: EventType, handler: EventHandler) -> None:
        """Unsubscribe from event type"""
        if event_type in self.handlers:
            if handler in self.handlers[event_type]:
                self.handlers[event_type].remove(handler)
            
            if not self.handlers[event_type]:
                # Unsubscribe from Redis channel
                await self.pubsub.unsubscribe(f"events:{event_type.value}")
                del self.handlers[event_type]
    
    async def start(self) -> None:
        """Start event bus processing"""
        if self._running:
            return
        
        self._running = True
        self._task = asyncio.create_task(self._process_messages())
        logger.info("🚀 Event bus started")
    
    async def stop(self) -> None:
        """Stop event bus processing"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        
        await self.pubsub.close()
        logger.info("🛑 Event bus stopped")
    
    async def _process_messages(self) -> None:
        """Process incoming messages"""
        async for message in self.pubsub.listen():
            if message["type"] == "message":
                try:
                    # Parse event
                    event_data = json.loads(message["data"])
                    event = Event.parse_obj(event_data)
                    
                    # Find handlers
                    event_type = event.metadata.event_type
                    if event_type in self.handlers:
                        # Execute handlers
                        tasks = []
                        for handler in self.handlers[event_type]:
                            task = asyncio.create_task(handler.handle(event))
                            tasks.append(task)
                        
                        # Wait for all handlers to complete
                        await asyncio.gather(*tasks, return_exceptions=True)
                        
                except Exception as e:
                    logger.error(f"❌ Error processing message: {e}")


class InMemoryCommandBus(ICommandBus):
    """In-memory command bus with handler registration"""
    
    def __init__(self):
        self.handlers: Dict[Type[Command], CommandHandler] = {}
        self.middleware: List[Callable] = []
    
    async def send(self, command: Command) -> Any:
        """Send command to appropriate handler"""
        command_type = type(command)
        
        if command_type not in self.handlers:
            raise ValueError(f"No handler registered for command type {command_type}")
        
        handler = self.handlers[command_type]
        
        # Apply middleware
        result = command
        for middleware in self.middleware:
            result = await middleware(result)
        
        # Execute handler
        return await handler.handle(result)
    
    async def register_handler(self, command_type: Type[Command], handler: CommandHandler) -> None:
        """Register command handler"""
        self.handlers[command_type] = handler
        logger.info(f"📝 Registered handler for {command_type.__name__}")
    
    def add_middleware(self, middleware: Callable) -> None:
        """Add middleware to command bus"""
        self.middleware.append(middleware)


class InMemoryQueryBus(IQueryBus):
    """In-memory query bus with handler registration"""
    
    def __init__(self):
        self.handlers: Dict[Type[Query], QueryHandler] = {}
        self.cache: Dict[str, Any] = {}
        self.cache_ttl: Dict[str, float] = {}
    
    async def ask(self, query: Query) -> Any:
        """Ask query to appropriate handler"""
        query_type = type(query)
        
        if query_type not in self.handlers:
            raise ValueError(f"No handler registered for query type {query_type}")
        
        # Check cache
        cache_key = f"{query_type.__name__}:{query.query_id}"
        if cache_key in self.cache:
            if time.time() < self.cache_ttl[cache_key]:
                logger.info(f"💾 Cache hit for query {query.query_id}")
                return self.cache[cache_key]
            else:
                # Remove expired cache entry
                del self.cache[cache_key]
                del self.cache_ttl[cache_key]
        
        handler = self.handlers[query_type]
        result = await handler.handle(query)
        
        # Cache result (TTL: 5 minutes)
        self.cache[cache_key] = result
        self.cache_ttl[cache_key] = time.time() + 300
        
        return result
    
    async def register_handler(self, query_type: Type[Query], handler: QueryHandler) -> None:
        """Register query handler"""
        self.handlers[query_type] = handler
        logger.info(f"📝 Registered handler for {query_type.__name__}")
    
    def clear_cache(self) -> None:
        """Clear query cache"""
        self.cache.clear()
        self.cache_ttl.clear()


class SagaManager:
    """Manages distributed transactions using saga pattern"""
    
    def __init__(self, event_bus: IEventBus):
        self.event_bus = event_bus
        self.sagas: Dict[str, Dict[str, Any]] = {}
        self.compensations: Dict[str, List[Callable]] = {}
    
    async def start_saga(self, saga_id: str, steps: List[Dict[str, Any]]) -> None:
        """Start a new saga"""
        self.sagas[saga_id] = {
            "steps": steps,
            "current_step": 0,
            "status": "running",
            "compensations": []
        }
        
        # Execute first step
        await self._execute_step(saga_id, 0)
    
    async def _execute_step(self, saga_id: str, step_index: int) -> None:
        """Execute a saga step"""
        saga = self.sagas[saga_id]
        steps = saga["steps"]
        
        if step_index >= len(steps):
            # Saga completed successfully
            saga["status"] = "completed"
            return
        
        step = steps[step_index]
        
        try:
            # Execute step
            result = await step["action"]()
            
            # Store compensation if provided
            if "compensation" in step:
                saga["compensations"].append(step["compensation"])
            
            # Move to next step
            saga["current_step"] = step_index + 1
            await self._execute_step(saga_id, step_index + 1)
            
        except Exception as e:
            # Step failed, start compensation
            logger.error(f"❌ Saga step failed: {e}")
            await self._compensate(saga_id, step_index)
    
    async def _compensate(self, saga_id: str, failed_step: int) -> None:
        """Compensate for failed saga"""
        saga = self.sagas[saga_id]
        compensations = saga["compensations"]
        
        # Execute compensations in reverse order
        for i in range(len(compensations) - 1, -1, -1):
            try:
                await compensations[i]()
            except Exception as e:
                logger.error(f"❌ Compensation failed: {e}")
        
        saga["status"] = "failed"
        logger.info(f"🔄 Saga {saga_id} compensated")


class EventSourcingManager:
    """Manages event sourcing for aggregate reconstruction"""
    
    def __init__(self, event_store: IEventStore):
        self.event_store = event_store
        self.snapshots: Dict[str, Dict[str, Any]] = {}
    
    async def save_events(self, aggregate_id: str, events: List[Event], expected_version: int) -> None:
        """Save events for aggregate"""
        # Validate version
        current_events = await self.event_store.read(f"aggregate:{aggregate_id}")
        if len(current_events) != expected_version:
            raise ValueError("Concurrency conflict detected")
        
        # Save events
        await self.event_store.append(f"aggregate:{aggregate_id}", events)
        
        # Create snapshot if needed
        if len(current_events) + len(events) >= 100:  # Snapshot every 100 events
            await self._create_snapshot(aggregate_id, current_events + events)
    
    async def load_aggregate(self, aggregate_id: str, aggregate_class: Type) -> Any:
        """Load aggregate from events"""
        # Try to load from snapshot first
        if aggregate_id in self.snapshots:
            snapshot = self.snapshots[aggregate_id]
            aggregate = aggregate_class(**snapshot["state"])
            
            # Apply events after snapshot
            events = await self.event_store.read(f"aggregate:{aggregate_id}", snapshot["version"])
            for event in events:
                aggregate.apply(event)
            
            return aggregate
        
        # Load from all events
        events = await self.event_store.read(f"aggregate:{aggregate_id}")
        aggregate = aggregate_class()
        
        for event in events:
            aggregate.apply(event)
        
        return aggregate
    
    async def _create_snapshot(self, aggregate_id: str, events: List[Event]) -> None:
        """Create snapshot of aggregate state"""
        # This would typically serialize the aggregate state
        # For now, we'll just store the event count
        self.snapshots[aggregate_id] = {
            "version": len(events),
            "state": {"event_count": len(events)},
            "timestamp": datetime.now(timezone.utc)
        }


class DeadLetterQueue:
    """Handles failed events and commands"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.dlq_key = "dead_letter_queue"
    
    async def add_failed_event(self, event: Event, error: Exception) -> None:
        """Add failed event to DLQ"""
        dlq_item = {
            "event": event.json(),
            "error": str(error),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "retry_count": 0
        }
        
        await self.redis.lpush(self.dlq_key, json.dumps(dlq_item))
        logger.warning(f"⚠️ Event {event.metadata.event_id} moved to DLQ: {error}")
    
    async def retry_failed_events(self, max_retries: int = 3) -> None:
        """Retry failed events from DLQ"""
        while True:
            # Get item from DLQ
            item_data = await self.redis.rpop(self.dlq_key)
            if not item_data:
                break
            
            item = json.loads(item_data)
            retry_count = item["retry_count"]
            
            if retry_count >= max_retries:
                logger.error(f"❌ Event exceeded max retries: {item['event']}")
                continue
            
            # Increment retry count
            item["retry_count"] += 1
            
            # Put back in DLQ for retry
            await self.redis.lpush(self.dlq_key, json.dumps(item))
            
            logger.info(f"🔄 Retrying event (attempt {retry_count + 1})")


# Factory functions
def create_event_store(redis_url: str = "redis://localhost:6379") -> IEventStore:
    """Create Redis event store"""
    redis_client = redis.from_url(redis_url)
    return RedisEventStore(redis_client)


def create_event_bus(redis_url: str = "redis://localhost:6379") -> IEventBus:
    """Create Redis event bus"""
    redis_client = redis.from_url(redis_url)
    return RedisEventBus(redis_client)


def create_command_bus() -> ICommandBus:
    """Create in-memory command bus"""
    return InMemoryCommandBus()


def create_query_bus() -> IQueryBus:
    """Create in-memory query bus"""
    return InMemoryQueryBus()


# Utility functions
def create_event(
    event_type: EventType,
    data: Dict[str, Any],
    correlation_id: Optional[str] = None,
    user_id: Optional[str] = None,
    **kwargs
) -> Event:
    """Create event with metadata"""
    metadata = EventMetadata(
        event_id=str(uuid.uuid4()),
        event_type=event_type,
        timestamp=datetime.now(timezone.utc),
        correlation_id=correlation_id or str(uuid.uuid4()),
        user_id=user_id,
        **kwargs
    )
    
    return Event(metadata=metadata, data=data)


def create_command(data: Dict[str, Any], user_id: Optional[str] = None, **kwargs) -> Command:
    """Create command"""
    return Command(data=data, user_id=user_id, **kwargs)


def create_query(parameters: Dict[str, Any], user_id: Optional[str] = None, **kwargs) -> Query:
    """Create query"""
    return Query(parameters=parameters, user_id=user_id, **kwargs) 