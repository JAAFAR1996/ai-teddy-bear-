@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM === تهيئة Git Credential Manager (GCM) ===
git config --global credential.helper manager

REM === الانتقال إلى مجلد السكربت ===
cd /d "%~dp0" || (
  echo [خطأ] لم ينجح الانتقال إلى مجلد السكربت: "%~dp0"
  pause & exit /b 1
)
echo ✅ انتقلت إلى: %CD%

REM === تأكد وجود remote 'origin' ===
git remote get-url origin >nul 2>&1 || (
  echo [ملاحظة] إضافة remote origin...
  git remote add origin https://github.com/JAAFAR1996/ai-teddy-bear-.git
)

REM === معرفة الفرع الحالي ===
for /f "delims=" %%b in ('git rev-parse --abbrev-ref HEAD') do set BRANCH=%%b
echo [فرع العمل:] !BRANCH!

REM === إضافة، ورفع التغييرات ===
git add -A || (echo [خطأ] git add فشل! & pause & exit /b 1)
git diff --cached --exit-code >nul || (
  git commit -m "Auto-backup %TIMESTAMP%"
  git push -u origin !BRANCH! || (
    echo [خطأ] git push فشل!
    pause & exit /b 2
  )
  echo ✅ تم رفع التغييرات بنجاح
)
exit /b 0
