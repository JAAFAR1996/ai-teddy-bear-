"""
Memory Domain Models - Core memory entities and value objects
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np


class MemoryType(Enum):
    """Types of memory storage"""

    SHORT_TERM = "short_term"  # Current session
    WORKING = "working"  # Active context (last few interactions)
    LONG_TERM = "long_term"  # Persistent memories
    EPISODIC = "episodic"  # Specific events/experiences
    SEMANTIC = "semantic"  # Facts and knowledge
    EMOTIONAL = "emotional"  # Emotional associations
    PROCEDURAL = "procedural"  # How to do things


class MemoryImportance(Enum):
    """Importance levels for memories"""

    CRITICAL = 5  # Never forget (safety, important facts)
    HIGH = 4  # Important memories (learning milestones)
    MEDIUM = 3  # Regular interactions
    LOW = 2  # Casual conversations
    TRIVIAL = 1  # Can be forgotten


@dataclass
class Memory:
    """Individual memory unit - Core domain entity"""

    id: str
    child_id: str
    content: str
    memory_type: MemoryType
    importance: MemoryImportance
    timestamp: datetime
    context: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[np.ndarray] = None
    emotions: List[str] = field(default_factory=list)
    topics: List[str] = field(default_factory=list)
    related_memories: List[str] = field(default_factory=list)
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    decay_rate: float = 0.1  # How fast the memory fades

    def access(self) -> None:
        """Update access information - Domain behavior"""
        self.access_count += 1
        self.last_accessed = datetime.now()

    def get_strength(self) -> float:
        """Calculate memory strength based on recency and access - Domain logic"""
        if not self.last_accessed:
            self.last_accessed = self.timestamp

        # Time decay
        days_old = (datetime.now() - self.timestamp).days
        time_factor = np.exp(-self.decay_rate * days_old)

        # Access reinforcement
        access_factor = min(1.0, self.access_count / 10)

        # Importance factor
        importance_factor = self.importance.value / 5

        return time_factor * 0.4 + access_factor * 0.3 + importance_factor * 0.3

    def is_strong(self) -> bool:
        """Check if memory is strong enough to persist"""
        return self.get_strength() > 0.3

    def should_consolidate(self) -> bool:
        """Check if memory should be consolidated"""
        return self.importance.value >= MemoryImportance.MEDIUM.value and self.access_count > 1
