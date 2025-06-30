#!/usr/bin/env python3
"""
📱 Parent Mobile App Simulator - Complete Control Dashboard
محاكي تطبيق الهاتف المحمول للتحكم الأبوي
"""
import structlog
logger = structlog.get_logger(__name__)


import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import threading
import time
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

SERVER_URL = "http://127.0.0.1:8000"

class ParentMobileAppSimulator:
    """محاكي تطبيق الهاتف المحمول للوالدين"""
    
    def __init__(self):
        self.session_token = None
        self.family_id = None
        self.children_list = []
        self.selected_child = None
        self.notifications = []
        
        self.create_modern_gui()
        self.setup_notifications()
        
    def create_modern_gui(self):
        """إنشاء واجهة حديثة للتطبيق"""
        self.root = tk.Tk()
        self.root.title("📱 AI Teddy Bear - Parent Control App")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f8f9fa')
        
        # Modern Style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Header
        self.create_header()
        
        # Main Content with Tabs
        self.create_main_tabs()
        
        # Status Bar
        self.create_status_bar()
        
        self.log("📱 Parent Mobile App Simulator Ready")
        
    def create_header(self):
        """إنشاء الهيدر"""
        header = tk.Frame(self.root, bg='#007acc', height=80)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        # Logo and Title
        title_frame = tk.Frame(header, bg='#007acc')
        title_frame.pack(side="left", fill="y", padx=20)
        
        tk.Label(
            title_frame,
            text="🧸 AI Teddy Bear",
            font=('Arial', 20, 'bold'),
            fg='white',
            bg='#007acc'
        ).pack(anchor="w", pady=10)
        
        tk.Label(
            title_frame,
            text="Parent Control Dashboard",
            font=('Arial', 12),
            fg='#cce7ff',
            bg='#007acc'
        ).pack(anchor="w")
        
        # User Info
        user_frame = tk.Frame(header, bg='#007acc')
        user_frame.pack(side="right", fill="y", padx=20)
        
        self.user_label = tk.Label(
            user_frame,
            text="👤 Parent Dashboard",
            font=('Arial', 12),
            fg='white',
            bg='#007acc'
        )
        self.user_label.pack(pady=10)
        
        # Notifications Button
        self.notif_button = tk.Button(
            user_frame,
            text="🔔 0",
            font=('Arial', 10),
            bg='#ff6b6b',
            fg='white',
            relief='flat',
            command=self.show_notifications
        )
        self.notif_button.pack(pady=5)
        
    def create_main_tabs(self):
        """إنشاء التبويبات الرئيسية"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Dashboard Tab
        self.create_dashboard_tab()
        
        # Children Management Tab
        self.create_children_tab()
        
        # Device Control Tab
        self.create_device_control_tab()
        
        # Analytics & Reports Tab
        self.create_analytics_tab()
        
        # Settings Tab
        self.create_settings_tab()
        
    def create_dashboard_tab(self):
        """تبويب لوحة التحكم الرئيسية"""
        dashboard_frame = tk.Frame(self.notebook, bg='#f8f9fa')
        self.notebook.add(dashboard_frame, text="🏠 Dashboard")
        
        # Quick Stats
        stats_frame = tk.LabelFrame(dashboard_frame, text="📊 Quick Overview", font=('Arial', 12, 'bold'))
        stats_frame.pack(fill="x", padx=10, pady=10)
        
        stats_grid = tk.Frame(stats_frame)
        stats_grid.pack(pady=10)
        
        # Stat Cards
        self.create_stat_card(stats_grid, "👶 Active Children", "2", "#4caf50", 0, 0)
        self.create_stat_card(stats_grid, "💬 Today's Conversations", "15", "#2196f3", 0, 1)
        self.create_stat_card(stats_grid, "⏱️ Screen Time Today", "2h 30m", "#ff9800", 0, 2)
        self.create_stat_card(stats_grid, "😊 Mood Score", "8.5/10", "#9c27b0", 0, 3)
        
        # Recent Activity
        activity_frame = tk.LabelFrame(dashboard_frame, text="📋 Recent Activity", font=('Arial', 12, 'bold'))
        activity_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.activity_text = tk.Text(activity_frame, height=10, font=('Arial', 10))
        activity_scroll = tk.Scrollbar(activity_frame, orient="vertical", command=self.activity_text.yview)
        self.activity_text.configure(yscrollcommand=activity_scroll.set)
        self.activity_text.pack(side="left", fill="both", expand=True)
        activity_scroll.pack(side="right", fill="y")
        
        # Load sample activity
        self.load_sample_activity()
        
    def create_stat_card(self, parent, title, value, color, row, col):
        """إنشاء بطاقة إحصائية"""
        card = tk.Frame(parent, bg=color, relief='raised', bd=2)
        card.grid(row=row, column=col, padx=10, pady=10, ipadx=20, ipady=10)
        
        tk.Label(card, text=title, font=('Arial', 10), fg='white', bg=color).pack()
        tk.Label(card, text=value, font=('Arial', 16, 'bold'), fg='white', bg=color).pack()
        
    def create_children_tab(self):
        """تبويب إدارة الأطفال"""
        children_frame = tk.Frame(self.notebook, bg='#f8f9fa')
        self.notebook.add(children_frame, text="👶 Children")
        
        # Children List
        list_frame = tk.LabelFrame(children_frame, text="👨‍👩‍👧‍👦 Family Members", font=('Arial', 12, 'bold'))
        list_frame.pack(fill="x", padx=10, pady=10)
        
        # Add Child Button
        add_child_frame = tk.Frame(list_frame)
        add_child_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Button(
            add_child_frame,
            text="➕ Add New Child",
            font=('Arial', 12, 'bold'),
            bg='#4caf50',
            fg='white',
            command=self.add_child_dialog
        ).pack(side="left")
        
        # Children Listbox
        self.children_listbox = tk.Listbox(list_frame, height=5, font=('Arial', 11))
        self.children_listbox.pack(fill="x", padx=10, pady=10)
        self.children_listbox.bind('<<ListboxSelect>>', self.on_child_select)
        
        # Child Details
        details_frame = tk.LabelFrame(children_frame, text="👶 Child Details", font=('Arial', 12, 'bold'))
        details_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.child_details_text = tk.Text(details_frame, height=15, font=('Arial', 10))
        details_scroll = tk.Scrollbar(details_frame, orient="vertical", command=self.child_details_text.yview)
        self.child_details_text.configure(yscrollcommand=details_scroll.set)
        self.child_details_text.pack(side="left", fill="both", expand=True)
        details_scroll.pack(side="right", fill="y")
        
        # Load sample children
        self.load_sample_children()
        
    def create_device_control_tab(self):
        """تبويب التحكم بالأجهزة"""
        device_frame = tk.Frame(self.notebook, bg='#f8f9fa')
        self.notebook.add(device_frame, text="🧸 Device Control")
        
        # Device Selection
        selection_frame = tk.LabelFrame(device_frame, text="📱 Select Device", font=('Arial', 12, 'bold'))
        selection_frame.pack(fill="x", padx=10, pady=10)
        
        self.device_var = tk.StringVar()
        device_combo = ttk.Combobox(selection_frame, textvariable=self.device_var, width=40)
        device_combo['values'] = ('ESP32_ABC12345 - Sara\'s Teddy', 'ESP32_DEF67890 - Ahmed\'s Teddy')
        device_combo.set('ESP32_ABC12345 - Sara\'s Teddy')
        device_combo.pack(padx=10, pady=10)
        
        # Volume Control
        volume_frame = tk.LabelFrame(device_frame, text="🔊 Volume Control", font=('Arial', 12, 'bold'))
        volume_frame.pack(fill="x", padx=10, pady=10)
        
        volume_control_frame = tk.Frame(volume_frame)
        volume_control_frame.pack(pady=10)
        
        tk.Label(volume_control_frame, text="🔉", font=('Arial', 14)).pack(side="left", padx=5)
        
        self.volume_scale = tk.Scale(
            volume_control_frame,
            from_=0, to=100,
            orient="horizontal",
            length=300,
            command=self.volume_changed
        )
        self.volume_scale.set(50)
        self.volume_scale.pack(side="left", padx=10)
        
        tk.Label(volume_control_frame, text="🔊", font=('Arial', 14)).pack(side="left", padx=5)
        
        self.volume_label = tk.Label(volume_frame, text="Volume: 50%", font=('Arial', 12))
        self.volume_label.pack(pady=5)
        
        # Quick Actions
        actions_frame = tk.LabelFrame(device_frame, text="⚡ Quick Actions", font=('Arial', 12, 'bold'))
        actions_frame.pack(fill="x", padx=10, pady=10)
        
        actions_grid = tk.Frame(actions_frame)
        actions_grid.pack(pady=10)
        
        # Action buttons
        actions = [
            ("🔴 Emergency Stop", self.emergency_stop, "#e74c3c"),
            ("😴 Sleep Mode", self.sleep_mode, "#95a5a6"),
            ("🎵 Play Lullaby", self.play_lullaby, "#9b59b6"),
            ("📞 Call Child", self.call_child, "#3498db"),
            ("🔄 Restart Device", self.restart_device, "#f39c12"),
            ("⚙️ Update Firmware", self.update_firmware, "#2ecc71")
        ]
        
        for i, (text, command, color) in enumerate(actions):
            btn = tk.Button(
                actions_grid,
                text=text,
                command=command,
                bg=color,
                fg='white',
                width=15,
                font=('Arial', 10)
            )
            btn.grid(row=i//3, column=i%3, padx=5, pady=5)
        
        # WiFi Configuration
        wifi_frame = tk.LabelFrame(device_frame, text="📶 WiFi Configuration", font=('Arial', 12, 'bold'))
        wifi_frame.pack(fill="x", padx=10, pady=10)
        
        wifi_grid = tk.Frame(wifi_frame)
        wifi_grid.pack(pady=10)
        
        tk.Label(wifi_grid, text="SSID:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.ssid_entry = tk.Entry(wifi_grid, width=25)
        self.ssid_entry.insert(0, "HomeWiFi_2.4G")
        self.ssid_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(wifi_grid, text="Password:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.password_entry = tk.Entry(wifi_grid, show="*", width=25)
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Button(wifi_grid, text="📶 Update WiFi", command=self.update_wifi, bg="#2980b9", fg="white").grid(row=2, column=0, columnspan=2, pady=10)
        
    def create_analytics_tab(self):
        """تبويب التحليلات والتقارير"""
        analytics_frame = tk.Frame(self.notebook, bg='#f8f9fa')
        self.notebook.add(analytics_frame, text="📊 Analytics")
        
        # Time Range Selection
        range_frame = tk.LabelFrame(analytics_frame, text="📅 Time Range", font=('Arial', 12, 'bold'))
        range_frame.pack(fill="x", padx=10, pady=10)
        
        range_buttons = tk.Frame(range_frame)
        range_buttons.pack(pady=10)
        
        for text, days in [("Today", 1), ("Week", 7), ("Month", 30), ("3 Months", 90)]:
            tk.Button(
                range_buttons,
                text=text,
                command=lambda d=days: self.load_analytics(d),
                bg="#3498db",
                fg="white",
                width=10
            ).pack(side="left", padx=5)
        
        # Charts Frame
        charts_frame = tk.Frame(analytics_frame, bg='#f8f9fa')
        charts_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create sample charts
        self.create_sample_charts(charts_frame)
        
        # Detailed Reports
        reports_frame = tk.LabelFrame(analytics_frame, text="📋 Detailed Reports", font=('Arial', 12, 'bold'))
        reports_frame.pack(fill="x", padx=10, pady=10)
        
        reports_buttons = tk.Frame(reports_frame)
        reports_buttons.pack(pady=10)
        
        report_types = [
            ("📈 Usage Report", self.usage_report),
            ("😊 Emotional Report", self.emotional_report),
            ("🎓 Learning Progress", self.learning_report),
            ("👨‍👩‍👧‍👦 Family Insights", self.family_report)
        ]
        
        for text, command in report_types:
            tk.Button(
                reports_buttons,
                text=text,
                command=command,
                bg="#9b59b6",
                fg="white",
                width=15
            ).pack(side="left", padx=5)
        
    def create_settings_tab(self):
        """تبويب الإعدادات"""
        settings_frame = tk.Frame(self.notebook, bg='#f8f9fa')
        self.notebook.add(settings_frame, text="⚙️ Settings")
        
        # Account Settings
        account_frame = tk.LabelFrame(settings_frame, text="👤 Account Settings", font=('Arial', 12, 'bold'))
        account_frame.pack(fill="x", padx=10, pady=10)
        
        account_grid = tk.Frame(account_frame)
        account_grid.pack(pady=10)
        
        tk.Label(account_grid, text="Parent Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        parent_name = tk.Entry(account_grid, width=25)
        parent_name.insert(0, "والد محمد")
        parent_name.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(account_grid, text="Email:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        email_entry = tk.Entry(account_grid, width=25)
        email_entry.insert(0, "parent@example.com")
        email_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Notification Settings
        notif_frame = tk.LabelFrame(settings_frame, text="🔔 Notification Settings", font=('Arial', 12, 'bold'))
        notif_frame.pack(fill="x", padx=10, pady=10)
        
        notif_options = tk.Frame(notif_frame)
        notif_options.pack(pady=10)
        
        self.emotional_alerts = tk.BooleanVar(value=True)
        self.usage_alerts = tk.BooleanVar(value=True)
        self.learning_alerts = tk.BooleanVar(value=False)
        self.bedtime_alerts = tk.BooleanVar(value=True)
        
        tk.Checkbutton(notif_options, text="😟 Emotional Concerns", variable=self.emotional_alerts).pack(anchor="w")
        tk.Checkbutton(notif_options, text="⏰ Usage Time Limits", variable=self.usage_alerts).pack(anchor="w")
        tk.Checkbutton(notif_options, text="🎓 Learning Milestones", variable=self.learning_alerts).pack(anchor="w")
        tk.Checkbutton(notif_options, text="😴 Bedtime Reminders", variable=self.bedtime_alerts).pack(anchor="w")
        
        # Screen Time Settings
        screentime_frame = tk.LabelFrame(settings_frame, text="⏰ Screen Time Limits", font=('Arial', 12, 'bold'))
        screentime_frame.pack(fill="x", padx=10, pady=10)
        
        screentime_grid = tk.Frame(screentime_frame)
        screentime_grid.pack(pady=10)
        
        tk.Label(screentime_grid, text="Daily Limit (minutes):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        daily_limit = tk.Spinbox(screentime_grid, from_=30, to=300, width=10, value=120)
        daily_limit.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(screentime_grid, text="Bedtime:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        bedtime_entry = tk.Entry(screentime_grid, width=10)
        bedtime_entry.insert(0, "20:00")
        bedtime_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Save Button
        tk.Button(
            settings_frame,
            text="💾 Save All Settings",
            command=self.save_settings,
            bg="#27ae60",
            fg="white",
            font=('Arial', 12, 'bold'),
            width=20
        ).pack(pady=20)
        
    def create_status_bar(self):
        """إنشاء شريط الحالة"""
        self.status_bar = tk.Frame(self.root, bg='#34495e', height=30)
        self.status_bar.pack(fill="x", side="bottom")
        self.status_bar.pack_propagate(False)
        
        self.status_label = tk.Label(
            self.status_bar,
            text="📱 Ready - Connected to AI Teddy Bear System",
            font=('Arial', 10),
            fg='white',
            bg='#34495e'
        )
        self.status_label.pack(side="left", padx=10, pady=5)
        
        # Connection Status
        self.connection_label = tk.Label(
            self.status_bar,
            text="🟢 Online",
            font=('Arial', 10),
            fg='#2ecc71',
            bg='#34495e'
        )
        self.connection_label.pack(side="right", padx=10, pady=5)
        
    def setup_notifications(self):
        """تهيئة نظام الإشعارات"""
        # Sample notifications
        sample_notifications = [
            {"time": "10:30", "type": "emotional", "message": "Sara seems happy after her math game! 😊"},
            {"time": "14:15", "type": "usage", "message": "Ahmed has 30 minutes left today"},
            {"time": "16:45", "type": "learning", "message": "New milestone: Sara learned 5 new Arabic words!"},
            {"time": "19:00", "type": "bedtime", "message": "Bedtime approaching in 1 hour"}
        ]
        
        self.notifications = sample_notifications
        self.update_notification_badge()
        
    def update_notification_badge(self):
        """تحديث شارة الإشعارات"""
        count = len(self.notifications)
        self.notif_button.config(text=f"🔔 {count}")
        
    def log(self, message):
        """إضافة رسالة للسجل"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        print(log_entry.strip())
        
    # ======================== EVENT HANDLERS ========================
    
    def volume_changed(self, value):
        """تغيير مستوى الصوت"""
        volume = int(float(value))
        self.volume_label.config(text=f"Volume: {volume}%")
        self.send_volume_to_device(volume)
        
    def send_volume_to_device(self, volume):
        """إرسال مستوى الصوت للجهاز"""
        device_id = self.device_var.get().split()[0]
        try:
            response = requests.post(f"{SERVER_URL}/esp32/volume", json={
                "device_id": device_id,
                "volume": volume
            }, timeout=2)
            if response.status_code == 200:
                self.status_label.config(text=f"✅ Volume updated to {volume}%")
        except Exception as e:
    logger.error(f"Error in operation: {e}", exc_info=True)Exception as e:
    logger.error(f"Error in operation: {e}", exc_info=True)            self.status_label.config(text="❌ Failed to update volume")
            
    def emergency_stop(self):
        """إيقاف الطوارئ"""
        result = messagebox.askyesno("Emergency Stop", "Are you sure you want to emergency stop the teddy bear?")
        if result:
            self.status_label.config(text="🛑 Emergency stop sent to device")
            self.log("🛑 Emergency stop activated")
            
    def sleep_mode(self):
        """وضع السكون"""
        self.status_label.config(text="😴 Sleep mode activated")
        self.log("😴 Device set to sleep mode")
        
    def play_lullaby(self):
        """تشغيل تهويدة"""
        self.status_label.config(text="🎵 Playing lullaby...")
        self.log("🎵 Lullaby sent to device")
        
    def call_child(self):
        """استدعاء الطفل"""
        self.status_label.config(text="📞 Calling child...")
        self.log("📞 Call sent to device")
        
    def restart_device(self):
        """إعادة تشغيل الجهاز"""
        result = messagebox.askyesno("Restart Device", "Are you sure you want to restart the device?")
        if result:
            self.status_label.config(text="🔄 Restarting device...")
            self.log("🔄 Device restart initiated")
            
    def update_firmware(self):
        """تحديث البرمجيات"""
        result = messagebox.askyesno("Firmware Update", "Check for firmware updates?")
        if result:
            self.status_label.config(text="⚙️ Checking for updates...")
            self.log("⚙️ Firmware update check started")
            
    def update_wifi(self):
        """تحديث إعدادات WiFi"""
        ssid = self.ssid_entry.get()
        password = self.password_entry.get()
        
        if ssid and password:
            self.status_label.config(text=f"📶 Updating WiFi to {ssid}...")
            self.log(f"📶 WiFi updated: {ssid}")
        else:
            messagebox.showwarning("Warning", "Please enter both SSID and password")
            
    def on_child_select(self, event):
        """عند اختيار طفل"""
        selection = self.children_listbox.curselection()
        if selection:
            child_name = self.children_listbox.get(selection[0])
            self.load_child_details(child_name)
            
    def load_child_details(self, child_name):
        """تحميل تفاصيل الطفل"""
        # Sample child details
        details = f"""
👶 Child Profile: {child_name}

📊 Today's Activity:
• Conversations: 8
• Games played: 3
• Stories heard: 2
• Learning time: 45 minutes

😊 Emotional Status:
• Overall mood: Happy 😊
• Energy level: High
• Last interaction: 15 minutes ago

🎯 Learning Progress:
• Arabic letters: 18/28 ✅
• Numbers: 1-20 ✅
• Colors: 8/12 ✅
• Animals: 15/20 ✅

⚠️ Recent Concerns:
• None detected

🏆 Achievements:
• Completed first math puzzle!
• Learned 3 new words today
• Showed empathy in story response

📈 Weekly Trends:
• Usage time: Stable
• Mood: Improving
• Learning engagement: High
"""
        
        self.child_details_text.delete(1.0, "end")
        self.child_details_text.insert(1.0, details)
        
    def load_sample_children(self):
        """تحميل عينة من الأطفال"""
        children = ["👧 Sara (7 years)", "👦 Ahmed (5 years)", "👶 Layla (3 years)"]
        for child in children:
            self.children_listbox.insert("end", child)
            
    def load_sample_activity(self):
        """تحميل نشاط عينة"""
        activities = [
            "[09:15] 👧 Sara started morning conversation",
            "[09:18] 🎮 Played counting game - scored 8/10",
            "[09:25] 😊 Detected happy mood",
            "[10:30] 📚 Listened to 'The Brave Little Mouse' story",
            "[10:45] 🎯 Chose brave option in story - positive behavior",
            "[11:00] 👦 Ahmed joined conversation",
            "[11:05] 🎵 Sang Arabic alphabet song together",
            "[11:20] 🧠 Completed color matching game",
            "[14:15] ⚠️ Ahmed seems tired - recommended break",
            "[15:30] 👧 Sara asked about her grandmother",
            "[15:35] 💝 Sweet conversation about family love",
            "[16:45] 🎓 Learning milestone: New vocabulary words",
            "[17:00] 🎮 Family game session with both children",
            "[18:30] 😴 Bedtime story preparation"
        ]
        
        for activity in activities:
            self.activity_text.insert("end", activity + "\n")
            
    def create_sample_charts(self, parent):
        """إنشاء مخططات عينة"""
        # Daily Usage Chart
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(10, 6))
        
        # Usage time
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        usage = [45, 60, 30, 75, 90, 120, 80]
        ax1.bar(days, usage, color='#3498db')
        ax1.set_title('Daily Usage (minutes)')
        ax1.set_ylim(0, 150)
        
        # Mood trends
        mood_scores = [7.5, 8.2, 6.8, 8.5, 9.1, 8.8, 8.0]
        ax2.plot(days, mood_scores, marker='o', color='#e74c3c', linewidth=2)
        ax2.set_title('Mood Trends (1-10)')
        ax2.set_ylim(0, 10)
        
        # Learning progress
        subjects = ['Arabic', 'Math', 'Colors', 'Animals', 'Songs']
        progress = [85, 70, 95, 80, 90]
        ax3.pie(progress, labels=subjects, autopct='%1.1f%%', startangle=90)
        ax3.set_title('Learning Progress (%)')
        
        # Activity distribution
        activities = ['Games', 'Stories', 'Songs', 'Learning', 'Chat']
        time_spent = [25, 30, 15, 20, 10]
        ax4.bar(activities, time_spent, color=['#f39c12', '#9b59b6', '#1abc9c', '#2ecc71', '#34495e'])
        ax4.set_title('Activity Distribution (%)')
        
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
    # ======================== DIALOG FUNCTIONS ========================
    
    def add_child_dialog(self):
        """حوار إضافة طفل جديد"""
        dialog = tk.Toplevel(self.root)
        dialog.title("👶 Add New Child")
        dialog.geometry("400x300")
        dialog.configure(bg='#f8f9fa')
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="👶 Add New Child", font=('Arial', 16, 'bold'), bg='#f8f9fa').pack(pady=20)
        
        # Form
        form_frame = tk.Frame(dialog, bg='#f8f9fa')
        form_frame.pack(pady=20)
        
        tk.Label(form_frame, text="Name:", bg='#f8f9fa').grid(row=0, column=0, sticky="w", padx=5, pady=5)
        name_entry = tk.Entry(form_frame, width=25)
        name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(form_frame, text="Age:", bg='#f8f9fa').grid(row=1, column=0, sticky="w", padx=5, pady=5)
        age_entry = tk.Spinbox(form_frame, from_=2, to=12, width=23)
        age_entry.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(form_frame, text="Gender:", bg='#f8f9fa').grid(row=2, column=0, sticky="w", padx=5, pady=5)
        gender_var = tk.StringVar()
        gender_combo = ttk.Combobox(form_frame, textvariable=gender_var, width=22)
        gender_combo['values'] = ('Boy', 'Girl')
        gender_combo.grid(row=2, column=1, padx=5, pady=5)
        
        # Buttons
        button_frame = tk.Frame(dialog, bg='#f8f9fa')
        button_frame.pack(pady=20)
        
        def save_child():
            name = name_entry.get().strip()
            age = age_entry.get()
            gender = gender_var.get()
            
            if name and age and gender:
                icon = "👧" if gender == "Girl" else "👦"
                child_entry = f"{icon} {name} ({age} years)"
                self.children_listbox.insert("end", child_entry)
                self.log(f"✅ Added new child: {name}")
                dialog.destroy()
            else:
                messagebox.showwarning("Warning", "Please fill all fields")
        
        tk.Button(button_frame, text="💾 Save", command=save_child, bg="#27ae60", fg="white", width=10).pack(side="left", padx=5)
        tk.Button(button_frame, text="❌ Cancel", command=dialog.destroy, bg="#e74c3c", fg="white", width=10).pack(side="left", padx=5)
        
    def show_notifications(self):
        """عرض الإشعارات"""
        dialog = tk.Toplevel(self.root)
        dialog.title("🔔 Notifications")
        dialog.geometry("500x400")
        dialog.configure(bg='#f8f9fa')
        
        tk.Label(dialog, text="🔔 Notifications", font=('Arial', 16, 'bold'), bg='#f8f9fa').pack(pady=20)
        
        # Notifications list
        notif_frame = tk.Frame(dialog, bg='#f8f9fa')
        notif_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        notif_text = tk.Text(notif_frame, height=15, font=('Arial', 11))
        notif_scroll = tk.Scrollbar(notif_frame, orient="vertical", command=notif_text.yview)
        notif_text.configure(yscrollcommand=notif_scroll.set)
        notif_text.pack(side="left", fill="both", expand=True)
        notif_scroll.pack(side="right", fill="y")
        
        for notif in self.notifications:
            notif_text.insert("end", f"[{notif['time']}] {notif['message']}\n\n")
            
        # Clear button
        tk.Button(dialog, text="🗑️ Clear All", command=lambda: self.clear_notifications(dialog), bg="#e74c3c", fg="white").pack(pady=10)
        
    def clear_notifications(self, dialog):
        """مسح الإشعارات"""
        self.notifications = []
        self.update_notification_badge()
        dialog.destroy()
        
    # ======================== REPORT FUNCTIONS ========================
    
    def load_analytics(self, days):
        """تحميل التحليلات"""
        self.status_label.config(text=f"📊 Loading {days} days analytics...")
        self.log(f"📊 Analytics loaded for {days} days")
        
    def usage_report(self):
        """تقرير الاستخدام"""
        self.log("📈 Usage report generated")
        
    def emotional_report(self):
        """تقرير المشاعر"""
        self.log("😊 Emotional report generated")
        
    def learning_report(self):
        """تقرير التعلم"""
        self.log("🎓 Learning progress report generated")
        
    def family_report(self):
        """تقرير العائلة"""
        self.log("👨‍👩‍👧‍👦 Family insights report generated")
        
    def save_settings(self):
        """حفظ الإعدادات"""
        self.status_label.config(text="💾 Settings saved successfully")
        self.log("💾 All settings saved")
        messagebox.showinfo("Success", "Settings saved successfully!")
        
    def run(self):
        """تشغيل التطبيق"""
        try:
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.root.mainloop()
        except Exception as e:
    logger.error(f"Error: {e}")"\n👋 Parent App shutting down...")
        
    def on_closing(self):
        """عند إغلاق التطبيق"""
        self.root.destroy()

if __name__ == "__main__":
    print("📱 Starting Parent Mobile App Simulator...")
    print("=" * 60)
    print("🎯 Complete Parent Control Dashboard")
    print("👨‍👩‍👧‍👦 Family Management System")
    print("📊 Real-time Analytics & Reports")
    print("🔔 Smart Notifications & Alerts")
    print("⚙️ Full Device Control")
    print("=" * 60)
    
    try:
        app = ParentMobileAppSimulator()
        app.run()
    except Exception as e:
    logger.error(f"Error: {e}")f"❌ App error: {e}") 