#!/usr/bin/env python3
"""
🧸 ESP32 Real Simulator - AI Teddy Bear Project
===============================================
محاكي ESP32 حقيقي يحاكي الجهاز الفعلي بالضبط:
- تسجيل صوت حقيقي من الميكروفون
- إرسال للسيرفر مع UDID فريد
- استقبال الرد الصوتي وتشغيله
- جميع ميزات ESP32 الحقيقية
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
import speech_recognition as sr

# إعدادات ESP32
ESP32_SERVER_URL = "https://ai-teddy-bear.onrender.com"
ESP32_SAMPLE_RATE = 16000  # 16kHz مثل ESP32 الحقيقي
ESP32_CHANNELS = 1  # Mono
ESP32_DTYPE = 'int16'
CHUNK_SIZE = 1024

class ESP32TeddySimulator:
    """
    محاكي ESP32 الحقيقي للدبدوب الذكي
    ===================================
    يحاكي بالضبط ما يحدث في ESP32 الحقيقي:
    1. تسجيل صوت من الميكروفون
    2. إرسال للسيرفر مع UDID
    3. استقبال الرد الصوتي
    4. تشغيل الصوت للطفل
    """
    
    def __init__(self):
        # UDID فريد لكل جهاز (مثل ESP32 الحقيقي)
        self.device_udid = self.generate_udid()
        self.server_url = ESP32_SERVER_URL
        self.client = httpx.AsyncClient(timeout=60.0)
        
        # حالة ESP32
        self.is_powered = False
        self.is_connected = False
        self.is_recording = False
        self.is_playing = False
        self.battery_level = 100
        self.wifi_signal = -45
        
        # إعدادات الصوت
        self.sample_rate = ESP32_SAMPLE_RATE
        self.channels = ESP32_CHANNELS
        self.recording_duration = 10  # ثواني
        
        # تهيئة pygame للصوت
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        # إنشاء الواجهة
        self.create_gui()
        
        print(f"🧸 ESP32 Real Simulator Started")
        print(f"🆔 Device UDID: {self.device_udid}")
        print(f"🌐 Server: {self.server_url}")
    
    def generate_udid(self) -> str:
        """توليد UDID فريد للجهاز (مثل ESP32 الحقيقي)"""
        # محاكاة MAC address ESP32
        mac_part = uuid.uuid4().hex[:12].upper()
        # تنسيق مثل ESP32: TEDDY_XXXXXX
        udid = f"TEDDY_{mac_part[:8]}"
        return udid
    
    def create_gui(self):
        """إنشاء واجهة المحاكي"""
        self.root = tk.Tk()
        self.root.title(f"🧸 ESP32 Real Simulator - {self.device_udid}")
        self.root.geometry("600x700")
        self.root.configure(bg='#1a1a1a')
        
        # العنوان
        title_frame = tk.Frame(self.root, bg='#2d2d2d', height=80)
        title_frame.pack(fill='x', pady=5)
        title_frame.pack_propagate(False)
        
        tk.Label(
            title_frame,
            text="🧸 ESP32 AI Teddy Bear - Real Hardware Simulation",
            font=('Arial', 16, 'bold'),
            fg='white',
            bg='#2d2d2d'
        ).pack(pady=20)
        
        # معلومات الجهاز
        info_frame = tk.Frame(self.root, bg='#333333', relief='raised', bd=2)
        info_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(
            info_frame,
            text=f"🆔 Device UDID: {self.device_udid}",
            font=('Courier', 12, 'bold'),
            fg='#00ff00',
            bg='#333333'
        ).pack(pady=5)
        
        tk.Label(
            info_frame,
            text=f"🌐 Server: {self.server_url}",
            font=('Courier', 10),
            fg='#cccccc',
            bg='#333333'
        ).pack(pady=2)
        
        # حالة ESP32
        self.status_frame = tk.Frame(self.root, bg='#444444', relief='sunken', bd=2)
        self.status_frame.pack(fill='x', padx=10, pady=10)
        
        self.status_label = tk.Label(
            self.status_frame,
            text="⭕ ESP32 POWERED OFF",
            font=('Arial', 14, 'bold'),
            fg='#ff4444',
            bg='#444444'
        )
        self.status_label.pack(pady=10)
        
        # مؤشرات الجهاز
        indicators_frame = tk.Frame(self.root, bg='#555555')
        indicators_frame.pack(fill='x', padx=10, pady=5)
        
        # البطارية
        self.battery_label = tk.Label(
            indicators_frame,
            text=f"🔋 Battery: {self.battery_level}%",
            font=('Arial', 10),
            fg='white',
            bg='#555555'
        )
        self.battery_label.pack(side='left', padx=10)
        
        # WiFi
        self.wifi_label = tk.Label(
            indicators_frame,
            text=f"📶 WiFi: {self.wifi_signal}dBm",
            font=('Arial', 10),
            fg='white',
            bg='#555555'
        )
        self.wifi_label.pack(side='right', padx=10)
        
        # أزرار التحكم
        controls_frame = tk.Frame(self.root, bg='#1a1a1a')
        controls_frame.pack(pady=20)
        
        # زر الطاقة
        self.power_button = tk.Button(
            controls_frame,
            text="🔌 POWER ON ESP32",
            font=('Arial', 12, 'bold'),
            bg='#007700',
            fg='white',
            width=20,
            height=2,
            command=self.toggle_power
        )
        self.power_button.pack(pady=10)
        
        # زر الاتصال
        self.connect_button = tk.Button(
            controls_frame,
            text="🌐 CONNECT TO SERVER",
            font=('Arial', 12, 'bold'),
            bg='#0066cc',
            fg='white',
            width=20,
            command=self.connect_to_server,
            state='disabled'
        )
        self.connect_button.pack(pady=5)
        
        # زر التسجيل (الزر الرئيسي)
        self.record_button = tk.Button(
            controls_frame,
            text="🎤 START VOICE RECORDING",
            font=('Arial', 12, 'bold'),
            bg='#cc3300',
            fg='white',
            width=20,
            height=3,
            command=self.start_voice_interaction,
            state='disabled'
        )
        self.record_button.pack(pady=10)
        
        # منطقة المعلومات
        self.info_text = tk.Text(
            self.root,
            height=15,
            width=70,
            font=('Courier', 9),
            bg='#000000',
            fg='#00ff00',
            insertbackground='white'
        )
        self.info_text.pack(padx=10, pady=10, fill='both', expand=True)
        
        # إضافة رسالة ترحيب
        self.log("🧸 ESP32 AI Teddy Bear Simulator Started")
        self.log(f"🆔 Device UDID: {self.device_udid}")
        self.log("💡 Click 'POWER ON ESP32' to start")
    
    def log(self, message: str):
        """إضافة رسالة لسجل المعلومات"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        self.info_text.insert(tk.END, log_message)
        self.info_text.see(tk.END)
        print(log_message.strip())
    
    def toggle_power(self):
        """تبديل حالة الطاقة"""
        if not self.is_powered:
            self.power_on()
        else:
            self.power_off()
    
    def power_on(self):
        """تشغيل ESP32"""
        self.is_powered = True
        
        # تحديث الواجهة
        self.power_button.config(text="🔌 POWER OFF ESP32", bg='#cc0000')
        self.connect_button.config(state='normal')
        self.status_label.config(text="✅ ESP32 POWERED ON - Ready", fg='#00ff00')
        
        # بدء مراقبة البطارية
        self.start_battery_monitor()
        
        self.log("✅ ESP32 powered ON")
        self.log("🌐 Click 'CONNECT TO SERVER' to connect to cloud")
    
    def power_off(self):
        """إطفاء ESP32"""
        self.is_powered = False
        self.is_connected = False
        
        # تحديث الواجهة
        self.power_button.config(text="🔌 POWER ON ESP32", bg='#007700')
        self.connect_button.config(state='disabled')
        self.record_button.config(state='disabled')
        self.status_label.config(text="⭕ ESP32 POWERED OFF", fg='#ff4444')
        
        self.log("🔴 ESP32 powered OFF")
    
    def start_battery_monitor(self):
        """مراقبة البطارية (محاكاة ESP32)"""
        def monitor():
            while self.is_powered:
                time.sleep(5)
                self.battery_level = max(0, self.battery_level - 0.5)
                self.battery_label.config(text=f"🔋 Battery: {int(self.battery_level)}%")
                
                if self.battery_level <= 20:
                    self.log(f"⚠️ Low battery: {int(self.battery_level)}%")
        
        threading.Thread(target=monitor, daemon=True).start()
    
    def connect_to_server(self):
        """الاتصال بالسيرفر"""
        self.status_label.config(text="🔄 CONNECTING TO SERVER...", fg='#ffaa00')
        self.log("🔄 Connecting to server...")
        
        # تشغيل الاتصال في thread منفصل
        threading.Thread(target=self.run_connection_test, daemon=True).start()
    
    def run_connection_test(self):
        """تشغيل اختبار الاتصال"""
        try:
            async def test_connection():
                # اختبار الاتصال
                response = await self.client.get(f"{self.server_url}/esp32/connect")
                if response.status_code == 200:
                    # تسجيل الجهاز
                    register_data = {
                        "device_id": self.device_udid,
                        "status": "online",
                        "last_seen": datetime.now().isoformat(),
                        "battery_level": int(self.battery_level),
                        "wifi_strength": self.wifi_signal
                    }
                    
                    reg_response = await self.client.post(
                        f"{self.server_url}/esp32/status",
                        json=register_data
                    )
                    
                    return True, response.json()
                else:
                    return False, f"HTTP {response.status_code}"
            
            # تشغيل async
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success, data = loop.run_until_complete(test_connection())
            loop.close()
            
            # تحديث الواجهة
            self.root.after(0, self.connection_result, success, data)
            
        except Exception as e:
            self.root.after(0, self.connection_result, False, str(e))
    
    def connection_result(self, success: bool, data: Any):
        """نتيجة الاتصال"""
        if success:
            self.is_connected = True
            self.status_label.config(text="🌐 CONNECTED TO AI CLOUD", fg='#00ff00')
            self.record_button.config(state='normal')
            
            self.log("✅ Connected to AI server successfully")
            self.log("🎤 Ready for voice interaction")
            self.log("👶 Child can now talk to teddy bear!")
            
        else:
            self.status_label.config(text="❌ CONNECTION FAILED", fg='#ff4444')
            self.log(f"❌ Connection failed: {data}")
    
    def start_voice_interaction(self):
        """بدء التفاعل الصوتي (مثل ESP32 الحقيقي)"""
        if self.is_recording:
            self.log("⚠️ Already recording...")
            return
        
        self.log("🎤 Starting voice recording...")
        self.record_button.config(text="⏹️ STOP RECORDING", bg='#ff6600')
        self.status_label.config(text="🎤 RECORDING AUDIO...", fg='#ff6600')
        
        # بدء التسجيل في thread منفصل
        threading.Thread(target=self.record_and_process_audio, daemon=True).start()
    
    def record_and_process_audio(self):
        """تسجيل ومعالجة الصوت (مثل ESP32 الحقيقي)"""
        try:
            self.is_recording = True
            self.log(f"🎤 Recording audio at {self.sample_rate}Hz...")
            
            # تسجيل الصوت (مثل ESP32)
            audio_data = sd.rec(
                int(self.recording_duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=self.dtype
            )
            
            # انتظار انتهاء التسجيل
            sd.wait()
            
            # تحديث الواجهة
            self.root.after(0, self.recording_finished)
            
            # حفظ الصوت في ملف مؤقت
            temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            sf.write(temp_file.name, audio_data, self.sample_rate)
            
            self.log("💾 Audio recorded, sending to server...")
            
            # إرسال للسيرفر
            self.send_audio_to_server(temp_file.name)
            
            # حذف الملف المؤقت
            os.unlink(temp_file.name)
            
        except Exception as e:
            self.log(f"❌ Recording error: {e}")
            self.root.after(0, self.recording_finished)
        finally:
            self.is_recording = False
    
    def recording_finished(self):
        """انتهاء التسجيل"""
        self.record_button.config(text="🎤 START VOICE RECORDING", bg='#cc3300')
        self.status_label.config(text="📤 SENDING TO AI SERVER...", fg='#ffaa00')
    
    def send_audio_to_server(self, audio_file_path: str):
        """إرسال الصوت للسيرفر (مثل ESP32 الحقيقي)"""
        try:
            async def send_audio():
                # قراءة الملف الصوتي
                with open(audio_file_path, 'rb') as audio_file:
                    files = {
                        'audio_file': ('recording.wav', audio_file, 'audio/wav')
                    }
                    data = {
                        'device_id': self.device_udid
                    }
                    
                    # إرسال للسيرفر
                    response = await self.client.post(
                        f"{self.server_url}/api/audio/upload",
                        files=files,
                        data=data
                    )
                    
                    return response.status_code == 200, response.json() if response.status_code == 200 else response.text
            
            # تشغيل async
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success, result = loop.run_until_complete(send_audio())
            loop.close()
            
            # تحديث الواجهة
            self.root.after(0, self.server_audio_response, success, result)
            
        except Exception as e:
            self.root.after(0, self.server_audio_response, False, str(e))
    
    def server_audio_response(self, success: bool, result: Any):
        """استجابة السيرفر للصوت"""
        if success and isinstance(result, dict):
            self.log("✅ Server processed audio successfully")
            
            # استخراج الرد
            ai_response = result.get('ai_response', {})
            response_text = ai_response.get('text', 'No response')
            response_audio = result.get('response_audio')  # base64 audio
            
            self.log(f"🧸 AI Response: {response_text}")
            
            # تشغيل الصوت إذا متوفر
            if response_audio:
                self.play_response_audio(response_audio)
            else:
                self.log("⚠️ No audio response from server")
                self.status_label.config(text="🌐 CONNECTED - Ready", fg='#00ff00')
            
        else:
            self.log(f"❌ Server error: {result}")
            self.status_label.config(text="❌ SERVER ERROR", fg='#ff4444')
    
    def play_response_audio(self, audio_base64: str):
        """تشغيل الرد الصوتي (مثل ESP32 الحقيقي)"""
        try:
            self.status_label.config(text="🔊 PLAYING RESPONSE...", fg='#9900ff')
            self.log("🔊 Playing AI response audio...")
            
            # فك تشفير base64
            audio_data = base64.b64decode(audio_base64)
            
            # حفظ في ملف مؤقت وتشغيل
            temp_audio = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
            temp_audio.write(audio_data)
            temp_audio.close()
            
            # تشغيل الصوت
            pygame.mixer.music.load(temp_audio.name)
            pygame.mixer.music.play()
            
            # انتظار انتهاء التشغيل في thread منفصل
            def wait_for_playback():
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                
                # تنظيف
                os.unlink(temp_audio.name)
                self.root.after(0, self.playback_finished)
            
            threading.Thread(target=wait_for_playback, daemon=True).start()
            
        except Exception as e:
            self.log(f"❌ Audio playback error: {e}")
            self.status_label.config(text="🌐 CONNECTED - Ready", fg='#00ff00')
    
    def playback_finished(self):
        """انتهاء التشغيل"""
        self.log("✅ Audio playback finished")
        self.status_label.config(text="🌐 CONNECTED - Ready", fg='#00ff00')
        self.log("🎤 Ready for next voice interaction")
    
    async def cleanup(self):
        """تنظيف الموارد"""
        await self.client.aclose()
    
    def on_closing(self):
        """عند إغلاق النافذة"""
        try:
            asyncio.run(self.cleanup())
        except:
            pass
        self.root.destroy()
    
    def run(self):
        """تشغيل المحاكي"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # رسائل الإرشاد
        self.log("=" * 50)
        self.log("🧸 ESP32 AI Teddy Bear - Real Hardware Simulation")
        self.log("=" * 50)
        self.log("📋 Instructions:")
        self.log("1. Click 'POWER ON ESP32'")
        self.log("2. Click 'CONNECT TO SERVER'")
        self.log("3. Click 'START VOICE RECORDING' and speak")
        self.log("4. Listen to AI response")
        self.log("=" * 50)
        
        # بدء GUI
        self.root.mainloop()


if __name__ == "__main__":
    print("🚀 Starting ESP32 Real Simulator...")
    
    # تحقق من المكتبات المطلوبة
    required_modules = ['sounddevice', 'soundfile', 'pygame', 'httpx', 'speech_recognition']
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"❌ Missing modules: {', '.join(missing_modules)}")
        print("📦 Installing required modules...")
        
        import subprocess
        import sys
        
        for module in missing_modules:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", module])
                print(f"✅ Installed {module}")
            except subprocess.CalledProcessError:
                print(f"❌ Failed to install {module}")
                print("Please install manually:")
                print(f"pip install {module}")
                exit(1)
    
    # تشغيل المحاكي
    try:
        simulator = ESP32TeddySimulator()
        simulator.run()
    except Exception as e:
        print(f"❌ Simulator error: {e}")
        print("Please check your microphone and audio system") 