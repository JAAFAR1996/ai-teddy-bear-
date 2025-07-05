import re
from typing import Optional

from .base import BasePasswordValidator


class UppercaseValidator(BasePasswordValidator):
    """Validates for at least one uppercase letter."""

    def __init__(self):
        super().__init__("Password must contain at least one uppercase letter")

    def validate(self, password: str, user_info: Optional[dict] = None) -> Optional[str]:
        if not re.search(r"[A-Z]", password):
            return self.message
        return None


class LowercaseValidator(BasePasswordValidator):
    """Validates for at least one lowercase letter."""

    def __init__(self):
        super().__init__("Password must contain at least one lowercase letter")

    def validate(self, password: str, user_info: Optional[dict] = None) -> Optional[str]:
        if not re.search(r"[a-z]", password):
            return self.message
        return None
