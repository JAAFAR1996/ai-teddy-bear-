"""
🌟 Shared Kernel - AI Teddy Bear Core
====================================

The shared kernel contains common abstractions and base classes
used across the domain. This ensures consistency and provides
foundational building blocks for the domain model.

Components:
- Base entity and aggregate root classes
- Domain event abstractions
- Common value object patterns
- Specification pattern implementations
"""

from .base_entity import Entity
from .aggregate_root import AggregateRoot
from .domain_event import DomainEvent
from .value_object import ValueObject
from .specification import Specification
from .repository import Repository
from .domain_service import DomainService

__all__ = [
    'Entity',
    'AggregateRoot',
    'DomainEvent',
    'ValueObject',
    'Specification',
    'Repository',
    'DomainService'
] 