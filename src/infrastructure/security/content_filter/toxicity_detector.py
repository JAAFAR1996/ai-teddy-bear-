"""
Toxicity detector for identifying harmful content.
"""
from typing import Any, Dict, List

from .models import RiskLevel, SafetyViolation


class ToxicityDetector:
    """
    Analyzes text content to detect various categories of toxicity, such as
    violence, hate speech, and profanity, and assesses a risk level.
    """

    def __init__(self):
        self.toxic_patterns = self._load_toxic_patterns()
        self.severity_weights = {
            "violence": 0.9,
            "hate_speech": 0.8,
            "sexual": 1.0,
            "drugs": 0.7,
            "profanity": 0.5,
            "personal_info": 1.0,
        }

    def _load_toxic_patterns(self) -> Dict[str, List[str]]:
        """
        Loads a predefined dictionary of toxic patterns. In a real application,
        this would come from a configuration file or a database.
        """
        return {
            "violence": ["عنف", "ضرب", "قتل", "إيذاء", "عدوان"],
            "hate_speech": ["كراهية", "تمييز", "عنصرية", "طائفية"],
            "sexual": ["جنس", "عري", "إثارة"],
            "drugs": ["مخدرات", "سجائر", "كحول", "مسكرات"],
            "profanity": ["سب", "شتم", "لعن", "كلام سيء"],
            "personal_info": ["رقم هاتف", "عنوان", "اسم عائلة", "مدرسة"],
        }

    async def analyze_toxicity(self, content: str, child_age: int) -> Dict[str, Any]:
        """Analyzes the toxicity of a given string content based on the child's age."""
        content_lower = content.lower()
        detected_categories = {}
        violations = []

        for category, patterns in self.toxic_patterns.items():
            detected_patterns = [p for p in patterns if p in content_lower]
            if not detected_patterns:
                continue

            age_multiplier = self._get_age_sensitivity_multiplier(
                child_age, category)
            category_score = min(1.0, len(
                detected_patterns) * self.severity_weights.get(category, 0.5) * age_multiplier)

            detected_categories[category] = {
                "score": category_score,
                "patterns": detected_patterns,
            }
            violations.append(SafetyViolation(
                violation_type=category,
                severity=self._calculate_severity_from_score(category_score),
                description=f"Detected toxic content in category: {category}",
                content_excerpt=content[:100],
                requires_parent_notification=category_score > 0.7,
            ))

        total_score = max([cat["score"] for cat in detected_categories.values(
        )]) if detected_categories else 0.0

        return {
            "toxicity_score": total_score,
            "detected_categories": detected_categories,
            "violations": violations,
            "is_toxic": total_score > 0.3,
        }

    def _get_age_sensitivity_multiplier(self, age: int, category: str) -> float:
        """Calculates an age-based sensitivity multiplier for a given toxicity category."""
        multipliers = {
            "violence": {range(3, 7): 2.0, range(7, 11): 1.5},
            "hate_speech": {range(3, 7): 2.0, range(7, 11): 1.8},
            "sexual": {range(3, 7): 3.0, range(7, 11): 2.5},
            "drugs": {range(3, 7): 2.0, range(7, 11): 1.5},
            "profanity": {range(3, 7): 1.5, range(7, 11): 1.2},
        }
        category_multipliers = multipliers.get(category, {})
        for age_range, multiplier in category_multipliers.items():
            if age in age_range:
                return multiplier
        return 1.0

    def _calculate_severity_from_score(self, score: float) -> RiskLevel:
        """Calculates the risk level based on a numerical toxicity score."""
        if score >= 0.8:
            return RiskLevel.CRITICAL
        if score >= 0.6:
            return RiskLevel.HIGH_RISK
        if score >= 0.4:
            return RiskLevel.MEDIUM_RISK
        if score > 0:
            return RiskLevel.LOW_RISK
        return RiskLevel.SAFE
