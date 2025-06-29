@echo off
title AI Teddy Bear - Enhanced System v2.0

echo ===============================================
echo      🧸 AI TEDDY BEAR - ENHANCED SYSTEM v2.0
echo ===============================================
echo.

echo 🌟 New Features:
echo   ✅ Advanced Emotion Analysis
echo   ✅ Secure ESP32 Communication  
echo   ✅ Parent Report Generation
echo   ✅ Enhanced Voice Processing
echo   ✅ Smart Content Recommendations
echo.

echo 📋 System Requirements Check...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.11+
    pause
    exit /b 1
)
echo ✅ Python found

echo.
echo 🚀 Choose startup option:
echo   1. Enhanced System (Recommended)
echo   2. Legacy Production System
echo   3. Development Mode
echo   4. Install/Update Requirements
echo   5. System Diagnostics
echo.

set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" goto enhanced
if "%choice%"=="2" goto legacy
if "%choice%"=="3" goto dev
if "%choice%"=="4" goto install
if "%choice%"=="5" goto diagnostics

echo Invalid choice!
pause
exit /b 1

:enhanced
echo.
echo 🚀 Starting Enhanced AI Teddy Bear System...
echo.

REM Check for enhanced requirements
echo 📦 Checking enhanced requirements...
pip show transformers >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Enhanced AI packages not found. Installing...
    pip install transformers torch librosa
)

echo 🧸 Starting Enhanced Server...
start "AI Teddy Server Enhanced" cmd /k "python -m src.main"

timeout /t 3 >nul

echo 📱 Starting ESP32 Advanced Simulator...
start "ESP32 Advanced Simulator" cmd /k "python -m simulators.esp32_teddy_simulator"

timeout /t 2 >nul

echo 🌐 Opening Enhanced Dashboard...
start http://localhost:8000/docs
start http://localhost:8000/dashboard

echo.
echo ✅ Enhanced System Started Successfully!
echo.
echo 📖 Usage Guide:
echo   • Server: http://localhost:8000
echo   • API Docs: http://localhost:8000/docs  
echo   • Dashboard: http://localhost:8000/dashboard
echo   • Health: http://localhost:8000/health
echo.
echo 🎤 Voice Interaction:
echo   1. Say "يا دبدوب" (wake word)
echo   2. Wait for blue LED
echo   3. Speak your message
echo.
echo 📊 New Features:
echo   • Advanced emotion analysis from voice and text
echo   • Secure ESP32 communication with HTTPS
echo   • Comprehensive parent reports with charts
echo   • Smart recommendations based on child's profile
echo.
goto end

:legacy
echo.
echo 🔄 Starting Legacy Production System...
python production_teddy_system.py
goto end

:dev
echo.
echo 🛠️ Starting Development Mode...
echo.
set FLASK_ENV=development
set DEBUG=true
python -m src.main --debug
goto end

:install
echo.
echo 📦 Installing/Updating Requirements...
echo.

echo Installing basic requirements...
pip install -r requirements.txt

echo.
echo Installing enhanced requirements...
pip install -r requirements_enhanced.txt

echo.
echo Installing AI models...
python -c "from transformers import pipeline; pipeline('text-classification', model='j-hartmann/emotion-english-distilroberta-base')"

echo.
echo ✅ All requirements installed successfully!
echo.
pause
goto enhanced

:diagnostics
echo.
echo 🔍 Running System Diagnostics...
echo.

echo Checking Python environment...
python --version

echo.
echo Checking required packages...
python -c "import fastapi; print('✅ FastAPI:', fastapi.__version__)"
python -c "import transformers; print('✅ Transformers:', transformers.__version__)" 2>nul || echo "❌ Transformers not installed"
python -c "import torch; print('✅ PyTorch:', torch.__version__)" 2>nul || echo "❌ PyTorch not installed"
python -c "import librosa; print('✅ Librosa:', librosa.__version__)" 2>nul || echo "❌ Librosa not installed"

echo.
echo Checking system health...
python -c "
import requests
try:
    response = requests.get('http://localhost:8000/health', timeout=5)
    print('✅ Server is running:', response.status_code)
    print('   Response:', response.json())
except:
    print('❌ Server is not running')
"

echo.
echo Running security scan...
if exist scripts\security_scan.py (
    python scripts\security_scan.py
) else (
    echo ⚠️ Security scan script not found
)

echo.
echo 📋 Diagnostic Summary:
echo   • Check the output above for any issues
echo   • Missing packages can be installed with option 4
echo   • If server is not running, use option 1 to start
echo.
pause
goto start

:end
echo.
echo 🧸 AI Teddy Bear System is ready!
echo.
echo 📖 For help and documentation:
echo   • Read: ENHANCED_SYSTEM_GUIDE.md
echo   • Visit: docs/README.md
echo   • Support: Create GitHub issue
echo.
echo Press any key to exit...
pause >nul 