import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

#!/usr/bin/env python3
"""
🚀 Complete AI Teddy Bear System Launcher
مشغل النظام الكامل للدبدوب الذكي - المحاكيات الثلاث
"""
import structlog

logger = structlog.get_logger(__name__)


import os
import subprocess
import sys
import threading
import time
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

import requests


class CompleteTeddySystemLauncher:
    """مشغل النظام الكامل مع المحاكيات الثلاث"""
    
    def __init__(self):
        self.processes = {
            'cloud_server': None,
            'esp32_simulator': None,
            'parent_app': None
        }
        
        self.status = {
            'cloud_server': False,
            'esp32_simulator': False,
            'parent_app': False
        }
        
        self.create_launcher_gui()
        
    def create_launcher_gui(self) -> Any:
        """إنشاء واجهة مشغل النظام"""
        self.root = tk.Tk()
        self.root.title("🚀 AI Teddy Bear - Complete System Launcher")
        self.root.geometry("800x600")
        self.root.configure(bg='#1a1a2e')
        
        # Header
        self.create_header()
        
        # System Overview
        self.create_system_overview()
        
        # Control Panel
        self.create_control_panel()
        
        # Status Monitor
        self.create_status_monitor()
        
        # Footer
        self.create_footer()
        
    def create_header(self) -> Any:
        """إنشاء الهيدر"""
        header = tk.Frame(self.root, bg='#16213e', height=120)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        # Title
        tk.Label(
            header,
            text="🧸 AI Teddy Bear System",
            font=('Arial', 24, 'bold'),
            fg='#00d4ff',
            bg='#16213e'
        ).pack(pady=10)
        
        tk.Label(
            header,
            text="Complete Production-Ready Simulation Suite",
            font=('Arial', 14),
            fg='#a8a8a8',
            bg='#16213e'
        ).pack()
        
        # System Status Indicator
        self.overall_status = tk.Label(
            header,
            text="🔴 SYSTEM OFFLINE",
            font=('Arial', 16, 'bold'),
            fg='#ff4757',
            bg='#16213e'
        )
        self.overall_status.pack(pady=10)
        
    def create_system_overview(self) -> Any:
        """نظرة عامة على النظام"""
        overview_frame = tk.LabelFrame(
            self.root, 
            text="🏗️ System Architecture", 
            font=('Arial', 12, 'bold'),
            bg='#0f3460',
            fg='white'
        )
        overview_frame.pack(fill="x", padx=15, pady=10)
        
        # Architecture Diagram (text-based)
        arch_text = tk.Text(
            overview_frame,
            height=8,
            font=('Consolas', 10),
            bg='#1a1a2e',
            fg='#00d4ff',
            relief='flat'
        )
        arch_text.pack(padx=10, pady=10, fill="x")
        
        architecture = '''
        📱 Parent Mobile App     ←→     ☁️ Cloud Server     ←→     🧸 ESP32 Teddy
        =====================           ==================           ==================
        • Family Management             • FastAPI Server              • Wake Word Detection
        • Real-time Monitoring          • OpenAI Integration          • Audio Recording  
        • Settings Control              • SQLite Database             • Voice Playback
        • Analytics Dashboard           • WebSocket Support           • LED Status
        • Push Notifications            • RESTful APIs                • WiFi Connectivity
        • Volume Control                • Advanced Analytics          • Hardware Simulation
        
        🎯 Complete Simulation: Test the entire system before production deployment!
        '''
        
        arch_text.insert(1.0, architecture)
        arch_text.config(state='disabled')
        
    def create_control_panel(self) -> Any:
        """لوحة التحكم الرئيسية"""
        control_frame = tk.LabelFrame(
            self.root,
            text="🎮 System Control Panel",
            font=('Arial', 12, 'bold'),
            bg='#0f3460',
            fg='white'
        )
        control_frame.pack(fill="x", padx=15, pady=10)
        
        # Quick Launch Buttons
        quick_frame = tk.Frame(control_frame, bg='#0f3460')
        quick_frame.pack(pady=15)
        
        # Launch All Button
        self.launch_all_btn = tk.Button(
            quick_frame,
            text="🚀 LAUNCH COMPLETE SYSTEM",
            font=('Arial', 16, 'bold'),
            bg='#2ed573',
            fg='white',
            width=25,
            height=2,
            command=self.launch_complete_system
        )
        self.launch_all_btn.pack(pady=10)
        
        # Individual Controls
        controls_grid = tk.Frame(control_frame, bg='#0f3460')
        controls_grid.pack(pady=10)
        
        # Cloud Server Controls
        self.create_component_control(
            controls_grid, 
            "☁️ Cloud Server", 
            "The brain of the system",
            "cloud_server",
            0, 0
        )
        
        # ESP32 Simulator Controls  
        self.create_component_control(
            controls_grid,
            "🧸 ESP32 Teddy Simulator", 
            "Hardware teddy bear simulation",
            "esp32_simulator", 
            0, 1
        )
        
        # Parent App Controls
        self.create_component_control(
            controls_grid,
            "📱 Parent Mobile App",
            "Family control dashboard", 
            "parent_app",
            1, 0
        )
        
        # Emergency Stop
        emergency_frame = tk.Frame(control_frame, bg='#0f3460')
        emergency_frame.pack(pady=15)
        
        self.emergency_btn = tk.Button(
            emergency_frame,
            text="🛑 EMERGENCY STOP ALL",
            font=('Arial', 14, 'bold'),
            bg='#ff4757',
            fg='white',
            width=20,
            command=self.emergency_stop_all
        )
        self.emergency_btn.pack()
        
    def create_component_control(self, parent, title, description, component_key, row, col) -> Any:
        """إنشاء تحكم مكون"""
        component_frame = tk.LabelFrame(
            parent,
            text=title,
            font=('Arial', 11, 'bold'),
            bg='#1a1a2e',
            fg='#00d4ff',
            width=250,
            height=180
        )
        component_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        component_frame.grid_propagate(False)
        
        # Description
        tk.Label(
            component_frame,
            text=description,
            font=('Arial', 9),
            fg='#a8a8a8',
            bg='#1a1a2e',
            wraplength=200
        ).pack(pady=5)
        
        # Status
        status_label = tk.Label(
            component_frame,
            text="🔴 OFFLINE",
            font=('Arial', 12, 'bold'),
            fg='#ff4757',
            bg='#1a1a2e'
        )
        status_label.pack(pady=5)
        setattr(self, f"{component_key}_status_label", status_label)
        
        # Controls
        buttons_frame = tk.Frame(component_frame, bg='#1a1a2e')
        buttons_frame.pack(pady=10)
        
        start_btn = tk.Button(
            buttons_frame,
            text="▶️ Start",
            bg='#2ed573',
            fg='white',
            width=8,
            command=lambda: self.start_component(component_key)
        )
        start_btn.pack(side="left", padx=2)
        setattr(self, f"{component_key}_start_btn", start_btn)
        
        stop_btn = tk.Button(
            buttons_frame,
            text="⏹️ Stop", 
            bg='#ff4757',
            fg='white',
            width=8,
            state='disabled',
            command=lambda: self.stop_component(component_key)
        )
        stop_btn.pack(side="left", padx=2)
        setattr(self, f"{component_key}_stop_btn", stop_btn)
        
    def create_status_monitor(self) -> Any:
        """مراقب الحالة"""
        status_frame = tk.LabelFrame(
            self.root,
            text="📊 System Status Monitor",
            font=('Arial', 12, 'bold'),
            bg='#0f3460',
            fg='white'
        )
        status_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Log Display
        self.log_text = tk.Text(
            status_frame,
            height=12,
            font=('Consolas', 9),
            bg='#1a1a2e',
            fg='#00d4ff',
            insertbackground='white'
        )
        
        log_scroll = tk.Scrollbar(status_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scroll.set)
        
        self.log_text.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        log_scroll.pack(side="right", fill="y", pady=10)
        
        # Initial welcome message
        self.log("🚀 AI Teddy Bear System Launcher Ready")
        self.log("💡 Click 'LAUNCH COMPLETE SYSTEM' to start all components")
        self.log("📋 Monitor this area for system status updates")
        
    def create_footer(self) -> Any:
        """إنشاء الفوتر"""
        footer = tk.Frame(self.root, bg='#16213e', height=50)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)
        
        # Instructions
        instructions = tk.Label(
            footer,
            text="🎯 Instructions: Launch the complete system to test all features before production",
            font=('Arial', 11),
            fg='#a8a8a8',
            bg='#16213e'
        )
        instructions.pack(side="left", padx=15, pady=15)
        
        # System Time
        self.time_label = tk.Label(
            footer,
            text="",
            font=('Arial', 10),
            fg='#00d4ff',
            bg='#16213e'
        )
        self.time_label.pack(side="right", padx=15, pady=15)
        
        self.update_time()
        
    def update_time(self) -> Any:
        """تحديث الوقت"""
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if hasattr(self, 'time_label') and self.time_label.winfo_exists():
                self.time_label.config(text=f"🕐 {current_time}")
                self.root.after(1000, self.update_time)
        except Exception as e:
    logger.error(f"Error: {e}", exc_info=True)as e:
    logger.error(f"Error: {e}", exc_info=True)s e:
    logger.warning(f"Ignored exception: {e}")
        
    def log(self, message) -> Any:
        """إضافة رسالة للسجل"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert("end", log_entry)
        self.log_text.see("end")
        logger.info(log_entry.strip())
        
    def update_overall_status(self) -> Any:
        """تحديث الحالة العامة"""
        online_count = sum(self.status.values())
        total_count = len(self.status)
        
        if online_count == 0:
            self.overall_status.config(text="🔴 SYSTEM OFFLINE", fg="#ff4757")
        elif online_count == total_count:
            self.overall_status.config(text="🟢 SYSTEM FULLY ONLINE", fg="#2ed573")
        else:
            self.overall_status.config(text=f"🟡 SYSTEM PARTIAL ({online_count}/{total_count})", fg="#ffa502")
            
    # ======================== COMPONENT CONTROL ========================
    
    def start_component(self, component) -> Any:
        """بدء مكون"""
        try:
            self.log(f"🚀 Starting {component}...")
            
            if component == "cloud_server":
                self.start_cloud_server()
            elif component == "esp32_simulator":
                self.start_esp32_simulator()
            elif component == "parent_app":
                self.start_parent_app()
                
        except Exception as e:
            self.log(f"❌ Failed to start {component}: {e}")
            
    def stop_component(self, component) -> Any:
        """إيقاف مكون"""
        try:
            self.log(f"🛑 Stopping {component}...")
            
            if self.processes[component]:
                self.processes[component].terminate()
                self.processes[component] = None
                
            self.status[component] = False
            self.update_component_ui(component, False)
            self.update_overall_status()
            
            self.log(f"✅ {component} stopped")
            
        except Exception as e:
            self.log(f"❌ Failed to stop {component}: {e}")
            
    def start_cloud_server(self) -> Any:
        """بدء السيرفر السحابي"""
        try:
            # تشغيل السيرفر مباشرة بدلاً من مشغل السيرفر
            self.processes['cloud_server'] = subprocess.Popen(
                [sys.executable, "-m", "src.main"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.status['cloud_server'] = True
            self.update_component_ui('cloud_server', True)
            self.update_overall_status()
            
            self.log("✅ Cloud server launcher started")
            
            # Check if server is responding
            threading.Thread(target=self.check_cloud_server_health, daemon=True).start()
            
        except Exception as e:
            self.log(f"❌ Cloud server start failed: {e}")
            
    def start_esp32_simulator(self) -> Any:
        """بدء محاكي ESP32"""
        try:
            script_path = os.path.join("simulators", "esp32_teddy_simulator.py")
            
            self.processes['esp32_simulator'] = subprocess.Popen(
                [sys.executable, script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.status['esp32_simulator'] = True
            self.update_component_ui('esp32_simulator', True)
            self.update_overall_status()
            
            self.log("✅ ESP32 teddy simulator started")
            
        except Exception as e:
            self.log(f"❌ ESP32 simulator start failed: {e}")
            
    def start_parent_app(self) -> Any:
        """بدء تطبيق الأهل"""
        try:
            script_path = os.path.join("simulators", "parent_mobile_app_simulator.py")
            
            self.processes['parent_app'] = subprocess.Popen(
                [sys.executable, script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,  
                text=True
            )
            
            self.status['parent_app'] = True
            self.update_component_ui('parent_app', True)
            self.update_overall_status()
            
            self.log("✅ Parent mobile app started")
            
        except Exception as e:
            self.log(f"❌ Parent app start failed: {e}")
            
    def update_component_ui(self, component, online) -> Any:
        """تحديث واجهة المكون"""
        status_label = getattr(self, f"{component}_status_label")
        start_btn = getattr(self, f"{component}_start_btn")
        stop_btn = getattr(self, f"{component}_stop_btn")
        
        if online:
            status_label.config(text="🟢 ONLINE", fg="#2ed573")
            start_btn.config(state='disabled')
            stop_btn.config(state='normal')
        else:
            status_label.config(text="🔴 OFFLINE", fg="#ff4757")
            start_btn.config(state='normal')
            stop_btn.config(state='disabled')
            
    def check_cloud_server_health(self) -> Any:
        """فحص صحة السيرفر السحابي"""
        for attempt in range(30):  # 30 seconds timeout
            try:
                response = requests.get("http://127.0.0.1:8000/health", timeout=2)
                if response.status_code == 200:
   except ConnectionError as e:
    logger.error(f"Error in operation: {e}", exc_info=True)ConnectionError as e:
    logger.error(f"Error in operation: {e}", exc_info=True)         self.root.after(0, lambda: self.log("✅ Cloud server is responding to requests"))
     except ConnectionError as e:
    logger.warning(f"Ignoring error: {e}")      except ConnectionError as e:
    logger.error(f"Error in operation: {e}", exc_info=True)ConnectionError as e:
    logger.error(f"Error in operation: {e}", exc_info=True)onnectionError as e:
    logger.warning(f"Ignoring error: {e}")
            time.sleep(1)
            
        self.root.after(0, lambda: self.log("⚠️ Cloud server may not be responding"))
        
    def launch_complete_system(self) -> Any:
        """تشغيل النظام الكامل"""
        self.log("🚀 Launching Complete AI Teddy Bear System...")
        self.log("📋 This will start all three components:")
        self.log("   1. ☁️ Cloud Server (Backend)")
        self.log("   2. 🧸 ESP32 Teddy Simulator (Hardware)")
        self.log("   3. 📱 Parent Mobile App (Control)")
        
        # Launch in sequence with delays
        self.launch_all_btn.config(state='disabled', text="🚀 LAUNCHING...")
        
        # Start cloud server first
        threading.Thread(target=self.launch_sequence, daemon=True).start()
        
    def launch_sequence(self) -> Any:
        """تسلسل التشغيل"""
        try:
            # Step 1: Cloud Server
            self.root.after(0, lambda: self.log("🔥 Step 1: Starting Cloud Server..."))
            self.start_cloud_server()
            time.sleep(5)  # Wait for server to initialize
            
            # Step 2: ESP32 Simulator
            self.root.after(0, lambda: self.log("🔥 Step 2: Starting ESP32 Teddy Simulator..."))
            self.start_esp32_simulator()
            time.sleep(2)
            
            # Step 3: Parent App
            self.root.after(0, lambda: self.log("🔥 Step 3: Starting Parent Mobile App..."))
            self.start_parent_app()
            time.sleep(2)
            
            # Complete
            self.root.after(0, lambda: self.launch_complete())
            
        except Exception as e:
            self.root.after(0, lambda: self.log(f"❌ Launch sequence failed: {e}"))
            self.root.after(0, lambda: self.launch_all_btn.config(state='normal', text="🚀 LAUNCH COMPLETE SYSTEM"))
            
    def launch_complete(self) -> Any:
        """اكتمال التشغيل"""
        self.launch_all_btn.config(state='normal', text="🚀 LAUNCH COMPLETE SYSTEM")
        
        self.log("🎉 SYSTEM LAUNCH COMPLETE!")
        self.log("=" * 50)
        self.log("✅ All components are now running")
        self.log("🧸 You can now test the complete AI Teddy Bear system")
        self.log("📱 Use the Parent App to control and monitor")
        self.log("🎤 Use the ESP32 Simulator to test conversations")
        self.log("☁️ All data is processed through the Cloud Server")
        self.log("=" * 50)
        
        # Show success message
        messagebox.showinfo(
            "🎉 Launch Complete!",
            "The complete AI Teddy Bear system is now running!\n\n"
            "You can now:\n"
            "• Test conversations with the ESP32 Teddy\n"
            "• Monitor and control via Parent App\n"  
            "• View real-time analytics\n"
            "• Test all advanced features\n\n"
            "All components are connected and ready!"
        )
        
    def emergency_stop_all(self) -> Any:
        """إيقاف طوارئ لجميع المكونات"""
        result = messagebox.askyesno(
            "🛑 Emergency Stop",
            "Stop all system components immediately?"
        )
        
        if result:
            self.log("🛑 EMERGENCY STOP ACTIVATED")
            
            for component in self.processes:
                if self.processes[component]:
                    try:
 except IndexError as e:
    logger.error(f"Error in operation: {e}", exc_info=True)                self.processes[component].terminate()
                   except IndexError as e:
    logger.error(f"Error in operation: {e}", exc_info=True)f.processes[component] = None
                        self.status[component] = False
                        self.update_component_ui(compexcept IndexError as e:
    logger.warning(f"Ignoring error: {e}")cept:
                        pass
                        
            self.update_overall_status()
            self.log("✅ All components stopped")
            
    def run(self) -> Any:
        """تشغيل مشغل النظام"""
        try:
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.root.mainloop()
        except Exception as e:
    logger.error(f"Error: {e}")"\n👋 System Launcher shutting down...")
        finally:
            self.emergency_stop_all()
            
    def on_closing(self) -> Any:
        """عند إغلاق النافذة"""
        active_components = [comp for comp, status in self.status.items() if status]
        
        if active_components:
            result = messagebox.askyesno(
                "Exit System",
                f"The following components are still running:\n"
                f"{', '.join(active_components)}\n\n"
                f"Stop all components and exit?"
            )
            if result:
                self.emergency_stop_all()
                self.root.destroy()
        else:
            self.root.destroy()

if __name__ == "__main__":
    logger.info("🚀 Starting Complete AI Teddy Bear System Launcher...")
    logger.info("=" * 70)
    logger.info("🎯 Production-Ready Simulation Suite")
    logger.info("☁️ Cloud Server - AI Processing Backend")
    logger.info("🧸 ESP32 Teddy - Hardware Simulation")
    logger.info("📱 Parent App - Family Control Dashboard")
    logger.info("🔗 Full Integration Testing Environment")
    logger.info("=" * 70)
    
    try:
        launcher = CompleteTeddySystemLauncher()
        launcher.run()
    except Exception as e:
    logger.error(f"Error: {e}")f"❌ System Launcher error: {e}") 