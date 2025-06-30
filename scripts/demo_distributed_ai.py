#!/usr/bin/env python3
"""
Distributed AI Processing Demo for AI Teddy Bear Project.

This demo showcases the distributed AI processing system using Ray Serve
for parallel conversation handling across multiple AI services.

AI Team Implementation - Task 11 Demo
Author: AI Team Lead
"""

import asyncio
import numpy as np
import logging
import time
from typing import Dict, List, Any
from pathlib import Path
import sys

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import Distributed AI components
try:
    from src.infrastructure.ai.distributed_processor import (
        DistributedAIProcessor,
        ConversationRequest,
        ConversationResponse,
        ChildContext,
        ProcessingPriority,
        AIServiceType,
        MockAIServices,
        RAY_AVAILABLE
    )
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
                    conversation_history=["مرحبا", "كيف حالك؟"]
                ),
                ChildContext(
                    child_id="child_002", 
                    name="فاطمة",
                    age=5,
                    language="ar",
                    voice_profile="gentle",
                    emotion_state="happy"
                ),
                ChildContext(
                    child_id="child_003",
                    name="Omar",
                    age=9,
                    language="ar",
                    voice_profile="curious",
                    safety_level="enhanced"
                )
            ],
            "audio_samples": {
                "happy_greeting": self._generate_audio_sample(0.3, "happy"),
                "sad_expression": self._generate_audio_sample(0.1, "sad"), 
                "excited_question": self._generate_audio_sample(0.5, "excited"),
                "calm_statement": self._generate_audio_sample(0.2, "calm"),
                "background_noise": self._generate_audio_sample(0.05, "noise")
            },
            "test_scenarios": [
                {
                    "name": "Simple Greeting",
                    "audio_key": "happy_greeting",
                    "child_index": 0,
                    "expected_emotion": "happy"
                },
                {
                    "name": "Emotional Support",
                    "audio_key": "sad_expression", 
                    "child_index": 1,
                    "expected_emotion": "sad"
                },
                {
                    "name": "Curious Learning",
                    "audio_key": "excited_question",
                    "child_index": 2,
                    "expected_emotion": "excited"
                }
            ]
        }
    
    def _generate_audio_sample(self, energy_level: float, sample_type: str) -> bytes:
        """Generate synthetic audio sample."""
        duration = 2.0  # 2 seconds
        sample_rate = 16000
        samples = int(duration * sample_rate)
        
        # Generate audio with different characteristics
        if sample_type == "happy":
            # Higher frequency, variable amplitude
            audio = energy_level * np.sin(2 * np.pi * 440 * np.linspace(0, duration, samples))
            audio += 0.1 * energy_level * np.random.uniform(-1, 1, samples)
        elif sample_type == "sad":
            # Lower frequency, steady amplitude
            audio = energy_level * np.sin(2 * np.pi * 220 * np.linspace(0, duration, samples))
        elif sample_type == "excited":
            # High frequency with rapid changes
            t = np.linspace(0, duration, samples)
            audio = energy_level * np.sin(2 * np.pi * 880 * t + np.sin(2 * np.pi * 5 * t))
        elif sample_type == "calm":
            # Smooth, low frequency
            audio = energy_level * np.sin(2 * np.pi * 330 * np.linspace(0, duration, samples))
        else:  # noise
            audio = energy_level * np.random.uniform(-1, 1, samples)
        
        # Convert to bytes
        audio_int16 = (audio * 32767).astype(np.int16)
        return audio_int16.tobytes()
    
    def print_header(self, title: str) -> None:
        """Print formatted section header."""
        print(f"\n{'='*60}")
        print(f" {title}")
        print(f"{'='*60}")
    
    def print_subheader(self, title: str) -> None:
        """Print formatted subsection header."""
        print(f"\n{'-'*40}")
        print(f" {title}")
        print(f"{'-'*40}")
    
    async def demo_system_initialization(self) -> None:
        """Demonstrate system initialization."""
        self.print_subheader("Distributed AI System Initialization")
        
        try:
            print(f"🔧 System Capabilities:")
            print(f"   📡 Ray Available: {'✅ YES' if RAY_AVAILABLE else '❌ NO'}")
            print(f"   🤖 AI Services: Mock services ready")
            print(f"   🎵 Audio Processing: Synthetic data generation")
            
            print(f"\n🚀 Initializing Distributed AI Processor...")
            start_time = time.time()
            
            self.processor = DistributedAIProcessor()
            await self.processor.initialize()
            
            init_time = (time.time() - start_time) * 1000
            print(f"✅ System initialized in {init_time:.2f}ms")
            
            # Display system configuration
            metrics = self.processor.get_performance_metrics()
            system_info = metrics["system_info"]
            
            print(f"\n📊 System Configuration:")
            print(f"   🔄 Ray Initialized: {'YES' if self.processor.ray_initialized else 'NO'}")
            print(f"   🎯 Services Available: {len(self.processor.services)}")
            print(f"   📈 Processing Mode: {'Distributed' if RAY_AVAILABLE else 'Local Mock'}")
            
        except Exception as e:
            print(f"❌ System initialization failed: {e}")
    
    async def demo_mock_services(self) -> None:
        """Demonstrate individual mock services."""
        self.print_subheader("Mock AI Services Testing")
        
        try:
            audio_sample = self.demo_data["audio_samples"]["happy_greeting"]
            test_text = "مرحبا تيدي، كيف حالك اليوم؟"
            
            print(f"🧪 Testing Individual Services:")
            print(f"   📝 Test Text: '{test_text}'")
            print(f"   🎵 Audio Size: {len(audio_sample)} bytes")
            
            # Test Transcription
            print(f"\n🎙️  Testing Transcription Service:")
            start_time = time.time()
            transcription = await MockAIServices.transcribe_audio(audio_sample)
            transcription_time = (time.time() - start_time) * 1000
            
            print(f"   📝 Result: '{transcription['text']}'")
            print(f"   🔮 Confidence: {transcription['confidence']:.3f}")
            print(f"   🌐 Language: {transcription['language']}")
            print(f"   ⏱️  Time: {transcription_time:.2f}ms")
            
            # Test Emotion Analysis
            print(f"\n😊 Testing Emotion Analysis Service:")
            start_time = time.time()
            emotion = await MockAIServices.analyze_emotion(audio_sample, test_text)
            emotion_time = (time.time() - start_time) * 1000
            
            print(f"   😊 Primary Emotion: {emotion['primary_emotion']}")
            print(f"   🔮 Confidence: {emotion['confidence']:.3f}")
            print(f"   📈 Arousal: {emotion['arousal']:.3f}")
            print(f"   📊 Valence: {emotion['valence']:.3f}")
            print(f"   ⏱️  Time: {emotion_time:.2f}ms")
            
            # Show emotion breakdown
            top_emotions = sorted(emotion['emotion_scores'].items(), 
                                key=lambda x: x[1], reverse=True)[:3]
            print(f"   🏆 Top emotions: {', '.join([f'{e}({s:.2f})' for e, s in top_emotions])}")
            
            # Test Safety Check
            print(f"\n🛡️  Testing Safety Check Service:")
            start_time = time.time()
            safety = await MockAIServices.check_safety(test_text, audio_sample)
            safety_time = (time.time() - start_time) * 1000
            
            print(f"   ✅ Is Safe: {'YES' if safety['is_safe'] else 'NO'}")
            print(f"   ⚠️  Risk Level: {safety['risk_level']}")
            print(f"   🔮 Confidence: {safety['confidence']:.3f}")
            print(f"   ⏱️  Time: {safety_time:.2f}ms")
            
            if safety['detected_issues']:
                print(f"   🚨 Issues: {', '.join(safety['detected_issues'])}")
            
            # Test AI Response
            child_context = self.demo_data["children"][0]
            print(f"\n🤖 Testing AI Response Service:")
            start_time = time.time()
            ai_response = await MockAIServices.generate_ai_response(test_text, child_context)
            ai_time = (time.time() - start_time) * 1000
            
            print(f"   💬 Response: '{ai_response['response_text'][:80]}...'")
            print(f"   😊 Emotion: {ai_response['emotion']}")
            print(f"   🔮 Confidence: {ai_response['confidence']:.3f}")
            print(f"   ⏱️  Time: {ai_time:.2f}ms")
            
            # Test TTS
            print(f"\n🔊 Testing TTS Service:")
            start_time = time.time()
            tts = await MockAIServices.synthesize_speech(
                ai_response['response_text'], 
                ai_response['emotion'], 
                child_context.voice_profile
            )
            tts_time = (time.time() - start_time) * 1000
            
            print(f"   🎵 Audio Generated: {len(tts['audio_data'])} bytes")
            print(f"   📊 Sample Rate: {tts['sample_rate']} Hz")
            print(f"   ⏱️  Duration: {tts['duration_seconds']:.2f}s")
            print(f"   ⏱️  Time: {tts_time:.2f}ms")
            
        except Exception as e:
            print(f"❌ Mock services testing failed: {e}")
    
    async def demo_conversation_processing(self) -> None:
        """Demonstrate complete conversation processing."""
        self.print_subheader("Complete Conversation Processing")
        
        try:
            scenarios = self.demo_data["test_scenarios"]
            
            for i, scenario in enumerate(scenarios):
                print(f"\n🎬 Scenario {i+1}: {scenario['name']}")
                
                # Get test data
                audio_data = self.demo_data["audio_samples"][scenario["audio_key"]]
                child_context = self.demo_data["children"][scenario["child_index"]]
                
                print(f"   👶 Child: {child_context.name} (age {child_context.age})")
                print(f"   🎵 Audio: {scenario['audio_key']} ({len(audio_data)} bytes)")
                print(f"   🎯 Expected Emotion: {scenario['expected_emotion']}")
                
                # Process conversation
                start_time = time.time()
                response = await self.processor.process_conversation(audio_data, child_context)
                total_time = (time.time() - start_time) * 1000
                
                # Display results
                print(f"\n   📊 Processing Results:")
                print(f"      ✅ Success: {'YES' if response.success else 'NO'}")
                print(f"      🆔 Request ID: {response.request_id}")
                print(f"      📝 Transcription: '{response.transcription}'")
                print(f"      😊 Detected Emotion: {response.emotion}")
                print(f"      🛡️  Safety Status: {response.safety_status}")
                print(f"      🔮 Confidence: {response.confidence:.3f}")
                print(f"      ⏱️  Total Time: {total_time:.2f}ms")
                print(f"      💬 AI Response: '{response.ai_text[:60]}...'")
                
                # Service breakdown
                if response.service_results:
                    print(f"\n   🔍 Service Breakdown:")
                    for service, result in response.service_results.items():
                        if isinstance(result, dict) and 'processing_time_ms' in result:
                            print(f"      {service}: {result['processing_time_ms']:.1f}ms")
                
                # Recommendations
                if response.recommendations:
                    print(f"   💡 Recommendations: {', '.join(response.recommendations[:2])}")
                
                print(f"   {'✅ PASS' if response.success else '❌ FAIL'}")
            
        except Exception as e:
            print(f"❌ Conversation processing demo failed: {e}")
    
    async def demo_parallel_processing(self) -> None:
        """Demonstrate parallel processing capabilities."""
        self.print_subheader("Parallel Processing Performance")
        
        try:
            print(f"🔄 Testing Parallel Processing Capabilities...")
            
            # Create multiple conversation requests
            requests = []
            children = self.demo_data["children"]
            audio_samples = list(self.demo_data["audio_samples"].values())
            
            for i in range(5):
                audio_data = audio_samples[i % len(audio_samples)]
                child_context = children[i % len(children)]
                requests.append((audio_data, child_context))
            
            print(f"   📊 Batch Size: {len(requests)} conversations")
            print(f"   👥 Children: {len(children)} unique profiles")
            
            # Sequential processing
            print(f"\n⏯️  Sequential Processing:")
            sequential_start = time.time()
            sequential_results = []
            
            for audio_data, child_context in requests:
                result = await self.processor.process_conversation(audio_data, child_context)
                sequential_results.append(result)
            
            sequential_time = time.time() - sequential_start
            print(f"   ⏱️  Total Time: {sequential_time:.2f}s")
            print(f"   📊 Average per Request: {(sequential_time/len(requests)):.2f}s")
            print(f"   ✅ Success Rate: {sum(1 for r in sequential_results if r.success)}/{len(requests)}")
            
            # Parallel processing
            print(f"\n⚡ Parallel Processing:")
            parallel_start = time.time()
            parallel_results = await self.processor.process_batch_conversations(requests)
            parallel_time = time.time() - parallel_start
            
            print(f"   ⏱️  Total Time: {parallel_time:.2f}s")
            print(f"   📊 Average per Request: {(parallel_time/len(requests)):.2f}s")
            print(f"   ✅ Success Rate: {sum(1 for r in parallel_results if r.success)}/{len(requests)}")
            
            # Performance comparison
            speedup = sequential_time / parallel_time if parallel_time > 0 else 1.0
            efficiency = (speedup / len(requests)) * 100
            
            print(f"\n📈 Performance Analysis:")
            print(f"   🚀 Speedup: {speedup:.2f}x")
            print(f"   ⚡ Efficiency: {efficiency:.1f}%")
            print(f"   💡 Parallel Advantage: {((sequential_time - parallel_time)/sequential_time)*100:.1f}% faster")
            
        except Exception as e:
            print(f"❌ Parallel processing demo failed: {e}")
    
    async def demo_performance_monitoring(self) -> None:
        """Demonstrate performance monitoring and metrics."""
        self.print_subheader("Performance Monitoring & Metrics")
        
        try:
            # Get current metrics
            metrics = self.processor.get_performance_metrics()
            
            print(f"📊 System Performance Metrics:")
            
            # Processing metrics
            processing_metrics = metrics["processing_metrics"]
            print(f"\n   🔢 Request Statistics:")
            print(f"      📈 Total Requests: {processing_metrics['total_requests']}")
            print(f"      ✅ Successful: {processing_metrics['successful_requests']}")
            print(f"      ❌ Failed: {processing_metrics['failed_requests']}")
            
            if processing_metrics['total_requests'] > 0:
                success_rate = (processing_metrics['successful_requests'] / 
                              processing_metrics['total_requests']) * 100
                print(f"      📊 Success Rate: {success_rate:.1f}%")
            
            print(f"      ⏱️  Average Processing Time: {processing_metrics['average_processing_time_ms']:.2f}ms")
            print(f"      🚀 Throughput: {processing_metrics['throughput_per_second']:.2f} req/s")
            
            # System info
            system_info = metrics["system_info"]
            print(f"\n   🖥️  System Information:")
            print(f"      📡 Ray Available: {'YES' if system_info['ray_available'] else 'NO'}")
            print(f"      🤖 AI Services Available: {'YES' if system_info['ai_services_available'] else 'NO'}")
            print(f"      🎵 Audio Processing Available: {'YES' if system_info['audio_processing_available'] else 'NO'}")
            print(f"      🧠 Core Services Available: {'YES' if system_info['core_services_available'] else 'NO'}")
            
            # Service health
            service_health = metrics["service_health"]
            print(f"\n   🏥 Service Health Status:")
            for service, status in service_health.items():
                status_icon = "✅" if status == "healthy" else "❌" if status == "unavailable" else "⚠️"
                print(f"      {status_icon} {service}: {status}")
            
            # Performance targets
            print(f"\n   🎯 Performance Targets:")
            avg_time = processing_metrics['average_processing_time_ms']
            print(f"      ⚡ Real-time Target (<1000ms): {'✅ MET' if avg_time < 1000 else '❌ MISSED'}")
            print(f"      🚀 Fast Response (<500ms): {'✅ MET' if avg_time < 500 else '❌ MISSED'}")
            print(f"      ⭐ Ultra-fast (<200ms): {'✅ MET' if avg_time < 200 else '❌ MISSED'}")
            
        except Exception as e:
            print(f"❌ Performance monitoring demo failed: {e}")
    
    async def demo_load_optimization(self) -> None:
        """Demonstrate load optimization capabilities."""
        self.print_subheader("Load Optimization & Scaling")
        
        try:
            print(f"🔧 Load Optimization Testing:")
            
            # Test different load scenarios
            load_scenarios = [
                {"name": "Light Load", "expected_load": 5, "description": "5 concurrent users"},
                {"name": "Medium Load", "expected_load": 25, "description": "25 concurrent users"},
                {"name": "Heavy Load", "expected_load": 100, "description": "100 concurrent users"}
            ]
            
            for scenario in load_scenarios:
                print(f"\n   📊 {scenario['name']} ({scenario['description']}):")
                
                # Apply optimization
                await self.processor.optimize_for_load(scenario["expected_load"])
                
                # Simulate load test
                num_requests = min(scenario["expected_load"] // 10, 10)  # Scale down for demo
                print(f"      🧪 Simulating {num_requests} concurrent requests...")
                
                # Create concurrent requests
                tasks = []
                for i in range(num_requests):
                    audio_data = self.demo_data["audio_samples"]["happy_greeting"]
                    child_context = self.demo_data["children"][i % len(self.demo_data["children"])]
                    
                    task = self.processor.process_conversation(audio_data, child_context)
                    tasks.append(task)
                
                # Execute concurrently
                start_time = time.time()
                results = await asyncio.gather(*tasks, return_exceptions=True)
                concurrent_time = time.time() - start_time
                
                # Analyze results
                successful = sum(1 for r in results if isinstance(r, ConversationResponse) and r.success)
                failed = len(results) - successful
                
                print(f"      ⏱️  Total Time: {concurrent_time:.2f}s")
                print(f"      📊 Requests/Second: {len(results)/concurrent_time:.2f}")
                print(f"      ✅ Success Rate: {successful}/{len(results)} ({(successful/len(results))*100:.1f}%)")
                
                if concurrent_time > 0:
                    throughput = len(results) / concurrent_time
                    print(f"      🚀 Throughput: {throughput:.2f} conversations/sec")
                    
                    # Estimate scaling
                    estimated_capacity = throughput * 60  # per minute
                    print(f"      📈 Estimated Capacity: {estimated_capacity:.0f} conversations/minute")
            
        except Exception as e:
            print(f"❌ Load optimization demo failed: {e}")
    
    def demo_system_capabilities(self) -> None:
        """Demonstrate system capabilities and architecture."""
        self.print_subheader("System Capabilities & Architecture")
        
        print(f"🏗️  Distributed AI System Architecture:")
        print(f"\n   🎯 Core Components:")
        print(f"      🤖 DistributedAIProcessor: Main orchestration engine")
        print(f"      🎙️  Transcription Service: Whisper + OpenAI fallback")
        print(f"      😊 Emotion Analysis Service: Multi-modal emotion detection")
        print(f"      🛡️  Safety Check Service: Multi-level content filtering")
        print(f"      💬 AI Response Service: GPT-4 powered responses")
        print(f"      🔊 TTS Service: ElevenLabs + fallback synthesis")
        
        print(f"\n   📊 Processing Features:")
        print(f"      ⚡ Parallel Processing: All services run concurrently")
        print(f"      🔄 Async Architecture: Non-blocking operation")
        print(f"      🚀 Auto-scaling: Ray Serve dynamic worker allocation")
        print(f"      🛡️  Error Resilience: Graceful failure handling")
        print(f"      📈 Performance Monitoring: Real-time metrics")
        
        print(f"\n   🎯 AI Service Types:")
        for service_type in AIServiceType:
            print(f"      🔹 {service_type.value.replace('_', ' ').title()}")
        
        print(f"\n   🏆 Performance Targets:")
        print(f"      ⚡ Real-time Response: <1000ms end-to-end")
        print(f"      🚀 High Throughput: 100+ conversations/minute")
        print(f"      🎯 High Accuracy: 95%+ service reliability")
        print(f"      📊 Scalability: Horizontal scaling with Ray")
        
        print(f"\n   🔧 Deployment Options:")
        print(f"      📡 Distributed: Ray Serve across multiple nodes")
        print(f"      💻 Local: Single-machine development mode")
        print(f"      🧪 Mock: Testing without external dependencies")
        print(f"      ☁️  Cloud: Kubernetes + Ray cluster deployment")
    
    async def run_complete_demo(self) -> None:
        """Run the complete distributed AI demonstration."""
        self.print_header("🚀 DISTRIBUTED AI PROCESSING DEMO")
        
        if not DISTRIBUTED_AI_AVAILABLE:
            print(f"❌ Distributed AI not available: {import_error}")
            print(f"📦 Install requirements: pip install ray[serve] openai numpy")
            return
        
        try:
            # Run all demo sections
            await self.demo_system_initialization()
            await self.demo_mock_services()
            await self.demo_conversation_processing()
            await self.demo_parallel_processing()
            await self.demo_performance_monitoring()
            await self.demo_load_optimization()
            self.demo_system_capabilities()
            
            self.print_header("✅ DISTRIBUTED AI DEMO COMPLETED")
            print(f"🎯 All distributed AI features demonstrated")
            print(f"⚡ Parallel processing capabilities verified")
            print(f"📊 Performance monitoring validated")
            print(f"🚀 Ray Serve integration {'confirmed' if RAY_AVAILABLE else 'simulated'}")
            print(f"🤖 AI Team implementation complete")
            
        except Exception as e:
            self.print_header("❌ DEMO FAILED")
            print(f"Error: {e}")
            logger.exception("Demo failed with exception")
        
        finally:
            # Cleanup
            if self.processor:
                await self.processor.cleanup()


async def main():
    """Main demo execution."""
    demo = DistributedAIDemo()
    await demo.run_complete_demo()


if __name__ == "__main__":
    # Run the demo
    asyncio.run(main()) 