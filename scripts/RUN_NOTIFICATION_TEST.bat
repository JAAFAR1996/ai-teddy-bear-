@echo off
chcp 65001 > nul
color 0A

echo.
echo 🛎️ ========================================
echo    AI Teddy Bear - Notification Service Test
echo ========================================
echo.

echo 📋 Starting Notification Service Test Suite...
echo    Testing all notification channels and features
echo.

REM تشغيل اختبار خدمة الإشعارات
echo ⚡ Running notification service tests...
python test_notification_service.py

echo.
if errorlevel 1 (
    echo ❌ Tests completed with errors. Check the output above.
    echo    Please review and fix issues before deploying.
) else (
    echo ✅ Tests completed successfully!
    echo    Notification service is ready for production.
)

echo.
echo 📄 Check notification_test_results.json for detailed results
echo.

pause 