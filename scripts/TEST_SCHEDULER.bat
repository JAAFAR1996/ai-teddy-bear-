@echo off
REM ⏰ AI Teddy Bear - Scheduler Test Runner
REM اختبار نظام الجدولة APScheduler

echo.
echo 🧸 AI Teddy Bear - Scheduler Integration Test
echo =============================================
echo.

REM تحقق من وجود Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM تحقق من المتطلبات
echo 📦 Checking requirements...
python -c "import apscheduler" >nul 2>&1
if errorlevel 1 (
    echo ❌ APScheduler not found. Installing...
    pip install apscheduler
    if errorlevel 1 (
        echo ❌ Failed to install APScheduler
        pause
        exit /b 1
    )
)

echo ✅ Dependencies ready
echo.

REM تشغيل اختبار المجدول
echo 🚀 Running scheduler integration test...
echo.

python test_scheduler_integration.py

if errorlevel 1 (
    echo.
    echo ❌ Test failed! Check the error messages above.
) else (
    echo.
    echo ✅ Test completed successfully!
    echo 🎉 Scheduler is ready for production use!
)

echo.
echo Press any key to exit...
pause >nul 