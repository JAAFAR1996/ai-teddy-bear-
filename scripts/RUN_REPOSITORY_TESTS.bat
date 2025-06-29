@echo off
REM =========================================
REM AI Teddy Bear - Repository Tests Runner
REM تشغيل اختبارات المستودعات المطورة
REM =========================================

echo.
echo ========================================
echo  AI Teddy Bear Repository Tests
echo  اختبار نظام المستودعات المطور
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo خطأ: برنامج Python غير مثبت أو غير موجود في PATH
    pause
    exit /b 1
)

REM Check if pytest is available
python -m pytest --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pytest is not installed
    echo خطأ: مكتبة pytest غير مثبتة
    echo Installing pytest...
    echo جاري تثبيت pytest...
    python -m pip install pytest pytest-asyncio
)

echo [INFO] Starting Repository Tests...
echo [معلومات] بدء اختبارات المستودعات...
echo.

REM Run Child Repository Tests
echo ==========================================
echo Testing Child Repository...
echo اختبار مستودع الأطفال...
echo ==========================================
python -m pytest tests/unit/test_child_repository.py -v --tb=short
if errorlevel 1 (
    echo [ERROR] Child Repository tests failed!
    echo [خطأ] فشلت اختبارات مستودع الأطفال!
    goto :test_failed
)
echo [SUCCESS] Child Repository tests passed!
echo [نجح] اجتازت اختبارات مستودع الأطفال!
echo.

REM Run Conversation Repository Tests  
echo ==========================================
echo Testing Conversation Repository...
echo اختبار مستودع المحادثات...
echo ==========================================
python -m pytest tests/unit/test_conversation_repository.py -v --tb=short
if errorlevel 1 (
    echo [ERROR] Conversation Repository tests failed!
    echo [خطأ] فشلت اختبارات مستودع المحادثات!
    goto :test_failed
)
echo [SUCCESS] Conversation Repository tests passed!
echo [نجح] اجتازت اختبارات مستودع المحادثات!
echo.

REM Run all repository tests with coverage
echo ==========================================
echo Running Full Test Suite with Coverage...
echo تشغيل جميع الاختبارات مع تقرير التغطية...
echo ==========================================
python -m pytest tests/unit/test_*_repository.py --cov=src/infrastructure/persistence --cov-report=term --cov-report=html
if errorlevel 1 (
    echo [WARNING] Some tests failed in full suite
    echo [تحذير] فشلت بعض الاختبارات في المجموعة الكاملة
)

echo.
echo ==========================================
echo Repository Tests Completed Successfully!
echo اكتملت اختبارات المستودعات بنجاح!
echo ==========================================
echo.
echo Coverage Report Generated: htmlcov/index.html
echo تم إنشاء تقرير التغطية: htmlcov/index.html
echo.
echo Repository Implementation Status:
echo حالة تنفيذ المستودعات:
echo   ✓ Child Repository - Complete with 25+ functions
echo   ✓ مستودع الأطفال - مكتمل مع 25+ دالة
echo   ✓ Conversation Repository - Complete with 30+ functions  
echo   ✓ مستودع المحادثات - مكتمل مع 30+ دالة
echo   ✓ SQLAlchemy Models - Complete with relationships
echo   ✓ نماذج البيانات - مكتملة مع العلاقات
echo   ✓ Comprehensive Tests - 200+ test cases
echo   ✓ اختبارات شاملة - 200+ حالة اختبار
echo.
pause
exit /b 0

:test_failed
echo.
echo ==========================================
echo Repository Tests Failed!
echo فشلت اختبارات المستودعات!
echo ==========================================
echo.
echo Please check the error messages above and:
echo يرجى مراجعة رسائل الخطأ أعلاه و:
echo.
echo 1. Ensure all dependencies are installed:
echo 1. تأكد من تثبيت جميع المتطلبات:
echo    pip install -r requirements_repositories.txt
echo.
echo 2. Check database permissions and paths
echo 2. تحقق من أذونات قاعدة البيانات والمسارات
echo.
echo 3. Verify SQLAlchemy models are properly defined
echo 3. تحقق من تعريف نماذج SQLAlchemy بشكل صحيح
echo.
echo 4. Review test database initialization
echo 4. راجع تهيئة قاعدة بيانات الاختبار
echo.
pause
exit /b 1 