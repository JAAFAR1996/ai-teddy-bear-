@echo off
title 🧸 ESP32 Render Test Simulator
cls

echo ================================================================
echo      🧸 AI TEDDY BEAR - ESP32 RENDER TEST SIMULATOR
echo ================================================================
echo.
echo 🌐 Testing deployed service: https://ai-teddy-bear.onrender.com
echo.
echo Starting ESP32 simulator for Render testing...
echo.

python scripts/esp32_render_test.py

echo.
echo ================================================================
echo 👋 ESP32 Simulator finished. Press any key to exit...
pause >nul 