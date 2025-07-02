"""
🧪 Too Many Arguments Fix Verification Test
Tests the synthesis_service.py refactoring for parameter reduction using INTRODUCE PARAMETER OBJECT
"""

import asyncio
import pytest
import sys
import os
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any, Optional

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    # Import the refactored service
    from src.application.services.core.synthesis_service import (
        ModernSynthesisService,
        SynthesisConfig,
        SynthesisServiceCredentials,
        VoiceProvider,
        create_synthesis_service,
        create_synthesis_service_legacy
    )
    from src.domain.value_objects import EmotionalTone
    print("✅ All imports successful!")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    exit(1)

# ================== TEST CONFIGURATION ==================

class TestTooManyArgumentsFix:
    """Test Too Many Arguments refactoring results"""
    
    @pytest.fixture
    def sample_credentials(self):
        """Create sample credentials for testing"""
        return SynthesisServiceCredentials(
            elevenlabs_api_key="test_elevenlabs_key",
            openai_api_key="test_openai_key",
            azure_speech_key="test_azure_key",
            azure_speech_region="eastus"
        )
    
    @pytest.fixture
    def sample_config(self):
        """Create sample config for testing"""
        return SynthesisConfig(
            sample_rate=22050,
            chunk_size=512,
            streaming_enabled=True
        )
    
    # ================== PARAMETER OBJECT TESTS ==================
    
    def test_synthesis_service_credentials_creation(self, sample_credentials):
        """Test SynthesisServiceCredentials parameter object"""
        
        # Test creation
        assert sample_credentials.elevenlabs_api_key == "test_elevenlabs_key"
        assert sample_credentials.openai_api_key == "test_openai_key"
        assert sample_credentials.azure_speech_key == "test_azure_key"
        assert sample_credentials.azure_speech_region == "eastus"
    
    def test_credentials_validation_methods(self, sample_credentials):
        """Test credential validation helper methods"""
        
        # Test has methods
        assert sample_credentials.has_elevenlabs() == True
        assert sample_credentials.has_openai() == True
        assert sample_credentials.has_azure() == True
        
        # Test with empty credentials
        empty_credentials = SynthesisServiceCredentials()
        assert empty_credentials.has_elevenlabs() == False
        assert empty_credentials.has_openai() == False
        assert empty_credentials.has_azure() == False
    
    def test_get_available_providers(self, sample_credentials):
        """Test available providers detection"""
        
        providers = sample_credentials.get_available_providers()
        
        # Should include all providers when keys are available
        expected_providers = [
            VoiceProvider.ELEVENLABS,
            VoiceProvider.OPENAI,
            VoiceProvider.AZURE,
            VoiceProvider.SYSTEM
        ]
        
        for provider in expected_providers:
            assert provider in providers
    
    def test_partial_credentials(self):
        """Test credentials with only some providers"""
        
        partial_credentials = SynthesisServiceCredentials(
            openai_api_key="test_openai_key"
        )
        
        assert partial_credentials.has_elevenlabs() == False
        assert partial_credentials.has_openai() == True
        assert partial_credentials.has_azure() == False
        
        providers = partial_credentials.get_available_providers()
        assert VoiceProvider.OPENAI in providers
        assert VoiceProvider.SYSTEM in providers
        assert VoiceProvider.ELEVENLABS not in providers
        assert VoiceProvider.AZURE not in providers
    
    # ================== FACTORY FUNCTION TESTS ==================
    
    @pytest.mark.asyncio
    async def test_create_synthesis_service_new_interface(self, sample_config, sample_credentials):
        """Test new create_synthesis_service with reduced arguments"""
        
        # Mock the initialization
        with patch.object(ModernSynthesisService, 'initialize', new_callable=AsyncMock) as mock_init:
            # Test with both parameters
            service = await create_synthesis_service(
                config=sample_config,
                credentials=sample_credentials
            )
            
            # Verify service created
            assert isinstance(service, ModernSynthesisService)
            
            # Verify initialize called with credentials
            mock_init.assert_called_once_with(credentials=sample_credentials)
    
    @pytest.mark.asyncio
    async def test_create_synthesis_service_minimal_args(self):
        """Test new interface with minimal arguments"""
        
        with patch.object(ModernSynthesisService, 'initialize', new_callable=AsyncMock) as mock_init:
            # Test with no parameters (should use defaults)
            service = await create_synthesis_service()
            
            assert isinstance(service, ModernSynthesisService)
            mock_init.assert_called_once_with(credentials=None)
    
    @pytest.mark.asyncio
    async def test_create_synthesis_service_legacy_compatibility(self, sample_config):
        """Test legacy function maintains backward compatibility"""
        
        with patch.object(ModernSynthesisService, 'initialize', new_callable=AsyncMock) as mock_init:
            # Test legacy function with individual parameters
            service = await create_synthesis_service_legacy(
                config=sample_config,
                elevenlabs_api_key="test_eleven",
                openai_api_key="test_openai",
                azure_speech_key="test_azure",
                azure_speech_region="westus"
            )
            
            assert isinstance(service, ModernSynthesisService)
            
            # Verify initialize called with proper credentials object
            mock_init.assert_called_once()
            called_credentials = mock_init.call_args[1]['credentials']
            
            assert called_credentials.elevenlabs_api_key == "test_eleven"
            assert called_credentials.openai_api_key == "test_openai"
            assert called_credentials.azure_speech_key == "test_azure"
            assert called_credentials.azure_speech_region == "westus"
    
    # ================== INITIALIZE METHOD TESTS ==================
    
    @pytest.mark.asyncio
    async def test_initialize_with_credentials_object(self, sample_credentials):
        """Test ModernSynthesisService.initialize with credentials object"""
        
        service = ModernSynthesisService()
        
        # Mock the external dependencies
        with patch('src.application.services.core.synthesis_service.ElevenLabs') as mock_eleven, \
             patch('src.application.services.core.synthesis_service.AsyncOpenAI') as mock_openai, \
             patch('src.application.services.core.synthesis_service.speechsdk') as mock_azure:
            
            # Mock the _load_default_characters method
            service._load_default_characters = AsyncMock()
            
            await service.initialize(credentials=sample_credentials)
            
            # Verify all clients were initialized
            mock_eleven.assert_called_once_with(api_key="test_elevenlabs_key")
            mock_openai.assert_called_once_with(api_key="test_openai_key")
            mock_azure.SpeechConfig.assert_called_once_with(
                subscription="test_azure_key",
                region="eastus"
            )
    
    @pytest.mark.asyncio
    async def test_initialize_with_no_credentials(self):
        """Test initialize with None credentials (should use defaults)"""
        
        service = ModernSynthesisService()
        service._load_default_characters = AsyncMock()
        
        # Should not raise exception
        await service.initialize(credentials=None)
        
        # Should call _load_default_characters
        service._load_default_characters.assert_called_once()
    
    # ================== ARGUMENT COUNT VERIFICATION ==================
    
    def test_argument_count_reduction(self):
        """Verify that argument count was reduced from 5 to 2"""
        
        import inspect
        
        # Check new function signature
        sig_new = inspect.signature(create_synthesis_service)
        new_params = list(sig_new.parameters.keys())
        
        # Should have exactly 2 parameters: config and credentials
        assert len(new_params) == 2
        assert 'config' in new_params
        assert 'credentials' in new_params
        
        print(f"✅ New function has {len(new_params)} arguments (down from 5)")
        print(f"   Parameters: {new_params}")
        
        # Check legacy function signature (should maintain 5 parameters)
        sig_legacy = inspect.signature(create_synthesis_service_legacy)
        legacy_params = list(sig_legacy.parameters.keys())
        
        assert len(legacy_params) == 5
        print(f"✅ Legacy function maintains {len(legacy_params)} arguments for compatibility")
    
    # ================== INTEGRATION TESTS ==================
    
    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self, sample_config, sample_credentials):
        """Test complete workflow with new parameter object approach"""
        
        # Mock all external dependencies
        with patch('src.application.services.core.synthesis_service.ElevenLabs'), \
             patch('src.application.services.core.synthesis_service.AsyncOpenAI'), \
             patch('src.application.services.core.synthesis_service.speechsdk'):
            
            # Create service using new interface
            service = await create_synthesis_service(
                config=sample_config,
                credentials=sample_credentials
            )
            
            # Verify service is functional
            assert isinstance(service, ModernSynthesisService)
            assert service.config == sample_config
            
            # Test that service has the expected attributes
            assert hasattr(service, 'elevenlabs_client')
            assert hasattr(service, 'openai_client')
            assert hasattr(service, 'azure_speech_config')
    
    def test_parameter_object_benefits(self):
        """Test benefits of parameter object pattern"""
        
        # Test 1: Easy to extend with new provider
        extended_credentials = SynthesisServiceCredentials(
            elevenlabs_api_key="test_key",
            openai_api_key="test_key",
            azure_speech_key="test_key",
            azure_speech_region="eastus"
            # Easy to add new provider keys here without changing function signature
        )
        
        assert extended_credentials.has_elevenlabs()
        assert extended_credentials.has_openai()
        assert extended_credentials.has_azure()
        
        # Test 2: Clear grouping of related parameters
        assert hasattr(extended_credentials, 'elevenlabs_api_key')
        assert hasattr(extended_credentials, 'openai_api_key')
        assert hasattr(extended_credentials, 'azure_speech_key')
        assert hasattr(extended_credentials, 'azure_speech_region')
        
        # Test 3: Built-in validation methods
        assert callable(extended_credentials.has_elevenlabs)
        assert callable(extended_credentials.has_openai)
        assert callable(extended_credentials.has_azure)
        assert callable(extended_credentials.get_available_providers)

