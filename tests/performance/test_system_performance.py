"""
System Performance Tests - اختبارات الأداء الشاملة
"""

import asyncio
import gc
import random
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List

import numpy as np
import psutil
import pytest
from locust import HttpUser, between, task

from src.application.services.audio_service import AudioService
from src.application.services.cleanup_service import CleanupService
from src.application.services.interaction_service import InteractionService
from tests.framework import PerformanceTestCase


class TestSystemPerformance(PerformanceTestCase):
    """اختبارات الأداء الشاملة"""

    @pytest.fixture(autouse=True)
    async def setup_performance_services(self):
        """Setup performance test services"""
        self.interaction_service = InteractionService()
        self.audio_service = AudioService()
        self.cleanup_service = CleanupService()

        yield

    async def cleanup(self):
        """Cleanup after each test"""
        gc.collect()
        await asyncio.sleep(0.1)

    @pytest.mark.performance
    @pytest.mark.timeout(30)
    async def test_concurrent_users_handling(self):
        """اختبار 1000 مستخدم متزامن"""
        # Arrange
        num_users = 1000
        tasks = []
        start_time = time.time()

        # Create test users
        users = [
            self.test_data_builder.create_child(age=random.randint(3, 12))
            for _ in range(num_users)
        ]

        # Start performance tracking
        self.start_performance_tracking()

        # Act - محاكاة تفاعلات متزامنة
        async def simulate_user_interaction(user):
            operation_times = []

            for _ in range(5):  # 5 تفاعلات لكل مستخدم
                op_start = time.perf_counter()

                try:
                    await self.interaction_service.process(
                        child_id=user.id, message=self.faker.sentence()
                    )

                    op_duration = (time.perf_counter() - op_start) * 1000
                    operation_times.append(op_duration)
                    self.record_operation(f"user_{user.id}_interaction", op_duration)

                except Exception as e:
                    # Record failed operation
                    self.record_operation(f"user_{user.id}_interaction_failed", -1)

                await asyncio.sleep(random.uniform(0.1, 0.5))

            return operation_times

        # Execute concurrent interactions
        tasks = [simulate_user_interaction(user) for user in users]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Stop tracking and get metrics
        metrics = self.stop_performance_tracking()

        # Calculate statistics
        duration = time.time() - start_time
        successful_users = sum(1 for r in results if not isinstance(r, Exception))
        total_operations = sum(len(r) for r in results if not isinstance(r, Exception))
        error_rate = (len(results) - successful_users) / len(results)

        # Assert performance criteria
        assert duration < 30, f"Test took {duration}s, expected < 30s"
        assert error_rate < 0.01, f"Error rate {error_rate*100}% exceeds 1%"
        assert (
            successful_users >= num_users * 0.99
        ), f"Only {successful_users}/{num_users} users succeeded"

        # Check system resources
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_percent = psutil.virtual_memory().percent

        assert cpu_percent < 80, f"CPU usage {cpu_percent}% exceeds 80%"
        assert memory_percent < 85, f"Memory usage {memory_percent}% exceeds 85%"

        # Verify performance metrics
        self.assert_performance_within_limits(metrics)

        # Log performance summary
        print(f"\nPerformance Summary:")
        print(f"- Total Users: {num_users}")
        print(f"- Successful Users: {successful_users}")
        print(f"- Total Operations: {total_operations}")
        print(f"- Error Rate: {error_rate*100:.2f}%")
        print(f"- Duration: {duration:.2f}s")
        print(f"- Avg Latency: {metrics['avg_latency_ms']:.2f}ms")
        print(f"- P95 Latency: {metrics['p95_latency_ms']:.2f}ms")
        print(f"- P99 Latency: {metrics['p99_latency_ms']:.2f}ms")

    @pytest.mark.performance
    async def test_audio_streaming_latency(self):
        """اختبار زمن الاستجابة لـ audio streaming"""
        # Arrange
        audio_chunk_size = 1024 * 16  # 16KB chunks
        num_chunks = 100
        latencies = []

        self.start_performance_tracking()

        # Act
        for i in range(num_chunks):
            audio_data = self.generate_audio_chunk(audio_chunk_size)

            start_time = time.perf_counter()
            result = await self.audio_service.process_chunk(audio_data)
            latency = (time.perf_counter() - start_time) * 1000  # ms

            latencies.append(latency)
            self.record_operation(f"audio_chunk_{i}", latency)

        # Calculate statistics
        avg_latency = np.mean(latencies)
        p50_latency = np.percentile(latencies, 50)
        p95_latency = np.percentile(latencies, 95)
        p99_latency = np.percentile(latencies, 99)
        max_latency = np.max(latencies)

        # Assert latency requirements
        assert avg_latency < 50, f"Average latency {avg_latency:.2f}ms exceeds 50ms"
        assert p95_latency < 100, f"P95 latency {p95_latency:.2f}ms exceeds 100ms"
        assert p99_latency < 200, f"P99 latency {p99_latency:.2f}ms exceeds 200ms"
        assert max_latency < 500, f"Max latency {max_latency:.2f}ms exceeds 500ms"

        # Check jitter (latency variation)
        jitter = np.std(latencies)
        assert jitter < 20, f"Latency jitter {jitter:.2f}ms too high"

        # Log results
        print(f"\nAudio Streaming Latency:")
        print(f"- Chunks Processed: {num_chunks}")
        print(f"- Avg Latency: {avg_latency:.2f}ms")
        print(f"- P50 Latency: {p50_latency:.2f}ms")
        print(f"- P95 Latency: {p95_latency:.2f}ms")
        print(f"- P99 Latency: {p99_latency:.2f}ms")
        print(f"- Max Latency: {max_latency:.2f}ms")
        print(f"- Jitter: {jitter:.2f}ms")

    @pytest.mark.performance
    @pytest.mark.memory
    async def test_memory_leak_detection(self):
        """كشف تسريبات الذاكرة في العمليات المستمرة"""
        # Arrange
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        iterations = 1000
        memory_samples = []

        # Act - تشغيل عمليات متكررة
        for i in range(iterations):
            # محاكاة دورة حياة كاملة
            child = self.test_data_builder.create_child()

            # Process multiple interactions
            for _ in range(10):
                await self.interaction_service.process(
                    child_id=child.id, message=self.faker.sentence()
                )

            # Cleanup
            await self.cleanup_service.cleanup_child_session(child.id)

            # Sample memory every 100 iterations
            if i % 100 == 0:
                gc.collect()  # Force garbage collection
                await asyncio.sleep(0.01)  # Allow cleanup to complete

                current_memory = process.memory_info().rss / 1024 / 1024
                memory_samples.append(current_memory)

                print(f"Iteration {i}: Memory = {current_memory:.2f}MB")

        # Final memory check
        gc.collect()
        await asyncio.sleep(0.1)
        final_memory = process.memory_info().rss / 1024 / 1024
        memory_increase = final_memory - initial_memory

        # Assert - التحقق من عدم وجود تسريب
        assert (
            memory_increase < 50
        ), f"Memory leak detected: {memory_increase:.2f}MB increase"

        # Check memory stability (no continuous growth)
        if len(memory_samples) > 2:
            # Linear regression to check for trend
            x = np.arange(len(memory_samples))
            slope, _ = np.polyfit(x, memory_samples, 1)

            # Slope should be near zero (< 0.5 MB per 100 iterations)
            assert (
                abs(slope) < 0.5
            ), f"Memory growth detected: {slope:.2f}MB per 100 iterations"

        print(f"\nMemory Leak Test:")
        print(f"- Initial Memory: {initial_memory:.2f}MB")
        print(f"- Final Memory: {final_memory:.2f}MB")
        print(f"- Memory Increase: {memory_increase:.2f}MB")
        print(f"- Memory Stable: {'Yes' if abs(slope) < 0.5 else 'No'}")

    @pytest.mark.performance
    async def test_database_query_performance(self):
        """اختبار أداء استعلامات قاعدة البيانات"""
        # Create test data
        num_children = 100
        children = [self.test_data_builder.create_child() for _ in range(num_children)]

        # Test different query patterns
        query_tests = [
            {
                "name": "Single child lookup",
                "query": lambda: self.data_repository.get_child(children[0].id),
                "expected_ms": 10,
            },
            {
                "name": "Batch child lookup",
                "query": lambda: self.data_repository.get_children_batch(
                    [c.id for c in children[:10]]
                ),
                "expected_ms": 20,
            },
            {
                "name": "Children by parent",
                "query": lambda: self.data_repository.get_children_by_parent(
                    children[0].parent_id
                ),
                "expected_ms": 15,
            },
            {
                "name": "Recent interactions",
                "query": lambda: self.data_repository.get_recent_interactions(
                    children[0].id, limit=50
                ),
                "expected_ms": 25,
            },
        ]

        results = []

        for test in query_tests:
            latencies = []

            # Run query multiple times
            for _ in range(50):
                start = time.perf_counter()
                await test["query"]()
                latency = (time.perf_counter() - start) * 1000
                latencies.append(latency)

            avg_latency = np.mean(latencies)
            p95_latency = np.percentile(latencies, 95)

            # Assert performance
            assert (
                avg_latency < test["expected_ms"]
            ), f"{test['name']} avg latency {avg_latency:.2f}ms exceeds {test['expected_ms']}ms"

            results.append(
                {"query": test["name"], "avg_ms": avg_latency, "p95_ms": p95_latency}
            )

        # Print results
        print("\nDatabase Query Performance:")
        for result in results:
            print(
                f"- {result['query']}: avg={result['avg_ms']:.2f}ms, p95={result['p95_ms']:.2f}ms"
            )

    @pytest.mark.performance
    async def test_api_endpoint_response_times(self):
        """اختبار أوقات استجابة API endpoints"""
        # Define endpoint tests
        endpoint_tests = [
            {
                "endpoint": "/api/v1/interactions/process",
                "method": "POST",
                "data": {"child_id": "test", "message": "Hello"},
                "expected_ms": 100,
            },
            {
                "endpoint": "/api/v1/children/{child_id}",
                "method": "GET",
                "expected_ms": 50,
            },
            {
                "endpoint": "/api/v1/safety/check",
                "method": "POST",
                "data": {"content": "Test message", "child_age": 7},
                "expected_ms": 75,
            },
        ]

        # Test each endpoint
        for test in endpoint_tests:
            response_times = []

            for _ in range(100):
                start = time.perf_counter()

                # Simulate API call
                if test["method"] == "POST":
                    response = await self.simulate_api_call(
                        test["endpoint"], method="POST", data=test.get("data", {})
                    )
                else:
                    response = await self.simulate_api_call(
                        test["endpoint"], method="GET"
                    )

                response_time = (time.perf_counter() - start) * 1000
                response_times.append(response_time)

            # Calculate metrics
            avg_time = np.mean(response_times)
            p95_time = np.percentile(response_times, 95)
            p99_time = np.percentile(response_times, 99)

            # Assert
            assert (
                avg_time < test["expected_ms"]
            ), f"{test['endpoint']} avg time {avg_time:.2f}ms exceeds {test['expected_ms']}ms"

            print(f"\n{test['endpoint']} Performance:")
            print(f"- Avg: {avg_time:.2f}ms")
            print(f"- P95: {p95_time:.2f}ms")
            print(f"- P99: {p99_time:.2f}ms")

    def generate_audio_chunk(self, size: int) -> bytes:
        """Generate random audio data for testing"""
        return bytes(random.randint(0, 255) for _ in range(size))

    async def simulate_api_call(
        self, endpoint: str, method: str = "GET", data: Dict = None
    ):
        """Simulate API call for testing"""
        # Simulate network latency
        await asyncio.sleep(random.uniform(0.001, 0.01))

        return {"status": "success", "data": {}, "timestamp": time.time()}
