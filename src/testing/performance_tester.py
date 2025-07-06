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
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

import psutil
import secrets
from .smart_fuzzer import ChildContext
from .performance_components import (
    LoadTestConfig,
    PerformanceReport,
    export_performance_report,
    generate_performance_report,
    run_baseline_test,
    run_concurrency_test,
    run_endurance_test,
    run_load_test,
    run_resource_test,
    run_spike_test,
    run_stress_test,
)

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
        """
        config = config or LoadTestConfig()
        start_time = time.time()

        logger.info("🚀 Starting comprehensive performance testing")

        test_results = []

        # Baseline performance test
        baseline_results = await run_baseline_test(
            target_function, self.child_interaction_patterns, self.performance_targets
        )
        test_results.extend(baseline_results)

        # Load testing
        load_results = await run_load_test(target_function, config, self.performance_targets)
        test_results.extend(load_results)

        # Stress testing
        stress_results = await run_stress_test(target_function)
        test_results.extend(stress_results)

        # Spike testing
        spike_results = await run_spike_test(target_function)
        test_results.extend(spike_results)

        # Memory and resource testing
        resource_results = await run_resource_test(target_function, self.performance_targets)
        test_results.extend(resource_results)

        # Concurrency testing
        concurrency_results = await run_concurrency_test(target_function)
        test_results.extend(concurrency_results)

        # Endurance testing
        endurance_results = await run_endurance_test(target_function)
        test_results.extend(endurance_results)

        end_time = time.time()

        # Generate comprehensive report
        report = await generate_performance_report(
            test_results, start_time, end_time, self.performance_targets
        )

        logger.info(
            f"✅ Performance testing complete: {report.pass_fail_status}")

        return report

    async def export_performance_report(
        self, report: PerformanceReport, output_file: str
    ) -> bool:
        """Export performance report to file"""
        return await export_performance_report(report, output_file)
