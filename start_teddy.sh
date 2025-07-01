#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}===============================================${NC}"
echo -e "${BLUE} 🧸 AI Teddy Bear - Quick Start (Mac/Linux)${NC}"
echo -e "${BLUE}===============================================${NC}"
echo

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 not found! Please install Python 3.11+${NC}"
    echo "Download from: https://python.org"
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js not found! Please install Node.js 18+${NC}"
    echo "Download from: https://nodejs.org"
    exit 1
fi

echo -e "${GREEN}✅ System requirements check passed!${NC}"
echo

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Creating Python virtual environment...${NC}"
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Failed to create virtual environment${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Virtual environment created!${NC}"
fi

# Activate virtual environment
echo -e "${YELLOW}🔄 Activating virtual environment...${NC}"
source venv/bin/activate

# Install Python dependencies if not installed
if [ ! -f "venv/lib/python*/site-packages/fastapi/__init__.py" ]; then
    echo -e "${YELLOW}📥 Installing Python dependencies...${NC}"
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Failed to install dependencies${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Dependencies installed!${NC}"
fi

# Install Frontend dependencies if not installed
if [ ! -d "frontend/node_modules" ]; then
    echo -e "${YELLOW}📥 Installing Frontend dependencies...${NC}"
    cd frontend
    npm install
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Failed to install frontend dependencies${NC}"
        exit 1
    fi
    cd ..
    echo -e "${GREEN}✅ Frontend dependencies installed!${NC}"
fi

# Create .env file if not exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}🔐 Creating environment configuration...${NC}"
    python scripts/generate_env.py
    echo -e "${YELLOW}⚠️ Please add your API keys to .env file!${NC}"
    echo "Press Enter after adding your API keys..."
    read
fi

# Setup project
echo -e "${YELLOW}🛠️ Setting up project...${NC}"
python src/setup.py

echo
echo -e "${BLUE}🚀 Starting AI Teddy Bear...${NC}"
echo

# Create logs directory
mkdir -p logs

# Start Backend
echo -e "${GREEN}Starting Backend Server...${NC}"
python src/main.py > logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Wait for backend to start
echo -e "${YELLOW}Waiting for backend to start...${NC}"
sleep 8

# Check if backend is running
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${RED}❌ Backend failed to start. Check logs/backend.log${NC}"
    exit 1
fi

# Start Frontend
echo -e "${GREEN}Starting Frontend Dashboard...${NC}"
cd frontend
npm start > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo "Frontend PID: $FRONTEND_PID"

# Store PIDs for cleanup
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

echo
echo -e "${BLUE}===============================================${NC}"
echo -e "${BLUE} 🎉 AI Teddy Bear is starting!${NC}"
echo -e "${BLUE}===============================================${NC}"
echo -e "${GREEN} 📱 Frontend Dashboard: http://localhost:3000${NC}"
echo -e "${GREEN} 🔗 Backend API: http://localhost:8000${NC}"
echo -e "${GREEN} 📊 Health Check: http://localhost:8000/health${NC}"
echo -e "${BLUE}===============================================${NC}"
echo

# Cleanup function
cleanup() {
    echo
    echo -e "${YELLOW}🛑 Stopping AI Teddy Bear...${NC}"
    
    if [ -f ".backend.pid" ]; then
        BACKEND_PID=$(cat .backend.pid)
        kill $BACKEND_PID 2>/dev/null
        rm .backend.pid
        echo -e "${GREEN}✅ Backend stopped${NC}"
    fi
    
    if [ -f ".frontend.pid" ]; then
        FRONTEND_PID=$(cat .frontend.pid)
        kill $FRONTEND_PID 2>/dev/null
        rm .frontend.pid
        echo -e "${GREEN}✅ Frontend stopped${NC}"
    fi
    
    echo -e "${BLUE}👋 Goodbye!${NC}"
    exit 0
}

# Set trap for cleanup
trap cleanup INT TERM

echo -e "${YELLOW}💡 Tips:${NC}"
echo "- Keep this terminal open"
echo "- Check logs/ folder for detailed logs"
echo "- Press Ctrl+C to stop all services"
echo "- Use 'tail -f logs/backend.log' to monitor backend"
echo "- Use 'tail -f logs/frontend.log' to monitor frontend"
echo

# Wait for services (keep script running)
echo -e "${GREEN}🔄 Services are running... Press Ctrl+C to stop${NC}"
while true; do
    # Check if processes are still running
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo -e "${RED}❌ Backend process died! Check logs/backend.log${NC}"
        cleanup
    fi
    
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo -e "${RED}❌ Frontend process died! Check logs/frontend.log${NC}"
        cleanup
    fi
    
    sleep 5
done 