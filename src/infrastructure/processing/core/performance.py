"""
Performance monitoring and metrics collection for the async processor.
"""
import time
from collections import defaultdict, deque
from typing import Any, Dict

from .models import ProcessingTask, TaskResult, TaskStatus


class PerformanceMonitor:
    """
    Tracks and provides performance metrics for the async processing system,
    including throughput, latency, and resource usage.
    """

    def __init__(self, history_len: int = 100):
        self.metrics = {
            "tasks_processed": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "tasks_cancelled": 0,
            "total_execution_time": 0.0,
            "peak_memory_usage": 0,
            "worker_utilization": defaultdict(float),
        }
        self.queue_size_history = deque(maxlen=history_len)
        self.throughput_history = deque(maxlen=history_len)
        self.start_time = time.monotonic()
        self._last_throughput_check = time.monotonic()
        self._last_task_count = 0

    def record_task_completion(self, task: ProcessingTask, result: TaskResult) -> None:
        """Records metrics from a completed task result."""
        self.metrics["tasks_processed"] += 1

        status_map = {
            TaskStatus.COMPLETED: "tasks_completed",
            TaskStatus.FAILED: "tasks_failed",
            TaskStatus.CANCELLED: "tasks_cancelled",
        }
        metric_key = status_map.get(result.status)
        if metric_key:
            self.metrics[metric_key] += 1

        self.metrics["total_execution_time"] += result.execution_time
        self.metrics["peak_memory_usage"] = max(
            self.metrics["peak_memory_usage"], result.memory_used
        )

        if task.worker_id:
            self.metrics["worker_utilization"][task.worker_id] += result.execution_time

    def record_queue_size(self, size: int) -> None:
        """Records the current size of the task queue for historical analysis."""
        self.queue_size_history.append((time.monotonic(), size))

    def calculate_and_record_throughput(self) -> float:
        """Calculates and records the current throughput in tasks per second."""
        current_time = time.monotonic()
        time_diff = current_time - self._last_throughput_check

        if time_diff < 1.0:
            return self.throughput_history[-1][1] if self.throughput_history else 0.0

        processed_now = self.metrics["tasks_processed"]
        task_diff = processed_now - self._last_task_count
        throughput = task_diff / time_diff

        self.throughput_history.append((current_time, throughput))
        self._last_throughput_check = current_time
        self._last_task_count = processed_now
        return throughput

    def get_summary(self) -> Dict[str, Any]:
        """Returns a summary of all collected performance metrics."""
        uptime = time.monotonic() - self.start_time
        total_processed = self.metrics["tasks_processed"]

        summary = self.metrics.copy()
        summary.update({
            "uptime_seconds": uptime,
            "average_tasks_per_second": total_processed / uptime if uptime > 0 else 0,
            "success_rate": (self.metrics["tasks_completed"] / total_processed * 100) if total_processed > 0 else 100,
            "average_execution_time": (self.metrics["total_execution_time"] / total_processed) if total_processed > 0 else 0,
            "peak_memory_usage_mb": self.metrics["peak_memory_usage"] / (1024 * 1024),
            "current_queue_size": self.queue_size_history[-1][1] if self.queue_size_history else 0,
            "current_throughput_tps": self.throughput_history[-1][1] if self.throughput_history else 0,
        })
        return summary
