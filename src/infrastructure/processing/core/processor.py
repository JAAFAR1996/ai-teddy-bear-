"""
The core AdvancedAsyncProcessor implementation.
"""
import asyncio
import logging
import signal
import sys
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from typing import Any, Callable, Dict, List, Optional, Set

from .models import ProcessingTask, ProcessingType, TaskResult, TaskStatus
from .performance import PerformanceMonitor
from .processors import (
    process_ai_response,
    process_audio_enhancement,
    process_audio_transcription,
    process_custom,
    process_data_analytics,
    process_database_operation,
    process_emotion_analysis,
    process_image_generation,
    process_image_processing,
    process_notification,
    process_text_analysis,
)
from .task_manager import TaskManager

logger = logging.getLogger(__name__)


class AdvancedAsyncProcessor:
    """
    High-performance async processor with task management, multiple execution
    contexts, and a pluggable processor architecture.
    """

    def __init__(
        self,
        max_workers: int = 10,
        max_thread_workers: int = 5,
        max_process_workers: int = 2,
        enable_monitoring: bool = True,
    ):
        self.max_workers = max_workers
        self.priority_queue = asyncio.PriorityQueue()
        self.task_manager = TaskManager()
        self.performance_monitor = PerformanceMonitor() if enable_monitoring else None

        self.workers: List[asyncio.Task] = []
        self._running = False
        self._shutdown_event = asyncio.Event()

        self.thread_executor = ThreadPoolExecutor(
            max_workers=max_thread_workers)
        self.process_executor = ProcessPoolExecutor(
            max_workers=max_process_workers)

        self.processors: Dict[ProcessingType, Callable] = {}
        self._register_default_processors()

        self.running_tasks: Dict[str, asyncio.Task] = {}
        self._setup_signal_handlers()

    def _register_default_processors(self):
        """Registers the default set of task processors."""
        self.register_processor(
            ProcessingType.AUDIO_TRANSCRIPTION, process_audio_transcription)
        self.register_processor(
            ProcessingType.AUDIO_ENHANCEMENT, process_audio_enhancement)
        self.register_processor(
            ProcessingType.AI_RESPONSE, process_ai_response)
        self.register_processor(
            ProcessingType.EMOTION_ANALYSIS, process_emotion_analysis)
        self.register_processor(
            ProcessingType.IMAGE_GENERATION, process_image_generation)
        self.register_processor(
            ProcessingType.IMAGE_PROCESSING, process_image_processing)
        self.register_processor(
            ProcessingType.TEXT_ANALYSIS, process_text_analysis)
        self.register_processor(
            ProcessingType.DATA_ANALYTICS, process_data_analytics)
        self.register_processor(
            ProcessingType.DATABASE_OPERATION, process_database_operation)
        self.register_processor(
            ProcessingType.NOTIFICATION, process_notification)
        self.register_processor(ProcessingType.CUSTOM, process_custom)

    def register_processor(self, task_type: ProcessingType, processor_func: Callable):
        """Registers or overrides a processor for a given task type."""
        self.processors[task_type] = processor_func
        logger.info(f"Registered processor for task type: {task_type.name}")

    def _setup_signal_handlers(self):
        if sys.platform != "win32":
            loop = asyncio.get_event_loop()
            for sig in (signal.SIGINT, signal.SIGTERM):
                loop.add_signal_handler(
                    sig, lambda: asyncio.create_task(self.shutdown()))

    async def start(self):
        if self._running:
            return
        self._running = True
        self.workers = [
            asyncio.create_task(self._worker(f"worker-{i}")) for i in range(self.max_workers)
        ]
        if self.performance_monitor:
            self.workers.append(asyncio.create_task(self._monitoring_loop()))
        logger.info(f"AsyncProcessor started with {self.max_workers} workers.")

    async def shutdown(self, timeout: float = 30.0):
        if not self._running:
            return
        logger.info("Initiating graceful shutdown...")
        self._running = False
        self._shutdown_event.set()

        for task in self.running_tasks.values():
            task.cancel()

        await asyncio.sleep(0.1)  # allow tasks to receive cancellation

        for _ in self.workers:
            await self.priority_queue.put(None)

        await asyncio.gather(*self.workers, return_exceptions=True)

        self.thread_executor.shutdown(wait=True)
        self.process_executor.shutdown(wait=True)
        logger.info("AsyncProcessor shutdown complete.")

    async def submit_task(self, task: ProcessingTask) -> str:
        await self.task_manager.register_task(task)
        if await self._is_task_ready(task):
            await self.priority_queue.put(task)
        return task.id

    async def _is_task_ready(self, task: ProcessingTask) -> bool:
        if task.status != TaskStatus.PENDING:
            return False
        if not task.depends_on:
            return True

        results = await asyncio.gather(*[self.task_manager.get_result(dep_id) for dep_id in task.depends_on])
        return all(res and res.status == TaskStatus.COMPLETED for res in results)

    async def _worker(self, worker_id: str):
        while self._running:
            try:
                task = await self.priority_queue.get()
                if task is None:
                    break

                self.running_tasks[task.id] = asyncio.current_task()
                await self._process_and_update(task, worker_id)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(
                    f"Worker {worker_id} encountered an error: {e}", exc_info=True)
            finally:
                if 'task' in locals() and task:
                    self.running_tasks.pop(task.id, None)
                    self.priority_queue.task_done()

    async def _process_and_update(self, task: ProcessingTask, worker_id: str):
        task.status = TaskStatus.RUNNING
        task.worker_id = worker_id
        start_time = time.monotonic()

        try:
            processor = self.processors[task.task_type]

            if task.cpu_intensive:
                result_data = await asyncio.get_running_loop().run_in_executor(
                    self.process_executor, processor, task
                )
            elif task.io_bound:
                result_data = await asyncio.get_running_loop().run_in_executor(
                    self.thread_executor, processor, task
                )
            else:
                result_data = await processor(task)

            result = TaskResult(
                task_id=task.id, status=TaskStatus.COMPLETED, result=result_data)
        except Exception as e:
            result = TaskResult(
                task_id=task.id, status=TaskStatus.FAILED, error=str(e))

        result.execution_time = time.monotonic() - start_time

        if self.performance_monitor:
            self.performance_monitor.record_task_completion(task, result)

        ready_tasks = await self.task_manager.complete_task(task.id, result)
        for ready_task_id in ready_tasks:
            ready_task = await self.task_manager.get_task(ready_task_id)
            if ready_task:
                await self.priority_queue.put(ready_task)

    async def _monitoring_loop(self):
        while self._running:
            await asyncio.sleep(5)
            self.performance_monitor.record_queue_size(
                self.priority_queue.qsize())
            self.performance_monitor.calculate_and_record_throughput()
