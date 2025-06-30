from typing import Dict, List, Any, Optional

# Strategy pattern implementation
class Strategy:
    def execute(self, *args, **kwargs) -> Any:
        raise NotImplementedError

class Context:
    def __init__(self, strategy: Strategy):
        self._strategy = strategy

    def set_strategy(self, strategy -> Any: Strategy) -> Any:
        self._strategy = strategy

    def execute_strategy(self, *args, **kwargs) -> Any:
        return self._strategy.execute(*args, **kwargs) 