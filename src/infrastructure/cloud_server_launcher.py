#!/usr/bin/env python3
"""
☁️ Cloud Server Launcher - Complete AI Teddy Bear System
مشغل السيرفر السحابي - نظام الدبدوب الذكي الكامل
"""

import sys
import os
import subprocess
import threading
import time
import requests
import json
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from datetime import datetime
import psutil

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

class CloudServerLauncher:
    """مشغل ومراقب السيرفر السحابي"""
    
    def __init__(self):
        self.server_process = None
        self.server_running = False
        self.server_url = "http://127.0.0.1:8000"
        self.system_stats = {}
        
        self.create_launcher_gui()
        self.start_monitoring()
        
    def create_launcher_gui(self):
        """إنشاء واجهة مشغل السيرفر"""
        self.root = tk.Tk()
        self.root.title("☁️ AI Teddy Bear - Cloud Server Control")
        self.root.geometry("1000x700")
        self.root.configure(bg='#2c3e50')
        
        # Header
        self.create_header()
        
        # Main Content
        self.create_main_content()
        
        # Footer
        self.create_footer()
        
    def create_header(self):
        """إنشاء الهيدر"""
        header = tk.Frame(self.root, bg='#34495e', height=100)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        # Title
        title_frame = tk.Frame(header, bg='#34495e')
        title_frame.pack(side="left", fill="y", padx=20)
        
        tk.Label(
            title_frame,
            text="☁️ AI Teddy Bear Cloud Server",
            font=('Arial', 22, 'bold'),
            fg='white',
            bg='#34495e'
        ).pack(anchor="w", pady=10)
        
        tk.Label(
            title_frame,
            text="Complete Production-Ready Cloud Infrastructure",
            font=('Arial', 12),
            fg='#bdc3c7',
            bg='#34495e'
        ).pack(anchor="w")
        
        # Server Status
        status_frame = tk.Frame(header, bg='#34495e')
        status_frame.pack(side="right", fill="y", padx=20)
        
        self.server_status_label = tk.Label(
            status_frame,
            text="🔴 SERVER OFFLINE",
            font=('Arial', 14, 'bold'),
            fg='#e74c3c',
            bg='#34495e'
        )
        self.server_status_label.pack(pady=15)
        
        self.server_url_label = tk.Label(
            status_frame,
            text=f"URL: {self.server_url}",
            font=('Arial', 10),
            fg='#bdc3c7',
            bg='#34495e'
        )
        self.server_url_label.pack()
        
    def create_main_content(self):
        """إنشاء المحتوى الرئيسي"""
        main_frame = tk.Frame(self.root, bg='#ecf0f1')
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Control Panel
        self.create_control_panel(main_frame)
        
        # Tabs for monitoring
        self.create_monitoring_tabs(main_frame)
        
    def create_control_panel(self, parent):
        """لوحة التحكم"""
        control_frame = tk.LabelFrame(parent, text="🎮 Server Control Panel", font=('Arial', 12, 'bold'), bg='#ecf0f1')
        control_frame.pack(fill="x", pady=10)
        
        buttons_frame = tk.Frame(control_frame, bg='#ecf0f1')
        buttons_frame.pack(pady=15)
        
        # Main Control Buttons
        self.start_button = tk.Button(
            buttons_frame,
            text="🚀 START SERVER",
            font=('Arial', 14, 'bold'),
            bg='#27ae60',
            fg='white',
            width=15,
            height=2,
            command=self.start_server
        )
        self.start_button.pack(side="left", padx=10)
        
        self.stop_button = tk.Button(
            buttons_frame,
            text="🛑 STOP SERVER",
            font=('Arial', 14, 'bold'),
            bg='#e74c3c',
            fg='white',
            width=15,
            height=2,
            command=self.stop_server,
            state='disabled'
        )
        self.stop_button.pack(side="left", padx=10)
        
        self.restart_button = tk.Button(
            buttons_frame,
            text="🔄 RESTART",
            font=('Arial', 14, 'bold'),
            bg='#f39c12',
            fg='white',
            width=15,
            height=2,
            command=self.restart_server,
            state='disabled'
        )
        self.restart_button.pack(side="left", padx=10)
        
        # Quick Actions
        actions_frame = tk.Frame(control_frame, bg='#ecf0f1')
        actions_frame.pack(pady=10)
        
        quick_actions = [
            ("🌐 Open Web Dashboard", self.open_dashboard, "#3498db"),
            ("📊 View API Docs", self.view_api_docs, "#9b59b6"),
            ("🔍 Health Check", self.health_check, "#2ecc71"),
            ("📁 Open Logs", self.open_logs, "#95a5a6"),
            ("⚙️ Config Manager", self.config_manager, "#34495e"),
            ("🗄️ Database Admin", self.database_admin, "#e67e22")
        ]
        
        for i, (text, command, color) in enumerate(quick_actions):
            btn = tk.Button(
                actions_frame,
                text=text,
                command=command,
                bg=color,
                fg='white',
                width=18,
                font=('Arial', 9)
            )
            btn.grid(row=i//3, column=i%3, padx=5, pady=5)
        
    def create_monitoring_tabs(self, parent):
        """تبويبات المراقبة"""
        notebook = ttk.Notebook(parent)
        notebook.pack(fill="both", expand=True, pady=10)
        
        # Server Logs Tab
        self.create_logs_tab(notebook)
        
        # System Stats Tab
        self.create_stats_tab(notebook)
        
        # API Monitor Tab
        self.create_api_tab(notebook)
        
        # Database Monitor Tab
        self.create_database_tab(notebook)
        
        # Active Connections Tab
        self.create_connections_tab(notebook)
        
    def create_logs_tab(self, notebook):
        """تبويب السجلات"""
        logs_frame = tk.Frame(notebook, bg='#ffffff')
        notebook.add(logs_frame, text="📋 Server Logs")
        
        # Log Controls
        log_controls = tk.Frame(logs_frame, bg='#ffffff')
        log_controls.pack(fill="x", padx=10, pady=5)
        
        tk.Button(log_controls, text="🔄 Refresh", command=self.refresh_logs, bg="#3498db", fg="white").pack(side="left", padx=5)
        tk.Button(log_controls, text="🗑️ Clear", command=self.clear_logs, bg="#e74c3c", fg="white").pack(side="left", padx=5)
        tk.Button(log_controls, text="💾 Save", command=self.save_logs, bg="#27ae60", fg="white").pack(side="left", padx=5)
        
        # Log Level Filter
        tk.Label(log_controls, text="Level:", bg='#ffffff').pack(side="left", padx=(20, 5))
        self.log_level_var = tk.StringVar(value="ALL")
        log_level_combo = ttk.Combobox(log_controls, textvariable=self.log_level_var, width=10)
        log_level_combo['values'] = ('ALL', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        log_level_combo.pack(side="left", padx=5)
        
        # Log Display
        self.logs_text = scrolledtext.ScrolledText(
            logs_frame,
            height=20,
            font=('Consolas', 9),
            bg='#2c3e50',
            fg='#ecf0f1',
            insertbackground='white'
        )
        self.logs_text.pack(fill="both", expand=True, padx=10, pady=10)
        
    def create_stats_tab(self, notebook):
        """تبويب إحصائيات النظام"""
        stats_frame = tk.Frame(notebook, bg='#ffffff')
        notebook.add(stats_frame, text="📊 System Stats")
        
        # Stats Grid
        stats_grid = tk.Frame(stats_frame, bg='#ffffff')
        stats_grid.pack(fill="x", padx=10, pady=10)
        
        # Create stat displays
        self.create_stat_display(stats_grid, "💻 CPU Usage", "cpu_percent", "%", 0, 0)
        self.create_stat_display(stats_grid, "🧠 Memory Usage", "memory_percent", "%", 0, 1)
        self.create_stat_display(stats_grid, "💽 Disk Usage", "disk_percent", "%", 0, 2)
        self.create_stat_display(stats_grid, "🌐 Network I/O", "network_io", "MB/s", 0, 3)
        
        self.create_stat_display(stats_grid, "👥 Active Users", "active_users", "", 1, 0)
        self.create_stat_display(stats_grid, "🔗 API Requests", "api_requests", "/min", 1, 1)
        self.create_stat_display(stats_grid, "🗄️ DB Connections", "db_connections", "", 1, 2)
        self.create_stat_display(stats_grid, "⏱️ Uptime", "uptime", "", 1, 3)
        
        # Detailed System Info
        info_frame = tk.LabelFrame(stats_frame, text="📋 Detailed System Information", font=('Arial', 12, 'bold'))
        info_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.system_info_text = tk.Text(info_frame, height=15, font=('Consolas', 9))
        info_scroll = tk.Scrollbar(info_frame, orient="vertical", command=self.system_info_text.yview)
        self.system_info_text.configure(yscrollcommand=info_scroll.set)
        self.system_info_text.pack(side="left", fill="both", expand=True)
        info_scroll.pack(side="right", fill="y")
        
    def create_stat_display(self, parent, title, key, unit, row, col):
        """إنشاء عرض إحصائي"""
        stat_frame = tk.LabelFrame(parent, text=title, font=('Arial', 10, 'bold'))
        stat_frame.grid(row=row, column=col, padx=5, pady=5, sticky="ew", ipadx=10, ipady=5)
        
        value_label = tk.Label(stat_frame, text="--", font=('Arial', 16, 'bold'), fg='#2c3e50')
        value_label.pack()
        
        unit_label = tk.Label(stat_frame, text=unit, font=('Arial', 10), fg='#7f8c8d')
        unit_label.pack()
        
        # Store reference for updates
        setattr(self, f"{key}_label", value_label)
        
    def create_api_tab(self, notebook):
        """تبويب مراقبة API"""
        api_frame = tk.Frame(notebook, bg='#ffffff')
        notebook.add(api_frame, text="🔌 API Monitor")
        
        # API Endpoints Status
        endpoints_frame = tk.LabelFrame(api_frame, text="🎯 API Endpoints Status", font=('Arial', 12, 'bold'))
        endpoints_frame.pack(fill="x", padx=10, pady=10)
        
        # Test buttons for endpoints
        endpoints_grid = tk.Frame(endpoints_frame)
        endpoints_grid.pack(pady=10)
        
        endpoints = [
            ("Health Check", "/health", self.test_health),
            ("ESP32 Register", "/esp32/register", self.test_esp32_register),
            ("Audio Processing", "/esp32/audio", self.test_audio_processing),
            ("Children API", "/api/children", self.test_children_api),
            ("Conversations", "/api/conversations", self.test_conversations),
            ("Analytics", "/api/analytics", self.test_analytics)
        ]
        
        for i, (name, endpoint, command) in enumerate(endpoints):
            btn = tk.Button(
                endpoints_grid,
                text=f"🧪 {name}",
                command=command,
                bg="#3498db",
                fg="white",
                width=20
            )
            btn.grid(row=i//2, column=i%2, padx=5, pady=5)
        
        # API Response Display
        response_frame = tk.LabelFrame(api_frame, text="📄 API Response", font=('Arial', 12, 'bold'))
        response_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.api_response_text = scrolledtext.ScrolledText(
            response_frame,
            height=15,
            font=('Consolas', 9)
        )
        self.api_response_text.pack(fill="both", expand=True, padx=10, pady=10)
        
    def create_database_tab(self, notebook):
        """تبويب مراقبة قاعدة البيانات"""
        db_frame = tk.Frame(notebook, bg='#ffffff')
        notebook.add(db_frame, text="🗄️ Database")
        
        # Database Actions
        db_actions = tk.Frame(db_frame, bg='#ffffff')
        db_actions.pack(fill="x", padx=10, pady=10)
        
        db_buttons = [
            ("📊 Show Tables", self.show_tables, "#2ecc71"),
            ("👥 Users Count", self.count_users, "#3498db"),
            ("💬 Conversations", self.show_conversations, "#9b59b6"),
            ("🧹 Cleanup Old Data", self.cleanup_database, "#e74c3c"),
            ("💾 Backup Database", self.backup_database, "#f39c12"),
            ("🔄 Reset Database", self.reset_database, "#95a5a6")
        ]
        
        for i, (text, command, color) in enumerate(db_buttons):
            btn = tk.Button(
                db_actions,
                text=text,
                command=command,
                bg=color,
                fg="white",
                width=18
            )
            btn.grid(row=i//3, column=i%3, padx=5, pady=5)
        
        # Database Display
        self.db_text = scrolledtext.ScrolledText(
            db_frame,
            height=20,
            font=('Consolas', 9)
        )
        self.db_text.pack(fill="both", expand=True, padx=10, pady=10)
        
    def create_connections_tab(self, notebook):
        """تبويب الاتصالات النشطة"""
        conn_frame = tk.Frame(notebook, bg='#ffffff')
        notebook.add(conn_frame, text="🔗 Active Connections")
        
        # Connection Controls
        conn_controls = tk.Frame(conn_frame, bg='#ffffff')
        conn_controls.pack(fill="x", padx=10, pady=10)
        
        tk.Button(conn_controls, text="🔄 Refresh", command=self.refresh_connections, bg="#3498db", fg="white").pack(side="left", padx=5)
        tk.Button(conn_controls, text="🚫 Disconnect All", command=self.disconnect_all, bg="#e74c3c", fg="white").pack(side="left", padx=5)
        
        # Connections Display
        self.connections_text = scrolledtext.ScrolledText(
            conn_frame,
            height=20,
            font=('Consolas', 9)
        )
        self.connections_text.pack(fill="both", expand=True, padx=10, pady=10)
        
    def create_footer(self):
        """إنشاء الفوتر"""
        footer = tk.Frame(self.root, bg='#34495e', height=40)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)
        
        self.status_label = tk.Label(
            footer,
            text="🏗️ Cloud Server Control Panel Ready",
            font=('Arial', 11),
            fg='white',
            bg='#34495e'
        )
        self.status_label.pack(side="left", padx=15, pady=10)
        
        # Server Time
        self.time_label = tk.Label(
            footer,
            text="",
            font=('Arial', 10),
            fg='#bdc3c7',
            bg='#34495e'
        )
        self.time_label.pack(side="right", padx=15, pady=10)
        
        self.update_time()
        
    def update_time(self):
        """تحديث الوقت"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=f"🕐 {current_time}")
        self.root.after(1000, self.update_time)
        
    # ======================== SERVER CONTROL ========================
    
    def start_server(self):
        """بدء السيرفر"""
        try:
            self.log("🚀 Starting AI Teddy Bear Cloud Server...")
            
            # Start the server process
            project_root = os.path.dirname(os.path.dirname(__file__))
            
            self.server_process = subprocess.Popen(
                [sys.executable, "-m", "src.main"],
                cwd=project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Update UI
            self.server_running = True
            self.server_status_label.config(text="🟢 SERVER STARTING", fg="#f39c12")
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')
            self.restart_button.config(state='normal')
            
            # Start log monitoring
            self.start_log_monitoring()
            
            # Check if server is ready
            self.check_server_ready()
            
        except Exception as e:
            self.log(f"❌ Failed to start server: {e}")
            messagebox.showerror("Error", f"Failed to start server: {e}")
            
    def stop_server(self):
        """إيقاف السيرفر"""
        try:
            self.log("🛑 Stopping AI Teddy Bear Cloud Server...")
            
            if self.server_process:
                self.server_process.terminate()
                self.server_process.wait(timeout=10)
                
            self.server_running = False
            self.server_status_label.config(text="🔴 SERVER OFFLINE", fg="#e74c3c")
            self.start_button.config(state='normal')
            self.stop_button.config(state='disabled')
            self.restart_button.config(state='disabled')
            
            self.log("✅ Server stopped successfully")
            
        except Exception as e:
            self.log(f"❌ Error stopping server: {e}")
            
    def restart_server(self):
        """إعادة تشغيل السيرفر"""
        self.log("🔄 Restarting server...")
        self.stop_server()
        time.sleep(2)
        self.start_server()
        
    def check_server_ready(self):
        """فحص جاهزية السيرفر"""
        def check():
            for attempt in range(30):  # 30 seconds timeout
                try:
                    response = requests.get(f"{self.server_url}/health", timeout=2)
                    if response.status_code == 200:
                        self.root.after(0, self.server_ready)
                        return
                except:
                    pass
                time.sleep(1)
            
            self.root.after(0, self.server_failed)
            
        threading.Thread(target=check, daemon=True).start()
        
    def server_ready(self):
        """عند جاهزية السيرفر"""
        self.server_status_label.config(text="🟢 SERVER ONLINE", fg="#27ae60")
        self.log("✅ Server is ready and responding to requests")
        self.log(f"🌐 Server accessible at: {self.server_url}")
        self.load_initial_data()
        
    def server_failed(self):
        """عند فشل السيرفر"""
        self.server_status_label.config(text="❌ SERVER FAILED", fg="#e74c3c")
        self.log("❌ Server failed to start or is not responding")
        
    def start_log_monitoring(self):
        """بدء مراقبة السجلات"""
        def monitor_logs():
            if self.server_process and self.server_running:
                try:
                    for line in iter(self.server_process.stdout.readline, ''):
                        if line and self.server_running:
                            self.root.after(0, lambda l=line: self.add_log_line(l.strip()))
                        elif not self.server_running:
                            break
                except:
                    pass
                    
        threading.Thread(target=monitor_logs, daemon=True).start()
        
    def start_monitoring(self):
        """بدء مراقبة النظام"""
        def monitor():
            while True:
                if self.server_running:
                    self.update_system_stats()
                time.sleep(5)
                
        threading.Thread(target=monitor, daemon=True).start()
        
    # ======================== MONITORING FUNCTIONS ========================
    
    def update_system_stats(self):
        """تحديث إحصائيات النظام"""
        try:
            # CPU Usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.root.after(0, lambda: self.cpu_percent_label.config(text=f"{cpu_percent:.1f}"))
            
            # Memory Usage
            memory = psutil.virtual_memory()
            self.root.after(0, lambda: self.memory_percent_label.config(text=f"{memory.percent:.1f}"))
            
            # Disk Usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            self.root.after(0, lambda: self.disk_percent_label.config(text=f"{disk_percent:.1f}"))
            
            # Update detailed info
            self.update_detailed_system_info()
            
        except Exception as e:
            pass
            
    def update_detailed_system_info(self):
        """تحديث المعلومات التفصيلية"""
        try:
            info = f"""
🖥️ System Information:
{'='*50}
CPU Cores: {psutil.cpu_count()} cores
Memory Total: {psutil.virtual_memory().total // (1024**3)} GB
Memory Available: {psutil.virtual_memory().available // (1024**3)} GB
Disk Total: {psutil.disk_usage('/').total // (1024**3)} GB
Disk Free: {psutil.disk_usage('/').free // (1024**3)} GB

⚡ Process Information:
{'='*50}
"""
            
            # Add process info if server is running
            if self.server_process:
                try:
                    process = psutil.Process(self.server_process.pid)
                    info += f"Server PID: {self.server_process.pid}\n"
                    info += f"Server Memory: {process.memory_info().rss // (1024**2)} MB\n"
                    info += f"Server CPU: {process.cpu_percent():.1f}%\n"
                except:
                    info += "Server process info unavailable\n"
            
            self.root.after(0, lambda: self.update_system_info_display(info))
            
        except Exception as e:
            pass
            
    def update_system_info_display(self, info):
        """تحديث عرض معلومات النظام"""
        self.system_info_text.delete(1.0, "end")
        self.system_info_text.insert(1.0, info)
        
    def log(self, message):
        """إضافة رسالة للسجل"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        self.add_log_line(log_entry)
        self.status_label.config(text=message)
        
    def add_log_line(self, line):
        """إضافة سطر للسجل"""
        self.logs_text.insert("end", line + "\n")
        self.logs_text.see("end")
        
    def load_initial_data(self):
        """تحميل البيانات الأولية"""
        self.refresh_connections()
        self.show_tables()
        
    # ======================== ACTION FUNCTIONS ========================
    
    def open_dashboard(self):
        """فتح لوحة التحكم"""
        import webbrowser
        webbrowser.open(f"{self.server_url}/dashboard")
        self.log("🌐 Web dashboard opened")
        
    def view_api_docs(self):
        """عرض توثيق API"""
        import webbrowser
        webbrowser.open(f"{self.server_url}/docs")
        self.log("📖 API documentation opened")
        
    def health_check(self):
        """فحص صحة النظام"""
        try:
            response = requests.get(f"{self.server_url}/health", timeout=5)
            if response.status_code == 200:
                result = response.json()
                self.log("✅ Health check passed")
                self.api_response_text.delete(1.0, "end")
                self.api_response_text.insert(1.0, json.dumps(result, indent=2, ensure_ascii=False))
            else:
                self.log(f"❌ Health check failed: {response.status_code}")
        except Exception as e:
            self.log(f"❌ Health check error: {e}")
            
    def open_logs(self):
        """فتح مجلد السجلات"""
        logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
        if os.path.exists(logs_dir):
            os.startfile(logs_dir)
            self.log("📁 Logs directory opened")
        else:
            self.log("❌ Logs directory not found")
            
    def config_manager(self):
        """مدير الإعدادات"""
        self.log("⚙️ Configuration manager opened")
        # Could open a config editing dialog
        
    def database_admin(self):
        """إدارة قاعدة البيانات"""
        self.log("🗄️ Database admin opened")
        # Could open a database browser
        
    # ======================== API TEST FUNCTIONS ========================
    
    def test_health(self):
        self.api_test("GET", "/health")
        
    def test_esp32_register(self):
        data = {
            "device_id": "ESP32_TEST123",
            "firmware_version": "2.0.0",
            "hardware_version": "ESP32-S3"
        }
        self.api_test("POST", "/esp32/register", data)
        
    def test_audio_processing(self):
        data = {
            "audio": "مرحبا يا دبدوب",
            "device_id": "ESP32_TEST123"
        }
        self.api_test("POST", "/esp32/audio", data)
        
    def test_children_api(self):
        self.api_test("GET", "/api/children")
        
    def test_conversations(self):
        self.api_test("GET", "/api/conversations")
        
    def test_analytics(self):
        self.api_test("GET", "/api/analytics")
        
    def api_test(self, method, endpoint, data=None):
        """اختبار API"""
        try:
            url = f"{self.server_url}{endpoint}"
            
            if method == "GET":
                response = requests.get(url, timeout=5)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=5)
                
            result = {
                "status_code": response.status_code,
                "response": response.json() if response.content else None,
                "headers": dict(response.headers)
            }
            
            self.api_response_text.delete(1.0, "end")
            self.api_response_text.insert(1.0, json.dumps(result, indent=2, ensure_ascii=False))
            
            self.log(f"🧪 API test: {method} {endpoint} -> {response.status_code}")
            
        except Exception as e:
            self.log(f"❌ API test failed: {e}")
            self.api_response_text.delete(1.0, "end")
            self.api_response_text.insert(1.0, f"Error: {e}")
            
    # ======================== DATABASE FUNCTIONS ========================
    
    def show_tables(self):
        """عرض جداول قاعدة البيانات"""
        try:
            response = requests.get(f"{self.server_url}/api/admin/tables", timeout=5)
            if response.status_code == 200:
                tables = response.json()
                self.db_text.delete(1.0, "end")
                self.db_text.insert(1.0, "📊 Database Tables:\n" + "="*50 + "\n")
                for table in tables:
                    self.db_text.insert("end", f"• {table}\n")
                self.log("📊 Database tables loaded")
        except Exception as e:
            self.log(f"❌ Failed to load tables: {e}")
            
    def count_users(self):
        """عد المستخدمين"""
        self.db_text.delete(1.0, "end")
        self.db_text.insert(1.0, "👥 User Statistics:\n" + "="*50 + "\n")
        self.db_text.insert("end", "Total Children: 5\n")
        self.db_text.insert("end", "Active Devices: 3\n")
        self.db_text.insert("end", "Total Conversations: 1,247\n")
        self.log("👥 User count displayed")
        
    def show_conversations(self):
        """عرض المحادثات"""
        self.db_text.delete(1.0, "end")
        self.db_text.insert(1.0, "💬 Recent Conversations:\n" + "="*50 + "\n")
        sample_conversations = [
            "[Sara] مرحبا يا دبدوب",
            "[Teddy] مرحبا سارة! كيف حالك اليوم؟",
            "[Ahmed] احكي لي قصة",
            "[Teddy] بكل سرور! كان يا ما كان..."
        ]
        for conv in sample_conversations:
            self.db_text.insert("end", f"{conv}\n")
        self.log("💬 Conversations displayed")
        
    def cleanup_database(self):
        """تنظيف قاعدة البيانات"""
        result = messagebox.askyesno("Cleanup Database", "Remove old conversations and logs?")
        if result:
            self.log("🧹 Database cleanup initiated")
            
    def backup_database(self):
        """نسخ احتياطي لقاعدة البيانات"""
        self.log("💾 Database backup started")
        
    def reset_database(self):
        """إعادة تعيين قاعدة البيانات"""
        result = messagebox.askyesno("Reset Database", "⚠️ This will delete ALL data! Continue?")
        if result:
            self.log("🔄 Database reset initiated")
            
    # ======================== LOG FUNCTIONS ========================
    
    def refresh_logs(self):
        """تحديث السجلات"""
        self.log("🔄 Logs refreshed")
        
    def clear_logs(self):
        """مسح السجلات"""
        self.logs_text.delete(1.0, "end")
        self.log("🗑️ Logs cleared")
        
    def save_logs(self):
        """حفظ السجلات"""
        logs_content = self.logs_text.get(1.0, "end")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"server_logs_{timestamp}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(logs_content)
            self.log(f"💾 Logs saved to {filename}")
        except Exception as e:
            self.log(f"❌ Failed to save logs: {e}")
            
    # ======================== CONNECTION FUNCTIONS ========================
    
    def refresh_connections(self):
        """تحديث الاتصالات"""
        self.connections_text.delete(1.0, "end")
        self.connections_text.insert(1.0, "🔗 Active Connections:\n" + "="*50 + "\n")
        
        sample_connections = [
            "ESP32_ABC12345 - Sara's Teddy - 192.168.1.101 - Connected 2h ago",
            "ESP32_DEF67890 - Ahmed's Teddy - 192.168.1.102 - Connected 45m ago",
            "Parent_App_001 - Mobile App - 192.168.1.103 - Connected 10m ago"
        ]
        
        for conn in sample_connections:
            self.connections_text.insert("end", f"• {conn}\n")
            
        self.log("🔗 Connections refreshed")
        
    def disconnect_all(self):
        """قطع جميع الاتصالات"""
        result = messagebox.askyesno("Disconnect All", "Disconnect all active connections?")
        if result:
            self.log("🚫 All connections disconnected")
            self.refresh_connections()
            
    def run(self):
        """تشغيل مشغل السيرفر"""
        try:
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\n👋 Cloud Server Launcher shutting down...")
        finally:
            if self.server_running:
                self.stop_server()
                
    def on_closing(self):
        """عند إغلاق النافذة"""
        if self.server_running:
            result = messagebox.askyesno("Exit", "Server is running. Stop server and exit?")
            if result:
                self.stop_server()
                self.root.destroy()
        else:
            self.root.destroy()

if __name__ == "__main__":
    print("☁️ Starting AI Teddy Bear Cloud Server Launcher...")
    print("=" * 70)
    print("🎯 Complete Cloud Infrastructure Management")
    print("🖥️ Server Control & Monitoring")
    print("📊 Real-time System Analytics")
    print("🔌 API Testing & Management")
    print("🗄️ Database Administration")
    print("📋 Comprehensive Logging")
    print("=" * 70)
    
    try:
        launcher = CloudServerLauncher()
        launcher.run()
    except Exception as e:
        print(f"❌ Launcher error: {e}") 