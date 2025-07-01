#!/bin/bash

# Colors for output
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}===============================================${NC}"
echo -e "${BLUE} 🎬 AI Teddy Bear - Complete Demo Experience${NC}"
echo -e "${BLUE}===============================================${NC}"
echo

echo -e "${CYAN}🎯 This demo will showcase the full AI Teddy Bear system${NC}"
echo -e "${CYAN}   without requiring any ESP32 hardware!${NC}"
echo
echo -e "${YELLOW}What you'll experience:${NC}"
echo -e "${GREEN}✨ Real AI conversation simulation${NC}"
echo -e "${GREEN}✨ Parent dashboard with live metrics${NC}"  
echo -e "${GREEN}✨ Voice recording and AI responses${NC}"
echo -e "${GREEN}✨ Safety monitoring and content filtering${NC}"
echo -e "${GREEN}✨ Multiple child profiles and interactions${NC}"
echo

read -p "Press Enter to start the complete demo..."

echo
echo -e "${YELLOW}🔄 Starting complete demo sequence...${NC}"
echo

# Check if system is running
echo -e "${CYAN}📡 Checking system status...${NC}"
if curl -s http://localhost:8000/health >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend is already running!${NC}"
else
    echo -e "${YELLOW}⚠️ Backend not running. Starting system first...${NC}"
    ./start_teddy.sh &
    sleep 10
fi

echo
echo -e "${PURPLE}🎮 Step 1: Starting ESP32 Simulator...${NC}"
gnome-terminal --title="ESP32 Simulator" -- bash -c "python src/simulators/esp32_production_simulator.py; exec bash" 2>/dev/null || \
xterm -title "ESP32 Simulator" -e "python src/simulators/esp32_production_simulator.py" 2>/dev/null || \
python src/simulators/esp32_production_simulator.py &

sleep 3

echo
echo -e "${PURPLE}📊 Step 2: Starting Dashboard Demo...${NC}"
gnome-terminal --title="Dashboard Demo" -- bash -c "python src/dashboards/dashboard-demo-runner.py; exec bash" 2>/dev/null || \
xterm -title "Dashboard Demo" -e "python src/dashboards/dashboard-demo-runner.py" 2>/dev/null || \
python src/dashboards/dashboard-demo-runner.py &

sleep 3

echo
echo -e "${PURPLE}🤖 Step 3: Starting AI Testing Demo...${NC}"
gnome-terminal --title="AI Testing Demo" -- bash -c "python tests/ai_test_demo.py; exec bash" 2>/dev/null || \
xterm -title "AI Testing Demo" -e "python tests/ai_test_demo.py" 2>/dev/null || \
python tests/ai_test_demo.py &

sleep 3

echo
echo -e "${PURPLE}📈 Step 4: Starting Observability Demo...${NC}"
gnome-terminal --title="Observability Demo" -- bash -c "python src/infrastructure/observability/observability_demo.py; exec bash" 2>/dev/null || \
xterm -title "Observability Demo" -e "python src/infrastructure/observability/observability_demo.py" 2>/dev/null || \
python src/infrastructure/observability/observability_demo.py &

echo
echo -e "${CYAN}🌐 Step 5: Opening web interfaces...${NC}"
sleep 5

# Open web interfaces (try different browsers)
if command -v xdg-open >/dev/null; then
    xdg-open http://localhost:3000 >/dev/null 2>&1
    echo -e "${GREEN}   📱 Parent Dashboard opened${NC}"
    
    sleep 2
    xdg-open http://localhost:8000/docs >/dev/null 2>&1
    echo -e "${GREEN}   📚 API Documentation opened${NC}"
    
    sleep 2
    xdg-open http://localhost:8000/health >/dev/null 2>&1
    echo -e "${GREEN}   ❤️ Health Check opened${NC}"
elif command -v open >/dev/null; then  # macOS
    open http://localhost:3000
    echo -e "${GREEN}   📱 Parent Dashboard opened${NC}"
    
    sleep 2
    open http://localhost:8000/docs
    echo -e "${GREEN}   📚 API Documentation opened${NC}"
    
    sleep 2
    open http://localhost:8000/health
    echo -e "${GREEN}   ❤️ Health Check opened${NC}"
