"""
🗄️ Event Store Implementation
=============================

Event Sourcing implementation for AI Teddy Bear system with Kafka backend.
Provides event persistence, replay capabilities, and stream management.
"""

import json
import logging
import asyncio
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Dict, Any, AsyncIterator
from dataclasses import dataclass, asdict
from uuid import uuid4

from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError

from ...shared.kernel import DomainEvent
from ...infrastructure.messaging.kafka_config import KAFKA_CONFIG


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EventMetadata:
    """Metadata for stored events"""
    event_id: str
    stream_id: str
    event_type: str
    version: int
    timestamp: datetime
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None


@dataclass(frozen=True)
class StoredEvent:
    """Event with metadata for storage"""
    metadata: EventMetadata
    data: Dict[str, Any]
    

class EventStore(ABC):
    """Abstract event store interface"""
    
    @abstractmethod
    async def append_events(
        self, 
        stream_id: str, 
        events: List[DomainEvent],
        expected_version: int = -1
    ) -> None:
        """Append events to stream with optimistic concurrency"""
        pass
        
    @abstractmethod
    async def load_events(
        self, 
        stream_id: str,
        from_version: int = 0
    ) -> List[StoredEvent]:
        """Load events from stream"""
        pass
    
    @abstractmethod
    async def stream_exists(self, stream_id: str) -> bool:
        """Check if stream exists"""
        pass
    
    @abstractmethod
    async def get_stream_version(self, stream_id: str) -> int:
        """Get current stream version"""
        pass


class OptimisticConcurrencyError(Exception):
    """Raised when optimistic concurrency check fails"""
    pass


class KafkaEventStore(EventStore):
    """Kafka-based event store implementation"""
    
    def __init__(self):
        self.producer = None
        self.consumer = None
        self._stream_versions: Dict[str, int] = {}
        
    async def _get_producer(self) -> KafkaProducer:
        """Get or create Kafka producer"""
        if not self.producer:
            self.producer = KafkaProducer(
                bootstrap_servers=KAFKA_CONFIG.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode(),
                key_serializer=lambda k: k.encode() if k else None,
                acks='all',
                retries=3,
                max_in_flight_requests_per_connection=1
            )
        return self.producer
        
    async def _get_consumer(self) -> KafkaConsumer:
        """Get or create Kafka consumer"""
        if not self.consumer:
            self.consumer = KafkaConsumer(
                bootstrap_servers=KAFKA_CONFIG.bootstrap_servers,
                value_deserializer=lambda v: json.loads(v.decode()),
                key_deserializer=lambda k: k.decode() if k else None,
                auto_offset_reset='earliest'
            )
        return self.consumer
    
    async def append_events(
        self, 
        stream_id: str, 
        events: List[DomainEvent],
        expected_version: int = -1
    ) -> None:
        """Append events to Kafka stream"""
        
        if not events:
            return
            
        # Check optimistic concurrency
        current_version = await self.get_stream_version(stream_id)
        if expected_version != -1 and current_version != expected_version:
            raise OptimisticConcurrencyError(
                f"Expected version {expected_version}, got {current_version}"
            )
        
        producer = await self._get_producer()
        topic = f"eventstore.{stream_id.split('.')[0]}"
        
        try:
            for i, event in enumerate(events):
                version = current_version + i + 1
                stored_event = self._create_stored_event(
                    stream_id, event, version
                )
                
                # Send to Kafka
                future = producer.send(
                    topic=topic,
                    key=stream_id,
                    value=asdict(stored_event)
                )
                await asyncio.wrap_future(future)
                
            # Update cached version
            self._stream_versions[stream_id] = current_version + len(events)
            
            logger.info(f"Appended {len(events)} events to stream {stream_id}")
            
        except KafkaError as e:
            logger.error(f"Failed to append events to {stream_id}: {e}")
            raise
    
    async def load_events(
        self, 
        stream_id: str,
        from_version: int = 0
    ) -> List[StoredEvent]:
        """Load events from Kafka stream"""
        
        consumer = await self._get_consumer()
        topic = f"eventstore.{stream_id.split('.')[0]}"
        
        # Subscribe to topic and seek to beginning
        consumer.subscribe([topic])
        
        events = []
        
        try:
            for message in consumer:
                if message.key == stream_id:
                    stored_event_data = message.value
                    stored_event = StoredEvent(
                        metadata=EventMetadata(**stored_event_data['metadata']),
                        data=stored_event_data['data']
                    )
                    
                    if stored_event.metadata.version >= from_version:
                        events.append(stored_event)
                        
        except KafkaError as e:
            logger.error(f"Failed to load events from {stream_id}: {e}")
            raise
        finally:
            consumer.unsubscribe()
            
        return sorted(events, key=lambda e: e.metadata.version)
    
    async def stream_exists(self, stream_id: str) -> bool:
        """Check if stream exists"""
        try:
            events = await self.load_events(stream_id)
            return len(events) > 0
        except:
            return False
    
    async def get_stream_version(self, stream_id: str) -> int:
        """Get current stream version"""
        if stream_id in self._stream_versions:
            return self._stream_versions[stream_id]
            
        events = await self.load_events(stream_id)
        version = len(events)
        self._stream_versions[stream_id] = version
        return version
    
    def _create_stored_event(
        self, 
        stream_id: str, 
        event: DomainEvent, 
        version: int
    ) -> StoredEvent:
        """Create stored event with metadata"""
        
        metadata = EventMetadata(
            event_id=str(uuid4()),
            stream_id=stream_id,
            event_type=event.event_type,
            version=version,
            timestamp=datetime.utcnow(),
            correlation_id=getattr(event, 'correlation_id', None),
            causation_id=getattr(event, 'causation_id', None)
        )
        
        # Serialize event data
        if hasattr(event, '__dataclass_fields__'):
            data = asdict(event)
        else:
            data = event.__dict__.copy()
            
        return StoredEvent(metadata=metadata, data=data)


# Singleton instance
_event_store: Optional[EventStore] = None


def get_event_store() -> EventStore:
    """Get event store singleton"""
    global _event_store
    if not _event_store:
        _event_store = KafkaEventStore()
    return _event_store 