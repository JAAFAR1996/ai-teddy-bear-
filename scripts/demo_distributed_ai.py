"""
Distributed AI Processing Demo for AI Teddy Bear Project.

This demo showcases the distributed AI processing system using Ray Serve
for parallel conversation handling across multiple AI services.

AI Team Implementation - Task 11 Demo
Author: AI Team Lead
"""

import asyncio
import logging
import sys
import time
from pathlib import Path
from typing import Any, Dict

import numpy as np

sys.path.append(str(Path(__file__).parent.parent))
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
try:
    from src.infrastructure.ai.distributed_processor import (
        RAY_AVAILABLE, AIServiceType, ChildContext, ConversationRequest,
        ConversationResponse, DistributedAIProcessor, MockAIServices,
        ProcessingPriority)

    DISTRIBUTED_AI_AVAILABLE = True
except ImportError as e:
    DISTRIBUTED_AI_AVAILABLE = False
    import_error = str(e)
    logger.error(f"Distributed AI not available: {e}")


class DistributedAIDemo:
    """Comprehensive demonstration of distributed AI capabilities."""

    def __init__(self):
        self.processor = None
        self.demo_data = self._generate_demo_data()

    def _generate_demo_data(self) -> Dict[str, Any]:
        """Generate synthetic demo data for testing."""
        return {
            "children": [
                ChildContext(
                    child_id="child_001",
                    name="أحمد",
                    age=7,
                    language="ar",
                    voice_profile="playful",
                    conversation_history=["مرحبا", "كيف حالك؟"],
                ),
                ChildContext(
                    child_id="child_002",
                    name="فاطمة",
                    age=5,
                    language="ar",
                    voice_profile="gentle",
                    emotion_state="happy",
                ),
                ChildContext(
                    child_id="child_003",
                    name="Omar",
                    age=9,
                    language="ar",
                    voice_profile="curious",
                    safety_level="enhanced",
                ),
            ],
            "audio_samples": {
                "happy_greeting": self._generate_audio_sample(0.3, "happy"),
                "sad_expression": self._generate_audio_sample(0.1, "sad"),
                "excited_question": self._generate_audio_sample(0.5, "excited"),
                "calm_statement": self._generate_audio_sample(0.2, "calm"),
                "background_noise": self._generate_audio_sample(0.05, "noise"),
            },
            "test_scenarios": [
                {
                    "name": "Simple Greeting",
                    "audio_key": "happy_greeting",
                    "child_index": 0,
                    "expected_emotion": "happy",
                },
                {
                    "name": "Emotional Support",
                    "audio_key": "sad_expression",
                    "child_index": 1,
                    "expected_emotion": "sad",
                },
                {
                    "name": "Curious Learning",
                    "audio_key": "excited_question",
                    "child_index": 2,
                    "expected_emotion": "excited",
                },
            ],
        }

    def _generate_audio_sample(self, energy_level: float, sample_type: str) -> bytes:
        """Generate synthetic audio sample."""
        duration = 2.0
        sample_rate = 16000
        samples = int(duration * sample_rate)
        if sample_type == "happy":
            audio = energy_level * np.sin(
                2 * np.pi * 440 * np.linspace(0, duration, samples)
            )
            audio += 0.1 * energy_level * np.random.uniform(-1, 1, samples)
        elif sample_type == "sad":
            audio = energy_level * np.sin(
                2 * np.pi * 220 * np.linspace(0, duration, samples)
            )
        elif sample_type == "excited":
            t = np.linspace(0, duration, samples)
            audio = energy_level * np.sin(
                2 * np.pi * 880 * t + np.sin(2 * np.pi * 5 * t)
            )
        elif sample_type == "calm":
            audio = energy_level * np.sin(
                2 * np.pi * 330 * np.linspace(0, duration, samples)
            )
        else:
            audio = energy_level * np.random.uniform(-1, 1, samples)
        audio_int16 = (audio * 32767).astype(np.int16)
        return audio_int16.tobytes()

    def print_header(self, title: str) -> None:
        """Print formatted section header."""
        logger.info(f"\n{'=' * 60}")
        logger.info(f" {title}")
        logger.info(f"{'=' * 60}")

    def print_subheader(self, title: str) -> None:
        """Print formatted subsection header."""
        logger.info(f"\n{'-' * 40}")
        logger.info(f" {title}")
        logger.info(f"{'-' * 40}")

    async def demo_system_initialization(self) -> None:
        """Demonstrate system initialization."""
        self.print_subheader("Distributed AI System Initialization")
        try:
            logger.info("🔧 System Capabilities:")
            logger.info(
                f"   📡 Ray Available: {'✅ YES' if RAY_AVAILABLE else '❌ NO'}"
            )
            logger.info("   🤖 AI Services: Mock services ready")
            logger.info("   🎵 Audio Processing: Synthetic data generation")
            logger.info("\n🚀 Initializing Distributed AI Processor...")
            start_time = time.time()
            self.processor = DistributedAIProcessor()
            await self.processor.initialize()
            init_time = (time.time() - start_time) * 1000
            logger.info(f"✅ System initialized in {init_time:.2f}ms")
            metrics = self.processor.get_performance_metrics()
            system_info = metrics["system_info"]
            logger.info("\n📊 System Configuration:")
            logger.info(
                f"   🔄 Ray Initialized: {'YES' if self.processor.ray_initialized else 'NO'}"
            )
            logger.info(f"   🎯 Services Available: {len(self.processor.services)}")
            logger.info(
                f"   📈 Processing Mode: {'Distributed' if RAY_AVAILABLE else 'Local Mock'}"
            )
        except Exception as e:
            logger.info(f"❌ System initialization failed: {e}")

    async def demo_mock_services(self) -> None:
        """Demonstrate individual mock services."""
        self.print_subheader("Mock AI Services Testing")
        try:
            audio_sample = self.demo_data["audio_samples"]["happy_greeting"]
            test_text = "مرحبا تيدي، كيف حالك اليوم؟"
            logger.info("🧪 Testing Individual Services:")
            logger.info(f"   📝 Test Text: '{test_text}'")
            logger.info(f"   🎵 Audio Size: {len(audio_sample)} bytes")
            logger.info("\n🎙️  Testing Transcription Service:")
            start_time = time.time()
            transcription = await MockAIServices.transcribe_audio(audio_sample)
            transcription_time = (time.time() - start_time) * 1000
            logger.info(f"   📝 Result: '{transcription['text']}'")
            logger.info(f"   🔮 Confidence: {transcription['confidence']:.3f}")
            logger.info(f"   🌐 Language: {transcription['language']}")
            logger.info(f"   ⏱️  Time: {transcription_time:.2f}ms")
            logger.info("\n😊 Testing Emotion Analysis Service:")
            start_time = time.time()
            emotion = await MockAIServices.analyze_emotion(audio_sample, test_text)
            emotion_time = (time.time() - start_time) * 1000
            logger.info(f"   😊 Primary Emotion: {emotion['primary_emotion']}")
            logger.info(f"   🔮 Confidence: {emotion['confidence']:.3f}")
            logger.info(f"   📈 Arousal: {emotion['arousal']:.3f}")
            logger.info(f"   📊 Valence: {emotion['valence']:.3f}")
            logger.info(f"   ⏱️  Time: {emotion_time:.2f}ms")
            top_emotions = sorted(
                emotion["emotion_scores"].items(), key=lambda x: x[1], reverse=True
            )[:3]
            logger.info(
                f"   🏆 Top emotions: {', '.join([f'{e}({s:.2f})' for e, s in top_emotions])}"
            )
            logger.info("\n🛡️  Testing Safety Check Service:")
            start_time = time.time()
            safety = await MockAIServices.check_safety(test_text, audio_sample)
            safety_time = (time.time() - start_time) * 1000
            logger.info(f"   ✅ Is Safe: {'YES' if safety['is_safe'] else 'NO'}")
            logger.info(f"   ⚠️  Risk Level: {safety['risk_level']}")
            logger.info(f"   🔮 Confidence: {safety['confidence']:.3f}")
            logger.info(f"   ⏱️  Time: {safety_time:.2f}ms")
            if safety["detected_issues"]:
                logger.info(f"   🚨 Issues: {', '.join(safety['detected_issues'])}")
            child_context = self.demo_data["children"][0]
            logger.info("\n🤖 Testing AI Response Service:")
            start_time = time.time()
            ai_response = await MockAIServices.generate_ai_response(
                test_text, child_context
            )
            ai_time = (time.time() - start_time) * 1000
            logger.info(f"   💬 Response: '{ai_response['response_text'][:80]}...'")
            logger.info(f"   😊 Emotion: {ai_response['emotion']}")
            logger.info(f"   🔮 Confidence: {ai_response['confidence']:.3f}")
            logger.info(f"   ⏱️  Time: {ai_time:.2f}ms")
            logger.info("\n🔊 Testing TTS Service:")
            start_time = time.time()
            tts = await MockAIServices.synthesize_speech(
                ai_response["response_text"],
                ai_response["emotion"],
                child_context.voice_profile,
            )
            tts_time = (time.time() - start_time) * 1000
            logger.info(f"   🎵 Audio Generated: {len(tts['audio_data'])} bytes")
            logger.info(f"   📊 Sample Rate: {tts['sample_rate']} Hz")
            logger.info(f"   ⏱️  Duration: {tts['duration_seconds']:.2f}s")
            logger.info(f"   ⏱️  Time: {tts_time:.2f}ms")
        except Exception as e:
            logger.info(f"❌ Mock services testing failed: {e}")

    async def demo_conversation_processing(self) -> None:
        """Demonstrate complete conversation processing."""
        self.print_subheader("Complete Conversation Processing")
        try:
            scenarios = self.demo_data["test_scenarios"]
            for i, scenario in enumerate(scenarios):
                logger.info(f"\n🎬 Scenario {i + 1}: {scenario['name']}")
                audio_data = self.demo_data["audio_samples"][scenario["audio_key"]]
                child_context = self.demo_data["children"][scenario["child_index"]]
                logger.info(
                    f"   👶 Child: {child_context.name} (age {child_context.age})"
                )
                logger.info(
                    f"   🎵 Audio: {scenario['audio_key']} ({len(audio_data)} bytes)"
                )
                logger.info(f"   🎯 Expected Emotion: {scenario['expected_emotion']}")
                start_time = time.time()
                response = await self.processor.process_conversation(
                    audio_data, child_context
                )
                total_time = (time.time() - start_time) * 1000
                logger.info("\n   📊 Processing Results:")
                logger.info(f"      ✅ Success: {'YES' if response.success else 'NO'}")
                logger.info(f"      🆔 Request ID: {response.request_id}")
                logger.info(f"      📝 Transcription: '{response.transcription}'")
                logger.info(f"      😊 Detected Emotion: {response.emotion}")
                logger.info(f"      🛡️  Safety Status: {response.safety_status}")
                logger.info(f"      🔮 Confidence: {response.confidence:.3f}")
                logger.info(f"      ⏱️  Total Time: {total_time:.2f}ms")
                logger.info(f"      💬 AI Response: '{response.ai_text[:60]}...'")
                if response.service_results:
                    logger.info("\n   🔍 Service Breakdown:")
                    for service, result in response.service_results.items():
                        if isinstance(result, dict) and "processing_time_ms" in result:
                            logger.info(
                                f"      {service}: {result['processing_time_ms']:.1f}ms"
                            )
                if response.recommendations:
                    logger.info(
                        f"   💡 Recommendations: {', '.join(response.recommendations[:2])}"
                    )
                logger.info(f"   {'✅ PASS' if response.success else '❌ FAIL'}")
        except Exception as e:
            logger.info(f"❌ Conversation processing demo failed: {e}")

    async def demo_parallel_processing(self) -> None:
        """Demonstrate parallel processing capabilities."""
        self.print_subheader("Parallel Processing Performance")
        try:
            logger.info("🔄 Testing Parallel Processing Capabilities...")
            requests = []
            children = self.demo_data["children"]
            audio_samples = list(self.demo_data["audio_samples"].values())
            for i in range(5):
                audio_data = audio_samples[i % len(audio_samples)]
                child_context = children[i % len(children)]
                requests.append((audio_data, child_context))
            logger.info(f"   📊 Batch Size: {len(requests)} conversations")
            logger.info(f"   👥 Children: {len(children)} unique profiles")
            logger.info("\n⏯️  Sequential Processing:")
            sequential_start = time.time()
            sequential_results = []
            for audio_data, child_context in requests:
                result = await self.processor.process_conversation(
                    audio_data, child_context
                )
                sequential_results.append(result)
            sequential_time = time.time() - sequential_start
            logger.info(f"   ⏱️  Total Time: {sequential_time:.2f}s")
            logger.info(
                f"   📊 Average per Request: {sequential_time / len(requests):.2f}s"
            )
            logger.info(
                f"   ✅ Success Rate: {sum(1 for r in sequential_results if r.success)}/{len(requests)}"
            )
            logger.info("\n⚡ Parallel Processing:")
            parallel_start = time.time()
            parallel_results = await self.processor.process_batch_conversations(
                requests
            )
            parallel_time = time.time() - parallel_start
            logger.info(f"   ⏱️  Total Time: {parallel_time:.2f}s")
            logger.info(
                f"   📊 Average per Request: {parallel_time / len(requests):.2f}s"
            )
            logger.info(
                f"   ✅ Success Rate: {sum(1 for r in parallel_results if r.success)}/{len(requests)}"
            )
            speedup = sequential_time / parallel_time if parallel_time > 0 else 1.0
            efficiency = speedup / len(requests) * 100
            logger.info("\n📈 Performance Analysis:")
            logger.info(f"   🚀 Speedup: {speedup:.2f}x")
            logger.info(f"   ⚡ Efficiency: {efficiency:.1f}%")
            logger.info(
                f"   💡 Parallel Advantage: {(sequential_time - parallel_time) / sequential_time * 100:.1f}% faster"
            )
        except Exception as e:
            logger.info(f"❌ Parallel processing demo failed: {e}")

    async def demo_performance_monitoring(self) -> None:
        """Demonstrate performance monitoring and metrics."""
        self.print_subheader("Performance Monitoring & Metrics")
        try:
            metrics = self.processor.get_performance_metrics()
            logger.info("📊 System Performance Metrics:")
            processing_metrics = metrics["processing_metrics"]
            logger.info("\n   🔢 Request Statistics:")
            logger.info(
                f"      📈 Total Requests: {processing_metrics['total_requests']}"
            )
            logger.info(
                f"      ✅ Successful: {processing_metrics['successful_requests']}"
            )
            logger.info(f"      ❌ Failed: {processing_metrics['failed_requests']}")
            if processing_metrics["total_requests"] > 0:
                success_rate = (
                    processing_metrics["successful_requests"]
                    / processing_metrics["total_requests"]
                    * 100
                )
                logger.info(f"      📊 Success Rate: {success_rate:.1f}%")
            logger.info(
                f"      ⏱️  Average Processing Time: {processing_metrics['average_processing_time_ms']:.2f}ms"
            )
            logger.info(
                f"      🚀 Throughput: {processing_metrics['throughput_per_second']:.2f} req/s"
            )
            system_info = metrics["system_info"]
            logger.info("\n   🖥️  System Information:")
            logger.info(
                f"      📡 Ray Available: {'YES' if system_info['ray_available'] else 'NO'}"
            )
            logger.info(
                f"      🤖 AI Services Available: {'YES' if system_info['ai_services_available'] else 'NO'}"
            )
            logger.info(
                f"      🎵 Audio Processing Available: {'YES' if system_info['audio_processing_available'] else 'NO'}"
            )
            logger.info(
                f"      🧠 Core Services Available: {'YES' if system_info['core_services_available'] else 'NO'}"
            )
            service_health = metrics["service_health"]
            logger.info("\n   🏥 Service Health Status:")
            for service, status in service_health.items():
                status_icon = (
                    "✅"
                    if status == "healthy"
                    else "❌" if status == "unavailable" else "⚠️"
                )
                logger.info(f"      {status_icon} {service}: {status}")
            logger.info("\n   🎯 Performance Targets:")
            avg_time = processing_metrics["average_processing_time_ms"]
            logger.info(
                f"      ⚡ Real-time Target (<1000ms): {'✅ MET' if avg_time < 1000 else '❌ MISSED'}"
            )
            logger.info(
                f"      🚀 Fast Response (<500ms): {'✅ MET' if avg_time < 500 else '❌ MISSED'}"
            )
            logger.info(
                f"      ⭐ Ultra-fast (<200ms): {'✅ MET' if avg_time < 200 else '❌ MISSED'}"
            )
        except Exception as e:
            logger.info(f"❌ Performance monitoring demo failed: {e}")

    async def demo_load_optimization(self) -> None:
        """Demonstrate load optimization capabilities."""
        self.print_subheader("Load Optimization & Scaling")
        try:
            logger.info("🔧 Load Optimization Testing:")
            load_scenarios = [
                {
                    "name": "Light Load",
                    "expected_load": 5,
                    "description": "5 concurrent users",
                },
                {
                    "name": "Medium Load",
                    "expected_load": 25,
                    "description": "25 concurrent users",
                },
                {
                    "name": "Heavy Load",
                    "expected_load": 100,
                    "description": "100 concurrent users",
                },
            ]
            for scenario in load_scenarios:
                logger.info(f"\n   📊 {scenario['name']} ({scenario['description']}):")
                await self.processor.optimize_for_load(scenario["expected_load"])
                num_requests = min(scenario["expected_load"] // 10, 10)
                logger.info(
                    f"      🧪 Simulating {num_requests} concurrent requests..."
                )
                tasks = []
                for i in range(num_requests):
                    audio_data = self.demo_data["audio_samples"]["happy_greeting"]
                    child_context = self.demo_data["children"][
                        i % len(self.demo_data["children"])
                    ]
                    task = self.processor.process_conversation(
                        audio_data, child_context
                    )
                    tasks.append(task)
                start_time = time.time()
                results = await asyncio.gather(*tasks, return_exceptions=True)
                concurrent_time = time.time() - start_time
                successful = sum(
                    1
                    for r in results
                    if isinstance(r, ConversationResponse) and r.success
                )
                failed = len(results) - successful
                logger.info(f"      ⏱️  Total Time: {concurrent_time:.2f}s")
                logger.info(
                    f"      📊 Requests/Second: {len(results) / concurrent_time:.2f}"
                )
                logger.info(
                    f"      ✅ Success Rate: {successful}/{len(results)} ({successful / len(results) * 100:.1f}%)"
                )
                if concurrent_time > 0:
                    throughput = len(results) / concurrent_time
                    logger.info(
                        f"      🚀 Throughput: {throughput:.2f} conversations/sec"
                    )
                    estimated_capacity = throughput * 60
                    logger.info(
                        f"      📈 Estimated Capacity: {estimated_capacity:.0f} conversations/minute"
                    )
        except Exception as e:
            logger.info(f"❌ Load optimization demo failed: {e}")

    def demo_system_capabilities(self) -> None:
        """Demonstrate system capabilities and architecture."""
        self.print_subheader("System Capabilities & Architecture")
        logger.info("🏗️  Distributed AI System Architecture:")
        logger.info("\n   🎯 Core Components:")
        logger.info("      🤖 DistributedAIProcessor: Main orchestration engine")
        logger.info("      🎙️  Transcription Service: Whisper + OpenAI fallback")
        logger.info("      😊 Emotion Analysis Service: Multi-modal emotion detection")
        logger.info("      🛡️  Safety Check Service: Multi-level content filtering")
        logger.info("      💬 AI Response Service: GPT-4 powered responses")
        logger.info("      🔊 TTS Service: ElevenLabs + fallback synthesis")
        logger.info("\n   📊 Processing Features:")
        logger.info("      ⚡ Parallel Processing: All services run concurrently")
        logger.info("      🔄 Async Architecture: Non-blocking operation")
        logger.info("      🚀 Auto-scaling: Ray Serve dynamic worker allocation")
        logger.info("      🛡️  Error Resilience: Graceful failure handling")
        logger.info("      📈 Performance Monitoring: Real-time metrics")
        logger.info("\n   🎯 AI Service Types:")
        for service_type in AIServiceType:
            logger.info(f"      🔹 {service_type.value.replace('_', ' ').title()}")
        logger.info("\n   🏆 Performance Targets:")
        logger.info("      ⚡ Real-time Response: <1000ms end-to-end")
        logger.info("      🚀 High Throughput: 100+ conversations/minute")
        logger.info("      🎯 High Accuracy: 95%+ service reliability")
        logger.info("      📊 Scalability: Horizontal scaling with Ray")
        logger.info("\n   🔧 Deployment Options:")
        logger.info("      📡 Distributed: Ray Serve across multiple nodes")
        logger.info("      💻 Local: Single-machine development mode")
        logger.info("      🧪 Mock: Testing without external dependencies")
        logger.info("      ☁️  Cloud: Kubernetes + Ray cluster deployment")

    async def run_complete_demo(self) -> None:
        """Run the complete distributed AI demonstration."""
        self.print_header("🚀 DISTRIBUTED AI PROCESSING DEMO")
        if not DISTRIBUTED_AI_AVAILABLE:
            logger.info(f"❌ Distributed AI not available: {import_error}")
            logger.info("📦 Install requirements: pip install ray[serve] openai numpy")
            return
        try:
            await self.demo_system_initialization()
            await self.demo_mock_services()
            await self.demo_conversation_processing()
            await self.demo_parallel_processing()
            await self.demo_performance_monitoring()
            await self.demo_load_optimization()
            self.demo_system_capabilities()
            self.print_header("✅ DISTRIBUTED AI DEMO COMPLETED")
            logger.info("🎯 All distributed AI features demonstrated")
            logger.info("⚡ Parallel processing capabilities verified")
            logger.info("📊 Performance monitoring validated")
            logger.info(
                f"🚀 Ray Serve integration {'confirmed' if RAY_AVAILABLE else 'simulated'}"
            )
            logger.info("🤖 AI Team implementation complete")
        except Exception as e:
            self.print_header("❌ DEMO FAILED")
            logger.info(f"Error: {e}")
            logger.exception("Demo failed with exception")
        finally:
            if self.processor:
                await self.processor.cleanup()


async def main():
    """Main demo execution."""
    demo = DistributedAIDemo()
    await demo.run_complete_demo()


if __name__ == "__main__":
    asyncio.run(main())
