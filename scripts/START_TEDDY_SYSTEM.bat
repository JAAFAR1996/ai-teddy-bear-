@echo off
title AI Teddy Bear System Launcher
color 0A

echo.
echo =====================================
echo   🧸 AI Teddy Bear System Launcher
echo =====================================
echo.
echo 🎯 Complete Production System
echo ☁️ Cloud Server + 🧸 ESP32 + 📱 Parent App
echo.

echo 🚀 Step 1: Starting Cloud Server...
start "Cloud Server" cmd /k "python -m src.main"
timeout /t 5 /nobreak >nul

echo 🧸 Step 2: Starting ESP32 Teddy Simulator...
start "ESP32 Teddy" cmd /k "python simulators/esp32_teddy_simulator.py"
timeout /t 2 /nobreak >nul

echo 📱 Step 3: Starting Parent Mobile App...
start "Parent App" cmd /k "python simulators/parent_mobile_app_simulator.py"
timeout /t 2 /nobreak >nul

echo.
echo ✅ All components started!
echo.
echo 📋 Instructions:
echo   1. In ESP32 Teddy window: Click "POWER ON"
echo   2. Say "يا دبدوب" to the microphone
echo   3. Start talking with your AI teddy!
echo   4. Use Parent App to monitor and control
echo.
echo 🎉 Enjoy your AI Teddy Bear system!
echo.
pause 