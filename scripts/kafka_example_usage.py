#!/usr/bin/env python3
"""
🚀 Kafka Event Streaming - Complete Usage Example
=================================================

Comprehensive example showing the full Kafka event-driven architecture
for the AI Teddy Bear system integrated with DDD patterns.
"""

import asyncio
import logging
from datetime import datetime
from uuid import uuid4

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def main():
    """Main example demonstrating Kafka event streaming"""
    
    print("🚀 Starting AI Teddy Bear Kafka Event Streaming Example")
    print("=" * 60)
    
    try:
        # Import after path setup
        from src.infrastructure.messaging.event_bus_integration import (
            get_event_bus, get_event_dispatcher, EventDispatchContext
        )
        from src.domain.aggregates.child_aggregate import Child
        from src.domain.value_objects import ChildId, ParentId, DeviceId
        from src.domain.entities import EmotionDetection, MessageType
        
        # Initialize event system
        event_bus = get_event_bus()
        event_dispatcher = get_event_dispatcher()
        
        print("📡 Initializing Kafka Event System...")
        
        # Health check
        health = await event_bus.health_check()
        print(f"   Event Bus Status: {health['status']}")
        print(f"   Publisher: {health['publisher']['status']}")
        print(f"   Consumer: {health['consumer']['status']}")
        
        if health['status'] != 'healthy':
            print("❌ Event system not healthy. Please check Kafka connection.")
            return
        
        print("\n🎯 Example 1: Child Registration with Event Streaming")
        print("-" * 50)
        
        # Create new child (this will generate domain events)
        child = Child.register_new_child(
            name="Emma Thompson",
            age=7,
            udid="ESP32-TEDDY-001",
            parent_id=ParentId(uuid4()),
            device_id=DeviceId(uuid4())
        )
        
        print(f"✅ Child registered: {child.name} (age {child.age})")
        print(f"   Voice Profile: {child.voice_profile.complexity_level}/5 complexity")
        print(f"   Safety Settings: {child.safety_settings.content_filter_level.value} filtering")
        
        # Use context manager to automatically dispatch events
        async with EventDispatchContext(child):
            print("📧 Domain events will be dispatched automatically...")
        
        print("✅ Child registration events published to Kafka!")
        
        print("\n🎯 Example 2: Conversation Lifecycle with Events")
        print("-" * 50)
        
        # Start conversation
        conversation = child.start_conversation("learning about dinosaurs")
        print(f"💬 Started conversation: {conversation.title}")
        
        # Simulate child messages with emotion detection
        messages = [
            ("I want to learn about T-Rex!", EmotionDetection.EXCITED, 0.85),
            ("Are dinosaurs scary?", EmotionDetection.CONFUSED, 0.65),
            ("That's so cool!", EmotionDetection.HAPPY, 0.92)
        ]
        
        for content, emotion, confidence in messages:
            # Add child message
            message = conversation.add_child_message(
                content=content,
                message_type=MessageType.CHILD_TEXT,
                emotion_detected=emotion,
                emotion_confidence=confidence
            )
            
            print(f"👶 Child: \"{content}\" (emotion: {emotion.value}, confidence: {confidence})")
            
            # Simulate AI response
            ai_response = f"That's a great question about dinosaurs! {content.lower()} is very interesting."
            response_msg = conversation.add_ai_response(
                content=ai_response,
                processing_time_ms=750,
                metadata={"topic": "dinosaurs", "complexity": "age_7"}
            )
            
            print(f"🤖 AI: \"{ai_response[:50]}...\"")
            
            # Track emotional state
            child.track_emotional_state(
                emotion=emotion.value,
                confidence=confidence,
                context="dinosaur conversation"
            )
        
        # End conversation
        child.end_conversation(str(conversation.id), "Natural ending")
        print(f"✅ Conversation ended after {conversation.get_duration_minutes():.1f} minutes")
        
        # Dispatch all events from conversation
        async with EventDispatchContext(child, conversation):
            print("📧 Conversation events being dispatched...")
        
        print("✅ All conversation events published to Kafka!")
        
        print("\n🎯 Example 3: Safety Violation Handling")
        print("-" * 45)
        
        # Simulate safety violation
        child.report_safety_violation(
            violation_type="inappropriate_topic_request",
            details="Child asked about violent content"
        )
        
        print(f"⚠️  Safety violation reported for {child.name}")
        print(f"   Total violations: {child.safety_violations_count}")
        
        # Dispatch safety events
        async with EventDispatchContext(child):
            print("🚨 Safety violation events being dispatched...")
        
        print("✅ Safety events published to Kafka!")
        
        print("\n🎯 Example 4: Voice Profile Optimization")
        print("-" * 45)
        
        # Create domain service for voice optimization
        from src.domain.services import ChildDomainService
        child_service = ChildDomainService()
        
        # Get voice optimization recommendations
        optimized_profile = child_service.recommend_voice_profile_adjustments(
            child=child,
            recent_conversations=[conversation]
        )
        
        if optimized_profile:
            print("🎵 Voice profile optimization recommended:")
            print(f"   New pitch: {optimized_profile.pitch:.2f}")
            print(f"   New speed: {optimized_profile.speed:.2f}")
            print(f"   Emotion sensitivity: {optimized_profile.emotion_sensitivity:.2f}")
            
            # Update voice profile (generates events)
            try:
                child.update_voice_profile(optimized_profile)
                print("✅ Voice profile updated successfully")
            except Exception as e:
                print(f"❌ Voice profile update failed: {e}")
        else:
            print("ℹ️  No voice optimization needed")
        
        # Dispatch profile update events
        async with EventDispatchContext(child):
            print("🎵 Voice profile events being dispatched...")
        
        print("\n🎯 Example 5: Analytics and Metrics")
        print("-" * 40)
        
        # Get daily usage summary
        usage_summary = child.get_daily_usage_summary()
        print("📊 Daily Usage Summary:")
        print(f"   Conversations today: {usage_summary['conversations_today']}")
        print(f"   Minutes used: {usage_summary['minutes_used']:.1f}")
        print(f"   Minutes remaining: {usage_summary['minutes_remaining']:.1f}")
        print(f"   Can start new: {usage_summary['can_start_new']}")
        
        # Get event bus metrics
        metrics = event_bus.get_metrics()
        print("\n📈 Event Bus Metrics:")
        print(f"   Published events: {metrics['publisher_metrics']['events_published']}")
        print(f"   Failed events: {metrics['publisher_metrics']['events_failed']}")
        print(f"   Success rate: {metrics['publisher_metrics']['success_rate']:.2%}")
        print(f"   Average publish time: {metrics['publisher_metrics']['average_publish_time']:.3f}s")
        
        if 'consumer_metrics' in metrics:
            print(f"   Consumed events: {metrics['consumer_metrics']['events_consumed']}")
            print(f"   Processed events: {metrics['consumer_metrics']['events_processed']}")
            print(f"   Processing success rate: {metrics['consumer_metrics']['success_rate']:.2%}")
        
        print("\n🎯 Example 6: Safety Assessment")
        print("-" * 35)
        
        # Conduct comprehensive safety assessment
        safety_result = child_service.conduct_comprehensive_safety_assessment(
            child=child,
            recent_conversations=[conversation],
            parent_feedback={
                "recent_review": True,
                "feedback_provided": True,
                "settings_updated_recently": False
            }
        )
        
        print("🛡️  Safety Assessment Results:")
        print(f"   Overall score: {safety_result.overall_safety_score:.2f}/1.0")
        print(f"   Risk factors: {len(safety_result.risk_factors)}")
        for risk in safety_result.risk_factors:
            print(f"     - {risk}")
        print(f"   Protective factors: {len(safety_result.protective_factors)}")
        for protection in safety_result.protective_factors:
            print(f"     - {protection}")
        print(f"   Parent review required: {safety_result.requires_parent_review}")
        
        if safety_result.recommendations:
            print("   Recommendations:")
            for rec in safety_result.recommendations:
                print(f"     - {rec}")
        
        print("\n🎯 Example 7: Event Processing (Consumer Side)")
        print("-" * 45)
        
        # Start event processing in background
        print("🔄 Starting event consumer for 10 seconds...")
        
        # Create task for event processing
        consumer_task = asyncio.create_task(
            event_bus.start_event_processing()
        )
        
        # Let it run for a few seconds to process events
        await asyncio.sleep(10)
        
        # Stop event processing
        await event_bus.stop_event_processing(timeout=5)
        
        # Cancel the consumer task
        consumer_task.cancel()
        try:
            await consumer_task
        except asyncio.CancelledError:
            pass
        
        print("✅ Event processing demonstration completed")
        
        print("\n🎉 Complete Kafka Event Streaming Example Finished!")
        print("=" * 60)
        print("\nKey Features Demonstrated:")
        print("✅ Domain events automatically published to Kafka")
        print("✅ Event handlers processing events from Kafka")
        print("✅ Event-driven analytics and monitoring")
        print("✅ Safety violation handling and escalation")
        print("✅ Voice profile optimization based on usage")
        print("✅ Comprehensive safety assessments")
        print("✅ Real-time event processing")
        print("✅ Health checks and metrics")
        
        print("\n📊 Final System Health Check:")
        final_health = await event_bus.health_check()
        print(f"   Overall Status: {final_health['status']} ✅")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure you're running from the project root directory")
        print("and all dependencies are installed.")
    except Exception as e:
        logger.error(f"Example failed: {e}")
        print(f"\n❌ Example failed with error: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure Kafka is running: docker-compose -f docker-compose.kafka.yml up -d")
        print("2. Check network connectivity to Kafka (localhost:9092)")
        print("3. Verify all Python dependencies are installed")
        print("4. Check logs for detailed error information")


if __name__ == "__main__":
    # Run the complete example
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Example interrupted by user")
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        exit(1) 