# Base use case class
class BaseUseCase:
    """Base class for all use cases."""
    def __init__(self):
        pass

    def execute(self, *args, **kwargs):
        raise NotImplementedError("Use case must implement execute method.") 