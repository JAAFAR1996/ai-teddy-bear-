"""
Skill Analysis Domain Service
Analyzes skill development and learning patterns
"""

import logging
from collections import Counter
from typing import Dict, List

from ..models.report_models import InteractionAnalysis, SkillAnalysis


class SkillAnalyzer:
    """Domain service for skill analysis"""

    ALL_POSSIBLE_SKILLS = {
        "counting",
        "reading",
        "writing",
        "drawing",
        "singing",
        "problem_solving",
        "memory_games",
        "pattern_recognition",
        "storytelling",
        "role_playing",
        "creative_thinking",
        "social_skills",
        "emotional_expression",
        "listening",
    }

    SKILL_ACTIVITIES = {
        "counting": "ألعاب الأرقام والعد التفاعلي",
        "reading": "قراءة القصص المصورة البسيطة",
        "writing": "أنشطة الرسم والكتابة الحرة",
        "drawing": "الرسم والتلوين الإبداعي",
        "singing": "تعلم الأغاني والموسيقى",
        "problem_solving": "ألعاب الألغاز البسيطة",
        "memory_games": "ألعاب الذاكرة والتذكر",
        "pattern_recognition": "ألعاب الأنماط والأشكال",
        "storytelling": "إنشاء القصص الخيالية",
        "role_playing": "ألعاب تمثيل الأدوار",
        "creative_thinking": "أنشطة الإبداع والخيال",
        "social_skills": "ألعاب جماعية وتفاعلية",
        "emotional_expression": "أنشطة التعبير عن المشاعر",
        "listening": "ألعاب الاستماع والتركيز",
    }

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def _count_skill_usage(self, interactions: List[InteractionAnalysis]) -> Counter:
        """Counts the usage of each skill across all interactions."""
        skill_counts = Counter()
        for interaction in interactions:
            skill_counts.update(interaction.skills_used)
        return skill_counts

    def _identify_new_skills(self, skill_counts: Counter) -> List[str]:
        """Identifies new skills based on low usage count."""
        return [skill for skill, count in skill_counts.items() if count <= 2]

    def _identify_improvement_areas(
        self, skill_counts: Counter, new_skills: List[str]
    ) -> List[str]:
        """Identifies skills needing improvement."""
        return [
            skill
            for skill, count in skill_counts.items()
            if count <= 3 and skill not in new_skills
        ]

    def _calculate_mastery_levels(self, skill_counts: Counter) -> Dict[str, float]:
        """Calculates mastery level for each skill based on usage frequency."""
        max_count = max(skill_counts.values()) if skill_counts else 1
        return {
            skill: min(count / max_count, 1.0) for skill, count in skill_counts.items()
        }

    def analyze_skills_practiced(
        self, interactions: List[InteractionAnalysis]
    ) -> SkillAnalysis:
        """Analyze skills practiced during interactions"""
        try:
            if not interactions:
                return SkillAnalysis(
                    skills_practiced={},
                    new_skills_learned=[],
                    improvement_areas=[],
                    mastery_level={},
                )

            skill_counts = self._count_skill_usage(interactions)
            new_skills = self._identify_new_skills(skill_counts)
            improvement_areas = self._identify_improvement_areas(
                skill_counts, new_skills
            )
            mastery_level = self._calculate_mastery_levels(skill_counts)

            return SkillAnalysis(
                skills_practiced=dict(skill_counts),
                new_skills_learned=new_skills,
                improvement_areas=improvement_areas,
                mastery_level=mastery_level,
            )

        except Exception as e:
            self.logger.error(f"Skills analysis error: {e}")
            return SkillAnalysis(
                skills_practiced={},
                new_skills_learned=[],
                improvement_areas=[],
                mastery_level={},
            )

    def _check_skill_diversity(
        self, interactions: List[InteractionAnalysis]
    ) -> List[str]:
        """Checks for skill diversity achievements."""
        all_skills = {
            skill for interaction in interactions for skill in interaction.skills_used
        }
        skill_diversity = len(all_skills)
        if skill_diversity >= 8:
            return [f"تنوع مهاري ممتاز - استخدم {skill_diversity} مهارات مختلفة"]
        elif skill_diversity >= 5:
            return [f"تنوع مهاري جيد - استخدم {skill_diversity} مهارات"]
        return []

    def _check_skill_consistency(
        self, interactions: List[InteractionAnalysis]
    ) -> List[str]:
        """Checks for consistent skill practice."""
        skill_counts = self._count_skill_usage(interactions)
        consistent_skills = [
            skill
            for skill, count in skill_counts.items()
            if count >= len(interactions) * 0.3
        ]
        if consistent_skills:
            return [f"ممارسة مستمرة للمهارات: {', '.join(consistent_skills[:3])}"]
        return []

    def _check_advanced_skill_usage(
        self, interactions: List[InteractionAnalysis]
    ) -> List[str]:
        """Checks for the usage of advanced skills."""
        advanced_skills = [
            "problem_solving",
            "critical_thinking",
            "creativity",
            "complex_reasoning",
            "analytical_thinking",
        ]
        used_advanced_skills = {
            skill
            for interaction in interactions
            for skill in interaction.skills_used
            if skill in advanced_skills
        }
        if used_advanced_skills:
            return [f"استخدام مهارات متقدمة: {', '.join(used_advanced_skills)}"]
        return []

    def _check_skill_progression(
        self, interactions: List[InteractionAnalysis]
    ) -> List[str]:
        """Checks for skill progression over time."""
        if len(interactions) < 5:
            return []

        mid_point = len(interactions) // 2
        early_skills = {
            skill
            for interaction in interactions[:mid_point]
            for skill in interaction.skills_used
        }
        late_skills = {
            skill
            for interaction in interactions[mid_point:]
            for skill in interaction.skills_used
        }

        new_skills_gained = late_skills - early_skills
        if new_skills_gained:
            return [f"تطوير مهارات جديدة: {len(new_skills_gained)} مهارات جديدة"]
        return []

    def identify_achievements(
        self, interactions: List[InteractionAnalysis]
    ) -> List[str]:
        """Identify learning achievements based on skill usage"""
        try:
            if not interactions:
                return []

            achievements = []

            check_functions = [
                self._check_skill_diversity,
                self._check_skill_consistency,
                self._check_advanced_skill_usage,
                self._check_skill_progression,
            ]

            for check_func in check_functions:
                achievements.extend(check_func(interactions))

            return achievements

        except Exception as e:
            self.logger.error(f"Achievement identification error: {e}")
            return []

    def _recommend_for_underused_skills(self, used_skills: set) -> List[str]:
        """Recommends activities for underused skills."""
        underused_skills = self.ALL_POSSIBLE_SKILLS - used_skills
        return [
            self.SKILL_ACTIVITIES[skill]
            for skill in list(underused_skills)[:5]
            if skill in self.SKILL_ACTIVITIES
        ]

    def _recommend_to_strengthen_top_skills(self, skill_counts: Counter) -> List[str]:
        """Recommends activities to strengthen the most used skills."""
        top_skills = [skill for skill, _ in skill_counts.most_common(3)]
        return [
            f"تطوير المهارة القوية: {self.SKILL_ACTIVITIES[skill]}"
            for skill in top_skills
            if skill in self.SKILL_ACTIVITIES
        ]

    def _recommend_age_appropriate_activities(
        self, interactions: List[InteractionAnalysis]
    ) -> List[str]:
        """Recommends age-appropriate activities based on interaction complexity."""
        avg_topics = sum(len(i.topics_discussed) for i in interactions) / len(
            interactions
        )
        if avg_topics < 2:
            return ["أنشطة بسيطة ومباشرة لبناء الثقة"]
        elif avg_topics > 4:
            return ["أنشطة معقدة ومتقدمة لتحدي القدرات"]
        return []

    def generate_activity_recommendations(
        self, interactions: List[InteractionAnalysis]
    ) -> List[str]:
        """Generate activity recommendations based on skill analysis"""
        try:
            if not interactions:
                return ["أنشطة تفاعلية بسيطة لبناء الثقة"]

            skill_counts = self._count_skill_usage(interactions)

            recommendations = []
            recommendations.extend(
                self._recommend_for_underused_skills(set(skill_counts.keys()))
            )
            recommendations.extend(
                self._recommend_to_strengthen_top_skills(skill_counts)
            )
            recommendations.extend(
                self._recommend_age_appropriate_activities(interactions)
            )

            return recommendations[:8]

        except Exception as e:
            self.logger.error(f"Activity recommendations generation error: {e}")
            return ["أنشطة تعليمية متنوعة مناسبة للعمر"]

    def calculate_skill_progression_rate(
        self, interactions: List[InteractionAnalysis]
    ) -> float:
        """Calculate rate of skill progression over time"""
        try:
            if len(interactions) < 3:
                return 0.0

            # Divide interactions into time periods
            third = len(interactions) // 3

            period1_skills = set()
            period2_skills = set()
            period3_skills = set()

            for interaction in interactions[:third]:
                period1_skills.update(interaction.skills_used)

            for interaction in interactions[third : 2 * third]:
                period2_skills.update(interaction.skills_used)

            for interaction in interactions[2 * third :]:
                period3_skills.update(interaction.skills_used)

            # Calculate progression
            initial_skills = len(period1_skills)
            final_skills = len(period3_skills)

            if initial_skills == 0:
                return 1.0 if final_skills > 0 else 0.0

            progression_rate = (final_skills - initial_skills) / initial_skills
            return max(0.0, min(2.0, progression_rate))  # Cap between 0 and 2

        except Exception as e:
            self.logger.error(f"Skill progression calculation error: {e}")
            return 0.0

    def _get_expected_skills_by_age(self, age: int) -> set:
        """Returns the set of expected skills for a given age."""
        if age <= 3:
            return {
                "counting",
                "drawing",
                "singing",
                "emotional_expression",
                "listening",
            }
        elif age <= 5:
            return {
                "reading",
                "writing",
                "memory_games",
                "social_skills",
                "pattern_recognition",
            }
        else:  # 6+
            return {
                "problem_solving",
                "storytelling",
                "creative_thinking",
                "role_playing",
            }

    def identify_skill_gaps(
        self, interactions: List[InteractionAnalysis], age: int
    ) -> List[str]:
        """Identify skill gaps based on age and interactions"""
        try:
            if not interactions:
                return ["لا توجد بيانات كافية لتحديد الفجوات"]

            practiced_skills = {
                skill
                for interaction in interactions
                for skill in interaction.skills_used
            }
            expected_skills = self._get_expected_skills_by_age(age)

            missing_skills = expected_skills - practiced_skills

            if not missing_skills:
                return ["لا توجد فجوات مهارية واضحة حالياً، أداء جيد!"]

            return [
                f"فجوة في مهارة: {self.SKILL_ACTIVITIES.get(skill, skill)}"
                for skill in missing_skills
            ]

        except Exception as e:
            self.logger.error(f"Skill gap identification error: {e}")
            return ["خطأ في تحديد الفجوات المهارية"]
