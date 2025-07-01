"""
Conversation Widget for AI Teddy Bear
Modern chat interface with message history and auto-scrolling
"""

import asyncio
from datetime import datetime
from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, 
    QPushButton, QScrollArea
)
from PySide6.QtCore import Qt, pyqtSlot
from PySide6.QtGui import QFont

import structlog

logger = structlog.get_logger()


class ConversationWidget(QWidget):
    """Modern conversation interface widget"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.message_sender = None  # Will be set by parent
        self.setup_ui()
    
    def setup_ui(self) -> Any:
        """Initialize the conversation interface"""
        layout = QVBoxLayout(self)
        
        # Chat display area
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(QFont("Arial", 11))
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #3c3c3c;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        # Input area
        input_layout = QHBoxLayout()
        
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Type your message here...")
        self.message_input.setFont(QFont("Arial", 10))
        self.message_input.setStyleSheet("""
            QLineEdit {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 6px;
                padding: 8px;
            }
            QLineEdit:focus {
                border: 2px solid #007acc;
            }
        """)
        
        self.send_button = QPushButton("Send")
        self.send_button.setFont(QFont("Arial", 10, QFont.Bold))
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #004578;
            }
        """)
        
        # Setup connections
        self.message_input.returnPressed.connect(self.send_message)
        self.send_button.clicked.connect(self.send_message)
        
        # Add widgets to layout
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)
        
        layout.addWidget(self.chat_display, 1)
        layout.addLayout(input_layout)
        
        # Add welcome message
        self.add_message("Teddy", "Hi! I'm your AI Teddy Bear. How can I help you today?")
    
    def add_message(Optional[datetime] = None) -> None:
        """Add a message to the conversation display"""
        if timestamp is None:
            timestamp = datetime.now()
        
        time_str = timestamp.strftime("%H:%M:%S")
        
        # Format message based on sender
        if sender.lower() == "teddy":
            formatted_message = f"""
            <div style="margin: 8px 0; padding: 10px; background-color: #1e3a5f; 
                        border-radius: 12px; border-left: 4px solid #007acc;">
                <strong style="color: #4da6ff;">🧸 Teddy</strong> 
                <span style="color: #888; font-size: 10px;">{time_str}</span><br>
                <span style="color: #ffffff;">{message}</span>
            </div>
            """
        else:
            formatted_message = f"""
            <div style="margin: 8px 0; padding: 10px; background-color: #2d4a3e; 
                        border-radius: 12px; border-left: 4px solid #28a745;">
                <strong style="color: #66cc66;">👤 {sender}</strong> 
                <span style="color: #888; font-size: 10px;">{time_str}</span><br>
                <span style="color: #ffffff;">{message}</span>
            </div>
            """
        
        self.chat_display.append(formatted_message)
        
        # Auto-scroll to bottom
        scrollbar = self.chat_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    @pyqtSlot()
    def send_message(self) -> Any:
        """Send message to the server"""
        message = self.message_input.text().strip()
        if not message:
            return
        
        # Add user message to display
        self.add_message("You", message)
        
        # Clear input
        self.message_input.clear()
        
        # Send to server
        self._send_message_to_server(message)
    
    def _send_message_to_server(str) -> None:
        """Send message to server asynchronously"""
        if self.message_sender:
            try:
                # Create metadata for the message
                metadata = {
                    "source": "conversation_widget",
                    "message_type": "text_chat",
                    "session_id": f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                }
                
                # Send async
                asyncio.create_task(
                    self.message_sender.send_text_message(message, metadata)
                )
                
                logger.info("Text message sent", message_preview=message[:50])
                
            except Exception as e:
                logger.error("Failed to send text message", error=str(e))
                self.add_message("System", f"❌ Failed to send message: {e}")
        else:
            logger.warning("No message sender configured")
            self.add_message("System", "⚠️ No connection to server")
    
    def set_message_sender(self, message_sender) -> Any:
        """Set the message sender instance"""
        self.message_sender = message_sender
    
    def handle_server_response(dict) -> None:
        """Handle response from server"""
        if response.get("type") == "text_response":
            teddy_message = response.get("response", "I didn't understand that.")
            self.add_message("Teddy", teddy_message)
        elif response.get("type") == "error":
            error_msg = response.get("message", "Unknown error occurred")
            self.add_message("System", f"❌ Error: {error_msg}")
    
    def clear_conversation(self) -> Any:
        """Clear the conversation history"""
        self.chat_display.clear()
        self.add_message("Teddy", "Conversation cleared! How can I help you?")
        logger.info("Conversation history cleared") 