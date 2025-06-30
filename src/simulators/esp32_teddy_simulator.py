import logging

logger = logging.getLogger(__name__)

import structlog
logger = structlog.get_logger(__name__)

from typing import Dict, List, Optional, Any, Union
#!/usr/bin/env python3
"""
🧸 ESP32 Teddy Bear Simulator - Complete Production Version
محاكي ESP32 للدبدوب الذكي - إصدار الإنتاج الكامل
"""

import requests
import threading
import time
from datetime import datetime
import speech_recognition as sr
from gtts import gTTS
import pygame
import io
import uuid
import tkinter as tk

# ======================== CONFIGURATION ========================

SERVER_URL = "http://127.0.0.1:8000"
WAKE_WORDS = ["يا دبدوب", "hey teddy", "hello teddy"]
DEVICE_MAC = f"ESP32_{uuid.uuid4().hex[:8].upper()}"

# Language Detection Mapping
LANGUAGE_MAP = {
    "يا دبدوب": "ar-SA",
    "hey teddy": "en-US", 
    "hello teddy": "en-US"
}

# ======================== ESP32 TEDDY SIMULATOR ========================

class ESP32TeddyBearSimulator:
    """محاكي ESP32 الكامل للدبدوب الذكي"""
    
    def __init__(self):
        # Hardware States
        self.is_powered_on = False
        self.device_id = DEVICE_MAC
        self.volume_level = 50
        self.wifi_connected = False
        self.server_connected = False  # مؤشر منفصل للسيرفر
        self.session_id = None
        self.server_monitor_active = False
        
        # AI & Learning
        self.child_profile = None
        self.conversation_history = []
        self.learning_progress = {}
        self.current_language = "ar-SA"  # Default to Arabic
        
        # Audio System
        self.init_audio()
        
        # Network
        self.websocket = None
        
        # GUI
        self.create_advanced_gui()
        
        logger.info(f"🧸 ESP32 Teddy Bear Simulator - Production Ready")
        logger.info(f"🆔 Device ID: {self.device_id}")
    
    def _init_audio(self) -> Any:
        """تهيئة نظام الصوت المتقدم"""
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            
            # Initialize microphone with ULTRA-SENSITIVE settings
            self.microphone = sr.Microphone()
            self.recognizer = sr.Recognizer()
            
            # ULTRA-SENSITIVE settings for better detection
            self.recognizer.energy_threshold = 100  # MUCH lower for sensitivity
            self.recognizer.dynamic_energy_threshold = False  # Fixed threshold
            self.recognizer.pause_threshold = 0.3   # Very quick detection
            self.recognizer.phrase_threshold = 0.1  # Instant trigger
            self.recognizer.non_speaking_duration = 0.2  # Very quick cutoff
            
            # Quick calibration
            logger.info("🎤 Calibrating microphone for MAXIMUM sensitivity...")
            with self.microphone as source:
                # Very short calibration to avoid adjusting threshold too high
                self.recognizer.adjust_for_ambient_noise(source, duration=0.1)
                # Force low threshold after calibration
                self.recognizer.energy_threshold = 100
            
            logger.info("✅ Microphone ready - ULTRA SENSITIVE MODE!")
            logger.info(f"🔊 Energy threshold: {self.recognizer.energy_threshold}")
            
        except Exception as e:
    logger.error(f"Error: {e}")f"❌ Audio error: {e}")
    
    def _create_advanced_gui(self) -> Any:
        """إنشاء واجهة المحاكي المتقدمة"""
        self.root = tk.Tk()
        self.root.title(f"🧸 ESP32 Teddy Bear - {self.device_id}")
        self.root.geometry("600x800")
        self.root.configure(bg='#2c3e50')
        
        # Header
        header = tk.Frame(self.root, bg='#34495e', height=80)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Label(
            header, 
            text="🧸 AI Teddy Bear - ESP32 Simulator",
            font=('Arial', 18, 'bold'),
            fg='white',
            bg='#34495e'
        ).pack(pady=25)
        
        # Device Status Panel
        self.create_status_panel()
        
        # Control Panel
        self.create_control_panel()
        
        # Child Profile Panel
        self.create_child_panel()
        
        # Activity Monitor
        self.create_activity_panel()
        
        # Advanced Features
        self.create_features_panel()
        
        self.log("🧸 ESP32 Teddy Bear Simulator Ready")
        self.log("💡 Press POWER to start your AI teddy bear")
        
        # بدء مراقبة السيرفر المستمرة
        self.start_server_monitor()
    
    def _create_status_panel(self) -> Any:
        """لوحة حالة الجهاز"""
        status_frame = tk.LabelFrame(self.root, text="Device Status", bg='#ecf0f1', font=('Arial', 12, 'bold'))
        status_frame.pack(fill="x", padx=15, pady=10)
        
        # LED Status with Audio Visualizer
        led_frame = tk.Frame(status_frame, bg='#ecf0f1')
        led_frame.pack(pady=10)
        
        self.led_canvas = tk.Canvas(led_frame, width=80, height=80, bg='#ecf0f1', highlightthickness=0)
        self.led_canvas.pack(side="left", padx=20)
        self.led_circle = self.led_canvas.create_oval(15, 15, 65, 65, fill='red', outline='white', width=3)
        
        # Audio Visualizer
        self.audio_visualizer = tk.Canvas(led_frame, width=200, height=80, bg='#2c3e50', highlightthickness=0)
        self.audio_visualizer.pack(side="left", padx=20)
        self.visualizer_bars = []
        self.is_visualizing = False
        
        # إنشاء أعمدة المؤشر الصوتي
        for i in range(20):
            x = i * 10 + 5
            bar = self.audio_visualizer.create_rectangle(x, 70, x+8, 70, fill='#3498db', outline='#3498db')
            self.visualizer_bars.append(bar)
        
        # Status Info
        info_frame = tk.Frame(led_frame, bg='#ecf0f1')
        info_frame.pack(side="left", fill="both", expand=True)
        
        tk.Label(info_frame, text=f"Device: {self.device_id}", bg='#ecf0f1', font=('Arial', 10)).pack(anchor="w")
        tk.Label(info_frame, text=f"Server: {SERVER_URL}", bg='#ecf0f1', font=('Arial', 10)).pack(anchor="w")
        
        self.status_label = tk.Label(info_frame, text="🔴 POWERED OFF", bg='#ecf0f1', font=('Arial', 12, 'bold'), fg='red')
        self.status_label.pack(anchor="w", pady=5)
        
        self.wifi_label = tk.Label(info_frame, text="📶 WiFi: Disconnected", bg='#ecf0f1', font=('Arial', 10))
        self.wifi_label.pack(anchor="w")
        
        self.server_status_label = tk.Label(info_frame, text="🔴 Server: Disconnected", bg='#ecf0f1', font=('Arial', 10), fg='red')
        self.server_status_label.pack(anchor="w")
        
        self.profile_status_label = tk.Label(info_frame, text="👶 Profile: Not Set", bg='#ecf0f1', font=('Arial', 10), fg='orange')
        self.profile_status_label.pack(anchor="w")
        
        self.volume_label = tk.Label(info_frame, text=f"🔊 Volume: {self.volume_level}%", bg='#ecf0f1', font=('Arial', 10))
        self.volume_label.pack(anchor="w")
    
    def _create_control_panel(self) -> Any:
        """لوحة التحكم الرئيسية"""
        control_frame = tk.LabelFrame(self.root, text="Main Controls", bg='#ecf0f1', font=('Arial', 12, 'bold'))
        control_frame.pack(fill="x", padx=15, pady=10)
        
        buttons_frame = tk.Frame(control_frame, bg='#ecf0f1')
        buttons_frame.pack(pady=15)
        
        # Power Button
        self.power_button = tk.Button(
            buttons_frame,
            text="🔌 POWER ON",
            font=('Arial', 14, 'bold'),
            bg='#27ae60',
            fg='white',
            width=15,
            height=2,
            command=self.toggle_power
        )
        self.power_button.pack(side="left", padx=10)
        
        # Restart Button
        self.restart_button = tk.Button(
            buttons_frame,
            text="🔄 RESTART",
            font=('Arial', 12, 'bold'),
            bg='#f39c12',
            fg='white',
            width=12,
            command=self.full_restart
        )
        self.restart_button.pack(side="left", padx=10)
        
        # Emergency Stop
        self.emergency_button = tk.Button(
            buttons_frame,
            text="🛑 EMERGENCY",
            font=('Arial', 12, 'bold'),
            bg='#e74c3c',
            fg='white',
            width=12,
            command=self.emergency_stop
        )
        self.emergency_button.pack(side="left", padx=10)
        
        # Audio Restart
        self.audio_restart_button = tk.Button(
            buttons_frame,
            text="🔄 RESTART AUDIO",
            font=('Arial', 12, 'bold'),
            bg='#f39c12',
            fg='white',
            width=15,
            command=self.restart_audio_system
        )
        self.audio_restart_button.pack(side="left", padx=10)
        
        # Volume Controls
        volume_frame = tk.Frame(control_frame, bg='#ecf0f1')
        volume_frame.pack(pady=10)
        
        tk.Button(volume_frame, text="🔉", command=self.volume_down, bg='#3498db', fg='white').pack(side="left", padx=5)
        self.volume_scale = tk.Scale(volume_frame, from_=0, to=100, orient="horizontal", length=200, command=self.volume_changed)
        self.volume_scale.set(self.volume_level)
        self.volume_scale.pack(side="left", padx=10)
        tk.Button(volume_frame, text="🔊", command=self.volume_up, bg='#3498db', fg='white').pack(side="left", padx=5)
        
        # Microphone Sensitivity Controls
        mic_frame = tk.Frame(control_frame, bg='#ecf0f1')
        mic_frame.pack(pady=10)
        
        tk.Label(mic_frame, text="🎤 Microphone Sensitivity:", bg='#ecf0f1', font=('Arial', 10, 'bold')).pack(side="left", padx=5)
        tk.Button(mic_frame, text="📉", command=self.sensitivity_down, bg='#e67e22', fg='white').pack(side="left", padx=5)
        self.sensitivity_scale = tk.Scale(mic_frame, from_=100, to=1000, orient="horizontal", length=150, command=self.sensitivity_changed)
        self.sensitivity_scale.set(300)  # القيمة الافتراضية
        self.sensitivity_scale.pack(side="left", padx=10)
        tk.Button(mic_frame, text="📈", command=self.sensitivity_up, bg='#e67e22', fg='white').pack(side="left", padx=5)
        self.sensitivity_label = tk.Label(mic_frame, text="Sensitivity: 300", bg='#ecf0f1', font=('Arial', 9))
        self.sensitivity_label.pack(side="left", padx=5)
    
    def _create_child_panel(self) -> Any:
        """لوحة ملف الطفل"""
        child_frame = tk.LabelFrame(self.root, text="Child Profile", bg='#ecf0f1', font=('Arial', 12, 'bold'))
        child_frame.pack(fill="x", padx=15, pady=10)
        
        profile_frame = tk.Frame(child_frame, bg='#ecf0f1')
        profile_frame.pack(pady=10)
        
        # Child Info
        tk.Label(profile_frame, text="Name:", bg='#ecf0f1').grid(row=0, column=0, sticky="w", padx=5)
        self.child_name = tk.Entry(profile_frame, width=20)
        self.child_name.grid(row=0, column=1, padx=5)
        
        tk.Label(profile_frame, text="Age:", bg='#ecf0f1').grid(row=0, column=2, sticky="w", padx=5)
        self.child_age = tk.Spinbox(profile_frame, from_=2, to=12, width=5)
        self.child_age.grid(row=0, column=3, padx=5)
        
        tk.Button(profile_frame, text="💾 Save Profile", command=self.save_child_profile, bg='#9b59b6', fg='white').grid(row=0, column=4, padx=10)
        
        self.profile_status = tk.Label(child_frame, text="👶 No child profile set", bg='#ecf0f1', font=('Arial', 10))
        self.profile_status.pack(pady=5)
    
    def _create_activity_panel(self) -> Any:
        """لوحة مراقبة النشاط"""
        activity_frame = tk.LabelFrame(self.root, text="Activity Monitor", bg='#ecf0f1', font=('Arial', 12, 'bold'))
        activity_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Tabs
        notebook = ttk.Notebook(activity_frame)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Activity Log Tab
        log_frame = tk.Frame(notebook, bg='#ffffff')
        notebook.add(log_frame, text="📋 Activity Log")
        
        self.log_text = tk.Text(log_frame, height=8, font=('Arial', 9))
        log_scrollbar = tk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        self.log_text.pack(side="left", fill="both", expand=True)
        log_scrollbar.pack(side="right", fill="y")
        
        # Conversations Tab
        conv_frame = tk.Frame(notebook, bg='#ffffff')
        notebook.add(conv_frame, text="💬 Conversations")
        
        self.conv_text = tk.Text(conv_frame, height=8, font=('Arial', 9))
        conv_scrollbar = tk.Scrollbar(conv_frame, orient="vertical", command=self.conv_text.yview)
        self.conv_text.configure(yscrollcommand=conv_scrollbar.set)
        self.conv_text.pack(side="left", fill="both", expand=True)
        conv_scrollbar.pack(side="right", fill="y")
        
        # Analytics Tab
        analytics_frame = tk.Frame(notebook, bg='#ffffff')
        notebook.add(analytics_frame, text="📊 Analytics")
        
        self.analytics_text = tk.Text(analytics_frame, height=8, font=('Arial', 9))
        self.analytics_text.pack(fill="both", expand=True, padx=10, pady=10)
    
    def _create_features_panel(self) -> Any:
        """لوحة الميزات المتقدمة"""
        features_frame = tk.LabelFrame(self.root, text="Advanced Features", bg='#ecf0f1', font=('Arial', 12, 'bold'))
        features_frame.pack(fill="x", padx=15, pady=10)
        
        features_grid = tk.Frame(features_frame, bg='#ecf0f1')
        features_grid.pack(pady=10)
        
        # Feature buttons
        tk.Button(features_grid, text="🎮 Games", command=self.test_games, bg='#e67e22', fg='white', width=12).grid(row=0, column=0, padx=5, pady=5)
        tk.Button(features_grid, text="📚 Stories", command=self.test_stories, bg='#8e44ad', fg='white', width=12).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(features_grid, text="🎵 Songs", command=self.test_songs, bg='#16a085', fg='white', width=12).grid(row=0, column=2, padx=5, pady=5)
        tk.Button(features_grid, text="🧠 Learning", command=self.test_learning, bg='#2980b9', fg='white', width=12).grid(row=0, column=3, padx=5, pady=5)
        
        tk.Button(features_grid, text="😊 Emotions", command=self.test_emotions, bg='#f39c12', fg='white', width=12).grid(row=1, column=0, padx=5, pady=5)
        tk.Button(features_grid, text="👨‍👩‍👧‍👦 Family", command=self.test_family, bg='#27ae60', fg='white', width=12).grid(row=1, column=1, padx=5, pady=5)
        tk.Button(features_grid, text="📊 Reports", command=self.show_reports, bg='#34495e', fg='white', width=12).grid(row=1, column=2, padx=5, pady=5)
        tk.Button(features_grid, text="⚙️ Settings", command=self.show_settings, bg='#95a5a6', fg='white', width=12).grid(row=1, column=3, padx=5, pady=5)
        
        # Quick Test Button
        tk.Button(features_grid, text="🧪 Quick Test", command=self.quick_test, bg='#e74c3c', fg='white', width=12).grid(row=2, column=0, padx=5, pady=5)
        tk.Button(features_grid, text="🔍 Test Server", command=self.test_server, bg='#3498db', fg='white', width=12).grid(row=2, column=1, padx=5, pady=5)
        tk.Button(features_grid, text="🎵 Test TTS", command=self.test_tts, bg='#9b59b6', fg='white', width=12).grid(row=2, column=2, padx=5, pady=5)
        tk.Button(features_grid, text="💬 Test AI", command=self.test_ai_direct, bg='#2ecc71', fg='white', width=12).grid(row=2, column=3, padx=5, pady=5)
        
        # Emergency Controls
        emergency_frame = tk.Frame(features_frame, bg='#ecf0f1')
        emergency_frame.pack(pady=5)
        
        tk.Button(emergency_frame, text="🛡️ KEEP ALIVE", command=self.force_stay_alive, bg='#e67e22', fg='white', width=15).pack(side="left", padx=5)
        tk.Button(emergency_frame, text="🔧 FORCE FIX", command=self.force_fix_system, bg='#c0392b', fg='white', width=15).pack(side="left", padx=5)
    
    def _log(self, message) -> Any:
        """إضافة رسالة للسجل"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert("end", log_entry)
        self.log_text.see("end")
        logger.info(log_entry.strip())
    
    def _log_conversation(self, user_msg, ai_response) -> Any:
        """تسجيل المحادثة"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        conv_entry = f"[{timestamp}] 👶: {user_msg}\n[{timestamp}] 🧸: {ai_response}\n\n"
        
        self.conv_text.insert("end", conv_entry)
        self.conv_text.see("end")
        
        # حفظ في التاريخ
        self.conversation_history.append({
            "timestamp": timestamp,
            "user": user_msg,
            "ai": ai_response
        })
    
    def _start_audio_visualizer(self) -> Any:
        """بدء المؤشر الصوتي المتحرك"""
        if not self.is_visualizing:  # منع التشغيل المتعدد
            self.is_visualizing = True
            self.animate_visualizer()
    
    def _stop_audio_visualizer(self) -> Any:
        """إيقاف المؤشر الصوتي"""
        self.is_visualizing = False
        # إعادة تعيين الأعمدة للوضع الطبيعي
        for i, bar in enumerate(self.visualizer_bars):
            self.audio_visualizer.coords(bar, i*10+5, 70, i*10+13, 70)
    
    def _animate_visualizer(self) -> Any:
        """تحريك المؤشر الصوتي"""
        if not self.is_visualizing:
            return
            
        import random
        
        # تحريك الأعمدة بناءً على نشاط صوتي محاكى
        for i, bar in enumerate(self.visualizer_bars):
            # ارتفاع عشوائي لمحاكاة الصوت
            height = random.randint(10, 70)
            y_top = 70 - height
            
            # ألوان مختلفة حسب الارتفاع
            if height > 50:
                color = '#e74c3c'  # أحمر للأصوات العالية
            elif height > 30:
                color = '#f39c12'  # برتقالي للأصوات المتوسطة
            else:
                color = '#3498db'  # أزرق للأصوات المنخفضة
                
            self.audio_visualizer.coords(bar, i*10+5, y_top, i*10+13, 70)
            self.audio_visualizer.itemconfig(bar, fill=color, outline=color)
        
        # تكرار الحركة كل 100ms
        if self.is_visualizing:
            self.root.after(100, self.animate_visualizer)
    
    def _toggle_power(self) -> Any:
        """تشغيل/إطفاء الدبدوب"""
        if not self.is_powered_on:
            self.power_on()
        else:
            self.power_off()
    
    def _power_on(self) -> Any:
        """تشغيل الدبدوب"""
        if self.is_powered_on:
            self.log("⚠️ Teddy is already powered on")
            return
            
        self.is_powered_on = True
        
        # تحديث الواجهة
        self.led_canvas.itemconfig(self.led_circle, fill='green')
        self.status_label.config(text="🟢 POWERED ON", fg='green')
        self.power_button.config(text="🔌 POWER OFF", bg='#e74c3c')
        
        self.log("✅ Teddy Bear POWERED ON")
        self.log("📶 Connecting to WiFi...")
        
        # محاكاة الاتصال بالإنترنت
        threading.Timer(2.0, self.connect_wifi).start()
        
        # بدء الاستماع
        threading.Timer(3.0, self.start_listening).start()
    
    def _power_off(self) -> Any:
        """إطفاء الدبدوب"""
        if not self.is_powered_on:
            return  # لا تطفئ إذا كان مطفأ بالفعل
            
        self.is_powered_on = False
        self.wifi_connected = False
        self.server_connected = False
        
        # إيقاف الصوت
        try:
            pygame.mixer.stexcept Exception as e:
    logger.error(f"Error in operation: {e}", exc_info=True)Exception as e:
    logger.error(f"Error in operation: {e}", exc_info=True)xception as e:
    logger.warning(f"Ignoring error: {e}")         pass
        
        # تحديث الواجهة
        self.led_canvas.itemconfig(self.led_circle, fill='red')
        self.status_label.config(text="🔴 POWERED OFF", fg='red')
        self.power_button.config(text="🔌 POWER ON", bg='#27ae60')
        self.wifi_label.config(text="📶 WiFi: Disconnected")
        self.server_status_label.config(text="🔴 Server: Disconnected", fg='red')
        
        self.log("🔴 Teddy Bear POWERED OFF")
    
    def _connect_wifi(self) -> Any:
        """الاتصال بالواي فاي أولاً ثم السيرفر - محاكاة واقعية"""
        
        # خطوة 1: محاكاة الاتصال بالواي فاي
        try:
            self.log("📶 Scanning for WiFi networks...")
            time.sleep(1)  # محاكاة البحث عن الشبكات
            
            self.log("📶 Found WiFi: TeddyBear_Network")
            time.sleep(0.5)
            
            self.log("🔐 Connecting to WiFi...")
            time.sleep(1)  # محاكاة الاتصال
            
            # نجح الاتصال بالواي فاي
            self.wifi_connected = True
            self.wifi_label.config(text="📶 WiFi: Connected ✅")
            self.log("✅ WiFi connected successfully!")
            
            # خطوة 2: الآن نحاول الاتصال بالسيرفر
            self.connect_to_server()
            
        except Exception as e:
            self.wifi_connected = False
            self.server_connected = False
            self.wifi_label.config(text="📶 WiFi: Failed ❌")
            self.server_status_label.config(text="🔴 Server: No WiFi", fg='red')
            self.log(f"❌ WiFi connection failed: {e}")
            self.led_canvas.itemconfig(self.led_circle, fill='red')
            self.status_label.config(text="❌ NO WIFI", fg='red')
    
    def _connect_to_server(self) -> Any:
        """الاتصال بالسيرفر (يتطلب WiFi أولاً)"""
        if not self.wifi_connected:
            self.log("❌ Cannot connect to server - No WiFi!")
            return
            
        try:
            self.log("☁️ Connecting to cloud server...")
            response = requests.get(f"{SERVER_URL}/health", timeout=5)
            
            if response.status_code == 200:
                self.server_connected = True
                self.server_status_label.config(text="🟢 Server: Connected", fg='green')
                self.log("✅ Connected to cloud server")
                self.register_device()
            else:
                raise Exception(f"Server responded with {response.status_code}")
                
        except Exception as e:
            self.server_connected = False
            self.server_status_label.config(text="🔴 Server: Failed", fg='red')
            self.log(f"❌ Failed to connect to server: {e}")
            # واي فاي متصل لكن السيرفر لا
            self.led_canvas.itemconfig(self.led_circle, fill='orange')
            self.status_label.config(text="⚠️ SERVER OFFLINE", fg='orange')
    
    def _register_device(self) -> Any:
        """تسجيل الجهاز"""
        try:
            data = {
                "device_id": self.device_id,
                "firmware_version": "2.0.0-simulator",
                "hardware_version": "ESP32-S3",
                "capabilities": ["audio", "wifi", "ai", "games", "stories", "learning"]
            }
            
            response = requests.post(f"{SERVER_URL}/esp32/register", json=data, timeout=5)
            if response.status_code == 200:
                result = response.json()
                self.session_id = result.get("session_id")
                self.log(f"📝 Device registered - Session: {self.session_id}")
        except Exception as e:
            self.log(f"❌ Registration failed: {e}")
    
    def _start_listening(self) -> Any:
        """Start listening for wake words with detailed debugging"""
        if not self.is_powered_on:
            self.log("❌ Cannot start listening - Device not powered on")
            return
            
        if not self.wifi_connected:
            self.log("❌ Cannot start listening - No WiFi connection")
            return
            
        if not self.server_connected:
            self.log("❌ Cannot start listening - No server connection")
            return
        
        self.log("🎤 STARTING LISTENING SYSTEM...")
        self.log("✅ All conditions met - Power ON, WiFi OK, Server OK")
        
        # Stop any existing listening thread
        if hasattr(self, 'listening_thread') and self.listening_thread and self.listening_thread.is_alive():
            self.log("🔄 Stopping existing listening thread...")
            # We can't stop it directly, just let it die naturally
        
        # Start new listening thread
        try:
            self.listening_thread = threading.Thread(target=self.listen_for_audio, daemon=True)
            self.listening_thread.start()
            self.log("✅ LISTENING THREAD STARTED!")
            self.log("🗣️ SAY: 'يا دبدوب' أو 'Hey Teddy' to activate!")
        except Exception as e:
            self.log(f"❌ Failed to start listening thread: {e}")
        
        # Show instructions
        self.log("👂 Listening for wake words: 'يا دبدوب' or 'Hey Teddy'")
        self.log("💡 Say 'يا دبدوب' للعربية أو 'Hey Teddy' for English!")
        self.log("📝 Remember: Say wake word FIRST, then your message!")
        self.log("🔊 MICROPHONE IS NOW ACTIVE AND LISTENING...")
        self.log("🎯 Ultra-sensitive mode enabled - speak clearly!")
        
        # Update UI
        self.update_connection_status()
    
    def _listen_for_audio(self) -> Any:
        """SUPER RESPONSIVE wake word detection with detailed logging"""
        self.log("🎤 🎤 🎤 LISTENING THREAD STARTED! 🎤 🎤 🎤")
        self.log(f"🔊 Energy threshold: {self.recognizer.energy_threshold}")
        self.log(f"🔊 Wake words: {WAKE_WORDS}")
        
        listen_count = 0
        
        while self.is_powered_on and self.server_connected:
            try:
                listen_count += 1
                self.log(f"🔄 Listen cycle #{listen_count}")
                
                # Visual feedback - rapid blinking while listening
                self.root.after(0, lambda: self.led_canvas.itemconfig(self.led_circle, fill='yellow'))
                
                with self.microphone as source:
                    try:
                        # VERY responsive listening
                        self.log("🔊 LISTENING NOW... Say 'يا دبدوب' or 'Hey Teddy'")
                        self.log("📢 Speak clearly and loud enough!")
                        
                        # Listen for audio
                        audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=4)
                        self.log("✅ Audio captured! Processing...")
                        
                        # Reset LED
                        self.root.after(0, lambda: self.led_canvas.itemconfig(self.led_circle, fill='green'))
                        
                        # Try BOTH languages immediately
                        recognized_text = None
                        detected_lang = None
                        
                        # Try Arabic first
                        try:
                            self.log("🔄 Trying Arabic recognition...")
                            text = self.recognizer.recognize_google(audio, language='ar-SA')
                            if text:
                                recognized_text = text.lower()
                                detected_lang = 'ar-SA'
                                self.log(f"🎤 ✅ سمعت (عربي): '{text}'")
                        except Exception as ar_error:
                            self.log(f"❌ Arabic recognition failed: {ar_error}")
                        
                        # Try English if Arabic failed
                        if not recognized_text:
                            try:
                                self.log("🔄 Trying English recognition...")
                                text = self.recognizer.recognize_google(audio, language='en-US')
                                if text:
                                    recognized_text = text.lower()
                                    detected_lang = 'en-US'
                                    self.log(f"🎤 ✅ Heard (English): '{text}'")
                            except Exception as en_error:
                                self.log(f"❌ English recognition failed: {en_error}")
                        
                        # Check for wake words if we got text
                        if recognized_text:
                            self.log(f"🔍 Checking wake words in: '{recognized_text}'")
                            wake_detected = False
                            for wake_word in WAKE_WORDS:
                                if wake_word in recognized_text:
                                    self.log(f"🎯 ✅ WAKE WORD DETECTED: '{wake_word}'!")
                                    self.current_language = LANGUAGE_MAP.get(wake_word, detected_lang)
                                    self.root.after(0, lambda: self.wake_word_detected(wake_word, recognized_text))
                                    wake_detected = True
                                    break
                            
                            if not wake_detected:
                                self.log(f"❌ Not a wake word: '{recognized_text}' - continue listening...")
                            else:
                                self.log("🎯 Wake word processed! Exiting listen loop...")
                                break  # Exit to handle wake word
                        else:
                            # No text recognized
                            self.log("❓ No speech detected, continuing to listen...")
                                
                    except sr.WaitTimeoutError:
                        # Normal timeout, just continue
                        self.log("⏰ Listen timeout - continuing...")
                        pass
                    except Exception as e:
                        self.log(f"⚠️ Audio processing error: {e}")
                        time.sleep(0.1)
                        
            except Exception as e:
                self.log(f"❌ System error in listen loop: {e}")
                time.sleep(0.5)
                
        # Restart listening for next wake word
        if self.is_powered_on and self.server_connected:
            self.log("🔄 Restarting listening thread after wake word...")
            time.sleep(1)  # Longer delay before restart
            self.listening_thread = threading.Thread(target=self.listen_for_audio, daemon=True)
            self.listening_thread.start()
        else:
            self.log("🛑 Listening stopped - device powered off or disconnected")
    
    def _wake_word_detected(self, wake_word, full_text) -> Any:
        """عند اكتشاف كلمة التفعيل"""
        self.log(f"🎯 Wake word detected: '{wake_word}' (Language: {self.current_language})")
        self.log("🎤 Recording your message...")
        
        # LED أزرق = تسجيل
        self.led_canvas.itemconfig(self.led_circle, fill='blue')
        self.status_label.config(text="🎤 RECORDING", fg='blue')
        
        # بدء المؤشر الصوتي للتسجيل
        self.start_audio_visualizer()
        
        # تسجيل الرسالة
        threading.Thread(target=self.record_and_process, args=(full_text,), daemon=True).start()
    
    def _record_and_process(self, initial_text=None) -> Any:
        """تسجيل ومعالجة الرسالة"""
        if not self.is_powered_on:
            return  # لا تعمل شيء إذا كان الدبدوب مطفأ
            
        try:
            message_text = None
            
            # استخراج الرسالة من النص الأولي إن وجد
            if initial_text:
                text_lower = initial_text.lower()
                for wake_word in WAKE_WORDS:
                    if wake_word in text_lower:
                        message_text = text_lower.replace(wake_word, "").strip()
                        break
                
                if message_text and len(message_text) > 2:  # أكثر مرونة
                    self.root.after(0, lambda: self.log(f"📝 Message from wake phrase ({self.current_language}): {message_text}"))
                    self.send_to_ai(message_text)
                    return
            
            # إذا لم نحصل على رسالة واضحة، اطلب من الطفل التحدث مرة أخرى
            self.root.after(0, lambda: self.log("🎤 Please continue speaking... (1 second timeout)"))
            
            # إعادة تهيئة الميكروفون لتجنب Stream closed
            self.microphone = sr.Microphone()
            with self.microphone as source:
                # تسريع المعايرة 
                self.recognizer.adjust_for_ambient_noise(source, duration=0.1)
                # timeout أطول للسماح بالتكلم بسهولة
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=8)
            
            # LED برتقالي = معالجة
            self.root.after(0, lambda: self.led_canvas.itemconfig(self.led_circle, fill='orange'))
            self.root.after(0, lambda: self.status_label.config(text="🧠 THINKING", fg='orange'))
            self.root.after(0, lambda: self.log("🧠 Processing your message..."))
            
            # تحويل لنص بحسب اللغة المحددة
            message = self.recognizer.recognize_google(audio, language=self.current_language)
            self.root.after(0, lambda: self.log(f"👶 Child said ({self.current_language}): {message}"))
            
            # إرسال للذكاء الاصطناعي
            self.send_to_ai(message)
            
        except sr.WaitTimeoutError:
            self.root.after(0, lambda: self.log("⏱️ No speech heard - returning to listening"))
            self.stop_audio_visualizer()
            self.return_to_listening()
        except sr.UnknownValueError:
            self.root.after(0, lambda: self.log("❓ Could not understand - returning to listening"))
            self.stop_audio_visualizer()
            self.return_to_listening()
        except Exception as e:
            self.root.after(0, lambda: self.log(f"❌ Recording error: {e} - returning to listening"))
            # عودة سريعة للاستماع بدون انتظار
            self.stop_audio_visualizer()
            self.return_to_listening()
    
    def _send_to_ai(self, message) -> Any:
        """إرسال للذكاء الاصطناعي"""
        try:
            data = {
                "audio": message,
                "device_id": self.device_id,
                "session_id": self.session_id or f"session_{int(time.time())}",
                "language": self.current_language,
                "child_profile": self.child_profile
            }
            
            response = requests.post(f"{SERVER_URL}/esp32/audio", json=data, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get("ai_response", {})
                ai_text = ai_response.get("text", "عذراً، لم أفهم")
                emotion = ai_response.get("emotion", "neutral")
                
                self.root.after(0, lambda: self.log(f"🧸 Teddy says: {ai_text}"))
                self.root.after(0, lambda: self.log(f"😊 Emotion: {emotion}"))
                
                # حفظ المحادثة
                self.root.after(0, lambda: self.log_conversation(message, ai_text))
                
                # تشغيل الرد
                self.speak_response(ai_text)
                
            else:
                self.root.after(0, lambda: self.log(f"❌ Server error: {response.status_code}"))
                self.return_to_listening()
                
        except Exception as e:
            self.root.after(0, lambda: self.log(f"❌ AI request failed: {e}"))
            self.return_to_listening()
    
    def _speak_response(self, text) -> Any:
        """تشغيل رد الدبدوب"""
        try:
            # LED بنفسجي = يتكلم
            self.root.after(0, lambda: self.led_canvas.itemconfig(self.led_circle, fill='purple'))
            self.root.after(0, lambda: self.status_label.config(text="🗣️ SPEAKING", fg='purple'))
            
            # تحويل النص لصوت بحسب اللغة
            lang_code = 'ar' if self.current_language == 'ar-SA' else 'en'
            tts = gTTS(text=text, lang=lang_code, slow=False)
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            
            # تشغيل الصوت بمستوى الصوت المحدد
            pygame.mixer.music.set_volume(self.volume_level / 100.0)
            pygame.mixer.music.load(audio_buffer)
            pygame.mixer.music.play()
            
            # بدء المؤشر الصوتي أثناء التحدث فقط
            self.start_audio_visualizer()
            
            # انتظار انتهاء التشغيل
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            
            self.root.after(0, lambda: self.log("🔊 Response played"))
            # إيقاف المؤشر الصوتي
            self.stop_audio_visualizer()
            
        except Exception as e:
            self.root.after(0, lambda: self.log(f"❌ Speech error: {e}"))
            # حاول تشغيل رد بسيط بدلاً من الانطفاء
            try:
                simple_response = "أعتذر، حدث خطأ في النظام الصوتي" if self.current_language == 'ar-SA' else "Sorry, there was an audio system error"
                pygame.mixer.music.stop()
                time.sleep(0.5)
                lang_code = 'ar' if self.current_language == 'ar-SA' else 'en'
                tts_simple = gTTS(text=simple_response, lang=lang_code, slow=False)
                buffer_simple = io.BytesIO()
                tts_simple.write_to_fp(buffer_simple)
                buffer_simple.seek(0)
                pygame.mixer.music.load(buffer_simple)
               except Exception as e:
    logger.error(f"Error in operation: {e}", exc_info=True).mixer.music.play()
                while pygame.mixer.music.get_buexcept Exception as e:
    logger.error(f"Error in operation: {e}", exc_info=True)                  time.sleep(0.1)
            except Exception as e:
    logger.error(f"Error in operation: {e}", exc_info=True)Exception as e:
    logger.error(f"Error in operation: {e}", exc_info=True)                self.root.after(0, lambda: self.log("❌ Fallback speech also failed"))
        
        finally:
            self.stop_audio_visualizer()
            self.return_to_listening()
    
    def _return_to_listening(self) -> Any:
        """العودة لحالة الاستماع"""
        # إيقاف المؤشر الصوتي دائماً عند العودة للاستماع
        self.stop_audio_visualizer()
        
        if self.is_powered_on:
            if not self.wifi_connected:
                # لا يوجد واي فاي
                self.led_canvas.itemconfig(self.led_circle, fill='red')
                self.status_label.config(text="❌ NO WIFI", fg='red')
                self.log("❌ No WiFi - waiting for connection...")
            elif not self.server_connected:
                # واي فاي موجود لكن السيرفر لا
                self.led_canvas.itemconfig(self.led_circle, fill='orange')
                self.status_label.config(text="⚠️ SERVER OFFLINE", fg='orange')
                self.log("⚠️ Server disconnected - waiting for reconnection...")
            else:
                # كل شيء متصل
                self.led_canvas.itemconfig(self.led_circle, fill='green')
                self.status_label.config(text="🟢 LISTENING", fg='green')
                self.log("👂 Back to listening for wake words...")
        else:
            self.log("💡 Teddy is powered off")
    
    # ======================== CONTROLS ========================
    
    def _volume_up(self) -> Any:
        self.volume_level = min(100, self.volume_level + 10)
        self.volume_scale.set(self.volume_level)
        self.volume_changed(self.volume_level)
    
    def _volume_down(self) -> Any:
        self.volume_level = max(0, self.volume_level - 10)
        self.volume_scale.set(self.volume_level)
        self.volume_changed(self.volume_level)
    
    def _volume_changed(self, value) -> Any:
        self.volume_level = int(float(value))
        self.volume_label.config(text=f"🔊 Volume: {self.volume_level}%")
        if self.wifi_connected:
            # إرسال مستوى الصوت للسيرفر
            try:
    except Exception as e:
    logger.error(f"Error in operation: {e}", exc_info=True)     requests.post(f"{SERVER_URL}/esp32/volume", json={
                    "device_id": self.device_id,
                    "volume": self.vexcept Exception as e:
    logger.error(f"Error in operation: {e}", exc_info=True)vel
                }, timeout=2)except Exception as e:
    logger.warning(f"Ignoring error: {e}")         pass
    
    def _sensitivity_up(self) -> Any:
        current = self.sensitivity_scale.get()
        new_value = min(1000, current + 50)
        self.sensitivity_scale.set(new_value)
        self.sensitivity_changed(new_value)
    
    def _sensitivity_down(self) -> Any:
        current = self.sensitivity_scale.get()
        new_value = max(100, current - 50)
        self.sensitivity_scale.set(new_value)
        self.sensitivity_changed(new_value)
    
    def _sensitivity_changed(self, value) -> Any:
        threshold = int(float(value))
        self.recognizer.energy_threshold = threshold
        self.sensitivity_label.config(text=f"Sensitivity: {threshold}")
        self.log(f"🎤 Microphone sensitivity set to: {threshold}")
        # إعادة تعديل إعدادات الميكروفون الأخرى حسب الحساسية
        if threshold < 200:
            self.recognizer.pause_threshold = 0.5  # أكثر حساسية
            self.recognizer.phrase_threshold = 0.2
        elif threshold > 500:
            self.recognizer.pause_threshold = 1.2  # أقل حساسية
            self.recognizer.phrase_threshold = 0.5
        else:
            self.recognizer.pause_threshold = 0.8  # متوسط
            self.recognizer.phrase_threshold = 0.3
    
    def _full_restart(self) -> Any:
        """إعادة تشغيل كاملة للنظام"""
        self.log("🔄 Full system restart initiated...")
        
        # إيقاف كل شيء
        self.power_off()
        pygame.mixer.stop()
        
        # انتظار ثانية
        time.sleep(1)
        
        # إعادة تشغيل النظام الصوتي
        self.restart_audio_system()
        
        # إعادة تشغيل الدبدوب
        threading.Timer(2.0, self.power_on).start()
        
        self.log("🔄 System restart completed")
    
    def _emergency_stop(self) -> Any:
        """إيقاف طوارئ"""
        self.power_off()
        pygame.mixer.stop()
        self.log("🛑 EMERGENCY STOP ACTIVATED")
    
    def _restart_audio_system(self) -> Any:
        """إعادة تشغيل نظام الصوت"""
        try:
            self.log("🔄 Restarting audio system...")
            
            # إعادة تهيئة الصوت
            pygame.mixer.quit()
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            
            # إعادة تهيئة الميكروفون
            self.microphone = sr.Microphone()
            self.recognizer = sr.Recognizer()
            
            # معايرة جديدة
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            self.log("✅ Audio system restarted successfully")
            
            # إعادة بدء الاستماع إذا كان الدبدوب مشغل
            if self.is_powered_on and self.wifi_connected:
                self.start_listening()
                
        except Exception as e:
            self.log(f"❌ Audio restart failed: {e}")
    
    def _save_child_profile(self) -> Any:
        """حفظ ملف الطفل"""
        name = self.child_name.get().strip()
        age = self.child_age.get()
        
        if not name:
            self.log("⚠️ Please enter child's name")
            return
        
        self.child_profile = {
            "name": name,
            "age": int(age),
            "device_id": self.device_id,
            "language": "Arabic"
        }
        
        # تحديث المؤشر فوراً
        self.profile_status_label.config(text=f"👶 Profile: {name}, {age}y", fg='green')
        self.log(f"✅ Child profile set: {name}, {age} years old")
        
        # إرسال للسيرفر (اختياري)
        if self.wifi_connected:
            try:
                response = requests.post(f"{SERVER_URL}/api/children", json=self.child_profile, timeout=5)
                if response.status_code == 200:
                    self.log("✅ Profile synced with cloud")
                else:
                    self.log("⚠️ Profile saved locally only")
            except Exception as e:
                self.log(f"⚠️ Cloud sync failed, saved locally: {e}")
        else:
            self.log("⚠️ Profile saved locally, will sync when connected")
    
    # ======================== ADVANCED FEATURES ========================
    
    def test_games(self) -> Any:
        """اختبار الألعاب"""
        self.log("🎮 Testing educational games...")
        self.send_test_message("هل نلعب لعبة تعليمية؟")
    
    def test_stories(self) -> Any:
        """اختبار القصص"""
        self.log("📚 Testing interactive stories...")
        self.send_test_message("احكي لي قصة جميلة")
    
    def test_songs(self) -> Any:
        """اختبار الأغاني"""
        self.log("🎵 Testing songs and music...")
        self.send_test_message("غني لي أغنية")
    
    def test_learning(self) -> Any:
        """اختبار التعلم"""
        self.log("🧠 Testing learning modules...")
        self.send_test_message("علمني الألوان")
    
    def test_emotions(self) -> Any:
        """اختبار تحليل المشاعر"""
        self.log("😊 Testing emotion detection...")
        self.send_test_message("أنا سعيد اليوم")
    
    def test_family(self) -> Any:
        """اختبار النظام العائلي"""
        self.log("👨‍👩‍👧‍👦 Testing family system...")
        self.send_test_message("أين أمي؟")
    
    def send_test_message(self, message) -> Any:
        """إرسال رسالة تجريبية"""
        if self.wifi_connected:
            threading.Thread(target=lambda: self.send_to_ai(message), daemon=True).start()
        else:
            self.log("❌ Please connect to server first")
    
    def quick_test(self) -> Any:
        """اختبار سريع لمحاكاة كلمة التفعيل"""
        self.log("🧪 Quick Test: Simulating 'يا دبدوب' + 'مرحبا'")
        self.wake_word_detected("يا دبدوب", "يا دبدوب مرحبا")
    
    def test_server(self) -> Any:
        """اختبار الاتصال بالسيرفر"""
        self.log("🔍 Testing server connection...")
        try:
            response = requests.get(f"{SERVER_URL}/health", timeout=5)
            if response.status_code == 200:
                self.log("✅ Server is responding correctly")
                self.log(f"📊 Response: {response.json()}")
            else:
                self.log(f"❌ Server error: {response.status_code}")
        except Exception as e:
            self.log(f"❌ Server connection failed: {e}")
    
    def test_tts(self) -> Any:
        """اختبار تحويل النص لصوت"""
        self.log("🎵 Testing Text-to-Speech...")
        test_text = "مرحباً! هذا اختبار للنظام الصوتي"
        threading.Thread(target=lambda: self.speak_response(test_text), daemon=True).start()
    
    def test_ai_direct(self) -> Any:
        """اختبار الذكاء الاصطناعي مباشرة"""
        self.log("💬 Testing AI with: 'ما هو اسمك؟'")
        threading.Thread(target=lambda: self.send_to_ai("ما هو اسمك؟"), daemon=True).start()
    
    def _force_stay_alive(self) -> Any:
        """منع إطفاء الدبدوب تلقائياً"""
        self.log("🛡️ KEEP ALIVE mode activated")
        if not self.is_powered_on:
            self.power_on()
        
        # إعادة تشغيل كل شيء
        self.restart_audio_system()
        threading.Timer(2.0, self.start_listening).start()
        self.log("✅ System forced to stay alive")
    
    def _force_fix_system(self) -> Any:
        """إصلاح إجباري للنظام"""
        self.log("🔧 FORCE FIX initiexcept Exception as e:
    logger.error(f"Error in operation: {e}", exc_info=True)")
        
        # إيقاف كل شيء
        self.is_powered_on = False
        time.sleep(1)
        
        # إعادة تهيئة كاملة
        try:
            pygame.mixer.quit()
            pygame.mixer.init()
         except Exception as e:
    logger.error(f"Error in operation: {e}", exc_info=True)microphone = sr.Microphone()
            self.recognizer = sr.Recognizexcept Exception as e:
    logger.warning(f"Ignoring error: {e}")         pass
        
        # إعادة تشغيل
        self.is_powered_on = True
        self.led_canvas.itemconfig(self.led_circle, fill='green')
        self.status_label.config(text="🔧 FORCE FIXED", fg='green')
        self.power_button.config(text="🔌 POWER OFF", bg='#e74c3c')
        
        self.log("🔧 System force-fixed and restarted")
        threading.Timer(2.0, self.start_listening).start()
    
    def _start_server_monitor(self) -> Any:
        """بدء مراقبة السيرفر المستمرة"""
        if not self.server_monitor_active:
            self.server_monitor_active = True
            self.log("🔍 Starting server monitor...")
            threading.Thread(target=self.monitor_server_continuously, daemon=True).start()
    
    def _monitor_server_continuously(self) -> Any:
        """مراقبة مستمرة لحالة السيرفر"""
        while self.server_monitor_active:
            try:
                # فحص السيرفر كل 10 ثوان
                time.sleep(10)
                
                if not self.is_powered_on:
                    continue
                
                # أولاً: فحص الواي فاي (محاكاة)
                wifi_ok = True  # في الواقع ستكون فحص حقيقي
                
                if not wifi_ok:
                    # الواي فاي منقطع
                    if self.wifi_connected:
                        self.wifi_connected = False
                        self.server_connected = False
                        self.root.after(0, lambda: self.wifi_label.config(text="📶 WiFi: Disconnected ❌"))
                        self.root.after(0, lambda: self.server_status_label.config(text="🔴 Server: No WiFi", fg='red'))
                        self.root.after(0, lambda: self.log("❌ WiFi connection lost"))
                        self.root.after(0, lambda: self.led_canvas.itemconfig(self.led_circle, fill='red'))
                    continue
                
                # ثانياً: فحص السيرفر (إذا كان الواي فاي متصل)
                if self.wifi_connected:
                    response = requests.get(f"{SERVER_URL}/health", timeout=3)
                    
                    if response.status_code == 200:
                        # السيرفر متصل
                        if not self.server_connected:
                            self.server_connected = True
                            self.root.after(0, lambda: self.server_status_label.config(text="🟢 Server: Connected", fg='green'))
                            self.root.after(0, lambda: self.log("✅ Server connection restored"))
                            
                            # إذا كان الدبدوب مشغل، استعد الاستماع
                            if self.is_powered_on and self.wifi_connected:
                                self.root.after(0, lambda: self.led_canvas.itemconfig(self.led_circle, fill='green'))
                                self.root.after(0, lambda: self.status_label.config(text="🟢 LISTENING", fg='green'))
                                self.root.after(0, lambda: self.start_listening())
                    else:
                        raise Exception("Server not responding")
                    
            except Exception as e:
                # السيرفر منقطع (لكن الواي فاي متصل)
                if self.server_connected:
                    self.server_connected = False
                    self.root.after(0, lambda: self.server_status_label.config(text="🔴 Server: Disconnected", fg='red'))
                    self.root.after(0, lambda: self.log(f"❌ Server connection lost: {e}"))
                    
                    # إذا كان الدبدوب مشغل، اجعل الضوء برتقالي (واي فاي موجود لكن سيرفر لا)
                    if self.is_powered_on:
                        self.root.after(0, lambda: self.led_canvas.itemconfig(self.led_circle, fill='orange'))
                        self.root.after(0, lambda: self.status_label.config(text="⚠️ SERVER OFFLINE", fg='orange'))
    
    def _show_reports(self) -> Any:
        """عرض التقارير"""
        analytics_data = f"""
📊 ESP32 Teddy Bear Analytics Report
=================================

👶 Child Profile:
{self.child_profile if self.child_profile else "No profile set"}

💬 Total Conversations: {len(self.conversation_history)}

🎯 Recent Activity:
"""
        for conv in self.conversation_history[-5:]:
            analytics_data += f"[{conv['timestamp']}] 👶: {conv['user']}\n"
            analytics_data += f"[{conv['timestamp']}] 🧸: {conv['ai']}\n\n"
        
        analytics_data += f"""
🔊 Current Volume: {self.volume_level}%
📶 WiFi Status: {"Connected" if self.wifi_connected else "Disconnected"}
🔋 Power Status: {"ON" if self.is_powered_on else "OFF"}
🆔 Device ID: {self.device_id}
"""
        
        self.analytics_text.delete(1.0, "end")
        self.analytics_text.insert(1.0, analytics_data)
        self.log("📊 Analytics updated")
    
    def _show_settings(self) -> Any:
        """عرض الإعدادات"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("⚙️ ESP32 Teddy Settings")
        settings_window.geometry("400x300")
        settings_window.configure(bg='#ecf0f1')
        
        tk.Label(settings_window, text="⚙️ Device Settings", font=('Arial', 16, 'bold'), bg='#ecf0f1').pack(pady=20)
        
        # WiFi Settings
        wifi_frame = tk.LabelFrame(settings_window, text="WiFi Configuration", bg='#ecf0f1')
        wifi_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(wifi_frame, text="SSID:", bg='#ecf0f1').grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ssid_entry = tk.Entry(wifi_frame, width=20)
        ssid_entry.insert(0, "TeddyBear_WiFi")
        ssid_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(wifi_frame, text="Password:", bg='#ecf0f1').grid(row=1, column=0, sticky="w", padx=5, pady=5)
        password_entry = tk.Entry(wifi_frame, show="*", width=20)
        password_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Voice Settings
        voice_frame = tk.LabelFrame(settings_window, text="Voice Configuration", bg='#ecf0f1')
        voice_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(voice_frame, text="Voice Speed:", bg='#ecf0f1').grid(row=0, column=0, sticky="w", padx=5, pady=5)
        speed_scale = tk.Scale(voice_frame, from_=0.5, to=2.0, resolution=0.1, orient="horizontal")
        speed_scale.set(1.0)
        speed_scale.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Button(settings_window, text="💾 Save Settings", bg='#27ae60', fg='white').pack(pady=20)
    
    def _run(self) -> Any:
        """تشغيل المحاكي"""
        try:
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.root.mainloop()
        except Exception as e:
    logger.error(f"Error: {e}")"\n👋 ESP32 Simulator shutting down...")
        finally:
            self.power_off()
    
    def _on_closing(self) -> Any:
        """عند إغلاق النافذة"""
        self.server_monitor_active = False  # إيقاف مراقبة السيرفر
        self.power_off()
        self.root.destroy()

if __name__ == "__main__":
    logger.info("🧸 Starting ESP32 Teddy Bear Simulator...")
    logger.info("=" * 60)
    logger.info("🎯 Complete Production Simulator")
    logger.info("🔌 Hardware: ESP32-S3 with full audio system")
    logger.info("☁️ Cloud: AI processing with advanced features")
    logger.info("🎤 Wake Word: 'يا دبدوب'")
    logger.info("🎮 Features: Games, Stories, Learning, Emotions")
    logger.info("=" * 60)
    
    try:
        simulator = ESP32TeddyBearSimulator()
        simulator.run()
    except Exception as e:
    logger.error(f"Error: {e}")f"❌ Simulator error: {e}") 