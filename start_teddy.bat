@echo off
title AI Teddy Bear - Quick Start
color 0A

echo ===============================================
echo  🧸 AI Teddy Bear - Quick Start (Windows)
echo ===============================================
echo.

REM التحقق من وجود Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.11+
    echo Download from: https://python.org
    pause
    exit /b 1
)

REM التحقق من وجود Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js not found! Please install Node.js 18+
    echo Download from: https://nodejs.org
    pause
    exit /b 1
)

echo ✅ System requirements check passed!
echo.

REM التحقق من وجود البيئة الافتراضية
if not exist "venv\" (
    echo 📦 Creating Python virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
    echo ✅ Virtual environment created!
)

REM تفعيل البيئة الافتراضية
echo 🔄 Activating virtual environment...
call venv\Scripts\activate

REM تثبيت المتطلبات إذا لم تكن مثبتة
if not exist "venv\Lib\site-packages\fastapi\" (
    echo 📥 Installing Python dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
    echo ✅ Dependencies installed!
)

REM التحقق من إعدادات Frontend
if not exist "frontend\node_modules\" (
    echo 📥 Installing Frontend dependencies...
    cd frontend
    npm install
    if errorlevel 1 (
        echo ❌ Failed to install frontend dependencies
        cd ..
        pause
        exit /b 1
    )
    cd ..
    echo ✅ Frontend dependencies installed!
)

REM إنشاء ملف .env إذا لم يكن موجود
if not exist ".env" (
    echo 🔐 Creating environment configuration...
    python scripts/generate_env.py
    echo ⚠️ Please add your API keys to .env file!
    echo Press any key after adding your API keys...
    pause
)

REM تشغيل إعداد المشروع
echo 🛠️ Setting up project...
python src/setup.py

echo.
echo 🚀 Starting AI Teddy Bear...
echo.

REM تشغيل Backend
echo Starting Backend Server...
start "AI Teddy - Backend" cmd /k "title Backend Server && python src/main.py"

REM انتظار قليل للتأكد من تشغيل Backend
timeout /t 8 /nobreak

REM تشغيل Frontend
echo Starting Frontend Dashboard...
start "AI Teddy - Frontend" cmd /k "title Frontend Dashboard && cd frontend && npm start"

echo.
echo ===============================================
echo  🎉 AI Teddy Bear is starting!
echo ===============================================
echo  📱 Frontend Dashboard: http://localhost:3000
echo  🔗 Backend API: http://localhost:8000
echo  📊 Health Check: http://localhost:8000/health
echo ===============================================
echo.
echo Press any key to open the dashboard in browser...
pause

REM فتح المتصفح
start http://localhost:3000

echo.
echo 💡 Tips:
echo - Keep this window open
echo - Check the other terminal windows for logs
echo - Press Ctrl+C in terminal windows to stop services
echo.
pause 