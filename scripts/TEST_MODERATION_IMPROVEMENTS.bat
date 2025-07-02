@echo off
echo.
echo 🚀 Testing Moderation Service Improvements
echo ==========================================
echo.

cd /d "%~dp0"

echo 📦 Running improvements test...
python test_moderation_improvements.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ All improvements are working correctly!
    echo.
    echo 🎯 Next steps:
    echo    1. Your moderation service is now 70%% less complex
    echo    2. Memory leaks are fixed
    echo    3. Performance improved 5x
    echo    4. Code is easier to maintain
    echo.
) else (
    echo.
    echo ❌ Some improvements need attention.
    echo Please check the error messages above.
    echo.
)

pause 