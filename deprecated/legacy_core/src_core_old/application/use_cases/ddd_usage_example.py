"""
🎯 DDD Usage Example - Practical Implementation
==============================================

This file demonstrates how to use the new Domain-Driven Design architecture
in real-world scenarios for the AI Teddy Bear system.
"""

from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from ..domain.aggregates.child_aggregate import Child, SafetyViolation, ConversationLimitExceeded
from ..domain.value_objects import (
    ChildId, ParentId, DeviceId, VoiceProfile, SafetySettings,
    VoiceGender, EmotionBaseline, ContentFilterLevel
)
from ..domain.entities import Conversation, ConversationStatus, MessageType, EmotionDetection
from ..domain.services import ChildDomainService, ConversationCompatibilityResult
from ..domain.events import ChildRegistered, ConversationStarted, SafetyViolationDetected


class DDDUsageExamples:
    """
    Practical examples showing how to use the new DDD architecture
    for common AI Teddy Bear operations.
    """
    
    def __init__(self):
        self.child_service = ChildDomainService()

    def example_1_register_new_child(self) -> Child:
        """
        Example 1: Register a new child with complete DDD patterns
        """
        
        print("🎯 Example 1: Registering New Child with DDD")
        print("=" * 50)
        
        # Create value objects with proper validation
        parent_id = ParentId(uuid4())
        device_id = DeviceId(uuid4())
        
        try:
            # Use aggregate factory method with business rules
            child = Child.register_new_child(
                name="Emma Thompson",
                age=7,
                udid="ESP32-TEDDY-001",
                parent_id=parent_id,
                device_id=device_id
            )
            
            print(f"✅ Child registered successfully: {child}")
            print(f"   Voice Profile: {child.voice_profile}")
            print(f"   Safety Settings: {child.safety_settings}")
            
            # Handle domain events
            events = child.clear_events()
            for event in events:
                if isinstance(event, ChildRegistered):
                    print(f"📧 Event: Child registered at {event.registered_at}")
            
            return child
            
        except ValueError as e:
            print(f"❌ Registration failed: {e}")
            return None

    def example_2_start_conversation_with_safety_check(self, child: Child) -> Optional[Conversation]:
        """
        Example 2: Start conversation with comprehensive safety checks
        """
        
        print("\n🎯 Example 2: Starting Conversation with Safety Checks")
        print("=" * 55)
        
        # Check conversation compatibility using domain service
        compatibility = self.child_service.assess_conversation_compatibility(
            child=child,
            proposed_topic="learning about dinosaurs",
            conversation_history=[]
        )
        
        print(f"🔍 Compatibility Score: {compatibility.compatibility_score:.2f}")
        print(f"   Recommendations: {compatibility.recommendations}")
        print(f"   Blocking Issues: {compatibility.blocking_issues}")
        
        if not compatibility.is_compatible:
            print("❌ Conversation blocked by safety rules")
            return None
        
        try:
            # Use aggregate method with business rules enforcement
            conversation = child.start_conversation("learning about dinosaurs")
            
            print(f"✅ Conversation started: {conversation}")
            print(f"   Status: {conversation.status}")
            print(f"   Max Duration: {conversation.max_duration_minutes} minutes")
            
            # Handle domain events
            events = child.clear_events()
            for event in events:
                if isinstance(event, ConversationStarted):
                    print(f"📧 Event: Conversation started at {event.started_at}")
            
            return conversation
            
        except (SafetyViolation, ConversationLimitExceeded) as e:
            print(f"❌ Conversation failed: {e}")
            return None

    def example_3_handle_child_message_with_emotion_detection(
        self, 
        child: Child, 
        conversation: Conversation
    ) -> None:
        """
        Example 3: Process child message with emotion detection and response
        """
        
        print("\n🎯 Example 3: Processing Child Message with Emotion Detection")
        print("=" * 60)
        
        # Simulate child message with emotion detection
        child_message = "I'm really excited about dinosaurs! Tell me about T-Rex!"
        detected_emotion = EmotionDetection.EXCITED
        emotion_confidence = 0.87
        
        try:
            # Add child message using entity method
            message = conversation.add_child_message(
                content=child_message,
                message_type=MessageType.CHILD_TEXT,
                emotion_detected=detected_emotion,
                emotion_confidence=emotion_confidence
            )
            
            print(f"💬 Child Message: \"{child_message}\"")
            print(f"😊 Emotion Detected: {detected_emotion.value} (confidence: {emotion_confidence})")
            
            # Track emotional state in aggregate
            child.track_emotional_state(
                emotion=detected_emotion.value,
                confidence=emotion_confidence,
                context="dinosaur conversation"
            )
            
            # Adjust voice profile based on emotion using value object method
            if child.voice_profile:
                adjusted_profile = child.voice_profile.adjust_for_emotion(
                    detected_emotion=detected_emotion.value,
                    intensity=emotion_confidence
                )
                
                print(f"🎵 Voice Adjusted: pitch={adjusted_profile.pitch:.2f}, speed={adjusted_profile.speed:.2f}")
            
            # Generate AI response
            ai_response = self._generate_ai_response(child, message, detected_emotion)
            
            # Add AI response to conversation
            response_message = conversation.add_ai_response(
                content=ai_response,
                processing_time_ms=850,
                metadata={"emotion_adjusted": True, "topic": "dinosaurs"}
            )
            
            print(f"🤖 AI Response: \"{ai_response}\"")
            print(f"⚡ Processing Time: {response_message.processing_time_ms}ms")
            
        except Exception as e:
            print(f"❌ Message processing failed: {e}")

    def example_4_safety_assessment_and_violation_handling(self, child: Child) -> None:
        """
        Example 4: Comprehensive safety assessment and violation handling
        """
        
        print("\n🎯 Example 4: Safety Assessment and Violation Handling")
        print("=" * 55)
        
        # Conduct comprehensive safety assessment using domain service
        safety_assessment = self.child_service.conduct_comprehensive_safety_assessment(
            child=child,
            recent_conversations=[],
            parent_feedback={"recent_review": True, "feedback_provided": True}
        )
        
        print(f"🛡️ Overall Safety Score: {safety_assessment.overall_safety_score:.2f}")
        print(f"   Risk Factors: {safety_assessment.risk_factors}")
        print(f"   Protective Factors: {safety_assessment.protective_factors}")
        print(f"   Recommendations: {safety_assessment.recommendations}")
        print(f"   Parent Review Required: {safety_assessment.requires_parent_review}")
        
        # Simulate safety violation
        if safety_assessment.overall_safety_score < 0.8:
            print("\n⚠️ Simulating Safety Violation...")
            
            # Report safety violation using aggregate method
            child.report_safety_violation(
                violation_type="inappropriate_topic_request",
                details="Child asked about violent content"
            )
            
            print(f"📊 Safety Violations Count: {child.safety_violations_count}")
            
            # Handle domain events
            events = child.clear_events()
            for event in events:
                if isinstance(event, SafetyViolationDetected):
                    print(f"🚨 Safety Event: {event.violation_type} - {event.details}")

    def example_5_voice_profile_optimization(self, child: Child) -> None:
        """
        Example 5: Voice profile optimization based on interaction patterns
        """
        
        print("\n🎯 Example 5: Voice Profile Optimization")
        print("=" * 45)
        
        # Get current voice profile
        current_profile = child.voice_profile
        print(f"🎤 Current Voice Profile: {current_profile}")
        
        # Get optimization recommendations using domain service
        optimized_profile = self.child_service.recommend_voice_profile_adjustments(
            child=child,
            recent_conversations=[]
        )
        
        if optimized_profile:
            print(f"✨ Recommended Optimization: {optimized_profile}")
            
            try:
                # Update voice profile using aggregate method with business rules
                child.update_voice_profile(optimized_profile)
                print("✅ Voice profile updated successfully")
                
            except Exception as e:
                print(f"❌ Voice profile update failed: {e}")
        else:
            print("ℹ️ No optimization needed - current profile is optimal")

    def example_6_usage_summary_and_limits(self, child: Child) -> None:
        """
        Example 6: Daily usage tracking and limit enforcement
        """
        
        print("\n🎯 Example 6: Usage Summary and Limit Enforcement")
        print("=" * 50)
        
        # Get daily usage summary using aggregate method
        usage_summary = child.get_daily_usage_summary()
        
        print("📊 Daily Usage Summary:")
        print(f"   Conversations Today: {usage_summary['conversations_today']}")
        print(f"   Minutes Used: {usage_summary['minutes_used']:.1f}")
        print(f"   Minutes Remaining: {usage_summary['minutes_remaining']:.1f}")
        print(f"   Active Conversations: {usage_summary['active_conversations']}")
        print(f"   Can Start New: {usage_summary['can_start_new']}")
        
        # Check if child can start conversation using aggregate method
        can_start = child.can_start_conversation()
        if can_start:
            print("✅ Child can start new conversation")
        else:
            print("❌ Child cannot start conversation (limits reached)")

    def example_7_aggregate_consistency_validation(self, child: Child) -> None:
        """
        Example 7: Validate aggregate consistency using domain service
        """
        
        print("\n🎯 Example 7: Aggregate Consistency Validation")
        print("=" * 50)
        
        # Validate aggregate consistency using domain service
        violations = self.child_service.validate_child_aggregate_consistency(child)
        
        if violations:
            print("❌ Consistency Violations Found:")
            for violation in violations:
                print(f"   - {violation}")
        else:
            print("✅ Aggregate is consistent and valid")

    def _generate_ai_response(
        self, 
        child: Child, 
        message, 
        emotion: EmotionDetection
    ) -> str:
        """Generate AI response based on child profile and emotion"""
        
        # This would integrate with actual AI service
        age = child.age
        emotion_value = emotion.value
        
        if emotion == EmotionDetection.EXCITED and "dinosaur" in message.content.lower():
            if age <= 6:
                return "Wow! T-Rex was a really big dinosaur with huge teeth! They lived a long, long time ago. Would you like to hear about other dinosaurs too?"
            else:
                return "T-Rex was amazing! It was one of the largest land predators ever, living about 68 million years ago. Did you know they had teeth as big as bananas?"
        
        return "That's really interesting! Tell me more about what you'd like to learn."

    def run_all_examples(self) -> None:
        """Run all DDD examples in sequence"""
        
        print("🚀 Running All DDD Architecture Examples")
        print("=" * 60)
        
        # Example 1: Register child
        child = self.example_1_register_new_child()
        if not child:
            return
        
        # Example 2: Start conversation
        conversation = self.example_2_start_conversation_with_safety_check(child)
        if not conversation:
            return
        
        # Example 3: Handle message
        self.example_3_handle_child_message_with_emotion_detection(child, conversation)
        
        # Example 4: Safety assessment
        self.example_4_safety_assessment_and_violation_handling(child)
        
        # Example 5: Voice optimization
        self.example_5_voice_profile_optimization(child)
        
        # Example 6: Usage summary
        self.example_6_usage_summary_and_limits(child)
        
        # Example 7: Consistency validation
        self.example_7_aggregate_consistency_validation(child)
        
        print("\n🎉 All DDD Examples Completed Successfully!")
        print("=" * 50)


# Example usage
if __name__ == "__main__":
    examples = DDDUsageExamples()
    examples.run_all_examples() 