# ================== COMPLEXITY ANALYSIS ==================

def analyze_argument_reduction():
    """
    📊 Argument Reduction Analysis Report
    
    BEFORE REFACTORING:
    - create_synthesis_service: 5 arguments (Exceeds threshold of 4)
    
    AFTER REFACTORING:
    - create_synthesis_service: 2 arguments (Below threshold)
    - create_synthesis_service_legacy: 5 arguments (Backward compatibility)
    """
    
    print("🎯 TOO MANY ARGUMENTS FIX ANALYSIS")
    print("=" * 50)
    
    improvements = {
        "create_synthesis_service": {
            "before": 5,
            "after": 2,
            "improvement": "60% reduction"
        },
        "parameter_cohesion": {
            "before": "Low - unrelated parameters mixed",
            "after": "High - logically grouped in parameter objects"
        },
        "extensibility": {
            "before": "Poor - requires function signature changes",
            "after": "Excellent - add new fields to parameter object"
        }
    }
    
    for aspect, stats in improvements.items():
        print(f"📈 {aspect}:")
        if isinstance(stats, dict) and 'before' in stats:
            print(f"   Before: {stats['before']}")
            print(f"   After:  {stats['after']}")
            if 'improvement' in stats:
                print(f"   Improvement: {stats['improvement']}")
        else:
            print(f"   {stats}")
        print()
    
    print("✅ REFACTORING BENEFITS:")
    print("- Reduced argument count below threshold (≤4)")
    print("- Applied INTRODUCE PARAMETER OBJECT pattern")
    print("- Improved parameter cohesion and logical grouping")
    print("- Enhanced extensibility for future providers")
    print("- Maintained backward compatibility")
    print("- Added built-in validation methods")

