"""
Moderation Rule Engine
Manages and evaluates content moderation rules
"""

import re
from typing import Dict, List, Tuple
import logging

from .moderation_types import ContentCategory, ModerationRule, ModerationSeverity


class RuleEngine:
    """Advanced rule engine for content moderation"""

    def __init__(self):
        self.rules: Dict[str, ModerationRule] = {}
        self.compiled_patterns: Dict[str, re.Pattern] = {}
        self.logger = logging.getLogger(self.__class__.__name__)
        self._load_default_rules()

    def _load_default_rules(self) -> None:
        """Load default moderation rules"""
        default_rules = [
            ModerationRule(
                id="personal_info_1",
                name="Personal Information Detection",
                description="Detects personal information like phone numbers, addresses",
                pattern=r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b|\b\d{5,}\b",
                category=ContentCategory.PERSONAL_INFO,
                severity=ModerationSeverity.HIGH,
                is_regex=True,
            ),
            ModerationRule(
                id="violence_1",
                name="Violence Keywords",
                description="Detects violent language",
                keywords=["kill", "murder", "hurt", "harm", "attack", "fight"],
                category=ContentCategory.VIOLENCE,
                severity=ModerationSeverity.HIGH,
                context_required=True,
            ),
            ModerationRule(
                id="scary_content_1",
                name="Scary Content for Young Children",
                description="Content that might scare young children",
                keywords=["monster", "ghost", "scary", "nightmare", "demon"],
                category=ContentCategory.SCARY_CONTENT,
                severity=ModerationSeverity.LOW,
                age_range=(3, 8),
            ),
            ModerationRule(
                id="bullying_1",
                name="Bullying Detection",
                description="Detects bullying language",
                keywords=["stupid", "dumb", "loser",
                          "hate you", "nobody likes"],
                category=ContentCategory.BULLYING,
                severity=ModerationSeverity.MEDIUM,
            ),
            ModerationRule(
                id="drugs_1",
                name="Drug References",
                description="Detects drug-related content",
                keywords=["drugs", "cocaine", "marijuana",
                          "pills", "high", "stoned"],
                category=ContentCategory.DRUGS,
                severity=ModerationSeverity.HIGH,
            ),
            ModerationRule(
                id="weapons_1",
                name="Weapons References",
                description="Detects weapon-related content",
                keywords=["gun", "knife", "bomb", "weapon", "shoot"],
                category=ContentCategory.WEAPONS,
                severity=ModerationSeverity.HIGH,
                context_required=True,
            ),
            ModerationRule(
                id="self_harm_1",
                name="Self Harm Detection",
                description="Detects self-harm content",
                keywords=["suicide", "cut myself",
                          "kill myself", "end my life"],
                category=ContentCategory.SELF_HARM,
                severity=ModerationSeverity.CRITICAL,
            ),
            ModerationRule(
                id="sexual_content_1",
                name="Sexual Content",
                description="Detects sexual content",
                keywords=["sex", "naked", "porn"],
                category=ContentCategory.SEXUAL,
                severity=ModerationSeverity.HIGH,
            ),
            ModerationRule(
                id="hate_speech_1",
                name="Hate Speech",
                description="Detects hate speech",
                keywords=["hate", "racist", "discriminate"],
                category=ContentCategory.HATE_SPEECH,
                severity=ModerationSeverity.HIGH,
                context_required=True,
            ),
            ModerationRule(
                id="email_pattern",
                name="Email Detection",
                description="Detects email addresses",
                pattern=r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
                category=ContentCategory.PERSONAL_INFO,
                severity=ModerationSeverity.MEDIUM,
                is_regex=True,
            ),
        ]

        for rule in default_rules:
            self.add_rule(rule)

    def add_rule(self, rule: ModerationRule) -> None:
        """Add a moderation rule"""
        self.rules[rule.id] = rule
        if rule.pattern and rule.is_regex:
            self.compiled_patterns[rule.id] = re.compile(
                rule.pattern, re.IGNORECASE)

    def remove_rule(self, rule_id: str) -> None:
        """Remove a moderation rule"""
        if rule_id in self.rules:
            del self.rules[rule_id]
            if rule_id in self.compiled_patterns:
                del self.compiled_patterns[rule_id]

    def update_rule(self, rule_id: str, updates: Dict) -> bool:
        """Update an existing rule"""
        if rule_id not in self.rules:
            return False

        rule = self.rules[rule_id]
        for key, value in updates.items():
            if hasattr(rule, key):
                setattr(rule, key, value)

        # Recompile pattern if updated
        if rule.pattern and rule.is_regex:
            self.compiled_patterns[rule_id] = re.compile(
                rule.pattern, re.IGNORECASE)

        return True

    def get_rule(self, rule_id: str) -> ModerationRule:
        """Get a specific rule"""
        return self.rules.get(rule_id)

    def get_all_rules(self) -> Dict[str, ModerationRule]:
        """Get all rules"""
        return self.rules.copy()

    def get_rules_by_category(self, category: ContentCategory) -> List[ModerationRule]:
        """Get rules by category"""
        return [rule for rule in self.rules.values() if rule.category == category]

    def get_rules_by_severity(self, severity: ModerationSeverity) -> List[ModerationRule]:
        """Get rules by severity"""
        return [rule for rule in self.rules.values() if rule.severity == severity]

    async def evaluate(
        self, text: str, age: int = 10, language: str = "en"
    ) -> List[Tuple[ModerationRule, float]]:
        """Evaluate text against all rules"""
        matched_rules = []

        for rule_id, rule in self.rules.items():
            if not rule.enabled:
                continue

            # Check age range
            if not (rule.age_range[0] <= age <= rule.age_range[1]):
                continue

            # Check language
            if language not in rule.languages:
                continue

            confidence = 0.0

            # Check regex pattern
            if rule.pattern and rule.is_regex and rule_id in self.compiled_patterns:
                if self.compiled_patterns[rule_id].search(text):
                    confidence = 0.9

            # Check keywords
            if rule.keywords:
                text_lower = text.lower()
                matches = sum(
                    1 for keyword in rule.keywords if keyword.lower() in text_lower
                )
                if matches > 0:
                    confidence = max(confidence, min(matches * 0.3, 0.9))

            if confidence > 0:
                matched_rules.append((rule, confidence))

        return matched_rules

    def export_rules(self) -> List[Dict]:
        """Export all rules as dictionaries"""
        return [
            {
                "id": rule.id,
                "name": rule.name,
                "description": rule.description,
                "pattern": rule.pattern,
                "keywords": rule.keywords,
                "category": rule.category.value,
                "severity": rule.severity.value,
                "age_range": rule.age_range,
                "languages": rule.languages,
                "is_regex": rule.is_regex,
                "context_required": rule.context_required,
                "enabled": rule.enabled,
                "parent_override": rule.parent_override,
                "action": rule.action,
            }
            for rule in self.rules.values()
        ]

    def import_rules(self, rules_data: List[Dict]) -> int:
        """Import rules from dictionaries"""
        imported_count = 0

        for rule_data in rules_data:
            try:
                # Convert string values back to enums
                rule_data["category"] = ContentCategory(rule_data["category"])
                rule_data["severity"] = ModerationSeverity(
                    rule_data["severity"])

                rule = ModerationRule(**rule_data)
                self.add_rule(rule)
                imported_count += 1
            except (KeyError, TypeError, ValueError) as exc:
                self.logger.warning(
                    f"Skipping invalid rule data: {rule_data}. Error: {exc}")
                continue

        return imported_count
