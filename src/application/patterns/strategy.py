# Strategy pattern implementation
class Strategy:
    def execute(self, *args, **kwargs):
        raise NotImplementedError

class Context:
    def __init__(self, strategy: Strategy):
        self._strategy = strategy

    def set_strategy(self, strategy: Strategy):
        self._strategy = strategy

    def execute_strategy(self, *args, **kwargs):
        return self._strategy.execute(*args, **kwargs) 