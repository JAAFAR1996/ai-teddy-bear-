"""
🚌 Event Bus Integration
========================

Integration between Domain Events and Kafka Event System
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from ...shared.kernel import DomainEvent
from .event_consumer import KafkaEventConsumer
from .event_handlers import EVENT_HANDLERS
from .event_publisher import KafkaEventPublisher, get_event_publisher

logger = logging.getLogger(__name__)


class EventBus:
    """
    Central event bus integrating domain events with Kafka messaging.

    This class provides the bridge between our DDD domain events
    and the Kafka-based event streaming infrastructure.
    """

    def __init__(
        self,
        publisher: Optional[KafkaEventPublisher] = None,
        consumer: Optional[KafkaEventConsumer] = None,
    ):
        self.publisher = publisher or get_event_publisher()
        self.consumer = consumer or KafkaEventConsumer()
        self._setup_event_handlers()

    def _setup_event_handlers(self) -> None:
        """Setup event handlers for consumer"""

        self.consumer.register_handlers(EVENT_HANDLERS)
        logger.info(f"Registered {len(EVENT_HANDLERS)} event handler types")

    async def publish_domain_event(
        self, event: DomainEvent, partition_key: Optional[str] = None
    ) -> bool:
        """
        Publish a domain event to the event stream

        Args:
            event: Domain event to publish
            partition_key: Key for partitioning

        Returns:
            bool: True if published successfully
        """

        try:
            result = await self.publisher.publish_event(event, partition_key)

            if result:
                logger.info(f"Published domain event: {event.event_type}")
            else:
                logger.error(f"Failed to publish domain event: {event.event_type}")

            return result

        except Exception as e:
            logger.error(f"Error publishing domain event {event.event_type}: {e}")
            return False

    async def publish_domain_events(
        self, events: List[DomainEvent], partition_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Publish multiple domain events as a batch

        Args:
            events: List of domain events to publish
            partition_key: Key for partitioning

        Returns:
            Dict with success/failure counts
        """

        if not events:
            return {"success_count": 0, "failure_count": 0}

        try:
            result = await self.publisher.publish_events_batch(events, partition_key)

            logger.info(
                f"Published {result['success_count']}/{len(events)} domain events"
            )

            if result["failure_count"] > 0:
                logger.warning(f"{result['failure_count']} events failed to publish")

            return result

        except Exception as e:
            logger.error(f"Error publishing domain events batch: {e}")
            return {"success_count": 0, "failure_count": len(events)}

    async def start_event_processing(self, topics: Optional[List[str]] = None) -> None:
        """Start processing events from Kafka"""

        try:
            logger.info("Starting event processing...")
            await self.consumer.start_consuming(topics)
        except Exception as e:
            logger.error(f"Error starting event processing: {e}")
            raise

    async def stop_event_processing(self, timeout: int = 30) -> None:
        """Stop processing events gracefully"""

        logger.info("Stopping event processing...")
        await self.consumer.stop_consuming(timeout)

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on event bus"""

        publisher_health = await self.publisher.health_check()
        consumer_health = await self.consumer.health_check()

        overall_status = (
            "healthy"
            if publisher_health["status"] == "healthy"
            and consumer_health["status"] == "healthy"
            else "unhealthy"
        )

        return {
            "status": overall_status,
            "publisher": publisher_health,
            "consumer": consumer_health,
            "last_check": datetime.utcnow().isoformat(),
        }

    def get_metrics(self) -> Dict[str, Any]:
        """Get event bus metrics"""

        return {
            "publisher_metrics": self.publisher.get_metrics(),
            "consumer_metrics": self.consumer.get_metrics(),
        }


class DomainEventDispatcher:
    """
    Dispatcher for handling domain events from aggregates.

    This integrates with the DDD architecture to automatically
    publish events when they are emitted from domain aggregates.
    """

    def __init__(self, event_bus: Optional[EventBus] = None):
        self.event_bus = event_bus or EventBus()

    async def dispatch_events(self, aggregate) -> None:
        """
        Dispatch all pending events from an aggregate

        Args:
            aggregate: Domain aggregate with pending events
        """

        if not hasattr(aggregate, "clear_events"):
            logger.warning(
                f"Aggregate {type(aggregate)} does not support event dispatch"
            )
            return

        # Get pending events
        events = aggregate.clear_events()

        if not events:
            return

        # Determine partition key (usually child_id or aggregate_id)
        partition_key = self._extract_partition_key(aggregate)

        # Publish events
        result = await self.event_bus.publish_domain_events(events, partition_key)

        logger.info(
            f"Dispatched {result['success_count']} events from {type(aggregate).__name__}"
        )

        if result["failure_count"] > 0:
            logger.error(
                f"Failed to dispatch {result['failure_count']} events from {type(aggregate).__name__}"
            )

    def _extract_partition_key(self, aggregate) -> Optional[str]:
        """Extract partition key from aggregate"""

        # Try common aggregate ID patterns
        for attr in ["id", "child_id", "conversation_id", "device_id"]:
            if hasattr(aggregate, attr):
                return str(getattr(aggregate, attr))

        return None


# Application Service Integration
class EventDrivenApplicationService:
    """
    Base class for application services that need event dispatching.

    This ensures domain events are automatically published after
    domain operations complete.
    """

    def __init__(self, event_dispatcher: Optional[DomainEventDispatcher] = None):
        self.event_dispatcher = event_dispatcher or DomainEventDispatcher()

    async def execute_with_events(self, operation_func, *args, **kwargs):
        """
        Execute operation and dispatch events

        Args:
            operation_func: Function to execute
            *args, **kwargs: Arguments for the function

        Returns:
            Function result
        """

        try:
            # Execute domain operation
            result = await operation_func(*args, **kwargs)

            # Dispatch events from any aggregates in the result
            await self._dispatch_events_from_result(result)

            return result

        except Exception as e:
            logger.error(f"Error executing operation with events: {e}")
            raise

    async def _dispatch_events_from_result(self, result) -> None:
        """Dispatch events from operation result"""

        if hasattr(result, "clear_events"):
            # Single aggregate
            await self.event_dispatcher.dispatch_events(result)
        elif isinstance(result, (list, tuple)):
            # Multiple aggregates
            for item in result:
                if hasattr(item, "clear_events"):
                    await self.event_dispatcher.dispatch_events(item)
        elif isinstance(result, dict):
            # Dict containing aggregates
            for value in result.values():
                if hasattr(value, "clear_events"):
                    await self.event_dispatcher.dispatch_events(value)


# Global instances
_event_bus: Optional[EventBus] = None
_event_dispatcher: Optional[DomainEventDispatcher] = None


def get_event_bus() -> EventBus:
    """Get global event bus instance"""
    global _event_bus

    if _event_bus is None:
        _event_bus = EventBus()

    return _event_bus


def get_event_dispatcher() -> DomainEventDispatcher:
    """Get global event dispatcher instance"""
    global _event_dispatcher

    if _event_dispatcher is None:
        _event_dispatcher = DomainEventDispatcher(get_event_bus())

    return _event_dispatcher


# Context manager for automatic event dispatching
class EventDispatchContext:
    """Context manager for automatic event dispatching"""

    def __init__(self, *aggregates):
        self.aggregates = aggregates
        self.dispatcher = get_event_dispatcher()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:  # No exception occurred
            for aggregate in self.aggregates:
                await self.dispatcher.dispatch_events(aggregate)


# Usage example with context manager
async def example_usage():
    """Example of using event dispatch context"""

    from uuid import uuid4

    from ...domain.aggregates.child_aggregate import Child
    from ...domain.value_objects import DeviceId, ParentId

    # Create child aggregate
    child = Child.register_new_child(
        name="Emma",
        age=7,
        udid="ESP32-001",
        parent_id=ParentId(uuid4()),
        device_id=DeviceId(uuid4()),
    )

    # Use context manager for automatic event dispatching
    async with EventDispatchContext(child):
        # Start conversation
        conversation = child.start_conversation("learning about animals")

        # Add message
        conversation.add_child_message(
            content="Tell me about lions!",
            emotion_detected="excited",
            emotion_confidence=0.85,
        )

        # Events will be automatically dispatched when exiting context
