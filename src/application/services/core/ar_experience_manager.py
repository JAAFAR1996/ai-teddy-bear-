#!/usr/bin/env python3
"""
🎯 مدير تجارب الواقع المعزز
مسؤول عن إدارة تجارب AR فقط
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class ARExperience:
    """تجربة واقع معزز"""
    experience_id: str
    name: str
    description: str
    category: str  # educational, entertainment, interactive_story, game
    age_range: Tuple[int, int]  # (min_age, max_age)
    duration_minutes: int
    difficulty_level: str  # easy, medium, hard
    required_objects: List[str] = None
    learning_objectives: List[str] = None
    safety_requirements: List[str] = None
    ar_models: Dict[str, str] = None
    interaction_points: List[Dict] = None

    def __post_init__(self):
        if self.required_objects is None:
            self.required_objects = []
        if self.learning_objectives is None:
            self.learning_objectives = []
        if self.safety_requirements is None:
            self.safety_requirements = []
        if self.ar_models is None:
            self.ar_models = {}
        if self.interaction_points is None:
            self.interaction_points = []


class ARExperienceManager:
    """مدير تجارب الواقع المعزز - مسؤولية واحدة فقط"""

    def __init__(self):
        self.ar_experiences: Dict[str, ARExperience] = {}
        self._initialize_default_experiences()

    def _initialize_default_experiences(self) -> None:
        """تهيئة التجارب الافتراضية"""
        educational_ar = [
            ARExperience(
                experience_id="ar_alphabet",
                name="رحلة الحروف المعززة",
                description="تعلم الحروف العربية بالواقع المعزز",
                category="educational",
                age_range=(3, 7),
                duration_minutes=10,
                difficulty_level="easy",
                required_objects=["book", "table"],
                learning_objectives=[
                    "تعلم الحروف",
                    "تحسين النطق",
                    "تطوير الذاكرة البصرية",
                ],
                safety_requirements=["مساحة آمنة 2x2 متر", "إشراف بالغ"],
                ar_models={
                    "letters": "3d_arabic_letters.obj",
                    "animations": "letter_animations.fbx",
                },
                interaction_points=[
                    {"type": "touch", "object": "letter", "action": "play_sound"},
                    {"type": "voice", "trigger": "say_letter", "response": "show_animation"},
                ],
            ),
            ARExperience(
                experience_id="ar_animals",
                name="حديقة الحيوانات المعززة",
                description="استكشاف الحيوانات بالواقع المعزز",
                category="educational",
                age_range=(4, 10),
                duration_minutes=15,
                difficulty_level="medium",
                required_objects=["floor_space"],
                learning_objectives=[
                    "تعلم أسماء الحيوانات",
                    "فهم بيئات الحيوانات",
                    "تطوير التفكير العلمي",
                ],
                safety_requirements=["مساحة آمنة 3x3 متر", "تجنب الحركة السريعة"],
                ar_models={
                    "animals": "3d_animals_pack.obj",
                    "environments": "habitats.fbx",
                },
                interaction_points=[
                    {"type": "gesture", "object": "animal", "action": "show_info"},
                    {"type": "voice", "trigger": "animal_sound", "response": "play_animal_sound"},
                ],
            ),
        ]

        for exp in educational_ar:
            self.ar_experiences[exp.experience_id] = exp

    def get_experience_by_id(self, experience_id: str) -> ARExperience:
        """الحصول على تجربة محددة"""
        return self.ar_experiences.get(experience_id)

    def get_available_experiences(
        self, child_age: int = None, difficulty: str = None
    ) -> List[ARExperience]:
        """الحصول على التجارب المتاحة مع تصفية"""
        experiences = list(self.ar_experiences.values())

        if child_age:
            experiences = [
                exp for exp in experiences
                if exp.age_range[0] <= child_age <= exp.age_range[1]
            ]

        if difficulty:
            experiences = [
                exp for exp in experiences 
                if exp.difficulty_level == difficulty
            ]

        return experiences

    def add_custom_experience(self, experience: ARExperience) -> bool:
        """إضافة تجربة مخصصة"""
        if experience.experience_id not in self.ar_experiences:
            self.ar_experiences[experience.experience_id] = experience
            return True
        return False

    def get_setup_instructions(self, experience: ARExperience) -> List[str]:
        """تعليمات إعداد التجربة"""
        instructions = [
            "تأكد من وجود إضاءة جيدة في المكان",
            "امسك الجهاز بثبات على مسافة مناسبة",
            "تأكد من وجود مساحة كافية للحركة الآمنة",
        ]

        if experience.required_objects:
            instructions.append(
                f"ضع الأجسام التالية في مجال الرؤية: {', '.join(experience.required_objects)}"
            )

        if "مساحة" in str(experience.safety_requirements):
            instructions.append("تأكد من خلو المساحة من العوائق")

        return instructions 