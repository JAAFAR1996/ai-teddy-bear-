@echo off
echo ===============================================
echo      🧸 AI TEDDY BEAR - ESP32 SIMULATOR
echo ===============================================
echo.
echo Starting ESP32 Simulator...
echo.

REM Start ESP32 Simulator
start "ESP32 Teddy Simulator" cmd /k "cd /d %~dp0 && python -m simulators.esp32_teddy_simulator"

echo.
echo ✅ ESP32 Simulator is starting in a new window!
echo.
echo 📝 Instructions:
echo   1. Click "Connect Cloud" 
echo   2. Click "Setup Child" (optional)
echo   3. Click "Talk to Teddy" or use Text Mode
echo   4. Say "يا دبدوب" then your message
echo.
echo ===============================================
pause 