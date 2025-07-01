import uuid
from typing import Any, Dict, List

import pytest


class ChildProfile:
    """Child aggregate for testing"""

    def __init__(self, name: str, age: int, parent_id: str, language_preference: str = "en"):
        self.id = str(uuid.uuid4())
        self.name = name
        self.age = age
        self.parent_id = parent_id
        self.language_preference = language_preference
        self.active_sessions: List[str] = []
        self._domain_events: List[Dict[str, Any]] = []

    def can_start_session(self) -> bool:
        """Check if child can start a new session"""
        return len(self.active_sessions) == 0

    def start_session(self, session_id: str) -> None:
        """Start a new session"""
        if not self.can_start_session():
            raise ValueError("Child already has an active session")

        self.active_sessions.append(session_id)
        self._domain_events.append({"type": "SessionStarted", "child_id": self.id, "session_id": session_id})


class TestChildAggregate:
    """Test child aggregate business logic"""

    def test_child_creation(self):
        """Test creating a child profile"""
        child = ChildProfile(name="Ahmed", age=7, parent_id="parent-123", language_preference="ar")

        assert child.name == "Ahmed"
        assert child.age == 7
        assert child.language_preference == "ar"
        assert len(child.active_sessions) == 0

    def test_can_start_session(self):
        """Test session start business rule"""
        child = ChildProfile(name="Fatima", age=6, parent_id="parent-456")

        # Should be able to start first session
        assert child.can_start_session() is True

        # Start a session
        child.start_session("session-1")

        # Should not be able to start another
        assert child.can_start_session() is False

    def test_domain_events(self):
        """Test domain event generation"""
        child = ChildProfile(name="Omar", age=8, parent_id="parent-789")

        # Start session should generate event
        child.start_session("session-1")

        assert len(child._domain_events) == 1
        event = child._domain_events[0]
        assert event["type"] == "SessionStarted"
        assert event["child_id"] == child.id
        assert event["session_id"] == "session-1"
