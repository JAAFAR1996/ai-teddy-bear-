@echo off
title AI Teddy Bear - Stop Services
color 0C

echo ===============================================
echo  🛑 AI Teddy Bear - Stop Services (Windows)
echo ===============================================
echo.

echo Stopping AI Teddy Bear services...
echo.

REM Stop processes running on common ports
echo 🔍 Finding and stopping services...

REM Stop processes on port 8000 (Backend)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do (
    echo Stopping Backend service (PID: %%a)
    taskkill /PID %%a /F >nul 2>&1
)

REM Stop processes on port 3000 (Frontend)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000') do (
    echo Stopping Frontend service (PID: %%a)
    taskkill /PID %%a /F >nul 2>&1
)

REM Stop processes on port 8765 (WebSocket)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8765') do (
    echo Stopping WebSocket service (PID: %%a)
    taskkill /PID %%a /F >nul 2>&1
)

REM Stop Node.js processes
echo Stopping Node.js processes...
taskkill /IM node.exe /F >nul 2>&1

REM Stop Python processes with "main.py" in command line
echo Stopping Python processes...
wmic process where "commandline like '%%main.py%%'" delete >nul 2>&1

echo.
echo ✅ All AI Teddy Bear services have been stopped!
echo.
pause 