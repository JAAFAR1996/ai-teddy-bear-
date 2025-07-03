@echo off
chcp 65001 >nul

setlocal enabledelayedexpansion

git config --global credential.helper store

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
    :PUSH
    git push https://github.com/JAAFAR1996/ai-teddy-bear-.git main
    if errorlevel 1 (
        echo [تحذير] رفض الدفع، محاولة الدمج مع التغييرات من الريموت...
        git pull --no-edit origin main
        if errorlevel 1 (
            echo [خطأ] تعذر الدمج الآلي. فضلاً عالج التعارضات يدويًا.
            pause
            exit /b 1
        )
        goto PUSH
    )
    echo ✅ التغييرات تم رفعها بنجاح.
    git log -1 --oneline
) else (
    echo ✅ لا توجد تغييرات لرفعها. %TIMESTAMP%
)
git status
pause
