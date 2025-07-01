@echo off
title AI Teddy Bear - Complete Demo
color 0B

echo ===============================================
echo  🎬 AI Teddy Bear - Complete Demo Experience
echo ===============================================
echo.

echo 🎯 This demo will showcase the full AI Teddy Bear system
echo    without requiring any ESP32 hardware!
echo.
echo What you'll experience:
echo ✨ Real AI conversation simulation
echo ✨ Parent dashboard with live metrics  
echo ✨ Voice recording and AI responses
echo ✨ Safety monitoring and content filtering
echo ✨ Multiple child profiles and interactions
echo.

pause

echo.
echo 🔄 Starting complete demo sequence...
echo.

REM Check if system is running
echo 📡 Checking system status...
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Backend not running. Starting system first...
    call start_teddy.bat
    timeout /t 10
) else (
    echo ✅ Backend is already running!
)

echo.
echo 🎮 Step 1: Starting ESP32 Simulator...
start "ESP32 Simulator" cmd /k "title ESP32 Simulator && python src/simulators/esp32_production_simulator.py"

timeout /t 3

echo.
echo 📊 Step 2: Starting Dashboard Demo...  
start "Dashboard Demo" cmd /k "title Dashboard Demo && python src/dashboards/dashboard-demo-runner.py"

timeout /t 3

echo.
echo 🤖 Step 3: Starting AI Testing Demo...
start "AI Testing Demo" cmd /k "title AI Testing Demo && python tests/ai_test_demo.py"

timeout /t 3

echo.
echo 📈 Step 4: Starting Observability Demo...
start "Observability Demo" cmd /k "title Observability Demo && python src/infrastructure/observability/observability_demo.py"

echo.
echo 🌐 Step 5: Opening web interfaces...
timeout /t 5

start http://localhost:3000
echo   📱 Parent Dashboard opened

timeout /t 2

start http://localhost:8000/docs  
echo   📚 API Documentation opened

timeout /t 2

start http://localhost:8000/health
echo   ❤️ Health Check opened

echo.
echo ===============================================
echo  🎉 COMPLETE DEMO IS NOW RUNNING!
echo ===============================================
echo.
echo 🎮 ESP32 Simulator:
echo    - Connect to server
echo    - Setup child profile
echo    - Try voice recording!
echo.
echo 📊 Dashboard Demo:
echo    - Watch live metrics
echo    - See safety scores  
echo    - Monitor conversations
echo.
echo 🌐 Web Interfaces:
echo    📱 Parent Dashboard: http://localhost:3000
echo    📚 API Docs: http://localhost:8000/docs
echo    ❤️ Health: http://localhost:8000/health
echo.
echo 💡 Demo Tips:
echo    1. Start with ESP32 Simulator - connect and setup profile
echo    2. Use "Hold to Talk" to record voice messages
echo    3. Watch Dashboard for real-time metrics
echo    4. Check web interfaces for detailed views
echo    5. Let demos run for 5-10 minutes for full experience
echo.
echo ⚠️ To stop all demos: close all terminal windows
echo    or run stop_teddy.bat
echo.

pause

echo.
echo 🎊 Demo Experience Guide:
echo ========================================
echo.
echo 🎤 Voice Interaction Test:
echo    1. Open ESP32 Simulator window
echo    2. Click "Connect to Server"  
echo    3. Click "Setup Child Profile"
echo    4. Hold "🎤 Hold to Talk" and say:
echo       • "مرحبا دبدوب" (Hello Teddy)
echo       • "احكي لي قصة" (Tell me a story)
echo       • "كيف حالك؟" (How are you?)
echo    5. Watch AI respond in real-time!
echo.
echo 📊 Dashboard Monitoring:
echo    1. Check Dashboard Demo terminal
echo    2. See live safety scores
echo    3. Monitor conversation growth
echo    4. Watch system health metrics
echo.
echo 🏆 Expected Results:
echo    ✅ ESP32 connects successfully
echo    ✅ Voice is recorded and processed
echo    ✅ AI generates appropriate responses
echo    ✅ Safety filters work correctly
echo    ✅ All metrics update in real-time
echo    ✅ Parent dashboard shows activity
echo.

pause

echo.
echo 🎯 Your AI Teddy Bear system is now fully demonstrated!
echo 🚀 Ready for real ESP32 hardware integration!
echo 💫 Perfect for showcasing to stakeholders and investors!
echo.
pause 