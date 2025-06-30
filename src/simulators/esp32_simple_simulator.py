#!/usr/bin/env python3
"""
🧸 ESP32 Teddy Bear Simulator - Exact Hardware Simulation
محاكي ESP32 للدبدوب - محاكاة دقيقة للجهاز الحقيقي
"""
import structlog
logger = structlog.get_logger(__name__)


import sys
import asyncio
import json
import requests
import wave
import threading
import time
from datetime import datetime
import pyaudio
import speech_recognition as sr
from gtts import gTTS
import pygame
import io
import base64
import uuid

try:
    from tkinter import Tk, Label, Button, Frame, StringVar, Text, Scrollbar, END, VERTICAL, RIGHT, Y, BOTH, X
    from tkinter import ttk, messagebox
    import tkinter as tk
except Exception as e:
    logger.error(f"Error: {e}")"❌ Tkinter not available")
    sys.exit(1)

# ============================ CONFIGURATION ============================

SERVER_URL = "http://127.0.0.1:8000"  # السيرفر المحلي (حاسوبك)
WAKE_WORD = "يا دبدوب"  # كلمة التفعيل
DEVICE_MAC = f"ESP32_{uuid.uuid4().hex[:8].upper()}"  # معرف الجهاز الفريد

# ============================ ESP32 SIMULATOR CLASS ============================

