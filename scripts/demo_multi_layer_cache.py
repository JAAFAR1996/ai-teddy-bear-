"""
Interactive Demo for Multi-Layer Caching System.

This demo showcases the enterprise-grade multi-layer caching capabilities
implemented for the AI Teddy Bear project.

Performance Team Implementation - Task 12
Author: Performance Team Lead
"""

import asyncio
import logging
import random
import time
from typing import Any, Dict, Optional

try:
    from src.infrastructure.caching_advanced.cache_integration_service import (
        CacheIntegrationService, create_cache_integration_service)
    from src.infrastructure.caching_advanced.multi_layer_cache import (
        CacheConfig, CacheLayer, ContentType, MultiLayerCache)
    from src.infrastructure.caching_advanced.performance_optimizer import (
        CacheHealthMonitor, PerformanceOptimizer, create_health_monitor,
        create_performance_optimizer)

    CACHE_SYSTEM_AVAILABLE = True
except ImportError as e:
    logger.info(f"⚠️  Cache system not available: {e}")
    CACHE_SYSTEM_AVAILABLE = False
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CacheDemoSystem:
    """Comprehensive demo system for multi-layer caching."""

    def __init__(self):
        self.cache_system: Optional[MultiLayerCache] = None
        self.integration_service: Optional[CacheIntegrationService] = None
        self.optimizer: Optional[PerformanceOptimizer] = None
        self.health_monitor: Optional[CacheHealthMonitor] = None
        self.demo_data = self._generate_demo_data()

    def _generate_demo_data(self) -> Dict[str, Any]:
        """Generate realistic demo data."""
        return {
            "audio_transcriptions": [
                {
                    "audio_hash": f"audio_{i}",
                    "text": f"Hello, this is transcription {i}",
                }
                for i in range(20)
            ],
            "ai_responses": [
                {
                    "context": {"user_message": f"Question {i}", "emotion": "happy"},
                    "response": f"AI response to question {i}",
                }
                for i in range(15)
            ],
            "emotion_analyses": [
                {
                    "features": {"mfcc": [0.1, 0.2, 0.3], "energy": 0.5},
                    "emotions": {"happy": 0.8, "sad": 0.2},
                }
                for i in range(10)
            ],
            "voice_synthesis": [
                {
                    "text": f"Voice synthesis text {i}",
                    "config": {"voice": "child_friendly", "speed": 1.0},
                    "audio_data": f"audio_bytes_{i}".encode(),
                }
                for i in range(8)
            ],
            "configurations": {
                "system_config": {
                    "version": "1.0",
                    "features": ["ai", "voice", "emotion"],
                },
                "user_preferences": {"voice_speed": 1.0, "emotion_detection": True},
                "model_settings": {"whisper_model": "base", "emotion_model": "v1.0"},
            },
        }

    async def initialize(self):
        """Initialize the demo system."""
        if not CACHE_SYSTEM_AVAILABLE:
            logger.info(
                "❌ Cache system not available. Please install required dependencies."
            )
            return False
        try:
            logger.info("🚀 Initializing Multi-Layer Cache Demo System...")
            config = CacheConfig(
                l1_enabled=True,
                l1_max_size_mb=128,
                l1_ttl_seconds=300,
                l2_enabled=True,
                l2_redis_url="redis://localhost:6379",
                l3_enabled=True,
                compression_enabled=True,
                async_write_enabled=True,
                cache_warming_enabled=True,
                metrics_enabled=True,
            )
            self.cache_system = MultiLayerCache(config)
            await self.cache_system.initialize()
            logger.info("✅ Multi-layer cache system initialized")
            self.integration_service = await create_cache_integration_service(config)
            logger.info("✅ Cache integration service initialized")
            self.optimizer = create_performance_optimizer()
            self.health_monitor = create_health_monitor(self.optimizer)
            logger.info("✅ Performance optimizer initialized")
            return True
        except Exception as e:
            logger.info(f"❌ Initialization failed: {e}")
            return False

    async def demo_basic_operations(self):
        """Demonstrate basic cache operations."""
        logger.info("\n" + "=" * 60)
        logger.info("🔧 DEMO: Basic Cache Operations")
        logger.info("=" * 60)
        operations = [
            ("ai_response_001", "Hello, I'm your AI friend!", ContentType.AI_RESPONSE),
            (
                "transcription_001",
                "Child said: Hello teddy bear!",
                ContentType.AUDIO_TRANSCRIPTION,
            ),
            (
                "emotion_001",
                {"happy": 0.8, "excited": 0.6},
                ContentType.EMOTION_ANALYSIS,
            ),
            (
                "config_system",
                {"version": "2.0", "mode": "production"},
                ContentType.CONFIGURATION,
            ),
        ]
        logger.info("\n📝 Setting cache values...")
        for key, value, content_type in operations:
            start_time = time.time()
            success = await self.cache_system.set_multi_layer(key, value, content_type)
            latency_ms = (time.time() - start_time) * 1000
            status = "✅" if success else "❌"
            logger.info(
                f"{status} Set {key} ({content_type.value}): {latency_ms:.2f}ms"
            )
        logger.info("\n📖 Retrieving cache values...")
        for key, expected_value, content_type in operations:
            start_time = time.time()
            value = await self.cache_system.get_with_fallback(key, content_type)
            latency_ms = (time.time() - start_time) * 1000
            status = "✅" if value == expected_value else "❌"
            logger.info(
                f"{status} Get {key}: {latency_ms:.2f}ms (Hit: {value is not None})"
            )
        logger.info("\n🔍 Testing cache miss...")
        start_time = time.time()
        value = await self.cache_system.get_with_fallback(
            "nonexistent_key", ContentType.AI_RESPONSE
        )
        latency_ms = (time.time() - start_time) * 1000
        logger.info(f"❌ Cache miss test: {latency_ms:.2f}ms (Value: {value})")

    async def demo_cache_integration(self):
        """Demonstrate cache integration with AI services."""
        logger.info("\n" + "=" * 60)
        logger.info("🤖 DEMO: AI Service Integration")
        logger.info("=" * 60)
        logger.info("\n🎤 Audio Transcription Caching...")

        async def mock_transcription_service(audio_data):
            await asyncio.sleep(0.1)
            return f"Transcribed: {audio_data}"

        for i in range(3):
            audio_hash = f"demo_audio_{i}"
            start_time = time.time()
            result = await self.integration_service.cache_audio_transcription(
                audio_hash, mock_transcription_service, f"audio_data_{i}"
            )
            latency_ms = (time.time() - start_time) * 1000
            logger.info(f"🎯 Transcription {i + 1}: {latency_ms:.2f}ms -> {result}")
        logger.info("\n🔄 Testing cache hit on repeated transcription...")
        start_time = time.time()
        result = await self.integration_service.cache_audio_transcription(
            "demo_audio_0", mock_transcription_service, "audio_data_0"
        )
        latency_ms = (time.time() - start_time) * 1000
        logger.info(f"⚡ Cached result: {latency_ms:.2f}ms -> {result}")
        logger.info("\n🧠 AI Response Caching...")

        async def mock_ai_response_service(context):
            await asyncio.sleep(0.15)
            return f"AI says: {context['user_message']}"

        contexts = [
            {"user_message": "Hello!", "emotion": "happy"},
            {"user_message": "How are you?", "emotion": "curious"},
            {"user_message": "Hello!", "emotion": "happy"},
        ]
        for i, context in enumerate(contexts):
            start_time = time.time()
            result = await self.integration_service.cache_ai_response(
                context, mock_ai_response_service, context
            )
            latency_ms = (time.time() - start_time) * 1000
            cache_hit = "HIT" if latency_ms < 50 else "MISS"
            logger.info(
                f"💬 Response {i + 1} ({cache_hit}): {latency_ms:.2f}ms -> {result}"
            )

    async def demo_performance_analysis(self):
        """Demonstrate performance analysis and optimization."""
        logger.info("\n" + "=" * 60)
        logger.info("📊 DEMO: Performance Analysis")
        logger.info("=" * 60)
        logger.info("\n🏋️ Generating cache load for analysis...")
        await self._generate_cache_load()
        metrics = self.optimizer.record_metrics(self.cache_system)
        if metrics:
            logger.info(f"📈 Recorded metrics at {metrics.timestamp}")
            logger.info(f"   Hit Rate: {metrics.hit_rate:.2%}")
            logger.info(f"   Avg Latency: {metrics.average_latency_ms:.2f}ms")
            logger.info(f"   Throughput: {metrics.throughput_ops_per_sec:.1f} ops/sec")
            logger.info(f"   Memory Usage: {metrics.memory_usage_mb:.1f}MB")
        for _ in range(5):
            await self._generate_cache_load()
            self.optimizer.record_metrics(self.cache_system)
            await asyncio.sleep(0.1)
        trends = self.optimizer.analyze_performance_trends()
        if trends.get("status") != "insufficient_data":
            logger.info("\n📊 Performance Trends:")
            stats = trends.get("statistics", {})
            if "hit_rate" in stats:
                hr_stats = stats["hit_rate"]
                logger.info(
                    f"   Hit Rate - Current: {hr_stats['current']:.2%}, Avg: {hr_stats['average']:.2%}"
                )
            if "latency" in stats:
                lat_stats = stats["latency"]
                logger.info(
                    f"   Latency - Current: {lat_stats['current']:.1f}ms, P95: {lat_stats.get('p95', 0):.1f}ms"
                )
        logger.info("\n🎯 Generating optimization recommendations...")
        config = self.cache_system.config
        recommendations = self.optimizer.generate_optimization_recommendations(
            self.cache_system, config
        )
        if recommendations:
            logger.info(f"📋 Found {len(recommendations)} recommendations:")
            for i, rec in enumerate(recommendations[:3], 1):
                logger.info(f"\n   {i}. {rec.title} ({rec.priority})")
                logger.info(f"      {rec.description}")
                logger.info(f"      Expected: {rec.expected_improvement}")
        else:
            logger.info("✅ No optimization recommendations - system performing well!")

    async def demo_health_monitoring(self):
        """Demonstrate health monitoring capabilities."""
        logger.info("\n" + "=" * 60)
        logger.info("🏥 DEMO: Health Monitoring")
        logger.info("=" * 60)
        health_status = await self.health_monitor.check_health(
            self.cache_system, self.cache_system.config
        )
        if health_status.get("status") == "no_data":
            logger.info("⚠️  Insufficient data for health check")
            await self._generate_cache_load()
            self.optimizer.record_metrics(self.cache_system)
            health_status = await self.health_monitor.check_health(
                self.cache_system, self.cache_system.config
            )
        logger.info(
            f"🏥 Health Status: {health_status.get('overall_status', 'UNKNOWN')}"
        )
        alerts = health_status.get("alerts", [])
        if alerts:
            logger.info(f"⚠️  {len(alerts)} alert(s) found:")
            for alert in alerts:
                level_emoji = "🔴" if alert["level"] == "CRITICAL" else "🟡"
                logger.info(f"   {level_emoji} {alert['metric']}: {alert['message']}")
        else:
            logger.info("✅ No alerts - system healthy!")
        metrics_summary = health_status.get("metrics_summary", {})
        if metrics_summary:
            logger.info("\n📊 Current Metrics:")
            logger.info(f"   Hit Rate: {metrics_summary.get('hit_rate', 0):.2%}")
            logger.info(f"   Latency: {metrics_summary.get('latency_ms', 0):.1f}ms")
            logger.info(f"   Error Rate: {metrics_summary.get('error_rate', 0):.2%}")
            logger.info(
                f"   Memory Usage: {metrics_summary.get('memory_usage_mb', 0):.1f}MB"
            )

    async def demo_cache_warming(self):
        """Demonstrate cache warming capabilities."""
        logger.info("\n" + "=" * 60)
        logger.info("🔥 DEMO: Cache Warming")
        logger.info("=" * 60)
        warm_data = [
            (
                "config:system",
                self.demo_data["configurations"]["system_config"],
                ContentType.CONFIGURATION,
            ),
            (
                "config:user_prefs",
                self.demo_data["configurations"]["user_preferences"],
                ContentType.CONFIGURATION,
            ),
            (
                "ai:greeting",
                "Hello! I'm your friendly AI teddy bear!",
                ContentType.AI_RESPONSE,
            ),
            ("ai:goodbye", "Goodbye! Have a wonderful day!", ContentType.AI_RESPONSE),
        ]
        logger.info(f"🔥 Warming cache with {len(warm_data)} entries...")
        start_time = time.time()
        success_count = await self.cache_system.warm_cache(warm_data)
        warming_time = (time.time() - start_time) * 1000
        logger.info(
            f"✅ Cache warming completed: {success_count}/{len(warm_data)} successful"
        )
        logger.info(f"⏱️  Warming time: {warming_time:.2f}ms")
        logger.info("\n⚡ Testing warmed cache performance...")
        test_keys = ["config:system", "ai:greeting", "config:user_prefs"]
        for key in test_keys:
            start_time = time.time()
            value = await self.cache_system.get_with_fallback(
                key,
                (
                    ContentType.CONFIGURATION
                    if key.startswith("config:")
                    else ContentType.AI_RESPONSE
                ),
            )
            latency_ms = (time.time() - start_time) * 1000
            status = "✅" if value is not None else "❌"
            logger.info(f"{status} {key}: {latency_ms:.2f}ms")

    async def demo_comprehensive_performance_report(self):
        """Generate and display comprehensive performance report."""
        logger.info("\n" + "=" * 60)
        logger.info("📋 DEMO: Comprehensive Performance Report")
        logger.info("=" * 60)
        logger.info("🏋️ Generating comprehensive load...")
        for _ in range(10):
            await self._generate_cache_load()
            self.optimizer.record_metrics(self.cache_system)
        config = self.cache_system.config
        report = self.optimizer.generate_performance_report(self.cache_system, config)
        summary = report.get("summary", {})
        logger.info("\n📊 Performance Summary:")
        logger.info(f"   Overall Health: {summary.get('overall_health', 'UNKNOWN')}")
        logger.info(
            f"   Performance Score: {summary.get('performance_score', 0):.1f}/100"
        )
        logger.info(f"   Critical Issues: {summary.get('critical_issues', 0)}")
        logger.info(
            f"   Optimization Opportunities: {summary.get('optimization_opportunities', 0)}"
        )
        current_metrics = report.get("current_metrics")
        if current_metrics:
            logger.info("\n📈 Current Metrics:")
            logger.info(f"   Hit Rate: {current_metrics.get('hit_rate', 0):.2%}")
            logger.info(
                f"   Average Latency: {current_metrics.get('average_latency_ms', 0):.2f}ms"
            )
            logger.info(
                f"   Throughput: {current_metrics.get('throughput_ops_per_sec', 0):.1f} ops/sec"
            )
            logger.info(
                f"   Memory Usage: {current_metrics.get('memory_usage_mb', 0):.1f}MB"
            )
        recommendations = report.get("recommendations", [])
        if recommendations:
            logger.info("\n🎯 Top Optimization Recommendations:")
            for i, rec in enumerate(recommendations[:3], 1):
                logger.info(f"\n   {i}. {rec['title']} ({rec['priority']} Priority)")
                logger.info(f"      {rec['description']}")
                logger.info(f"      Expected: {rec['expected_improvement']}")
                logger.info(f"      Effort: {rec['implementation_effort']}")
        trends = report.get("trends_analysis", {})
        hit_rates = trends.get("cache_system_metrics", {}).get("hit_rate_by_layer", {})
        if hit_rates:
            logger.info("\n🏗️  Cache Layer Performance:")
            logger.info(f"   L1 (Memory): {hit_rates.get('l1', 0):.2%} hit rate")
            logger.info(f"   L2 (Redis): {hit_rates.get('l2', 0):.2%} hit rate")
            logger.info(f"   L3 (CDN): {hit_rates.get('l3', 0):.2%} hit rate")

    async def _generate_cache_load(self, operations: int = 50):
        """Generate cache load for testing."""
        tasks = []
        for i in range(operations):
            operation_type = random.choice(["set", "get", "get_miss"])
            if operation_type == "set":
                key = f"load_key_{random.randint(1, 20)}"
                value = f"load_value_{i}"
                content_type = random.choice(list(ContentType))
                task = self.cache_system.set_multi_layer(key, value, content_type)
            elif operation_type == "get":
                key = f"load_key_{random.randint(1, 20)}"
                content_type = random.choice(list(ContentType))
                task = self.cache_system.get_with_fallback(key, content_type)
            else:
                key = f"miss_key_{random.randint(100, 200)}"
                content_type = random.choice(list(ContentType))
                task = self.cache_system.get_with_fallback(key, content_type)
            tasks.append(task)
        await asyncio.gather(*tasks, return_exceptions=True)

    async def cleanup(self):
        """Cleanup demo resources."""
        if self.cache_system:
            await self.cache_system.cleanup()
        if self.integration_service:
            await self.integration_service.cleanup()


