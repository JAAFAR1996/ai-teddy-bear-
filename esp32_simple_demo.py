#!/usr/bin/env python3
"""
🧸 ESP32 Simple Demo - Quick Working Simulator
محاكي ESP32 بسيط وسريع للتجربة السريعة
"""
import asyncio
import json
import time
import requests
from datetime import datetime
from typing import Dict, Any

# Configuration
SERVER_URL = "http://localhost:8000"
DEVICE_ID = "ESP32_SIMPLE_001"

class ESP32SimpleSimulator:
    """محاكي ESP32 بسيط للتجربة السريعة"""
    
    def __init__(self):
        self.device_id = DEVICE_ID
        self.is_connected = False
        self.child_id = None
        
    def log(self, message: str, level: str = "INFO"):
        """طباعة رسالة مع الوقت"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level}] 🧸 {message}")
    
    def check_server(self) -> bool:
        """فحص اتصال الخادم"""
        try:
            response = requests.get(f"{SERVER_URL}/health", timeout=5)
            if response.status_code == 200:
                self.log("✅ Server is running and healthy")
                return True
            else:
                self.log(f"❌ Server responded with status: {response.status_code}", "ERROR")
                return False
        except requests.exceptions.ConnectionError:
            self.log("❌ Cannot connect to server - make sure it's running", "ERROR")
            return False
        except Exception as e:
            self.log(f"❌ Server check failed: {e}", "ERROR")
            return False
    
    def register_device(self) -> bool:
        """تسجيل الجهاز"""
        try:
            data = {
                "device_id": self.device_id,
                "child_name": "تجربة",
                "child_age": 6
            }
            
            response = requests.post(f"{SERVER_URL}/api/device/register", json=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                self.child_id = result.get("child_id")
                self.is_connected = True
                self.log(f"✅ Device registered successfully!")
                self.log(f"👶 Child ID: {self.child_id}")
                return True
            else:
                self.log(f"❌ Registration failed: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Registration error: {e}", "ERROR")
            return False
    
    def send_message(self, message: str) -> Dict[str, Any]:
        """إرسال رسالة للخادم"""
        if not self.is_connected:
            self.log("❌ Device not connected!", "ERROR")
            return {}
        
        try:
            data = {
                "child_id": self.child_id,
                "message": message
            }
            
            self.log(f"📤 Sending: {message}")
            response = requests.post(f"{SERVER_URL}/api/conversations", json=data, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get("response", "No response")
                emotion = result.get("emotion", "unknown")
                
                self.log(f"📥 AI Response: {ai_response}")
                self.log(f"😊 Detected Emotion: {emotion}")
                
                return result
            else:
                self.log(f"❌ Message failed: {response.status_code}", "ERROR")
                return {}
                
        except Exception as e:
            self.log(f"❌ Send error: {e}", "ERROR")
            return {}
    
    def run_demo(self):
        """تشغيل العرض التوضيحي"""
        print("=" * 60)
        print("🧸 ESP32 Simple Simulator - Quick Demo")
        print("=" * 60)
        
        # فحص الخادم
        self.log("🔍 Checking server connection...")
        if not self.check_server():
            self.log("💡 Make sure to run: python simple_backend.py", "INFO")
            return
        
        # تسجيل الجهاز
        self.log("📡 Registering device...")
        if not self.register_device():
            return
        
        # رسائل تجريبية
        demo_messages = [
            "مرحباً دبدوبي",
            "كيف حالك اليوم؟",
            "أريد أن ألعب معك",
            "هل يمكنك أن تحكي لي قصة؟",
            "ما هو لونك المفضل؟"
        ]
        
        self.log("🎮 Starting conversation demo...")
        print()
        
        for i, message in enumerate(demo_messages, 1):
            self.log(f"--- Message {i}/{len(demo_messages)} ---")
            self.send_message(message)
            print()
            time.sleep(2)  # وقفة بين الرسائل
        
        # عرض الإحصائيات
        self.log("📊 Getting analytics...")
        try:
            response = requests.get(f"{SERVER_URL}/api/analytics/emotions?child_id={self.child_id}")
            if response.status_code == 200:
                analytics = response.json()
                emotions = analytics.get("emotions", {})
                total = analytics.get("total_interactions", 0)
                
                self.log(f"📈 Total interactions: {total}")
                self.log("😊 Emotion breakdown:")
                for emotion, percentage in emotions.items():
                    self.log(f"   • {emotion}: {percentage}%")
        except:
            self.log("⚠️ Could not get analytics", "WARN")
        
        print()
        self.log("🎉 Demo completed successfully!")
        self.log("💡 The ESP32 simulator can now communicate with the AI server")
        print("=" * 60)

def main():
    """نقطة البدء الرئيسية"""
    try:
        simulator = ESP32SimpleSimulator()
        simulator.run_demo()
    except KeyboardInterrupt:
        print("\n👋 Demo stopped by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")

if __name__ == "__main__":
    main() 