# ================== MAIN TEST RUNNER ==================

async def run_too_many_arguments_tests():
    """Run all Too Many Arguments fix tests"""
    
    print("🧪 Running Too Many Arguments Fix Tests...")
    print("=" * 50)
    
    # Initialize test
    test_instance = TestTooManyArgumentsFix()
    
    try:
        # Create fixtures
        sample_credentials = test_instance.sample_credentials()
        sample_config = test_instance.sample_config()
        
        # Run tests
        test_instance.test_synthesis_service_credentials_creation(sample_credentials)
        test_instance.test_credentials_validation_methods(sample_credentials)
        test_instance.test_get_available_providers(sample_credentials)
        test_instance.test_partial_credentials()
        
        await test_instance.test_create_synthesis_service_new_interface(sample_config, sample_credentials)
        await test_instance.test_create_synthesis_service_minimal_args()
        await test_instance.test_create_synthesis_service_legacy_compatibility(sample_config)
        
        await test_instance.test_initialize_with_credentials_object(sample_credentials)
        await test_instance.test_initialize_with_no_credentials()
        
        test_instance.test_argument_count_reduction()
        await test_instance.test_end_to_end_workflow(sample_config, sample_credentials)
        test_instance.test_parameter_object_benefits()
        
        print("✅ ALL TESTS PASSED!")
        print("🎯 Too Many Arguments refactoring successful!")
        
        # Show analysis
        analyze_argument_reduction()
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(run_too_many_arguments_tests())
    if success:
        print("\n🎉 TOO MANY ARGUMENTS FIX COMPLETED SUCCESSFULLY!")
        print("synthesis_service.py now has optimal parameter count")
    else:
        print("\n💥 TESTS FAILED - Please check the implementation") 