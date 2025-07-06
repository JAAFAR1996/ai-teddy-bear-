"""
Components for the Enterprise Dashboard.
"""

from .emotion_analytics import EmotionAnalyticsEngine
from .handlers import (add_child_profile, add_emotion_data, display_alert,
                       display_plotly_chart, process_alerts,
                       refresh_all_charts, setup_timers, toggle_alerts,
                       update_alert_sensitivity, update_charts,
                       update_connection_status,
                       update_current_emotion_display,
                       update_realtime_metrics)
from .smart_alerts import SmartAlertSystem
from .ui_setup import create_charts_panel, create_metrics_panel, setup_ui

__all__ = [
    "EmotionAnalyticsEngine",
    "SmartAlertSystem",
    "setup_ui",
    "create_metrics_panel",
    "create_charts_panel",
    "setup_timers",
    "update_realtime_metrics",
    "add_emotion_data",
    "update_current_emotion_display",
    "update_charts",
    "display_plotly_chart",
    "process_alerts",
    "display_alert",
    "toggle_alerts",
    "update_alert_sensitivity",
    "refresh_all_charts",
    "update_connection_status",
    "add_child_profile",
]
