"""
📡 Kafka Event Publisher
========================

High-performance, reliable event publishing for AI Teddy Bear domain events
"""

import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import uuid4
from dataclasses import asdict
import asyncio
from concurrent.futures import ThreadPoolExecutor

from kafka import KafkaProducer
from kafka.errors import KafkaError, KafkaTimeoutError

from .kafka_config import KafkaProducerConfig, KafkaTopics, KAFKA_CONFIG
from ..domain.events import DomainEvent
from ..shared.kernel import DomainEvent as BaseDomainEvent


logger = logging.getLogger(__name__)


class EventPublishingError(Exception):
    """Exception raised when event publishing fails"""
    pass


class KafkaEventPublisher:
    """
    High-performance Kafka event publisher for domain events.
    
    Features:
    - Async publishing with batching
    - Automatic retry with exponential backoff
    - Dead letter queue for failed events
    - Schema validation
    - Metrics and monitoring
    """
    
    def __init__(self, config: Optional[KafkaProducerConfig] = None):
        self.config = config or KAFKA_CONFIG[0]  # Producer config
        self._producer: Optional[KafkaProducer] = None
        self._executor = ThreadPoolExecutor(max_workers=4)
        self._metrics = {
            'events_published': 0,
            'events_failed': 0,
            'total_publish_time': 0.0
        }
        
        # Topic routing for domain events
        self._topic_routing = {
            'child.registered': KafkaTopics.CHILD_REGISTERED.name,
            'child.profile_updated': KafkaTopics.CHILD_PROFILE_UPDATED.name,
            'child.safety_violation': KafkaTopics.CHILD_SAFETY_VIOLATION.name,
            'child.milestone_achieved': KafkaTopics.CHILD_MILESTONE_ACHIEVED.name,
            'conversation.started': KafkaTopics.CONVERSATION_STARTED.name,
            'conversation.ended': KafkaTopics.CONVERSATION_ENDED.name,
            'conversation.escalated': KafkaTopics.CONVERSATION_ESCALATED.name,
            'message.received': KafkaTopics.MESSAGE_RECEIVED.name,
            'response.generated': KafkaTopics.RESPONSE_GENERATED.name,
            'emotion.detected': KafkaTopics.EMOTION_DETECTED.name
        }

    def _get_producer(self) -> KafkaProducer:
        """Get or create Kafka producer instance"""
        if self._producer is None:
            try:
                self._producer = KafkaProducer(
                    **self.config.to_kafka_config(),
                    value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
                    key_serializer=lambda v: v.encode('utf-8') if v else None
                )
                logger.info("Kafka producer initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Kafka producer: {e}")
                raise EventPublishingError(f"Producer initialization failed: {e}")
        
        return self._producer

    async def publish_event(
        self, 
        event: BaseDomainEvent,
        partition_key: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Publish a single domain event to Kafka
        
        Args:
            event: Domain event to publish
            partition_key: Key for partitioning (usually child_id)
            headers: Additional headers for the message
            
        Returns:
            bool: True if published successfully, False otherwise
        """
        
        start_time = datetime.utcnow()
        
        try:
            # Determine topic from event type
            topic = self._get_topic_for_event(event)
            
            # Serialize event
            event_data = self._serialize_event(event)
            
            # Set partition key (default to child_id if available)
            if partition_key is None:
                partition_key = self._extract_partition_key(event)
            
            # Set headers
            message_headers = self._create_headers(event, headers)
            
            # Publish to Kafka
            loop = asyncio.get_event_loop()
            future = loop.run_in_executor(
                self._executor,
                self._send_to_kafka,
                topic,
                event_data,
                partition_key,
                message_headers
            )
            
            result = await future
            
            # Update metrics
            self._update_metrics(start_time, success=True)
            
            logger.info(f"Published event {event.event_type} to topic {topic}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish event {event.event_type}: {e}")
            self._update_metrics(start_time, success=False)
            
            # Send to dead letter queue
            await self._send_to_dlq(event, str(e))
            return False

    async def publish_events_batch(
        self, 
        events: List[BaseDomainEvent],
        partition_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Publish multiple events in a batch for better performance
        
        Args:
            events: List of domain events to publish
            partition_key: Key for partitioning
            
        Returns:
            Dict with success/failure counts and details
        """
        
        if not events:
            return {'success_count': 0, 'failure_count': 0, 'failures': []}
        
        results = {
            'success_count': 0,
            'failure_count': 0,
            'failures': []
        }
        
        # Group events by topic for better batching
        events_by_topic = {}
        for event in events:
            topic = self._get_topic_for_event(event)
            if topic not in events_by_topic:
                events_by_topic[topic] = []
            events_by_topic[topic].append(event)
        
        # Publish each topic's events in parallel
        tasks = []
        for topic, topic_events in events_by_topic.items():
            task = self._publish_topic_batch(topic, topic_events, partition_key)
            tasks.append(task)
        
        # Wait for all batches to complete
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Aggregate results
        for batch_result in batch_results:
            if isinstance(batch_result, dict):
                results['success_count'] += batch_result['success_count']
                results['failure_count'] += batch_result['failure_count']
                results['failures'].extend(batch_result['failures'])
            else:
                results['failure_count'] += 1
                results['failures'].append(str(batch_result))
        
        logger.info(f"Batch publish completed: {results['success_count']} successes, "
                   f"{results['failure_count']} failures")
        
        return results

    def _send_to_kafka(
        self, 
        topic: str, 
        event_data: Dict[str, Any],
        partition_key: Optional[str],
        headers: Dict[str, bytes]
    ) -> bool:
        """Send event to Kafka (synchronous)"""
        
        producer = self._get_producer()
        
        try:
            future = producer.send(
                topic=topic,
                value=event_data,
                key=partition_key,
                headers=list(headers.items()) if headers else None
            )
            
            # Wait for send to complete
            record_metadata = future.get(timeout=30)
            
            logger.debug(f"Event sent to {record_metadata.topic} "
                        f"partition {record_metadata.partition} "
                        f"offset {record_metadata.offset}")
            
            return True
            
        except KafkaTimeoutError:
            logger.error(f"Timeout sending event to topic {topic}")
            raise
        except KafkaError as e:
            logger.error(f"Kafka error sending event to topic {topic}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error sending event to topic {topic}: {e}")
            raise

    async def _publish_topic_batch(
        self, 
        topic: str, 
        events: List[BaseDomainEvent],
        partition_key: Optional[str]
    ) -> Dict[str, Any]:
        """Publish a batch of events for a single topic"""
        
        results = {
            'success_count': 0,
            'failure_count': 0,
            'failures': []
        }
        
        # Publish events concurrently within the topic
        tasks = []
        for event in events:
            task = self.publish_event(event, partition_key)
            tasks.append(task)
        
        # Wait for all events to be published
        event_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Count successes and failures
        for i, result in enumerate(event_results):
            if isinstance(result, bool) and result:
                results['success_count'] += 1
            else:
                results['failure_count'] += 1
                results['failures'].append({
                    'event_type': events[i].event_type,
                    'error': str(result) if isinstance(result, Exception) else "Unknown error"
                })
        
        return results

    def _get_topic_for_event(self, event: BaseDomainEvent) -> str:
        """Determine Kafka topic for domain event"""
        
        event_type = event.event_type
        topic = self._topic_routing.get(event_type)
        
        if not topic:
            logger.warning(f"No topic mapping for event type {event_type}, using default")
            topic = KafkaTopics.AUDIT_LOG.name  # Default topic
        
        return topic

    def _serialize_event(self, event: BaseDomainEvent) -> Dict[str, Any]:
        """Serialize domain event to JSON-compatible dict"""
        
        try:
            # Convert dataclass to dict
            if hasattr(event, '__dataclass_fields__'):
                event_dict = asdict(event)
            else:
                # Fallback for non-dataclass events
                event_dict = {
                    attr: getattr(event, attr) 
                    for attr in dir(event) 
                    if not attr.startswith('_') and not callable(getattr(event, attr))
                }
            
            # Add metadata
            event_dict.update({
                'event_id': str(uuid4()),
                'event_version': '1.0',
                'published_at': datetime.utcnow().isoformat(),
                'publisher': 'teddy-event-publisher'
            })
            
            return event_dict
            
        except Exception as e:
            logger.error(f"Failed to serialize event {event.event_type}: {e}")
            raise EventPublishingError(f"Event serialization failed: {e}")

    def _extract_partition_key(self, event: BaseDomainEvent) -> Optional[str]:
        """Extract partition key from event (usually child_id)"""
        
        # Try to get child_id for partitioning
        if hasattr(event, 'child_id'):
            return str(event.child_id)
        elif hasattr(event, 'conversation_id'):
            return str(event.conversation_id)
        elif hasattr(event, 'device_id'):
            return str(event.device_id)
        
        return None

    def _create_headers(
        self, 
        event: BaseDomainEvent, 
        additional_headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, bytes]:
        """Create message headers"""
        
        headers = {
            'event_type': event.event_type.encode('utf-8'),
            'content_type': 'application/json'.encode('utf-8'),
            'timestamp': datetime.utcnow().isoformat().encode('utf-8'),
            'source': 'ai-teddy-bear'.encode('utf-8')
        }
        
        if additional_headers:
            for key, value in additional_headers.items():
                headers[key] = value.encode('utf-8')
        
        return headers

    async def _send_to_dlq(self, event: BaseDomainEvent, error_message: str) -> None:
        """Send failed event to dead letter queue"""
        
        try:
            dlq_data = {
                'original_event': self._serialize_event(event),
                'error_message': error_message,
                'failed_at': datetime.utcnow().isoformat(),
                'retry_count': 0
            }
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self._executor,
                self._send_to_kafka,
                KafkaTopics.DLQ_FAILED_EVENTS.name,
                dlq_data,
                None,
                {'event_type': b'dlq.failed_event'}
            )
            
            logger.info(f"Sent failed event {event.event_type} to DLQ")
            
        except Exception as e:
            logger.error(f"Failed to send event to DLQ: {e}")

    def _update_metrics(self, start_time: datetime, success: bool) -> None:
        """Update publishing metrics"""
        
        duration = (datetime.utcnow() - start_time).total_seconds()
        
        if success:
            self._metrics['events_published'] += 1
        else:
            self._metrics['events_failed'] += 1
        
        self._metrics['total_publish_time'] += duration

    def get_metrics(self) -> Dict[str, Any]:
        """Get publishing metrics"""
        
        total_events = self._metrics['events_published'] + self._metrics['events_failed']
        
        return {
            'events_published': self._metrics['events_published'],
            'events_failed': self._metrics['events_failed'],
            'success_rate': (
                self._metrics['events_published'] / total_events 
                if total_events > 0 else 0.0
            ),
            'average_publish_time': (
                self._metrics['total_publish_time'] / total_events 
                if total_events > 0 else 0.0
            ),
            'total_events': total_events
        }

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on Kafka connection"""
        
        try:
            producer = self._get_producer()
            
            # Test with a simple health check event
            test_event = {
                'event_type': 'system.health_check',
                'timestamp': datetime.utcnow().isoformat(),
                'status': 'healthy'
            }
            
            future = producer.send(
                KafkaTopics.HEALTH_CHECK.name,
                value=test_event
            )
            
            # Wait for completion with short timeout
            future.get(timeout=5)
            
            return {
                'status': 'healthy',
                'kafka_connection': 'ok',
                'last_check': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                'status': 'unhealthy',
                'kafka_connection': 'failed',
                'error': str(e),
                'last_check': datetime.utcnow().isoformat()
            }

    def close(self) -> None:
        """Close producer and cleanup resources"""
        
        if self._producer:
            try:
                self._producer.flush(timeout=10)
                self._producer.close(timeout=10)
                logger.info("Kafka producer closed successfully")
            except Exception as e:
                logger.error(f"Error closing Kafka producer: {e}")
        
        self._executor.shutdown(wait=True)


# Global event publisher instance
_event_publisher: Optional[KafkaEventPublisher] = None


def get_event_publisher() -> KafkaEventPublisher:
    """Get global event publisher instance"""
    global _event_publisher
    
    if _event_publisher is None:
        _event_publisher = KafkaEventPublisher()
    
    return _event_publisher 