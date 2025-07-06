import random
from datetime import datetime
from typing import Dict

import structlog
from PySide6.QtCore import QTimer
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel

try:
    from PySide6.QtWebEngineWidgets import QWebEngineView

    WEBENGINE_AVAILABLE = True
except ImportError:
    WEBENGINE_AVAILABLE = False


logger = structlog.get_logger()


def setup_timers(widget) -> None:
    """Setup update timers"""
    # Real-time updates every 3 seconds
    widget.realtime_timer = QTimer()
    widget.realtime_timer.timeout.connect(
        lambda: update_realtime_metrics(widget))
    widget.realtime_timer.start(3000)

    # Charts update every 15 seconds
    widget.charts_timer = QTimer()
    widget.charts_timer.timeout.connect(lambda: update_charts(widget))
    widget.charts_timer.start(15000)

    # Alerts processing every 10 seconds
    widget.alerts_timer = QTimer()
    widget.alerts_timer.timeout.connect(lambda: process_alerts(widget))
    widget.alerts_timer.start(10000)


def update_realtime_metrics(widget) -> None:
    """Update real-time metrics"""
    try:
        # Simulate real-time data
        active_children = random.randint(0, 12)
        interactions_today = random.randint(25, 150)

        widget.active_children_label.setText(str(active_children))
        widget.interactions_today_label.setText(str(interactions_today))

        # Simulate emotion updates (30% chance)
        if random.random() > 0.7:
            emotions = [
                "happy",
                "excited",
                "calm",
                "curious",
                "frustrated",
                "sad"]
            emotion = random.choice(emotions)
            confidence = random.uniform(0.6, 0.95)

            add_emotion_data(widget, emotion, confidence)

    except Exception as e:
        logger.error("Failed to update real-time metrics", error=str(e))


def add_emotion_data(widget, emotion: str, confidence: float, metadata: dict = None) -> None:
    """Add new emotion data and update displays"""
    # Add to analytics engine
    widget.emotion_engine.add_emotion_data(
        emotion=emotion, confidence=confidence, metadata=metadata
    )

    # Update current emotion display
    update_current_emotion_display(widget, emotion, confidence)

    # Emit signal
    widget.emotion_detected.emit(
        [{"emotion": emotion, "confidence": confidence}], confidence
    )

    logger.info(
        "Emotion data added",
        emotion=emotion,
        confidence=confidence)


def update_current_emotion_display(widget, emotion: str, confidence: float) -> None:
    """Update current emotion display"""
    emotion_emojis = {
        "happy": "😊",
        "excited": "🤩",
        "calm": "😌",
        "curious": "🤔",
        "frustrated": "😤",
        "sad": "😢",
        "angry": "😠",
        "surprised": "😲",
        "neutral": "😐",
    }

    emoji = emotion_emojis.get(emotion, "😐")
    widget.current_emotion_label.setText(f"{emoji} {emotion.title()}")
    widget.emotion_confidence_bar.setValue(int(confidence * 100))

    # Update background color
    emotion_colors = {
        "happy": "#e8f5e8",
        "excited": "#fff3e0",
        "calm": "#e3f2fd",
        "curious": "#f3e5f5",
        "frustrated": "#ffebee",
        "sad": "#f1f8e9",
        "angry": "#fce4ec",
        "surprised": "#fff8e1",
        "neutral": "#f5f5f5",
    }

    bg_color = emotion_colors.get(emotion, "#f0f0f0")
    widget.current_emotion_label.setStyleSheet(
        f"""
        QLabel {{
            font-size: 24px;
            font-weight: bold;
            background-color: {bg_color};
            border: 2px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            margin: 5px;
        }}
    """
    )


def update_charts(widget) -> None:
    """Update all emotion charts"""
    if not widget.emotion_engine.plotly_available:
        return

    try:
        # Clear existing charts
        for i in reversed(range(widget.emotion_charts_layout.count())):
            child = widget.emotion_charts_layout.itemAt(i).widget()
            if child:
                child.setParent(None)

        # Get time range
        time_range_text = widget.time_range_combo.currentText()
        hours_map = {
            "Last Hour": 1,
            "Last 6 Hours": 6,
            "Last 24 Hours": 24,
            "Last Week": 168,
        }
        hours = hours_map.get(time_range_text, 6)

        # Create timeline chart
        timeline_fig = widget.emotion_engine.create_emotion_timeline_chart(
            hours)
        if timeline_fig:
            display_plotly_chart(widget, timeline_fig, "timeline")

        # Create distribution chart
        distribution_fig = widget.emotion_engine.create_emotion_distribution_chart()
        if distribution_fig:
            display_plotly_chart(widget, distribution_fig, "distribution")

        # Create heatmap
        heatmap_fig = widget.emotion_engine.create_emotion_heatmap()
        if heatmap_fig:
            display_plotly_chart(widget, heatmap_fig, "heatmap")

    except Exception as e:
        logger.error("Failed to update charts", error=str(e))


