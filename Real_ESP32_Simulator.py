#!/usr/bin/env python3
"""
🧸 Real ESP32 Simulator - AI Teddy Bear
======================================
محاكي ESP32 حقيقي يحاكي الجهاز الفعلي:
- تسجيل صوت من الميكروفون
- إرسال للسيرفر مع UDID فريد  
- استقبال رد صوتي وتشغيله
- جميع وظائف ESP32 الحقيقية
"""

import asyncio
import tkinter as tk
from tkinter import ttk, messagebox
import sounddevice as sd
import soundfile as sf
import numpy as np
import httpx
import json
import uuid
import time
import threading
import tempfile
import os
import pygame
import base64
import io
from datetime import datetime
from typing import Optional, Dict, Any

# إعدادات ESP32 الحقيقية
ESP32_SERVER = "https://ai-teddy-bear.onrender.com"
ESP32_SAMPLE_RATE = 16000
ESP32_CHANNELS = 1
RECORDING_DURATION = 8

class RealESP32Simulator:
    """محاكي ESP32 حقيقي مع جميع الوظائف"""
    
    def __init__(self):
        # UDID فريد لكل جهاز
        self.device_udid = self.generate_device_udid()
        self.server_url = ESP32_SERVER
        self.client = httpx.AsyncClient(timeout=60.0)
        
        # حالة الجهاز
        self.is_powered = False
        self.is_connected = False
        self.is_recording = False
        self.battery_level = 100
        
        # تهيئة الصوت
        pygame.mixer.init()
        
        # إنشاء الواجهة
        self.create_interface()
        
        print(f"🧸 Real ESP32 Simulator Started")
        print(f"🆔 UDID: {self.device_udid}")
    
    def generate_device_udid(self) -> str:
        """توليد UDID فريد مثل ESP32 الحقيقي"""
        # محاكاة ESP32 MAC Address
        mac = uuid.uuid4().hex[:12].upper()
        udid = f"ESP32_TEDDY_{mac[:8]}"
        return udid
    
    def create_interface(self):
        """إنشاء واجهة المحاكي"""
        self.root = tk.Tk()
        self.root.title(f"🧸 Real ESP32 Simulator - {self.device_udid}")
        self.root.geometry("700x800")
        self.root.configure(bg='#1e1e1e')
        
        # العنوان
        title_label = tk.Label(
            self.root,
            text="🧸 ESP32 AI Teddy Bear - Real Hardware Simulation",
            font=('Arial', 16, 'bold'),
            fg='white',
            bg='#1e1e1e'
        )
        title_label.pack(pady=20)
        
        # معلومات الجهاز
        info_frame = tk.Frame(self.root, bg='#2d2d2d', relief='raised', bd=2)
        info_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(
            info_frame,
            text=f"🆔 Device UDID: {self.device_udid}",
            font=('Courier', 12, 'bold'),
            fg='#00ff41',
            bg='#2d2d2d'
        ).pack(pady=10)
        
        tk.Label(
            info_frame,
            text=f"🌐 Server: {self.server_url}",
            font=('Courier', 10),
            fg='#cccccc',
            bg='#2d2d2d'
        ).pack(pady=5)
        
        # حالة الجهاز
        self.status_label = tk.Label(
            self.root,
            text="⚫ ESP32 POWERED OFF",
            font=('Arial', 14, 'bold'),
            fg='#ff4444',
            bg='#1e1e1e'
        )
        self.status_label.pack(pady=20)
        
        # مؤشرات
        indicators_frame = tk.Frame(self.root, bg='#1e1e1e')
        indicators_frame.pack(pady=10)
        
        self.battery_label = tk.Label(
            indicators_frame,
            text=f"🔋 Battery: {self.battery_level}%",
            font=('Arial', 11),
            fg='white',
            bg='#1e1e1e'
        )
        self.battery_label.pack(side='left', padx=20)
        
        # أزرار التحكم
        controls_frame = tk.Frame(self.root, bg='#1e1e1e')
        controls_frame.pack(pady=30)
        
        # زر الطاقة
        self.power_btn = tk.Button(
            controls_frame,
            text="🔌 POWER ON",
            font=('Arial', 12, 'bold'),
            bg='#00aa00',
            fg='white',
            width=15,
            height=2,
            command=self.toggle_power
        )
        self.power_btn.pack(pady=10)
        
        # زر الاتصال
        self.connect_btn = tk.Button(
            controls_frame,
            text="🌐 CONNECT",
            font=('Arial', 12, 'bold'),
            bg='#0066cc',
            fg='white',
            width=15,
            command=self.connect_server,
            state='disabled'
        )
        self.connect_btn.pack(pady=5)
        
        # زر التسجيل الرئيسي
        self.record_btn = tk.Button(
            controls_frame,
            text="🎤 RECORD VOICE",
            font=('Arial', 14, 'bold'),
            bg='#cc0000',
            fg='white',
            width=15,
            height=3,
            command=self.start_recording,
            state='disabled'
        )
        self.record_btn.pack(pady=15)
        
        # منطقة السجل
        log_label = tk.Label(
            self.root,
            text="📋 Activity Log:",
            font=('Arial', 12, 'bold'),
            fg='white',
            bg='#1e1e1e'
        )
        log_label.pack(anchor='w', padx=20, pady=(20, 5))
        
        self.log_text = tk.Text(
            self.root,
            height=15,
            width=80,
            font=('Courier', 9),
            bg='#000000',
            fg='#00ff41',
            insertbackground='white'
        )
        self.log_text.pack(padx=20, pady=10, fill='both', expand=True)
        
        # رسائل البداية
        self.log("🧸 ESP32 Real Simulator Initialized")
        self.log(f"🆔 Device UDID: {self.device_udid}")
        self.log("💡 Click 'POWER ON' to start ESP32")
    
    def log(self, message: str):
        """إضافة رسالة للسجل"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        print(log_entry.strip())
    
    def toggle_power(self):
        """تبديل الطاقة"""
        if not self.is_powered:
            self.power_on()
        else:
            self.power_off()
    
    def power_on(self):
        """تشغيل ESP32"""
        self.is_powered = True
        
        self.power_btn.config(text="🔌 POWER OFF", bg='#cc0000')
        self.connect_btn.config(state='normal')
        self.status_label.config(text="✅ ESP32 POWERED ON", fg='#00ff41')
        
        self.log("✅ ESP32 Hardware Powered ON")
        self.log("🔌 WiFi module initializing...")
        self.log("🎤 Microphone ready")
        self.log("🔊 Speaker ready")
        self.log("🌐 Ready to connect to server")
        
        # بدء مراقبة البطارية
        self.start_battery_monitor()
    
    def power_off(self):
        """إطفاء ESP32"""
        self.is_powered = False
        self.is_connected = False
        
        self.power_btn.config(text="🔌 POWER ON", bg='#00aa00')
        self.connect_btn.config(state='disabled')
        self.record_btn.config(state='disabled')
        self.status_label.config(text="⚫ ESP32 POWERED OFF", fg='#ff4444')
        
        self.log("🔴 ESP32 Hardware Powered OFF")
    
    def start_battery_monitor(self):
        """مراقبة البطارية"""
        def monitor():
            while self.is_powered:
                time.sleep(10)
                self.battery_level = max(0, self.battery_level - 1)
                self.battery_label.config(text=f"🔋 Battery: {self.battery_level}%")
                
                if self.battery_level <= 20:
                    self.log(f"⚠️ Low Battery Warning: {self.battery_level}%")
        
        threading.Thread(target=monitor, daemon=True).start()
    
    def connect_server(self):
        """الاتصال بالسيرفر"""
        self.status_label.config(text="🔄 CONNECTING...", fg='#ffaa00')
        self.log("🔄 Attempting connection to AI server...")
        
        threading.Thread(target=self.do_connection, daemon=True).start()
    
    def do_connection(self):
        """تنفيذ الاتصال"""
        try:
            async def connect():
                # اختبار الاتصال
                response = await self.client.get(f"{self.server_url}/esp32/connect")
                if response.status_code == 200:
                    # تسجيل الجهاز
                    register_data = {
                        "device_id": self.device_udid,
                        "status": "online",
                        "last_seen": datetime.now().isoformat(),
                        "battery_level": self.battery_level,
                        "wifi_strength": -45
                    }
                    
                    await self.client.post(f"{self.server_url}/esp32/status", json=register_data)
                    return True, response.json()
                return False, f"HTTP {response.status_code}"
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success, data = loop.run_until_complete(connect())
            loop.close()
            
            self.root.after(0, self.connection_result, success, data)
            
        except Exception as e:
            self.root.after(0, self.connection_result, False, str(e))
    
    def connection_result(self, success: bool, data: Any):
        """نتيجة الاتصال"""
        if success:
            self.is_connected = True
            self.status_label.config(text="🌐 CONNECTED TO AI", fg='#00ff41')
            self.record_btn.config(state='normal')
            
            self.log("✅ Successfully connected to AI server")
            self.log("📡 Device registered with server")
            self.log("🎤 Voice recording enabled")
            self.log("👶 Ready for child interaction!")
            
        else:
            self.status_label.config(text="❌ CONNECTION FAILED", fg='#ff4444')
            self.log(f"❌ Connection failed: {data}")
    
    def start_recording(self):
        """بدء تسجيل الصوت"""
        if self.is_recording:
            return
        
        self.log("🎤 Starting voice recording...")
        self.record_btn.config(text="⏹️ RECORDING...", bg='#ff6600')
        self.status_label.config(text="🎤 RECORDING VOICE", fg='#ff6600')
        
        threading.Thread(target=self.record_audio, daemon=True).start()
    
    def record_audio(self):
        """تسجيل الصوت الحقيقي"""
        try:
            self.is_recording = True
            self.log(f"🎤 Recording {RECORDING_DURATION}s audio at {ESP32_SAMPLE_RATE}Hz...")
            
            # تسجيل صوت حقيقي من الميكروفون
            audio_data = sd.rec(
                int(RECORDING_DURATION * ESP32_SAMPLE_RATE),
                samplerate=ESP32_SAMPLE_RATE,
                channels=ESP32_CHANNELS,
                dtype='int16'
            )
            
            # انتظار انتهاء التسجيل
            sd.wait()
            
            self.root.after(0, self.recording_done)
            
            # حفظ في ملف مؤقت
            temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            sf.write(temp_file.name, audio_data, ESP32_SAMPLE_RATE)
            
            self.log("💾 Audio recorded, preparing to send...")
            
            # إرسال للسيرفر
            self.send_to_server(temp_file.name)
            
            # حذف الملف
            os.unlink(temp_file.name)
            
        except Exception as e:
            self.log(f"❌ Recording error: {e}")
            self.root.after(0, self.recording_done)
        finally:
            self.is_recording = False
    
    def recording_done(self):
        """انتهاء التسجيل"""
        self.record_btn.config(text="🎤 RECORD VOICE", bg='#cc0000')
        self.status_label.config(text="📤 SENDING TO AI...", fg='#ffaa00')
    
    def send_to_server(self, audio_file: str):
        """إرسال الصوت للسيرفر"""
        try:
            async def upload():
                with open(audio_file, 'rb') as f:
                    files = {'audio_file': ('voice.wav', f, 'audio/wav')}
                    data = {'device_id': self.device_udid}
                    
                    response = await self.client.post(
                        f"{self.server_url}/api/audio/upload",
                        files=files,
                        data=data
                    )
                    
                    return response.status_code == 200, response.json() if response.status_code == 200 else response.text
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success, result = loop.run_until_complete(upload())
            loop.close()
            
            self.root.after(0, self.server_response, success, result)
            
        except Exception as e:
            self.root.after(0, self.server_response, False, str(e))
    
    def server_response(self, success: bool, result: Any):
        """رد السيرفر"""
        if success and isinstance(result, dict):
            self.log("✅ Server processed audio successfully")
            
            # الحصول على الرد
            ai_response = result.get('ai_response', {})
            text = ai_response.get('text', 'No response')
            audio_response = result.get('response_audio')
            
            self.log(f"🧸 AI Response: {text[:100]}...")
            
            # تشغيل الصوت
            if audio_response:
                self.play_audio_response(audio_response)
            else:
                self.log("⚠️ No audio response received")
                self.ready_for_next()
            
        else:
            self.log(f"❌ Server error: {result}")
            self.status_label.config(text="❌ SERVER ERROR", fg='#ff4444')
    
    def play_audio_response(self, audio_base64: str):
        """تشغيل الرد الصوتي"""
        try:
            self.status_label.config(text="🔊 PLAYING RESPONSE", fg='#9900ff')
            self.log("🔊 Playing AI response audio...")
            
            # فك الترميز
            audio_data = base64.b64decode(audio_base64)
            
            # حفظ وتشغيل
            temp_audio = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
            temp_audio.write(audio_data)
            temp_audio.close()
            
            pygame.mixer.music.load(temp_audio.name)
            pygame.mixer.music.play()
            
            # انتظار انتهاء التشغيل
            def wait_playback():
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                os.unlink(temp_audio.name)
                self.root.after(0, self.ready_for_next)
            
            threading.Thread(target=wait_playback, daemon=True).start()
            
        except Exception as e:
            self.log(f"❌ Audio playback error: {e}")
            self.ready_for_next()
    
    def ready_for_next(self):
        """جاهز للتفاعل التالي"""
        self.status_label.config(text="🌐 READY FOR VOICE", fg='#00ff41')
        self.log("✅ Ready for next voice interaction")
    
    async def cleanup(self):
        """تنظيف الموارد"""
        await self.client.aclose()
    
    def on_close(self):
        """عند الإغلاق"""
        try:
            asyncio.run(self.cleanup())
        except:
            pass
        self.root.destroy()
    
    def run(self):
        """تشغيل المحاكي"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.log("=" * 60)
        self.log("🧸 ESP32 AI TEDDY BEAR - REAL HARDWARE SIMULATION")
        self.log("=" * 60)
        self.log("📋 Instructions:")
        self.log("1. Click 'POWER ON' to boot ESP32")
        self.log("2. Click 'CONNECT' to connect to AI server")
        self.log("3. Click 'RECORD VOICE' and speak to microphone")
        self.log("4. Listen to AI response from speaker")
        self.log("=" * 60)
        
        self.root.mainloop()


if __name__ == "__main__":
    print("🚀 Starting Real ESP32 Simulator...")
    
    # فحص المكتبات
    required = ['sounddevice', 'soundfile', 'pygame', 'httpx', 'numpy']
    missing = []
    
    for module in required:
        try:
            __import__(module)
        except ImportError:
            missing.append(module)
    
    if missing:
        print(f"❌ Missing: {', '.join(missing)}")
        print("📦 Installing...")
        
        import subprocess
        import sys
        
        for module in missing:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", module])
            except:
                print(f"❌ Failed to install {module}")
                print(f"Please run: pip install {module}")
                exit(1)
    
    # تشغيل المحاكي
    try:
        simulator = RealESP32Simulator()
        simulator.run()
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Check microphone permissions and audio drivers") 