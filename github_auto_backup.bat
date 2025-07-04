@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM === إعداد Git Credential Manager Core تلقائيًا ===
git config --global credential.helper manager-core

REM === إعداد التاريخ والوقت ===
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
    echo [خطأ] لم يتم العثور على remote! سيتم تعيينه...
    git remote add origin https://github.com/JAAFAR1996/ai-teddy-bear-.git
)

REM === معرفة الفرع الحالي ===
for /f "delims=" %%b in ('git rev-parse --abbrev-ref HEAD') do set BRANCH=%%b
echo [ملاحظة] الفرع الحالي: !BRANCH!

REM === إضافة جميع التغييرات ===
git add -A
if errorlevel 1 (
    echo [خطأ] فشل git add -A! تأكد من أنك في المسار الصحيح.
    pause & exit /b 1
)

git status

REM === التحقق من وجود تغييرات للتزام ===
git diff --cached --exit-code >nul
if errorlevel 1 (
    git commit -m "Auto-backup %TIMESTAMP%"
    if errorlevel 1 (
        echo [خطأ] فشل git commit!
        pause & exit /b 1
    )

    REM === دفع التغييرات وتعيين upstream عند الحاجة ===
    git push -u origin !BRANCH! 2>push.log
    if errorlevel 1 (
        type push.log
        echo [تحذير] فشل push! جاري المحاولة بعد pull...
        git pull --no-edit origin !BRANCH!
        if errorlevel 1 (
            echo [خطأ] تعارضات في الدمج تحتاج معالجة يدوية.
            pause & exit /b 2
        )
        goto PUSH_RETRY
    )
    echo ✅ التغييرات تم رفعها بنجاح.
    git log -1 --oneline
    goto END

    :PUSH_RETRY
    git push origin !BRANCH! 2>push2.log
    if errorlevel 1 (
        type push2.log
        echo [خطأ] لا يزال الدفع يفشل بعد الدمج.
        pause & exit /b 3
    )
    echo ✅ الدفع بعد الدمج تم بنجاح.
    git log -1 --oneline
) else (
    echo ✅ لا توجد تغييرات لرفعها. %TIMESTAMP%
)

:END
exit /b 0
