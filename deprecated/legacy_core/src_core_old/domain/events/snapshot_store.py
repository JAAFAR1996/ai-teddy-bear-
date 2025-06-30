"""
📸 Snapshot Store Implementation
================================

Snapshot store for Event Sourcing to improve performance by caching
aggregate states at specific points in time.
"""

import json
import logging
import asyncio
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, TypeVar, Generic
from dataclasses import dataclass, asdict

from ...shared.kernel import AggregateRoot
from ...infrastructure.messaging.kafka_config import KAFKA_CONFIG
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError


logger = logging.getLogger(__name__)

T = TypeVar('T', bound=AggregateRoot)


@dataclass(frozen=True)
class SnapshotMetadata:
    """Metadata for snapshots"""
    snapshot_id: str
    stream_id: str
    aggregate_type: str
    version: int
    timestamp: datetime
    

@dataclass(frozen=True)
class Snapshot(Generic[T]):
    """Snapshot of aggregate state"""
    metadata: SnapshotMetadata
    data: Dict[str, Any]


class SnapshotStore(ABC):
    """Abstract snapshot store interface"""
    
    @abstractmethod
    async def save_snapshot(
        self, 
        stream_id: str, 
        aggregate: T, 
        version: int
    ) -> None:
        """Save aggregate snapshot"""
        pass
    
    @abstractmethod
    async def load_snapshot(
        self, 
        stream_id: str
    ) -> Optional[Snapshot[T]]:
        """Load latest snapshot for stream"""
        pass
    
    @abstractmethod
    async def should_create_snapshot(
        self, 
        stream_id: str, 
        current_version: int
    ) -> bool:
        """Determine if snapshot should be created"""
        pass


class KafkaSnapshotStore(SnapshotStore):
    """Kafka-based snapshot store"""
    
    def __init__(self, snapshot_frequency: int = 10):
        self.producer = None
        self.consumer = None
        self.snapshot_frequency = snapshot_frequency
        self._last_snapshot_versions: Dict[str, int] = {}
    
    async def _get_producer(self) -> KafkaProducer:
        """Get or create Kafka producer"""
        if not self.producer:
            self.producer = KafkaProducer(
                bootstrap_servers=KAFKA_CONFIG.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode(),
                key_serializer=lambda k: k.encode() if k else None,
                acks='all'
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
    
    async def save_snapshot(
        self, 
        stream_id: str, 
        aggregate: T, 
        version: int
    ) -> None:
        """Save aggregate snapshot to Kafka"""
        
        producer = await self._get_producer()
        topic = f"snapshots.{stream_id.split('.')[0]}"
        
        try:
            snapshot = self._create_snapshot(stream_id, aggregate, version)
            
            future = producer.send(
                topic=topic,
                key=stream_id,
                value=asdict(snapshot)
            )
            await asyncio.wrap_future(future)
            
            self._last_snapshot_versions[stream_id] = version
            
            logger.info(f"Saved snapshot for {stream_id} at version {version}")
            
        except KafkaError as e:
            logger.error(f"Failed to save snapshot for {stream_id}: {e}")
            raise
    
    async def load_snapshot(
        self, 
        stream_id: str
    ) -> Optional[Snapshot[T]]:
        """Load latest snapshot from Kafka"""
        
        consumer = await self._get_consumer()
        topic = f"snapshots.{stream_id.split('.')[0]}"
        
        try:
            consumer.subscribe([topic])
            
            latest_snapshot = None
            latest_version = -1
            
            for message in consumer:
                if message.key == stream_id:
                    snapshot_data = message.value
                    snapshot = Snapshot(
                        metadata=SnapshotMetadata(**snapshot_data['metadata']),
                        data=snapshot_data['data']
                    )
                    
                    if snapshot.metadata.version > latest_version:
                        latest_snapshot = snapshot
                        latest_version = snapshot.metadata.version
            
            return latest_snapshot
            
        except KafkaError as e:
            logger.error(f"Failed to load snapshot for {stream_id}: {e}")
            return None
        finally:
            consumer.unsubscribe()
    
    async def should_create_snapshot(
        self, 
        stream_id: str, 
        current_version: int
    ) -> bool:
        """Check if snapshot should be created based on frequency"""
        
        last_snapshot_version = self._last_snapshot_versions.get(stream_id, 0)
        
        return (current_version - last_snapshot_version) >= self.snapshot_frequency
    
    def _create_snapshot(
        self, 
        stream_id: str, 
        aggregate: T, 
        version: int
    ) -> Snapshot[T]:
        """Create snapshot from aggregate"""
        
        from uuid import uuid4
        
        metadata = SnapshotMetadata(
            snapshot_id=str(uuid4()),
            stream_id=stream_id,
            aggregate_type=type(aggregate).__name__,
            version=version,
            timestamp=datetime.utcnow()
        )
        
        # Serialize aggregate state
        if hasattr(aggregate, '__dataclass_fields__'):
            data = asdict(aggregate)
        else:
            data = aggregate.__dict__.copy()
            
        # Remove internal fields
        data.pop('_domain_events', None)
        
        return Snapshot(metadata=metadata, data=data)


# Singleton instance
_snapshot_store: Optional[SnapshotStore] = None


def get_snapshot_store() -> SnapshotStore:
    """Get snapshot store singleton"""
    global _snapshot_store
    if not _snapshot_store:
        _snapshot_store = KafkaSnapshotStore()
    return _snapshot_store 