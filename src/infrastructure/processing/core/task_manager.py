"""
Task management with dependency and lifecycle tracking.
"""
import asyncio
from collections import defaultdict, deque
from typing import Dict, List, Set

from .models import ProcessingTask, TaskResult, TaskStatus


class TaskManager:
    """
    Manages the entire lifecycle of tasks, including registration,
    dependency tracking, and completion status.
    """

    def __init__(self) -> None:
        self.tasks: Dict[str, ProcessingTask] = {}
        self.results: Dict[str, TaskResult] = {}
        self.dependencies: Dict[str, Set[str]] = defaultdict(set)
        self.dependents: Dict[str, Set[str]] = defaultdict(set)
        self.completed_tasks: deque = deque(
            maxlen=1000)  # Cache of recent completions
        self._lock = asyncio.Lock()

    async def register_task(self, task: ProcessingTask) -> None:
        """Registers a new task and its dependencies."""
        async with self._lock:
            if task.id in self.tasks:
                return  # Avoid re-registering
            self.tasks[task.id] = task
            for dep_id in task.depends_on:
                self.dependencies[task.id].add(dep_id)
                self.dependents[dep_id].add(task.id)

    async def complete_task(self, task_id: str, result: TaskResult) -> List[str]:
        """
        Marks a task as complete, records its result, and determines which
        dependent tasks are now ready to run.
        """
        async with self._lock:
            if task_id not in self.tasks:
                return []

            task = self.tasks[task_id]
            task.status = result.status
            task.completed_at = result.completed_at
            self.results[task_id] = result

            if result.status == TaskStatus.COMPLETED:
                self.completed_tasks.append(task_id)

            # Check dependents to see if they are now ready
            ready_tasks = []
            if task_id in self.dependents:
                for dependent_id in self.dependents[task_id]:
                    if self._is_task_ready(dependent_id):
                        ready_tasks.append(dependent_id)
            return ready_tasks

    def _is_task_ready(self, task_id: str) -> bool:
        """
        Checks if a task is ready to be executed by verifying that all of
        its dependencies have been successfully completed.
        """
        task = self.tasks.get(task_id)
        if not task or task.status != TaskStatus.PENDING:
            return False

        for dep_id in self.dependencies.get(task_id, set()):
            dep_result = self.results.get(dep_id)
            if not dep_result or dep_result.status != TaskStatus.COMPLETED:
                return False
        return True

    async def get_ready_tasks(self) -> List[ProcessingTask]:
        """Returns a list of all tasks that are pending and have their dependencies met."""
        async with self._lock:
            return [
                task for task in self.tasks.values()
                if task.status == TaskStatus.PENDING and self._is_task_ready(task.id)
            ]

    async def cancel_task_with_dependents(self, task_id: str) -> bool:
        """
        Cancels a specific task and all of its recursive dependents.
        """
        async with self._lock:
            if task_id not in self.tasks or self.tasks[task_id].status == TaskStatus.CANCELLED:
                return False

            tasks_to_cancel = [task_id]
            i = 0
            while i < len(tasks_to_cancel):
                current_task_id = tasks_to_cancel[i]
                i += 1

                if current_task_id in self.tasks:
                    self.tasks[current_task_id].status = TaskStatus.CANCELLED
                    # Find tasks that depend on the cancelled task and add them to the list
                    for dependent_id in self.dependents.get(current_task_id, []):
                        if dependent_id not in tasks_to_cancel:
                            tasks_to_cancel.append(dependent_id)
            return True

    async def get_task(self, task_id: str) -> ProcessingTask | None:
        """Retrieves a task by its ID."""
        async with self._lock:
            return self.tasks.get(task_id)

    async def get_result(self, task_id: str) -> TaskResult | None:
        """Retrieves the result of a task by its ID."""
        async with self._lock:
            return self.results.get(task_id)
