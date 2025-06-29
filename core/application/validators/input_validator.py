# Input validator
class InputValidator:
    """Validator for user input."""
    @staticmethod
    def validate(text: str) -> bool:
        return bool(text and text.strip()) 