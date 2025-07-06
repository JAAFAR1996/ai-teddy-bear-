import asyncio
import time
from typing import Callable, List

from ..smart_fuzzer import ChildContext
from .models import PerformanceMetric, PerformanceResult, TestType


async def run_baseline_test(
    target_function: Callable, interaction_patterns: List, performance_targets: dict
) -> List[PerformanceResult]:
    """Run baseline performance test"""
    results = []

    # Test single request performance
    for pattern in interaction_patterns:
        for input_text in pattern["inputs"][:2]:  # Test 2 inputs per pattern
            start_time = time.perf_counter()

            try:
                # Simulate child context
                context = ChildContext(age=7, emotion="happy")

                # Execute test
                if asyncio.iscoroutinefunction(target_function):
                    await target_function(input_text, context)
                else:
                    target_function(input_text, context)

                response_time = (time.perf_counter() - start_time) * 1000
                success = response_time <= pattern["expected_response_time_ms"]

                result = PerformanceResult(
                    test_name=f"baseline_{pattern['name'].lower().replace(' ', '_')}",
                    test_type=TestType.LOAD_TEST,
                    metric=PerformanceMetric.RESPONSE_TIME,
                    value=response_time,
                    unit="ms",
                    timestamp=time.time(),
                    success=success,
                )
                results.append(result)

            except Exception as e:
                result = PerformanceResult(
                    test_name=f"baseline_{pattern['name'].lower().replace(' ', '_')}",
                    test_type=TestType.LOAD_TEST,
                    metric=PerformanceMetric.ERROR_RATE,
                    value=1.0,
                    unit="ratio",
                    timestamp=time.time(),
                    success=False,
                    error_message=str(e),
                )
                results.append(result)

    return results
