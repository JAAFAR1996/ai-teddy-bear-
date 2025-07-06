import asyncio
import logging
import secrets
import statistics
import time
from typing import Callable, List

from ..smart_fuzzer import ChildContext
from .models import (LoadTestConfig, PerformanceMetric, PerformanceResult,
                     TestType)

logger = logging.getLogger(__name__)


async def run_load_test(
    target_function: Callable, config: LoadTestConfig, performance_targets: dict
) -> List[PerformanceResult]:
    """Run load testing with multiple concurrent users"""
    logger.info(
        f"Running load test: {config.concurrent_users} users, {config.test_duration_seconds}s"
    )

    results = []
    response_times = []
    error_count = 0
    total_requests = 0

    start_time = time.time()
    end_time = start_time + config.test_duration_seconds

    # Create semaphore for controlling concurrency
    semaphore = asyncio.Semaphore(config.concurrent_users)

    async def single_user_simulation():
        nonlocal error_count, total_requests

        async with semaphore:
            while time.time() < end_time:
                # Select random interaction pattern
                emotions = ["happy", "excited", "curious"]
                emotion = secrets.choice(emotions)
                context = ChildContext(
                    # من 3 إلى 12 (Bandit_B311)
                    age=secrets.randbelow(10) + 3,
                    emotion=emotion,
                )

                request_start = time.perf_counter()
                total_requests += 1

                try:
                    if asyncio.iscoroutinefunction(target_function):
                        await target_function(context.input, context)
                    else:
                        target_function(context.input, context)

                    response_time = (
                        time.perf_counter() - request_start) * 1000
                    response_times.append(response_time)

                    # Small delay to simulate realistic user behavior
                    delay = (secrets.randbelow(91) + 10) / 100.0
                    await asyncio.sleep(delay)

                except Exception as e:
                    error_count += 1
                    logger.error(f"Load test error: {e}")

                # Break if test duration exceeded
                if time.time() >= end_time:
                    break

    # Run concurrent user simulations
    tasks = [single_user_simulation()
             for _ in range(config.concurrent_users)]
    await asyncio.gather(*tasks, return_exceptions=True)

    # Calculate metrics
    if response_times:
        avg_response_time = statistics.mean(response_times)
        p95_response_time = statistics.quantiles(response_times, n=20)[
            18
        ]  # 95th percentile
    else:
        avg_response_time = p95_response_time = 0

    error_rate = error_count / total_requests if total_requests > 0 else 1.0
    throughput = total_requests / config.test_duration_seconds

    # Create performance results
    results.extend(
        [
            PerformanceResult(
                test_name="load_test_avg_response_time",
                test_type=TestType.LOAD_TEST,
                metric=PerformanceMetric.RESPONSE_TIME,
                value=avg_response_time,
                unit="ms",
                timestamp=time.time(),
                success=avg_response_time
                <= performance_targets["average_response_time_ms"],
            ),
            PerformanceResult(
                test_name="load_test_p95_response_time",
                test_type=TestType.LOAD_TEST,
                metric=PerformanceMetric.LATENCY,
                value=p95_response_time,
                unit="ms",
                timestamp=time.time(),
                success=p95_response_time
                <= performance_targets["max_response_time_ms"],
            ),
            PerformanceResult(
                test_name="load_test_throughput",
                test_type=TestType.LOAD_TEST,
                metric=PerformanceMetric.THROUGHPUT,
                value=throughput,
                unit="rps",
                timestamp=time.time(),
                success=throughput
                >= performance_targets["min_throughput_rps"],
            ),
            PerformanceResult(
                test_name="load_test_error_rate",
                test_type=TestType.LOAD_TEST,
                metric=PerformanceMetric.ERROR_RATE,
                value=error_rate,
                unit="ratio",
                timestamp=time.time(),
                success=error_rate <= performance_targets["max_error_rate"],
            ),
        ]
    )

    return results
