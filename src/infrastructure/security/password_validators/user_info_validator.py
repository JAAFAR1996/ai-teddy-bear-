from typing import Optional

from .base import BasePasswordValidator


class UserInfoValidator(BasePasswordValidator):
    """Validates that the password does not contain user information."""

    def __init__(self):
        super().__init__("Password cannot contain user information")

    def validate(self, password: str, user_info: Optional[dict] = None) -> Optional[str]:
        if not user_info:
            return None

        for key, value in user_info.items():
            if value and len(value) > 3 and value.lower() in password.lower():
                return f"Password cannot contain {key}"
        return None
