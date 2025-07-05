from abc import ABC, abstractmethod
from typing import Any


# Strategy pattern implementation
class Strategy(ABC):
    """Abstract base strategy class"""

    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """Execute the strategy - must be implemented by subclasses"""
        pass


class Context:
    """Context class that uses a strategy"""

    def __init__(self, strategy: Strategy):
        self._strategy = strategy

    def set_strategy(self, strategy: Strategy) -> None:
        """Change the strategy at runtime"""
        self._strategy = strategy

    def execute_strategy(self, *args, **kwargs) -> Any:
        """Execute the current strategy"""
        return self._strategy.execute(*args, **kwargs)
