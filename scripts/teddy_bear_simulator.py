#!/usr/bin/env python3
"""
🧸 AI Teddy Bear Simulator - Enterprise Edition 2025
يحاكي جهاز ESP32 للدب الذكي مع ربط مباشر بالميكروفون والسبيكر
"""

import asyncio
import json
import logging
import os
import queue
import threading
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, Callable

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import websockets
import requests
import pyaudio
import wave
import tempfile
from io import BytesIO
import pygame
from concurrent.futures import ThreadPoolExecutor
import aiohttp
import base64


# ================== CONFIGURATION ==================

class TeddyConfig:
    """إعدادات المحاكي"""
    
    # Server Configuration
    SERVER_HOST = "localhost"
    SERVER_PORT = 5000
    WEBSOCKET_PORT = 8765
    
    # Audio Configuration
    SAMPLE_RATE = 22050
    CHANNELS = 1
    CHUNK_SIZE = 1024
    AUDIO_FORMAT = pyaudio.paInt16
    RECORD_SECONDS = 10  # Maximum recording time
    
    # Device Configuration
    DEVICE_ID = f"TEDDY_SIM_{uuid.uuid4().hex[:8]}"
    CHILD_NAME = "طفل تجريبي"
    CHILD_AGE = 7
    
    # UI Configuration
    WINDOW_TITLE = "🧸 محاكي الدب الذكي - AI Teddy Simulator"
    WINDOW_SIZE = "800x600"
    
    # File Paths
    TEMP_AUDIO_FILE = tempfile.gettempdir() + "/teddy_recording.wav"
    LOG_FILE = "logs/teddy_simulator.log"


# ================== AUDIO MANAGER ==================

class AudioManager:
    """إدارة تسجيل وتشغيل الصوت"""
    
    def __init__(self, config: TeddyConfig):
        self.config = config
        self.audio = pyaudio.PyAudio()
        self.is_recording = False
        self.is_playing = False
        
        # Initialize pygame for audio playback
        pygame.mixer.init()
        
        # Audio streams
        self.recording_stream = None
        self.audio_data = []
        
        self.logger = logging.getLogger(__name__)
    
    def start_recording(self) -> bool:
        """بدء تسجيل الصوت"""
        try:
            if self.is_recording:
                return False
            
            self.audio_data = []
            self.is_recording = True
            
            # Open audio stream
            self.recording_stream = self.audio.open(
                format=self.config.AUDIO_FORMAT,
                channels=self.config.CHANNELS,
                rate=self.config.SAMPLE_RATE,
                input=True,
                frames_per_buffer=self.config.CHUNK_SIZE
            )
            
            self.logger.info("🎤 بدء تسجيل الصوت")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في بدء التسجيل: {e}")
            return False
    
    def stop_recording(self) -> Optional[bytes]:
        """إيقاف تسجيل الصوت وإرجاع البيانات"""
        try:
            if not self.is_recording:
                return None
            
            self.is_recording = False
            
            # Stop and close stream
            if self.recording_stream:
                self.recording_stream.stop_stream()
                self.recording_stream.close()
                self.recording_stream = None
            
            # Save audio data to file
            if self.audio_data:
                audio_bytes = self._save_audio_to_bytes()
                self.logger.info("🎤 تم إيقاف التسجيل")
                return audio_bytes
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في إيقاف التسجيل: {e}")
            return None
    
    def record_audio_chunk(self) -> None:
        """تسجيل جزء من الصوت"""
        if self.is_recording and self.recording_stream:
            try:
                data = self.recording_stream.read(
                    self.config.CHUNK_SIZE, exception_on_overflow=False
                )
                self.audio_data.append(data)
            except Exception as e:
                self.logger.error(f"❌ خطأ في تسجيل الصوت: {e}")
    
    def _save_audio_to_bytes(self) -> bytes:
        """حفظ البيانات الصوتية كـ bytes"""
        try:
            # Create temporary file
            with wave.open(self.config.TEMP_AUDIO_FILE, 'wb') as wf:
                wf.setnchannels(self.config.CHANNELS)
                wf.setsampwidth(self.audio.get_sample_size(self.config.AUDIO_FORMAT))
                wf.setframerate(self.config.SAMPLE_RATE)
                wf.writeframes(b''.join(self.audio_data))
            
            # Read file as bytes
            with open(self.config.TEMP_AUDIO_FILE, 'rb') as f:
                return f.read()
                
        except Exception as e:
            self.logger.error(f"❌ خطأ في حفظ الصوت: {e}")
            return b''
    
    def play_audio_from_bytes(self, audio_bytes: bytes) -> bool:
        """تشغيل الصوت من البيانات"""
        try:
            if self.is_playing:
                return False
            
            self.is_playing = True
            
            # Save bytes to temporary file
            temp_file = tempfile.gettempdir() + "/teddy_response.wav"
            with open(temp_file, 'wb') as f:
                f.write(audio_bytes)
            
            # Play using pygame
            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()
            
            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)
            
            self.is_playing = False
            self.logger.info("🔊 تم تشغيل الرد الصوتي")
            
            # Clean up
            try:
                os.remove(temp_file)
            except:
                pass
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في تشغيل الصوت: {e}")
            self.is_playing = False
            return False
    
    def cleanup(self) -> None:
        """تنظيف الموارد"""
        if self.is_recording:
            self.stop_recording()
        
        if self.recording_stream:
            self.recording_stream.close()
        
        self.audio.terminate()
        pygame.mixer.quit()


