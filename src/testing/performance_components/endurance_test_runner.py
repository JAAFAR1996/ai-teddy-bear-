import asyncio
import logging
import statistics
import time
from typing import Callable, List

from ..smart_fuzzer import ChildContext
from .models import PerformanceMetric, PerformanceResult, TestType

logger = logging.getLogger(__name__)


async def run_endurance_test(
    target_function: Callable,
) -> List[PerformanceResult]:
    """Run endurance testing for extended periods"""
    logger.info("Running endurance test (abbreviated for demo)...")

    results = []

    # Abbreviated endurance test (normally would run for hours)
    test_duration = 30  # 30 seconds instead of hours
    start_time = time.time()
    end_time = start_time + test_duration

    request_count = 0
    error_count = 0
    response_times = []

    while time.time() < end_time:
        try:
            request_start = time.perf_counter()

            context = ChildContext(age=7, emotion="happy")

            if asyncio.iscoroutinefunction(target_function):
                await target_function("endurance test", context)
            else:
                target_function("endurance test", context)

            response_time = (time.perf_counter() - request_start) * 1000
            response_times.append(response_time)
            request_count += 1

            await asyncio.sleep(0.1)  # Small delay between requests

        except Exception as e:
            error_count += 1
            logger.error(f"Endurance test error: {e}")

    # Check for performance degradation over time
    if response_times:
        first_half = response_times[: len(response_times) // 2]
        second_half = response_times[len(response_times) // 2:]

        first_avg = statistics.mean(first_half) if first_half else 0
        second_avg = statistics.mean(second_half) if second_half else 0

        # Performance should not degrade more than 20%
        degradation = (second_avg - first_avg) / \
            first_avg if first_avg > 0 else 0
        performance_stable = degradation <= 0.2
    else:
        performance_stable = False

    error_rate = (
        error_count / (request_count + error_count)
        if (request_count + error_count) > 0
        else 1.0
    )

    results.extend(
        [
            PerformanceResult(
                test_name="endurance_test_stability",
                test_type=TestType.ENDURANCE_TEST,
                metric=PerformanceMetric.RESPONSE_TIME,
                value=degradation * 100 if response_times else 100,
                unit="percent_degradation",
                timestamp=time.time(),
                success=performance_stable,
            ),
            PerformanceResult(
                test_name="endurance_test_reliability",
                test_type=TestType.ENDURANCE_TEST,
                metric=PerformanceMetric.ERROR_RATE,
                value=error_rate,
                unit="ratio",
                timestamp=time.time(),
                success=error_rate <= 0.01,
            ),
        ]
    )

    return results
