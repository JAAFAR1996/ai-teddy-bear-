import time
import threading
import sys
import subprocess
import os
import structlog
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

#!/usr/bin/env python3
"""
🧸 AI Teddy Bear - Complete System Launcher
تشغيل النظام الكامل للدبدوب الذكي
"""

logger = structlog.get_logger(__name__)


def start_server() -> Any:
    """تشغيل السيرفر"""
    logger.info("🖥️ Starting Cloud Server...")
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


def start_esp32_simulator() -> Any:
    """تشغيل محاكي ESP32"""
    logger.info("📱 Starting ESP32 Simulator...")
    time.sleep(3)  # انتظار بدء السيرفر

    cmd = [sys.executable, "esp32_simple_simulator.py"]
    process = subprocess.Popen(cmd)
    return process


def main() -> Any:
    logger.info("🧸 AI Teddy Bear - Complete System")
    logger.info("=" * 50)
    logger.info("🎯 Starting both Cloud Server and ESP32 Simulator")
    logger.info("💡 This simulates the complete production environment")
    logger.info("=" * 50)

    try:
        # تشغيل السيرفر في thread منفصل
        server_thread = threading.Thread(target=start_server, daemon=True)
        server_thread.start()

        # انتظار قليل ثم تشغيل المحاكي
        time.sleep(2)

        # تشغيل محاكي ESP32
        esp32_process = start_esp32_simulator()

        logger.info("\n✅ System Started Successfully!")
        logger.info("🖥️ Cloud Server: http://localhost:8000")
        logger.info("📱 ESP32 Simulator: Running in GUI window")
        logger.info("\n💡 Instructions:")
        logger.info("1. Click 'تشغيل الدبدوب' in the ESP32 window")
        logger.info("2. Say 'يا دبدوب' to wake up the teddy")
        logger.info("3. Talk to your AI teddy bear!")
        logger.info("\n🛑 Press Ctrl+C to stop the system")

        # انتظار انتهاء المحاكي
        esp32_process.wait()

    except Exception as e:
    logger.error(f"Error: {e}")"\n👋 Shutting down Teddy Bear system...")
    except Exception as e:
    logger.error(f"Error: {e}")f"❌ Error: {e}")

if __name__ == "__main__":
    main()
