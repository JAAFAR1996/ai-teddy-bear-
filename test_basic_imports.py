#!/usr/bin/env python3
"""
🧸 AI Teddy Bear - Basic Import Test
Testing essential project structure after God Class refactoring
"""

import sys
import os

# Add src to path
sys.path.insert(0, 'src')

def test_basic_imports():
    """Test basic project structure imports."""
    results = []
    
    # Test 1: Domain models
    try:
        from src.domain.esp32.models.child_models import ChildProfile, ConversationEntry
        results.append("✅ ESP32 child models: OK")
    except ImportError as e:
        results.append(f"❌ ESP32 child models: {e}")
    
    # Test 2: Audio domain models  
    try:
        from src.domain.audio.models.audio_session import AudioSession
        results.append("✅ Audio domain models: OK")
    except ImportError as e:
        results.append(f"❌ Audio domain models: {e}")
    
    # Test 3: Domain core
    try:
        from src.domain.entities.child import Child
        results.append("✅ Domain entities: OK")
    except ImportError as e:
        results.append(f"❌ Domain entities: {e}")
    
    return results

def test_refactored_components():
    """Test refactored God Class components."""
    results = []
    
    # Test cleanup services
    try:
        from src.application.services.cleanup.backup_service import BackupService
        results.append("✅ Cleanup services (refactored): OK")
    except ImportError as e:
        results.append(f"❌ Cleanup services: {e}")
    
    return results

if __name__ == "__main__":
    print("🧸 AI Teddy Bear - Post-Refactoring Import Test")
    print("=" * 50)
    
    print("\n📋 Testing Basic Imports:")
    basic_results = test_basic_imports()
    for result in basic_results:
        print(f"  {result}")
    
    print("\n🔧 Testing Refactored Components:")
    refactor_results = test_refactored_components()
    for result in refactor_results:
        print(f"  {result}")
    
    # Summary
    total_tests = len(basic_results) + len(refactor_results)
    passed_tests = sum(1 for r in basic_results + refactor_results if r.startswith("✅"))
    
    print(f"\n📊 Summary:")
    print(f"  Tests passed: {passed_tests}/{total_tests}")
    print(f"  Success rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 All tests passed! Project structure is healthy.")
    else:
        print(f"\n⚠️  {total_tests - passed_tests} issues found. See details above.") 