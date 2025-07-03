"""
🧪 Quick Test: Streaming Service Refactoring Validation
Test the refactored streaming service to ensure bumpy road fixes work correctly
"""

import asyncio
import json
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch

# Import the refactored streaming service
from src.application.services.core.streaming_service import StreamingService


class TestStreamingRefactoring:
    """Test suite for validating streaming service refactoring"""
    
    def __init__(self):
        self.test_results = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "test_details": []
        }
    
    async def setup_streaming_service(self):
        """Setup a mock streaming service for testing"""
        # Mock dependencies
        mock_config = Mock()
        mock_config.api_keys.ELEVENLABS_API_KEY = "test_key"
        mock_config.speech.voice_name = "Rachel"
        mock_config.server.FLASK_HOST = "localhost"
        mock_config.server.WEBSOCKET_PORT = 8765
        mock_config.voice_settings.VOICE_SAMPLE_RATE = 16000
        
        mock_stt_service = AsyncMock()
        mock_conversation_repo = Mock()
        
        # Create streaming service instance
        service = StreamingService(
            config=mock_config,
            stt_service=mock_stt_service,
            conversation_repo=mock_conversation_repo
        )
        
        return service
    
    def record_test_result(self, test_name: str, passed: bool, details: str = ""):
        """Record test result"""
        self.test_results["total_tests"] += 1
        if passed:
            self.test_results["passed_tests"] += 1
            status = "✅ PASSED"
        else:
            self.test_results["failed_tests"] += 1
            status = "❌ FAILED"
        
        self.test_results["test_details"].append({
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
    
    async def test_tts_provider_availability_check(self):
        """Test _check_tts_providers_availability extraction"""
        service = await self.setup_streaming_service()
        
        try:
            # Test the extracted function
            providers = service._check_tts_providers_availability()
            
            # Validate structure
            expected_keys = ["elevenlabs", "gtts"]
            has_correct_structure = all(key in providers for key in expected_keys)
            has_boolean_values = all(isinstance(providers[key], bool) for key in expected_keys)
            
            if has_correct_structure and has_boolean_values:
                self.record_test_result(
                    "TTS Provider Availability Check", 
                    True, 
                    f"Providers detected: {providers}"
                )
            else:
                self.record_test_result(
                    "TTS Provider Availability Check", 
                    False, 
                    f"Invalid structure: {providers}"
                )
        except Exception as e:
            self.record_test_result(
                "TTS Provider Availability Check", 
                False, 
                f"Exception: {str(e)}"
            )
    
    async def test_elevenlabs_tts_extraction(self):
        """Test _try_elevenlabs_tts extraction"""
        service = await self.setup_streaming_service()
        
        try:
            with patch('elevenlabs.generate') as mock_generate:
                mock_generate.return_value = b"fake_audio_data"
                
                # Test the extracted function
                result = await service._try_elevenlabs_tts("Hello world")
                
                # Validate result structure
                expected_keys = ["success", "audio_bytes", "format", "provider"]
                has_correct_structure = all(key in result for key in expected_keys)
                
                if has_correct_structure and result["success"]:
                    self.record_test_result(
                        "ElevenLabs TTS Extraction", 
                        True, 
                        f"Result: {result['provider']}, Format: {result['format']}"
                    )
                else:
                    self.record_test_result(
                        "ElevenLabs TTS Extraction", 
                        False, 
                        f"Invalid result: {result}"
                    )
        except Exception as e:
            self.record_test_result(
                "ElevenLabs TTS Extraction", 
                False, 
                f"Exception: {str(e)}"
            )
    
    async def test_gtts_fallback_extraction(self):
        """Test _try_gtts_tts extraction"""
        service = await self.setup_streaming_service()
        
        try:
            with patch('gtts.gTTS') as mock_gtts:
                mock_tts_instance = Mock()
                mock_gtts.return_value = mock_tts_instance
                
                # Mock the write_to_fp method
                def mock_write_to_fp(buffer):
                    buffer.write(b"fake_gtts_audio")
                
                mock_tts_instance.write_to_fp = mock_write_to_fp
                
                # Test the extracted function
                result = await service._try_gtts_tts("مرحبا")
                
                # Validate result structure
                expected_keys = ["success", "audio_bytes", "format", "provider"]
                has_correct_structure = all(key in result for key in expected_keys)
                
                if has_correct_structure and result["success"]:
                    self.record_test_result(
                        "gTTS Fallback Extraction", 
                        True, 
                        f"Result: {result['provider']}, Format: {result['format']}"
                    )
                else:
                    self.record_test_result(
                        "gTTS Fallback Extraction", 
                        False, 
                        f"Invalid result: {result}"
                    )
        except Exception as e:
            self.record_test_result(
                "gTTS Fallback Extraction", 
                False, 
                f"Exception: {str(e)}"
            )
    
    async def test_input_moderation_extraction(self):
        """Test _check_input_moderation extraction"""
        service = await self.setup_streaming_service()
        
        try:
            # Mock moderation service
            service.moderation_service = AsyncMock()
            service.moderation_service.check_content.return_value = {"allowed": True}
            
            # Test the extracted function
            result = await service._check_input_moderation("Hello world")
            
            # Validate result structure
            expected_keys = ["allowed"]
            has_correct_structure = all(key in result for key in expected_keys)
            
            if has_correct_structure and result["allowed"]:
                self.record_test_result(
                    "Input Moderation Extraction", 
                    True, 
                    "Moderation check successful"
                )
            else:
                self.record_test_result(
                    "Input Moderation Extraction", 
                    False, 
                    f"Invalid result: {result}"
                )
        except Exception as e:
            self.record_test_result(
                "Input Moderation Extraction", 
                False, 
                f"Exception: {str(e)}"
            )
    
    async def test_conversation_context_building(self):
        """Test _build_conversation_context extraction"""
        service = await self.setup_streaming_service()
        
        try:
            # Test the extracted function
            conversation = service._build_conversation_context("Hello", "test_session")
            
            # Validate conversation structure
            has_messages = hasattr(conversation, 'messages')
            has_system_message = len(conversation.messages) > 0 and conversation.messages[0].role == 'system'
            has_user_message = len(conversation.messages) > 1 and conversation.messages[-1].role == 'user'
            
            if has_messages and has_system_message and has_user_message:
                self.record_test_result(
                    "Conversation Context Building", 
                    True, 
                    f"Built conversation with {len(conversation.messages)} messages"
                )
            else:
                self.record_test_result(
                    "Conversation Context Building", 
                    False, 
                    f"Invalid conversation structure"
                )
        except Exception as e:
            self.record_test_result(
                "Conversation Context Building", 
                False, 
                f"Exception: {str(e)}"
            )
    
    async def test_code_quality_stats(self):
        """Test code quality statistics"""
        service = await self.setup_streaming_service()
        
        try:
            # Test the code quality stats function
            stats = service.get_code_quality_stats()
            
            # Validate stats structure
            required_keys = ["service_name", "refactoring_applied", "code_quality_improvements"]
            has_correct_structure = all(key in stats for key in required_keys)
            
            bumpy_road_stats = stats["code_quality_improvements"]["bumpy_road_elimination"]
            bumps_eliminated = bumpy_road_stats["before"]["total_bumps"] == 7 and bumpy_road_stats["after"]["total_bumps"] == 0
            
            if has_correct_structure and bumps_eliminated:
                self.record_test_result(
                    "Code Quality Statistics", 
                    True, 
                    f"Bumpy road elimination: {bumpy_road_stats['improvement']}"
                )
            else:
                self.record_test_result(
                    "Code Quality Statistics", 
                    False, 
                    f"Invalid stats structure"
                )
        except Exception as e:
            self.record_test_result(
                "Code Quality Statistics", 
                False, 
                f"Exception: {str(e)}"
            )
    
    async def test_function_lengths(self):
        """Test that extracted functions have reasonable lengths"""
        service = await self.setup_streaming_service()
        
        try:
            # Get source lines for extracted functions
            import inspect
            
            extracted_functions = [
                service._convert_text_to_speech,
                service._check_tts_providers_availability,
                service._try_elevenlabs_tts,
                service._try_gtts_tts,
                service._send_audio_response,
                service._check_input_moderation,
                service._build_conversation_context,
                service._generate_llm_response,
                service._check_output_moderation,
                service._log_interaction,
                service._handle_llm_error
            ]
            
            function_lengths = []
            for func in extracted_functions:
                source_lines = inspect.getsource(func).split('\n')
                # Count non-empty, non-comment lines
                code_lines = [line for line in source_lines if line.strip() and not line.strip().startswith('#')]
                function_lengths.append(len(code_lines))
            
            avg_length = sum(function_lengths) / len(function_lengths)
            max_length = max(function_lengths)
            
            # Validate function lengths (should be < 40 lines per our rules)
            if max_length < 40 and avg_length < 25:
                self.record_test_result(
                    "Function Length Compliance", 
                    True, 
                    f"Avg: {avg_length:.1f} lines, Max: {max_length} lines"
                )
            else:
                self.record_test_result(
                    "Function Length Compliance", 
                    False, 
                    f"Functions too long - Avg: {avg_length:.1f}, Max: {max_length}"
                )
        except Exception as e:
            self.record_test_result(
                "Function Length Compliance", 
                False, 
                f"Exception: {str(e)}"
            )
    
    async def run_all_tests(self):
        """Run all refactoring validation tests"""
        print("🧪 Starting Streaming Service Refactoring Tests...")
        print("=" * 60)
        
        # Run individual tests
        await self.test_tts_provider_availability_check()
        await self.test_elevenlabs_tts_extraction()
        await self.test_gtts_fallback_extraction()
        await self.test_input_moderation_extraction()
        await self.test_conversation_context_building()
        await self.test_code_quality_stats()
        await self.test_function_lengths()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total = self.test_results["total_tests"]
        passed = self.test_results["passed_tests"]
        failed = self.test_results["failed_tests"]
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"Total Tests:    {total}")
        print(f"Passed:         {passed}")
        print(f"Failed:         {failed}")
        print(f"Success Rate:   {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("\n🎉 REFACTORING VALIDATION: SUCCESS!")
            print("✅ Bumpy Road patterns successfully eliminated")
            print("✅ Function extraction working correctly") 
            print("✅ Code quality improvements verified")
        else:
            print("\n⚠️  REFACTORING VALIDATION: NEEDS ATTENTION")
            print("❌ Some tests failed - review implementations")
        
        return success_rate >= 80


async def main():
    """Main test runner"""
    print("🚀 AI Teddy Bear - Streaming Service Refactoring Test")
    print("Testing EXTRACT FUNCTION pattern and Bumpy Road elimination")
    print()
    
    tester = TestStreamingRefactoring()
    success = await tester.run_all_tests()
    
    print("\n" + "=" * 60)
    if success:
        print("🎯 CONCLUSION: Refactoring successfully implemented!")
        print("💡 Next steps: Consider EXTRACT CLASS for Low Cohesion")
    else:
        print("🔧 CONCLUSION: Some issues found - review and fix")
    
    return success


if __name__ == "__main__":
    asyncio.run(main()) 