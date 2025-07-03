#!/usr/bin/env python3
"""
🧪 Test imports for AI services modules
اختبار imports لوحدات خدمات AI
"""

import sys
import os

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

def test_imports():
    """Test all module imports"""
    print("🧪 Testing AI Services Module Imports...")
    
    try:
        # Test main factory
        from llm_service_factory import (
            LLMServiceFactory, 
            GenerationRequest,
            generate_simple
        )
        print("✅ Main factory imports work")
        
        # Test validation module
        from validation import LLMParameterValidationService, LLMParameterValidator
        print("✅ Validation module imports work")
        
        # Test caching module
        from caching import LLMResponseCache
        print("✅ Caching module imports work")
        
        # Test selection module  
        from selection import LLMModelSelector, ModelSelectionRequest
        print("✅ Selection module imports work")
        
        print("🎉 All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality"""
    print("\n🔧 Testing Basic Functionality...")
    
    try:
        # Test validation
        from validation import LLMParameterValidationService
        validator = LLMParameterValidationService()
        validator.validate_temperature_range(0.7)
        print("✅ Validation service works")
        
        # Test caching
        from caching import LLMResponseCache
        cache = LLMResponseCache()
        stats = cache.get_stats()
        print(f"✅ Caching service works: {stats}")
        
        # Test selection
        from selection import LLMModelSelector
        selector = LLMModelSelector()
        print("✅ Selection service works")
        
        print("🎉 All functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Functionality error: {e}")
        return False

if __name__ == "__main__":
    success = test_imports() and test_basic_functionality()
    if success:
        print("\n🎯 All tests passed! The module structure is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Check the module structure.")
    
    sys.exit(0 if success else 1) 