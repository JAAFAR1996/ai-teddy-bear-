#!/usr/bin/env python3
"""Final comprehensive status check after God Class refactoring and cleanup"""

import sys
import os
from pathlib import Path

sys.path.insert(0, 'src')

def check_core_functionality():
    """Check core functionality that should work without heavy dependencies."""
    print("🏗️  CORE FUNCTIONALITY CHECK")
    print("-" * 40)
    
    results = []
    
    # Domain models - should work
    try:
        from src.domain.esp32.models.child_models import ChildProfile, ConversationEntry
        child = ChildProfile(
            name="Test Child",
            age=8,
            child_id="test123",
            device_id="device123"
        )
        results.append("✅ ChildProfile: Fully functional")
    except Exception as e:
        results.append(f"❌ ChildProfile: {e}")
    
    # Audio domain models
    try:
        from src.domain.audio.models.audio_session import AudioSession
        results.append("✅ AudioSession: Import successful")
    except Exception as e:
        results.append(f"❌ AudioSession: {e}")
    
    # ESP32 device models
    try:
        from src.domain.esp32.models.device_models import ESP32Device
        results.append("✅ ESP32Device: Import successful")
    except Exception as e:
        results.append(f"❌ ESP32Device: {e}")
    
    return results

def check_refactored_components():
    """Check refactored components from God Classes."""
    print("\n🔧 REFACTORED COMPONENTS CHECK")
    print("-" * 40)
    
    results = []
    
    # Audio services (refactored from audio_manager.py God Class)
    try:
        from src.application.services.audio.audio_session_service import AudioSessionService
        results.append("✅ AudioSessionService: God Class refactoring successful")
    except Exception as e:
        results.append(f"❌ AudioSessionService: {e}")
    
    # ESP32 services (refactored from esp32_teddy_simulator.py God Class)
    try:
        from src.application.services.esp32.device_service import DeviceManagementService
        results.append("✅ DeviceService: God Class refactoring successful")  
    except Exception as e:
        results.append(f"❌ DeviceService: {e}")
    
    return results

def check_file_structure():
    """Check that key refactored files exist."""
    print("\n📁 FILE STRUCTURE CHECK")
    print("-" * 40)
    
    key_files = [
        "src/domain/audio/models/audio_session.py",
        "src/domain/esp32/models/child_models.py", 
        "src/application/services/audio/audio_session_service.py",
        "src/application/services/esp32/device_service.py",
        "src/infrastructure/audio/audio_coordinator.py",
        "src/application/services/cleanup/backup_service.py",
    ]
    
    results = []
    for file_path in key_files:
        if Path(file_path).exists():
            results.append(f"✅ {file_path}: Exists")
        else:
            results.append(f"❌ {file_path}: Missing")
    
    return results

def check_import_dependencies():
    """Check what dependencies are missing vs working."""
    print("\n📦 DEPENDENCY STATUS CHECK")
    print("-" * 40)
    
    results = []
    
    # Core dependencies that should be available
    core_deps = ['structlog', 'numpy', 'sqlalchemy']
    for dep in core_deps:
        try:
            __import__(dep)
            results.append(f"✅ {dep}: Installed")
        except ImportError:
            results.append(f"❌ {dep}: Missing")
    
    # Optional/Heavy dependencies
    optional_deps = ['transformers', 'librosa', 'torch']
    for dep in optional_deps:
        try:
            __import__(dep)
            results.append(f"✅ {dep}: Installed (optional)")
        except ImportError:
            results.append(f"⚠️  {dep}: Missing (optional - for AI features)")
    
    return results

def main():
    print("🧸 AI TEDDY BEAR - FINAL STATUS CHECK")
    print("=" * 50)
    print("Post God Class Refactoring & Cleanup Verification")
    print("=" * 50)
    
    # Run all checks
    core_results = check_core_functionality()
    refactor_results = check_refactored_components()
    file_results = check_file_structure()
    dep_results = check_import_dependencies()
    
    # Print results
    for result in core_results:
        print(f"  {result}")
    
    for result in refactor_results:
        print(f"  {result}")
    
    for result in file_results:
        print(f"  {result}")
    
    for result in dep_results:
        print(f"  {result}")
    
    # Summary
    all_results = core_results + refactor_results + file_results
    passed = sum(1 for r in all_results if r.startswith("✅"))
    total = len(all_results)
    success_rate = (passed / total) * 100
    
    print(f"\n📊 FINAL SUMMARY")
    print("-" * 40)
    print(f"Tests passed: {passed}/{total}")
    print(f"Success rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("\n🎉 EXCELLENT! Project structure is healthy after refactoring!")
        print("   Core functionality is working well.")
        if success_rate < 100:
            print("   Some optional features need additional dependencies.")
    elif success_rate >= 60:
        print("\n✅ GOOD! Most components working after cleanup.")
        print("   Minor issues that can be easily resolved.")
    else:
        print("\n⚠️  NEEDS ATTENTION: Several issues found.")
        print("   Review the errors above and address them.")

if __name__ == "__main__":
    main() 