"""
📡 Kafka Event Streaming Infrastructure
======================================

Enterprise-grade event streaming infrastructure for AI Teddy Bear system
"""

from .kafka_config import (
    KafkaProducerConfig,
    KafkaConsumerConfig, 
    KafkaTopics,
    CompressionType,
    AcksConfig,
    KAFKA_CONFIG,
    SCHEMA_REGISTRY_CONFIG,
    MONITORING_CONFIG
)

from .event_publisher import (
    KafkaEventPublisher,
    EventPublishingError,
    get_event_publisher
)

from .event_consumer import (
    KafkaEventConsumer,
    EventConsumptionError,
    EventHandler,
    ConsumedEvent
)

from .event_handlers import (
    ChildRegisteredHandler,
    SafetyViolationHandler,
    ConversationAnalyticsHandler,
    EmotionAnalyticsHandler,
    ParentNotificationHandler,
    EVENT_HANDLERS
)

from .event_bus_integration import (
    EventBus,
    DomainEventDispatcher,
    EventDrivenApplicationService,
    EventDispatchContext,
    get_event_bus,
    get_event_dispatcher
)

__all__ = [
    # Configuration
    'KafkaProducerConfig',
    'KafkaConsumerConfig',
    'KafkaTopics',
    'CompressionType',
    'AcksConfig',
    'KAFKA_CONFIG',
    'SCHEMA_REGISTRY_CONFIG',
    'MONITORING_CONFIG',
    
    # Publisher
    'KafkaEventPublisher',
    'EventPublishingError',
    'get_event_publisher',
    
    # Consumer
    'KafkaEventConsumer',
    'EventConsumptionError',
    'EventHandler',
    'ConsumedEvent',
    
    # Handlers
    'ChildRegisteredHandler',
    'SafetyViolationHandler',
    'ConversationAnalyticsHandler',
    'EmotionAnalyticsHandler',
    'ParentNotificationHandler',
    'EVENT_HANDLERS',
    
    # Integration
    'EventBus',
    'DomainEventDispatcher',
    'EventDrivenApplicationService',
    'EventDispatchContext',
    'get_event_bus',
    'get_event_dispatcher'
]

# Version information
__version__ = "1.0.0"
__author__ = "Backend Team"
__description__ = "Kafka Event Streaming Infrastructure for AI Teddy Bear" 