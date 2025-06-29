@echo off
chcp 65001 >nul
title تشغيل واجهة دبدوب الذكي
color 0A

echo.
echo =========================================
echo      🧸 واجهة دبدوب الذكي 🧸
echo =========================================
echo.

:: التحقق من وجود Node.js
echo [1/4] فحص Node.js...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js غير مثبت!
    echo.
    echo يرجى تثبيت Node.js أولاً من:
    echo https://nodejs.org/
    echo.
    echo بعد التثبيت، أعد تشغيل هذا الملف
    pause
    exit /b 1
)
echo ✅ Node.js مثبت

:: الانتقال لمجلد frontend
echo.
echo [2/4] الانتقال لمجلد frontend...
if not exist "frontend" (
    echo ❌ مجلد frontend غير موجود!
    echo تأكد من وضع هذا الملف في مجلد المشروع الرئيسي
    pause
    exit /b 1
)
cd frontend
echo ✅ تم الانتقال

:: التحقق من التبعيات
echo.
echo [3/4] فحص التبعيات...
if not exist "node_modules" (
    echo ⏳ تثبيت التبعيات (قد يستغرق بضع دقائق)...
    npm install
    if %errorlevel% neq 0 (
        echo ❌ فشل في تثبيت التبعيات!
        echo تحقق من اتصال الإنترنت وحاول مرة أخرى
        pause
        exit /b 1
    )
    echo ✅ تم تثبيت التبعيات
) else (
    echo ✅ التبعيات مثبتة مسبقاً
)

:: بدء التشغيل
echo.
echo [4/4] بدء تشغيل الواجهة...
echo.
echo 🚀 سيتم فتح المتصفح تلقائياً على:
echo    http://localhost:3000
echo.
echo 💡 لإيقاف الخادم: اضغط Ctrl+C
echo.
echo =========================================
echo.

npm start

echo.
echo =========================================
echo      تم إيقاف الخادم بنجاح ✅
echo =========================================
pause 