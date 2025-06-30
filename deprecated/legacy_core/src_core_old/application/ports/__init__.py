"""
🔌 Application Ports - AI Teddy Bear Core
=========================================

Ports define the interfaces for external services and repositories.
They follow the Dependency Inversion Principle, allowing the
application core to be independent of external concerns.

Port types:
- Inbound Ports: Interfaces for driving adapters (controllers, handlers)
- Outbound Ports: Interfaces for driven adapters (repositories, external services)

Following Hexagonal Architecture principles:
- Abstract external dependencies
- Enable testability through mocking
- Support multiple implementations
- Clear separation of concerns
"""

from .inbound import (
    ChildManagementPort,
    ConversationPort,
    LearningPort,
    SafetyPort
)

from .outbound import (
    ChildRepositoryPort,
    ConversationRepositoryPort,
    AudioProcessingPort,
    AIServicePort,
    NotificationPort,
    CachePort,
    EventPublisherPort
)

__all__ = [
    # Inbound Ports (Use Case Interfaces)
    'ChildManagementPort',
    'ConversationPort',
    'LearningPort',
    'SafetyPort',
    
    # Outbound Ports (External Service Interfaces)
    'ChildRepositoryPort',
    'ConversationRepositoryPort',
    'AudioProcessingPort',
    'AIServicePort',
    'NotificationPort',
    'CachePort',
    'EventPublisherPort'
] 