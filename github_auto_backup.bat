@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM — تهيئة Git Credential Manager
git config --global credential.helper manager

REM — التنقل إلى مجلّد السكربت نفسه
cd /d "%~dp0" || (
  echo [خطأ] فشل الانتقال إلى مجلد السكربت: "%~dp0"
  pause & exit /b 1
)
echo ✅ مجلد العمل: %CD%

REM — ضبط سلوك الدفع التلقائي للفرع الحالي
git config --global push.default current
git config --global push.autoSetupRemote true

REM — تأكيد وجود الريموت origin
git remote get-url origin >nul 2>&1 || (
  echo [ملاحظة] إضافة remote origin...
  git remote add origin https://github.com/JAAFAR1996/ai-teddy-bear-.git
)

REM — تحديد اسم الفرع الحالي
for /f "delims=" %%b in ('git rev-parse --abbrev-ref HEAD') do set BRANCH=%%b
echo [فرع العمل الحالي:] !BRANCH!

REM — إذا كنا على فرع مختلف عن main، نستخدم stash للانتقال دون مشاكل:
set "TARGET=main"
if /I "!BRANCH!" NEQ "%TARGET%" (
  echo [تنبيه] غير على main، سيتم تخزين التعديلات مؤقتًا...
  git stash push -u -m "auto-backup stash" 1>nul 2>&1

  git checkout %TARGET% || (
    echo [خطأ] فشل checkout إلى main. تأكد من وجوده.
    pause & exit /b 1
  )

  echo ✅ تم الانتقال إلى main، استعادة التعديلات...
  git stash pop 1>nul 2>&1
)

REM — إضافة وتلخيص التغييرات
git add -A || (
  echo [خطأ] git add فشل!
  pause & exit /b 1
)

REM — إذا وُجدت تغييرات، نلزمها ونرفعها:
git diff --cached --exit-code >nul || (
  git commit -m "Auto-backup %DATE%_%TIME%" || (
    echo [خطأ] git commit فشل!
    pause & exit /b 1
  )

  git push origin %TARGET% || (
    echo [خطأ] git push فشل! تحقق من المصادقة أو التراخيص.
    pause & exit /b 2
  )

  echo ✅ تم الدفع إلى "%TARGET%" بنجاح.
  git log -1 --oneline
) || (
  echo ✅ لا توجد تغييرات جديدة للالتزام.
)

pause
exit /b 0
