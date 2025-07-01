"""GUI management service for ESP32 teddy bear simulator."""

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any, Callable, Dict

import structlog


logger = structlog.get_logger(__name__)


class GUIManagementService:
    """Service for managing the GUI interface of the ESP32 simulator."""

    def __init__(self, device_id: str):
        self.device_id = device_id
        self.root = None
        self.gui_components = {}
        self.update_callbacks = {}
        self.gui_thread = None

        logger.info(" GUI management service initialized")

    def register_update_callback(self, component: str, callback: Callable) -> None:
        """Register callback for GUI component updates."""
        self.update_callbacks[component] = callback

    def initialize_gui(self) -> tk.Tk:
        """Initialize the main GUI window."""
        try:
            self.root = tk.Tk()
            self.root.title(f" ESP32 Teddy Bear - {self.device_id}")
            self.root.geometry("600x800")
            self.root.configure(bg="#2c3e50")

            # Create main components
            self._create_header()
            self._create_status_panel()
            self._create_control_panel()
            self._create_child_panel()
            self._create_activity_panel()
            self._create_features_panel()

            # Setup close handler
            self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

            logger.info(" GUI initialized successfully")
            return self.root

        except Exception as e:
            logger.error(f" GUI initialization failed: {e}")
            raise

    def update_device_status(self, status_data: Dict[str, Any]) -> None:
        """Update device status display."""
        try:
            if "status_label" in self.gui_components:
                power_state = status_data.get("power_state", "powered_off")
                if power_state == "powered_on":
                    text = " POWERED ON"
                    color = "green"
                else:
                    text = " POWERED OFF"
                    color = "red"

                self.gui_components["status_label"].config(text=text, fg=color)

            if (
                "led_canvas" in self.gui_components
                and "led_circle" in self.gui_components
            ):
                led_color = status_data.get("hardware", {}).get("led_status", "red")
                self.gui_components["led_canvas"].itemconfig(
                    self.gui_components["led_circle"], fill=led_color
                )

            if "volume_label" in self.gui_components:
                volume = status_data.get("hardware", {}).get("volume_level", 50)
                self.gui_components["volume_label"].config(text=f" Volume: {volume}%")

        except Exception as e:
            logger.error(f" Device status update failed: {e}")

    def update_network_status(self, network_data: Dict[str, Any]) -> None:
        """Update network status display."""
        try:
            wifi_status = network_data.get("wifi", {})
            server_status = network_data.get("server", {})

            if "wifi_label" in self.gui_components:
                if wifi_status.get("status") == "connected":
                    text = f" WiFi: {wifi_status.get('ssid', 'Connected')} "
                else:
                    text = " WiFi: Disconnected"
                self.gui_components["wifi_label"].config(text=text)

            if "server_status_label" in self.gui_components:
                if server_status.get("status") == "connected":
                    text = " Server: Connected"
                    color = "green"
                else:
                    text = " Server: Disconnected"
                    color = "red"
                self.gui_components["server_status_label"].config(text=text, fg=color)

        except Exception as e:
            logger.error(f" Network status update failed: {e}")

    def update_audio_visualization(self, viz_data: Dict[str, Any]) -> None:
        """Update audio visualization."""
        try:
            if not viz_data.get("is_active", False):
                return

            if (
                "audio_visualizer" in self.gui_components
                and "visualizer_bars" in self.gui_components
            ):
                heights = viz_data.get("bar_heights", [])
                colors = viz_data.get("colors", [])
                bars = self.gui_components["visualizer_bars"]

                for i, (height, color) in enumerate(zip(heights, colors)):
                    if i < len(bars):
                        y_top = 70 - height
                        self.gui_components["audio_visualizer"].coords(
                            bars[i], i * 10 + 5, y_top, i * 10 + 13, 70
                        )
                        self.gui_components["audio_visualizer"].itemconfig(
                            bars[i], fill=color, outline=color
                        )

        except Exception as e:
            logger.error(f" Audio visualization update failed: {e}")

    def log_message(self, message: str) -> None:
        """Add message to activity log."""
        try:
            if "log_text" in self.gui_components:
                timestamp = tk.time.strftime("%H:%M:%S")
                log_entry = f"[{timestamp}] {message}\n"

                self.gui_components["log_text"].insert("end", log_entry)
                self.gui_components["log_text"].see("end")

        except Exception as e:
            logger.error(f" Log message failed: {e}")

    def log_conversation(self, user_msg: str, ai_response: str) -> None:
        """Add conversation to conversation log."""
        try:
            if "conv_text" in self.gui_components:
                timestamp = tk.time.strftime("%H:%M:%S")
                conv_entry = (
                    f"[{timestamp}] : {user_msg}\n[{timestamp}] : {ai_response}\n\n"
                )

                self.gui_components["conv_text"].insert("end", conv_entry)
                self.gui_components["conv_text"].see("end")

        except Exception as e:
            logger.error(f" Log conversation failed: {e}")

    def show_message(self, title: str, message: str, msg_type: str = "info") -> None:
        """Show message dialog."""
        try:
            if msg_type == "error":
                messagebox.showerror(title, message)
            elif msg_type == "warning":
                messagebox.showwarning(title, message)
            else:
                messagebox.showinfo(title, message)
        except Exception as e:
            logger.error(f" Show message failed: {e}")

    def run_gui(self) -> None:
        """Run the GUI main loop."""
        try:
            if self.root:
                self.root.mainloop()
        except Exception as e:
            logger.error(f" GUI run failed: {e}")

    def destroy_gui(self) -> None:
        """Destroy the GUI."""
        try:
            if self.root:
                self.root.destroy()
                self.root = None
                logger.info(" GUI destroyed")
        except Exception as e:
            logger.error(f" GUI destroy failed: {e}")

    def _create_header(self) -> None:
        """Create the header section."""
        header = tk.Frame(self.root, bg="#34495e", height=80)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text=" AI Teddy Bear - ESP32 Simulator",
            font=("Arial", 18, "bold"),
            fg="white",
            bg="#34495e",
        ).pack(pady=25)

    def _create_status_panel(self) -> None:
        """Create device status panel."""
        status_frame = tk.LabelFrame(
            self.root, text="Device Status", bg="#ecf0f1", font=("Arial", 12, "bold")
        )
        status_frame.pack(fill="x", padx=15, pady=10)

        # LED Status with Audio Visualizer
        led_frame = tk.Frame(status_frame, bg="#ecf0f1")
        led_frame.pack(pady=10)

        # LED Canvas
        led_canvas = tk.Canvas(
            led_frame, width=80, height=80, bg="#ecf0f1", highlightthickness=0
        )
        led_canvas.pack(side="left", padx=20)
        led_circle = led_canvas.create_oval(
            15, 15, 65, 65, fill="red", outline="white", width=3
        )

        self.gui_components["led_canvas"] = led_canvas
        self.gui_components["led_circle"] = led_circle

        # Audio Visualizer
        audio_visualizer = tk.Canvas(
            led_frame, width=200, height=80, bg="#2c3e50", highlightthickness=0
        )
        audio_visualizer.pack(side="left", padx=20)

        visualizer_bars = []
        for i in range(20):
            x = i * 10 + 5
            bar = audio_visualizer.create_rectangle(
                x, 70, x + 8, 70, fill="#3498db", outline="#3498db"
            )
            visualizer_bars.append(bar)

        self.gui_components["audio_visualizer"] = audio_visualizer
        self.gui_components["visualizer_bars"] = visualizer_bars

        # Status Info
        info_frame = tk.Frame(led_frame, bg="#ecf0f1")
        info_frame.pack(side="left", fill="both", expand=True)

        tk.Label(
            info_frame,
            text=f"Device: {self.device_id}",
            bg="#ecf0f1",
            font=("Arial", 10),
        ).pack(anchor="w")
        tk.Label(
            info_frame,
            text="Server: http://127.0.0.1:8000",
            bg="#ecf0f1",
            font=("Arial", 10),
        ).pack(anchor="w")

        status_label = tk.Label(
            info_frame,
            text=" POWERED OFF",
            bg="#ecf0f1",
            font=("Arial", 12, "bold"),
            fg="red",
        )
        status_label.pack(anchor="w", pady=5)

        wifi_label = tk.Label(
            info_frame, text=" WiFi: Disconnected", bg="#ecf0f1", font=("Arial", 10)
        )
        wifi_label.pack(anchor="w")

        server_status_label = tk.Label(
            info_frame,
            text=" Server: Disconnected",
            bg="#ecf0f1",
            font=("Arial", 10),
            fg="red",
        )
        server_status_label.pack(anchor="w")

        volume_label = tk.Label(
            info_frame, text=" Volume: 50%", bg="#ecf0f1", font=("Arial", 10)
        )
        volume_label.pack(anchor="w")

        self.gui_components["status_label"] = status_label
        self.gui_components["wifi_label"] = wifi_label
        self.gui_components["server_status_label"] = server_status_label
        self.gui_components["volume_label"] = volume_label

    def _create_control_panel(self) -> None:
        """Create control panel."""
        control_frame = tk.LabelFrame(
            self.root, text="Main Controls", bg="#ecf0f1", font=("Arial", 12, "bold")
        )
        control_frame.pack(fill="x", padx=15, pady=10)

        buttons_frame = tk.Frame(control_frame, bg="#ecf0f1")
        buttons_frame.pack(pady=15)

        # Power Button
        power_button = tk.Button(
            buttons_frame,
            text=" POWER ON",
            font=("Arial", 14, "bold"),
            bg="#27ae60",
            fg="white",
            width=15,
            height=2,
            command=self._on_power_button,
        )
        power_button.pack(side="left", padx=10)

        self.gui_components["power_button"] = power_button

    def _create_child_panel(self) -> None:
        """Create child profile panel."""
        child_frame = tk.LabelFrame(
            self.root, text="Child Profile", bg="#ecf0f1", font=("Arial", 12, "bold")
        )
        child_frame.pack(fill="x", padx=15, pady=10)

        profile_frame = tk.Frame(child_frame, bg="#ecf0f1")
        profile_frame.pack(pady=10)

        # Child Info
        tk.Label(profile_frame, text="Name:", bg="#ecf0f1").grid(
            row=0, column=0, sticky="w", padx=5
        )
        child_name = tk.Entry(profile_frame, width=20)
        child_name.grid(row=0, column=1, padx=5)

        tk.Label(profile_frame, text="Age:", bg="#ecf0f1").grid(
            row=0, column=2, sticky="w", padx=5
        )
        child_age = tk.Spinbox(profile_frame, from_=2, to=12, width=5)
        child_age.grid(row=0, column=3, padx=5)

        save_button = tk.Button(
            profile_frame,
            text=" Save Profile",
            command=self._on_save_profile,
            bg="#9b59b6",
            fg="white",
        )
        save_button.grid(row=0, column=4, padx=10)

        self.gui_components["child_name"] = child_name
        self.gui_components["child_age"] = child_age

    def _create_activity_panel(self) -> None:
        """Create activity monitoring panel."""
        activity_frame = tk.LabelFrame(
            self.root, text="Activity Monitor", bg="#ecf0f1", font=("Arial", 12, "bold")
        )
        activity_frame.pack(fill="both", expand=True, padx=15, pady=10)

        # Tabs
        notebook = ttk.Notebook(activity_frame)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Activity Log Tab
        log_frame = tk.Frame(notebook, bg="#ffffff")
        notebook.add(log_frame, text=" Activity Log")

        log_text = tk.Text(log_frame, height=8, font=("Arial", 9))
        log_scrollbar = tk.Scrollbar(
            log_frame, orient="vertical", command=log_text.yview
        )
        log_text.configure(yscrollcommand=log_scrollbar.set)
        log_text.pack(side="left", fill="both", expand=True)
        log_scrollbar.pack(side="right", fill="y")

        # Conversations Tab
        conv_frame = tk.Frame(notebook, bg="#ffffff")
        notebook.add(conv_frame, text=" Conversations")

        conv_text = tk.Text(conv_frame, height=8, font=("Arial", 9))
        conv_scrollbar = tk.Scrollbar(
            conv_frame, orient="vertical", command=conv_text.yview
        )
        conv_text.configure(yscrollcommand=conv_scrollbar.set)
        conv_text.pack(side="left", fill="both", expand=True)
        conv_scrollbar.pack(side="right", fill="y")

        self.gui_components["log_text"] = log_text
        self.gui_components["conv_text"] = conv_text

    def _create_features_panel(self) -> None:
        """Create features panel."""
        features_frame = tk.LabelFrame(
            self.root,
            text="Advanced Features",
            bg="#ecf0f1",
            font=("Arial", 12, "bold"),
        )
        features_frame.pack(fill="x", padx=15, pady=10)

        features_grid = tk.Frame(features_frame, bg="#ecf0f1")
        features_grid.pack(pady=10)

        # Feature buttons
        test_buttons = [
            (" Games", self._test_games),
            (" Stories", self._test_stories),
            (" Songs", self._test_songs),
            (" Learning", self._test_learning),
        ]

        for i, (text, command) in enumerate(test_buttons):
            btn = tk.Button(
                features_grid,
                text=text,
                command=command,
                bg="#3498db",
                fg="white",
                width=12,
            )
            btn.grid(row=0, column=i, padx=5, pady=5)

    def _on_power_button(self) -> None:
        """Handle power button click."""
        if "power_button_callback" in self.update_callbacks:
            self.update_callbacks["power_button_callback"]()

    def _on_save_profile(self) -> None:
        """Handle save profile button click."""
        if "save_profile_callback" in self.update_callbacks:
            name = self.gui_components["child_name"].get()
            age = self.gui_components["child_age"].get()
            self.update_callbacks["save_profile_callback"](name, age)

    def _test_games(self) -> None:
        """Test games functionality."""
        self.show_message("Games", " Games feature activated!")

    def _test_stories(self) -> None:
        """Test stories functionality."""
        self.show_message("Stories", " Stories feature activated!")

    def _test_songs(self) -> None:
        """Test songs functionality."""
        self.show_message("Songs", " Songs feature activated!")

    def _test_learning(self) -> None:
        """Test learning functionality."""
        self.show_message("Learning", " Learning feature activated!")

    def _on_closing(self) -> None:
        """Handle window closing."""
        if "closing_callback" in self.update_callbacks:
            self.update_callbacks["closing_callback"]()
        else:
            self.destroy_gui()
