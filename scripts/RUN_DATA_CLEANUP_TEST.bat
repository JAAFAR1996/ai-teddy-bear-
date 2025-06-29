@echo off
chcp 65001 > nul
title AI Teddy Bear - Data Cleanup Service Test

echo.
echo ==========================================
echo 🧸 AI Teddy Bear - Data Cleanup Test
echo ==========================================
echo.

echo 🔍 Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python not found! Please install Python 3.9+
    pause
    exit /b 1
)

echo.
echo 🔍 Checking project directory...
if not exist "src" (
    echo ❌ Project directory not found! Run from project root.
    pause
    exit /b 1
)

echo.
echo 🚀 Running Data Cleanup Service Test...
echo.

python test_data_cleanup_service.py

echo.
echo 📄 Test completed! Check the results above.
echo.

if exist "data_cleanup_test_results.json" (
    echo 📋 Detailed results saved to: data_cleanup_test_results.json
)

echo.
pause 