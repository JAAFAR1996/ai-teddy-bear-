@echo off
:: إعداد التاريخ والوقت بشكل مرتب
for /f "tokens=1-4 delims=/ " %%a in ("%DATE%") do (
    set DD=%%a
    set MM=%%b
    set YYYY=%%c
)
set CURRENT_TIME=%TIME: =0%
set TIMESTAMP=%YYYY%-%MM%-%DD%_%CURRENT_TIME:~0,2%-%CURRENT_TIME:~3,2%

:: الانتقال إلى مجلد المشروع
cd /d "C:\Users\jaafa\Desktop\5555\New folder"

:: عرض المسار الحالي
echo 🔁 Running auto-backup for: %CD%

:: إضافة كل الملفات (جديدة، معدلة، محذوفة)
git add -A

:: التحقق من وجود تغييرات
git diff --cached --exit-code >nul
if %ERRORLEVEL% EQU 0 (
    echo ✅ لا توجد تغييرات لرفعها. %TIMESTAMP%
) else (
    :: إنشاء commit باسم وتاريخ
    git commit -m "Auto-backup %TIMESTAMP%"

    :: رفع التغييرات (باستخدام التوكن المباشر مثل سكربتك الأصلي)
    git push https://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@github.com/JAAFAR1996/ai-teddy-bear-.git main

    echo ✅ التغييرات تم رفعها بنجاح إلى GitHub.
    git log -1 --oneline
)

:: عرض الحالة النهائية
git status
pause
