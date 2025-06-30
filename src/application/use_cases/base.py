from typing import Dict, List, Any, Optional

# Base use case class
class BaseUseCase:
    """Base class for all use cases."""
    def __init__(self):
        pass

    def execute(self, *args, **kwargs) -> Any:
        raise NotImplementedError("Use case must implement execute method.") 