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


async def run_concurrency_test(
    target_function: Callable,
) -> List[PerformanceResult]:
    """Run concurrency testing"""
    logger.info("Running concurrency test...")

    results = []

    # Test different concurrency levels
    concurrency_levels = [1, 5, 10, 25, 50, 100]

    for level in concurrency_levels:
        tasks = []
        for _ in range(level):
            task = _single_performance_request(
                target_function, f"concurrency_{level}"
            )
            tasks.append(task)

        responses = await asyncio.gather(*tasks, return_exceptions=True)

        success_count = len(
            [r for r in responses if not isinstance(r, Exception)])
        success_rate = success_count / len(responses)

        result = PerformanceResult(
            test_name=f"concurrency_test_{level}_users",
            test_type=TestType.SCALABILITY_TEST,
            metric=PerformanceMetric.CONCURRENCY,
            value=success_rate,
            unit="ratio",
            timestamp=time.time(),
            success=success_rate >= 0.95,
        )
        results.append(result)

    return results
