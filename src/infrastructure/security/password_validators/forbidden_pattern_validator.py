import re
from typing import Optional, List

from .base import BasePasswordValidator


class ForbiddenPatternValidator(BasePasswordValidator):
    """Validates that the password does not contain forbidden patterns."""

    def __init__(self, forbidden_patterns: List[str]):
        self.forbidden_patterns = forbidden_patterns
        super().__init__("Password contains a forbidden pattern")

    def validate(self, password: str, user_info: Optional[dict] = None) -> Optional[str]:
        if any(re.search(pattern, password.lower()) for pattern in self.forbidden_patterns):
            return self.message
        return None
