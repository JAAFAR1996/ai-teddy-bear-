@echo off
echo ========================================
echo 🎯 Task 4: Dashboard Demo Launcher
echo ========================================
echo.
echo Starting ENHANCED AI Teddy Bear Dashboard with:
echo - Interactive Emotion Charts (4 types + Performance Mode)
echo - HIGH-QUALITY PDF Reports (300 DPI + Arabic fonts)
echo - Real-time WebSocket Notifications + Toast alerts
echo - Modern UI/UX Components with 2025 enhancements
echo.

REM Check if frontend directory exists
if not exist "frontend" (
    echo ❌ Error: frontend directory not found
    echo Please run this script from the project root directory
    pause
    exit /b 1
)

echo 📦 Installing dependencies...
cd frontend
call npm install

echo.
echo 🚀 Starting Dashboard Demo...
echo.
echo Available ENHANCED features to test:
echo - Emotion Charts: Line, Area, Pie, Radar + Performance controls
echo - PDF Generation: Professional reports (3x quality + Arabic fonts)  
echo - WebSocket Notifications: Real-time alerts with smart reconnection
echo - Performance Mode: Toggle high/normal performance for large datasets
echo - Responsive Design: Works on all devices with smooth animations
echo.
echo Dashboard will open at: http://localhost:3000
echo.

REM Start the development server
call npm start

echo.
echo ========================================
echo 🎉 Dashboard Demo Features:
echo ========================================
echo 📊 Charts: Performance toggle with data optimization
echo 📄 PDF: 300 DPI quality with Arabic font support  
echo 🔔 WebSocket: Smart reconnection + beautiful toasts
echo ⚡ Performance: Up to 40%% faster chart rendering
echo 🎨 UI: 2025 modern design with smooth animations
echo.
echo If npm is not found, please install Node.js first:
echo See SETUP_NODEJS_GUIDE.md for detailed instructions
echo.

pause 