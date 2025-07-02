#!/usr/bin/env python3
"""
🧸 محاكي الدبدوب الذكي - نسخة احترافية
=====================================
محاكي ESP32 كامل مع واجهة تفاعلية احترافية
تجربة حقيقية كأنك اشتريت الدبدوب من المحل!
"""

import tkinter as tk
from tkinter import ttk, messagebox, font
import asyncio
import threading
import time
import uuid
import json
from datetime import datetime
from typing import Dict, Any
import httpx

# إعدادات الدبدوب
RENDER_URL = "https://ai-teddy-bear.onrender.com"
DEVICE_ID = f"TEDDY_{uuid.uuid4().hex[:8].upper()}"

class محاكي_الدبدوب_الذكي:
    """
    محاكي الدبدوب الذكي الاحترافي
    ============================
    يحاكي جميع وظائف ESP32 الحقيقية:
    - استشعار اللمس
    - التعرف على الصوت  
    - الاستجابة الذكية
    - LED متعدد الألوان
    - مكبر الصوت
    - البطارية
    - WiFi
    """
    
    def __init__(self):
        # معلومات الجهاز
        self.device_id = DEVICE_ID
        self.server_url = RENDER_URL
        self.client = httpx.AsyncClient(timeout=30.0)
        
        # حالة الدبدوب
        self.حالة_الطاقة = False  # مطفأ/مشغل
        self.حالة_الاتصال = False  # متصل/غير متصل
        self.حالة_الدبدوب = "نائم"  # نائم، يستمع، يفكر، يتحدث، سعيد، حزين
        self.مستوى_البطارية = 85
        self.قوة_WiFi = -45
        
        # مؤشرات الجهاز
        self.led_لون = "أحمر"
        self.صوت_مستوى = 70
        self.حساسية_اللمس = True
        self.وضع_الليل = False
        
        # إنشاء الواجهة
        self.انشاء_النافذة_الرئيسية()
        self.انشاء_واجهة_الدبدوب()
        self.انشاء_لوحة_التحكم()
        self.انشاء_منطقة_المحادثة()
        self.بدء_الرسوم_المتحركة()
        
        print(f"🧸 محاكي الدبدوب الذكي بدأ!")
        print(f"🆔 معرف الجهاز: {self.device_id}")

    def انشاء_النافذة_الرئيسية(self):
        """إنشاء النافذة الرئيسية للمحاكي"""
        self.root = tk.Tk()
        self.root.title("🧸 محاكي الدبدوب الذكي - ESP32 Professional")
        self.root.geometry("1000x800")
        self.root.configure(bg='#1e3a8a')
        self.root.resizable(True, True)
        
        # خط عربي
        try:
            self.خط_عربي = font.Font(family="Arial Unicode MS", size=12)
            self.خط_عنوان = font.Font(family="Arial Unicode MS", size=18, weight="bold")
        except:
            self.خط_عربي = font.Font(family="Arial", size=12)
            self.خط_عنوان = font.Font(family="Arial", size=18, weight="bold")
        
        # شريط العنوان
        عنوان_اطار = tk.Frame(self.root, bg='#1e40af', height=80)
        عنوان_اطار.pack(fill='x', pady=5)
        عنوان_اطار.pack_propagate(False)
        
        tk.Label(
            عنوان_اطار,
            text="🧸 دبدوبي الذكي - محاكي ESP32",
            font=self.خط_عنوان,
            fg='white',
            bg='#1e40af'
        ).pack(pady=20)

    def انشاء_واجهة_الدبدوب(self):
        """إنشاء واجهة الدبدوب التفاعلية"""
        # الإطار الرئيسي
        الإطار_الرئيسي = tk.Frame(self.root, bg='#e0f2fe')
        الإطار_الرئيسي.pack(fill='both', expand=True, padx=10, pady=5)
        
        # إطار الدبدوب
        إطار_الدبدوب = tk.Frame(الإطار_الرئيسي, bg='#81c784', relief='raised', bd=3)
        إطار_الدبدوب.pack(side='left', fill='both', expand=True, padx=5)
        
        # وجه الدبدوب
        self.canvas_الوجه = tk.Canvas(
            إطار_الدبدوب,
            width=400,
            height=400,
            bg='#d7ccc8',
            highlightthickness=0
        )
        self.canvas_الوجه.pack(pady=20)
        
        # رسم الوجه
        self.رسم_وجه_الدبدوب()
        
        # حالة الدبدوب
        self.تسمية_الحالة = tk.Label(
            إطار_الدبدوب,
            text="😴 الدبدوب نائم",
            font=self.خط_عنوان,
            bg='#81c784',
            fg='#2e7d32'
        )
        self.تسمية_الحالة.pack(pady=10)
        
        # معلومات الجهاز
        إطار_معلومات = tk.Frame(إطار_الدبدوب, bg='#81c784')
        إطار_معلومات.pack(pady=10)
        
        tk.Label(
            إطار_معلومات,
            text=f"🆔 معرف الجهاز: {self.device_id}",
            font=self.خط_عربي,
            bg='#81c784'
        ).pack()
        
        tk.Label(
            إطار_معلومات,
            text=f"🌐 الخادم: {self.server_url}",
            font=self.خط_عربي,
            bg='#81c784'
        ).pack()

    def رسم_وجه_الدبدوب(self):
        """رسم وجه الدبدوب حسب الحالة"""
        canvas = self.canvas_الوجه
        canvas.delete("all")
        
        # الرأس
        canvas.create_oval(50, 50, 350, 350, fill='#8d6e63', outline='#5d4037', width=3)
        
        # الأذنين مع LED
        لون_led = self.get_led_color()
        canvas.create_oval(80, 30, 140, 90, fill=لون_led, outline='#5d4037', width=2)
        canvas.create_oval(260, 30, 320, 90, fill=لون_led, outline='#5d4037', width=2)
        
        # العيون حسب الحالة
        if self.حالة_الدبدوب == "نائم":
            # عيون مغلقة
            canvas.create_arc(130, 150, 170, 180, start=0, extent=180, fill='black', width=3)
            canvas.create_arc(230, 150, 270, 180, start=0, extent=180, fill='black', width=3)
        elif self.حالة_الدبدوب == "يستمع":
            # عيون متنبهة
            canvas.create_oval(130, 150, 170, 190, fill='black')
            canvas.create_oval(230, 150, 270, 190, fill='black')
            canvas.create_oval(145, 160, 155, 170, fill='white')
            canvas.create_oval(245, 160, 255, 170, fill='white')
        elif self.حالة_الدبدوب == "يفكر":
            # عيون تنظر لأعلى
            canvas.create_oval(130, 140, 170, 180, fill='black')
            canvas.create_oval(230, 140, 270, 180, fill='black')
            canvas.create_oval(145, 145, 155, 155, fill='white')
            canvas.create_oval(245, 145, 255, 155, fill='white')
        elif self.حالة_الدبدوب == "يتحدث":
            # عيون سعيدة
            canvas.create_arc(130, 150, 170, 180, start=0, extent=180, fill='black', width=2)
            canvas.create_arc(230, 150, 270, 180, start=0, extent=180, fill='black', width=2)
        elif self.حالة_الدبدوب == "سعيد":
            # عيون مبتسمة
            canvas.create_arc(130, 150, 170, 180, start=0, extent=180, fill='black', width=2)
            canvas.create_arc(230, 150, 270, 180, start=0, extent=180, fill='black', width=2)
        
        # الأنف
        canvas.create_oval(190, 200, 210, 220, fill='black')
        
        # الفم حسب الحالة
        if self.حالة_الدبدوب == "نائم":
            canvas.create_arc(180, 240, 220, 270, start=0, extent=180, fill='black', width=2)
        elif self.حالة_الدبدوب == "يتحدث":
            canvas.create_oval(180, 240, 220, 280, fill='#c62828', outline='black', width=2)
        elif self.حالة_الدبدوب == "سعيد":
            canvas.create_arc(160, 230, 240, 290, start=0, extent=180, outline='black', width=4)
        else:
            canvas.create_arc(170, 235, 230, 280, start=0, extent=180, outline='black', width=3)
        
        # تأثيرات خاصة
        if self.حالة_الدبدوب == "يستمع":
            # موجات صوتية
            canvas.create_oval(70, 20, 150, 100, outline='yellow', width=3, dash=(5, 5))
            canvas.create_oval(250, 20, 330, 100, outline='yellow', width=3, dash=(5, 5))
        elif self.حالة_الدبدوب == "يفكر":
            # فقاعات تفكير
            canvas.create_oval(320, 80, 340, 100, outline='lightblue', width=2)
            canvas.create_oval(340, 60, 355, 75, outline='lightblue', width=2)
            canvas.create_oval(350, 45, 360, 55, outline='lightblue', width=2)

    def get_led_color(self):
        """الحصول على لون LED حسب الحالة"""
        if not self.حالة_الطاقة:
            return '#424242'  # رمادي (مطفأ)
        elif not self.حالة_الاتصال:
            return '#f44336'  # أحمر (غير متصل)
        elif self.حالة_الدبدوب == "يستمع":
            return '#2196f3'  # أزرق (يستمع)
        elif self.حالة_الدبدوب == "يفكر":
            return '#ff9800'  # برتقالي (يفكر)
        elif self.حالة_الدبدوب == "يتحدث":
            return '#9c27b0'  # بنفسجي (يتحدث)
        elif self.حالة_الدبدوب == "سعيد":
            return '#4caf50'  # أخضر (سعيد)
        else:
            return '#4caf50'  # أخضر افتراضي

    def انشاء_لوحة_التحكم(self):
        """إنشاء لوحة التحكم الجانبية"""
        لوحة_التحكم = tk.Frame(self.root, bg='#37474f', width=250)
        لوحة_التحكم.pack(side='right', fill='y', padx=5, pady=5)
        لوحة_التحكم.pack_propagate(False)
        
        # عنوان لوحة التحكم
        tk.Label(
            لوحة_التحكم,
            text="🎛️ لوحة التحكم",
            font=self.خط_عنوان,
            fg='white',
            bg='#37474f'
        ).pack(pady=20)
        
        # زر الطاقة
        self.زر_الطاقة = tk.Button(
            لوحة_التحكم,
            text="🔌 تشغيل الدبدوب",
            font=self.خط_عربي,
            bg='#4caf50',
            fg='white',
            width=20,
            height=2,
            command=self.تبديل_الطاقة
        )
        self.زر_الطاقة.pack(pady=10)
        
        # زر الاتصال
        self.زر_الاتصال = tk.Button(
            لوحة_التحكم,
            text="🌐 اتصال السحابة",
            font=self.خط_عربي,
            bg='#2196f3',
            fg='white',
            width=20,
            command=self.اختبار_الاتصال,
            state='disabled'
        )
        self.زر_الاتصال.pack(pady=5)
        
        # زر اللمس
        self.زر_اللمس = tk.Button(
            لوحة_التحكم,
            text="👆 لمس الدبدوب",
            font=self.خط_عربي,
            bg='#ff9800',
            fg='white',
            width=20,
            command=self.لمس_الدبدوب,
            state='disabled'
        )
        self.زر_اللمس.pack(pady=5)
        
        # مؤشرات الحالة
        إطار_المؤشرات = tk.Frame(لوحة_التحكم, bg='#37474f')
        إطار_المؤشرات.pack(pady=20, fill='x')
        
        tk.Label(
            إطار_المؤشرات,
            text="📊 مؤشرات الجهاز",
            font=self.خط_عربي,
            fg='white',
            bg='#37474f'
        ).pack()
        
        # مستوى البطارية
        self.تسمية_البطارية = tk.Label(
            إطار_المؤشرات,
            text=f"🔋 البطارية: {self.مستوى_البطارية}%",
            font=self.خط_عربي,
            fg='white',
            bg='#37474f'
        )
        self.تسمية_البطارية.pack(pady=2)
        
        # قوة WiFi
        self.تسمية_wifi = tk.Label(
            إطار_المؤشرات,
            text=f"📶 WiFi: {self.قوة_WiFi} dBm",
            font=self.خط_عربي,
            fg='white',
            bg='#37474f'
        )
        self.تسمية_wifi.pack(pady=2)
        
        # حالة LED
        self.تسمية_led = tk.Label(
            إطار_المؤشرات,
            text=f"💡 LED: {self.led_لون}",
            font=self.خط_عربي,
            fg='white',
            bg='#37474f'
        )
        self.تسمية_led.pack(pady=2)
        
        # إعدادات متقدمة
        إطار_الإعدادات = tk.Frame(لوحة_التحكم, bg='#37474f')
        إطار_الإعدادات.pack(pady=20, fill='x')
        
        tk.Label(
            إطار_الإعدادات,
            text="⚙️ الإعدادات",
            font=self.خط_عربي,
            fg='white',
            bg='#37474f'
        ).pack()
        
        # مستوى الصوت
        tk.Label(
            إطار_الإعدادات,
            text="🔊 مستوى الصوت",
            font=self.خط_عربي,
            fg='white',
            bg='#37474f'
        ).pack()
        
        self.مقياس_الصوت = tk.Scale(
            إطار_الإعدادات,
            from_=0,
            to=100,
            orient='horizontal',
            bg='#37474f',
            fg='white',
            highlightthickness=0
        )
        self.مقياس_الصوت.set(self.صوت_مستوى)
        self.مقياس_الصوت.pack(fill='x', padx=10)

    def انشاء_منطقة_المحادثة(self):
        """إنشاء منطقة المحادثة"""
        إطار_المحادثة = tk.Frame(self.root, bg='#f5f5f5')
        إطار_المحادثة.pack(side='bottom', fill='x', padx=10, pady=5)
        
        # عنوان المحادثة
        tk.Label(
            إطار_المحادثة,
            text="💬 محادثة مع الدبدوب",
            font=self.خط_عنوان,
            bg='#f5f5f5'
        ).pack(pady=5)
        
        # منطقة عرض المحادثة
        إطار_العرض = tk.Frame(إطار_المحادثة, bg='#f5f5f5')
        إطار_العرض.pack(fill='both', expand=True, pady=5)
        
        self.نص_المحادثة = tk.Text(
            إطار_العرض,
            height=8,
            width=80,
            font=self.خط_عربي,
            wrap='word',
            bg='white',
            state='disabled'
        )
        
        شريط_التمرير = tk.Scrollbar(إطار_العرض, orient='vertical', command=self.نص_المحادثة.yview)
        self.نص_المحادثة.configure(yscrollcommand=شريط_التمرير.set)
        
        self.نص_المحادثة.pack(side='left', fill='both', expand=True, padx=5)
        شريط_التمرير.pack(side='right', fill='y')
        
        # إطار الإدخال
        إطار_الإدخال = tk.Frame(إطار_المحادثة, bg='#f5f5f5')
        إطار_الإدخال.pack(fill='x', pady=5)
        
        tk.Label(
            إطار_الإدخال,
            text="✍️ اكتب رسالتك:",
            font=self.خط_عربي,
            bg='#f5f5f5'
        ).pack(anchor='w')
        
        إطار_الإرسال = tk.Frame(إطار_الإدخال, bg='#f5f5f5')
        إطار_الإرسال.pack(fill='x', pady=5)
        
        self.حقل_الرسالة = tk.Entry(
            إطار_الإرسال,
            font=self.خط_عربي,
            width=60
        )
        self.حقل_الرسالة.pack(side='left', fill='x', expand=True, padx=(0, 10))
        self.حقل_الرسالة.bind('<Return>', self.ارسال_رسالة_enter)
        
        self.زر_الإرسال = tk.Button(
            إطار_الإرسال,
            text="📤 إرسال",
            font=self.خط_عربي,
            bg='#4caf50',
            fg='white',
            command=self.ارسال_رسالة,
            state='disabled'
        )
        self.زر_الإرسال.pack(side='right')

    def بدء_الرسوم_المتحركة(self):
        """بدء حلقة الرسوم المتحركة"""
        self.تحديث_المؤشرات()
        self.تحريك_الدبدوب()

    def تحريك_الدبدوب(self):
        """تحريك الدبدوب حسب الحالة"""
        if self.حالة_الدبدوب == "يستمع" and self.حالة_الطاقة:
            # وميض الأذنين
            current_time = time.time()
            if int(current_time * 2) % 2:
                self.led_لون = "أصفر"
            else:
                self.led_لون = "أزرق"
            self.رسم_وجه_الدبدوب()
        
        # إعادة جدولة التحريك
        self.root.after(500, self.تحريك_الدبدوب)

    def تحديث_المؤشرات(self):
        """تحديث مؤشرات الحالة"""
        # تحديث البطارية (تقل ببطء)
        if self.حالة_الطاقة:
            self.مستوى_البطارية = max(0, self.مستوى_البطارية - 0.1)
        
        # تحديث التسميات
        self.تسمية_البطارية.config(text=f"🔋 البطارية: {int(self.مستوى_البطارية)}%")
        self.تسمية_wifi.config(text=f"📶 WiFi: {self.قوة_WiFi} dBm")
        self.تسمية_led.config(text=f"💡 LED: {self.led_لون}")
        
        # إعادة جدولة التحديث
        self.root.after(5000, self.تحديث_المؤشرات)

    def إضافة_رسالة_محادثة(self, المرسل: str, الرسالة: str, اللون: str = 'black'):
        """إضافة رسالة للمحادثة"""
        self.نص_المحادثة.config(state='normal')
        
        الوقت = datetime.now().strftime("%H:%M:%S")
        
        if المرسل == "طفل":
            البادئة = "👶 أنت"
            لون_المرسل = '#1976d2'
        elif المرسل == "دبدوب":
            البادئة = "🧸 الدبدوب"
            لون_المرسل = '#d32f2f'
        else:
            البادئة = "ℹ️ النظام"
            لون_المرسل = '#388e3c'
        
        self.نص_المحادثة.insert(tk.END, f"[{الوقت}] {البادئة}: ", 'sender')
        self.نص_المحادثة.insert(tk.END, f"{الرسالة}\n\n", 'message')
        
        # تنسيق النص
        self.نص_المحادثة.tag_config('sender', foreground=لون_المرسل, font=(self.خط_عربي['family'], self.خط_عربي['size'], 'bold'))
        self.نص_المحادثة.tag_config('message', foreground='black', font=self.خط_عربي)
        
        self.نص_المحادثة.config(state='disabled')
        self.نص_المحادثة.see(tk.END)

    def تبديل_الطاقة(self):
        """تشغيل/إطفاء الدبدوب"""
        if not self.حالة_الطاقة:
            self.تشغيل_الدبدوب()
        else:
            self.إطفاء_الدبدوب()

    def تشغيل_الدبدوب(self):
        """تشغيل الدبدوب"""
        self.حالة_الطاقة = True
        self.حالة_الدبدوب = "يستمع"
        
        # تحديث الواجهة
        self.زر_الطاقة.config(text="😴 إطفاء الدبدوب", bg='#f44336')
        self.زر_الاتصال.config(state='normal')
        self.زر_اللمس.config(state='normal')
        self.تسمية_الحالة.config(text="👀 الدبدوب مستيقظ ومستعد!", fg='#1976d2')
        
        self.رسم_وجه_الدبدوب()
        
        self.إضافة_رسالة_محادثة("النظام", "🔌 تم تشغيل الدبدوب بنجاح!")
        self.إضافة_رسالة_محادثة("دبدوب", "مرحباً! أنا مستيقظ الآن. اتصل بي بالسحابة لنتحدث!")

    def إطفاء_الدبدوب(self):
        """إطفاء الدبدوب"""
        self.حالة_الطاقة = False
        self.حالة_الاتصال = False
        self.حالة_الدبدوب = "نائم"
        
        # تحديث الواجهة
        self.زر_الطاقة.config(text="🔌 تشغيل الدبدوب", bg='#4caf50')
        self.زر_الاتصال.config(state='disabled')
        self.زر_اللمس.config(state='disabled')
        self.زر_الإرسال.config(state='disabled')
        self.تسمية_الحالة.config(text="😴 الدبدوب نائم", fg='#757575')
        
        self.رسم_وجه_الدبدوب()
        
        self.إضافة_رسالة_محادثة("النظام", "😴 تم إطفاء الدبدوب. تصبح على خير!")

    def اختبار_الاتصال(self):
        """اختبار الاتصال بالخادم"""
        self.تسمية_الحالة.config(text="🌐 جاري الاتصال بالسحابة...")
        self.حالة_الدبدوب = "يفكر"
        self.رسم_وجه_الدبدوب()
        
        thread = threading.Thread(target=self.تشغيل_اختبار_الاتصال, daemon=True)
        thread.start()

    def تشغيل_اختبار_الاتصال(self):
        """تشغيل اختبار الاتصال"""
        try:
            async def اختبار():
                response = await self.client.get(f"{self.server_url}/esp32/connect")
                return response.status_code == 200, response.json() if response.status_code == 200 else None
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            نجح, البيانات = loop.run_until_complete(اختبار())
            loop.close()
            
            self.root.after(0, self.نتيجة_الاتصال, نجح, البيانات)
            
        except Exception as e:
            self.root.after(0, self.نتيجة_الاتصال, False, str(e))

    def نتيجة_الاتصال(self, نجح: bool, البيانات: Any):
        """نتيجة اختبار الاتصال"""
        if نجح:
            self.حالة_الاتصال = True
            self.حالة_الدبدوب = "سعيد"
            self.تسمية_الحالة.config(text="✅ متصل بالذكاء الاصطناعي!", fg='#2e7d32')
            self.زر_الإرسال.config(state='normal')
            
            self.إضافة_رسالة_محادثة("النظام", "✅ تم الاتصال بالسحابة بنجاح!")
            self.إضافة_رسالة_محادثة("دبدوب", "رائع! الآن يمكنني أن أفهمك وأجيب بذكاء. جرب أن تكلمني!")
        else:
            self.حالة_الدبدوب = "يستمع"
            self.تسمية_الحالة.config(text="❌ فشل الاتصال", fg='#d32f2f')
            
            self.إضافة_رسالة_محادثة("النظام", f"❌ فشل الاتصال: {البيانات}")
            self.إضافة_رسالة_محادثة("دبدوب", "لا أستطيع الاتصال بالسحابة، لكن يمكنني محادثتك بردود بسيطة!")
        
        self.رسم_وجه_الدبدوب()

    def لمس_الدبدوب(self):
        """محاكاة لمس الدبدوب"""
        if not self.حالة_الطاقة:
            return
        
        self.حالة_الدبدوب = "سعيد"
        self.رسم_وجه_الدبدوب()
        
        ردود_اللمس = [
            "هههه! هذا يدغدغني! 😄",
            "أحب عندما تلمسني! 🥰",
            "مرحباً صديقي! 👋",
            "أنت لطيف جداً! 💕",
            "هل تريد أن نلعب؟ 🎮"
        ]
        
        import random
        رد = random.choice(ردود_اللمس)
        self.إضافة_رسالة_محادثة("دبدوب", رد)
        
        # العودة للحالة العادية بعد 3 ثوانٍ
        self.root.after(3000, self.العودة_للاستماع)

    def العودة_للاستماع(self):
        """العودة لحالة الاستماع"""
        if self.حالة_الطاقة:
            self.حالة_الدبدوب = "يستمع"
            self.تسمية_الحالة.config(text="👂 الدبدوب يستمع...")
            self.رسم_وجه_الدبدوب()

    def ارسال_رسالة_enter(self, event):
        """إرسال الرسالة بضغط Enter"""
        self.ارسال_رسالة()

    def ارسال_رسالة(self):
        """إرسال رسالة للدبدوب"""
        الرسالة = self.حقل_الرسالة.get().strip()
        if not الرسالة:
            return
        
        self.حقل_الرسالة.delete(0, tk.END)
        
        # إضافة رسالة الطفل
        self.إضافة_رسالة_محادثة("طفل", الرسالة)
        
        # تحديث حالة الدبدوب
        self.حالة_الدبدوب = "يفكر"
        self.تسمية_الحالة.config(text="🧠 الدبدوب يفكر...")
        self.رسم_وجه_الدبدوب()
        
        # إرسال للخادم
        thread = threading.Thread(target=self.ارسال_للخادم, args=(الرسالة,), daemon=True)
        thread.start()

    def ارسال_للخادم(self, الرسالة: str):
        """إرسال الرسالة للخادم"""
        try:
            async def ارسال():
                response = await self.client.post(
                    f"{self.server_url}/api/audio/upload",
                    params={
                        "device_id": self.device_id,
                        "text_message": الرسالة
                    }
                )
                return response.status_code == 200, response.json() if response.status_code == 200 else response.text
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            نجح, البيانات = loop.run_until_complete(ارسال())
            loop.close()
            
            self.root.after(0, self.استجابة_الخادم, نجح, البيانات)
            
        except Exception as e:
            self.root.after(0, self.استجابة_الخادم, False, str(e))

    def استجابة_الخادم(self, نجح: bool, البيانات: Any):
        """استجابة الخادم"""
        if نجح and isinstance(البيانات, dict):
            استجابة_الذكاء = البيانات.get('ai_response', {})
            نص_الذكاء = استجابة_الذكاء.get('text', 'آسف، لم أستطع فهمك.')
            
            # تحديث حالة الدبدوب للتحدث
            self.حالة_الدبدوب = "يتحدث"
            self.تسمية_الحالة.config(text="🗣️ الدبدوب يتحدث...")
            self.رسم_وجه_الدبدوب()
            
            # إضافة رد الدبدوب
            self.إضافة_رسالة_محادثة("دبدوب", نص_الذكاء)
            
            # العودة للاستماع بعد 3 ثوانٍ
            self.root.after(3000, self.العودة_للاستماع)
            
        else:
            self.حالة_الدبدوب = "يستمع"
            self.تسمية_الحالة.config(text="❌ خطأ في الاستجابة")
            self.رسم_وجه_الدبدوب()
            
            self.إضافة_رسالة_محادثة("النظام", f"❌ خطأ: {البيانات}")
            self.إضافة_رسالة_محادثة("دبدوب", "آسف، واجهت مشكلة في فهمك. حاول مرة أخرى!")

    async def تنظيف_الموارد(self):
        """تنظيف الموارد"""
        await self.client.aclose()

    def عند_الإغلاق(self):
        """عند إغلاق النافذة"""
        asyncio.run(self.تنظيف_الموارد())
        self.root.destroy()

    def تشغيل(self):
        """تشغيل المحاكي"""
        self.root.protocol("WM_DELETE_WINDOW", self.عند_الإغلاق)
        
        # رسائل الترحيب
        self.إضافة_رسالة_محادثة("النظام", "🧸 أهلاً بك في محاكي الدبدوب الذكي!")
        self.إضافة_رسالة_محادثة("النظام", "1. اضغط 'تشغيل الدبدوب' للبدء")
        self.إضافة_رسالة_محادثة("النظام", "2. اضغط 'اتصال السحابة' للاتصال بالذكاء الاصطناعي")
        self.إضافة_رسالة_محادثة("النظام", "3. ابدأ المحادثة مع دبدوبك!")
        
        self.root.mainloop()


if __name__ == "__main__":
    print("🚀 بدء تشغيل محاكي الدبدوب الذكي الاحترافي...")
    
    # تحقق من المكتبات المطلوبة
    try:
        import httpx
    except ImportError:
        print("⚠️ تثبيت httpx...")
        import subprocess
        subprocess.check_call(["pip", "install", "httpx"])
        import httpx
    
    محاكي = محاكي_الدبدوب_الذكي()
    محاكي.تشغيل() 