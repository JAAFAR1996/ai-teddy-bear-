from typing import List


class ContentModerator:
    """Service for moderating content and filtering inappropriate material."""

    def __init__(self, blocked_words: List[str] = None):
        self.blocked_words = blocked_words or ["violence", "scary_content", "adult_themes", "badword1", "badword2"]

    def is_appropriate(self, text: str) -> bool:
        """Check if the text is appropriate for children."""
        lowered = text.lower()
        return not any(word in lowered for word in self.blocked_words)

    def add_blocked_word(str) -> None:
        if word not in self.blocked_words:
            self.blocked_words.append(word)

    def remove_blocked_word(str) -> None:
        if word in self.blocked_words:
            self.blocked_words.remove(word)
