@echo off
chcp 65001 >nul

setlocal enabledelayedexpansion

REM استخدم Credential Manager الأكثر أماناً
git config --global credential.helper manager-core

for /f "tokens=1-4 delims=/ " %%a in ("%DATE%") do (
    set DD=%%a
    set MM=%%b
    set YYYY=%%c
)
set CURRENT_TIME=%TIME: =0%
set TIMESTAMP=%YYYY%-%MM%-%DD%_%CURRENT_TIME:~0,2%-%CURRENT_TIME:~3,2%

cd /d "C:\Users\jaafa\Desktop\5555\New folder"
echo Running auto-backup for: %CD%

git add -A

git diff --cached --exit-code >nul
if errorlevel 1 (
    git commit -m "Auto-backup %TIMESTAMP%"

    REM جلب اسم الفرع الحالي
    for /f "delims=" %%b in ('git rev-parse --abbrev-ref HEAD') do set BRANCH=%%b

    :PUSH
    git push https://github.com/JAAFAR1996/ai-teddy-bear-.git !BRANCH!
    if errorlevel 1 (
        echo [تحذير] رفض الدفع، محاولة الدمج مع التغييرات من الريموت...
        git pull --no-edit origin !BRANCH!
        if errorlevel 1 (
            echo [خطأ] تعذر الدمج الآلي. فضلاً عالج التعارضات يدويًا.
            pause
            exit /b 1
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