def display_plotly_chart(widget, fig, chart_type: str) -> None:
    """Display Plotly chart in widget"""
    try:
        if WEBENGINE_AVAILABLE:
            # Use QWebEngineView for interactive charts
            html_str = fig.to_html(
                include_plotlyjs="cdn", div_id=f"chart_{chart_type}"
            )

            web_view = QWebEngineView()
            web_view.setHtml(html_str)
            web_view.setMinimumHeight(400)

            widget.emotion_charts_layout.addWidget(web_view)

        else:
            # Fallback: save as image and display
            import os
            import tempfile

            temp_file = tempfile.NamedTemporaryFile(
                suffix=".png", delete=False)
            fig.write_image(temp_file.name, width=800, height=400)

            pixmap = QPixmap(temp_file.name)
            label = QLabel()
            label.setPixmap(pixmap)
            label.setAlignment(widget.Qt.AlignCenter)

            widget.emotion_charts_layout.addWidget(label)

            # Clean up temp file
            os.unlink(temp_file.name)

    except Exception as e:
        logger.error(
            "Failed to display chart",
            error=str(e),
            chart_type=chart_type)

        # Show error message
        error_label = QLabel(f"Chart display error: {e}")
        error_label.setAlignment(widget.Qt.AlignCenter)
        error_label.setStyleSheet("QLabel { color: red; }")
        widget.emotion_charts_layout.addWidget(error_label)


def process_alerts(widget) -> None:
    """Process smart alerts"""
    if not widget.alert_system.enabled:
        return

    try:
        # Get new alerts
        new_alerts = widget.alert_system.process_emotion_data(
            widget.emotion_engine.emotion_history
        )

        # Display new alerts
        for alert in new_alerts:
            display_alert(widget, alert)

    except Exception as e:
        logger.error("Failed to process alerts", error=str(e))


def display_alert(widget, alert: Dict) -> None:
    """Display alert in the alerts panel"""
    timestamp = alert["timestamp"].strftime("%H:%M:%S")
    priority_colors = {
        "high": "#ff4444",
        "medium": "#ff8800",
        "low": "#4488ff"}

    color = priority_colors.get(alert["priority"], "#666666")

    alert_html = f"""
    <div style="border-left: 4px solid {color}; padding: 8px; margin: 4px 0; background-color: #f9f9f9;">
        <strong>{alert['emoji']} {alert['message']}</strong><br/>
        <small style="color: #666;">{timestamp} - {alert['priority'].upper()} priority</small>
    </div>
    """

    current_html = widget.alerts_display.toHtml()
    widget.alerts_display.setHtml(alert_html + current_html)

    # Emit signal for parent handling
    widget.alert_triggered.emit(
        alert["type"],
        alert["message"],
        alert["data"])


def toggle_alerts(widget, enabled: bool) -> None:
    """Toggle smart alerts system"""
    widget.alert_system.enabled = enabled

    if enabled:
        widget.alerts_timer.start(10000)
        logger.info("Smart alerts enabled")
    else:
        widget.alerts_timer.stop()
        logger.info("Smart alerts disabled")


def update_alert_sensitivity(widget, value: int) -> None:
    """Update alert sensitivity"""
    sensitivity = value / 5.0  # Convert 1-10 scale to 0.2-2.0
    widget.alert_system.set_sensitivity(sensitivity)


def refresh_all_charts(widget) -> None:
    """Manually refresh all charts"""
    update_charts(widget)
    logger.info("Charts refreshed manually")


def update_connection_status(widget, status: str) -> None:
    """Update connection status indicator"""
    status_config = {
        "Connected": {"color": "green", "symbol": "●"},
        "Connecting...": {"color": "orange", "symbol": "◐"},
        "Disconnected": {"color": "red", "symbol": "●"},
        "Error": {"color": "red", "symbol": "✖"},
    }

    config = status_config.get(status, {"color": "gray", "symbol": "●"})

    widget.connection_indicator.setText(f"{config['symbol']} {status}")
    widget.connection_indicator.setStyleSheet(
        f"QLabel {{ color: {config['color']}; font-weight: bold; }}"
    )


def add_child_profile(widget, name: str, age: int, metadata: dict = None) -> None:
    """Add child profile to dashboard"""
    profile_text = f"{name} (Age: {age})"
    widget.profiles_list.addItem(profile_text)

    widget.child_profiles.append(
        {
            "name": name,
            "age": age,
            "metadata": metadata or {},
            "added_time": datetime.now(),
        }
    )

    logger.info("Child profile added", name=name, age=age)
