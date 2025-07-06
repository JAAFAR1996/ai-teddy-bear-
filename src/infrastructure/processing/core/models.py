"""
Data models for the asynchronous processing system.
"""
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Set, Union


class TaskStatus(Enum):
    """Defines the execution status of a task."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class TaskPriority(Enum):
    """Defines the priority levels for tasks to determine execution order."""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BATCH = 5


class ProcessingType(Enum):
    """Categorizes the types of processing tasks supported by the system."""
    AUDIO_TRANSCRIPTION = "audio_transcription"
    AUDIO_ENHANCEMENT = "audio_enhancement"
    AI_RESPONSE = "ai_response"
    EMOTION_ANALYSIS = "emotion_analysis"
    IMAGE_GENERATION = "image_generation"
    IMAGE_PROCESSING = "image_processing"
    TEXT_ANALYSIS = "text_analysis"
    DATA_ANALYTICS = "data_analytics"
    DATABASE_OPERATION = "database_operation"
    NOTIFICATION = "notification"
    CUSTOM = "custom"


@dataclass
class TaskResult:
    """Represents the result of a completed processing task."""
    task_id: str
    status: TaskStatus
    result: Any = None
    error: Union[str, None] = None
    execution_time: float = 0.0
    memory_used: int = 0  # in bytes
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Union[datetime, None] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProcessingTask:
    """
    Represents a unit of work to be executed by the processor, including all
    necessary metadata for scheduling, execution, and tracking.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_type: ProcessingType = ProcessingType.CUSTOM
    payload: Dict[str, Any] = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.NORMAL
    timeout: Union[float, None] = None
    retry_count: int = 0
    max_retries: int = 3
    callback: Union[Callable, None] = None
    depends_on: List[str] = field(default_factory=list)
    tags: Set[str] = field(default_factory=set)

    # Execution tracking
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Union[datetime, None] = None
    completed_at: Union[datetime, None] = None
    status: TaskStatus = TaskStatus.PENDING
    worker_id: Union[str, None] = None

    # Resource requirements
    cpu_intensive: bool = False
    memory_intensive: bool = False
    io_bound: bool = False

    def __lt__(self, other):
        """Allows tasks to be compared by priority, for use in a priority queue."""
        if not isinstance(other, ProcessingTask):
            return NotImplemented
        return self.priority.value < other.priority.value

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the task object to a dictionary."""
        return {
            "id": self.id,
            "task_type": self.task_type.value,
            "priority": self.priority.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "tags": list(self.tags),
            "worker_id": self.worker_id,
        }
