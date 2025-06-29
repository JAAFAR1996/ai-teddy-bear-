@echo off
echo ===================================
echo 🏗️  AI Teddy Bear - Staging Environment
echo ===================================
echo.

REM تعيين متغيرات البيئة
set ENVIRONMENT=staging
set CONFIG_FILE=config/staging_config.json
set LOG_LEVEL=DEBUG

echo 📋 Checking system requirements...

REM فحص Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    pause
    exit /b 1
)

REM فحص المتطلبات
echo 📦 Installing/checking requirements...
pip install -r requirements.txt

REM إنشاء مجلدات السجلات
echo 📁 Creating logs directories...
if not exist "logs" mkdir logs
if not exist "cache" mkdir cache
if not exist "data" mkdir data

REM فحص ملف التكوين
echo 🔧 Checking configuration...
if not exist "%CONFIG_FILE%" (
    echo ❌ Staging config file not found: %CONFIG_FILE%
    echo Creating default staging config...
    copy config\config.json %CONFIG_FILE%
)

echo.
echo 🚀 Starting AI Teddy Bear System in STAGING mode...
echo.
echo ⚠️  STAGING ENVIRONMENT SETTINGS:
echo    - Database: staging_teddy_bear.db
echo    - Log Level: DEBUG
echo    - Notification Rate Limits: Reduced
echo    - Issue Tracking: Enabled
echo    - Simulation Mode: Active
echo.

REM تشغيل النظام
echo 🎯 Launching system components...
echo.

REM بدء خدمة Rate Monitor
echo 📊 Starting Rate Monitor Service...
python -c "
import asyncio
import sys
sys.path.append('src')
from application.services.rate_monitor_service import rate_monitor
from application.services.issue_tracker_service import issue_tracker

async def test_services():
    print('✅ Rate Monitor Service: Initialized')
    print('✅ Issue Tracker Service: Initialized')
    
    # إحصائيات أولية
    stats = await rate_monitor.get_statistics()
    print(f'📊 Current system stats: {stats}')
    
    # حالة النظام
    health = await issue_tracker.get_issue_statistics()
    print(f'🩺 System health: {health}')

asyncio.run(test_services())
"

if errorlevel 1 (
    echo ❌ Failed to initialize monitoring services
    pause
    exit /b 1
)

echo.
echo 🎮 Starting main system...
python src/main.py --config %CONFIG_FILE% --environment staging

if errorlevel 1 (
    echo ❌ System failed to start
    echo 📋 Check logs for details:
    echo    - logs/main.log
    echo    - logs/rate_monitor.db
    echo    - logs/issues.db
    pause
    exit /b 1
)

echo.
echo ✅ System started successfully!
echo.
echo 📊 Monitoring URLs:
echo    - Health Check: http://localhost:8000/health
echo    - Admin Dashboard: http://localhost:8000/admin
echo    - Rate Monitor Stats: http://localhost:8000/admin/rate-monitor
echo    - Issue Tracker: http://localhost:8000/admin/issues
echo.
echo 💡 Useful commands:
echo    - Test notification: curl -X POST http://localhost:8000/admin/notifications/trigger
echo    - View logs: tail -f logs/main.log
echo    - Stop system: Ctrl+C
echo.

pause 