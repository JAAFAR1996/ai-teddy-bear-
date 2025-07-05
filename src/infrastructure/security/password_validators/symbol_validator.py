import re
from typing import Optional

from .base import BasePasswordValidator


class SymbolValidator(BasePasswordValidator):
    """Validates for at least one special character."""

    def __init__(self):
        super().__init__("Password must contain at least one special character")

    def validate(self, password: str, user_info: Optional[dict] = None) -> Optional[str]:
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return self.message
        return None
