"""
Modern UI Module - PySide6 Implementation
Enterprise-grade UI for AI Teddy Bear
"""

from .dialogs import AboutDialog, ConfigurationDialog
from .modern_ui import ModernTeddyUI, TeddyMainWindow
from .widgets import AudioWidget, HealthWidget, SettingsWidget

__all__ = [
    "ModernTeddyUI",
    "TeddyMainWindow",
    "AudioWidget",
    "SettingsWidget",
    "HealthWidget",
    "ConfigurationDialog",
    "AboutDialog",
]
