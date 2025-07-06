import asyncio
import logging
import time
from typing import Callable, List

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


async def run_spike_test(
    target_function: Callable,
) -> List[PerformanceResult]:
    """Run spike testing for sudden load increases"""
    logger.info("Running spike test for sudden load increases...")

    results = []

    # Simulate sudden spike in load
    normal_load = 10
    spike_load = 100

    # Normal load baseline
    normal_tasks = []

    for _ in range(normal_load):
        task = _single_performance_request(
            target_function, "normal load")
        normal_tasks.append(task)

    normal_responses = await asyncio.gather(*normal_tasks, return_exceptions=True)

    # Sudden spike
    spike_tasks = []

    for _ in range(spike_load):
        task = _single_performance_request(
            target_function, "spike load")
        spike_tasks.append(task)

    spike_responses = await asyncio.gather(*spike_tasks, return_exceptions=True)

    # Analyze results
    normal_success_rate = len(
        [r for r in normal_responses if not isinstance(r, Exception)]
    ) / len(normal_responses)
    spike_success_rate = len(
        [r for r in spike_responses if not isinstance(r, Exception)]
    ) / len(spike_responses)

    # System should handle spike with reasonable degradation
    spike_success = spike_success_rate >= 0.8  # Allow 20% degradation

    results.extend(
        [
            PerformanceResult(
                test_name="spike_test_normal_load",
                test_type=TestType.SPIKE_TEST,
                metric=PerformanceMetric.ERROR_RATE,
                value=1.0 - normal_success_rate,
                unit="ratio",
                timestamp=time.time(),
                success=normal_success_rate >= 0.95,
            ),
            PerformanceResult(
                test_name="spike_test_spike_load",
                test_type=TestType.SPIKE_TEST,
                metric=PerformanceMetric.ERROR_RATE,
                value=1.0 - spike_success_rate,
                unit="ratio",
                timestamp=time.time(),
                success=spike_success,
            ),
        ]
    )

    return results
