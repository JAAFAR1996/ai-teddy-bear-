"""
Base Test Classes - كلاسات الأساس لجميع الاختبارات
"""

import asyncio
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Awaitable, Callable, Dict, Generic, TypeVar

import pytest
import structlog
from faker import Faker

from .bdd import ActionExecutor, TestContextBuilder
from .builders import MockFactory, TestDataBuilder
from .validators import (
    AgeAppropriateContentGenerator,
    ContentSafetyValidator,
    COPPAComplianceChecker,
)

T = TypeVar("T")

logger = structlog.get_logger(__name__)


class BaseTestCase(ABC, Generic[T]):
    """Base class لجميع test cases مع utilities مشتركة"""

    @pytest.fixture(autouse=True)
    async def setup_base(self):
        """Setup أساسي لكل الاختبارات"""
        self.faker = Faker()
        self.test_data_builder = TestDataBuilder()
        self.mock_factory = MockFactory()
        self.test_start_time = datetime.utcnow()

        # Setup test context
        self.test_context = {
            "test_id": self.faker.uuid4(),
            "test_name": (
                self._testMethodName if hasattr(
                    self,
                    "_testMethodName") else "unknown"),
            "start_time": self.test_start_time,
        }

        logger.info("Starting test", **self.test_context)

        yield

        # Cleanup
        await self.cleanup()

        test_duration = (
            datetime.utcnow() -
            self.test_start_time).total_seconds()
        logger.info(
            "Test completed",
            duration=test_duration,
            **self.test_context)

    @abstractmethod
    async def cleanup(self):
        """تنظيف بعد كل اختبار"""
        pass

    def given(self, description: str) -> TestContextBuilder:
        """BDD-style test setup"""
        logger.debug(f"Given: {description}")
        return TestContextBuilder(description)

    def when(self, action: Callable) -> ActionExecutor:
        """BDD-style action execution"""
        logger.debug(f"When: executing {action.__name__}")
        return ActionExecutor(action)

    def then(self, assertion: Callable) -> None:
        """BDD-style assertion"""
        logger.debug("Then: asserting")
        assertion()

    def assert_eventually(
        self,
        condition: Callable[[], bool],
        timeout: float = 5.0,
        interval: float = 0.1,
        message: str = "Condition not met within timeout",
    ):
        """Assert that a condition becomes true eventually"""
        import time

        end_time = time.time() + timeout

        while time.time() < end_time:
            if condition():
                return
            time.sleep(interval)

        raise AssertionError(message)

    async def assert_async_eventually(
        self,
        condition: Callable[[], Awaitable[bool]],
        timeout: float = 5.0,
        interval: float = 0.1,
        message: str = "Async condition not met within timeout",
    ):
        """Assert that an async condition becomes true eventually"""
        end_time = asyncio.get_event_loop().time() + timeout

        while asyncio.get_event_loop().time() < end_time:
            if await condition():
                return
            await asyncio.sleep(interval)

        raise AssertionError(message)


class ChildSafetyTestCase(BaseTestCase):
    """Base class خاص باختبارات أمان الأطفال"""

    @pytest.fixture(autouse=True)
    async def setup_child_safety(self):
        """Setup خاص بأمان الأطفال"""
        self.content_validator = ContentSafetyValidator()
        self.age_appropriate_generator = AgeAppropriateContentGenerator()
        self.coppa_compliance_checker = COPPAComplianceChecker()

        # Safety test patterns
        self.unsafe_patterns = {
            "violence": ["fight", "hurt", "kill", "weapon", "blood"],
            "inappropriate_language": ["damn", "hell", "stupid", "hate"],
            "adult_content": ["dating", "romance", "kiss", "adult"],
            "personal_info": [
                "my address is",
                "my phone number",
                "my email",
                "my school",
                "my parent's name",
            ],
            "dangerous_behavior": [
                "don't tell your parents",
                "keep this secret",
                "meet me at",
                "send me a photo",
            ],
        }

        self.safe_topics = {
            "educational": [
                "learn", "count", "alphabet", "colors", "shapes"], "stories": [
                "once upon a time", "adventure", "friendship", "animals"], "games": [
                "let's play", "imagine", "pretend", "fun"], "positive": [
                    "happy", "kind", "help", "share", "please"], }

        yield

    def generate_safe_content(
            self,
            age_group: int,
            topic: str = "general") -> str:
        """توليد محتوى آمن للاختبار"""
        return self.age_appropriate_generator.generate(age_group, topic)

    def generate_unsafe_content(self, violation_type: str) -> str:
        """توليد محتوى غير آمن للاختبار negative cases"""
        base_sentence = self.faker.sentence()
        unsafe_word = self.faker.random_choice(
            self.unsafe_patterns.get(violation_type, ["unsafe"])
        )
        return f"{base_sentence} {unsafe_word}"

    def assert_content_safe(self, content: str, age: int):
        """التحقق من أمان المحتوى"""
        result = self.content_validator.validate(content, age)
        assert result.is_safe, f"Content deemed unsafe: {result.reason}"

    def assert_content_unsafe(
            self,
            content: str,
            age: int,
            expected_violation: str):
        """التحقق من اكتشاف المحتوى غير الآمن"""
        result = self.content_validator.validate(content, age)
        assert not result.is_safe, "Content should be detected as unsafe"
        assert (
            expected_violation in result.violation_type
        ), f"Expected violation type {expected_violation}, got {result.violation_type}"


