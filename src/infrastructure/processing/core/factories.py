"""
Factory and utility functions for the async processing system.
"""
from typing import Any, Dict, Union

from .models import ProcessingTask, ProcessingType, TaskPriority
from .processor import AdvancedAsyncProcessor


async def create_processor(**kwargs) -> AdvancedAsyncProcessor:
    """
    Factory function to create and start a new AdvancedAsyncProcessor instance.
    """
    processor = AdvancedAsyncProcessor(**kwargs)
    await processor.start()
    return processor


def create_task(
    task_type: Union[ProcessingType, str],
    payload: Dict[str, Any],
    priority: Union[TaskPriority, int] = TaskPriority.NORMAL,
    **kwargs,
) -> ProcessingTask:
    """
    A convenience function for creating a ProcessingTask object.
    """
    if isinstance(task_type, str):
        try:
            task_type = ProcessingType(task_type)
        except ValueError:
            raise ValueError(f"'{task_type}' is not a valid ProcessingType.")

    if isinstance(priority, int):
        try:
            priority = TaskPriority(priority)
        except ValueError:
            raise ValueError(f"'{priority}' is not a valid TaskPriority.")

    return ProcessingTask(
        task_type=task_type, payload=payload, priority=priority, **kwargs
    )
