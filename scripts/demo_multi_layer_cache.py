#!/usr/bin/env python3
"""
Interactive Demo for Multi-Layer Caching System.

This demo showcases the enterprise-grade multi-layer caching capabilities
implemented for the AI Teddy Bear project.

Performance Team Implementation - Task 12
Author: Performance Team Lead
"""

import asyncio
import logging
import time
import json
import random
from datetime import datetime
from typing import Dict, Any, List, Optional

# Demo imports
try:
    from core.infrastructure.caching.multi_layer_cache import (
        MultiLayerCache, CacheConfig, ContentType, CacheLayer
    )
    from core.infrastructure.caching.cache_integration_service import (
        CacheIntegrationService, create_cache_integration_service
    )
    from core.infrastructure.caching.performance_optimizer import (
        PerformanceOptimizer, CacheHealthMonitor,
        create_performance_optimizer, create_health_monitor
    )
    CACHE_SYSTEM_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Cache system not available: {e}")
    CACHE_SYSTEM_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CacheDemoSystem:
    """Comprehensive demo system for multi-layer caching."""
    
    def __init__(self):
        self.cache_system: Optional[MultiLayerCache] = None
        self.integration_service: Optional[CacheIntegrationService] = None
        self.optimizer: Optional[PerformanceOptimizer] = None
        self.health_monitor: Optional[CacheHealthMonitor] = None
        
        # Demo data
        self.demo_data = self._generate_demo_data()
        
    def _generate_demo_data(self) -> Dict[str, Any]:
        """Generate realistic demo data."""
        return {
            "audio_transcriptions": [
                {"audio_hash": f"audio_{i}", "text": f"Hello, this is transcription {i}"}
                for i in range(20)
            ],
            "ai_responses": [
                {
                    "context": {"user_message": f"Question {i}", "emotion": "happy"},
                    "response": f"AI response to question {i}"
                }
                for i in range(15)
            ],
            "emotion_analyses": [
                {
                    "features": {"mfcc": [0.1, 0.2, 0.3], "energy": 0.5},
                    "emotions": {"happy": 0.8, "sad": 0.2}
                }
                for i in range(10)
            ],
            "voice_synthesis": [
                {
                    "text": f"Voice synthesis text {i}",
                    "config": {"voice": "child_friendly", "speed": 1.0},
                    "audio_data": f"audio_bytes_{i}".encode()
                }
                for i in range(8)
            ],
            "configurations": {
                "system_config": {"version": "1.0", "features": ["ai", "voice", "emotion"]},
                "user_preferences": {"voice_speed": 1.0, "emotion_detection": True},
                "model_settings": {"whisper_model": "base", "emotion_model": "v1.0"}
            }
        }
    
    async def initialize(self):
        """Initialize the demo system."""
        if not CACHE_SYSTEM_AVAILABLE:
            print("❌ Cache system not available. Please install required dependencies.")
            return False
        
        try:
            print("🚀 Initializing Multi-Layer Cache Demo System...")
            
            # Create cache configuration
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
                metrics_enabled=True
            )
            
            # Initialize cache system
            self.cache_system = MultiLayerCache(config)
            await self.cache_system.initialize()
            print("✅ Multi-layer cache system initialized")
            
            # Initialize integration service
            self.integration_service = await create_cache_integration_service(config)
            print("✅ Cache integration service initialized")
            
            # Initialize performance optimizer
            self.optimizer = create_performance_optimizer()
            self.health_monitor = create_health_monitor(self.optimizer)
            print("✅ Performance optimizer initialized")
            
            return True
            
        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            return False
    
    async def demo_basic_operations(self):
        """Demonstrate basic cache operations."""
        print("\n" + "="*60)
        print("🔧 DEMO: Basic Cache Operations")
        print("="*60)
        
        # Test different content types
        operations = [
            ("ai_response_001", "Hello, I'm your AI friend!", ContentType.AI_RESPONSE),
            ("transcription_001", "Child said: Hello teddy bear!", ContentType.AUDIO_TRANSCRIPTION),
            ("emotion_001", {"happy": 0.8, "excited": 0.6}, ContentType.EMOTION_ANALYSIS),
            ("config_system", {"version": "2.0", "mode": "production"}, ContentType.CONFIGURATION)
        ]
        
        print("\n📝 Setting cache values...")
        for key, value, content_type in operations:
            start_time = time.time()
            success = await self.cache_system.set_multi_layer(key, value, content_type)
            latency_ms = (time.time() - start_time) * 1000
            
            status = "✅" if success else "❌"
            print(f"{status} Set {key} ({content_type.value}): {latency_ms:.2f}ms")
        
        print("\n📖 Retrieving cache values...")
        for key, expected_value, content_type in operations:
            start_time = time.time()
            value = await self.cache_system.get_with_fallback(key, content_type)
            latency_ms = (time.time() - start_time) * 1000
            
            status = "✅" if value == expected_value else "❌"
            print(f"{status} Get {key}: {latency_ms:.2f}ms (Hit: {value is not None})")
        
        # Test cache miss
        print("\n🔍 Testing cache miss...")
        start_time = time.time()
        value = await self.cache_system.get_with_fallback(
            "nonexistent_key", 
            ContentType.AI_RESPONSE
        )
        latency_ms = (time.time() - start_time) * 1000
        print(f"❌ Cache miss test: {latency_ms:.2f}ms (Value: {value})")
    
    async def demo_cache_integration(self):
        """Demonstrate cache integration with AI services."""
        print("\n" + "="*60)
        print("🤖 DEMO: AI Service Integration")
        print("="*60)
        
        # Simulate AI transcription
        print("\n🎤 Audio Transcription Caching...")
        
        async def mock_transcription_service(audio_data):
            await asyncio.sleep(0.1)  # Simulate processing time
            return f"Transcribed: {audio_data}"
        
        for i in range(3):
            audio_hash = f"demo_audio_{i}"
            start_time = time.time()
            
            result = await self.integration_service.cache_audio_transcription(
                audio_hash,
                mock_transcription_service,
                f"audio_data_{i}"
            )
            
            latency_ms = (time.time() - start_time) * 1000
            print(f"🎯 Transcription {i+1}: {latency_ms:.2f}ms -> {result}")
        
        # Test cache hit on repeated call
        print("\n🔄 Testing cache hit on repeated transcription...")
        start_time = time.time()
        result = await self.integration_service.cache_audio_transcription(
            "demo_audio_0",
            mock_transcription_service,
            "audio_data_0"
        )
        latency_ms = (time.time() - start_time) * 1000
        print(f"⚡ Cached result: {latency_ms:.2f}ms -> {result}")
        
        # Simulate AI response generation
        print("\n🧠 AI Response Caching...")
        
        async def mock_ai_response_service(context):
            await asyncio.sleep(0.15)  # Simulate AI processing
            return f"AI says: {context['user_message']}"
        
        contexts = [
            {"user_message": "Hello!", "emotion": "happy"},
            {"user_message": "How are you?", "emotion": "curious"},
            {"user_message": "Hello!", "emotion": "happy"}  # Duplicate for cache test
        ]
        
        for i, context in enumerate(contexts):
            start_time = time.time()
            
            result = await self.integration_service.cache_ai_response(
                context,
                mock_ai_response_service,
                context
            )
            
            latency_ms = (time.time() - start_time) * 1000
            cache_hit = "HIT" if latency_ms < 50 else "MISS"
            print(f"💬 Response {i+1} ({cache_hit}): {latency_ms:.2f}ms -> {result}")
    
    async def demo_performance_analysis(self):
        """Demonstrate performance analysis and optimization."""
        print("\n" + "="*60)
        print("📊 DEMO: Performance Analysis")
        print("="*60)
        
        # Generate some load to create metrics
        print("\n🏋️ Generating cache load for analysis...")
        await self._generate_cache_load()
        
        # Record metrics
        metrics = self.optimizer.record_metrics(self.cache_system)
        if metrics:
            print(f"📈 Recorded metrics at {metrics.timestamp}")
            print(f"   Hit Rate: {metrics.hit_rate:.2%}")
            print(f"   Avg Latency: {metrics.average_latency_ms:.2f}ms")
            print(f"   Throughput: {metrics.throughput_ops_per_sec:.1f} ops/sec")
            print(f"   Memory Usage: {metrics.memory_usage_mb:.1f}MB")
        
        # Analyze trends (need multiple data points)
        for _ in range(5):
            await self._generate_cache_load()
            self.optimizer.record_metrics(self.cache_system)
            await asyncio.sleep(0.1)
        
        trends = self.optimizer.analyze_performance_trends()
        if trends.get("status") != "insufficient_data":
            print(f"\n📊 Performance Trends:")
            stats = trends.get("statistics", {})
            if "hit_rate" in stats:
                hr_stats = stats["hit_rate"]
                print(f"   Hit Rate - Current: {hr_stats['current']:.2%}, Avg: {hr_stats['average']:.2%}")
            
            if "latency" in stats:
                lat_stats = stats["latency"]
                print(f"   Latency - Current: {lat_stats['current']:.1f}ms, P95: {lat_stats.get('p95', 0):.1f}ms")
        
        # Generate optimization recommendations
        print("\n🎯 Generating optimization recommendations...")
        config = self.cache_system.config
        recommendations = self.optimizer.generate_optimization_recommendations(
            self.cache_system, config
        )
        
        if recommendations:
            print(f"📋 Found {len(recommendations)} recommendations:")
            for i, rec in enumerate(recommendations[:3], 1):  # Show top 3
                print(f"\n   {i}. {rec.title} ({rec.priority})")
                print(f"      {rec.description}")
                print(f"      Expected: {rec.expected_improvement}")
        else:
            print("✅ No optimization recommendations - system performing well!")
    
    async def demo_health_monitoring(self):
        """Demonstrate health monitoring capabilities."""
        print("\n" + "="*60)
        print("🏥 DEMO: Health Monitoring")
        print("="*60)
        
        # Check current health
        health_status = await self.health_monitor.check_health(
            self.cache_system, 
            self.cache_system.config
        )
        
        if health_status.get("status") == "no_data":
            print("⚠️  Insufficient data for health check")
            # Generate some metrics first
            await self._generate_cache_load()
            self.optimizer.record_metrics(self.cache_system)
            
            health_status = await self.health_monitor.check_health(
                self.cache_system, 
                self.cache_system.config
            )
        
        print(f"🏥 Health Status: {health_status.get('overall_status', 'UNKNOWN')}")
        
        alerts = health_status.get("alerts", [])
        if alerts:
            print(f"⚠️  {len(alerts)} alert(s) found:")
            for alert in alerts:
                level_emoji = "🔴" if alert["level"] == "CRITICAL" else "🟡"
                print(f"   {level_emoji} {alert['metric']}: {alert['message']}")
        else:
            print("✅ No alerts - system healthy!")
        
        # Show metrics summary
        metrics_summary = health_status.get("metrics_summary", {})
        if metrics_summary:
            print(f"\n📊 Current Metrics:")
            print(f"   Hit Rate: {metrics_summary.get('hit_rate', 0):.2%}")
            print(f"   Latency: {metrics_summary.get('latency_ms', 0):.1f}ms")
            print(f"   Error Rate: {metrics_summary.get('error_rate', 0):.2%}")
            print(f"   Memory Usage: {metrics_summary.get('memory_usage_mb', 0):.1f}MB")
    
    async def demo_cache_warming(self):
        """Demonstrate cache warming capabilities."""
        print("\n" + "="*60)
        print("🔥 DEMO: Cache Warming")
        print("="*60)
        
        # Prepare warming data
        warm_data = [
            ("config:system", self.demo_data["configurations"]["system_config"], ContentType.CONFIGURATION),
            ("config:user_prefs", self.demo_data["configurations"]["user_preferences"], ContentType.CONFIGURATION),
            ("ai:greeting", "Hello! I'm your friendly AI teddy bear!", ContentType.AI_RESPONSE),
            ("ai:goodbye", "Goodbye! Have a wonderful day!", ContentType.AI_RESPONSE),
        ]
        
        print(f"🔥 Warming cache with {len(warm_data)} entries...")
        start_time = time.time()
        
        success_count = await self.cache_system.warm_cache(warm_data)
        warming_time = (time.time() - start_time) * 1000
        
        print(f"✅ Cache warming completed: {success_count}/{len(warm_data)} successful")
        print(f"⏱️  Warming time: {warming_time:.2f}ms")
        
        # Test warmed cache performance
        print("\n⚡ Testing warmed cache performance...")
        test_keys = ["config:system", "ai:greeting", "config:user_prefs"]
        
        for key in test_keys:
            start_time = time.time()
            value = await self.cache_system.get_with_fallback(
                key, 
                ContentType.CONFIGURATION if key.startswith("config:") else ContentType.AI_RESPONSE
            )
            latency_ms = (time.time() - start_time) * 1000
            
            status = "✅" if value is not None else "❌"
            print(f"{status} {key}: {latency_ms:.2f}ms")
    
    async def demo_comprehensive_performance_report(self):
        """Generate and display comprehensive performance report."""
        print("\n" + "="*60)
        print("📋 DEMO: Comprehensive Performance Report")
        print("="*60)
        
        # Generate substantial load for meaningful metrics
        print("🏋️ Generating comprehensive load...")
        for _ in range(10):
            await self._generate_cache_load()
            self.optimizer.record_metrics(self.cache_system)
        
        # Generate performance report
        config = self.cache_system.config
        report = self.optimizer.generate_performance_report(
            self.cache_system, config
        )
        
        # Display report summary
        summary = report.get("summary", {})
        print(f"\n📊 Performance Summary:")
        print(f"   Overall Health: {summary.get('overall_health', 'UNKNOWN')}")
        print(f"   Performance Score: {summary.get('performance_score', 0):.1f}/100")
        print(f"   Critical Issues: {summary.get('critical_issues', 0)}")
        print(f"   Optimization Opportunities: {summary.get('optimization_opportunities', 0)}")
        
        # Display current metrics
        current_metrics = report.get("current_metrics")
        if current_metrics:
            print(f"\n📈 Current Metrics:")
            print(f"   Hit Rate: {current_metrics.get('hit_rate', 0):.2%}")
            print(f"   Average Latency: {current_metrics.get('average_latency_ms', 0):.2f}ms")
            print(f"   Throughput: {current_metrics.get('throughput_ops_per_sec', 0):.1f} ops/sec")
            print(f"   Memory Usage: {current_metrics.get('memory_usage_mb', 0):.1f}MB")
        
        # Display top recommendations
        recommendations = report.get("recommendations", [])
        if recommendations:
            print(f"\n🎯 Top Optimization Recommendations:")
            for i, rec in enumerate(recommendations[:3], 1):
                print(f"\n   {i}. {rec['title']} ({rec['priority']} Priority)")
                print(f"      {rec['description']}")
                print(f"      Expected: {rec['expected_improvement']}")
                print(f"      Effort: {rec['implementation_effort']}")
        
        # Show cache layer performance
        trends = report.get("trends_analysis", {})
        hit_rates = trends.get("cache_system_metrics", {}).get("hit_rate_by_layer", {})
        if hit_rates:
            print(f"\n🏗️  Cache Layer Performance:")
            print(f"   L1 (Memory): {hit_rates.get('l1', 0):.2%} hit rate")
            print(f"   L2 (Redis): {hit_rates.get('l2', 0):.2%} hit rate")
            print(f"   L3 (CDN): {hit_rates.get('l3', 0):.2%} hit rate")
    
    async def _generate_cache_load(self, operations: int = 50):
        """Generate cache load for testing."""
        tasks = []
        
        for i in range(operations):
            operation_type = random.choice(['set', 'get', 'get_miss'])
            
            if operation_type == 'set':
                key = f"load_key_{random.randint(1, 20)}"
                value = f"load_value_{i}"
                content_type = random.choice(list(ContentType))
                
                task = self.cache_system.set_multi_layer(key, value, content_type)
                
            elif operation_type == 'get':
                key = f"load_key_{random.randint(1, 20)}"
                content_type = random.choice(list(ContentType))
                
                task = self.cache_system.get_with_fallback(key, content_type)
                
            else:  # get_miss
                key = f"miss_key_{random.randint(100, 200)}"
                content_type = random.choice(list(ContentType))
                
                task = self.cache_system.get_with_fallback(key, content_type)
            
            tasks.append(task)
        
        # Execute operations concurrently
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def cleanup(self):
        """Cleanup demo resources."""
        if self.cache_system:
            await self.cache_system.cleanup()
        
        if self.integration_service:
            await self.integration_service.cleanup()


