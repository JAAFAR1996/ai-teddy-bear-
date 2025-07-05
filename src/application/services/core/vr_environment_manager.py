#!/usr/bin/env python3
"""
🌐 مدير بيئات الواقع الافتراضي
مسؤول عن إدارة بيئات VR فقط
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class VREnvironment:
    """بيئة واقع افتراضي"""
    environment_id: str
    name: str
    theme: str  # space, underwater, forest, fantasy, educational
    description: str
    immersion_level: str  # low, medium, high
    movement_type: str  # stationary, limited, full_movement
    educational_content: Dict = None
    interactive_elements: List[Dict] = None
    safety_boundaries: Dict = None
    comfort_settings: Dict = None

    def __post_init__(self):
        if self.educational_content is None:
            self.educational_content = {}
        if self.interactive_elements is None:
            self.interactive_elements = []
        if self.safety_boundaries is None:
            self.safety_boundaries = {"max_session_time": 15, "break_intervals": 5}
        if self.comfort_settings is None:
            self.comfort_settings = {
                "motion_sickness_prevention": True,
                "eye_strain_protection": True,
            }


class VREnvironmentManager:
    """مدير بيئات الواقع الافتراضي - مسؤولية واحدة فقط"""

    def __init__(self):
        self.vr_environments: Dict[str, VREnvironment] = {}
        self._initialize_default_environments()

    def _initialize_default_environments(self) -> None:
        """تهيئة البيئات الافتراضية"""
        educational_vr = [
            VREnvironment(
                environment_id="vr_space",
                name="رحلة إلى الفضاء",
                theme="space",
                description="استكشاف النظام الشمسي والكواكب",
                immersion_level="medium",
                movement_type="limited",
                educational_content={
                    "planets": ["معلومات عن الكواكب", "حجم الكواكب", "المسافات"],
                    "solar_system": ["الشمس", "القمر", "النجوم"],
                    "space_exploration": ["المركبات الفضائية", "رواد الفضاء"],
                },
                interactive_elements=[
                    {"type": "planet_selection", "action": "show_planet_info"},
                    {"type": "spacecraft_control", "action": "navigate_space"},
                    {"type": "quiz_mode", "action": "test_knowledge"},
                ],
            ),
            VREnvironment(
                environment_id="vr_underwater",
                name="عالم المحيط السحري",
                theme="underwater",
                description="استكشاف أعماق المحيط والحياة البحرية",
                immersion_level="high",
                movement_type="limited",
                educational_content={
                    "sea_creatures": ["الأسماك", "المرجان", "الحيتان"],
                    "ocean_layers": ["السطح", "الأعماق", "القاع"],
                    "ecosystem": ["السلسلة الغذائية", "التوازن البيئي"],
                },
                interactive_elements=[
                    {"type": "creature_interaction", "action": "learn_about_creature"},
                    {"type": "diving_simulation", "action": "explore_depths"},
                    {"type": "conservation_game", "action": "protect_ocean"},
                ],
            ),
        ]

        for env in educational_vr:
            self.vr_environments[env.environment_id] = env

    def get_environment_by_id(self, environment_id: str) -> VREnvironment:
        """الحصول على بيئة محددة"""
        return self.vr_environments.get(environment_id)

    def get_available_environments(
        self, child_age: int = None, theme: str = None
    ) -> List[VREnvironment]:
        """الحصول على البيئات المتاحة مع تصفية"""
        environments = list(self.vr_environments.values())

        # تصفية حسب العمر (VR مناسب للأطفال 6+ سنوات)
        if child_age:
            if child_age < 6:
                return []  # VR غير مناسب للأطفال الصغار
            elif child_age < 10:
                environments = [
                    env for env in environments
                    if env.immersion_level in ["low", "medium"]
                ]

        if theme:
            environments = [
                env for env in environments 
                if env.theme == theme
            ]

        return environments

    def add_custom_environment(self, environment: VREnvironment) -> bool:
        """إضافة بيئة مخصصة"""
        if environment.environment_id not in self.vr_environments:
            self.vr_environments[environment.environment_id] = environment
            return True
        return False

    def adapt_for_age(self, environment: VREnvironment, child_age: int) -> Dict:
        """تكييف إعدادات البيئة حسب العمر"""
        adapted = {
            "max_duration": environment.safety_boundaries["max_session_time"],
            "break_intervals": environment.safety_boundaries["break_intervals"],
            "comfort_settings": environment.comfort_settings.copy(),
        }

        if child_age < 8:
            adapted["max_duration"] = min(adapted["max_duration"], 10)
            adapted["break_intervals"] = 3
            adapted["comfort_settings"]["motion_reduction"] = True
            adapted["comfort_settings"]["simplified_interface"] = True
        elif child_age < 12:
            adapted["max_duration"] = min(adapted["max_duration"], 15)
            adapted["break_intervals"] = 5

        return adapted 