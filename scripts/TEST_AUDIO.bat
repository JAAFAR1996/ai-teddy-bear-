@echo off
cls
title 🎵 اختبار الصوت - Audio Test

echo ====================================
echo 🎵 Audio Test - اختبار الصوت
echo ====================================
echo.

REM Check if Python exists
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python غير مثبت على النظام
    pause
    exit /b 1
)

REM Check if required modules exist
python -c "import pyaudio, pygame" 2>nul
if %errorlevel% neq 0 (
    echo ❌ المكتبات المطلوبة غير مثبتة
    echo يرجى تشغيل INSTALL_REQUIREMENTS.bat أولاً
    pause
    exit /b 1
)

echo ✅ جميع المتطلبات متوفرة
echo.

REM Navigate to project directory
cd /d "%~dp0"

echo 🎵 تشغيل اختبار الصوت...
echo.

REM Run the audio test
python test_audio.py

echo.
echo 🛑 انتهى الاختبار
pause 