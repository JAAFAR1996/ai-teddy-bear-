@echo off

:: تفعيل التخزين الدائم (store) أو المؤقت (cache)
git config --global credential.helper store
:: أو استخدم هذا إذا أردت تخزينًا مؤقتًا:
:: git config --global credential.helper "cache --timeout=3600"

:: إعداد التاريخ والوقت
for /f "tokens=1-4 delims=/ " %%a in ("%DATE%") do (
    set DD=%%a & set MM=%%b & set YYYY=%%c
)
set CURRENT_TIME=%TIME: =0%
set TIMESTAMP=%YYYY%-%MM%-%DD%_%CURRENT_TIME:~0,2%-%CURRENT_TIME:~3,2%

cd /d "C:\Users\jaafa\Desktop\5555\New folder"
echo 🔁 Running auto-backup for: %CD%

git add -A
git diff --cached --exit-code >nul
if %ERRORLEVEL% EQU 0 (
    echo ✅ لا توجد تغييرات لرفعها. %TIMESTAMP%
) else (
    git commit -m "Auto-backup %TIMESTAMP%"
    git push https://github.com/JAAFAR1996/ai-teddy-bear-.git main
    echo ✅ التغييرات تم رفعها.
    git log -1 --oneline
)

git status
pause
