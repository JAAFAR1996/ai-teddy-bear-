from typing import Dict, List
from .models import StoryTheme


def load_story_templates() -> Dict[str, Dict]:
    return {
        StoryTheme.ADVENTURE.value: {"structure": "introduction → challenge → journey → resolution"},
        StoryTheme.FRIENDSHIP.value: {"structure": "meeting → conflict → understanding → bond"},
        StoryTheme.LEARNING.value: {"structure": "problem → research → success"},
        StoryTheme.BEDTIME.value: {"structure": "peaceful_setting → gentle_adventure → sleep"},
    }


def _get_animal_characters() -> List[str]:
    return ["أرنب صغير", "قطة لطيفة", "كلب وفي", "طائر مغرد", "فيل حكيم"]


def _get_fantasy_characters() -> List[str]:
    return ["تنين ودود", "جنية طيبة", "ساحر حكيم", "أميرة شجاعة", "فارس نبيل"]


def _get_human_characters() -> List[str]:
    return ["جد حكيم", "جدة محبة", "معلم صبور", "طبيب طيب", "شرطي مساعد"]


def _get_object_characters() -> List[str]:
    return ["كتاب سحري", "مصباح عجيب", "شجرة متكلمة", "نجمة لامعة", "قلم ملون"]


def load_character_bank() -> Dict[str, List[str]]:
    return {
        "animals": _get_animal_characters(),
        "fantasy": _get_fantasy_characters(),
        "humans": _get_human_characters(),
        "objects": _get_object_characters(),
    }


def load_moral_lessons() -> Dict[str, List[str]]:
    return {
        "3-6": ["المشاركة تجعل اللعب أكثر متعة", "الصدق أفضل من الكذب"],
        "7-10": ["العمل الجماعي يحقق نتائج أفضل", "المثابرة مفتاح النجاح"],
        "11-15": ["المسؤولية تجعلنا أشخاصاً أفضل", "العدالة أساس المجتمع"],
    }
