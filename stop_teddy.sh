#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}===============================================${NC}"
echo -e "${BLUE} 🛑 AI Teddy Bear - Stop Services (Mac/Linux)${NC}"
echo -e "${BLUE}===============================================${NC}"
echo

echo -e "${YELLOW}Stopping AI Teddy Bear services...${NC}"
echo

# Stop processes using PID files if they exist
if [ -f ".backend.pid" ]; then
    BACKEND_PID=$(cat .backend.pid)
    if kill -0 $BACKEND_PID 2>/dev/null; then
        echo -e "${YELLOW}Stopping Backend service (PID: $BACKEND_PID)${NC}"
        kill $BACKEND_PID
        sleep 2
        # Force kill if still running
        if kill -0 $BACKEND_PID 2>/dev/null; then
            kill -9 $BACKEND_PID 2>/dev/null
        fi
    fi
    rm .backend.pid
    echo -e "${GREEN}✅ Backend stopped${NC}"
fi

if [ -f ".frontend.pid" ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        echo -e "${YELLOW}Stopping Frontend service (PID: $FRONTEND_PID)${NC}"
        kill $FRONTEND_PID
        sleep 2
        # Force kill if still running
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            kill -9 $FRONTEND_PID 2>/dev/null
        fi
    fi
    rm .frontend.pid
    echo -e "${GREEN}✅ Frontend stopped${NC}"
fi

# Stop processes on common ports as fallback
echo -e "${YELLOW}🔍 Checking for remaining services...${NC}"

# Stop processes on port 8000 (Backend)
BACKEND_PIDS=$(lsof -ti :8000 2>/dev/null)
if [ ! -z "$BACKEND_PIDS" ]; then
    echo -e "${YELLOW}Stopping Backend processes on port 8000${NC}"
    echo $BACKEND_PIDS | xargs kill 2>/dev/null
    sleep 2
    # Force kill if still running
    BACKEND_PIDS=$(lsof -ti :8000 2>/dev/null)
    if [ ! -z "$BACKEND_PIDS" ]; then
        echo $BACKEND_PIDS | xargs kill -9 2>/dev/null
    fi
fi

# Stop processes on port 3000 (Frontend)
FRONTEND_PIDS=$(lsof -ti :3000 2>/dev/null)
if [ ! -z "$FRONTEND_PIDS" ]; then
    echo -e "${YELLOW}Stopping Frontend processes on port 3000${NC}"
    echo $FRONTEND_PIDS | xargs kill 2>/dev/null
    sleep 2
    # Force kill if still running
    FRONTEND_PIDS=$(lsof -ti :3000 2>/dev/null)
    if [ ! -z "$FRONTEND_PIDS" ]; then
        echo $FRONTEND_PIDS | xargs kill -9 2>/dev/null
    fi
fi

# Stop processes on port 8765 (WebSocket)
WS_PIDS=$(lsof -ti :8765 2>/dev/null)
if [ ! -z "$WS_PIDS" ]; then
    echo -e "${YELLOW}Stopping WebSocket processes on port 8765${NC}"
    echo $WS_PIDS | xargs kill 2>/dev/null
    sleep 2
    # Force kill if still running
    WS_PIDS=$(lsof -ti :8765 2>/dev/null)
    if [ ! -z "$WS_PIDS" ]; then
        echo $WS_PIDS | xargs kill -9 2>/dev/null
    fi
fi

# Stop any remaining Python main.py processes
PYTHON_PIDS=$(pgrep -f "python.*main.py" 2>/dev/null)
if [ ! -z "$PYTHON_PIDS" ]; then
    echo -e "${YELLOW}Stopping Python main.py processes${NC}"
    echo $PYTHON_PIDS | xargs kill 2>/dev/null
    sleep 2
    # Force kill if still running
    PYTHON_PIDS=$(pgrep -f "python.*main.py" 2>/dev/null)
    if [ ! -z "$PYTHON_PIDS" ]; then
        echo $PYTHON_PIDS | xargs kill -9 2>/dev/null
    fi
fi

# Stop any remaining npm start processes
NPM_PIDS=$(pgrep -f "npm.*start" 2>/dev/null)
if [ ! -z "$NPM_PIDS" ]; then
    echo -e "${YELLOW}Stopping npm start processes${NC}"
    echo $NPM_PIDS | xargs kill 2>/dev/null
    sleep 2
    # Force kill if still running
    NPM_PIDS=$(pgrep -f "npm.*start" 2>/dev/null)
    if [ ! -z "$NPM_PIDS" ]; then
        echo $NPM_PIDS | xargs kill -9 2>/dev/null
    fi
fi

echo
echo -e "${GREEN}✅ All AI Teddy Bear services have been stopped!${NC}"
echo -e "${BLUE}👋 Goodbye!${NC}" 