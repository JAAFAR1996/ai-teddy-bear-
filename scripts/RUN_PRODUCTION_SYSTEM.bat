@echo off
echo ========================================
echo 🧸 AI Teddy Bear - Production System
echo ========================================
echo 🎯 نظام الدب الذكي جاهز للإنتاج والبيع
echo 📦 Enterprise-grade system ready
echo ========================================
echo.

cd /d "%~dp0"

echo 🔧 Installing dependencies...
pip install -q fastapi uvicorn aiohttp websockets

echo.
echo 🚀 Starting complete production system...
echo.

python production_teddy_system.py

pause 