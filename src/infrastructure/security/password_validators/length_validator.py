from typing import Optional

from .base import BasePasswordValidator


class LengthValidator(BasePasswordValidator):
    """Validates the password length."""

    def __init__(self, min_length: int, max_length: int):
        self.min_length = min_length
        self.max_length = max_length
        super().__init__(
            f"Password must be between {min_length} and {max_length} characters long"
        )

    def validate(self, password: str, user_info: Optional[dict] = None) -> Optional[str]:
        if not (self.min_length <= len(password) <= self.max_length):
            return self.message
        return None
