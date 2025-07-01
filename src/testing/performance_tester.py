from typing import Any, Dict, List, Optional

"""
Performance Tester for AI Teddy Bear System
==========================================

Comprehensive performance testing framework focusing on
response times, scalability, and resource utilization
for optimal child experience.
"""

import asyncio
import json
import logging
import statistics
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

import memory_profiler
import psutil

logger = logging.getLogger(__name__)


class PerformanceMetric(Enum):
    """Types of performance metrics"""

    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"
    CONCURRENCY = "concurrency"
    LATENCY = "latency"
    ERROR_RATE = "error_rate"
    RESOURCE_UTILIZATION = "resource_utilization"


class TestType(Enum):
    """Types of performance tests"""

    LOAD_TEST = "load_test"
    STRESS_TEST = "stress_test"
    SPIKE_TEST = "spike_test"
    VOLUME_TEST = "volume_test"
    ENDURANCE_TEST = "endurance_test"
    SCALABILITY_TEST = "scalability_test"


@dataclass
class PerformanceResult:
    """Result from a performance test"""

    test_name: str
    test_type: TestType
    metric: PerformanceMetric
    value: float
    unit: str
    timestamp: float
    success: bool
    error_message: Optional[str] = None


@dataclass
class LoadTestConfig:
    """Configuration for load testing"""

    concurrent_users: int = 10
    test_duration_seconds: int = 60
    ramp_up_time_seconds: int = 10
    target_rps: Optional[int] = None  # Requests per second
    max_response_time_ms: int = 500
    acceptable_error_rate: float = 0.01  # 1%


@dataclass
class PerformanceReport:
    """Comprehensive performance test report"""

    test_suite_name: str
    start_time: float
    end_time: float
    total_duration: float
    results: List[PerformanceResult]
    summary_metrics: Dict[str, Any]
    recommendations: List[str]
    pass_fail_status: bool


