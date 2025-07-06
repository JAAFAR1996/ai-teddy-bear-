from .enterprise_components import (
    EmotionAnalyticsEngine,
    SmartAlertSystem,
    add_child_profile,
    add_emotion_data,
    process_alerts,
    refresh_all_charts,
    setup_timers,
    setup_ui,
    toggle_alerts,
    update_alert_sensitivity,
    update_charts,
    update_connection_status,
)
from typing import Any, Dict, List

#!/usr/bin/env python3
"""
Enterprise Dashboard with Advanced Analytics and Live Emotion Tracking
Features:
- Real-time emotion visualization with Plotly
- Smart parental alerts system
- Interactive charts and analytics
- Mobile-responsive design
- Live data updates via WebSocket
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List

import numpy as np
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QProgressBar,
    QPushButton,
    QSlider,
    QSplitter,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

import structlog

logger = structlog.get_logger()

try:
    from PySide6.QtWebEngineWidgets import QWebEngineView

    WEBENGINE_AVAILABLE = True
except ImportError:
    WEBENGINE_AVAILABLE = False
    logger.warning(
        "⚠️ QWebEngineView not available - using fallback chart display")


class EnterpriseDashboardWidget(QWidget):
    """Enterprise dashboard with advanced real-time analytics and emotion tracking"""

    # Signals for parent communication
    alert_triggered = Signal(str, str, dict)  # alert_type, message, data
    emotion_detected = Signal(list, float)  # emotions, confidence
    analytics_updated = Signal(dict)  # analytics_data

    def __init__(self, parent=None):
        super().__init__(parent)

        # Initialize analytics engines
        self.emotion_engine = EmotionAnalyticsEngine()
        self.alert_system = SmartAlertSystem()

        # Data stores
        self.performance_data = []
        self.session_analytics = {}
        self.child_profiles = []

        # Setup UI and systems
        setup_ui(self)
        setup_timers(self)

        logger.info("Enterprise dashboard initialized with advanced analytics")

    def add_emotion_data(
        self, emotion: str, confidence: float, metadata: dict = None
    ) -> None:
        add_emotion_data(self, emotion, confidence, metadata)

    def update_charts(self) -> None:
        update_charts(self)

    def process_alerts(self) -> None:
        process_alerts(self)

    def toggle_alerts(self, enabled: bool) -> None:
        toggle_alerts(self, enabled)

    def update_alert_sensitivity(self, value: int) -> None:
        update_alert_sensitivity(self, value)

    def refresh_all_charts(self) -> None:
        refresh_all_charts(self)

    def update_connection_status(self, status: str) -> None:
        update_connection_status(self, status)

    def add_child_profile(
            self,
            name: str,
            age: int,
            metadata: dict = None) -> None:
        add_child_profile(self, name, age, metadata)

    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get comprehensive analytics summary"""
        insights = self.emotion_engine.get_emotion_insights()
        recent_alerts = self.alert_system.get_recent_alerts(24)

        return {
            "emotion_insights": insights,
            "alerts_today": len(recent_alerts),
            "active_children": len(self.child_profiles),
            "total_interactions": len(self.emotion_engine.emotion_history),
            "dashboard_status": "active",
        }


# Backward compatibility alias
ModernDashboardWidget = EnterpriseDashboardWidget
