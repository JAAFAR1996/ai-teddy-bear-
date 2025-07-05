import re
from typing import Optional

from .base import BasePasswordValidator


class DigitValidator(BasePasswordValidator):
    """Validates for at least one digit."""

    def __init__(self):
        super().__init__("Password must contain at least one digit")

    def validate(self, password: str, user_info: Optional[dict] = None) -> Optional[str]:
        if not re.search(r"\d", password):
            return self.message
        return None
