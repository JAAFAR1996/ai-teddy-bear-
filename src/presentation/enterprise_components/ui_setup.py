from PySide6.QtCore import Qt
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


def setup_ui(widget: QWidget) -> None:
    """Setup comprehensive dashboard UI"""
    layout = QVBoxLayout(widget)

    # Create responsive layout with splitters
    main_splitter = QSplitter(Qt.Horizontal)

    # Left panel (30% width)
    left_panel = create_metrics_panel(widget)

    # Right panel (70% width)
    right_panel = create_charts_panel(widget)

    main_splitter.addWidget(left_panel)
    main_splitter.addWidget(right_panel)
    main_splitter.setSizes([300, 700])  # 30/70 split

    layout.addWidget(main_splitter)


def create_metrics_panel(widget: QWidget) -> QWidget:
    """Create left metrics panel"""
    panel = QWidget()
    layout = QVBoxLayout(panel)

    # Status metrics
    status_group = QGroupBox("🚀 System Status")
    status_layout = QGridLayout(status_group)

    # Connection indicator
    status_layout.addWidget(QLabel("Connection:"), 0, 0)
    widget.connection_indicator = QLabel("● Disconnected")
    widget.connection_indicator.setStyleSheet(
        "QLabel { color: red; font-weight: bold; }"
    )
    status_layout.addWidget(widget.connection_indicator, 0, 1)

    # Active children
    status_layout.addWidget(QLabel("Active Children:"), 1, 0)
    widget.active_children_label = QLabel("0")
    widget.active_children_label.setStyleSheet(
        "QLabel { font-weight: bold; color: #2196F3; }"
    )
    status_layout.addWidget(widget.active_children_label, 1, 1)

    # Today's interactions
    status_layout.addWidget(QLabel("Interactions Today:"), 2, 0)
    widget.interactions_today_label = QLabel("0")
    widget.interactions_today_label.setStyleSheet(
        "QLabel { font-weight: bold; color: #4CAF50; }"
    )
    status_layout.addWidget(widget.interactions_today_label, 2, 1)

    layout.addWidget(status_group)

    # Current emotion
    emotion_group = QGroupBox("😊 Current Emotion")
    emotion_layout = QVBoxLayout(emotion_group)

    widget.current_emotion_label = QLabel("😐 Neutral")
    widget.current_emotion_label.setAlignment(Qt.AlignCenter)
    widget.current_emotion_label.setStyleSheet(
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
    emotion_layout.addWidget(widget.current_emotion_label)

    # Confidence meter
    emotion_layout.addWidget(QLabel("Confidence:"))
    widget.emotion_confidence_bar = QProgressBar()
    widget.emotion_confidence_bar.setRange(0, 100)
    widget.emotion_confidence_bar.setValue(0)
    emotion_layout.addWidget(widget.emotion_confidence_bar)

    layout.addWidget(emotion_group)

    # Smart alerts
    alerts_group = QGroupBox("🚨 Smart Alerts")
    alerts_layout = QVBoxLayout(alerts_group)

    # Alert controls
    alert_controls = QHBoxLayout()

    widget.alerts_enabled_checkbox = QCheckBox("Enable Alerts")
    widget.alerts_enabled_checkbox.setChecked(True)
    widget.alerts_enabled_checkbox.toggled.connect(widget.toggle_alerts)
    alert_controls.addWidget(widget.alerts_enabled_checkbox)

    alert_controls.addWidget(QLabel("Sensitivity:"))
    widget.alert_sensitivity_slider = QSlider(Qt.Horizontal)
    widget.alert_sensitivity_slider.setRange(1, 10)
    widget.alert_sensitivity_slider.setValue(5)
    widget.alert_sensitivity_slider.valueChanged.connect(
        widget.update_alert_sensitivity
    )
    alert_controls.addWidget(widget.alert_sensitivity_slider)

    alerts_layout.addLayout(alert_controls)

    # Alerts display
    widget.alerts_display = QTextEdit()
    widget.alerts_display.setMaximumHeight(150)
    widget.alerts_display.setPlaceholderText(
        "Smart alerts will appear here...")
    widget.alerts_display.setStyleSheet(
        """
        QTextEdit {
            border: 1px solid #ddd;
            border-radius: 4px;
            background-color: #fafafa;
            font-size: 11px;
        }
    """
    )
    alerts_layout.addWidget(widget.alerts_display)

    layout.addWidget(alerts_group)

    # Child profiles
    profiles_group = QGroupBox("👶 Active Profiles")
    profiles_layout = QVBoxLayout(profiles_group)

    widget.profiles_list = QListWidget()
    widget.profiles_list.setMaximumHeight(100)
    profiles_layout.addWidget(widget.profiles_list)

    layout.addWidget(profiles_group)

    layout.addStretch()
    return panel


def create_charts_panel(widget: QWidget) -> QWidget:
    """Create right charts panel"""
    panel = QWidget()
    layout = QVBoxLayout(panel)

    # Chart controls
    controls_layout = QHBoxLayout()

    controls_layout.addWidget(QLabel("Time Range:"))
    widget.time_range_combo = QComboBox()
    widget.time_range_combo.addItems(
        ["Last Hour", "Last 6 Hours", "Last 24 Hours", "Last Week"]
    )
    widget.time_range_combo.setCurrentText("Last 6 Hours")
    widget.time_range_combo.currentTextChanged.connect(widget.update_charts)
    controls_layout.addWidget(widget.time_range_combo)

    refresh_btn = QPushButton("🔄 Refresh Charts")
    refresh_btn.clicked.connect(widget.refresh_all_charts)
    controls_layout.addWidget(refresh_btn)

    controls_layout.addStretch()
    layout.addLayout(controls_layout)

    # Charts tabs
    widget.charts_tabs = QTabWidget()

    # Emotion analytics tab
    emotion_tab = QWidget()
    emotion_layout = QVBoxLayout(emotion_tab)

    widget.emotion_charts_container = QWidget()
    widget.emotion_charts_layout = QVBoxLayout(widget.emotion_charts_container)

    # Placeholder
    placeholder = QLabel(
        "📊 Emotion charts will appear after first interactions")
    placeholder.setAlignment(Qt.AlignCenter)
    placeholder.setStyleSheet(
        "QLabel { color: #666; font-size: 16px; padding: 50px; }"
    )
    widget.emotion_charts_layout.addWidget(placeholder)

    emotion_layout.addWidget(widget.emotion_charts_container)
    widget.charts_tabs.addTab(emotion_tab, "😊 Emotion Analytics")

    # Performance tab
    performance_tab = QWidget()
    performance_layout = QVBoxLayout(performance_tab)

    perf_placeholder = QLabel(
        "📈 Performance metrics will be displayed here")
    perf_placeholder.setAlignment(Qt.AlignCenter)
    perf_placeholder.setStyleSheet(
        "QLabel { color: #666; font-size: 16px; padding: 50px; }"
    )
    performance_layout.addWidget(perf_placeholder)

    widget.charts_tabs.addTab(performance_tab, "📊 Performance")

    layout.addWidget(widget.charts_tabs)

    return panel
