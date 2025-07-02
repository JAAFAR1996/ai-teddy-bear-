@echo off
cls
title 🧸 AI Teddy Bear Simulator - محاكي الدب الذكي

echo ====================================
echo 🧸 AI Teddy Bear Simulator
echo    محاكي الدب الذكي
echo ====================================
echo.

REM Check if Python exists
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python غير مثبت على النظام
    echo يرجى تثبيت Python من https://python.org
    pause
    exit /b 1
)

echo ✅ تم العثور على Python

REM Check if required packages are installed
echo 📦 فحص المكتبات المطلوبة...

python -c "import tkinter" 2>nul
if %errorlevel% neq 0 (
    echo ❌ مكتبة tkinter غير مثبتة
    echo يرجى تثبيت tkinter
    pause
    exit /b 1
)

python -c "import pyaudio" 2>nul
if %errorlevel% neq 0 (
    echo ⚠️ مكتبة pyaudio غير مثبتة، تثبيت تلقائي...
    pip install pyaudio
)

python -c "import pygame" 2>nul
if %errorlevel% neq 0 (
    echo ⚠️ مكتبة pygame غير مثبتة، تثبيت تلقائي...
    pip install pygame
)

python -c "import requests" 2>nul
if %errorlevel% neq 0 (
    echo ⚠️ مكتبة requests غير مثبتة، تثبيت تلقائي...
    pip install requests
)

python -c "import aiohttp" 2>nul
if %errorlevel% neq 0 (
    echo ⚠️ مكتبة aiohttp غير مثبتة، تثبيت تلقائي...
    pip install aiohttp
)

python -c "import websockets" 2>nul
if %errorlevel% neq 0 (
    echo ⚠️ مكتبة websockets غير مثبتة، تثبيت تلقائي...
    pip install websockets
)

echo.
echo ✅ جميع المكتبات جاهزة

REM Navigate to project directory
cd /d "%~dp0"
cd ..

REM Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

echo.
echo 🚀 تشغيل محاكي الدب الذكي...
echo.
echo ℹ️ تذكير: تأكد من تشغيل السيرفر أولاً على المنفذ 5000
echo    يمكنك اختبار الصوت أولاً بتشغيل: TEST_AUDIO.bat
echo.

REM Run the simulator
python scripts/teddy_bear_simulator.py

echo.
echo 🛑 تم إيقاف المحاكي
pause 