async def run_interactive_demo():
    """Run interactive demo with user choices."""
    print("🎯 AI Teddy Bear - Multi-Layer Caching System Demo")
    print("=" * 60)
    print("Performance Team Implementation - Task 12")
    print("=" * 60)
    
    demo = CacheDemoSystem()
    
    if not await demo.initialize():
        return
    
    try:
        while True:
            print("\n🎮 Demo Options:")
            print("1. Basic Cache Operations")
            print("2. AI Service Integration") 
            print("3. Performance Analysis")
            print("4. Health Monitoring")
            print("5. Cache Warming")
            print("6. Comprehensive Performance Report")
            print("7. Run All Demos")
            print("0. Exit")
            
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
                print("\n🚀 Running all demos...")
                await demo.demo_basic_operations()
                await demo.demo_cache_integration()
                await demo.demo_performance_analysis()
                await demo.demo_health_monitoring()
                await demo.demo_cache_warming()
                await demo.demo_comprehensive_performance_report()
                print("\n✅ All demos completed!")
            else:
                print("❌ Invalid choice. Please select 0-7.")
            
            if choice != "0":
                input("\nPress Enter to continue...")
    
    finally:
        await demo.cleanup()
        print("\n👋 Demo completed. Thank you!")


async def run_automated_demo():
    """Run automated demo without user interaction."""
    print("🤖 Running Automated Multi-Layer Cache Demo...")
    
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
        
        print("\n✅ Automated demo completed successfully!")
        
    finally:
        await demo.cleanup()


if __name__ == "__main__":
    import sys
    
    if "--automated" in sys.argv:
        asyncio.run(run_automated_demo())
    else:
        asyncio.run(run_interactive_demo()) 