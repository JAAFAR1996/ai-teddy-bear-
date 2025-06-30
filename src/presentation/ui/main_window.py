"""
Main Window for AI Teddy Bear Application
Modern enterprise interface with modular design
"""

import sys
from typing import Dict, Any

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QPushButton, QLabel, QStatusBar, QMenuBar,
    QMessageBox, QSystemTrayIcon, QMenu
)
from PySide6.QtCore import Qt, QTimer, QSettings
from PySide6.QtGui import QFont, QIcon, QAction

from .networking.websocket_client import WebSocketClient
from .networking.message_sender import EnterpriseMessageSender
from .widgets.audio_widget import ModernAudioWidget
from .widgets.conversation_widget import ConversationWidget

import structlog

logger = structlog.get_logger()


class TeddyMainWindow(QMainWindow):
    """Main application window for AI Teddy Bear"""
    
    def __init__(self):
        super().__init__()
        self.settings = QSettings("AiTeddyBear", "EnterpriseUI")
        self._setup_components()
        self._setup_ui()
        self._setup_connections()
        self._restore_window_state()
    
    def _setup_components(self) -> Any:
        """Initialize core components"""
        # Networking
        self.websocket_client = WebSocketClient()
        self.message_sender = EnterpriseMessageSender(self.websocket_client)
        
        # UI Components
        self.audio_widget = ModernAudioWidget()
        self.conversation_widget = ConversationWidget()
        
        # Connect message sender to widgets
        self.audio_widget.set_message_sender(self.message_sender)
        self.conversation_widget.set_message_sender(self.message_sender)
    
    def _setup_ui(self) -> Any:
        """Setup the user interface"""
        self.setWindowTitle("AI Teddy Bear - Enterprise Edition 2025")
        self.setMinimumSize(1000, 700)
        
        # Central widget with tabs
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Connection status
        self.connection_label = QLabel("🔴 Disconnected")
        self.connection_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(self.connection_label)
        
        # Main tabs
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self.audio_widget, "🎤 Audio Recording")
        self.tab_widget.addTab(self.conversation_widget, "💬 Conversation")
        
        layout.addWidget(self.tab_widget)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.connect_button = QPushButton("🔌 Connect")
        self.connect_button.clicked.connect(self._toggle_connection)
        controls_layout.addWidget(self.connect_button)
        
        self.status_label = QLabel("Ready")
        controls_layout.addWidget(self.status_label)
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("AI Teddy Bear Enterprise UI Ready")
        
        # Menu bar
        self._create_menu_bar()
        
        # Apply modern styling
        self._apply_modern_theme()
    
    def _create_menu_bar(self) -> Any:
        """Create application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        connect_action = QAction("Connect to Server", self)
        connect_action.triggered.connect(self._toggle_connection)
        file_menu.addAction(connect_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _setup_connections(self) -> Any:
        """Setup signal-slot connections"""
        # WebSocket connections
        self.websocket_client.connected.connect(self._on_connected)
        self.websocket_client.disconnected.connect(self._on_disconnected)
        self.websocket_client.message_received.connect(self._on_message_received)
        self.websocket_client.error_occurred.connect(self._on_error)
        self.websocket_client.connection_status_changed.connect(self._update_connection_status)
    
    def _toggle_connection(self) -> Any:
        """Toggle WebSocket connection"""
        if self.websocket_client.is_connected:
            self.websocket_client.disconnect_from_server()
        else:
            self.websocket_client.connect_to_server()
    
    def _on_connected(self) -> Any:
        """Handle successful connection"""
        self.connect_button.setText("🔌 Disconnect")
        self.status_label.setText("Connected to server")
        self.status_bar.showMessage("Connected to AI Teddy Bear server")
        logger.info("UI connected to server")
    
    def _on_disconnected(self) -> Any:
        """Handle disconnection"""
        self.connect_button.setText("🔌 Connect")
        self.status_label.setText("Disconnected")
        self.status_bar.showMessage("Disconnected from server")
        logger.info("UI disconnected from server")
    
    def _on_message_received(self, message -> Any: Dict[str, Any]) -> Any:
        """Handle incoming WebSocket message"""
        message_type = message.get("type")
        
        if message_type in ["text_response", "audio_response"]:
            # Forward to conversation widget
            self.conversation_widget.handle_server_response(message)
        elif message_type == "status_update":
            self._handle_status_update(message)
        else:
            logger.debug("Unhandled message type", message_type=message_type)
    
    def _handle_status_update(self, message -> Any: Dict[str, Any]) -> Any:
        """Handle server status updates"""
        status = message.get("status", "unknown")
        self.status_bar.showMessage(f"Server: {status}")
    
    def _on_error(self, error -> Any: str) -> Any:
        """Handle WebSocket error"""
        self.status_label.setText(f"Error: {error}")
        self.status_bar.showMessage(f"Connection error: {error}")
        logger.error("WebSocket error", error=error)
    
    def _update_connection_status(self, status -> Any: str) -> Any:
        """Update connection status display"""
        status_colors = {
            "Connecting...": "🟡",
            "Connected": "🟢",
            "Disconnected": "🔴",
            "Error": "❌",
            "Failed": "❌"
        }
        
        color = status_colors.get(status, "❓")
        self.connection_label.setText(f"{color} {status}")
    
    def _show_about(self) -> Any:
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About AI Teddy Bear",
            """
            <h3>AI Teddy Bear - Enterprise Edition 2025</h3>
            <p>Modern, intelligent companion for children</p>
            <p>Features:</p>
            <ul>
                <li>🎤 Professional audio recording</li>
                <li>🤖 AI-powered conversations</li>
                <li>🔒 Enterprise-grade security</li>
                <li>📊 Real-time analytics</li>
            </ul>
            <p><b>Version:</b> 2025.1.0</p>
            """
        )
    
    def _apply_modern_theme(self) -> Any:
        """Apply modern dark theme"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QTabWidget::pane {
                border: 1px solid #3c3c3c;
                background-color: #2b2b2b;
            }
            QTabBar::tab {
                background-color: #3c3c3c;
                color: #ffffff;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #007acc;
            }
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QLabel {
                color: #ffffff;
            }
            QStatusBar {
                background-color: #3c3c3c;
                color: #ffffff;
            }
        """)
    
    def _save_window_state(self) -> Any:
        """Save window state to settings"""
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
    
    def _restore_window_state(self) -> Any:
        """Restore window state from settings"""
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        
        window_state = self.settings.value("windowState")
        if window_state:
            self.restoreState(window_state)
    
    def closeEvent(self, event) -> Any:
        """Handle window close event"""
        self._save_window_state()
        
        if self.websocket_client.is_connected:
            self.websocket_client.disconnect_from_server()
        
        event.accept()
        logger.info("Application closed")


class ModernTeddyUI:
    """Main application class"""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("AI Teddy Bear Enterprise")
        self.app.setApplicationVersion("2025.1.0")
        
        # Setup exception handling
        sys.excepthook = self._handle_exception
        
        self.main_window = TeddyMainWindow()
    
    def run(self) -> Any:
        """Run the application"""
        self.main_window.show()
        
        # Auto-connect on startup
        QTimer.singleShot(1000, self.main_window.websocket_client.connect_to_server)
        
        return self.app.exec()
    
    def _handle_exception(self, exc_type, exc_value, exc_traceback) -> Any:
        """Handle uncaught exceptions"""
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        logger.error("Uncaught exception", 
                    exc_type=exc_type.__name__,
                    exc_value=str(exc_value))
        
        # Show error dialog
        QMessageBox.critical(
            None,
            "Application Error",
            f"An unexpected error occurred:\n\n{exc_type.__name__}: {exc_value}"
        )


def main() -> Any:
    """Main entry point"""
    ui = ModernTeddyUI()
    return ui.run()


if __name__ == "__main__":
    sys.exit(main()) 