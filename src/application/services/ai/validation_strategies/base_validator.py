from abc import ABC, abstractmethod
from typing import List

from .....domain.entities import Child


class ValidationStrategy(ABC):
    """Abstract base class for a validation strategy."""

    @abstractmethod
    def validate(self, child: Child) -> List[str]:
        """
        Performs a validation check on the Child aggregate.

        Args:
            child: The Child aggregate to validate.

        Returns:
            A list of validation error messages. An empty list indicates
            the validation passed.
        """
        pass
