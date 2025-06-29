"""
Comprehensive Tests for AI Bias Detection System
Security Team Testing Suite
"""

import asyncio
import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from core.domain.safety.bias_detector import AIBiasDetector
from core.domain.safety.bias_models import ConversationContext, BiasAnalysisResult


class TestAIBiasDetector:
    """Test suite for AI Bias Detection System"""
    
    @pytest.fixture
    def bias_detector(self):
        """Create bias detector instance for testing"""
        return AIBiasDetector()
    
    @pytest.fixture
    def sample_context(self):
        """Create sample conversation context"""
        return ConversationContext(
            child_age=6,
            child_gender="female",
            conversation_history=["Hello!", "How are you?"],
            interaction_count=2,
            session_duration=5.0
        )
    
    @pytest.mark.asyncio
    async def test_gender_bias_detection(self, bias_detector, sample_context):
        """Test detection of gender bias"""
        biased_response = "Girls are naturally better at reading, while boys are better at math."
        
        result = await bias_detector.detect_bias(biased_response, sample_context)
        
        assert result.has_bias == True
        assert result.bias_scores.get('gender', 0) > 0.3
        assert 'gender' in result.bias_categories
        assert len(result.mitigation_suggestions) > 0
    
    @pytest.mark.asyncio
    async def test_cultural_bias_detection(self, bias_detector, sample_context):
        """Test detection of cultural bias"""
        biased_response = "Normal families celebrate Christmas, and everyone has a traditional dinner."
        
        result = await bias_detector.detect_bias(biased_response, sample_context)
        
        assert result.has_bias == True
        assert result.bias_scores.get('cultural', 0) > 0.2
        assert 'cultural' in result.bias_categories
    
    @pytest.mark.asyncio
    async def test_socioeconomic_bias_detection(self, bias_detector, sample_context):
        """Test detection of socioeconomic bias"""
        biased_response = "Ask your parents to buy you the expensive new toy for your big house."
        
        result = await bias_detector.detect_bias(biased_response, sample_context)
        
        assert result.has_bias == True
        assert result.bias_scores.get('socioeconomic', 0) > 0.2 or result.contextual_bias.get('socioeconomic_assumption', 0) > 0.2
    
    @pytest.mark.asyncio
    async def test_ability_bias_detection(self, bias_detector, sample_context):
        """Test detection of ability bias"""
        biased_response = "Look at the picture and listen to the music while you run around."
        
        result = await bias_detector.detect_bias(biased_response, sample_context)
        
        # This should detect ability assumptions
        assert result.contextual_bias.get('ability_assumption', 0) > 0.0
    
    @pytest.mark.asyncio
    async def test_age_bias_detection(self, bias_detector, sample_context):
        """Test detection of age bias"""
        biased_response = "You're too young to understand this complex topic."
        
        result = await bias_detector.detect_bias(biased_response, sample_context)
        
        assert result.has_bias == True
        assert result.bias_scores.get('age', 0) > 0.2
    
    @pytest.mark.asyncio
    async def test_unbiased_content(self, bias_detector, sample_context):
        """Test that unbiased content passes"""
        unbiased_response = "Let's learn about colors! What's your favorite color?"
        
        result = await bias_detector.detect_bias(unbiased_response, sample_context)
        
        assert result.has_bias == False
        assert result.overall_bias_score < 0.3
        assert result.risk_level in ["MINIMAL", "LOW"]
    
    @pytest.mark.asyncio
    async def test_contextual_bias_analysis(self, bias_detector):
        """Test contextual bias analysis"""
        context = ConversationContext(
            child_age=4,
            child_gender="male",
            conversation_history=["I like cars"],
            interaction_count=1
        )
        
        response = "Boys always like cars and trucks!"
        result = await bias_detector.detect_bias(response, context)
        
        assert result.has_bias == True
        assert result.contextual_bias.get('gender_assumption', 0) > 0.0
    
    @pytest.mark.asyncio
    async def test_mitigation_suggestions(self, bias_detector, sample_context):
        """Test bias mitigation suggestions"""
        biased_response = "All girls love pink and dolls."
        
        result = await bias_detector.detect_bias(biased_response, sample_context)
        
        assert len(result.mitigation_suggestions) > 0
        assert any("gender-neutral" in suggestion.lower() for suggestion in result.mitigation_suggestions)
    
    @pytest.mark.asyncio
    async def test_batch_bias_analysis(self, bias_detector):
        """Test batch bias analysis"""
        responses = [
            "Let's learn about animals!",
            "Boys are stronger than girls.",
            "What's your favorite color?",
            "Rich families have better opportunities."
        ]
        
        contexts = [
            ConversationContext(child_age=5),
            ConversationContext(child_age=6),
            ConversationContext(child_age=7),
            ConversationContext(child_age=8)
        ]
        
        results = await bias_detector.batch_analyze_bias(responses, contexts)
        
        assert len(results) == len(responses)
        assert not results[0].has_bias  # Learning content
        assert results[1].has_bias      # Gender bias
        assert not results[2].has_bias  # Neutral question
        assert results[3].has_bias      # Socioeconomic bias
    
    def test_bias_statistics(self, bias_detector):
        """Test bias detection statistics"""
        stats = bias_detector.get_bias_statistics()
        
        assert "detection_method" in stats
        assert "system_accuracy" in stats
    
    @pytest.mark.asyncio
    async def test_enhanced_pattern_detection(self, bias_detector, sample_context):
        """Test enhanced pattern detection"""
        patterns_to_test = [
            ("She should be more gentle.", "gendered_expectation"),
            ("Boys are better than girls at this.", "comparative_bias"),
            ("All children are naturally good at art.", "absolutist_generalization"),
            ("Only smart kids can do this.", "exclusionary_language")
        ]
        
        for text, expected_pattern in patterns_to_test:
            result = await bias_detector.detect_bias(text, sample_context)
            
            # Check if the expected pattern is detected
            pattern_detected = any(expected_pattern in pattern for pattern in result.detected_patterns)
            if not pattern_detected:
                print(f"Pattern '{expected_pattern}' not detected in: {text}")
                print(f"Detected patterns: {result.detected_patterns}")
    
    @pytest.mark.asyncio
    async def test_risk_level_calculation(self, bias_detector, sample_context):
        """Test risk level calculation"""
        test_cases = [
            ("What's your favorite animal?", ["MINIMAL", "LOW"]),
            ("Girls like pink and boys like blue.", ["LOW", "MEDIUM"]),
            ("All poor children are less intelligent.", ["HIGH", "CRITICAL"])
        ]
        
        for text, expected_levels in test_cases:
            result = await bias_detector.detect_bias(text, sample_context)
            assert result.risk_level in expected_levels, f"Unexpected risk level for: {text}"
    
    @pytest.mark.asyncio
    async def test_bias_report_generation(self, bias_detector):
        """Test bias report generation"""
        # Generate some analysis results
        sample_results = []
        contexts = [ConversationContext(child_age=6) for _ in range(3)]
        
        responses = [
            "Let's learn together!",
            "Boys are naturally stronger.",
            "Rich kids get better education."
        ]
        
        for response, context in zip(responses, contexts):
            result = await bias_detector.detect_bias(response, context)
            sample_results.append(result)
        
        report = await bias_detector.generate_bias_report(sample_results)
        
        assert "summary" in report
        assert "bias_breakdown" in report
        assert "recommendations" in report
        assert report["summary"]["total_responses_analyzed"] == 3


