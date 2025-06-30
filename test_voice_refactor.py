"""
Test Voice Interaction Refactoring
Quick test to verify all components work together
"""

import asyncio
import logging

# Test imports from new structure
try:
    # Domain imports
    from src.domain.audio.models import (
        EmotionalTone, Language, AudioConfig, VoiceProfile
    )
    from src.domain.audio.services import (
        VoiceActivityDetector, AudioProcessor
    )
    
    # Application service imports
    from src.application.services.audio.voice_synthesis_service import VoiceSynthesisService
    from src.application.services.audio.voice_recognition_service import VoiceRecognitionService
    from src.application.services.audio.voice_profile_service import VoiceProfileService
    
    # Infrastructure imports
    from src.infrastructure.audio.clients import (
        ElevenLabsClient, AzureSpeechClient, WhisperClient, OpenAISpeechClient
    )
    
    print("✅ All imports successful!")
    imports_success = True
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    imports_success = False


async def test_domain_models():
    """Test domain models functionality"""
    try:
        # Test AudioConfig
        config = AudioConfig()
        assert config.validate() == True
        
        # Test EmotionalTone enum
        emotion = EmotionalTone.HAPPY
        assert emotion.value == "happy"
        
        # Test Language enum
        lang = Language.ARABIC
        assert lang.value == "ar"
        
        print("✅ Domain models test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Domain models test failed: {e}")
        return False


async def test_domain_services():
    """Test domain services functionality"""
    try:
        config = AudioConfig()
        
        # Test VoiceActivityDetector
        vad = VoiceActivityDetector(config)
        assert vad is not None
        
        # Test AudioProcessor
        processor = AudioProcessor(config)
        assert processor is not None
        
        print("✅ Domain services test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Domain services test failed: {e}")
        return False


async def test_application_services():
    """Test application services functionality"""
    try:
        # Test VoiceProfileService
        profile_service = VoiceProfileService()
        assert profile_service is not None
        
        # Test default profiles creation
        profiles = await profile_service.create_default_profiles()
        assert len(profiles) > 0
        
        print("✅ Application services test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Application services test failed: {e}")
        return False


async def main():
    """Run all tests"""
    print("🧸 Voice Interaction Refactoring Test")
    print("=" * 50)
    
    results = []
    
    # Test imports
    results.append(imports_success)
    
    if imports_success:
        # Test domain models
        results.append(await test_domain_models())
        
        # Test domain services
        results.append(await test_domain_services())
        
        # Test application services
        results.append(await test_application_services())
    
    # Summary
    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 All tests passed! ({passed}/{total})")
        print("✅ Voice Interaction Service refactoring successful!")
        return True
    else:
        print(f"⚠️  Some tests failed: {passed}/{total}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1) 