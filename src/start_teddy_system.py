#!/usr/bin/env python3
"""
🧸 AI Teddy Bear - Complete System Launcher
تشغيل النظام الكامل للدبدوب الذكي
"""
import structlog
logger = structlog.get_logger(__name__)


import subprocess
import threading
import time
import sys
import os

def start_server():
    """تشغيل السيرفر"""
    print("🖥️ Starting Cloud Server...")
    cmd = [sys.executable, "production_teddy_system.py"]
    
    # تمرير الخيار "1" للسيرفر
    process = subprocess.Popen(
        cmd, 
        stdin=subprocess.PIPE, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE,
        text=True
    )
    
    # إرسال "1" لاختيار السيرفر
    process.stdin.write("1\n")
    process.stdin.flush()
    
    return process

def start_esp32_simulator():
    """تشغيل محاكي ESP32"""
    print("📱 Starting ESP32 Simulator...")
    time.sleep(3)  # انتظار بدء السيرفر
    
    cmd = [sys.executable, "esp32_simple_simulator.py"]
    process = subprocess.Popen(cmd)
    return process

def main():
    print("🧸 AI Teddy Bear - Complete System")
    print("=" * 50)
    print("🎯 Starting both Cloud Server and ESP32 Simulator")
    print("💡 This simulates the complete production environment")
    print("=" * 50)
    
    try:
        # تشغيل السيرفر في thread منفصل
        server_thread = threading.Thread(target=start_server, daemon=True)
        server_thread.start()
        
        # انتظار قليل ثم تشغيل المحاكي
        time.sleep(2)
        
        # تشغيل محاكي ESP32
        esp32_process = start_esp32_simulator()
        
        print("\n✅ System Started Successfully!")
        print("🖥️ Cloud Server: http://localhost:8000")
        print("📱 ESP32 Simulator: Running in GUI window")
        print("\n💡 Instructions:")
        print("1. Click 'تشغيل الدبدوب' in the ESP32 window")
        print("2. Say 'يا دبدوب' to wake up the teddy")
        print("3. Talk to your AI teddy bear!")
        print("\n🛑 Press Ctrl+C to stop the system")
        
        # انتظار انتهاء المحاكي
        esp32_process.wait()
        
    except Exception as e:
    logger.error(f"Error: {e}")"\n👋 Shutting down Teddy Bear system...")
    except Exception as e:
    logger.error(f"Error: {e}")f"❌ Error: {e}")

if __name__ == "__main__":
    main() 