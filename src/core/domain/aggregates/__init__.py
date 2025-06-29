"""
🏗️ Domain Aggregates - AI Teddy Bear Core
=========================================

Aggregates are clusters of associated objects that we treat as a unit
for data changes. Each aggregate has a root entity and maintains
consistency boundaries.

Following DDD principles:
- Aggregate Root controls access to internal entities
- Maintains invariants across the aggregate
- Emits domain events for external changes
- Clear transactional boundaries
"""

from .child_aggregate import ChildAggregate
from .conversation_aggregate import ConversationAggregate
from .learning_session_aggregate import LearningSessionAggregate

__all__ = [
    'ChildAggregate',
    'ConversationAggregate', 
    'LearningSessionAggregate'
] 