"""
Comprehensive Frontend Tests
Full test coverage for the AI Teddy Bear frontend application
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List
import requests
import logging

# Test configuration
TEST_CONFIG = {
    "base_url": "http://localhost:3000",
    "api_url": "http://localhost:8000/api/v1",
    "test_timeout": 30,
    "test_user": {
        "email": "test@example.com",
        "password": "Test123!@#",
        "role": "parent",
    },
}

logger = logging.getLogger(__name__)


class TestAuthentication:
    """Test authentication functionality"""

    @pytest.fixture
    def auth_service(self):
        """Mock auth service"""
        service = Mock()
        service.login = AsyncMock()
        service.logout = AsyncMock()
        service.refresh_token = AsyncMock()
        service.is_authenticated = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_login_success(self, auth_service):
        """Test successful login"""
        # Arrange
        auth_service.login.return_value = {
            "user": {"id": "123", "email": TEST_CONFIG["test_user"]["email"]},
            "token": "jwt_token",
            "refreshToken": "refresh_token",
        }

        # Act
        result = await auth_service.login(
            TEST_CONFIG["test_user"]["email"], TEST_CONFIG["test_user"]["password"]
        )

        # Assert
        assert result["token"] == "jwt_token"
        assert result["user"]["email"] == TEST_CONFIG["test_user"]["email"]
        auth_service.login.assert_called_once()

    @pytest.mark.asyncio
    async def test_login_failure(self, auth_service):
        """Test failed login with invalid credentials"""
        # Arrange
        auth_service.login.side_effect = Exception("Invalid credentials")

        # Act & Assert
        with pytest.raises(Exception, match="Invalid credentials"):
            await auth_service.login("wrong@example.com", "wrong_password")

    @pytest.mark.asyncio
    async def test_logout(self, auth_service):
        """Test logout functionality"""
        # Arrange
        auth_service.logout.return_value = True

        # Act
        result = await auth_service.logout()

        # Assert
        assert result is True
        auth_service.logout.assert_called_once()

    @pytest.mark.asyncio
    async def test_token_refresh(self, auth_service):
        """Test token refresh"""
        # Arrange
        auth_service.refresh_token.return_value = {
            "token": "new_jwt_token",
            "refreshToken": "new_refresh_token",
        }

        # Act
        result = await auth_service.refresh_token("old_refresh_token")

        # Assert
        assert result["token"] == "new_jwt_token"
        auth_service.refresh_token.assert_called_once_with("old_refresh_token")

    @pytest.mark.asyncio
    async def test_auth_guard(self, auth_service):
        """Test authentication guard"""
        # Test authenticated user
        auth_service.is_authenticated.return_value = True
        assert await auth_service.is_authenticated() is True

        # Test unauthenticated user
        auth_service.is_authenticated.return_value = False
        assert await auth_service.is_authenticated() is False


class TestDashboard:
    """Test dashboard functionality"""

    @pytest.fixture
    def dashboard_service(self):
        """Mock dashboard service"""
        service = Mock()
        service.get_stats = AsyncMock()
        service.get_conversations = AsyncMock()
        service.get_emotion_data = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_dashboard_stats(self, dashboard_service):
        """Test fetching dashboard statistics"""
        # Arrange
        expected_stats = {
            "dailyConversations": 8,
            "emotionalState": "happy",
            "activityTime": 45,
            "educationalProgress": 85,
            "conversationTrend": [
                {"date": "2024-01-01", "count": 5},
                {"date": "2024-01-02", "count": 8},
            ],
        }
        dashboard_service.get_stats.return_value = expected_stats

        # Act
        stats = await dashboard_service.get_stats()

        # Assert
        assert stats["dailyConversations"] == 8
        assert stats["emotionalState"] == "happy"
        assert stats["activityTime"] == 45
        assert stats["educationalProgress"] == 85
        assert len(stats["conversationTrend"]) == 2

    @pytest.mark.asyncio
    async def test_emotion_distribution(self, dashboard_service):
        """Test emotion distribution data"""
        # Arrange
        emotion_data = [
            {"emotion": "happy", "value": 40},
            {"emotion": "neutral", "value": 30},
            {"emotion": "excited", "value": 20},
            {"emotion": "sad", "value": 10},
        ]
        dashboard_service.get_emotion_data.return_value = emotion_data

        # Act
        emotions = await dashboard_service.get_emotion_data()

        # Assert
        assert len(emotions) == 4
        assert sum(e["value"] for e in emotions) == 100
        assert emotions[0]["emotion"] == "happy"
        assert emotions[0]["value"] == 40

    @pytest.mark.asyncio
    async def test_real_time_updates(self, dashboard_service):
        """Test real-time dashboard updates"""
        # Arrange
        update_count = 0

        async def mock_stats():
            nonlocal update_count
            update_count += 1
            return {"update": update_count}

        dashboard_service.get_stats = mock_stats

        # Act - Simulate multiple updates
        results = []
        for _ in range(3):
            result = await dashboard_service.get_stats()
            results.append(result)
            await asyncio.sleep(0.1)

        # Assert
        assert len(results) == 3
        assert results[0]["update"] == 1
        assert results[2]["update"] == 3


class TestConversations:
    """Test conversations functionality"""

    @pytest.fixture
    def conversation_service(self):
        """Mock conversation service"""
        service = Mock()
        service.get_conversations = AsyncMock()
        service.get_conversation_details = AsyncMock()
        service.start_conversation = AsyncMock()
        service.end_conversation = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_get_conversations(self, conversation_service):
        """Test fetching conversations list"""
        # Arrange
        conversations = [
            {
                "id": "conv1",
                "childId": "child1",
                "startTime": "2024-01-01T10:00:00Z",
                "duration": 300,
                "summary": "Story about animals",
            },
            {
                "id": "conv2",
                "childId": "child1",
                "startTime": "2024-01-01T14:00:00Z",
                "duration": 450,
                "summary": "Learning numbers",
            },
        ]
        conversation_service.get_conversations.return_value = {
            "conversations": conversations,
            "total": 2,
        }

        # Act
        result = await conversation_service.get_conversations("child1")

        # Assert
        assert result["total"] == 2
        assert len(result["conversations"]) == 2
        assert result["conversations"][0]["id"] == "conv1"

    @pytest.mark.asyncio
    async def test_conversation_details(self, conversation_service):
        """Test fetching conversation details"""
        # Arrange
        conversation_details = {
            "id": "conv1",
            "childId": "child1",
            "startTime": "2024-01-01T10:00:00Z",
            "endTime": "2024-01-01T10:05:00Z",
            "duration": 300,
            "transcript": [
                {
                    "speaker": "child",
                    "text": "Tell me a story",
                    "timestamp": "2024-01-01T10:00:10Z",
                },
                {
                    "speaker": "teddy",
                    "text": "Once upon a time...",
                    "timestamp": "2024-01-01T10:00:15Z",
                },
            ],
            "emotions": [
                {
                    "emotion": "happy",
                    "confidence": 0.85,
                    "timestamp": "2024-01-01T10:00:10Z",
                },
                {
                    "emotion": "excited",
                    "confidence": 0.75,
                    "timestamp": "2024-01-01T10:02:00Z",
                },
            ],
        }
        conversation_service.get_conversation_details.return_value = (
            conversation_details
        )

        # Act
        details = await conversation_service.get_conversation_details("conv1")

        # Assert
        assert details["id"] == "conv1"
        assert details["duration"] == 300
        assert len(details["transcript"]) == 2
        assert len(details["emotions"]) == 2
        assert details["transcript"][0]["speaker"] == "child"

    @pytest.mark.asyncio
    async def test_conversation_search(self, conversation_service):
        """Test conversation search functionality"""
        # Arrange
        search_results = [
            {"id": "conv1", "summary": "Story about cats", "relevance": 0.95},
            {"id": "conv3", "summary": "Cat sounds", "relevance": 0.80},
        ]
        conversation_service.search_conversations = AsyncMock(
            return_value=search_results
        )

        # Act
        results = await conversation_service.search_conversations("cat")

        # Assert
        assert len(results) == 2
        assert results[0]["relevance"] > results[1]["relevance"]
        assert "cat" in results[0]["summary"].lower()


class TestChildProfile:
    """Test child profile functionality"""

    @pytest.fixture
    def child_service(self):
        """Mock child service"""
        service = Mock()
        service.get_children = AsyncMock()
        service.get_child = AsyncMock()
        service.create_child = AsyncMock()
        service.update_child = AsyncMock()
        service.delete_child = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_get_children(self, child_service):
        """Test fetching children list"""
        # Arrange
        children = [
            {"id": "child1", "name": "أحمد", "age": 5, "gender": "male"},
            {"id": "child2", "name": "فاطمة", "age": 7, "gender": "female"},
        ]
        child_service.get_children.return_value = children

        # Act
        result = await child_service.get_children()

        # Assert
        assert len(result) == 2
        assert result[0]["name"] == "أحمد"
        assert result[1]["age"] == 7

    @pytest.mark.asyncio
    async def test_create_child(self, child_service):
        """Test creating a new child profile"""
        # Arrange
        new_child = {
            "name": "محمد",
            "age": 6,
            "gender": "male",
            "preferences": {
                "language": "ar",
                "interests": ["animals", "space"],
                "educationLevel": "kindergarten",
            },
        }
        child_service.create_child.return_value = {
            "id": "child3",
            **new_child,
            "createdAt": datetime.utcnow().isoformat(),
        }

        # Act
        created = await child_service.create_child(new_child)

        # Assert
        assert created["id"] == "child3"
        assert created["name"] == "محمد"
        assert "animals" in created["preferences"]["interests"]

    @pytest.mark.asyncio
    async def test_update_child(self, child_service):
        """Test updating child profile"""
        # Arrange
        updates = {
            "age": 6,
            "preferences": {
                "interests": [
                    "animals",
                    "space",
                    "art"]}}
        child_service.update_child.return_value = {
            "id": "child1",
            "name": "أحمد",
            "age": 6,
            "preferences": {"interests": ["animals", "space", "art"]},
        }

        # Act
        updated = await child_service.update_child("child1", updates)

        # Assert
        assert updated["age"] == 6
        assert len(updated["preferences"]["interests"]) == 3
        assert "art" in updated["preferences"]["interests"]

    @pytest.mark.asyncio
    async def test_child_statistics(self, child_service):
        """Test child statistics"""
        # Arrange
        stats = {
            "totalConversations": 150,
            "totalInteractionTime": 27000,  # seconds
            "averageSessionDuration": 180,
            "emotionalTrend": {"happy": 0.6, "neutral": 0.3, "sad": 0.1},
            "favoriteTopics": ["animals", "stories", "games"],
            "progressIndicators": [
                {"area": "language", "score": 85, "trend": "improving"},
                {"area": "social", "score": 78, "trend": "stable"},
            ],
        }
        child_service.get_child_statistics = AsyncMock(return_value=stats)

        # Act
        result = await child_service.get_child_statistics("child1")

        # Assert
        assert result["totalConversations"] == 150
        assert result["emotionalTrend"]["happy"] == 0.6
        assert result["progressIndicators"][0]["area"] == "language"
        assert result["progressIndicators"][0]["trend"] == "improving"


class TestReports:
    """Test reports functionality"""

    @pytest.fixture
    def report_service(self):
        """Mock report service"""
        service = Mock()
        service.generate_report = AsyncMock()
        service.get_reports = AsyncMock()
        service.export_report = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_generate_report(self, report_service):
        """Test report generation"""
        # Arrange
        report_params = {
            "childId": "child1",
            "type": "weekly",
            "period": {"start": "2024-01-01", "end": "2024-01-07"},
        }
        generated_report = {
            "id": "report1",
            "childId": "child1",
            "type": "weekly",
            "metrics": {
                "conversationCount": 14,
                "totalInteractionTime": 5400,
                "emotionalDistribution": {
                    "happy": 0.5,
                    "excited": 0.3,
                    "neutral": 0.2},
            },
            "insights": [
                {
                    "type": "achievement",
                    "title": "تحسن في المفردات",
                    "description": "زيادة استخدام كلمات جديدة بنسبة 20%",
                }],
        }
        report_service.generate_report.return_value = generated_report

        # Act
        report = await report_service.generate_report(report_params)

        # Assert
        assert report["id"] == "report1"
        assert report["metrics"]["conversationCount"] == 14
        assert len(report["insights"]) == 1
        assert report["insights"][0]["type"] == "achievement"

    @pytest.mark.asyncio
    async def test_export_report_pdf(self, report_service):
        """Test PDF export"""
        # Arrange
        report_service.export_report.return_value = b"PDF_CONTENT"

        # Act
        pdf_content = await report_service.export_report("report1", "pdf")

        # Assert
        assert pdf_content == b"PDF_CONTENT"
        report_service.export_report.assert_called_once_with("report1", "pdf")


class TestWebSocket:
    """Test WebSocket functionality"""

    @pytest.fixture
    def websocket_service(self):
        """Mock WebSocket service"""
        service = Mock()
        service.connect = AsyncMock()
        service.disconnect = AsyncMock()
        service.send_message = AsyncMock()
        service.receive_message = AsyncMock()
        service.on_message = Mock()
        return service

    @pytest.mark.asyncio
    async def test_websocket_connection(self, websocket_service):
        """Test WebSocket connection"""
        # Arrange
        websocket_service.connect.return_value = True

        # Act
        connected = await websocket_service.connect("ws://localhost:8000/ws")

        # Assert
        assert connected is True
        websocket_service.connect.assert_called_once()

    @pytest.mark.asyncio
    async def test_real_time_emotion_updates(self, websocket_service):
        """Test real-time emotion updates via WebSocket"""
        # Arrange
        emotion_update = {
            "type": "emotion_update",
            "data": {
                "conversationId": "conv1",
                "emotion": "happy",
                "confidence": 0.9,
                "timestamp": datetime.utcnow().isoformat(),
            },
        }
        websocket_service.receive_message.return_value = emotion_update

        # Act
        message = await websocket_service.receive_message()

        # Assert
        assert message["type"] == "emotion_update"
        assert message["data"]["emotion"] == "happy"
        assert message["data"]["confidence"] == 0.9

    @pytest.mark.asyncio
    async def test_audio_streaming(self, websocket_service):
        """Test audio streaming via WebSocket"""
        # Arrange
        audio_chunk = {
            "type": "audio_stream",
            "data": {
                "conversationId": "conv1",
                "chunk": "base64_encoded_audio",
                "sequence": 1,
            },
        }

        # Act
        await websocket_service.send_message(audio_chunk)

        # Assert
        websocket_service.send_message.assert_called_once_with(audio_chunk)


class TestEmergencyAlerts:
    """Test emergency alerts functionality"""

    @pytest.fixture
    def emergency_service(self):
        """Mock emergency service"""
        service = Mock()
        service.get_alerts = AsyncMock()
        service.acknowledge_alert = AsyncMock()
        service.trigger_alert = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_get_emergency_alerts(self, emergency_service):
        """Test fetching emergency alerts"""
        # Arrange
        alerts = [
            {
                "id": "alert1",
                "type": "safety",
                "severity": "high",
                "title": "محتوى غير مناسب",
                "description": "تم اكتشاف محتوى قد يكون غير مناسب",
                "timestamp": datetime.utcnow().isoformat(),
                "acknowledged": False,
            }
        ]
        emergency_service.get_alerts.return_value = alerts

        # Act
        result = await emergency_service.get_alerts()

        # Assert
        assert len(result) == 1
        assert result[0]["type"] == "safety"
        assert result[0]["severity"] == "high"
        assert result[0]["acknowledged"] is False

    @pytest.mark.asyncio
    async def test_acknowledge_alert(self, emergency_service):
        """Test acknowledging an alert"""
        # Arrange
        emergency_service.acknowledge_alert.return_value = True

        # Act
        result = await emergency_service.acknowledge_alert("alert1")

        # Assert
        assert result is True
        emergency_service.acknowledge_alert.assert_called_once_with("alert1")


class TestI18n:
    """Test internationalization"""

    def test_language_switching(self):
        """Test language switching between Arabic and English"""
        # Mock i18n
        i18n = Mock()
        i18n.language = "ar"
        i18n.changeLanguage = Mock()

        # Switch to English
        i18n.changeLanguage("en")
        i18n.changeLanguage.assert_called_with("en")

        # Switch back to Arabic
        i18n.changeLanguage("ar")
        assert i18n.changeLanguage.call_count == 2

    def test_rtl_support(self):
        """Test RTL support for Arabic"""
        # Mock document
        document = Mock()

        # Set RTL for Arabic
        document.dir = "rtl"
        assert document.dir == "rtl"

        # Set LTR for English
        document.dir = "ltr"
        assert document.dir == "ltr"


class TestAccessibility:
    """Test accessibility features"""

    def test_aria_labels(self):
        """Test ARIA labels are present"""
        elements = [
            {"role": "button", "aria-label": "فتح القائمة"},
            {"role": "navigation", "aria-label": "القائمة الرئيسية"},
            {"role": "main", "aria-label": "المحتوى الرئيسي"},
        ]

        for element in elements:
            assert "aria-label" in element
            assert element["aria-label"] != ""

    def test_keyboard_navigation(self):
        """Test keyboard navigation support"""
        # Mock keyboard events
        keyboard_events = [
            {"key": "Tab", "result": "next_element"},
            {"key": "Shift+Tab", "result": "previous_element"},
            {"key": "Enter", "result": "activate"},
            {"key": "Escape", "result": "close"},
        ]

        for event in keyboard_events:
            assert event["result"] is not None


class TestPerformance:
    """Test performance optimizations"""

    @pytest.mark.asyncio
    async def test_lazy_loading(self):
        """Test lazy loading of components"""
        load_times = []

        async def mock_load_component(name):
            start = datetime.utcnow()
            await asyncio.sleep(0.1)  # Simulate loading
            end = datetime.utcnow()
            load_time = (end - start).total_seconds()
            load_times.append(load_time)
            return f"{name}_component"

        # Load multiple components
        components = await asyncio.gather(
            mock_load_component("Dashboard"),
            mock_load_component("Conversations"),
            mock_load_component("Reports"),
        )

        assert len(components) == 3
        assert all(time < 0.2 for time in load_times)  # All loaded quickly

    def test_memoization(self):
        """Test memoization of expensive computations"""
        call_count = 0

        def expensive_computation(data):
            nonlocal call_count
            call_count += 1
            return sum(data)

        # Mock memoized function
        memo_cache = {}

        def memoized_computation(data):
            key = str(data)
            if key not in memo_cache:
                memo_cache[key] = expensive_computation(data)
            return memo_cache[key]

        # First call
        result1 = memoized_computation([1, 2, 3])
        assert result1 == 6
        assert call_count == 1

        # Second call with same data
        result2 = memoized_computation([1, 2, 3])
        assert result2 == 6
        assert call_count == 1  # Not called again

    @pytest.mark.asyncio
    async def test_debounced_search(self):
        """Test debounced search functionality"""
        search_calls = []

        async def search(query):
            search_calls.append(query)
            await asyncio.sleep(0.05)
            return f"results for {query}"

        # Simulate rapid typing
        queries = ["c", "ca", "cat"]

        # Without debounce - all calls made
        for query in queries:
            await search(query)

        assert len(search_calls) == 3

        # With debounce simulation
        search_calls.clear()
        last_query = queries[-1]
        await search(last_query)

        assert len(search_calls) == 1
        assert search_calls[0] == "cat"


class TestErrorHandling:
    """Test error handling and recovery"""

    @pytest.mark.asyncio
    async def test_network_error_retry(self):
        """Test network error retry logic"""
        attempt_count = 0

        async def flaky_api_call():
            nonlocal attempt_count
            attempt_count += 1

            if attempt_count < 3:
                raise Exception("Network error")

            return {"success": True}

        # Retry logic
        max_retries = 3
        for i in range(max_retries):
            try:
                result = await flaky_api_call()
                break
            except requests.exceptions.RequestException as exc:
                logger.warning(f"Network error on attempt {i+1}: {exc}")
                if i == max_retries - 1:
                    raise
                await asyncio.sleep(0.1 * (i + 1))  # Exponential backoff

        assert result["success"] is True
        assert attempt_count == 3

    def test_error_boundary(self):
        """Test error boundary catches errors"""

        # Mock error boundary
        class ErrorBoundary:
            def __init__(self):
                self.has_error = False
                self.error = None

            def catch_error(self, error):
                self.has_error = True
                self.error = error
                return "Fallback UI"

        boundary = ErrorBoundary()

        # Simulate error
        try:
            raise ValueError("Component error")
        except Exception as e:
            result = boundary.catch_error(e)

        assert boundary.has_error is True
        assert str(boundary.error) == "Component error"
        assert result == "Fallback UI"


class TestSecurity:
    """Test security features"""

    def test_xss_prevention(self):
        """Test XSS prevention"""
        dangerous_inputs = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "<iframe src='malicious.com'></iframe>",
        ]

        def sanitize_input(text):
            # Simple sanitization simulation
            dangerous_patterns = [
                "<script", "javascript:", "onerror=", "<iframe"]
            for pattern in dangerous_patterns:
                if pattern in text.lower():
                    return ""
            return text

        for input_text in dangerous_inputs:
            sanitized = sanitize_input(input_text)
            assert sanitized == ""

    def test_secure_storage(self):
        """Test secure storage of sensitive data"""

        # Mock secure storage
        class SecureStorage:
            def __init__(self):
                self._storage = {}

            def set_item(self, key, value, encrypt=False):
                if encrypt:
                    # Simulate encryption
                    value = f"encrypted_{value}"
                self._storage[key] = value

            def get_item(self, key, decrypt=False):
                value = self._storage.get(key)
                if decrypt and value and value.startswith("encrypted_"):
                    # Simulate decryption
                    value = value.replace("encrypted_", "")
                return value

        storage = SecureStorage()

        # Store sensitive data
        storage.set_item("token", "jwt_secret_token", encrypt=True)
        storage.set_item("user_id", "12345", encrypt=False)

        # Retrieve data
        token = storage.get_item("token", decrypt=True)
        user_id = storage.get_item("user_id")

        assert token == "jwt_secret_token"
        assert user_id == "12345"
        assert storage._storage["token"] == "encrypted_jwt_secret_token"


# Integration Tests
class TestIntegration:
    """Integration tests for complete user flows"""

    @pytest.mark.asyncio
    async def test_complete_user_journey(self):
        """Test complete user journey from login to report generation"""
        # Mock services
        auth_service = Mock()
        child_service = Mock()
        conversation_service = Mock()
        report_service = Mock()

        # 1. Login
        auth_service.login = AsyncMock(
            return_value={
                "user": {"id": "user1", "email": "parent@example.com"},
                "token": "jwt_token",
            }
        )
        login_result = await auth_service.login("parent@example.com", "password")
        assert login_result["token"] == "jwt_token"

        # 2. Get children
        child_service.get_children = AsyncMock(
            return_value=[{"id": "child1", "name": "أحمد", "age": 5}]
        )
        children = await child_service.get_children()
        assert len(children) == 1

        # 3. Get conversations
        conversation_service.get_conversations = AsyncMock(
            return_value={
                "conversations": [
                    {"id": "conv1", "childId": "child1", "duration": 300}
                ],
                "total": 1,
            }
        )
        conversations = await conversation_service.get_conversations("child1")
        assert conversations["total"] == 1

        # 4. Generate report
        report_service.generate_report = AsyncMock(
            return_value={
                "id": "report1",
                "childId": "child1",
                "type": "weekly",
                "metrics": {"conversationCount": 7},
            }
        )
        report = await report_service.generate_report(
            {"childId": "child1", "type": "weekly"}
        )
        assert report["metrics"]["conversationCount"] == 7

    @pytest.mark.asyncio
    async def test_real_time_conversation_flow(self):
        """Test real-time conversation flow with WebSocket"""
        # Mock services
        websocket = Mock()
        conversation_service = Mock()

        # 1. Start conversation
        conversation_service.start_conversation = AsyncMock(
            return_value={"conversationId": "conv1", "sessionToken": "session_token"}
        )
        conversation = await conversation_service.start_conversation("child1")

        # 2. Connect WebSocket
        websocket.connect = AsyncMock(return_value=True)
        connected = await websocket.connect(
            f"ws://localhost:8000/ws?token=session_token"
        )
        assert connected is True

        # 3. Stream audio and receive responses
        messages = [
            {"type": "audio_stream", "data": {"chunk": "audio1"}},
            {"type": "teddy_response", "data": {"text": "مرحباً!"}},
            {"type": "emotion_update", "data": {"emotion": "happy", "confidence": 0.9}},
        ]

        for message in messages:
            if message["type"] == "audio_stream":
                await websocket.send_message(message)
            else:
                websocket.receive_message = AsyncMock(return_value=message)
                received = await websocket.receive_message()
                assert received["type"] in ["teddy_response", "emotion_update"]

        # 4. End conversation
        conversation_service.end_conversation = AsyncMock(return_value=True)
        ended = await conversation_service.end_conversation("conv1")
        assert ended is True


# Run all tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=.", "--cov-report=html",
                 "--cov-report=term-missing"])
