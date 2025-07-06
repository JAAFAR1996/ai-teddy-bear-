"""
Task processor for custom, user-defined tasks.
"""
import asyncio

from ..models import ProcessingTask


async def process_custom(task: ProcessingTask) -> dict:
    """
    Processes a custom task by executing a user-provided callable.
    """
    custom_processor = task.payload.get("processor")
    if not callable(custom_processor):
        raise ValueError(
            "A callable 'processor' must be provided in the payload for custom tasks.")

    if asyncio.iscoroutinefunction(custom_processor):
        return await custom_processor(task.payload)
    else:
        # For synchronous custom processors, consider running in a thread pool
        # in the main processor logic to avoid blocking the event loop.
        return custom_processor(task.payload)
