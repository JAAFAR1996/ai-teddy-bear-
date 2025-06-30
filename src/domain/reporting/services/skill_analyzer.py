"""
Skill Analysis Domain Service
Analyzes skill development and learning patterns
"""

import logging
from typing import List, Dict, Any
from collections import Counter

from ..models.report_models import InteractionAnalysis, SkillAnalysis


class SkillAnalyzer:
    """Domain service for skill analysis"""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def analyze_skills_practiced(self, interactions: List[InteractionAnalysis]) -> SkillAnalysis:
        """Analyze skills practiced during interactions"""
        try:
            if not interactions:
                return SkillAnalysis(
                    skills_practiced={},
                    new_skills_learned=[],
                    improvement_areas=[],
                    mastery_level={}
                )

            # Count skill usage
            skill_counts = {}
            all_skills = set()
            
            for interaction in interactions:
                for skill in interaction.skills_used:
                    skill_counts[skill] = skill_counts.get(skill, 0) + 1
                    all_skills.add(skill)

            # Identify new skills (skills used less frequently)
            new_skills = [
                skill for skill, count in skill_counts.items()
                if count <= 2  # Used 2 times or less
            ]

            # Identify improvement areas (skills used infrequently)
            improvement_areas = [
                skill for skill, count in skill_counts.items()
                if count <= 3 and skill not in new_skills
            ]

            # Calculate mastery levels
            max_count = max(skill_counts.values()) if skill_counts else 1
            mastery_level = {
                skill: min(count / max_count, 1.0)
                for skill, count in skill_counts.items()
            }

            return SkillAnalysis(
                skills_practiced=skill_counts,
                new_skills_learned=new_skills,
                improvement_areas=improvement_areas,
                mastery_level=mastery_level
            )

        except Exception as e:
            self.logger.error(f"Skills analysis error: {e}")
            return SkillAnalysis(
                skills_practiced={},
                new_skills_learned=[],
                improvement_areas=[],
                mastery_level={}
            )

    def identify_achievements(self, interactions: List[InteractionAnalysis]) -> List[str]:
        """Identify learning achievements based on skill usage"""
        try:
            achievements = []
            
            if not interactions:
                return achievements
            
            # Analyze skill diversity
            all_skills = set()
            for interaction in interactions:
                all_skills.update(interaction.skills_used)
            
            skill_diversity = len(all_skills)
            if skill_diversity >= 8:
                achievements.append(f"تنوع مهاري ممتاز - استخدم {skill_diversity} مهارات مختلفة")
            elif skill_diversity >= 5:
                achievements.append(f"تنوع مهاري جيد - استخدم {skill_diversity} مهارات")
            
            # Skill consistency analysis
            skill_counts = Counter()
            for interaction in interactions:
                skill_counts.update(interaction.skills_used)
            
            # Check for consistent skill practice
            consistent_skills = [
                skill for skill, count in skill_counts.items()
                if count >= len(interactions) * 0.3  # Used in 30%+ of interactions
            ]
            
            if consistent_skills:
                achievements.append(f"ممارسة مستمرة للمهارات: {', '.join(consistent_skills[:3])}")
            
            # Advanced skill usage
            advanced_skills = [
                "problem_solving", "critical_thinking", "creativity", 
                "complex_reasoning", "analytical_thinking"
            ]
            
            used_advanced_skills = [
                skill for skill in advanced_skills
                if any(skill in interaction.skills_used for interaction in interactions)
            ]
            
            if used_advanced_skills:
                achievements.append(f"استخدام مهارات متقدمة: {', '.join(used_advanced_skills)}")
            
            # Skill progression (detecting improvement over time)
            if len(interactions) >= 5:
                early_skills = set()
                late_skills = set()
                
                mid_point = len(interactions) // 2
                
                for interaction in interactions[:mid_point]:
                    early_skills.update(interaction.skills_used)
                
                for interaction in interactions[mid_point:]:
                    late_skills.update(interaction.skills_used)
                
                new_skills_gained = late_skills - early_skills
                if new_skills_gained:
                    achievements.append(f"تطوير مهارات جديدة: {len(new_skills_gained)} مهارات جديدة")
            
            return achievements

        except Exception as e:
            self.logger.error(f"Achievement identification error: {e}")
            return []

    def generate_activity_recommendations(self, interactions: List[InteractionAnalysis]) -> List[str]:
        """Generate activity recommendations based on skill analysis"""
        try:
            recommendations = []
            
            if not interactions:
                return ["أنشطة تفاعلية بسيطة لبناء الثقة"]
            
            # Analyze current skill usage
            skill_counts = Counter()
            for interaction in interactions:
                skill_counts.update(interaction.skills_used)
            
            # Identify underused skills
            all_possible_skills = {
                "counting", "reading", "writing", "drawing", "singing",
                "problem_solving", "memory_games", "pattern_recognition",
                "storytelling", "role_playing", "creative_thinking",
                "social_skills", "emotional_expression", "listening"
            }
            
            used_skills = set(skill_counts.keys())
            underused_skills = all_possible_skills - used_skills
            
            # Recommend activities for underused skills
            skill_activities = {
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
                "listening": "ألعاب الاستماع والتركيز"
            }
            
            # Add recommendations for underused skills
            for skill in list(underused_skills)[:5]:  # Top 5 underused skills
                if skill in skill_activities:
                    recommendations.append(skill_activities[skill])
            
            # Recommend strengthening frequently used skills
            top_skills = [skill for skill, _ in skill_counts.most_common(3)]
            for skill in top_skills:
                if skill in skill_activities:
                    recommendations.append(f"تطوير المهارة القوية: {skill_activities[skill]}")
            
            # Age-appropriate recommendations based on interaction complexity
            avg_topics_per_interaction = sum(
                len(interaction.topics_discussed) for interaction in interactions
            ) / len(interactions)
            
            if avg_topics_per_interaction < 2:
                recommendations.append("أنشطة بسيطة ومباشرة لبناء الثقة")
            elif avg_topics_per_interaction > 4:
                recommendations.append("أنشطة معقدة ومتقدمة لتحدي القدرات")
            
            return recommendations[:8]  # Limit to 8 recommendations

        except Exception as e:
            self.logger.error(f"Activity recommendations generation error: {e}")
            return ["أنشطة تعليمية متنوعة مناسبة للعمر"]

    def calculate_skill_progression_rate(self, interactions: List[InteractionAnalysis]) -> float:
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
            
            for interaction in interactions[third:2*third]:
                period2_skills.update(interaction.skills_used)
            
            for interaction in interactions[2*third:]:
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

    def identify_skill_gaps(self, interactions: List[InteractionAnalysis], age: int) -> List[str]:
        """Identify skill gaps based on age-appropriate expectations"""
        try:
            gaps = []
            
            # Age-appropriate skill expectations
            age_expectations = {
                3: ["counting", "simple_words", "basic_colors", "listening"],
                4: ["counting", "simple_words", "basic_colors", "listening", "drawing", "sharing"],
                5: ["counting", "reading", "writing", "problem_solving", "memory_games", "social_skills"],
                6: ["reading", "writing", "problem_solving", "memory_games", "social_skills", "creative_thinking"],
                7: ["reading", "writing", "problem_solving", "critical_thinking", "advanced_counting", "storytelling"]
            }
            
            # Get expected skills for age
            expected_skills = set()
            for expected_age in range(3, min(age + 1, 8)):
                expected_skills.update(age_expectations.get(expected_age, []))
            
            # Get actually used skills
            used_skills = set()
            for interaction in interactions:
                used_skills.update(interaction.skills_used)
            
            # Identify gaps
            missing_skills = expected_skills - used_skills
            
            for skill in missing_skills:
                gaps.append(f"مهارة مفقودة: {skill}")
            
            return gaps[:5]  # Return top 5 gaps
            
        except Exception as e:
            self.logger.error(f"Skill gap identification error: {e}")
            return [] 