import asyncio
import logging
import statistics
import time
from typing import Callable, List

import psutil

from ..smart_fuzzer import ChildContext
from .models import PerformanceMetric, PerformanceResult, TestType

logger = logging.getLogger(__name__)


async def _single_performance_request(
    target_function: Callable, test_context: str
):
    """Execute a single performance request"""
    try:
        context = ChildContext(age=7, emotion="happy")

        if asyncio.iscoroutinefunction(target_function):
            return await target_function(
                f"test request for {test_context}", context
            )
        else:
            return target_function(
                f"test request for {test_context}", context)
    except Exception as e:
        raise e


async def run_resource_test(
    target_function: Callable, performance_targets: dict
) -> List[PerformanceResult]:
    """Run resource utilization testing"""
    logger.info("Running resource utilization test...")

    results = []

    # Monitor resource usage during load
    initial_memory = psutil.virtual_memory().used
    psutil.cpu_percent()  # Call once to initialize

    # Run sustained load
    load_tasks = []
    for _ in range(50):
        task = _single_performance_request(
            target_function, "resource test")
        load_tasks.append(task)

    # Monitor resources during execution
    memory_measurements = []
    cpu_measurements = []

    async def monitor_resources():
        for _ in range(10):  # Monitor for 10 intervals
            memory_measurements.append(psutil.virtual_memory().used)
            cpu_measurements.append(psutil.cpu_percent())
            await asyncio.sleep(0.1)

    # Run load and monitoring concurrently
    monitor_task = asyncio.create_task(monitor_resources())
    await asyncio.gather(*load_tasks, return_exceptions=True)
    await monitor_task

    # Calculate resource usage
    max_memory_used = max(memory_measurements) - initial_memory
    max_memory_mb = max_memory_used / (1024 * 1024)
    avg_cpu_usage = statistics.mean(cpu_measurements)

    results.extend(
        [
            PerformanceResult(
                test_name="resource_test_memory_usage",
                test_type=TestType.VOLUME_TEST,
                metric=PerformanceMetric.MEMORY_USAGE,
                value=max_memory_mb,
                unit="MB",
                timestamp=time.time(),
                success=max_memory_mb <= performance_targets["max_memory_mb"],
            ),
            PerformanceResult(
                test_name="resource_test_cpu_usage",
                test_type=TestType.VOLUME_TEST,
                metric=PerformanceMetric.CPU_USAGE,
                value=avg_cpu_usage,
                unit="percent",
                timestamp=time.time(),
                success=avg_cpu_usage <= performance_targets["max_cpu_percent"],
            ),
        ])

    return results
