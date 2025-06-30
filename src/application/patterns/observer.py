from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod

# Observer pattern implementation
class Observer(ABC):
    """Abstract observer class"""
    @abstractmethod
    def update(self, subject: 'Subject') -> None:
        """Update method called when subject state changes"""
        pass

class Subject:
    """Subject class that notifies observers"""
    def __init__(self):
        self._observers: List[Observer] = []
        self._state: Any = None

    def attach(self, observer: Observer) -> None:
        """Attach an observer to the subject"""
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        """Detach an observer from the subject"""
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self) -> None:
        """Notify all observers of state changes"""
        for observer in self._observers:
            observer.update(self)
    
    def get_state(self) -> Any:
        """Get the current state"""
        return self._state
    
    def set_state(self, state: Any) -> None:
        """Set the state and notify observers"""
        self._state = state
        self.notify() 