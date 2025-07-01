"""
Advanced Educational Value Evaluator for Child Content
"""

import asyncio
import re
from dataclasses import dataclass
from typing import Dict, List, Set

from .models import EducationalValueResult


class EducationalValueEvaluator:
    """Evaluate educational value and learning potential of content"""

    def __init__(self):
        self.learning_frameworks = self._initialize_learning_frameworks()
        self.age_curricula = self._load_age_curricula()
        self.skill_taxonomies = self._create_skill_taxonomies()

    def _initialize_learning_frameworks(self) -> Dict:
        """Initialize educational frameworks and standards"""
        return {
            "cognitive_domains": {
                "remember": ["recall", "list", "name", "identify", "what is"],
                "understand": ["explain", "describe", "why", "how", "what does"],
                "apply": ["use", "solve", "show", "demonstrate", "practice"],
                "analyze": ["compare", "contrast", "examine", "break down"],
                "evaluate": ["judge", "assess", "critique", "decide"],
                "create": ["design", "build", "make", "invent", "imagine"],
            },
            "learning_styles": {
                "visual": ["see", "look", "picture", "image", "color", "shape"],
                "auditory": ["hear", "listen", "sound", "music", "song", "rhyme"],
                "kinesthetic": ["move", "touch", "feel", "play", "action", "hands-on"],
            },
            "multiple_intelligences": {
                "linguistic": ["words", "story", "read", "write", "speak"],
                "logical": ["number", "count", "math", "pattern", "logic"],
                "spatial": ["space", "shape", "direction", "map", "picture"],
                "musical": ["music", "rhythm", "song", "sound", "beat"],
                "bodily": ["move", "dance", "exercise", "physical", "sport"],
                "interpersonal": ["friend", "team", "group", "share", "help"],
                "intrapersonal": ["think", "feel", "self", "reflect", "understand"],
                "naturalistic": ["nature", "animal", "plant", "environment", "outdoor"],
            },
        }

    def _load_age_curricula(self) -> Dict:
        """Load age-appropriate learning objectives"""
        return {
            3: {
                "core_skills": ["colors", "shapes", "numbers_1_10", "letters", "animals"],
                "social_skills": ["sharing", "taking_turns", "please_thank_you"],
                "motor_skills": ["walking", "running", "jumping", "holding_objects"],
                "language": ["simple_words", "basic_sentences", "following_instructions"],
            },
            4: {
                "core_skills": ["counting_to_20", "alphabet", "rhyming", "basic_addition"],
                "social_skills": ["friendship", "cooperation", "empathy", "manners"],
                "motor_skills": ["drawing", "cutting", "building", "balance"],
                "language": ["storytelling", "questions", "expressing_feelings"],
            },
            5: {
                "core_skills": ["reading_readiness", "writing_letters", "counting_to_50", "patterns"],
                "social_skills": ["problem_solving", "conflict_resolution", "leadership"],
                "motor_skills": ["fine_motor", "sports_basics", "coordination"],
                "language": ["complex_sentences", "vocabulary_expansion", "listening_skills"],
            },
            6: {
                "core_skills": ["reading", "writing", "math_basics", "science_concepts"],
                "social_skills": ["teamwork", "responsibility", "respect", "diversity"],
                "motor_skills": ["sports", "arts_crafts", "technology_basics"],
                "language": ["reading_comprehension", "creative_writing", "presentations"],
            },
        }

    def _create_skill_taxonomies(self) -> Dict:
        """Create taxonomies for skill development"""
        return {
            "cognitive_skills": {
                "memory": ["remember", "recall", "memorize", "review"],
                "attention": ["focus", "concentrate", "listen", "observe"],
                "problem_solving": ["solve", "figure out", "find solution", "overcome"],
                "critical_thinking": ["analyze", "evaluate", "judge", "reason"],
                "creativity": ["create", "imagine", "invent", "design", "art"],
            },
            "social_skills": {
                "communication": ["talk", "speak", "express", "share", "tell"],
                "cooperation": ["work together", "team", "help", "collaborate"],
                "empathy": ["understand feelings", "care", "kind", "compassion"],
                "leadership": ["lead", "guide", "responsible", "in charge"],
            },
            "emotional_skills": {
                "self_awareness": ["feelings", "emotions", "self", "identity"],
                "self_regulation": ["control", "calm", "manage", "patience"],
                "motivation": ["goal", "try", "effort", "persistence"],
                "social_awareness": ["others", "community", "respect", "differences"],
            },
        }

    async def evaluate_educational_value(
        self, content: str, child_age: int, conversation_context: List[str] = None
    ) -> EducationalValueResult:
        """Evaluate educational value of content"""

        # Analyze learning categories
        learning_categories = self._identify_learning_categories(content)

        # Calculate educational score
        educational_score = self._calculate_educational_score(content, child_age, learning_categories)

        # Assess cognitive complexity
        cognitive_complexity = self._assess_cognitive_complexity(content, child_age)

        # Identify skill development opportunities
        skill_development = self._identify_skill_development(content)

        # Check age alignment
        age_alignment = self._check_age_alignment(content, child_age)

        return EducationalValueResult(
            educational_score=educational_score,
            learning_categories=learning_categories,
            cognitive_complexity=cognitive_complexity,
            skill_development=skill_development,
            age_alignment=age_alignment,
        )

    def _identify_learning_categories(self, content: str) -> List[str]:
        """Identify learning categories present in content"""
        content_lower = content.lower()
        identified_categories = []

        # Check multiple intelligences
        for intelligence, keywords in self.learning_frameworks["multiple_intelligences"].items():
            if any(keyword in content_lower for keyword in keywords):
                identified_categories.append(f"intelligence_{intelligence}")

        # Check cognitive domains
        for domain, keywords in self.learning_frameworks["cognitive_domains"].items():
            if any(keyword in content_lower for keyword in keywords):
                identified_categories.append(f"cognitive_{domain}")

        # Check learning styles
        for style, keywords in self.learning_frameworks["learning_styles"].items():
            if any(keyword in content_lower for keyword in keywords):
                identified_categories.append(f"style_{style}")

        return list(set(identified_categories))

    def _calculate_educational_score(self, content: str, child_age: int, learning_categories: List[str]) -> float:
        """Calculate overall educational value score"""

        base_score = 0.0
        content_lower = content.lower()

        # Score based on educational keywords
        educational_keywords = [
            "learn",
            "study",
            "teach",
            "show",
            "explain",
            "discover",
            "explore",
            "practice",
            "try",
            "experiment",
            "question",
        ]

        educational_content = sum(1 for keyword in educational_keywords if keyword in content_lower)
        base_score += min(0.4, educational_content * 0.1)

        # Score based on learning categories
        category_score = len(learning_categories) * 0.05
        base_score += min(0.3, category_score)

        # Score based on age-appropriate curriculum alignment
        curriculum_score = self._assess_curriculum_alignment(content, child_age)
        base_score += curriculum_score * 0.3

        # Bonus for interactive elements
        interactive_keywords = ["what", "how", "why", "can you", "try to", "let's"]
        interactive_content = sum(1 for keyword in interactive_keywords if keyword in content_lower)
        base_score += min(0.2, interactive_content * 0.05)

        return min(1.0, base_score)

    def _assess_cognitive_complexity(self, content: str, child_age: int) -> float:
        """Assess cognitive complexity of content"""
        content_lower = content.lower()
        complexity_indicators = {
            "simple": ["what", "who", "see", "look", "is", "are", "simple"],
            "moderate": ["how", "why", "because", "explain", "compare"],
            "complex": ["analyze", "evaluate", "create", "design", "solve"],
            "advanced": ["synthesize", "critique", "research", "hypothesis"],
        }

        complexity_scores = {}
        for level, keywords in complexity_indicators.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            complexity_scores[level] = score

        # Determine dominant complexity level
        if complexity_scores:
            max_complexity = max(complexity_scores.items(), key=lambda x: x[1])

            # Map complexity to numerical score
            complexity_mapping = {"simple": 0.25, "moderate": 0.5, "complex": 0.75, "advanced": 1.0}

            return complexity_mapping.get(max_complexity[0], 0.25)

        return 0.25

    def _identify_skill_development(self, content: str) -> List[str]:
        """Identify skills that can be developed through content"""
        content_lower = content.lower()
        skills_identified = []

        for skill_category, skill_types in self.skill_taxonomies.items():
            for skill_type, keywords in skill_types.items():
                if any(keyword in content_lower for keyword in keywords):
                    skills_identified.append(f"{skill_category}_{skill_type}")

        return list(set(skills_identified))

    def _check_age_alignment(self, content: str, child_age: int) -> float:
        """Check how well content aligns with age-appropriate learning"""
        age_curriculum = self.age_curricula.get(child_age, self.age_curricula[6])
        content_lower = content.lower()

        alignment_score = 0.0
        total_categories = 0

        for category, skills in age_curriculum.items():
            total_categories += 1
            category_match = 0

            for skill in skills:
                if skill.replace("_", " ") in content_lower:
                    category_match += 1

            if category_match > 0:
                alignment_score += min(1.0, category_match / len(skills))

        return alignment_score / total_categories if total_categories > 0 else 0.0

    def _assess_curriculum_alignment(self, content: str, child_age: int) -> float:
        """Assess alignment with educational curriculum"""
        age_curriculum = self.age_curricula.get(child_age, self.age_curricula[6])
        content_lower = content.lower()

        total_skills = sum(len(skills) for skills in age_curriculum.values())
        matched_skills = 0

        for category, skills in age_curriculum.items():
            for skill in skills:
                skill_keywords = skill.replace("_", " ").split()
                if all(keyword in content_lower for keyword in skill_keywords):
                    matched_skills += 1

        return matched_skills / total_skills if total_skills > 0 else 0.0

    def suggest_educational_enhancements(self, content: str, child_age: int, current_score: float) -> List[str]:
        """Suggest ways to enhance educational value"""
        suggestions = []
        content_lower = content.lower()

        # Suggest missing learning categories
        age_curriculum = self.age_curricula.get(child_age, self.age_curricula[6])

        for category, skills in age_curriculum.items():
            category_present = any(skill.replace("_", " ") in content_lower for skill in skills)

            if not category_present:
                suggestions.append(f"Consider adding {category} elements")

        # Suggest cognitive engagement improvements
        if "what" not in content_lower and "how" not in content_lower:
            suggestions.append("Add questions to increase engagement")

        # Suggest interactive elements
        interactive_keywords = ["try", "practice", "do", "make", "create"]
        if not any(keyword in content_lower for keyword in interactive_keywords):
            suggestions.append("Add hands-on or interactive elements")

        # Suggest age-appropriate challenges
        if current_score < 0.5:
            suggestions.append("Increase educational content and learning objectives")

        return suggestions

    def analyze_learning_progression(self, conversation_history: List[str], child_age: int) -> Dict[str, any]:
        """Analyze learning progression through conversation"""

        learning_timeline = []
        skill_development_over_time = {}

        for i, content in enumerate(conversation_history):
            result = asyncio.run(self.evaluate_educational_value(content, child_age))

            learning_timeline.append(
                {
                    "turn": i,
                    "educational_score": result.educational_score,
                    "learning_categories": result.learning_categories,
                    "skills": result.skill_development,
                }
            )

            # Track skill development
            for skill in result.skill_development:
                if skill not in skill_development_over_time:
                    skill_development_over_time[skill] = []
                skill_development_over_time[skill].append(i)

        # Analyze progression trends
        progression_trend = self._calculate_learning_trend(learning_timeline)
        skill_mastery = self._assess_skill_mastery(skill_development_over_time)

        return {
            "learning_timeline": learning_timeline,
            "progression_trend": progression_trend,
            "skill_mastery": skill_mastery,
            "recommendations": self._generate_learning_recommendations(progression_trend, skill_mastery, child_age),
        }

    def _calculate_learning_trend(self, timeline: List[Dict]) -> str:
        """Calculate learning progression trend"""
        if len(timeline) < 3:
            return "insufficient_data"

        scores = [turn["educational_score"] for turn in timeline]

        # Simple trend analysis
        if scores[-1] > scores[0] + 0.1:
            return "improving"
        elif scores[-1] < scores[0] - 0.1:
            return "declining"
        else:
            return "stable"

    def _assess_skill_mastery(self, skill_timeline: Dict[str, List[int]]) -> Dict[str, str]:
        """Assess skill mastery levels"""
        mastery_levels = {}

        for skill, occurrences in skill_timeline.items():
            if len(occurrences) >= 5:
                mastery_levels[skill] = "mastered"
            elif len(occurrences) >= 3:
                mastery_levels[skill] = "developing"
            elif len(occurrences) >= 1:
                mastery_levels[skill] = "introduced"
            else:
                mastery_levels[skill] = "not_covered"

        return mastery_levels

    def _generate_learning_recommendations(
        self, progression_trend: str, skill_mastery: Dict[str, str], child_age: int
    ) -> List[str]:
        """Generate learning recommendations"""
        recommendations = []

        if progression_trend == "declining":
            recommendations.append("Educational content decreasing - add more learning activities")

        # Check for skill gaps
        expected_skills = self.age_curricula.get(child_age, {})
        for category, skills in expected_skills.items():
            covered_skills = [skill for skill in skill_mastery.keys() if skill.endswith(category)]

            if len(covered_skills) < len(skills) * 0.5:
                recommendations.append(f"Focus more on {category} development")

        # Suggest skill advancement
        mastered_skills = [skill for skill, level in skill_mastery.items() if level == "mastered"]

        if len(mastered_skills) > 3:
            recommendations.append("Child showing mastery - consider advancing to more complex topics")

        return recommendations
