"""
A high-performance, modular asynchronous processing system.
"""

from .factories import create_processor, create_task
from .models import (
    ProcessingTask,
    ProcessingType,
    TaskPriority,
    TaskResult,
    TaskStatus,
)
from .performance import PerformanceMonitor
from .processor import AdvancedAsyncProcessor
from .task_manager import TaskManager

__all__ = [
    # Main classes
    "AdvancedAsyncProcessor",
    "TaskManager",
    "PerformanceMonitor",
    # Models
    "ProcessingTask",
    "TaskResult",
    "ProcessingType",
    "TaskStatus",
    "TaskPriority",
    # Factories
    "create_processor",
    "create_task",
]
