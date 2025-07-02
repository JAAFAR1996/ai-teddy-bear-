@echo off
echo 🧸 ESP32 Real Simulator Launcher
echo ================================
echo.
echo 🚀 Starting Real ESP32 AI Teddy Bear Simulator...
echo 📡 Server: https://ai-teddy-bear.onrender.com
echo.

REM تحقق من وجود Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.8+
    pause
    exit /b 1
)

REM تحقق من وجود الملف
if not exist "Real_ESP32_Simulator.py" (
    echo ❌ Real_ESP32_Simulator.py not found!
    pause
    exit /b 1
)

echo ✅ Python detected
echo 🎤 Checking microphone permissions...
echo.

REM تشغيل المحاكي
echo 🧸 Launching ESP32 Real Simulator...
python Real_ESP32_Simulator.py

echo.
echo 🔴 Simulator closed
pause 