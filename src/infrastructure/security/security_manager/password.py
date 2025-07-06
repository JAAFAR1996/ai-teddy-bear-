"""
Advanced password security management.
"""
import logging
import re
import secrets
import string
from typing import Dict, List, Optional, Tuple

import bcrypt

from ..password_validators import (
    DigitValidator,
    EntropyValidator,
    ForbiddenPatternValidator,
    LengthValidator,
    LowercaseValidator,
    SymbolValidator,
    UppercaseValidator,
    UserInfoValidator,
)

logger = logging.getLogger(__name__)


class PasswordSecurity:
    """
    Manages all aspects of password security, including hashing, verification,
    and validation against a set of configurable policies.
    """

    def __init__(self):
        self.min_length = 12
        self.max_length = 128
        self.min_entropy = 60
        self.forbidden_patterns = ["password",
                                   "123456", "qwerty", "admin", "teddy"]
        self.validators = self._initialize_validators()

    def _initialize_validators(self) -> list:
        """Initializes the list of password validation policies."""
        return [
            LengthValidator(self.min_length, self.max_length),
            UppercaseValidator(),
            LowercaseValidator(),
            DigitValidator(),
            SymbolValidator(),
            ForbiddenPatternValidator(self.forbidden_patterns),
            EntropyValidator(self.min_entropy),
            UserInfoValidator(),
        ]

    def hash_password(self, password: str) -> str:
        """Hashes a password using bcrypt with a high work factor."""
        if not password:
            raise ValueError("Password cannot be empty.")
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verifies a plaintext password against a bcrypt hash."""
        if not password or not hashed_password:
            return False
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))

    def validate_password(self, password: str, user_info: Optional[Dict[str, str]] = None) -> Tuple[bool, List[str]]:
        """
        Validates a password against all configured security policies.

        Returns a tuple containing a boolean (is_valid) and a list of error messages.
        """
        errors = [
            error for validator in self.validators
            if (error := validator.validate(password, user_info))
        ]
        if not errors:
            return True, []
        return False, errors

    def generate_secure_password(self, length: int = 16) -> str:
        """
        Generates a cryptographically secure password that complies with the
        configured validation policies.
        """
        # Ensure length is within configured bounds
        length = max(self.min_length, min(length, self.max_length))

        # Build a character set that guarantees compliance with basic policies
        char_set = string.ascii_lowercase + string.ascii_uppercase + \
            string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"

        while True:
            password = "".join(secrets.choice(char_set) for _ in range(length))
            # Ensure the generated password meets all criteria
            is_valid, errors = self.validate_password(password)
            if is_valid:
                return password
            else:
                logger.debug(
                    f"Generated password failed validation, retrying. Errors: {errors}")
