@echo off
REM Enhanced Audio System Test Runner
REM تشغيل اختبارات النظام الصوتي المتطور

echo ========================================
echo   AI Teddy Bear Enhanced Audio System
echo           Test Runner
echo ========================================
echo.

REM Set encoding for Arabic text
chcp 65001 > nul

REM Check Python installation
python --version > nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.8+
    pause
    exit /b 1
)

echo ✅ Python installation verified

REM Check if virtual environment should be created
if not exist "venv" (
    echo 🔧 Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/upgrade required packages
echo 📦 Installing/upgrading required packages...
pip install --upgrade pip
pip install -r requirements_enhanced_audio.txt
if errorlevel 1 (
    echo ⚠️ Some packages failed to install, continuing with available packages...
)

echo.
echo 🚀 Starting Enhanced Audio System Tests...
echo.

REM Run quick test first
echo ⚡ Running quick test...
python test_enhanced_audio_system.py quick
if errorlevel 1 (
    echo ❌ Quick test failed
    set QUICK_TEST_FAILED=1
) else (
    echo ✅ Quick test passed
    set QUICK_TEST_FAILED=0
)

echo.
echo 🧪 Running comprehensive tests...

REM Run comprehensive tests
python test_enhanced_audio_system.py
set COMPREHENSIVE_TEST_RESULT=%errorlevel%

echo.
echo ========================================
echo           Test Results Summary
echo ========================================

if %QUICK_TEST_FAILED%==0 (
    echo ✅ Quick Test: PASSED
) else (
    echo ❌ Quick Test: FAILED
)

if %COMPREHENSIVE_TEST_RESULT%==0 (
    echo ✅ Comprehensive Tests: PASSED
) else (
    echo ❌ Comprehensive Tests: FAILED
)

echo.

REM Check if audio system is working
echo 🔍 Checking audio system status...
python -c "
try:
    from src.audio.audio_manager import EnhancedAudioManager, create_child_safe_config
    config = create_child_safe_config()
    manager = EnhancedAudioManager(config)
    formats = manager.get_supported_formats()
    stats = manager.get_system_stats()
    manager.cleanup()
    print(f'📊 Supported formats: {len(formats)}')
    print(f'🎵 Audio system: OPERATIONAL')
except Exception as e:
    print(f'⚠️ Audio system issue: {e}')
"

echo.
echo 📁 Test files location:
for /f %%i in ('python -c "import tempfile; print(tempfile.gettempdir())"') do (
    echo    %%i\test_enhanced_audio_*
)

echo.
echo 📋 Next steps:
echo    1. Review test results above
echo    2. Check log files for detailed information
echo    3. Install missing audio libraries if needed:
echo       - ffmpeg: https://ffmpeg.org/download.html
echo       - PyAudio: pip install pipwin && pipwin install pyaudio
echo    4. Run individual tests: python test_enhanced_audio_system.py

echo.
echo 🧸 AI Teddy Bear Enhanced Audio System Test Complete! 🧸
pause 