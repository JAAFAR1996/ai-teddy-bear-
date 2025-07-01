from typing import Any, Dict, List, Optional

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

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import numpy as np
from PySide6.QtCore import QObject, Qt, QTimer, Signal
from PySide6.QtGui import QPainter, QPixmap
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

try:
    from PySide6.QtWebEngineWidgets import QWebEngineView

    WEBENGINE_AVAILABLE = True
except ImportError:
    WEBENGINE_AVAILABLE = False
    logger.warning("⚠️ QWebEngineView not available - using fallback chart display")

import structlog

logger = structlog.get_logger()


class EmotionAnalyticsEngine:
    """Advanced emotion analytics with machine learning insights"""

    def __init__(self):
        self.emotion_history = []
        self.patterns = {}
        self.predictions = {}
        self.setup_plotly()

    def setup_plotly(self) -> Any:
        """Setup Plotly for advanced visualization"""
        try:
            import plotly.express as px
            import plotly.figure_factory as ff
            import plotly.graph_objects as go

            self.plotly_available = True
            self.go = go
            self.px = px
            self.ff = ff

            logger.info("Plotly analytics engine initialized successfully")

        except ImportError:
            self.plotly_available = False
            logger.warning("Plotly not available - install with: pip install plotly")

    def add_emotion_data(dict=None) -> None:
        """Add new emotion data point"""
        entry = {"emotion": emotion, "confidence": confidence, "timestamp": datetime.now(), "metadata": metadata or {}}

        self.emotion_history.append(entry)

        # Keep only last 1000 entries for performance
        if len(self.emotion_history) > 1000:
            self.emotion_history.pop(0)

        # Trigger pattern analysis
        self.analyze_patterns()

    def analyze_patterns(self) -> Any:
        """Analyze emotion patterns for insights"""
        if len(self.emotion_history) < 10:
            return

        # Analyze emotion transitions
        transitions = {}
        for i in range(1, len(self.emotion_history)):
            prev_emotion = self.emotion_history[i - 1]["emotion"]
            curr_emotion = self.emotion_history[i]["emotion"]

            transition = f"{prev_emotion} -> {curr_emotion}"
            transitions[transition] = transitions.get(transition, 0) + 1

        self.patterns["transitions"] = transitions

        # Analyze time-based patterns
        hourly_emotions = {}
        for entry in self.emotion_history[-100:]:  # Last 100 entries
            hour = entry["timestamp"].hour
            emotion = entry["emotion"]

            if hour not in hourly_emotions:
                hourly_emotions[hour] = {}

            hourly_emotions[hour][emotion] = hourly_emotions[hour].get(emotion, 0) + 1

        self.patterns["hourly"] = hourly_emotions

    def create_emotion_timeline_chart(self, hours: int = 6) -> Any:
        """Create interactive emotion timeline chart"""
        if not self.plotly_available:
            return None

        # Filter data by time range
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_data = [entry for entry in self.emotion_history if entry["timestamp"] >= cutoff_time]

        if not recent_data:
            return None

        # Prepare data
        timestamps = [entry["timestamp"] for entry in recent_data]
        emotions = [entry["emotion"] for entry in recent_data]
        confidences = [entry["confidence"] for entry in recent_data]

        # Create interactive timeline
        fig = self.go.Figure()

        # Add emotion traces with different colors
        emotion_colors = {
            "happy": "#4CAF50",
            "excited": "#FF9800",
            "calm": "#2196F3",
            "curious": "#9C27B0",
            "frustrated": "#F44336",
            "sad": "#607D8B",
            "angry": "#E91E63",
            "surprised": "#FFEB3B",
            "neutral": "#9E9E9E",
        }

        unique_emotions = list(set(emotions))

        for emotion in unique_emotions:
            emotion_times = [timestamps[i] for i, e in enumerate(emotions) if e == emotion]
            emotion_conf = [confidences[i] for i, e in enumerate(emotions) if e == emotion]

            fig.add_trace(
                self.go.Scatter(
                    x=emotion_times,
                    y=emotion_conf,
                    mode="lines+markers",
                    name=emotion.title(),
                    line=dict(color=emotion_colors.get(emotion, "#666666"), width=3),
                    marker=dict(size=10, opacity=0.8),
                    hovertemplate=f"<b>{emotion.title()}</b><br>Confidence: %{{y:.1%}}<br>Time: %{{x}}<extra></extra>",
                )
            )

        fig.update_layout(
            title={
                "text": f"Emotion Timeline - Last {hours} Hours",
                "x": 0.5,
                "xanchor": "center",
                "font": {"size": 18},
            },
            xaxis_title="Time",
            yaxis_title="Confidence Level",
            yaxis=dict(tickformat=".0%"),
            hovermode="x unified",
            template="plotly_white",
            height=400,
            margin=dict(l=60, r=60, t=80, b=60),
        )

        return fig

    def create_emotion_distribution_chart(self) -> Any:
        """Create emotion distribution pie chart"""
        if not self.plotly_available or not self.emotion_history:
            return None

        # Count emotions in recent history
        recent_data = self.emotion_history[-50:]  # Last 50 entries
        emotion_counts = {}

        for entry in recent_data:
            emotion = entry["emotion"]
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

        if not emotion_counts:
            return None

        # Create donut chart
        fig = self.go.Figure(
            data=[
                self.go.Pie(
                    labels=list(emotion_counts.keys()),
                    values=list(emotion_counts.values()),
                    hole=0.4,
                    textinfo="label+percent",
                    textfont_size=14,
                    marker=dict(
                        colors=["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7", "#DDA0DD", "#98D8C8", "#F7DC6F"],
                        line=dict(color="#FFFFFF", width=2),
                    ),
                )
            ]
        )

        fig.update_layout(
            title={
                "text": "Emotion Distribution (Recent Activity)",
                "x": 0.5,
                "xanchor": "center",
                "font": {"size": 16},
            },
            template="plotly_white",
            height=350,
            margin=dict(l=60, r=60, t=80, b=60),
        )

        return fig

    def create_emotion_heatmap(self) -> Any:
        """Create emotion intensity heatmap by hour"""
        if not self.plotly_available or not self.emotion_history:
            return None

        # Prepare hourly emotion data
        hours = list(range(24))
        emotions = ["happy", "excited", "calm", "curious", "frustrated", "sad", "angry"]

        # Initialize matrix
        intensity_matrix = np.zeros((len(emotions), len(hours)))

        for entry in self.emotion_history[-200:]:  # Last 200 entries
            hour = entry["timestamp"].hour
            emotion = entry["emotion"]
            confidence = entry["confidence"]

            if emotion in emotions:
                emotion_idx = emotions.index(emotion)
                intensity_matrix[emotion_idx][hour] += confidence

        # Normalize by maximum value
        max_val = np.max(intensity_matrix) if np.max(intensity_matrix) > 0 else 1
        intensity_matrix = intensity_matrix / max_val

        fig = self.go.Figure(
            data=self.go.Heatmap(
                z=intensity_matrix,
                x=[f"{h:02d}:00" for h in hours],
                y=[e.title() for e in emotions],
                colorscale="Viridis",
                hoverongaps=False,
                hovertemplate="Hour: %{x}<br>Emotion: %{y}<br>Intensity: %{z:.2f}<extra></extra>",
            )
        )

        fig.update_layout(
            title={"text": "Emotion Intensity Heatmap by Hour", "x": 0.5, "xanchor": "center", "font": {"size": 16}},
            xaxis_title="Hour of Day",
            yaxis_title="Emotion Type",
            template="plotly_white",
            height=400,
            margin=dict(l=100, r=60, t=80, b=60),
        )

        return fig

    def get_emotion_insights(self) -> Dict[str, Any]:
        """Get AI-powered emotion insights"""
        if len(self.emotion_history) < 5:
            return {"status": "insufficient_data"}

        recent_emotions = self.emotion_history[-20:]

        # Calculate dominant emotion
        emotion_counts = {}
        for entry in recent_emotions:
            emotion = entry["emotion"]
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

        dominant_emotion = max(emotion_counts.items(), key=lambda x: x[1])

        # Calculate average confidence
        avg_confidence = sum(entry["confidence"] for entry in recent_emotions) / len(recent_emotions)

        # Detect trends
        trend = "stable"
        if len(recent_emotions) >= 10:
            first_half = recent_emotions[: len(recent_emotions) // 2]
            second_half = recent_emotions[len(recent_emotions) // 2 :]

            first_avg = sum(1 if e["emotion"] in ["happy", "excited", "calm"] else 0 for e in first_half) / len(
                first_half
            )
            second_avg = sum(1 if e["emotion"] in ["happy", "excited", "calm"] else 0 for e in second_half) / len(
                second_half
            )

            if second_avg > first_avg + 0.2:
                trend = "improving"
            elif second_avg < first_avg - 0.2:
                trend = "declining"

        return {
            "status": "ready",
            "dominant_emotion": dominant_emotion,
            "average_confidence": avg_confidence,
            "trend": trend,
            "total_interactions": len(self.emotion_history),
            "patterns_detected": len(self.patterns.get("transitions", {})),
        }


class SmartAlertSystem:
    """Intelligent alert system for parents"""

    def __init__(self):
        self.alert_rules = self.setup_alert_rules()
        self.alerts_history = []
        self.sensitivity = 1.0
        self.enabled = True

    def setup_alert_rules(self) -> Dict[str, Dict]:
        """Setup predefined alert rules"""
        return {
            "negative_emotion_streak": {
                "description": "Child showing persistent negative emotions",
                "threshold": 3,
                "timeframe": 300,  # 5 minutes
                "priority": "high",
                "emoji": "😟",
            },
            "sudden_mood_drop": {
                "description": "Sudden significant mood change detected",
                "threshold": 0.6,  # 60% confidence drop
                "priority": "medium",
                "emoji": "📉",
            },
            "extended_silence": {
                "description": "Child has been unusually quiet",
                "threshold": 1800,  # 30 minutes
                "priority": "low",
                "emoji": "🤫",
            },
            "high_frustration": {
                "description": "High frustration levels detected",
                "threshold": 0.8,  # 80% confidence
                "priority": "high",
                "emoji": "😤",
            },
            "learning_difficulty": {
                "description": "Child may be struggling with learning content",
                "threshold": 5,  # 5 confusion signals
                "priority": "medium",
                "emoji": "🤔",
            },
        }

    def process_emotion_data(self, emotion_history: List[Dict]) -> List[Dict]:
        """Process emotion data and generate alerts"""
        if not self.enabled or not emotion_history:
            return []

        new_alerts = []
        current_time = datetime.now()

        # Check negative emotion streak
        negative_emotions = ["sad", "angry", "frustrated", "confused"]
        recent_negative = [e for e in emotion_history[-10:] if e["emotion"] in negative_emotions]

        if len(recent_negative) >= self.alert_rules["negative_emotion_streak"]["threshold"]:
            alert = self.create_alert(
                "negative_emotion_streak",
                f"Child has shown {len(recent_negative)} negative emotions recently",
                {"emotions": recent_negative},
            )
            new_alerts.append(alert)

        # Check for sudden mood changes
        if len(emotion_history) >= 2:
            recent_confidence = emotion_history[-1]["confidence"]
            previous_confidence = emotion_history[-2]["confidence"]

            if (previous_confidence - recent_confidence) > self.alert_rules["sudden_mood_drop"]["threshold"]:
                alert = self.create_alert(
                    "sudden_mood_drop",
                    f"Confidence dropped from {previous_confidence:.1%} to {recent_confidence:.1%}",
                    {"previous": previous_confidence, "current": recent_confidence},
                )
                new_alerts.append(alert)

        # Check for high frustration
        recent_frustration = [
            e
            for e in emotion_history[-5:]
            if e["emotion"] == "frustrated" and e["confidence"] > self.alert_rules["high_frustration"]["threshold"]
        ]

        if recent_frustration:
            alert = self.create_alert(
                "high_frustration",
                f"High frustration level detected: {recent_frustration[-1]['confidence']:.1%}",
                {"confidence": recent_frustration[-1]["confidence"]},
            )
            new_alerts.append(alert)

        return new_alerts

    def create_alert(self, alert_type: str, message: str, data: Dict) -> Dict:
        """Create a formatted alert"""
        rule = self.alert_rules.get(alert_type, {})

        alert = {
            "type": alert_type,
            "message": message,
            "data": data,
            "timestamp": datetime.now(),
            "priority": rule.get("priority", "medium"),
            "emoji": rule.get("emoji", "⚠️"),
            "description": rule.get("description", ""),
            "id": len(self.alerts_history) + 1,
        }

        self.alerts_history.append(alert)

        # Keep only last 100 alerts
        if len(self.alerts_history) > 100:
            self.alerts_history.pop(0)

        logger.info("Smart alert generated", type=alert_type, priority=alert["priority"])

        return alert

    def get_recent_alerts(self, hours: int = 24) -> List[Dict]:
        """Get alerts from specified time period"""
        cutoff_time = datetime.now() - timedelta(hours=hours)

        return [alert for alert in self.alerts_history if alert["timestamp"] >= cutoff_time]

    def set_sensitivity(float) -> None:
        """Set alert sensitivity (0.1 to 2.0)"""
        self.sensitivity = max(0.1, min(2.0, level))

        # Adjust thresholds based on sensitivity
        for rule_name, rule in self.alert_rules.items():
            if "threshold" in rule:
                if rule_name in ["negative_emotion_streak", "learning_difficulty"]:
                    # For count-based thresholds, adjust inversely
                    rule["threshold"] = max(1, int(rule["threshold"] / self.sensitivity))
                else:
                    # For ratio-based thresholds, adjust directly
                    rule["threshold"] = rule["threshold"] * self.sensitivity

        logger.info("Alert sensitivity updated", level=self.sensitivity)


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
        self.setup_ui()
        self.setup_timers()

        logger.info("Enterprise dashboard initialized with advanced analytics")

    def setup_ui(self) -> Any:
        """Setup comprehensive dashboard UI"""
        layout = QVBoxLayout(self)

        # Create responsive layout with splitters
        main_splitter = QSplitter(Qt.Horizontal)

        # Left panel (30% width)
        left_panel = self.create_metrics_panel()

        # Right panel (70% width)
        right_panel = self.create_charts_panel()

        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(right_panel)
        main_splitter.setSizes([300, 700])  # 30/70 split

        layout.addWidget(main_splitter)

    def create_metrics_panel(self) -> QWidget:
        """Create left metrics panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Status metrics
        status_group = QGroupBox("🚀 System Status")
        status_layout = QGridLayout(status_group)

        # Connection indicator
        status_layout.addWidget(QLabel("Connection:"), 0, 0)
        self.connection_indicator = QLabel("● Disconnected")
        self.connection_indicator.setStyleSheet("QLabel { color: red; font-weight: bold; }")
        status_layout.addWidget(self.connection_indicator, 0, 1)

        # Active children
        status_layout.addWidget(QLabel("Active Children:"), 1, 0)
        self.active_children_label = QLabel("0")
        self.active_children_label.setStyleSheet("QLabel { font-weight: bold; color: #2196F3; }")
        status_layout.addWidget(self.active_children_label, 1, 1)

        # Today's interactions
        status_layout.addWidget(QLabel("Interactions Today:"), 2, 0)
        self.interactions_today_label = QLabel("0")
        self.interactions_today_label.setStyleSheet("QLabel { font-weight: bold; color: #4CAF50; }")
        status_layout.addWidget(self.interactions_today_label, 2, 1)

        layout.addWidget(status_group)

        # Current emotion
        emotion_group = QGroupBox("😊 Current Emotion")
        emotion_layout = QVBoxLayout(emotion_group)

        self.current_emotion_label = QLabel("😐 Neutral")
        self.current_emotion_label.setAlignment(Qt.AlignCenter)
        self.current_emotion_label.setStyleSheet(
            """
            QLabel {
                font-size: 24px;
                font-weight: bold;
                background-color: #f0f0f0;
                border: 2px solid #ddd;
                border-radius: 8px;
                padding: 15px;
                margin: 5px;
            }
        """
        )
        emotion_layout.addWidget(self.current_emotion_label)

        # Confidence meter
        emotion_layout.addWidget(QLabel("Confidence:"))
        self.emotion_confidence_bar = QProgressBar()
        self.emotion_confidence_bar.setRange(0, 100)
        self.emotion_confidence_bar.setValue(0)
        emotion_layout.addWidget(self.emotion_confidence_bar)

        layout.addWidget(emotion_group)

        # Smart alerts
        alerts_group = QGroupBox("🚨 Smart Alerts")
        alerts_layout = QVBoxLayout(alerts_group)

        # Alert controls
        alert_controls = QHBoxLayout()

        self.alerts_enabled_checkbox = QCheckBox("Enable Alerts")
        self.alerts_enabled_checkbox.setChecked(True)
        self.alerts_enabled_checkbox.toggled.connect(self.toggle_alerts)
        alert_controls.addWidget(self.alerts_enabled_checkbox)

        alert_controls.addWidget(QLabel("Sensitivity:"))
        self.alert_sensitivity_slider = QSlider(Qt.Horizontal)
        self.alert_sensitivity_slider.setRange(1, 10)
        self.alert_sensitivity_slider.setValue(5)
        self.alert_sensitivity_slider.valueChanged.connect(self.update_alert_sensitivity)
        alert_controls.addWidget(self.alert_sensitivity_slider)

        alerts_layout.addLayout(alert_controls)

        # Alerts display
        self.alerts_display = QTextEdit()
        self.alerts_display.setMaximumHeight(150)
        self.alerts_display.setPlaceholderText("Smart alerts will appear here...")
        self.alerts_display.setStyleSheet(
            """
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: #fafafa;
                font-size: 11px;
            }
        """
        )
        alerts_layout.addWidget(self.alerts_display)

        layout.addWidget(alerts_group)

        # Child profiles
        profiles_group = QGroupBox("👶 Active Profiles")
        profiles_layout = QVBoxLayout(profiles_group)

        self.profiles_list = QListWidget()
        self.profiles_list.setMaximumHeight(100)
        profiles_layout.addWidget(self.profiles_list)

        layout.addWidget(profiles_group)

        layout.addStretch()
        return panel

    def create_charts_panel(self) -> QWidget:
        """Create right charts panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Chart controls
        controls_layout = QHBoxLayout()

        controls_layout.addWidget(QLabel("Time Range:"))
        self.time_range_combo = QComboBox()
        self.time_range_combo.addItems(["Last Hour", "Last 6 Hours", "Last 24 Hours", "Last Week"])
        self.time_range_combo.setCurrentText("Last 6 Hours")
        self.time_range_combo.currentTextChanged.connect(self.update_charts)
        controls_layout.addWidget(self.time_range_combo)

        refresh_btn = QPushButton("🔄 Refresh Charts")
        refresh_btn.clicked.connect(self.refresh_all_charts)
        controls_layout.addWidget(refresh_btn)

        controls_layout.addStretch()
        layout.addLayout(controls_layout)

        # Charts tabs
        self.charts_tabs = QTabWidget()

        # Emotion analytics tab
        emotion_tab = QWidget()
        emotion_layout = QVBoxLayout(emotion_tab)

        self.emotion_charts_container = QWidget()
        self.emotion_charts_layout = QVBoxLayout(self.emotion_charts_container)

        # Placeholder
        placeholder = QLabel("📊 Emotion charts will appear after first interactions")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("QLabel { color: #666; font-size: 16px; padding: 50px; }")
        self.emotion_charts_layout.addWidget(placeholder)

        emotion_layout.addWidget(self.emotion_charts_container)
        self.charts_tabs.addTab(emotion_tab, "😊 Emotion Analytics")

        # Performance tab
        performance_tab = QWidget()
        performance_layout = QVBoxLayout(performance_tab)

        perf_placeholder = QLabel("📈 Performance metrics will be displayed here")
        perf_placeholder.setAlignment(Qt.AlignCenter)
        perf_placeholder.setStyleSheet("QLabel { color: #666; font-size: 16px; padding: 50px; }")
        performance_layout.addWidget(perf_placeholder)

        self.charts_tabs.addTab(performance_tab, "📊 Performance")

        layout.addWidget(self.charts_tabs)

        return panel

    def setup_timers(self) -> Any:
        """Setup update timers"""
        # Real-time updates every 3 seconds
        self.realtime_timer = QTimer()
        self.realtime_timer.timeout.connect(self.update_realtime_metrics)
        self.realtime_timer.start(3000)

        # Charts update every 15 seconds
        self.charts_timer = QTimer()
        self.charts_timer.timeout.connect(self.update_charts)
        self.charts_timer.start(15000)

        # Alerts processing every 10 seconds
        self.alerts_timer = QTimer()
        self.alerts_timer.timeout.connect(self.process_alerts)
        self.alerts_timer.start(10000)

    def update_realtime_metrics(self) -> Any:
        """Update real-time metrics"""
        try:
            import random

            # Simulate real-time data
            active_children = random.randint(0, 12)
            interactions_today = random.randint(25, 150)

            self.active_children_label.setText(str(active_children))
            self.interactions_today_label.setText(str(interactions_today))

            # Simulate emotion updates (30% chance)
            if random.random() > 0.7:
                emotions = ["happy", "excited", "calm", "curious", "frustrated", "sad"]
                emotion = random.choice(emotions)
                confidence = random.uniform(0.6, 0.95)

                self.add_emotion_data(emotion, confidence)

        except Exception as e:
            logger.error("Failed to update real-time metrics", error=str(e))

    def add_emotion_data(dict=None) -> None:
        """Add new emotion data and update displays"""
        # Add to analytics engine
        self.emotion_engine.add_emotion_data(emotion, confidence, metadata)

        # Update current emotion display
        self.update_current_emotion_display(emotion, confidence)

        # Emit signal
        self.emotion_detected.emit([{"emotion": emotion, "confidence": confidence}], confidence)

        logger.info("Emotion data added", emotion=emotion, confidence=confidence)

    def update_current_emotion_display(float) -> None:
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
        self.current_emotion_label.setText(f"{emoji} {emotion.title()}")
        self.emotion_confidence_bar.setValue(int(confidence * 100))

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
        self.current_emotion_label.setStyleSheet(
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

    def update_charts(self) -> Any:
        """Update all emotion charts"""
        if not self.emotion_engine.plotly_available:
            return

        try:
            # Clear existing charts
            for i in reversed(range(self.emotion_charts_layout.count())):
                child = self.emotion_charts_layout.itemAt(i).widget()
                if child:
                    child.setParent(None)

            # Get time range
            time_range_text = self.time_range_combo.currentText()
            hours_map = {"Last Hour": 1, "Last 6 Hours": 6, "Last 24 Hours": 24, "Last Week": 168}
            hours = hours_map.get(time_range_text, 6)

            # Create timeline chart
            timeline_fig = self.emotion_engine.create_emotion_timeline_chart(hours)
            if timeline_fig:
                self.display_plotly_chart(timeline_fig, "timeline")

            # Create distribution chart
            distribution_fig = self.emotion_engine.create_emotion_distribution_chart()
            if distribution_fig:
                self.display_plotly_chart(distribution_fig, "distribution")

            # Create heatmap
            heatmap_fig = self.emotion_engine.create_emotion_heatmap()
            if heatmap_fig:
                self.display_plotly_chart(heatmap_fig, "heatmap")

        except Exception as e:
            logger.error("Failed to update charts", error=str(e))

    def display_plotly_chart(str) -> None:
        """Display Plotly chart in widget"""
        try:
            if WEBENGINE_AVAILABLE:
                # Use QWebEngineView for interactive charts
                html_str = fig.to_html(include_plotlyjs="cdn", div_id=f"chart_{chart_type}")

                web_view = QWebEngineView()
                web_view.setHtml(html_str)
                web_view.setMinimumHeight(400)

                self.emotion_charts_layout.addWidget(web_view)

            else:
                # Fallback: save as image and display
                import os
                import tempfile

                temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
                fig.write_image(temp_file.name, width=800, height=400)

                pixmap = QPixmap(temp_file.name)
                label = QLabel()
                label.setPixmap(pixmap)
                label.setAlignment(Qt.AlignCenter)

                self.emotion_charts_layout.addWidget(label)

                # Clean up temp file
                os.unlink(temp_file.name)

        except Exception as e:
            logger.error("Failed to display chart", error=str(e), chart_type=chart_type)

            # Show error message
            error_label = QLabel(f"Chart display error: {e}")
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setStyleSheet("QLabel { color: red; }")
            self.emotion_charts_layout.addWidget(error_label)

    def process_alerts(self) -> Any:
        """Process smart alerts"""
        if not self.alert_system.enabled:
            return

        try:
            # Get new alerts
            new_alerts = self.alert_system.process_emotion_data(self.emotion_engine.emotion_history)

            # Display new alerts
            for alert in new_alerts:
                self.display_alert(alert)

        except Exception as e:
            logger.error("Failed to process alerts", error=str(e))

    def display_alert(Dict) -> None:
        """Display alert in the alerts panel"""
        timestamp = alert["timestamp"].strftime("%H:%M:%S")
        priority_colors = {"high": "#ff4444", "medium": "#ff8800", "low": "#4488ff"}

        color = priority_colors.get(alert["priority"], "#666666")

        alert_html = f"""
        <div style="border-left: 4px solid {color}; padding: 8px; margin: 4px 0; background-color: #f9f9f9;">
            <strong>{alert['emoji']} {alert['message']}</strong><br/>
            <small style="color: #666;">{timestamp} - {alert['priority'].upper()} priority</small>
        </div>
        """

        current_html = self.alerts_display.toHtml()
        self.alerts_display.setHtml(alert_html + current_html)

        # Emit signal for parent handling
        self.alert_triggered.emit(alert["type"], alert["message"], alert["data"])

    def toggle_alerts(bool) -> None:
        """Toggle smart alerts system"""
        self.alert_system.enabled = enabled

        if enabled:
            self.alerts_timer.start(10000)
            logger.info("Smart alerts enabled")
        else:
            self.alerts_timer.stop()
            logger.info("Smart alerts disabled")

    def update_alert_sensitivity(int) -> None:
        """Update alert sensitivity"""
        sensitivity = value / 5.0  # Convert 1-10 scale to 0.2-2.0
        self.alert_system.set_sensitivity(sensitivity)

    def refresh_all_charts(self) -> Any:
        """Manually refresh all charts"""
        self.update_charts()
        logger.info("Charts refreshed manually")

    def update_connection_status(str) -> None:
        """Update connection status indicator"""
        status_config = {
            "Connected": {"color": "green", "symbol": "●"},
            "Connecting...": {"color": "orange", "symbol": "◐"},
            "Disconnected": {"color": "red", "symbol": "●"},
            "Error": {"color": "red", "symbol": "✖"},
        }

        config = status_config.get(status, {"color": "gray", "symbol": "●"})

        self.connection_indicator.setText(f"{config['symbol']} {status}")
        self.connection_indicator.setStyleSheet(f"QLabel {{ color: {config['color']}; font-weight: bold; }}")

    def add_child_profile(dict=None) -> None:
        """Add child profile to dashboard"""
        profile_text = f"{name} (Age: {age})"
        self.profiles_list.addItem(profile_text)

        self.child_profiles.append({"name": name, "age": age, "metadata": metadata or {}, "added_time": datetime.now()})

        logger.info("Child profile added", name=name, age=age)

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