# ================== SERVER COMMUNICATOR ==================

class ServerCommunicator:
    """التواصل مع السيرفر"""
    
    def __init__(self, config: TeddyConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.session = None
        self.websocket = None
        
        # Server URLs
        self.base_url = f"http://{config.SERVER_HOST}:{config.SERVER_PORT}"
        self.ws_url = f"ws://{config.SERVER_HOST}:{config.WEBSOCKET_PORT}"
        
        # Session info
        self.session_id = str(uuid.uuid4())
    
    async def connect_websocket(self) -> bool:
        """الاتصال بـ WebSocket"""
        try:
            self.websocket = await websockets.connect(f"{self.ws_url}/ws/teddy/{self.session_id}")
            self.logger.info("🌐 تم الاتصال بـ WebSocket")
            return True
        except Exception as e:
            self.logger.error(f"❌ خطأ في الاتصال بـ WebSocket: {e}")
            return False
    
    async def send_audio_websocket(self, audio_bytes: bytes) -> Optional[Dict[str, Any]]:
        """إرسال الصوت عبر WebSocket"""
        try:
            if not self.websocket:
                return None
            
            # Encode audio as base64
            audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
            
            message = {
                "type": "audio_message",
                "device_id": self.config.DEVICE_ID,
                "session_id": self.session_id,
                "audio_data": audio_b64,
                "child_name": self.config.CHILD_NAME,
                "child_age": self.config.CHILD_AGE,
                "timestamp": datetime.now().isoformat()
            }
            
            await self.websocket.send(json.dumps(message))
            
            # Wait for response
            response = await self.websocket.recv()
            response_data = json.loads(response)
            
            self.logger.info("📤 تم إرسال الصوت واستلام الرد عبر WebSocket")
            return response_data
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في إرسال الصوت عبر WebSocket: {e}")
            return None
    
    async def send_audio_http(self, audio_bytes: bytes) -> Optional[Dict[str, Any]]:
        """إرسال الصوت عبر HTTP API"""
        try:
            async with aiohttp.ClientSession() as session:
                # Prepare multipart data
                data = aiohttp.FormData()
                data.add_field('audio_file', audio_bytes, filename='recording.wav', content_type='audio/wav')
                data.add_field('device_id', self.config.DEVICE_ID)
                data.add_field('child_context', json.dumps({
                    "name": self.config.CHILD_NAME,
                    "age": self.config.CHILD_AGE,
                    "session_id": self.session_id
                }))
                
                # Send request
                async with session.post(
                    f"{self.base_url}/api/audio/process-full",
                    data=data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        self.logger.info("📤 تم إرسال الصوت واستلام الرد عبر HTTP")
                        return result
                    else:
                        self.logger.error(f"❌ خطأ HTTP {response.status}")
                        return None
                        
        except Exception as e:
            self.logger.error(f"❌ خطأ في إرسال الصوت عبر HTTP: {e}")
            return None
    
    async def get_audio_response(self, response_url: str) -> Optional[bytes]:
        """تحميل الرد الصوتي"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}{response_url}") as response:
                    if response.status == 200:
                        audio_bytes = await response.read()
                        self.logger.info("🔊 تم تحميل الرد الصوتي")
                        return audio_bytes
                    else:
                        return None
        except Exception as e:
            self.logger.error(f"❌ خطأ في تحميل الرد الصوتي: {e}")
            return None
    
    def cleanup(self) -> None:
        """تنظيف الاتصالات"""
        if self.websocket:
            asyncio.create_task(self.websocket.close())


# ================== MAIN GUI APPLICATION ==================

class TeddyBearSimulator:
    """التطبيق الرئيسي للمحاكي"""
    
    def __init__(self):
        self.config = TeddyConfig()
        self.setup_logging()
        
        # Initialize components
        self.audio_manager = AudioManager(self.config)
        self.server_comm = ServerCommunicator(self.config)
        
        # GUI components
        self.root = None
        self.create_gui()
        
        # Threading
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.recording_thread = None
        
        # State
        self.is_connected = False
        self.last_response = None
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("🧸 تم تشغيل محاكي الدب الذكي")
    
    def setup_logging(self) -> None:
        """إعداد نظام التسجيل"""
        # Create logs directory
        Path("logs").mkdir(exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.config.LOG_FILE, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
    
    def create_gui(self) -> None:
        """إنشاء واجهة المستخدم"""
        self.root = tk.Tk()
        self.root.title(self.config.WINDOW_TITLE)
        self.root.geometry(self.config.WINDOW_SIZE)
        self.root.configure(bg='#f0f0f0')
        
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Device Info Frame
        info_frame = ttk.LabelFrame(main_frame, text="معلومات الجهاز", padding="10")
        info_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(info_frame, text=f"معرف الجهاز: {self.config.DEVICE_ID}").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(info_frame, text=f"اسم الطفل: {self.config.CHILD_NAME}").grid(row=1, column=0, sticky=tk.W)
        ttk.Label(info_frame, text=f"عمر الطفل: {self.config.CHILD_AGE}").grid(row=2, column=0, sticky=tk.W)
        
        # Connection Frame
        conn_frame = ttk.LabelFrame(main_frame, text="الاتصال بالسيرفر", padding="10")
        conn_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.connection_status = ttk.Label(conn_frame, text="غير متصل", foreground="red")
        self.connection_status.grid(row=0, column=0, sticky=tk.W)
        
        self.connect_btn = ttk.Button(conn_frame, text="اتصال", command=self.toggle_connection)
        self.connect_btn.grid(row=0, column=1, padx=(10, 0))
        
        # Audio Control Frame
        audio_frame = ttk.LabelFrame(main_frame, text="التحكم في الصوت", padding="10")
        audio_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.record_btn = ttk.Button(audio_frame, text="🎤 بدء التسجيل", command=self.toggle_recording)
        self.record_btn.grid(row=0, column=0, padx=(0, 10))
        
        self.send_btn = ttk.Button(audio_frame, text="📤 إرسال للسيرفر", command=self.send_audio, state="disabled")
        self.send_btn.grid(row=0, column=1, padx=(0, 10))
        
        self.play_btn = ttk.Button(audio_frame, text="🔊 تشغيل الرد", command=self.play_response, state="disabled")
        self.play_btn.grid(row=0, column=2)
        
        # Recording Status
        self.recording_status = ttk.Label(audio_frame, text="جاهز للتسجيل")
        self.recording_status.grid(row=1, column=0, columnspan=3, pady=(10, 0))
        
        # Protocol Selection
        protocol_frame = ttk.LabelFrame(main_frame, text="بروتوكول الاتصال", padding="10")
        protocol_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.protocol_var = tk.StringVar(value="http")
        ttk.Radiobutton(protocol_frame, text="HTTP API", variable=self.protocol_var, value="http").grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(protocol_frame, text="WebSocket", variable=self.protocol_var, value="websocket").grid(row=0, column=1, sticky=tk.W, padx=(20, 0))
        
        # Response Display
        response_frame = ttk.LabelFrame(main_frame, text="آخر رد من السيرفر", padding="10")
        response_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        self.response_text = scrolledtext.ScrolledText(response_frame, height=8, width=70)
        self.response_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Log Display
        log_frame = ttk.LabelFrame(main_frame, text="سجل الأحداث", padding="10")
        log_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=6, width=70)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(4, weight=1)
        main_frame.grid_rowconfigure(5, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Setup log handler
        self.setup_gui_log_handler()
    
    def setup_gui_log_handler(self) -> None:
        """إعداد معالج السجل للواجهة"""
        class GUILogHandler(logging.Handler):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget
            
            def emit(self, record):
                msg = self.format(record)
                def append():
                    self.text_widget.insert(tk.END, msg + '\n')
                    self.text_widget.see(tk.END)
                    # Keep only last 1000 lines
                    lines = self.text_widget.get("1.0", tk.END).split('\n')
                    if len(lines) > 1000:
                        self.text_widget.delete("1.0", f"{len(lines)-1000}.0")
                
                # Schedule GUI update
                self.text_widget.after(0, append)
        
        # Add GUI handler to root logger
        gui_handler = GUILogHandler(self.log_text)
        gui_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(gui_handler)
    
    def toggle_connection(self) -> None:
        """تبديل حالة الاتصال"""
        if self.is_connected:
            self.disconnect()
        else:
            self.connect()
    
    def connect(self) -> None:
        """الاتصال بالسيرفر"""
        def connect_task():
            try:
                # Test connection
                response = requests.get(f"{self.server_comm.base_url}/health", timeout=5)
                if response.status_code == 200:
                    self.is_connected = True
                    self.root.after(0, lambda: self.connection_status.config(text="متصل", foreground="green"))
                    self.root.after(0, lambda: self.connect_btn.config(text="قطع الاتصال"))
                    self.logger.info("✅ تم الاتصال بالسيرفر")
                else:
                    raise Exception(f"Server returned {response.status_code}")
            except Exception as e:
                self.logger.error(f"❌ فشل الاتصال بالسيرفر: {e}")
                messagebox.showerror("خطأ في الاتصال", f"لا يمكن الاتصال بالسيرفر:\n{e}")
        
        self.executor.submit(connect_task)
    
    def disconnect(self) -> None:
        """قطع الاتصال"""
        self.is_connected = False
        self.server_comm.cleanup()
        self.connection_status.config(text="غير متصل", foreground="red")
        self.connect_btn.config(text="اتصال")
        self.logger.info("🔌 تم قطع الاتصال")
    
    def toggle_recording(self) -> None:
        """تبديل حالة التسجيل"""
        if self.audio_manager.is_recording:
            self.stop_recording()
        else:
            self.start_recording()
    
    def start_recording(self) -> None:
        """بدء التسجيل"""
        if self.audio_manager.start_recording():
            self.record_btn.config(text="⏹️ إيقاف التسجيل")
            self.recording_status.config(text="🔴 جاري التسجيل...")
            self.send_btn.config(state="disabled")
            
            # Start recording thread
            self.recording_thread = threading.Thread(target=self.recording_loop)
            self.recording_thread.daemon = True
            self.recording_thread.start()
    
    def stop_recording(self) -> None:
        """إيقاف التسجيل"""
        audio_data = self.audio_manager.stop_recording()
        self.record_btn.config(text="🎤 بدء التسجيل")
        self.recording_status.config(text="⏸️ تم إيقاف التسجيل")
        
        if audio_data:
            self.send_btn.config(state="normal")
            self.last_recording = audio_data
            self.logger.info(f"📼 تم تسجيل {len(audio_data)} بايت")
        else:
            self.recording_status.config(text="❌ فشل التسجيل")
    
    def recording_loop(self) -> None:
        """حلقة التسجيل"""
        start_time = time.time()
        while self.audio_manager.is_recording:
            self.audio_manager.record_audio_chunk()
            
            # Auto-stop after max duration
            if time.time() - start_time > self.config.RECORD_SECONDS:
                self.root.after(0, self.stop_recording)
                break
            
            time.sleep(0.01)  # Small delay
    
    def send_audio(self) -> None:
        """إرسال الصوت للسيرفر"""
        if not self.is_connected:
            messagebox.showwarning("تحذير", "يجب الاتصال بالسيرفر أولاً")
            return
        
        if not hasattr(self, 'last_recording'):
            messagebox.showwarning("تحذير", "لا يوجد تسجيل صوتي")
            return
        
        # Disable button during processing
        self.send_btn.config(state="disabled", text="📤 جاري الإرسال...")
        
        def send_task():
            try:
                protocol = self.protocol_var.get()
                
                if protocol == "websocket":
                    # Use WebSocket
                    response = asyncio.run(self._send_via_websocket())
                else:
                    # Use HTTP
                    response = asyncio.run(self._send_via_http())
                
                if response:
                    self.last_response = response
                    self.root.after(0, lambda: self._display_response(response))
                    self.root.after(0, lambda: self.play_btn.config(state="normal"))
                else:
                    self.root.after(0, lambda: messagebox.showerror("خطأ", "فشل في إرسال الصوت"))
                
            except Exception as e:
                self.logger.error(f"❌ خطأ في إرسال الصوت: {e}")
                self.root.after(0, lambda: messagebox.showerror("خطأ", f"خطأ في الإرسال:\n{e}"))
            finally:
                self.root.after(0, lambda: self.send_btn.config(state="normal", text="📤 إرسال للسيرفر"))
        
        self.executor.submit(send_task)
    
    async def _send_via_websocket(self) -> Optional[Dict[str, Any]]:
        """إرسال عبر WebSocket"""
        if not await self.server_comm.connect_websocket():
            return None
        return await self.server_comm.send_audio_websocket(self.last_recording)
    
    async def _send_via_http(self) -> Optional[Dict[str, Any]]:
        """إرسال عبر HTTP"""
        return await self.server_comm.send_audio_http(self.last_recording)
    
    def _display_response(self, response: Dict[str, Any]) -> None:
        """عرض الرد"""
        self.response_text.delete("1.0", tk.END)
        self.response_text.insert("1.0", json.dumps(response, ensure_ascii=False, indent=2))
        self.logger.info("📄 تم استلام الرد من السيرفر")
    
    def play_response(self) -> None:
        """تشغيل الرد الصوتي"""
        if not self.last_response:
            messagebox.showwarning("تحذير", "لا يوجد رد صوتي")
            return
        
        # Disable button during playback
        self.play_btn.config(state="disabled", text="🔊 جاري التشغيل...")
        
        def play_task():
            try:
                # Get audio URL from response
                audio_url = self.last_response.get("audio_response_url")
                if audio_url:
                    # Download and play audio
                    audio_bytes = asyncio.run(self.server_comm.get_audio_response(audio_url))
                    if audio_bytes:
                        self.audio_manager.play_audio_from_bytes(audio_bytes)
                    else:
                        self.logger.error("❌ فشل في تحميل الرد الصوتي")
                else:
                    # Use TTS for text response
                    text_response = self.last_response.get("ai_response", {}).get("text", "")
                    if text_response:
                        self.logger.info(f"📝 النص: {text_response}")
                        # Could implement TTS here
                    else:
                        self.logger.warning("⚠️ لا يوجد نص أو صوت في الرد")
                
            except Exception as e:
                self.logger.error(f"❌ خطأ في تشغيل الرد: {e}")
            finally:
                self.root.after(0, lambda: self.play_btn.config(state="normal", text="🔊 تشغيل الرد"))
        
        self.executor.submit(play_task)
    
    def run(self) -> None:
        """تشغيل التطبيق"""
        try:
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.root.mainloop()
        except KeyboardInterrupt:
            self.logger.info("⏹️ تم إيقاف التطبيق بواسطة المستخدم")
        finally:
            self.cleanup()
    
    def on_closing(self) -> None:
        """معالجة إغلاق التطبيق"""
        if messagebox.askokcancel("إغلاق", "هل تريد إغلاق المحاكي؟"):
            self.cleanup()
            self.root.destroy()
    
    def cleanup(self) -> None:
        """تنظيف الموارد"""
        self.logger.info("🧹 تنظيف الموارد...")
        
        if self.is_connected:
            self.disconnect()
        
        self.audio_manager.cleanup()
        self.server_comm.cleanup()
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        # Clean up temp files
        try:
            if os.path.exists(self.config.TEMP_AUDIO_FILE):
                os.remove(self.config.TEMP_AUDIO_FILE)
        except:
            pass


# ================== MAIN EXECUTION ==================

def main():
    """الدالة الرئيسية"""
    try:
        # Create and run simulator
        simulator = TeddyBearSimulator()
        simulator.run()
        
    except Exception as e:
        logging.error(f"❌ خطأ في تشغيل المحاكي: {e}")
        messagebox.showerror("خطأ فادح", f"خطأ في تشغيل المحاكي:\n{e}")


if __name__ == "__main__":
    main()