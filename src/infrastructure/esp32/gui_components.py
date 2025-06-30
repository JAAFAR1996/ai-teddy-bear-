"""GUI components for ESP32 teddy bear simulator."""

import structlog
from typing import Dict, Any, Optional, Callable
import tkinter as tk
from tkinter import ttk

logger = structlog.get_logger(__name__)


class GUIComponents:
    """Pre-built GUI components for ESP32 simulator."""
    
    def __init__(self):
        self.components = {}
        self.callbacks = {}
        
        logger.info(" GUI components library initialized")
    
    def create_status_led(self, parent: tk.Widget, size: int = 80) -> Dict[str, Any]:
        """Create status LED component."""
        try:
            canvas = tk.Canvas(parent, width=size, height=size, bg='#ecf0f1', highlightthickness=0)
            circle = canvas.create_oval(
                size//4, size//4, 3*size//4, 3*size//4, 
                fill='red', outline='white', width=3
            )
            
            component = {
                'canvas': canvas,
                'circle': circle,
                'current_color': 'red'
            }
            
            # Add control methods
            def set_color(color: str):
                canvas.itemconfig(circle, fill=color)
                component['current_color'] = color
            
            def get_color() -> str:
                return component['current_color']
            
            component['set_color'] = set_color
            component['get_color'] = get_color
            
            return component
            
        except Exception as e:
            logger.error(f" Status LED creation failed: {e}")
            return {}
    
    def create_audio_visualizer(self, parent: tk.Widget, width: int = 200, height: int = 80, bars: int = 20) -> Dict[str, Any]:
        """Create audio visualizer component."""
        try:
            canvas = tk.Canvas(parent, width=width, height=height, bg='#2c3e50', highlightthickness=0)
            
            bar_width = width // bars
            visualizer_bars = []
            
            for i in range(bars):
                x = i * bar_width + 2
                bar = canvas.create_rectangle(
                    x, height-2, x+bar_width-4, height-2, 
                    fill='#3498db', outline='#3498db'
                )
                visualizer_bars.append(bar)
            
            component = {
                'canvas': canvas,
                'bars': visualizer_bars,
                'bar_count': bars,
                'width': width,
                'height': height,
                'is_active': False
            }
            
            def update_bars(heights: list, colors: list = None):
                if len(heights) != len(visualizer_bars):
                    return
                
                if colors is None:
                    colors = ['#3498db'] * len(heights)
                
                for i, (height, color) in enumerate(zip(heights, colors)):
                    bar = visualizer_bars[i]
                    x = i * bar_width + 2
                    y_top = max(2, height - height)
                    
                    canvas.coords(bar, x, y_top, x+bar_width-4, height-2)
                    canvas.itemconfig(bar, fill=color, outline=color)
            
            def reset_bars():
                for i, bar in enumerate(visualizer_bars):
                    x = i * bar_width + 2
                    canvas.coords(bar, x, height-2, x+bar_width-4, height-2)
                    canvas.itemconfig(bar, fill='#3498db', outline='#3498db')
            
            component['update_bars'] = update_bars
            component['reset_bars'] = reset_bars
            
            return component
            
        except Exception as e:
            logger.error(f" Audio visualizer creation failed: {e}")
            return {}
    
    def create_control_button(
        self, 
        parent: tk.Widget, 
        text: str, 
        command: Callable,
        bg_color: str = '#3498db',
        fg_color: str = 'white',
        width: int = 12,
        height: int = 1
    ) -> tk.Button:
        """Create styled control button."""
        try:
            button = tk.Button(
                parent,
                text=text,
                command=command,
                bg=bg_color,
                fg=fg_color,
                width=width,
                height=height,
                font=('Arial', 10, 'bold'),
                relief='raised',
                borderwidth=2
            )
            
            # Add hover effects
            def on_enter(event):
                button.config(bg=self._darken_color(bg_color))
            
            def on_leave(event):
                button.config(bg=bg_color)
            
            button.bind("<Enter>", on_enter)
            button.bind("<Leave>", on_leave)
            
            return button
            
        except Exception as e:
            logger.error(f" Control button creation failed: {e}")
            return tk.Button(parent, text=text, command=command)
    
    def create_status_panel(self, parent: tk.Widget, title: str = "Status") -> Dict[str, Any]:
        """Create status information panel."""
        try:
            frame = tk.LabelFrame(parent, text=title, bg='#ecf0f1', font=('Arial', 12, 'bold'))
            
            status_labels = {}
            
            def add_status_item(key: str, label: str, initial_value: str = "Unknown"):
                row = len(status_labels)
                
                tk.Label(
                    frame, 
                    text=f"{label}:", 
                    bg='#ecf0f1', 
                    font=('Arial', 10)
                ).grid(row=row, column=0, sticky="w", padx=5, pady=2)
                
                value_label = tk.Label(
                    frame, 
                    text=initial_value, 
                    bg='#ecf0f1', 
                    font=('Arial', 10, 'bold')
                )
                value_label.grid(row=row, column=1, sticky="w", padx=10, pady=2)
                
                status_labels[key] = value_label
            
            def update_status(key: str, value: str, color: str = 'black'):
                if key in status_labels:
                    status_labels[key].config(text=value, fg=color)
            
            def get_status(key: str) -> str:
                if key in status_labels:
                    return status_labels[key]['text']
                return ""
            
            component = {
                'frame': frame,
                'labels': status_labels,
                'add_status_item': add_status_item,
                'update_status': update_status,
                'get_status': get_status
            }
            
            return component
            
        except Exception as e:
            logger.error(f" Status panel creation failed: {e}")
            return {}
    
    def create_log_panel(self, parent: tk.Widget, title: str = "Activity Log", height: int = 8) -> Dict[str, Any]:
        """Create scrollable log panel."""
        try:
            frame = tk.LabelFrame(parent, text=title, bg='#ecf0f1', font=('Arial', 12, 'bold'))
            
            # Text widget with scrollbar
            text_widget = tk.Text(frame, height=height, font=('Arial', 9), wrap=tk.WORD)
            scrollbar = tk.Scrollbar(frame, orient="vertical", command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            text_widget.pack(side="left", fill="both", expand=True, padx=5, pady=5)
            scrollbar.pack(side="right", fill="y", pady=5)
            
            def add_log_entry(message: str, timestamp: bool = True):
                if timestamp:
                    import time
                    time_str = time.strftime("%H:%M:%S")
                    entry = f"[{time_str}] {message}\n"
                else:
                    entry = f"{message}\n"
                
                text_widget.insert("end", entry)
                text_widget.see("end")
            
            def clear_log():
                text_widget.delete(1.0, "end")
            
            def get_log_content() -> str:
                return text_widget.get(1.0, "end")
            
            component = {
                'frame': frame,
                'text_widget': text_widget,
                'scrollbar': scrollbar,
                'add_log_entry': add_log_entry,
                'clear_log': clear_log,
                'get_log_content': get_log_content
            }
            
            return component
            
        except Exception as e:
            logger.error(f" Log panel creation failed: {e}")
            return {}
    
    def create_progress_bar(self, parent: tk.Widget, length: int = 200) -> Dict[str, Any]:
        """Create progress bar component."""
        try:
            progress = ttk.Progressbar(parent, length=length, mode='determinate')
            
            def set_value(value: float):
                progress['value'] = max(0, min(100, value))
            
            def get_value() -> float:
                return progress['value']
            
            def set_indeterminate():
                progress.config(mode='indeterminate')
                progress.start()
            
            def set_determinate():
                progress.stop()
                progress.config(mode='determinate')
            
            component = {
                'progress': progress,
                'set_value': set_value,
                'get_value': get_value,
                'set_indeterminate': set_indeterminate,
                'set_determinate': set_determinate
            }
            
            return component
            
        except Exception as e:
            logger.error(f" Progress bar creation failed: {e}")
            return {}
    
    def create_input_form(self, parent: tk.Widget, fields: Dict[str, str]) -> Dict[str, Any]:
        """Create input form with multiple fields."""
        try:
            frame = tk.Frame(parent, bg='#ecf0f1')
            
            entries = {}
            
            for i, (field_key, field_label) in enumerate(fields.items()):
                tk.Label(
                    frame, 
                    text=f"{field_label}:", 
                    bg='#ecf0f1'
                ).grid(row=i, column=0, sticky="w", padx=5, pady=2)
                
                entry = tk.Entry(frame, width=20)
                entry.grid(row=i, column=1, padx=5, pady=2)
                
                entries[field_key] = entry
            
            def get_values() -> Dict[str, str]:
                return {key: entry.get() for key, entry in entries.items()}
            
            def set_values(values: Dict[str, str]):
                for key, value in values.items():
                    if key in entries:
                        entries[key].delete(0, "end")
                        entries[key].insert(0, value)
            
            def clear_values():
                for entry in entries.values():
                    entry.delete(0, "end")
            
            component = {
                'frame': frame,
                'entries': entries,
                'get_values': get_values,
                'set_values': set_values,
                'clear_values': clear_values
            }
            
            return component
            
        except Exception as e:
            logger.error(f" Input form creation failed: {e}")
            return {}
    
    def create_tabbed_panel(self, parent: tk.Widget, tabs: Dict[str, str]) -> Dict[str, Any]:
        """Create tabbed panel."""
        try:
            notebook = ttk.Notebook(parent)
            
            tab_frames = {}
            
            for tab_key, tab_title in tabs.items():
                frame = tk.Frame(notebook, bg='#ffffff')
                notebook.add(frame, text=tab_title)
                tab_frames[tab_key] = frame
            
            def get_tab_frame(tab_key: str) -> Optional[tk.Frame]:
                return tab_frames.get(tab_key)
            
            def select_tab(tab_key: str):
                if tab_key in tab_frames:
                    frame = tab_frames[tab_key]
                    notebook.select(frame)
            
            component = {
                'notebook': notebook,
                'tab_frames': tab_frames,
                'get_tab_frame': get_tab_frame,
                'select_tab': select_tab
            }
            
            return component
            
        except Exception as e:
            logger.error(f" Tabbed panel creation failed: {e}")
            return {}
    
    def _darken_color(self, color: str) -> str:
        """Darken a color for hover effects."""
        # Simple color darkening - in production would use proper color manipulation
        color_map = {
            '#3498db': '#2980b9',
            '#27ae60': '#229954',
            '#e74c3c': '#c0392b',
            '#f39c12': '#e67e22',
            '#9b59b6': '#8e44ad',
            '#16a085': '#148f77'
        }
        
        return color_map.get(color, color)
    
    def apply_theme(self, parent: tk.Widget, theme: str = "default"):
        """Apply color theme to components."""
        try:
            themes = {
                "default": {
                    "bg": "#ecf0f1",
                    "fg": "#2c3e50",
                    "accent": "#3498db"
                },
                "dark": {
                    "bg": "#2c3e50",
                    "fg": "#ecf0f1", 
                    "accent": "#e74c3c"
                },
                "child_friendly": {
                    "bg": "#fff5f5",
                    "fg": "#333333",
                    "accent": "#ff6b9d"
                }
            }
            
            if theme in themes:
                theme_colors = themes[theme]
                parent.configure(bg=theme_colors["bg"])
                
                # Apply to all child widgets recursively
                self._apply_theme_recursive(parent, theme_colors)
                
                logger.info(f" Applied theme: {theme}")
            
        except Exception as e:
            logger.error(f" Theme application failed: {e}")
    
    def _apply_theme_recursive(self, widget: tk.Widget, colors: Dict[str, str]):
        """Apply theme colors recursively to all child widgets."""
        try:
            # Apply to current widget if it supports the properties
            try:
                widget.configure(bg=colors["bg"])
            except:
                pass
            
            try:
                widget.configure(fg=colors["fg"])
            except:
                pass
            
            # Apply to children
            for child in widget.winfo_children():
                self._apply_theme_recursive(child, colors)
                
        except Exception as e:
            logger.debug(f"Theme application skipped for widget: {e}")
