"""
Task processor for database operations.
"""
import asyncio

from ..models import ProcessingTask


async def process_database_operation(task: ProcessingTask) -> dict:
    """
    Processes a generic database operation task. In a real implementation, this
    would interact with a database repository or client.
    """
    operation = task.payload.get("operation")
    if not operation:
        raise ValueError("A database operation must be specified.")

    # Mock database interaction
    await asyncio.sleep(0.05)  # DB operations should be fast

    return {
        "operation": operation,
        "table": task.payload.get("table", "unknown"),
        "success": True,
        "affected_rows": 1,
    }
