from abc import ABC, abstractmethod
from typing import Optional


class BasePasswordValidator(ABC):
    """Abstract base class for a password validator."""

    def __init__(self, message: str):
        self.message = message

    @abstractmethod
    def validate(self, password: str, user_info: Optional[dict] = None) -> Optional[str]:
        """
        Validates the password.

        Args:
            password: The password to validate.
            user_info: Optional user information to use in validation.

        Returns:
            An error message string if validation fails, otherwise None.
        """
        pass
