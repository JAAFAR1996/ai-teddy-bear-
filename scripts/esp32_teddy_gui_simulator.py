#!/usr/bin/env python3
"""
🧸 ESP32 Teddy Bear GUI Simulator - Professional Edition
========================================================
محاكي دبدوب ذكي احترافي مع واجهة جرافيكية تفاعلية
يحاكي التجربة الحقيقية للطفل مع الدبدوب
"""

import asyncio
import threading
import tkinter as tk
from tkinter import ttk, messagebox, PhotoImage
import time
import uuid
import json
from datetime import datetime
from typing import Dict, Any
import httpx
from PIL import Image, ImageTk, ImageDraw
import io
import base64

# إعدادات الاتصال
RENDER_URL = "https://ai-teddy-bear.onrender.com"
DEVICE_ID = f"ESP32_TEDDY_{uuid.uuid4().hex[:6].upper()}"

class TeddyBearGUISimulator:
    """محاكي الدبدوب الذكي مع واجهة احترافية"""
    
    def __init__(self):
        self.device_id = DEVICE_ID
        self.server_url = RENDER_URL
        self.client = httpx.AsyncClient(timeout=30.0)
        
        # حالات الدبدوب
        self.teddy_state = "sleeping"  # sleeping, listening, thinking, speaking
        self.is_powered = False
        self.is_connected = False
        
        # إنشاء الواجهة
        self.create_main_window()
        self.create_teddy_interface()
        self.start_animation_loop()
        
        print(f"🧸 Professional Teddy Bear Simulator Started!")
        print(f"🆔 Device: {self.device_id}")
    
    def create_main_window(self):
        """إنشاء النافذة الرئيسية"""
        self.root = tk.Tk()
        self.root.title("🧸 AI Teddy Bear - ESP32 Simulator")
        self.root.geometry("800x900")
        self.root.configure(bg='#2E8B57')  # لون أخضر هادئ
        self.root.resizable(False, False)
        
        # إضافة أيقونة (إذا أمكن)
        try:
            # يمكن إضافة أيقونة هنا
            pass
        except:
            pass
    
    def create_teddy_interface(self):
        """إنشاء واجهة الدبدوب التفاعلية"""
        
        # إطار الرأس
        header_frame = tk.Frame(self.root, bg='#2E8B57', height=80)
        header_frame.pack(fill='x', pady=10)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="🧸 My Smart Teddy Bear",
            font=('Comic Sans MS', 28, 'bold'),
            fg='white',
            bg='#2E8B57'
        )
        title_label.pack(pady=15)
        
        # إطار الدبدوب الرئيسي
        self.teddy_frame = tk.Frame(self.root, bg='#8FBC8F', relief='raised', bd=5)
        self.teddy_frame.pack(pady=20, padx=20, fill='both', expand=True)
        
        # وجه الدبدوب (Canvas للرسم)
        self.teddy_canvas = tk.Canvas(
            self.teddy_frame,
            width=400,
            height=400,
            bg='#DEB887',  # لون بني فاتح
            highlightthickness=0
        )
        self.teddy_canvas.pack(pady=20)
        
        # رسم وجه الدبدوب
        self.draw_teddy_face()
        
        # حالة الدبدوب
        self.status_frame = tk.Frame(self.teddy_frame, bg='#8FBC8F')
        self.status_frame.pack(pady=10)
        
        self.status_label = tk.Label(
            self.status_frame,
            text="😴 Teddy is sleeping...",
            font=('Comic Sans MS', 18, 'bold'),
            fg='#4A4A4A',
            bg='#8FBC8F'
        )
        self.status_label.pack()
        
        # معلومات الجهاز
        info_frame = tk.Frame(self.teddy_frame, bg='#8FBC8F')
        info_frame.pack(pady=10)
        
        device_info = tk.Label(
            info_frame,
            text=f"Device ID: {self.device_id}",
            font=('Arial', 10),
            fg='#666666',
            bg='#8FBC8F'
        )
        device_info.pack()
        
        # أزرار التحكم
        self.create_control_buttons()
        
        # منطقة المحادثة
        self.create_chat_area()
    
    def draw_teddy_face(self):
        """رسم وجه الدبدوب"""
        canvas = self.teddy_canvas
        
        # محو الرسم السابق
        canvas.delete("all")
        
        # الرأس (دائرة كبيرة)
        self.head = canvas.create_oval(50, 50, 350, 350, fill='#CD853F', outline='#8B4513', width=3)
        
        # الأذنين
        self.ear1 = canvas.create_oval(80, 30, 140, 90, fill='#CD853F', outline='#8B4513', width=2)
        self.ear2 = canvas.create_oval(260, 30, 320, 90, fill='#CD853F', outline='#8B4513', width=2)
        
        # العينين (تتغير حسب الحالة)
        if self.teddy_state == "sleeping":
            # عيون مغلقة
            self.eye1 = canvas.create_arc(130, 150, 170, 180, start=0, extent=180, fill='black', width=3)
            self.eye2 = canvas.create_arc(230, 150, 270, 180, start=0, extent=180, fill='black', width=3)
        elif self.teddy_state == "listening":
            # عيون واسعة ومتنبهة
            self.eye1 = canvas.create_oval(130, 150, 170, 190, fill='black', outline='black')
            self.eye2 = canvas.create_oval(230, 150, 270, 190, fill='black', outline='black')
            # نقاط بيضاء في العيون
            canvas.create_oval(145, 160, 155, 170, fill='white')
            canvas.create_oval(245, 160, 255, 170, fill='white')
        elif self.teddy_state == "thinking":
            # عيون تنظر لأعلى
            self.eye1 = canvas.create_oval(130, 140, 170, 180, fill='black')
            self.eye2 = canvas.create_oval(230, 140, 270, 180, fill='black')
            canvas.create_oval(145, 145, 155, 155, fill='white')
            canvas.create_oval(245, 145, 255, 155, fill='white')
        elif self.teddy_state == "speaking":
            # عيون مبتسمة
            self.eye1 = canvas.create_arc(130, 150, 170, 180, start=0, extent=180, fill='black', width=2)
            self.eye2 = canvas.create_arc(230, 150, 270, 180, start=0, extent=180, fill='black', width=2)
        
        # الأنف
        self.nose = canvas.create_oval(190, 200, 210, 220, fill='black')
        
        # الفم (يتغير حسب الحالة)
        if self.teddy_state == "sleeping":
            # فم صغير
            self.mouth = canvas.create_arc(180, 240, 220, 270, start=0, extent=180, fill='black', width=2)
        elif self.teddy_state == "speaking":
            # فم مفتوح
            self.mouth = canvas.create_oval(180, 240, 220, 280, fill='#8B0000', outline='black', width=2)
        else:
            # ابتسامة
            self.mouth = canvas.create_arc(160, 230, 240, 290, start=0, extent=180, outline='black', width=3)
        
        # إضافة تأثيرات حسب الحالة
        if self.teddy_state == "listening":
            # أضواء حول الأذنين
            canvas.create_oval(70, 20, 150, 100, outline='yellow', width=3, dash=(5, 5))
            canvas.create_oval(250, 20, 330, 100, outline='yellow', width=3, dash=(5, 5))
        elif self.teddy_state == "thinking":
            # فقاعات تفكير
            canvas.create_oval(320, 80, 340, 100, outline='lightblue', width=2)
            canvas.create_oval(340, 60, 355, 75, outline='lightblue', width=2)
            canvas.create_oval(350, 45, 360, 55, outline='lightblue', width=2)
    
    def create_control_buttons(self):
        """إنشاء أزرار التحكم"""
        control_frame = tk.Frame(self.teddy_frame, bg='#8FBC8F')
        control_frame.pack(pady=15)
        
        # زر التشغيل الرئيسي
        self.power_button = tk.Button(
            control_frame,
            text="🔌 Wake Up Teddy",
            font=('Comic Sans MS', 16, 'bold'),
            bg='#32CD32',
            fg='white',
            width=15,
            height=2,
            command=self.toggle_power,
            relief='raised',
            bd=3
        )
        self.power_button.pack(pady=5)
        
        # أزرار إضافية
        button_frame = tk.Frame(control_frame, bg='#8FBC8F')
        button_frame.pack(pady=10)
        
        self.connect_button = tk.Button(
            button_frame,
            text="🌐 Connect",
            font=('Arial', 12, 'bold'),
            bg='#4169E1',
            fg='white',
            width=12,
            command=self.test_connection,
            state='disabled'
        )
        self.connect_button.pack(side='left', padx=5)
        
        self.talk_button = tk.Button(
            button_frame,
            text="🎤 Talk to Teddy",
            font=('Arial', 12, 'bold'),
            bg='#FF6347',
            fg='white',
            width=12,
            command=self.start_conversation,
            state='disabled'
        )
        self.talk_button.pack(side='left', padx=5)
    
    def create_chat_area(self):
        """إنشاء منطقة المحادثة"""
        chat_frame = tk.Frame(self.root, bg='#F0F0F0', relief='sunken', bd=2)
        chat_frame.pack(pady=10, padx=20, fill='both', expand=False)
        
        chat_title = tk.Label(
            chat_frame,
            text="💬 Conversation with Teddy",
            font=('Arial', 14, 'bold'),
            bg='#F0F0F0'
        )
        chat_title.pack(pady=5)
        
        # منطقة النص
        self.chat_display = tk.Text(
            chat_frame,
            height=8,
            width=80,
            font=('Arial', 11),
            wrap='word',
            bg='white',
            fg='black',
            state='disabled'
        )
        
        # شريط التمرير
        scrollbar = tk.Scrollbar(chat_frame, orient='vertical', command=self.chat_display.yview)
        self.chat_display.configure(yscrollcommand=scrollbar.set)
        
        self.chat_display.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        scrollbar.pack(side='right', fill='y', pady=5)
        
        # إطار الإدخال
        input_frame = tk.Frame(self.root, bg='#2E8B57')
        input_frame.pack(pady=5, padx=20, fill='x')
        
        tk.Label(
            input_frame,
            text="Type your message:",
            font=('Arial', 12, 'bold'),
            bg='#2E8B57',
            fg='white'
        ).pack(anchor='w')
        
        # حقل الإدخال مع زر الإرسال
        entry_frame = tk.Frame(input_frame, bg='#2E8B57')
        entry_frame.pack(fill='x', pady=5)
        
        self.message_entry = tk.Entry(
            entry_frame,
            font=('Arial', 12),
            width=60
        )
        self.message_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        self.message_entry.bind('<Return>', self.send_message_enter)
        
        self.send_button = tk.Button(
            entry_frame,
            text="📤 Send",
            font=('Arial', 12, 'bold'),
            bg='#FF6347',
            fg='white',
            command=self.send_message,
            state='disabled'
        )
        self.send_button.pack(side='right')
    
    def start_animation_loop(self):
        """بدء حلقة الرسوم المتحركة"""
        self.animate_teddy()
    
    def animate_teddy(self):
        """رسوم متحركة للدبدوب"""
        if self.teddy_state == "listening":
            # وميض الأذنين
            current_time = time.time()
            if int(current_time * 2) % 2:  # وميض كل 0.5 ثانية
                self.teddy_canvas.itemconfig(self.ear1, fill='#FFD700')
                self.teddy_canvas.itemconfig(self.ear2, fill='#FFD700')
            else:
                self.teddy_canvas.itemconfig(self.ear1, fill='#CD853F')
                self.teddy_canvas.itemconfig(self.ear2, fill='#CD853F')
        
        # إعادة جدولة الرسوم المتحركة
        self.root.after(250, self.animate_teddy)
    
    def add_chat_message(self, sender: str, message: str, color: str = 'black'):
        """إضافة رسالة للمحادثة"""
        self.chat_display.config(state='normal')
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if sender == "Child":
            prefix = "👶 You"
            message_color = '#0066CC'
        else:
            prefix = "🧸 Teddy"
            message_color = '#CC6600'
        
        self.chat_display.insert(tk.END, f"[{timestamp}] {prefix}: ", 'sender')
        self.chat_display.insert(tk.END, f"{message}\n\n", 'message')
        
        # تنسيق النص
        self.chat_display.tag_config('sender', foreground=message_color, font=('Arial', 11, 'bold'))
        self.chat_display.tag_config('message', foreground='black', font=('Arial', 11))
        
        self.chat_display.config(state='disabled')
        self.chat_display.see(tk.END)
    
    def toggle_power(self):
        """تشغيل/إطفاء الدبدوب"""
        if not self.is_powered:
            self.power_on()
        else:
            self.power_off()
    
    def power_on(self):
        """تشغيل الدبدوب"""
        self.is_powered = True
        self.teddy_state = "listening"
        
        # تحديث الواجهة
        self.power_button.config(text="😴 Put Teddy to Sleep", bg='#DC143C')
        self.connect_button.config(state='normal')
        self.status_label.config(text="👀 Teddy is awake and ready!")
        
        # إعادة رسم الوجه
        self.draw_teddy_face()
        
        self.add_chat_message("System", "🔌 Teddy Bear is now awake!", 'green')
        self.add_chat_message("Teddy", "Hello! I'm awake now. Connect me to the cloud so we can talk!")
    
    def power_off(self):
        """إطفاء الدبدوب"""
        self.is_powered = False
        self.is_connected = False
        self.teddy_state = "sleeping"
        
        # تحديث الواجهة
        self.power_button.config(text="🔌 Wake Up Teddy", bg='#32CD32')
        self.connect_button.config(state='disabled')
        self.talk_button.config(state='disabled')
        self.send_button.config(state='disabled')
        self.status_label.config(text="😴 Teddy is sleeping...")
        
        # إعادة رسم الوجه
        self.draw_teddy_face()
        
        self.add_chat_message("System", "😴 Teddy Bear is now sleeping. Good night!", 'red')
    
    def test_connection(self):
        """اختبار الاتصال بالخادم"""
        self.status_label.config(text="🌐 Connecting to cloud...")
        self.teddy_state = "thinking"
        self.draw_teddy_face()
        
        # تشغيل الاختبار في thread منفصل
        thread = threading.Thread(target=self.run_connection_test, daemon=True)
        thread.start()
    
    def run_connection_test(self):
        """تشغيل اختبار الاتصال"""
        try:
            async def test():
                response = await self.client.get(f"{self.server_url}/esp32/connect")
                return response.status_code == 200, response.json() if response.status_code == 200 else None
            
            # تشغيل async في thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success, data = loop.run_until_complete(test())
            loop.close()
            
            # تحديث الواجهة في الـ main thread
            self.root.after(0, self.connection_result, success, data)
            
        except Exception as e:
            self.root.after(0, self.connection_result, False, str(e))
    
    def connection_result(self, success: bool, data: Any):
        """نتيجة اختبار الاتصال"""
        if success:
            self.is_connected = True
            self.teddy_state = "listening"
            self.status_label.config(text="✅ Connected to AI Cloud!")
            self.talk_button.config(state='normal')
            self.send_button.config(state='normal')
            
            self.add_chat_message("System", "✅ Successfully connected to AI cloud!", 'green')
            self.add_chat_message("Teddy", "Great! Now I can understand you and give smart responses. Try talking to me!")
        else:
            self.teddy_state = "listening"
            self.status_label.config(text="❌ Connection failed")
            
            self.add_chat_message("System", f"❌ Connection failed: {data}", 'red')
            self.add_chat_message("Teddy", "I can't connect to the cloud, but I can still chat with simple responses!")
        
        self.draw_teddy_face()
    
    def start_conversation(self):
        """بدء المحادثة"""
        self.add_chat_message("System", "🎤 You can now talk to Teddy! Type your message below.", 'blue')
        self.message_entry.focus()
    
    def send_message_enter(self, event):
        """إرسال الرسالة بضغط Enter"""
        self.send_message()
    
    def send_message(self):
        """إرسال رسالة للدبدوب"""
        message = self.message_entry.get().strip()
        if not message:
            return
        
        # مسح حقل الإدخال
        self.message_entry.delete(0, tk.END)
        
        # إضافة رسالة الطفل
        self.add_chat_message("Child", message)
        
        # تحديث حالة الدبدوب
        self.teddy_state = "thinking"
        self.status_label.config(text="🧠 Teddy is thinking...")
        self.draw_teddy_face()
        
        # إرسال للخادم في thread منفصل
        thread = threading.Thread(target=self.send_to_server, args=(message,), daemon=True)
        thread.start()
    
    def send_to_server(self, message: str):
        """إرسال الرسالة للخادم"""
        try:
            async def send():
                response = await self.client.post(
                    f"{self.server_url}/api/audio/upload",
                    params={
                        "device_id": self.device_id,
                        "text_message": message
                    }
                )
                return response.status_code == 200, response.json() if response.status_code == 200 else response.text
            
            # تشغيل async في thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success, data = loop.run_until_complete(send())
            loop.close()
            
            # تحديث الواجهة في الـ main thread
            self.root.after(0, self.server_response, success, data)
            
        except Exception as e:
            self.root.after(0, self.server_response, False, str(e))
    
    def server_response(self, success: bool, data: Any):
        """استجابة الخادم"""
        if success and isinstance(data, dict):
            ai_response = data.get('ai_response', {})
            ai_text = ai_response.get('text', 'Sorry, I could not understand.')
            
            # تحديث حالة الدبدوب للتحدث
            self.teddy_state = "speaking"
            self.status_label.config(text="🗣️ Teddy is speaking...")
            self.draw_teddy_face()
            
            # إضافة رد الدبدوب
            self.add_chat_message("Teddy", ai_text)
            
            # العودة للاستماع بعد 3 ثوانٍ
            self.root.after(3000, self.return_to_listening)
            
        else:
            self.teddy_state = "listening"
            self.status_label.config(text="❌ Error getting response")
            self.draw_teddy_face()
            
            self.add_chat_message("System", f"❌ Error: {data}", 'red')
            self.add_chat_message("Teddy", "Sorry, I had trouble understanding. Please try again!")
    
    def return_to_listening(self):
        """العودة لحالة الاستماع"""
        if self.is_powered:
            self.teddy_state = "listening"
            self.status_label.config(text="👂 Teddy is listening...")
            self.draw_teddy_face()
    
    async def cleanup(self):
        """تنظيف الموارد"""
        await self.client.aclose()
    
    def on_closing(self):
        """عند إغلاق النافذة"""
        asyncio.run(self.cleanup())
        self.root.destroy()
    
    def run(self):
        """تشغيل المحاكي"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # رسالة ترحيب
        self.add_chat_message("System", "🧸 Welcome to AI Teddy Bear Simulator!", 'purple')
        self.add_chat_message("System", "1. Click 'Wake Up Teddy' to start", 'gray')
        self.add_chat_message("System", "2. Click 'Connect' to connect to AI cloud", 'gray')
        self.add_chat_message("System", "3. Start chatting with your teddy!", 'gray')
        
        self.root.mainloop()


if __name__ == "__main__":
    print("🚀 Starting Professional Teddy Bear GUI Simulator...")
    
    try:
        # تحقق من وجود PIL
        from PIL import Image, ImageTk
    except ImportError:
        print("⚠️ PIL not found. Installing pillow...")
        import subprocess
        subprocess.check_call(["pip", "install", "pillow"])
        from PIL import Image, ImageTk
    
    simulator = TeddyBearGUISimulator()
    simulator.run() 