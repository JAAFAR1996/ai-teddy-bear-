from typing import Dict, List, Any, Optional

# Observer pattern implementation
class Observer:
    def update(self, data) -> Any:
        raise NotImplementedError

class Observable:
    def __init__(self):
        self._observers = []

    def add_observer(self, observer) -> Any:
        self._observers.append(observer)

    def notify_observers(self, data) -> Any:
        for observer in self._observers:
            observer.update(data) 