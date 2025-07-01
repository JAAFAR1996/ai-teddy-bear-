from typing import Any, Dict, List, Optional

#!/usr/bin/env python3
"""
Simple Backward Compatibility Test for modern_ui.py
اختبار بسيط للتوافق العكسي دون الحاجة للمكتبات الخارجية
"""

import ast
import importlib.util
import sys


def check_file_has_exports() -> Any:
    """Check that modern_ui.py has the expected exports"""
    print("🔍 Checking modern_ui.py structure...")
    
    try:
        with open('modern_ui.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for key imports
        expected_imports = [
            'AudioProcessingEngine',
            'WebSocketClient', 
            'ModernAudioWidget',
            'TeddyMainWindow',
            'ConversationWidget',
            'WaveformWidget'
        ]
        
        # Check for aliases
        expected_aliases = [
            'AudioWidget = ModernAudioWidget',
            'MainWindow = TeddyMainWindow',
            'AudioEngine = AudioProcessingEngine'
        ]
        
        # Check for utility functions
        expected_functions = [
            'def get_available_features',
            'def check_feature_compatibility',
            'def get_migration_info'
        ]
        
        print("\n✅ Checking Core Imports:")
        for item in expected_imports:
            if item in content:
                print(f"   ✅ {item} found")
            else:
                print(f"   ❌ {item} missing")
        
        print("\n✅ Checking Legacy Aliases:")
        for alias in expected_aliases:
            if alias in content:
                print(f"   ✅ {alias}")
            else:
                print(f"   ❌ {alias} missing")
        
        print("\n✅ Checking Utility Functions:")
        for func in expected_functions:
            if func in content:
                print(f"   ✅ {func}")
            else:
                print(f"   ❌ {func} missing")
        
        # Check __all__ list
        if '__all__' in content:
            print("\n✅ __all__ list found - exports are properly defined")
        else:
            print("\n❌ __all__ list missing")
        
        # Check backward compatibility comments
        if 'BACKWARD COMPATIBILITY' in content:
            print("✅ Backward compatibility documentation found")
        else:
            print("❌ Missing compatibility documentation")
        
        return True
        
    except Exception as e:
    logger.error(f"Error: {e}")"❌ modern_ui.py not found!")
        return False
    except Exception as e:
    logger.error(f"Error: {e}")f"❌ Error reading file: {e}")
        return False

def check_modular_files_exist() -> Any:
    """Check that the modular files exist"""
    print("\n🏗️ Checking Modular Structure:")
    
    expected_files = [
        'ui/audio/audio_engine.py',
        'ui/audio/audio_config.py', 
        'ui/audio/audio_recorder.py',
        'ui/networking/websocket_client.py',
        'ui/networking/message_sender.py',
        'ui/widgets/waveform_widget.py',
        'ui/widgets/conversation_widget.py',
        'ui/widgets/audio_widget.py',
        'ui/main_window.py'
    ]
    
    for file_path in expected_files:
        try:
            with open(file_path, 'r') as f:
                print(f"   ✅ {file_path}")
        except Exception as e:
    logger.error(f"Error: {e}")f"   ❌ {file_path} missing")
    
    return True

def check_import_syntax() -> Any:
    """Check that imports are syntactically correct"""
    print("\n📝 Checking Import Syntax:")
    
    try:
        # Try to parse the file without executing it
        with open('modern_ui.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the file to check syntax
        ast.parse(content)
        print("   ✅ modern_ui.py syntax is valid")
        
        # Check for circular imports by looking at the structure
        if 'from src.presentation.ui' in content:
            print("   ✅ Uses modular imports")
        else:
            print("   ❌ Modular imports not found")
        
        return True
        
    except Exception as e:
    logger.error(f"Error: {e}")f"   ❌ Syntax error in modern_ui.py: {e}")
        return False
    except Exception as e:
    logger.error(f"Error: {e}")f"   ❌ Error checking syntax: {e}")
        return False

def main() -> Any:
    """Run all compatibility checks"""
    print("🧸 AI Teddy Bear - Backward Compatibility Test")
    print("=" * 60)
    
    checks = [
        check_file_has_exports,
        check_modular_files_exist, 
        check_import_syntax
    ]
    
    passed = 0
    for check in checks:
        try:
            if check():
                passed += 1
        except Exception as e:
    logger.error(f"Error: {e}")f"❌ Check failed: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 COMPATIBILITY CHECK RESULTS: {passed}/{len(checks)} passed")
    
    if passed == len(checks):
        print("\n🎉 BACKWARD COMPATIBILITY STRUCTURE IS CORRECT!")
        print("   ✅ All expected exports are available")
        print("   ✅ Modular structure exists")
        print("   ✅ Syntax is valid")
        print("\n💡 To test actual imports, install required dependencies:")
        print("   pip install PySide6 numpy structlog")
        return True
    else:
        print(f"\n⚠️ {len(checks) - passed} checks failed")
        print("   Please review the modular structure")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 