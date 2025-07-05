"""
🌐 REST API Adapters - AI Teddy Bear
===================================

Inbound adapters for REST API endpoints.
These adapters translate HTTP requests into application use cases
and format responses back to HTTP.

Following Hexagonal Architecture:
- Adapters depend on ports, not vice versa
- Handle HTTP-specific concerns (status codes, headers, etc.)
- Validate and transform input/output
- Delegate business logic to use cases
"""

from .child_controller import ChildController
from .conversation_controller import ConversationController
from .health_controller import HealthController
from .learning_controller import LearningController
from .safety_controller import SafetyController

__all__ = [
    "ChildController",
    "ConversationController",
    "LearningController",
    "SafetyController",
    "HealthController",
]
