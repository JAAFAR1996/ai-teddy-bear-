@echo off
chcp 65001 >nul

setlocal enabledelayedexpansion

REM === إعداد التاريخ والوقت بشكل احترافي ===
for /f "tokens=1-4 delims=/ " %%a in ("%DATE%") do (
    set DD=%%a
    set MM=%%b
    set YYYY=%%c
)
set CURRENT_TIME=%TIME: =0%
set TIMESTAMP=%YYYY%-%MM%-%DD%_%CURRENT_TIME:~0,2%-%CURRENT_TIME:~3,2%

REM === الذهاب إلى مجلد المشروع ===
cd /d "C:\Users\jaafa\Desktop\5555\New folder"
echo Running auto-backup for: %CD%

REM === التأكد من وجود remote ===
git remote -v >nul 2>&1
if errorlevel 1 (
    echo [خطأ] لم يتم العثور على remote! سيتم تعيين الريموت الآن...
    git remote add origin https://github.com/JAAFAR1996/ai-teddy-bear-.git
)

REM === التأكد من الفرع الحالي تلقائيًا ===
for /f "delims=" %%b in ('git rev-parse --abbrev-ref HEAD') do set BRANCH=%%b
echo [ملاحظة] الفرع الحالي: !BRANCH!

REM === إضافة جميع التغييرات للـ staging area ===
git add -A
if errorlevel 1 (
    echo [خطأ] فشل في git add -A! تأكد من أنك في مجلد المشروع الصحيح أو لا يوجد ملف مقفل.
    pause
    exit /b 1
)

REM === فحص الملفات التي سيتم رفعها ===
git status

REM === التأكد من وجود تغييرات ستدخل للـ commit ===
git diff --cached --exit-code >nul
if errorlevel 1 (
    git commit -m "Auto-backup %TIMESTAMP%"
    if errorlevel 1 (
        echo [خطأ] فشل تنفيذ git commit. تحقق من المشاكل أو رسائل الخطأ.
        pause
        exit /b 1
    )
    :PUSH
    git push origin !BRANCH!
    if errorlevel 1 (
        echo [تحذير] فشل push! محاولة دمج مع الريموت...
        git pull --no-edit origin !BRANCH!
        if errorlevel 1 (
            echo [خطأ] تعذر الدمج الآلي. عالج التعارضات يدويًا.
            pause
            exit /b 2
        )
        goto PUSH
    )
    echo ✅ التغييرات تم رفعها بنجاح.
    git log -1 --oneline
    exit /b 0
) else (
    echo ✅ لا توجد تغييرات لرفعها. %TIMESTAMP%
    exit /b 0
)

REM === نهاية السكريبت ===
pause
