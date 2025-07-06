import asyncio
import logging
import time
from typing import Callable, List

from ..smart_fuzzer import ChildContext
from .models import PerformanceMetric, PerformanceResult, TestType

logger = logging.getLogger(__name__)


async def run_stress_test(
    target_function: Callable,
) -> List[PerformanceResult]:
    """Run stress testing to find breaking point"""
    logger.info("Running stress test to find system limits...")

    results = []

    # Gradually increase load until system breaks
    stress_levels = [50, 100, 200, 500, 1000, 2000]

    for stress_level in stress_levels:
        logger.info(
            f"Testing stress level: {stress_level} concurrent requests")

        start_time = time.perf_counter()
        error_count = 0
        successful_requests = 0

        async def stress_request():
            nonlocal error_count, successful_requests
            try:
                context = ChildContext(age=7, emotion="neutral")

                if asyncio.iscoroutinefunction(target_function):
                    await target_function("test stress", context)
                else:
                    target_function("test stress", context)

                successful_requests += 1
            except Exception:
                error_count += 1

        # Run stress level
        tasks = [stress_request() for _ in range(stress_level)]
        await asyncio.gather(*tasks, return_exceptions=True)

        duration = time.perf_counter() - start_time
        total_requests = successful_requests + error_count
        error_rate = error_count / total_requests if total_requests > 0 else 1.0
        throughput = successful_requests / duration if duration > 0 else 0

        # Consider test failed if error rate > 10%
        success = error_rate <= 0.1

        result = PerformanceResult(
            test_name=f"stress_test_{stress_level}_users",
            test_type=TestType.STRESS_TEST,
            metric=PerformanceMetric.ERROR_RATE,
            value=error_rate,
            unit="ratio",
            timestamp=time.time(),
            success=success,
        )
        results.append(result)

        # Stop if system is breaking (error rate > 50%)
        if error_rate > 0.5:
            logger.warning(
                f"System breaking at {stress_level} concurrent users")
            break

    return results
