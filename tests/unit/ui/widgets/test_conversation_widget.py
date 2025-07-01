"""
Unit Tests for ConversationWidget - Chat Interface Testing
"""

from datetime import datetime
from unittest.mock import patch

import pytest
from PySide6.QtWidgets import QApplication

from src.ui.widgets.conversation_widget import ConversationWidget


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication for testing Qt widgets"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class TestConversationWidget:
    """Test suite for ConversationWidget"""

    @pytest.fixture
    def conversation_widget(self, qapp):
        """Create ConversationWidget for testing"""
        return ConversationWidget()

    def test_widget_initialization(self, conversation_widget):
        """Test widget initialization with proper defaults"""
        assert conversation_widget.max_messages == 1000
        assert conversation_widget.auto_scroll == True
        assert conversation_widget.show_timestamps == True
        assert conversation_widget.word_wrap == True
        assert conversation_widget.message_history == []
        assert conversation_widget.current_session_id is None

    def test_ui_components_creation(self, conversation_widget):
        """Test that UI components are properly created"""
        assert conversation_widget.scroll_area is not None
        assert conversation_widget.messages_container is not None
        assert conversation_widget.messages_layout is not None
        assert conversation_widget.text_input is not None
        assert conversation_widget.send_button is not None
        assert conversation_widget.clear_button is not None

    def test_add_message_basic(self, conversation_widget):
        """Test basic message addition"""
        test_time = datetime.now()

        conversation_widget.add_message("User", "Hello world!", test_time, "user")

        assert len(conversation_widget.message_history) == 1
        message = conversation_widget.message_history[0]
        assert message["sender"] == "User"
        assert message["message"] == "Hello world!"
        assert message["timestamp"] == test_time
        assert message["type"] == "user"

    def test_add_message_with_metadata(self, conversation_widget):
        """Test message addition with metadata"""
        metadata = {"session_id": "test123", "confidence": 0.95}

        conversation_widget.add_message("AI", "Response message", metadata=metadata)

        message = conversation_widget.message_history[0]
        assert message["metadata"] == metadata

    def test_add_message_different_types(self, conversation_widget):
        """Test adding messages of different types"""
        message_types = ["user", "ai", "system", "error"]

        for msg_type in message_types:
            conversation_widget.add_message(
                "Sender", f"Message of type {msg_type}", message_type=msg_type
            )

        assert len(conversation_widget.message_history) == 4
        for i, msg_type in enumerate(message_types):
            assert conversation_widget.message_history[i]["type"] == msg_type

    def test_message_history_limit(self, conversation_widget):
        """Test message history limit enforcement"""
        conversation_widget.max_messages = 5

        # Add more messages than the limit
        for i in range(10):
            conversation_widget.add_message("User", f"Message {i}")

        assert len(conversation_widget.message_history) == 5
        # Should keep the latest messages
        assert "Message 9" in conversation_widget.message_history[-1]["message"]

    def test_send_message_functionality(self, conversation_widget):
        """Test message sending functionality"""
        test_message = "Test message to send"
        conversation_widget.text_input.setText(test_message)

        with patch.object(conversation_widget, "message_sent") as mock_signal:
            with patch.object(conversation_widget, "send_requested") as mock_send_req:
                conversation_widget.send_message()

                # Text input should be cleared
                assert conversation_widget.text_input.text() == ""

                # Signals should be emitted
                mock_signal.emit.assert_called_once_with(test_message)
                mock_send_req.emit.assert_called_once()

    def test_send_empty_message(self, conversation_widget):
        """Test that empty messages are not sent"""
        conversation_widget.text_input.setText("   ")  # Whitespace only

        with patch.object(conversation_widget, "message_sent") as mock_signal:
            conversation_widget.send_message()
            mock_signal.emit.assert_not_called()

    def test_clear_conversation(self, conversation_widget):
        """Test conversation clearing functionality"""
        # Add some messages first
        for i in range(3):
            conversation_widget.add_message("User", f"Message {i}")

        assert len(conversation_widget.message_history) == 3

        conversation_widget.clear_conversation()

        # History should be cleared, but system message added
        assert len(conversation_widget.message_history) == 1
        assert conversation_widget.message_history[0]["type"] == "system"

    def test_session_id_setting(self, conversation_widget):
        """Test session ID setting"""
        test_session_id = "session_12345"

        conversation_widget.set_session_id(test_session_id)

        assert conversation_widget.current_session_id == test_session_id

    def test_auto_scroll_setting(self, conversation_widget):
        """Test auto-scroll setting"""
        assert conversation_widget.auto_scroll == True

        conversation_widget.set_auto_scroll(False)
        assert conversation_widget.auto_scroll == False

    def test_timestamp_display_setting(self, conversation_widget):
        """Test timestamp display setting"""
        assert conversation_widget.show_timestamps == True

        conversation_widget.set_show_timestamps(False)
        assert conversation_widget.show_timestamps == False

    def test_export_conversation(self, conversation_widget):
        """Test conversation export functionality"""
        # Add some test messages
        conversation_widget.add_message("User", "Hello")
        conversation_widget.add_message("AI", "Hi there!")

        exported = conversation_widget.export_conversation()

        assert isinstance(exported, str)
        assert "Conversation Export" in exported
        assert "Hello" in exported
        assert "Hi there!" in exported

    def test_conversation_statistics(self, conversation_widget):
        """Test conversation statistics generation"""
        # Add messages of different types
        conversation_widget.add_message("User", "User message", message_type="user")
        conversation_widget.add_message("AI", "AI response", message_type="ai")
        conversation_widget.add_message("System", "System info", message_type="system")

        stats = conversation_widget.get_conversation_stats()

        assert isinstance(stats, dict)
        assert stats["message_count"] == 3
        assert "type_counts" in stats
        assert stats["type_counts"]["user"] == 1
        assert stats["type_counts"]["ai"] == 1
        assert stats["type_counts"]["system"] == 1
        assert "total_characters" in stats
        assert "average_message_length" in stats

    def test_empty_conversation_stats(self, conversation_widget):
        """Test statistics for empty conversation"""
        stats = conversation_widget.get_conversation_stats()

        assert stats["message_count"] == 0

    def test_metadata_formatting(self, conversation_widget):
        """Test metadata formatting for display"""
        metadata = {
            "session_id": "test123",
            "processing_time": 1.234,
            "confidence": 0.95,
            "irrelevant_key": "ignored",
        }

        formatted = conversation_widget._format_metadata(metadata)

        assert "session_id: test123" in formatted
        assert "processing_time: 1.23" in formatted  # Should be rounded
        assert "confidence: 0.95" in formatted
        assert "irrelevant_key" not in formatted  # Should be filtered

    def test_empty_metadata_formatting(self, conversation_widget):
        """Test formatting of empty or None metadata"""
        assert conversation_widget._format_metadata({}) == ""
        assert conversation_widget._format_metadata(None) == ""
        assert conversation_widget._format_metadata({"empty": None}) == ""

    def test_widget_styling_setup(self, conversation_widget):
        """Test that widget styling is properly set up"""
        assert conversation_widget.colors is not None
        assert conversation_widget.fonts is not None

        # Check that key colors are defined
        required_colors = [
            "background",
            "message_background",
            "user_message",
            "ai_message",
            "system_message",
            "error_message",
            "text",
        ]

        for color_key in required_colors:
            assert color_key in conversation_widget.colors

    def test_message_widget_creation(self, conversation_widget):
        """Test message widget creation with different types"""
        test_time = datetime.now()

        widget = conversation_widget._create_message_widget(
            "TestUser", "Test message", test_time, "user", {"test": "meta"}
        )

        assert widget is not None
        # Widget should be properly configured
        assert widget.layout() is not None

    def test_auto_scroll_timer(self, conversation_widget):
        """Test auto-scroll timer functionality"""
        assert conversation_widget.scroll_timer is not None
        assert conversation_widget.scroll_timer.isSingleShot()

    def test_error_handling_in_add_message(self, conversation_widget):
        """Test error handling when adding messages"""
        # This should not raise an exception
        try:
            conversation_widget.add_message(None, None)
        except Exception:
            pytest.fail("add_message should handle None values gracefully")

    def test_widget_cleanup(self, conversation_widget):
        """Test widget cleanup functionality"""
        # Add many messages to trigger cleanup
        conversation_widget.max_messages = 10

        for i in range(20):
            conversation_widget.add_message("User", f"Message {i}")

        # Should have triggered cleanup
        assert len(conversation_widget.message_history) <= 10


@pytest.mark.integration
class TestConversationWidgetIntegration:
    """Integration tests for ConversationWidget"""

    def test_widget_with_real_qt_signals(self, qapp):
        """Test widget with real Qt signal connections"""
        widget = ConversationWidget()

        # Test that signals are properly connected
        assert widget.message_sent is not None
        assert widget.send_requested is not None

        # Test button click simulation
        widget.text_input.setText("Test message")

        # This would simulate actual button click in integration test
        # widget.send_button.click()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