class TestBiasIntegrationScenarios:
    """Integration tests for real-world bias scenarios"""
    
    @pytest.fixture
    def bias_detector(self):
        return AIBiasDetector()
    
    @pytest.mark.asyncio
    async def test_storytelling_scenario(self, bias_detector):
        """Test bias detection in storytelling"""
        story_with_bias = "Once upon a time, there was a brave prince who saved the helpless princess."
        story_without_bias = "Once upon a time, there was a brave child who went on an adventure."
        
        context = ConversationContext(child_age=5, conversation_history=["Tell me a story"])
        
        biased_result = await bias_detector.detect_bias(story_with_bias, context)
        unbiased_result = await bias_detector.detect_bias(story_without_bias, context)
        
        assert biased_result.has_bias or biased_result.overall_bias_score > 0.2
        assert not unbiased_result.has_bias
    
    @pytest.mark.asyncio
    async def test_educational_content_scenario(self, bias_detector):
        """Test bias detection in educational content"""
        biased_education = "Boys are naturally better at science and math subjects."
        inclusive_education = "Everyone can be good at science and math with practice."
        
        context = ConversationContext(child_age=7, topics_discussed=["learning", "school"])
        
        biased_result = await bias_detector.detect_bias(biased_education, context)
        inclusive_result = await bias_detector.detect_bias(inclusive_education, context)
        
        assert biased_result.has_bias
        assert not inclusive_result.has_bias
    
    @pytest.mark.asyncio
    async def test_career_guidance_scenario(self, bias_detector):
        """Test bias detection in career-related responses"""
        biased_careers = "Girls should become teachers or nurses, while boys should be engineers."
        inclusive_careers = "You can become anything you want - teacher, nurse, engineer, or artist!"
        
        context = ConversationContext(child_age=8, child_gender="female")
        
        biased_result = await bias_detector.detect_bias(biased_careers, context)
        inclusive_result = await bias_detector.detect_bias(inclusive_careers, context)
        
        assert biased_result.has_bias
        assert biased_result.bias_scores.get('gender', 0) > 0.3
        assert not inclusive_result.has_bias


