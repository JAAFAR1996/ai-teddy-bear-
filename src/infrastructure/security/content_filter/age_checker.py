"""
Age-appropriateness checker for content.
"""
from typing import Any, Dict, List


class AgeAppropriatenessChecker:
    """
    Analyzes content to determine its appropriateness for a specific child's age,
    considering vocabulary, concepts, and emotional complexity.
    """

    def __init__(self):
        # In a real application, these would be loaded from a more sophisticated source
        self.inappropriate_concepts = [
            "موت", "مرض خطير", "حادث", "طلاق", "فقر", "حروب", "سياسة", "اقتصاد معقد"
        ]
        self.complex_emotions = [
            "اكتئاب", "قلق شديد", "خوف مرضي", "غضب شديد", "يأس", "إحباط عميق", "صدمة نفسية"
        ]

    async def check_age_appropriateness(self, content: str, child_age: int) -> Dict[str, Any]:
        """Performs a comprehensive check of the content's age appropriateness."""
        vocab_score = self._analyze_vocabulary_complexity(content, child_age)
        concept_score = self._analyze_concept_appropriateness(content)
        emotional_score = self._analyze_emotional_complexity(
            content, child_age)

        overall_score = (vocab_score + concept_score + emotional_score) / 3.0

        return {
            "is_age_appropriate": overall_score > 0.6,
            "appropriateness_score": overall_score,
            "details": {
                "vocabulary_score": vocab_score,
                "concept_score": concept_score,
                "emotional_score": emotional_score,
            },
            "recommendations": self._generate_age_recommendations(
                vocab_score, concept_score, emotional_score, child_age
            ),
        }

    def _analyze_vocabulary_complexity(self, content: str, age: int) -> float:
        """Analyzes vocabulary complexity based on average word length."""
        words = content.split()
        if not words:
            return 1.0

        avg_word_length = sum(len(w) for w in words) / len(words)

        # Age-based thresholds for average word length
        age_thresholds = {range(3, 6): 4, range(6, 9): 6, range(9, 13): 8}
        limit = next((l for r, l in age_thresholds.items() if age in r), 10)

        if avg_word_length <= limit:
            return 1.0
        if avg_word_length <= limit * 1.5:
            return 0.7
        return 0.3

    def _analyze_concept_appropriateness(self, content: str) -> float:
        """Analyzes the appropriateness of concepts mentioned in the content."""
        content_lower = content.lower()
        inappropriate_count = sum(
            1 for concept in self.inappropriate_concepts if concept in content_lower)

        if inappropriate_count == 0:
            return 1.0
        if inappropriate_count <= 2:
            return 0.5
        return 0.1

    def _analyze_emotional_complexity(self, content: str, age: int) -> float:
        """Analyzes the emotional complexity of the content based on the child's age."""
        content_lower = content.lower()
        complex_emotion_count = sum(
            1 for emotion in self.complex_emotions if emotion in content_lower)

        # Age-based tolerance for complex emotions
        age_tolerances = {range(0, 6): 0, range(6, 10): 1}
        tolerance = next((t for r, t in age_tolerances.items() if age in r), 2)

        if complex_emotion_count <= tolerance:
            return 1.0
        return max(0.2, 1.0 - (complex_emotion_count - tolerance) * 0.4)

    def _generate_age_recommendations(
        self, vocab_score: float, concept_score: float, emotional_score: float, age: int
    ) -> List[str]:
        """Generates recommendations for improving age appropriateness."""
        recommendations = []
        if vocab_score < 0.7:
            recommendations.append(
                "Simplify vocabulary and use shorter words.")
        if concept_score < 0.7:
            recommendations.append("Avoid complex or sensitive topics.")
        if emotional_score < 0.7:
            recommendations.append("Focus on basic, positive emotions.")
        if age < 6 and not recommendations:
            recommendations.append(
                "Keep topics concrete and simple for young children.")
        return recommendations
