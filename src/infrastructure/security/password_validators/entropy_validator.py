import re
import math
from typing import Optional

from .base import BasePasswordValidator


class EntropyValidator(BasePasswordValidator):
    """Validates the password's entropy."""

    def __init__(self, min_entropy: float):
        self.min_entropy = min_entropy
        super().__init__(
            f"Password is too predictable. Minimum entropy: {min_entropy} bits")

    def validate(self, password: str, user_info: Optional[dict] = None) -> Optional[str]:
        entropy = self._calculate_entropy(password)
        if entropy < self.min_entropy:
            return f"Password is too predictable (entropy: {entropy:.1f} bits, minimum: {self.min_entropy})"
        return None

    def _calculate_entropy(self, password: str) -> float:
        """Calculate password entropy in bits"""
        charset_size = 0
        if re.search(r"[a-z]", password):
            charset_size += 26
        if re.search(r"[A-Z]", password):
            charset_size += 26
        if re.search(r"\d", password):
            charset_size += 10
        if re.search(r"[^a-zA-Z0-9]", password):
            charset_size += 32
        if charset_size == 0:
            return 0
        return len(password) * math.log2(charset_size)
