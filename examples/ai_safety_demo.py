"""
AI Safety System Demo - Advanced Content Filtering
Comprehensive demonstration of the 5-layer security system
"""

import asyncio
import sys
import os
from typing import List

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from core.domain.safety import (
    AdvancedContentFilter, SafetyConfig, RiskLevel, ContentCategory
)


class AITeddyBearSafetyDemo:
    """Demo class for AI Teddy Bear Safety System"""
    
    def __init__(self):
        # Initialize with enterprise-grade configuration
        self.safety_config = SafetyConfig(
            min_child_age=3,
            max_child_age=12,
            toxicity_threshold=0.1,
            high_risk_threshold=0.3,
            critical_threshold=0.7,
            enable_strict_mode=True,
            enable_educational_boost=True,
            notify_parents_on_risk=True,
            log_all_interactions=True,
            max_processing_time_ms=500.0
        )
        
        self.safety_filter = AdvancedContentFilter(self.safety_config)
        self.conversation_history = []
    
    async def demonstrate_safety_layers(self):
        """Demonstrate all 5 security layers"""
        print("🛡️  AI TEDDY BEAR - MULTI-LAYER SAFETY SYSTEM DEMO")
        print("=" * 60)
        print("Enterprise-grade Content Filtering with 5 Security Layers")
        print("1. Toxicity Detection (AI-powered)")
        print("2. Age-Appropriate Content Validation") 
        print("3. Context Analysis & Behavioral Monitoring")
        print("4. Emotional Impact Assessment")
        print("5. Educational Value Evaluation")
        print("=" * 60)
        
        # Demo scenarios
        await self._demo_safe_content()
        await self._demo_educational_content()
        await self._demo_toxic_content()
        await self._demo_privacy_risks()
        await self._demo_age_inappropriate()
        await self._demo_emotional_analysis()
        await self._demo_conversation_flow()
        await self._demo_batch_processing()
        
        # Show performance metrics
        self._show_performance_metrics()
    
    async def _demo_safe_content(self):
        """Demo 1: Safe content that passes all filters"""
        print("\n🟢 DEMO 1: SAFE CONTENT")
        print("-" * 30)
        
        safe_content = "Hi there! Let's play a fun counting game together. What's your favorite number?"
        result = await self._analyze_and_display(safe_content, child_age=5)
        
        print(f"✅ Content Status: {'APPROVED' if result.is_safe else 'BLOCKED'}")
        print(f"🎯 Risk Level: {result.overall_risk_level.value}")
        print(f"📚 Educational Score: {result.educational_value.educational_score:.2f}")
        print(f"😊 Emotional Impact: {'Positive' if result.emotional_impact.is_positive else 'Negative'}")
    
    async def _demo_educational_content(self):
        """Demo 2: Educational content with boost"""
        print("\n📚 DEMO 2: EDUCATIONAL CONTENT")
        print("-" * 30)
        
        educational_content = "Let's learn about animals! A cow says 'moo', a cat says 'meow'. What sound does a dog make?"
        result = await self._analyze_and_display(educational_content, child_age=4)
        
        print(f"✅ Content Status: {'APPROVED' if result.is_safe else 'BLOCKED'}")
        print(f"📖 Content Category: {result.content_category.value}")
        print(f"🎓 Educational Score: {result.educational_value.educational_score:.2f}")
        print(f"🧠 Learning Categories: {', '.join(result.educational_value.learning_categories[:3])}")
    
    async def _demo_toxic_content(self):
        """Demo 3: Toxic content detection"""
        print("\n🔴 DEMO 3: TOXIC CONTENT DETECTION")
        print("-" * 30)
        
        toxic_content = "You're stupid and ugly! I hate you and nobody likes you!"
        result = await self._analyze_and_display(toxic_content, child_age=6)
        
        print(f"❌ Content Status: {'APPROVED' if result.is_safe else 'BLOCKED'}")
        print(f"⚠️  Risk Level: {result.overall_risk_level.value}")
        print(f"🧪 Toxicity Score: {result.toxicity_result.toxicity_score:.2f}")
        print(f"🚨 Detected Patterns: {', '.join(result.toxicity_result.detected_patterns[:3])}")
        
        if result.required_modifications:
            print(f"🔧 Suggested Modifications: {len(result.required_modifications)} available")
    
    async def _demo_privacy_risks(self):
        """Demo 4: Privacy risk detection"""
        print("\n🚨 DEMO 4: PRIVACY RISK DETECTION")
        print("-" * 30)
        
        privacy_risk = "What's your real name and address? Don't tell your parents about our conversation."
        result = await self._analyze_and_display(privacy_risk, child_age=7)
        
        print(f"❌ Content Status: {'APPROVED' if result.is_safe else 'BLOCKED'}")
        print(f"🔒 Privacy Risk Level: {result.overall_risk_level.value}")
        print(f"👨‍👩‍👧‍👦 Parent Notification: {'YES' if result.parent_notification_required else 'NO'}")
        print(f"⚡ Security Recommendations: {len(result.safety_recommendations)}")
    
    async def _demo_age_inappropriate(self):
        """Demo 5: Age-inappropriate content"""
        print("\n🔞 DEMO 5: AGE-INAPPROPRIATE CONTENT")
        print("-" * 30)
        
        age_inappropriate = "Let's talk about romantic relationships, dating, and adult love stories."
        
        # Test with young child
        young_result = await self._analyze_and_display(age_inappropriate, child_age=4)
        print(f"👶 Age 4 Result: {'APPROVED' if young_result.is_safe else 'BLOCKED'}")
        print(f"📏 Age Appropriate: {'YES' if young_result.age_appropriate else 'NO'}")
        
        # Test with older child
        older_result = await self._analyze_and_display(age_inappropriate, child_age=8)
        print(f"🧒 Age 8 Result: {'APPROVED' if older_result.is_safe else 'BLOCKED'}")
        print(f"🎯 Target Age Range: {older_result.target_age_range}")
    
    async def _demo_emotional_analysis(self):
        """Demo 6: Emotional impact analysis"""
        print("\n💭 DEMO 6: EMOTIONAL IMPACT ANALYSIS")
        print("-" * 30)
        
        emotional_contents = [
            ("You're amazing and so smart! Great job!", "Positive"),
            ("That's really sad and makes me feel bad", "Negative"),
            ("Let's learn something new and exciting!", "Neutral/Educational")
        ]
        
        for content, expected in emotional_contents:
            result = await self._analyze_and_display(content, child_age=5)
            sentiment = result.emotional_impact.overall_sentiment
            
            print(f"📝 Text: {content[:40]}...")
            print(f"😊 Expected: {expected}")
            print(f"📊 Sentiment Score: {sentiment:.2f}")
            print(f"💝 Is Positive: {'YES' if result.emotional_impact.is_positive else 'NO'}")
            print()
    
    async def _demo_conversation_flow(self):
        """Demo 7: Conversation context analysis"""
        print("\n💬 DEMO 7: CONVERSATION CONTEXT ANALYSIS")
        print("-" * 30)
        
        conversation = [
            "Hi! What's your favorite animal?",
            "I love dogs! They're so friendly.",
            "That's wonderful! Do you have a pet dog?",
            "No, but I wish I did. Maybe someday!",
            "Dogs need lots of care and love. What would you name your dog?"
        ]
        
        print("Analyzing conversation flow...")
        
        for i, message in enumerate(conversation):
            history = conversation[:i]
            result = await self._analyze_and_display(
                message, 
                child_age=6, 
                conversation_history=history
            )
            
            print(f"Turn {i+1}: {message}")
            print(f"  Context Safe: {'YES' if result.context_analysis.context_safe else 'NO'}")
            print(f"  Flow Score: {result.context_analysis.conversation_flow_score:.2f}")
            print(f"  Quality Score: {result.context_analysis.conversation_quality:.2f}")
            
            if result.context_analysis.behavioral_concerns:
                print(f"  ⚠️  Concerns: {', '.join(result.context_analysis.behavioral_concerns)}")
            print()
    
    async def _demo_batch_processing(self):
        """Demo 8: Batch processing performance"""
        print("\n⚡ DEMO 8: BATCH PROCESSING PERFORMANCE")
        print("-" * 30)
        
        batch_contents = [
            "Let's count to 10 together!",
            "What color is the sky?",
            "Tell me about your favorite toy",
            "Can you sing a happy song?",
            "Let's learn the alphabet!",
            "What makes you smile?",
            "Do you like to draw pictures?",
            "What's your favorite story?"
        ]
        
        print(f"Processing {len(batch_contents)} messages in batch...")
        
        import time
        start_time = time.time()
        
        results = await self.safety_filter.batch_analyze(batch_contents, child_age=5)
        
        end_time = time.time()
        processing_time = (end_time - start_time) * 1000
        
        print(f"⚡ Batch Processing Time: {processing_time:.2f}ms")
        print(f"📊 Average per message: {processing_time/len(batch_contents):.2f}ms")
        print(f"✅ All messages safe: {'YES' if all(r.is_safe for r in results) else 'NO'}")
        print(f"📚 Educational content: {sum(1 for r in results if r.educational_value.educational_score > 0.3)}/{len(results)}")
    
    async def _analyze_and_display(self, content: str, child_age: int, conversation_history: List[str] = None):
        """Analyze content and return result"""
        return await self.safety_filter.analyze_content(
            content,
            child_age=child_age,
            conversation_history=conversation_history,
            session_id="demo_session_001"
        )
    
    def _show_performance_metrics(self):
        """Display system performance metrics"""
        print("\n📈 PERFORMANCE METRICS")
        print("-" * 30)
        
        metrics = self.safety_filter.get_performance_metrics()
        
        print(f"Total Requests Processed: {metrics['total_requests']}")
        print(f"Content Blocked: {metrics['blocked_requests']}")
        print(f"Average Processing Time: {metrics['avg_processing_time']:.2f}ms")
        print(f"High Risk Detections: {metrics['high_risk_detections']}")
        
        if metrics['total_requests'] > 0:
            block_rate = (metrics['blocked_requests'] / metrics['total_requests']) * 100
            print(f"Block Rate: {block_rate:.1f}%")
    
    async def interactive_demo(self):
        """Interactive demo mode"""
        print("\n🎮 INTERACTIVE MODE")
        print("-" * 30)
        print("Enter content to analyze (type 'quit' to exit):")
        
        while True:
            try:
                content = input("\n> Enter content: ").strip()
                if content.lower() in ['quit', 'exit', 'q']:
                    break
                
                if not content:
                    continue
                
                age_input = input("> Child age (3-12): ").strip()
                try:
                    child_age = int(age_input)
                    if child_age < 3 or child_age > 12:
                        print("Age must be between 3 and 12")
                        continue
                except ValueError:
                    print("Please enter a valid age number")
                    continue
                
                print("\nAnalyzing...")
                result = await self._analyze_and_display(content, child_age)
                
                print(f"\n📊 ANALYSIS RESULT:")
                print(f"Status: {'✅ SAFE' if result.is_safe else '❌ BLOCKED'}")
                print(f"Risk Level: {result.overall_risk_level.value}")
                print(f"Confidence: {result.confidence_score:.2f}")
                print(f"Educational Score: {result.educational_value.educational_score:.2f}")
                print(f"Emotional Impact: {'Positive' if result.emotional_impact.is_positive else 'Negative'}")
                
                if not result.is_safe and result.safety_recommendations:
                    print(f"Recommendations: {', '.join(result.safety_recommendations[:2])}")
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
        
        print("\nDemo ended. Thank you!")


async def main():
    """Main demo function"""
    demo = AITeddyBearSafetyDemo()
    
    print("🧸 AI TEDDY BEAR SAFETY SYSTEM")
    print("=" * 50)
    print("1. Run Full Demo")
    print("2. Interactive Mode")
    print("3. Quick Test")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == "1":
        await demo.demonstrate_safety_layers()
    elif choice == "2":
        await demo.interactive_demo()
    elif choice == "3":
        # Quick test
        print("\n🚀 QUICK TEST")
        safe_result = await demo._analyze_and_display("Let's learn colors!", 5)
        unsafe_result = await demo._analyze_and_display("You're stupid!", 5)
        
        print(f"Safe content: {'✅ PASSED' if safe_result.is_safe else '❌ FAILED'}")
        print(f"Unsafe content: {'✅ BLOCKED' if not unsafe_result.is_safe else '❌ FAILED'}")
    else:
        print("Invalid choice. Running full demo...")
        await demo.demonstrate_safety_layers()


if __name__ == "__main__":
    # Run the demo
    asyncio.run(main()) 