else
    echo -e "${YELLOW}   🌐 Manually open these URLs:${NC}"
    echo -e "${CYAN}   📱 http://localhost:3000${NC}"
    echo -e "${CYAN}   📚 http://localhost:8000/docs${NC}"
    echo -e "${CYAN}   ❤️ http://localhost:8000/health${NC}"
fi

echo
echo -e "${BLUE}===============================================${NC}"
echo -e "${BLUE} 🎉 COMPLETE DEMO IS NOW RUNNING!${NC}"
echo -e "${BLUE}===============================================${NC}"
echo
echo -e "${YELLOW}🎮 ESP32 Simulator:${NC}"
echo -e "${GREEN}   - Connect to server${NC}"
echo -e "${GREEN}   - Setup child profile${NC}"
echo -e "${GREEN}   - Try voice recording!${NC}"
echo
echo -e "${YELLOW}📊 Dashboard Demo:${NC}"
echo -e "${GREEN}   - Watch live metrics${NC}"
echo -e "${GREEN}   - See safety scores${NC}"
echo -e "${GREEN}   - Monitor conversations${NC}"
echo
echo -e "${YELLOW}🌐 Web Interfaces:${NC}"
echo -e "${CYAN}   📱 Parent Dashboard: http://localhost:3000${NC}"
echo -e "${CYAN}   📚 API Docs: http://localhost:8000/docs${NC}"
echo -e "${CYAN}   ❤️ Health: http://localhost:8000/health${NC}"
echo
echo -e "${PURPLE}💡 Demo Tips:${NC}"
echo -e "${GREEN}   1. Start with ESP32 Simulator - connect and setup profile${NC}"
echo -e "${GREEN}   2. Use \"Hold to Talk\" to record voice messages${NC}"
echo -e "${GREEN}   3. Watch Dashboard for real-time metrics${NC}"
echo -e "${GREEN}   4. Check web interfaces for detailed views${NC}"
echo -e "${GREEN}   5. Let demos run for 5-10 minutes for full experience${NC}"
echo
echo -e "${RED}⚠️ To stop all demos: run ./stop_teddy.sh${NC}"
echo

read -p "Press Enter to continue..."

echo
echo -e "${CYAN}🎊 Demo Experience Guide:${NC}"
echo -e "${BLUE}========================================${NC}"
echo
echo -e "${YELLOW}🎤 Voice Interaction Test:${NC}"
echo -e "${GREEN}   1. Open ESP32 Simulator window${NC}"
echo -e "${GREEN}   2. Click \"Connect to Server\"${NC}"
echo -e "${GREEN}   3. Click \"Setup Child Profile\"${NC}"
echo -e "${GREEN}   4. Hold \"🎤 Hold to Talk\" and say:${NC}"
echo -e "${CYAN}      • \"مرحبا دبدوب\" (Hello Teddy)${NC}"
echo -e "${CYAN}      • \"احكي لي قصة\" (Tell me a story)${NC}"
echo -e "${CYAN}      • \"كيف حالك؟\" (How are you?)${NC}"
echo -e "${GREEN}   5. Watch AI respond in real-time!${NC}"
echo
echo -e "${YELLOW}📊 Dashboard Monitoring:${NC}"
echo -e "${GREEN}   1. Check Dashboard Demo terminal${NC}"
echo -e "${GREEN}   2. See live safety scores${NC}"
echo -e "${GREEN}   3. Monitor conversation growth${NC}"
echo -e "${GREEN}   4. Watch system health metrics${NC}"
echo
echo -e "${YELLOW}🏆 Expected Results:${NC}"
echo -e "${GREEN}   ✅ ESP32 connects successfully${NC}"
echo -e "${GREEN}   ✅ Voice is recorded and processed${NC}"
echo -e "${GREEN}   ✅ AI generates appropriate responses${NC}"
echo -e "${GREEN}   ✅ Safety filters work correctly${NC}"
echo -e "${GREEN}   ✅ All metrics update in real-time${NC}"
echo -e "${GREEN}   ✅ Parent dashboard shows activity${NC}"
echo

read -p "Press Enter to finish..."

echo
echo -e "${PURPLE}🎯 Your AI Teddy Bear system is now fully demonstrated!${NC}"
echo -e "${BLUE}🚀 Ready for real ESP32 hardware integration!${NC}"
echo -e "${YELLOW}💫 Perfect for showcasing to stakeholders and investors!${NC}"
echo 