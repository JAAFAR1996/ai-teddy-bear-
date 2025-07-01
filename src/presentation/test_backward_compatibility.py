from typing import Any, Dict, List, Optional

#!/usr/bin/env python3
"""
Test Backward Compatibility for modern_ui.py
هذا الملف يختبر أن كل الاستيرادات القديمة لا تزال تعمل
"""

import sys
import traceback


def test_import(import_statement, expected_name) -> Any:
    """Test a single import statement"""
    try:
        exec(import_statement)
        print(f"✅ {import_statement}")
        return True
    except Exception as e:
        print(f"❌ {import_statement}")
        print(f"   Error: {e}")
        return False


def test_backward_compatibility() -> Any:
    """Test all backward compatibility imports"""
    print("🔍 Testing Backward Compatibility for modern_ui.py")
    print("=" * 60)

    failed_imports = []
    total_tests = 0

    # Test main components
    imports_to_test = [
        # Original classes
        ("from modern_ui import AudioProcessingEngine", "AudioProcessingEngine"),
        ("from modern_ui import WebSocketClient", "WebSocketClient"),
        ("from modern_ui import ModernAudioWidget", "ModernAudioWidget"),
        ("from modern_ui import TeddyMainWindow", "TeddyMainWindow"),
        ("from modern_ui import ConversationWidget", "ConversationWidget"),
        ("from modern_ui import WaveformWidget", "WaveformWidget"),
        # Legacy aliases
        ("from modern_ui import AudioWidget", "AudioWidget"),
        ("from modern_ui import MainWindow", "MainWindow"),
        ("from modern_ui import AudioEngine", "AudioEngine"),
        ("from modern_ui import WSClient", "WSClient"),
        # Utility functions
        ("from modern_ui import get_available_features", "get_available_features"),
        ("from modern_ui import check_feature_compatibility", "check_feature_compatibility"),
        # Flags
        ("from modern_ui import ENTERPRISE_DASHBOARD_AVAILABLE", "ENTERPRISE_DASHBOARD_AVAILABLE"),
        ("from modern_ui import PYSIDE6_AVAILABLE", "PYSIDE6_AVAILABLE"),
    ]

    print("\n📦 Testing Core Component Imports:")
    for import_stmt, name in imports_to_test:
        total_tests += 1
        if not test_import(import_stmt, name):
            failed_imports.append(import_stmt)

    # Test PySide6 re-exports
    pyside6_imports = [
        ("from modern_ui import QApplication", "QApplication"),
        ("from modern_ui import QPushButton", "QPushButton"),
        ("from modern_ui import QWidget", "QWidget"),
        ("from modern_ui import Signal", "Signal"),
        ("from modern_ui import Qt", "Qt"),
    ]

    print("\n🎨 Testing PySide6 Re-exports:")
    for import_stmt, name in pyside6_imports:
        total_tests += 1
        if not test_import(import_stmt, name):
            failed_imports.append(import_stmt)

    # Test functionality
    print("\n⚙️ Testing Functionality:")
    try:
        from modern_ui import check_feature_compatibility, get_available_features

        features = get_available_features()
        print(f"✅ get_available_features() returned {len(features)} features")

        audio_available = check_feature_compatibility("audio_processing")
        print(f"✅ check_feature_compatibility('audio_processing') = {audio_available}")

        total_tests += 2

    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        failed_imports.append("functionality_test")
        total_tests += 2

    # Test aliases functionality
    print("\n🔄 Testing Aliases Functionality:")
    try:
        # Check that aliases point to correct classes
        from modern_ui import (
            AudioEngine,
            AudioProcessingEngine,
            AudioWidget,
            MainWindow,
            ModernAudioWidget,
            TeddyMainWindow,
        )

        assert AudioWidget is ModernAudioWidget, "AudioWidget alias incorrect"
        assert AudioEngine is AudioProcessingEngine, "AudioEngine alias incorrect"
        assert MainWindow is TeddyMainWindow, "MainWindow alias incorrect"

        print("✅ All aliases point to correct classes")
        total_tests += 1

    except Exception as e:
        print(f"❌ Aliases test failed: {e}")
        failed_imports.append("aliases_test")
        total_tests += 1

    # Summary
    print("\n" + "=" * 60)
    print("📊 BACKWARD COMPATIBILITY TEST RESULTS:")
    print(f"✅ Passed: {total_tests - len(failed_imports)}/{total_tests}")
    print(f"❌ Failed: {len(failed_imports)}/{total_tests}")

    if failed_imports:
        print("\n❌ Failed Imports:")
        for imp in failed_imports:
            print(f"   - {imp}")
        return False
    else:
        print("\n🎉 ALL BACKWARD COMPATIBILITY TESTS PASSED!")
        print("   Old code will continue to work without modification!")
        return True


if __name__ == "__main__":
    success = test_backward_compatibility()
    sys.exit(0 if success else 1)