class PerformanceTestCase(BaseTestCase):
    """Base class لاختبارات الأداء"""

    @pytest.fixture(autouse=True)
    async def setup_performance(self):
        """Setup خاص باختبارات الأداء"""
        self.performance_metrics = {
            "start_time": None,
            "end_time": None,
            "operations": [],
            "memory_samples": [],
        }

        # Performance thresholds
        self.thresholds = {
            "response_time_ms": 100,
            "p95_latency_ms": 200,
            "p99_latency_ms": 500,
            "memory_increase_mb": 50,
            "cpu_usage_percent": 80,
            "error_rate_percent": 1,
        }

        yield

    def start_performance_tracking(self):
        """بدء تتبع الأداء"""
        import time

        import psutil

        self.performance_metrics["start_time"] = time.perf_counter()
        self.performance_metrics["start_memory"] = (
            psutil.Process().memory_info().rss / 1024 / 1024
        )
        self.performance_metrics["start_cpu"] = psutil.cpu_percent(
            interval=0.1)

    def stop_performance_tracking(self) -> Dict[str, Any]:
        """إيقاف تتبع الأداء وإرجاع النتائج"""
        import time

        import numpy as np
        import psutil

        self.performance_metrics["end_time"] = time.perf_counter()

        duration = (
            self.performance_metrics["end_time"]
            - self.performance_metrics["start_time"]
        )
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_increase = end_memory - self.performance_metrics["start_memory"]

        operations = self.performance_metrics["operations"]
        if operations:
            latencies = [op["duration_ms"] for op in operations]
            p95_latency = np.percentile(latencies, 95)
            p99_latency = np.percentile(latencies, 99)
            avg_latency = np.mean(latencies)
        else:
            p95_latency = p99_latency = avg_latency = 0

        return {
            "total_duration_seconds": duration,
            "memory_increase_mb": memory_increase,
            "avg_latency_ms": avg_latency,
            "p95_latency_ms": p95_latency,
            "p99_latency_ms": p99_latency,
            "total_operations": len(operations),
        }

    def record_operation(self, operation_name: str, duration_ms: float):
        """تسجيل عملية للتحليل"""
        self.performance_metrics["operations"].append(
            {
                "name": operation_name,
                "duration_ms": duration_ms,
                "timestamp": datetime.utcnow(),
            }
        )

    def assert_performance_within_limits(self, metrics: Dict[str, Any]):
        """التحقق من أن الأداء ضمن الحدود المقبولة"""
        if "avg_latency_ms" in metrics:
            assert (
                metrics["avg_latency_ms"] < self.thresholds["response_time_ms"]
            ), f"Average latency {metrics['avg_latency_ms']}ms exceeds threshold"

        if "p95_latency_ms" in metrics:
            assert (
                metrics["p95_latency_ms"] < self.thresholds["p95_latency_ms"]
            ), f"P95 latency {metrics['p95_latency_ms']}ms exceeds threshold"

        if "memory_increase_mb" in metrics:
            assert (
                metrics["memory_increase_mb"] < self.thresholds["memory_increase_mb"]
            ), f"Memory increase {metrics['memory_increase_mb']}MB exceeds threshold"
