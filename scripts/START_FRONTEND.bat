@echo off
echo Starting AI Teddy Bear Frontend...
echo.

cd frontend
if %errorlevel% neq 0 (
    echo Error: frontend directory not found!
    pause
    exit /b 1
)

echo Installing dependencies...
npm install

echo Starting development server...
npm start

pause 