async def run_interactive_demo():
    """Run interactive demo with user choices."""
    logger.info("🎯 AI Teddy Bear - Multi-Layer Caching System Demo")
    logger.info("=" * 60)
    logger.info("Performance Team Implementation - Task 12")
    logger.info("=" * 60)
    demo = CacheDemoSystem()
    if not await demo.initialize():
        return
    try:
        while True:
            logger.info("\n🎮 Demo Options:")
            logger.info("1. Basic Cache Operations")
            logger.info("2. AI Service Integration")
            logger.info("3. Performance Analysis")
            logger.info("4. Health Monitoring")
            logger.info("5. Cache Warming")
            logger.info("6. Comprehensive Performance Report")
            logger.info("7. Run All Demos")
            logger.info("0. Exit")
            choice = input("\nSelect demo (0-7): ").strip()
            if choice == "0":
                break
            elif choice == "1":
                await demo.demo_basic_operations()
            elif choice == "2":
                await demo.demo_cache_integration()
            elif choice == "3":
                await demo.demo_performance_analysis()
            elif choice == "4":
                await demo.demo_health_monitoring()
            elif choice == "5":
                await demo.demo_cache_warming()
            elif choice == "6":
                await demo.demo_comprehensive_performance_report()
            elif choice == "7":
                logger.info("\n🚀 Running all demos...")
                await demo.demo_basic_operations()
                await demo.demo_cache_integration()
                await demo.demo_performance_analysis()
                await demo.demo_health_monitoring()
                await demo.demo_cache_warming()
                await demo.demo_comprehensive_performance_report()
                logger.info("\n✅ All demos completed!")
            else:
                logger.info("❌ Invalid choice. Please select 0-7.")
            if choice != "0":
                input("\nPress Enter to continue...")
    finally:
        await demo.cleanup()
        logger.info("\n👋 Demo completed. Thank you!")


async def run_automated_demo():
    """Run automated demo without user interaction."""
    logger.info("🤖 Running Automated Multi-Layer Cache Demo...")
    demo = CacheDemoSystem()
    if not await demo.initialize():
        return
    try:
        await demo.demo_basic_operations()
        await demo.demo_cache_integration()
        await demo.demo_performance_analysis()
        await demo.demo_health_monitoring()
        await demo.demo_cache_warming()
        await demo.demo_comprehensive_performance_report()
        logger.info("\n✅ Automated demo completed successfully!")
    finally:
        await demo.cleanup()


if __name__ == "__main__":
    import sys

    if "--automated" in sys.argv:
        asyncio.run(run_automated_demo())
    else:
        asyncio.run(run_interactive_demo())
