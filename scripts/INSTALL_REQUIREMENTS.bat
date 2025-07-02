@echo off
cls
title 🧸 تثبيت متطلبات محاكي الدب الذكي

echo ====================================
echo 🧸 AI Teddy Bear Simulator
echo    تثبيت المتطلبات
echo ====================================
echo.

REM Check if Python exists
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python غير مثبت على النظام
    echo يرجى تثبيت Python من https://python.org
    echo تأكد من تحديد "Add Python to PATH" أثناء التثبيت
    pause
    exit /b 1
)

echo ✅ تم العثور على Python
python --version

REM Check if pip exists
where pip >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ pip غير متوفر
    echo يرجى إعادة تثبيت Python مع pip
    pause
    exit /b 1
)

echo ✅ تم العثور على pip
echo.

echo 📦 تثبيت المتطلبات الأساسية...
echo.

REM Update pip first
echo ⬆️ تحديث pip...
python -m pip install --upgrade pip

echo.
echo 🎵 تثبيت مكتبة pyaudio (قد تستغرق وقتاً)...
pip install pyaudio
if %errorlevel% neq 0 (
    echo ⚠️ فشل تثبيت pyaudio بالطريقة العادية، جربة pipwin...
    pip install pipwin
    if %errorlevel% neq 0 (
        echo ❌ فشل تثبيت pipwin أيضاً
        echo يرجى تثبيت pyaudio يدوياً
        pause
        exit /b 1
    )
    pipwin install pyaudio
    if %errorlevel% neq 0 (
        echo ❌ فشل تثبيت pyaudio
        echo يرجى تثبيت Visual Studio Build Tools أو تحميل wheel file
        pause
        exit /b 1
    )
)

echo ✅ تم تثبيت pyaudio

echo.
echo 🎮 تثبيت pygame...
pip install pygame
if %errorlevel% neq 0 (
    echo ❌ فشل تثبيت pygame
    pause
    exit /b 1
)
echo ✅ تم تثبيت pygame

echo.
echo 🌐 تثبيت مكتبات الشبكة...
pip install requests aiohttp websockets
if %errorlevel% neq 0 (
    echo ❌ فشل تثبيت مكتبات الشبكة
    pause
    exit /b 1
)
echo ✅ تم تثبيت مكتبات الشبكة

echo.
echo 🔍 تثبيت المكتبات الاختيارية...
pip install sounddevice scipy numpy
if %errorlevel% neq 0 (
    echo ⚠️ فشل تثبيت بعض المكتبات الاختيارية (ليس ضرورياً)
)

echo.
echo ✅ ============================================
echo ✅ تم تثبيت جميع المتطلبات بنجاح!
echo ✅ ============================================
echo.
echo 🚀 يمكنك الآن تشغيل المحاكي بالضغط على:
echo    START_TEDDY_SIMULATOR.bat
echo.

pause 