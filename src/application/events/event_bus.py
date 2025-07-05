from typing import Any


# Event bus for application events
class EventBus:
    """Simple event bus for publishing and subscribing to events."""

    def __init__(self):
        self._subscribers = {}

    def subscribe(self, event_type, handler) -> Any:
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)

    def publish(self, event_type, data) -> Any:
        for handler in self._subscribers.get(event_type, []):
            handler(data)