class PerformanceTester:
    """
    Comprehensive performance testing framework specifically
    designed for child-facing AI systems with strict response
    time requirements.
    """

    def __init__(self):
        self.results = []
        self.baseline_metrics = {}

        # Child experience performance targets
        self.performance_targets = {
            "max_response_time_ms": 500,  # Maximum response time for child engagement
            "average_response_time_ms": 200,  # Target average response time
            "max_memory_mb": 512,  # Maximum memory usage
            "max_cpu_percent": 80,  # Maximum CPU usage
            "min_throughput_rps": 100,  # Minimum requests per second
            "max_error_rate": 0.01,  # Maximum 1% error rate
            "concurrent_users_target": 1000,  # Target concurrent users
        }

        # Child interaction patterns for realistic testing
        self.child_interaction_patterns = [
            {
                "name": "Quick Questions",
                "inputs": ["What time is it?", "Tell me a joke", "How are you?"],
                "expected_response_time_ms": 150,
                "frequency_percent": 40,
            },
            {
                "name": "Story Requests",
                "inputs": ["Tell me a story", "Read me a bedtime story"],
                "expected_response_time_ms": 300,
                "frequency_percent": 25,
            },
            {
                "name": "Learning Queries",
                "inputs": ["Help with math", "What is science?", "Teach me"],
                "expected_response_time_ms": 400,
                "frequency_percent": 20,
            },
            {
                "name": "Emotional Support",
                "inputs": ["I am sad", "I need help", "I am scared"],
                "expected_response_time_ms": 200,  # Quick response needed
                "frequency_percent": 15,
            },
        ]

    async def run_comprehensive_performance_test(
        self, target_function: Callable, config: Optional[LoadTestConfig] = None
    ) -> PerformanceReport:
        """
        Run comprehensive performance testing suite

        Args:
            target_function: Function to test for performance
            config: Load test configuration

        Returns:
            Comprehensive performance report
        """
        config = config or LoadTestConfig()
        start_time = time.time()

        logger.info("🚀 Starting comprehensive performance testing")

        test_results = []

        # Baseline performance test
        baseline_results = await self._run_baseline_test(target_function)
        test_results.extend(baseline_results)

        # Load testing
        load_results = await self._run_load_test(target_function, config)
        test_results.extend(load_results)

        # Stress testing
        stress_results = await self._run_stress_test(target_function)
        test_results.extend(stress_results)

        # Spike testing
        spike_results = await self._run_spike_test(target_function)
        test_results.extend(spike_results)

        # Memory and resource testing
        resource_results = await self._run_resource_test(target_function)
        test_results.extend(resource_results)

        # Concurrency testing
        concurrency_results = await self._run_concurrency_test(target_function)
        test_results.extend(concurrency_results)

        # Endurance testing
        endurance_results = await self._run_endurance_test(target_function)
        test_results.extend(endurance_results)

        end_time = time.time()

        # Generate comprehensive report
        report = await self._generate_performance_report(
            test_results, start_time, end_time
        )

        logger.info(f"✅ Performance testing complete: {report.pass_fail_status}")

        return report

    async def _run_baseline_test(
        self, target_function: Callable
    ) -> List[PerformanceResult]:
        """Run baseline performance test"""
        logger.info("Running baseline performance test...")

        results = []

        # Test single request performance
        for pattern in self.child_interaction_patterns:
            for input_text in pattern["inputs"][:2]:  # Test 2 inputs per pattern
                start_time = time.perf_counter()

                try:
                    # Simulate child context
                    from .smart_fuzzer import ChildContext

                    context = ChildContext(age=7, emotion="happy")

                    # Execute test
                    if asyncio.iscoroutinefunction(target_function):
                        response = await target_function(input_text, context)
                    else:
                        response = target_function(input_text, context)

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

    async def _run_load_test(
        self, target_function: Callable, config: LoadTestConfig
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
                    import random

                    pattern = random.choice(self.child_interaction_patterns)
                    input_text = random.choice(pattern["inputs"])

                    request_start = time.perf_counter()
                    total_requests += 1

                    try:
                        from .smart_fuzzer import ChildContext

                        context = ChildContext(
                            age=random.randint(3, 12),
                            emotion=random.choice(["happy", "excited", "curious"]),
                        )

                        if asyncio.iscoroutinefunction(target_function):
                            response = await target_function(input_text, context)
                        else:
                            response = target_function(input_text, context)

                        response_time = (time.perf_counter() - request_start) * 1000
                        response_times.append(response_time)

                        # Small delay to simulate realistic user behavior
                        await asyncio.sleep(random.uniform(0.1, 1.0))

                    except Exception as e:
                        error_count += 1
                        logger.error(f"Load test error: {e}")

                    # Break if test duration exceeded
                    if time.time() >= end_time:
                        break

        # Run concurrent user simulations
        tasks = [single_user_simulation() for _ in range(config.concurrent_users)]
        await asyncio.gather(*tasks, return_exceptions=True)

        # Calculate metrics
        if response_times:
            avg_response_time = statistics.mean(response_times)
            median_response_time = statistics.median(response_times)
            p95_response_time = statistics.quantiles(response_times, n=20)[
                18
            ]  # 95th percentile
            min_response_time = min(response_times)
            max_response_time = max(response_times)
        else:
            avg_response_time = median_response_time = p95_response_time = 0
            min_response_time = max_response_time = 0

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
                    <= self.performance_targets["average_response_time_ms"],
                ),
                PerformanceResult(
                    test_name="load_test_p95_response_time",
                    test_type=TestType.LOAD_TEST,
                    metric=PerformanceMetric.LATENCY,
                    value=p95_response_time,
                    unit="ms",
                    timestamp=time.time(),
                    success=p95_response_time
                    <= self.performance_targets["max_response_time_ms"],
                ),
                PerformanceResult(
                    test_name="load_test_throughput",
                    test_type=TestType.LOAD_TEST,
                    metric=PerformanceMetric.THROUGHPUT,
                    value=throughput,
                    unit="rps",
                    timestamp=time.time(),
                    success=throughput
                    >= self.performance_targets["min_throughput_rps"],
                ),
                PerformanceResult(
                    test_name="load_test_error_rate",
                    test_type=TestType.LOAD_TEST,
                    metric=PerformanceMetric.ERROR_RATE,
                    value=error_rate,
                    unit="ratio",
                    timestamp=time.time(),
                    success=error_rate <= self.performance_targets["max_error_rate"],
                ),
            ]
        )

        return results

    async def _run_stress_test(
        self, target_function: Callable
    ) -> List[PerformanceResult]:
        """Run stress testing to find breaking point"""
        logger.info("Running stress test to find system limits...")

        results = []

        # Gradually increase load until system breaks
        stress_levels = [50, 100, 200, 500, 1000, 2000]

        for stress_level in stress_levels:
            logger.info(f"Testing stress level: {stress_level} concurrent requests")

            start_time = time.perf_counter()
            error_count = 0
            successful_requests = 0

            async def stress_request():
                nonlocal error_count, successful_requests
                try:
                    from .smart_fuzzer import ChildContext

                    context = ChildContext(age=7, emotion="neutral")

                    if asyncio.iscoroutinefunction(target_function):
                        response = await target_function("test stress", context)
                    else:
                        response = target_function("test stress", context)

                    successful_requests += 1
                except Exception as e:
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
                logger.warning(f"System breaking at {stress_level} concurrent users")
                break

        return results

    async def _run_spike_test(
        self, target_function: Callable
    ) -> List[PerformanceResult]:
        """Run spike testing for sudden load increases"""
        logger.info("Running spike test for sudden load increases...")

        results = []

        # Simulate sudden spike in load
        normal_load = 10
        spike_load = 100

        # Normal load baseline
        start_time = time.perf_counter()
        normal_tasks = []

        for _ in range(normal_load):
            task = self._single_performance_request(target_function, "normal load")
            normal_tasks.append(task)

        normal_responses = await asyncio.gather(*normal_tasks, return_exceptions=True)
        normal_duration = time.perf_counter() - start_time

        # Sudden spike
        start_time = time.perf_counter()
        spike_tasks = []

        for _ in range(spike_load):
            task = self._single_performance_request(target_function, "spike load")
            spike_tasks.append(task)

        spike_responses = await asyncio.gather(*spike_tasks, return_exceptions=True)
        spike_duration = time.perf_counter() - start_time

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

    async def _run_resource_test(
        self, target_function: Callable
    ) -> List[PerformanceResult]:
        """Run resource utilization testing"""
        logger.info("Running resource utilization test...")

        results = []

        # Monitor resource usage during load
        initial_memory = psutil.virtual_memory().used
        initial_cpu = psutil.cpu_percent()

        # Run sustained load
        load_tasks = []
        for _ in range(50):
            task = self._single_performance_request(target_function, "resource test")
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
        load_responses = await asyncio.gather(*load_tasks, return_exceptions=True)
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
                    success=max_memory_mb <= self.performance_targets["max_memory_mb"],
                ),
                PerformanceResult(
                    test_name="resource_test_cpu_usage",
                    test_type=TestType.VOLUME_TEST,
                    metric=PerformanceMetric.CPU_USAGE,
                    value=avg_cpu_usage,
                    unit="percent",
                    timestamp=time.time(),
                    success=avg_cpu_usage
                    <= self.performance_targets["max_cpu_percent"],
                ),
            ]
        )

        return results

    async def _run_concurrency_test(
        self, target_function: Callable
    ) -> List[PerformanceResult]:
        """Run concurrency testing"""
        logger.info("Running concurrency test...")

        results = []

        # Test different concurrency levels
        concurrency_levels = [1, 5, 10, 25, 50, 100]

        for level in concurrency_levels:
            start_time = time.perf_counter()

            tasks = []
            for _ in range(level):
                task = self._single_performance_request(
                    target_function, f"concurrency_{level}"
                )
                tasks.append(task)

            responses = await asyncio.gather(*tasks, return_exceptions=True)
            duration = time.perf_counter() - start_time

            success_count = len([r for r in responses if not isinstance(r, Exception)])
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

    async def _run_endurance_test(
        self, target_function: Callable
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

                from .smart_fuzzer import ChildContext

                context = ChildContext(age=7, emotion="happy")

                if asyncio.iscoroutinefunction(target_function):
                    response = await target_function("endurance test", context)
                else:
                    response = target_function("endurance test", context)

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
            second_half = response_times[len(response_times) // 2 :]

            first_avg = statistics.mean(first_half) if first_half else 0
            second_avg = statistics.mean(second_half) if second_half else 0

            # Performance should not degrade more than 20%
            degradation = (second_avg - first_avg) / first_avg if first_avg > 0 else 0
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

    async def _single_performance_request(
        self, target_function: Callable, test_context: str
    ):
        """Execute a single performance request"""
        try:
            from .smart_fuzzer import ChildContext

            context = ChildContext(age=7, emotion="happy")

            if asyncio.iscoroutinefunction(target_function):
                return await target_function(
                    f"test request for {test_context}", context
                )
            else:
                return target_function(f"test request for {test_context}", context)
        except Exception as e:
            raise e

    async def _generate_performance_report(
        self, test_results: List[PerformanceResult], start_time: float, end_time: float
    ) -> PerformanceReport:
        """Generate comprehensive performance report"""

        # Calculate summary metrics
        total_tests = len(test_results)
        passed_tests = len([r for r in test_results if r.success])
        pass_rate = passed_tests / total_tests if total_tests > 0 else 0

        # Group results by metric type
        metrics_summary = {}
        for metric in PerformanceMetric:
            metric_results = [r for r in test_results if r.metric == metric]
            if metric_results:
                values = [r.value for r in metric_results]
                metrics_summary[metric.value] = {
                    "count": len(metric_results),
                    "average": statistics.mean(values),
                    "min": min(values),
                    "max": max(values),
                    "passed": len([r for r in metric_results if r.success]),
                }

        # Generate recommendations
        recommendations = self._generate_performance_recommendations(test_results)

        # Determine overall pass/fail
        overall_pass = pass_rate >= 0.8  # 80% of tests must pass

        report = PerformanceReport(
            test_suite_name="AI Teddy Bear Performance Test Suite",
            start_time=start_time,
            end_time=end_time,
            total_duration=end_time - start_time,
            results=test_results,
            summary_metrics={
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "pass_rate": pass_rate,
                "metrics_breakdown": metrics_summary,
            },
            recommendations=recommendations,
            pass_fail_status=overall_pass,
        )

        return report

    def _generate_performance_recommendations(
        self, test_results: List[PerformanceResult]
    ) -> List[str]:
        """Generate performance recommendations based on test results"""
        recommendations = []

        # Check response times
        response_time_results = [
            r for r in test_results if r.metric == PerformanceMetric.RESPONSE_TIME
        ]
        if response_time_results:
            avg_response_time = statistics.mean(
                [r.value for r in response_time_results]
            )
            if avg_response_time > self.performance_targets["average_response_time_ms"]:
                recommendations.append(
                    f"Average response time ({avg_response_time:.1f}ms) exceeds target "
                    f"({self.performance_targets['average_response_time_ms']}ms). "
                    "Consider optimizing AI processing or implementing caching."
                )

        # Check error rates
        error_rate_results = [
            r for r in test_results if r.metric == PerformanceMetric.ERROR_RATE
        ]
        if error_rate_results:
            max_error_rate = max([r.value for r in error_rate_results])
            if max_error_rate > self.performance_targets["max_error_rate"]:
                recommendations.append(
                    f"Error rate ({max_error_rate:.2%}) exceeds acceptable threshold "
                    f"({self.performance_targets['max_error_rate']:.2%}). "
                    "Implement better error handling and system resilience."
                )

        # Check memory usage
        memory_results = [
            r for r in test_results if r.metric == PerformanceMetric.MEMORY_USAGE
        ]
        if memory_results:
            max_memory = max([r.value for r in memory_results])
            if max_memory > self.performance_targets["max_memory_mb"]:
                recommendations.append(
                    f"Memory usage ({max_memory:.1f}MB) exceeds target "
                    f"({self.performance_targets['max_memory_mb']}MB). "
                    "Optimize memory usage and implement garbage collection."
                )

        # Check CPU usage
        cpu_results = [
            r for r in test_results if r.metric == PerformanceMetric.CPU_USAGE
        ]
        if cpu_results:
            max_cpu = max([r.value for r in cpu_results])
            if max_cpu > self.performance_targets["max_cpu_percent"]:
                recommendations.append(
                    f"CPU usage ({max_cpu:.1f}%) exceeds target "
                    f"({self.performance_targets['max_cpu_percent']}%). "
                    "Optimize algorithms and consider horizontal scaling."
                )

        # Check throughput
        throughput_results = [
            r for r in test_results if r.metric == PerformanceMetric.THROUGHPUT
        ]
        if throughput_results:
            min_throughput = min([r.value for r in throughput_results])
            if min_throughput < self.performance_targets["min_throughput_rps"]:
                recommendations.append(
                    f"Throughput ({min_throughput:.1f} RPS) below target "
                    f"({self.performance_targets['min_throughput_rps']} RPS). "
                    "Consider performance optimization and scaling strategies."
                )

        # Child-specific recommendations
        recommendations.extend(
            [
                "Ensure response times remain under 500ms for optimal child engagement",
                "Monitor performance during peak usage times (after school, weekends)",
                "Implement progressive loading for story content to reduce perceived latency",
                "Consider edge computing for reduced latency in different geographic regions",
                "Implement performance monitoring and alerting for production environment",
            ]
        )

        return recommendations

    async def export_performance_report(
        self, report: PerformanceReport, output_file: str
    ) -> bool:
        """Export performance report to file"""
        try:
            report_data = {
                "test_suite_name": report.test_suite_name,
                "timestamp": time.time(),
                "start_time": report.start_time,
                "end_time": report.end_time,
                "total_duration": report.total_duration,
                "summary_metrics": report.summary_metrics,
                "pass_fail_status": report.pass_fail_status,
                "recommendations": report.recommendations,
                "detailed_results": [
                    {
                        "test_name": r.test_name,
                        "test_type": r.test_type.value,
                        "metric": r.metric.value,
                        "value": r.value,
                        "unit": r.unit,
                        "success": r.success,
                        "error_message": r.error_message,
                    }
                    for r in report.results
                ],
            }

            with open(output_file, "w") as f:
                json.dump(report_data, f, indent=2)

            logger.info(f"Performance report exported to {output_file}")
            return True

        except Exception as e:
            logger.error(f"Failed to export performance report: {e}")
            return False
