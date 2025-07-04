@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM === تهيئة Git Credential Manager ===
git config --global credential.helper manager

REM === الانتقال إلى مجلد السكربت تلقائيًا ===
cd /d "%~dp0" || (
  echo [خطأ] لم يتم الانتقال إلى مجلد السكربت: "%~dp0"
  pause & exit /b 1
)
echo ✅ الانتقال إلى: %CD%

REM === تأكد من remote origin ===
git remote get-url origin >nul 2>&1 || (
  echo [ملاحظة] إضافة remote origin...
  git remote add origin https://github.com/JAAFAR1996/ai-teddy-bear-.git
)

REM === تحديد الفرع الحالي ===
for /f "delims=" %%b in ('git rev-parse --abbrev-ref HEAD') do set BRANCH=%%b
echo [فرع العمل:] !BRANCH!

REM === إضافة التعديلات ===
git add -A || (
  echo [خطأ] فشل git add!
  pause & exit /b 1
)

REM === في حال توجد تغييرات للتزام ===
git diff --cached --exit-code >nul || (
  git commit -m "Auto-backup %TIMESTAMP%" || (
    echo [خطأ] فشل git commit!
    pause & exit /b 1
  )

  REM === دفع التعديلات وإعداد upstream ===
  git push -u origin !BRANCH! >push.log 2>&1 || (
    type push.log
    echo [خطأ] فشل git push! تأكد من المصادقة أو تعارض بالفرع.
    pause & exit /b 2
  )

  echo ✅ تم رفع التعديلات بنجاح.
  git log -1 --oneline
) || (
  echo ✅ لا توجد تغييرات.
)

exit /b 0