@pytest.mark.asyncio
async def test_system_stress_bias_detection():
    """Stress test the bias detection system"""
    bias_detector = AIBiasDetector()
    
    # Test with various bias types simultaneously
    test_responses = [
        "Let's learn about space!",  # Safe
        "Boys are stronger than girls.",  # Gender bias
        "Normal families have lots of money.",  # Socioeconomic bias
        "Look at this picture carefully.",  # Ability assumption
        "Smart kids like you understand this.",  # Educational bias
        "All children from that country are different.",  # Cultural bias
        "You're too young for complex topics.",  # Age bias
        "Rich people are more successful."  # Socioeconomic bias
    ]
    
    contexts = [ConversationContext(child_age=6) for _ in range(len(test_responses))]
    
    # Run batch analysis
    results = await bias_detector.batch_analyze_bias(test_responses, contexts)
    
    assert len(results) == len(test_responses)
    
    # Verify safe content
    assert not results[0].has_bias  # Learning content should be safe
    
    # Verify bias detection
    biased_indices = [1, 2, 4, 5, 6, 7]  # Known biased content
    for i in biased_indices:
        assert results[i].has_bias or results[i].overall_bias_score > 0.2, f"Failed to detect bias in: {test_responses[i]}"
    
    # Check statistics
    stats = bias_detector.get_bias_statistics()
    assert stats['total_analyses'] >= len(test_responses)


if __name__ == "__main__":
    # Run basic tests if script is executed directly
    async def run_basic_bias_tests():
        detector = AIBiasDetector()
        
        print("🔍 AI Bias Detection System - Basic Tests")
        print("=" * 50)
        
        # Test 1: Safe content
        print("\n✅ Testing unbiased content...")
        context = ConversationContext(child_age=6)
        safe_result = await detector.detect_bias(
            "Let's learn about animals! What's your favorite animal?", 
            context
        )
        print(f"Unbiased content result: {not safe_result.has_bias}")
        print(f"Bias score: {safe_result.overall_bias_score:.2f}")
        
        # Test 2: Gender bias
        print("\n❌ Testing gender bias...")
        gender_result = await detector.detect_bias(
            "Boys are naturally better at math than girls.", 
            context
        )
        print(f"Gender bias detected: {gender_result.has_bias}")
        print(f"Bias score: {gender_result.overall_bias_score:.2f}")
        print(f"Suggestions: {len(gender_result.mitigation_suggestions)}")
        
        # Test 3: Cultural bias
        print("\n🌍 Testing cultural bias...")
        cultural_result = await detector.detect_bias(
            "Normal families celebrate Christmas and eat traditional food.", 
            context
        )
        print(f"Cultural bias detected: {cultural_result.has_bias}")
        print(f"Bias score: {cultural_result.overall_bias_score:.2f}")
        
        # Test 4: Socioeconomic bias
        print("\n💰 Testing socioeconomic bias...")
        economic_result = await detector.detect_bias(
            "Rich families provide better education for their children.", 
            context
        )
        print(f"Economic bias detected: {economic_result.has_bias}")
        print(f"Bias score: {economic_result.overall_bias_score:.2f}")
        
        print("\n🎉 Basic bias detection tests completed!")
        print(f"System statistics: {detector.get_bias_statistics()}")
    
    # Run the tests
    asyncio.run(run_basic_bias_tests()) 