class ESP32TeddySimulator:
    """محاكي ESP32 للدبدوب - يعمل تماماً مثل الجهاز الحقيقي"""
    
    def __init__(self):
        self.is_powered_on = False
        self.is_listening = False
        self.device_id = DEVICE_MAC
        self.session_id = None
        self.listening_thread = None
        self.stop_listening = False
        
        # تهيئة الصوت
        self.init_audio()
        
        # إنشاء الواجهة
        self.create_gui()
        
        print(f"🧸 ESP32 Teddy Simulator Started")
        print(f"🆔 Device ID: {self.device_id}")
        print(f"🌐 Cloud Server: {SERVER_URL}")
    
    def init_audio(self):
        """تهيئة نظام الصوت"""
        try:
            # تهيئة pygame للتشغيل
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            
            # تهيئة speech recognition
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            
            # معايرة الميكروفون
            print("🎤 Calibrating microphone...")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print("✅ Microphone calibrated")
            
        except Exception as e:
    logger.error(f"Error: {e}")f"❌ Audio initialization error: {e}")
    
    def create_gui(self):
        """إنشاء واجهة المحاكي"""
        self.root = tk.Tk()
        self.root.title(f"🧸 ESP32 Teddy Bear - {self.device_id}")
        self.root.geometry("400x500")
        self.root.configure(bg='#2c3e50')
        self.root.resizable(False, False)
        
        # Header
        header_frame = tk.Frame(self.root, bg='#34495e', height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame, 
            text="🧸 AI Teddy Bear",
            font=('Arial', 20, 'bold'),
            fg='white',
            bg='#34495e'
        ).pack(pady=20)
        
        # Device Info
        info_frame = tk.Frame(self.root, bg='#ecf0f1', height=100)
        info_frame.pack(fill="x", padx=20, pady=10)
        info_frame.pack_propagate(False)
        
        tk.Label(info_frame, text=f"Device: {self.device_id}", bg='#ecf0f1', font=('Arial', 10)).pack(pady=5)
        tk.Label(info_frame, text=f"Server: {SERVER_URL}", bg='#ecf0f1', font=('Arial', 10)).pack(pady=5)
        
        # Status Display
        self.status_frame = tk.Frame(self.root, bg='#2c3e50')
        self.status_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # LED Status (Visual)
        self.led_canvas = tk.Canvas(self.status_frame, width=100, height=100, bg='#2c3e50', highlightthickness=0)
        self.led_canvas.pack(pady=20)
        
        # إنشاء LED دائري
        self.led_circle = self.led_canvas.create_oval(25, 25, 75, 75, fill='red', outline='white', width=3)
        
        # Status Text
        self.status_label = tk.Label(
            self.status_frame, 
            text="🔴 الدبدوب مطفأ",
            font=('Arial', 16, 'bold'),
            fg='white',
            bg='#2c3e50'
        )
        self.status_label.pack(pady=10)
        
        # ON/OFF Button (الزر الوحيد)
        self.power_button = tk.Button(
            self.status_frame,
            text="🔌 تشغيل الدبدوب",
            font=('Arial', 14, 'bold'),
            bg='#27ae60',
            fg='white',
            width=20,
            height=2,
            command=self.toggle_power,
            relief='raised',
            borderwidth=3
        )
        self.power_button.pack(pady=20)
        
        # Activity Log
        log_frame = tk.Frame(self.root, bg='#ecf0f1')
        log_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        tk.Label(log_frame, text="📋 Activity Log", bg='#ecf0f1', font=('Arial', 12, 'bold')).pack()
        
        self.log_text = tk.Text(log_frame, height=8, width=50, font=('Arial', 9))
        scrollbar = tk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Initial log
        self.log("🧸 ESP32 Teddy Bear Simulator Ready")
        self.log(f"🆔 Device ID: {self.device_id}")
        self.log("💡 Press 'تشغيل الدبدوب' to power on")
    
    def log(self, message):
        """إضافة رسالة للسجل"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert("end", log_entry)
        self.log_text.see("end")
        print(log_entry.strip())
    
    def toggle_power(self):
        """تشغيل/إطفاء الدبدوب"""
        if not self.is_powered_on:
            self.power_on()
        else:
            self.power_off()
    
    def power_on(self):
        """تشغيل الدبدوب"""
        self.is_powered_on = True
        self.stop_listening = False
        
        # تحديث الواجهة
        self.led_canvas.itemconfig(self.led_circle, fill='green')
        self.status_label.config(text="🟢 الدبدوب يعمل - يستمع للنداء", fg='#27ae60')
        self.power_button.config(text="🔌 إطفاء الدبدوب", bg='#e74c3c')
        
        self.log("✅ Teddy Bear POWERED ON")
        self.log("🎤 Listening for wake word: 'يا دبدوب'")
        self.log("💡 Just say 'يا دبدوب' to start talking!")
        
        # تسجيل الجهاز مع السيرفر
        self.register_device()
        
        # بدء الاستماع في thread منفصل
        self.listening_thread = threading.Thread(target=self.listen_for_wake_word, daemon=True)
        self.listening_thread.start()
    
    def power_off(self):
        """إطفاء الدبدوب"""
        self.is_powered_on = False
        self.stop_listening = True
        
        # تحديث الواجهة
        self.led_canvas.itemconfig(self.led_circle, fill='red')
        self.status_label.config(text="🔴 الدبدوب مطفأ", fg='#e74c3c')
        self.power_button.config(text="🔌 تشغيل الدبدوب", bg='#27ae60')
        
        self.log("🔴 Teddy Bear POWERED OFF")
        
        # إيقاف الاستماع
        if self.listening_thread and self.listening_thread.is_alive():
            self.stop_listening = True
    
    def register_device(self):
        """تسجيل الجهاز مع السيرفر"""
        try:
            data = {
                "device_id": self.device_id,
                "firmware_version": "2.0.0-simulator",
                "hardware_version": "ESP32-S3",
                "capabilities": ["audio", "wifi", "ai"]
            }
            
            response = requests.post(f"{SERVER_URL}/esp32/register", json=data, timeout=5)
            
            if response.status_code == 200:
                result = response.json()
                self.session_id = result.get("session_id")
                self.log("✅ Device registered with cloud server")
                self.log(f"🆔 Session: {self.session_id}")
            else:
                self.log(f"❌ Registration failed: {response.status_code}")
                
        except Exception as e:
            self.log(f"❌ Server connection failed: {e}")
            self.log("⚠️ Working in offline mode")
    
    def listen_for_wake_word(self):
        """الاستماع المستمر لكلمة التفعيل"""
        while self.is_powered_on and not self.stop_listening:
            try:
                # LED يرمش أثناء الاستماع
                self.root.after(0, lambda: self.led_canvas.itemconfig(self.led_circle, fill='yellow'))
                time.sleep(0.1)
                self.root.after(0, lambda: self.led_canvas.itemconfig(self.led_circle, fill='green'))
                
                # استماع للصوت
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=3)
                
                # تحويل الصوت لنص
                try:
                    text = self.recognizer.recognize_google(audio, language='ar-SA')
                    self.root.after(0, lambda: self.log(f"👂 Heard: {text}"))
                    
                    # فحص كلمة التفعيل
                    if WAKE_WORD in text:
                        self.root.after(0, lambda: self.wake_word_detected())
                        
                except sr.UnknownValueError:
                    # لم يفهم ما قيل - استمر في الاستماع
                    pass
                except sr.RequestError as e:
                    self.root.after(0, lambda: self.log(f"❌ Speech recognition error: {e}"))
                    time.sleep(2)
                    
            except Exception as e:
                if not self.stop_listening:
                    self.root.after(0, lambda: self.log(f"❌ Listening error: {e}"))
                time.sleep(1)
    
    def wake_word_detected(self):
        """عند اكتشاف كلمة التفعيل"""
        self.log("🎯 Wake word detected: 'يا دبدوب'")
        self.log("🎤 Recording your message...")
        
        # LED أزرق = تسجيل
        self.led_canvas.itemconfig(self.led_circle, fill='blue')
        self.status_label.config(text="🎤 جاري التسجيل... تحدث الآن", fg='#3498db')
        
        # تسجيل الرسالة في thread منفصل
        recording_thread = threading.Thread(target=self.record_and_process, daemon=True)
        recording_thread.start()
    
    def record_and_process(self):
        """تسجيل ومعالجة الرسالة"""
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=10)
            
            # LED برتقالي = معالجة
            self.root.after(0, lambda: self.led_canvas.itemconfig(self.led_circle, fill='orange'))
            self.root.after(0, lambda: self.status_label.config(text="🧠 الدبدوب يفكر...", fg='#f39c12'))
            self.root.after(0, lambda: self.log("🧠 Processing your message..."))
            
            # تحويل لنص
            message = self.recognizer.recognize_google(audio, language='ar-SA')
            self.root.after(0, lambda: self.log(f"👶 Child said: {message}"))
            
            # إرسال للسيرفر
            self.send_to_ai(message)
            
        except sr.WaitTimeoutError:
            self.root.after(0, lambda: self.log("⏱️ Recording timeout - no speech detected"))
            self.return_to_listening()
        except sr.UnknownValueError:
            self.root.after(0, lambda: self.log("❓ Could not understand speech"))
            self.return_to_listening()
        except Exception as e:
            self.root.after(0, lambda: self.log(f"❌ Recording error: {e}"))
            self.return_to_listening()
    
    def send_to_ai(self, message):
        """إرسال الرسالة للذكاء الاصطناعي"""
        try:
            data = {
                "audio": message,  # في المحاكي نرسل النص مباشرة
                "device_id": self.device_id,
                "session_id": self.session_id or f"session_{int(time.time())}"
            }
            
            response = requests.post(f"{SERVER_URL}/esp32/audio", json=data, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get("ai_response", {})
                ai_text = ai_response.get("text", "عذراً، لم أفهم")
                
                self.root.after(0, lambda: self.log(f"🧸 Teddy says: {ai_text}"))
                
                # تشغيل الرد
                self.speak_response(ai_text)
                
            else:
                self.root.after(0, lambda: self.log(f"❌ Server error: {response.status_code}"))
                self.return_to_listening()
                
        except Exception as e:
            self.root.after(0, lambda: self.log(f"❌ AI request failed: {e}"))
            self.return_to_listening()
    
    def speak_response(self, text):
        """تشغيل رد الدبدوب"""
        try:
            # LED بنفسجي = يتكلم
            self.root.after(0, lambda: self.led_canvas.itemconfig(self.led_circle, fill='purple'))
            self.root.after(0, lambda: self.status_label.config(text="🗣️ الدبدوب يتكلم...", fg='#9b59b6'))
            
            # تحويل النص لصوت
            tts = gTTS(text=text, lang='ar', slow=False)
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            
            # تشغيل الصوت
            pygame.mixer.music.load(audio_buffer)
            pygame.mixer.music.play()
            
            # انتظار انتهاء التشغيل
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            
            self.root.after(0, lambda: self.log("🔊 Response played successfully"))
            
        except Exception as e:
            self.root.after(0, lambda: self.log(f"❌ Speech synthesis error: {e}"))
        
        finally:
            # العودة للاستماع
            self.return_to_listening()
    
    def return_to_listening(self):
        """العودة لحالة الاستماع"""
        if self.is_powered_on:
            self.led_canvas.itemconfig(self.led_circle, fill='green')
            self.status_label.config(text="🟢 الدبدوب يعمل - يستمع للنداء", fg='#27ae60')
            self.log("👂 Back to listening for 'يا دبدوب'")
    
    def run(self):
        """تشغيل المحاكي"""
        try:
            self.root.mainloop()
        except Exception as e:
    logger.error(f"Error: {e}")"\n👋 ESP32 Simulator shutting down...")
        finally:
            self.power_off()


# ============================ MAIN ============================

if __name__ == "__main__":
    print("🧸 Starting ESP32 Teddy Bear Simulator...")
    print("=" * 50)
    print("🎯 This simulates the EXACT behavior of ESP32 in teddy bear")
    print("🔌 Hardware: ESP32 with microphone, speaker, LED")
    print("☁️ Cloud: Your computer running the AI server")
    print("🎤 Wake Word: 'يا دبدوب'")
    print("=" * 50)
    
    try:
        simulator = ESP32TeddySimulator()
        simulator.run()
    except Exception as e:
    logger.error(f"Error: {e}")f"❌ Simulator error: {e}") 