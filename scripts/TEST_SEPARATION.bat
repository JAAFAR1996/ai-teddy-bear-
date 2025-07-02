@echo off
echo.
echo 🏗️ Testing Moderation Service Separation
echo ========================================
echo.

cd /d "%~dp0"

echo 📦 Running separation tests...
python test_separation.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ All separation tests passed!
    echo.
    echo 🎯 Benefits achieved:
    echo    📁 API Clients      - Separate file
    echo    🏠 Local Checkers   - Separate file  
    echo    📦 Cache Manager    - Separate file
    echo    📊 Result Processor - Separate file
    echo    🚀 Main Service     - Clean and simple
    echo.
    echo 📈 Results:
    echo    ✅ Single Responsibility Principle
    echo    ✅ Easier to test and maintain
    echo    ✅ Modular and extensible
    echo    ✅ Reduced complexity
    echo    ✅ Clear separation of concerns
    echo.
) else (
    echo.
    echo ❌ Some separation tests failed.
    echo Please check the error messages above.
    echo.
)

pause 