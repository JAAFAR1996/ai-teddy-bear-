from typing import Dict, List
from .models import EmotionCategory


def get_english_emotion_keywords() -> Dict[EmotionCategory, List[str]]:
    """Returns a dictionary of English emotion keywords."""
    return {
        EmotionCategory.HAPPY: ["happy", "glad", "joyful", "cheerful", "delighted"],
        EmotionCategory.SAD: ["sad", "unhappy", "miserable", "depressed"],
        EmotionCategory.ANGRY: ["angry", "mad", "furious", "irate"],
        EmotionCategory.SCARED: ["scared", "afraid", "terrified", "frightened"],
        EmotionCategory.EXCITED: ["excited", "thrilled", "eager", "enthusiastic"],
        EmotionCategory.SURPRISE: ["surprised", "shocked", "astonished"],
        EmotionCategory.LOVE: ["love", "adore", "cherish"],
        EmotionCategory.NEUTRAL: ["neutral", "okay", "fine"],
    }


def get_arabic_emotion_keywords() -> Dict[EmotionCategory, List[str]]:
    """Returns a dictionary of Arabic emotion keywords."""
    return {
        EmotionCategory.HAPPY: ["سعيد", "فرحان", "مبسوط"],
        EmotionCategory.SAD: ["حزين", "زعلان", "متضايق"],
        EmotionCategory.ANGRY: ["غاضب", "معصب", "منفعل"],
        EmotionCategory.SCARED: ["خايف", "مرعوب", "مذعور"],
        EmotionCategory.EXCITED: ["متحمس", "شغوف"],
        EmotionCategory.SURPRISE: ["متفاجئ", "مندهش"],
        EmotionCategory.LOVE: ["حب", "عشق", "مودة"],
        EmotionCategory.NEUTRAL: ["عادي", "تمام"],
    }


def load_emotion_keywords() -> Dict[EmotionCategory, List[str]]:
    """Loads a comprehensive list of emotion keywords for multiple languages."""
    english = get_english_emotion_keywords()
    arabic = get_arabic_emotion_keywords()
    all_keywords = {**english}
    for emotion, keywords in arabic.items():
        if emotion in all_keywords:
            all_keywords[emotion].extend(keywords)
        else:
            all_keywords[emotion] = keywords
    return all_keywords


def load_emoji_emotions() -> Dict[str, EmotionCategory]:
    """Enhanced emoji to emotion mapping"""
    return {
        "😊": EmotionCategory.HAPPY, "😁": EmotionCategory.HAPPY, "😄": EmotionCategory.HAPPY,
        "❤️": EmotionCategory.LOVE, "😍": EmotionCategory.LOVE, "🥰": EmotionCategory.LOVE,
        "😢": EmotionCategory.SAD, "😭": EmotionCategory.SAD, "😞": EmotionCategory.SAD,
        "😠": EmotionCategory.ANGRY, "😡": EmotionCategory.ANGRY, "🤬": EmotionCategory.ANGRY,
        "😨": EmotionCategory.SCARED, "😱": EmotionCategory.SCARED,
        "🤩": EmotionCategory.EXCITED, "🎉": EmotionCategory.EXCITED,
        "🤔": EmotionCategory.CURIOUS, "🧐": EmotionCategory.CURIOUS,
        "😕": EmotionCategory.CONFUSED, "🤷": EmotionCategory.CONFUSED,
        "😴": EmotionCategory.TIRED, "🥱": EmotionCategory.TIRED,
        "😲": EmotionCategory.SURPRISE, "😮": EmotionCategory.SURPRISE,
    }


def load_cultural_patterns() -> Dict[str, Dict[str, Dict[EmotionCategory, float]]]:
    """Cultural-specific emotional expressions"""
    return {
        "ar": {
            "الحمد لله": {EmotionCategory.HAPPY: 0.7, EmotionCategory.NEUTRAL: 0.3},
            "ما شاء الله": {EmotionCategory.HAPPY: 0.6, EmotionCategory.SURPRISE: 0.4},
            "يا ربي": {EmotionCategory.SURPRISE: 0.5, EmotionCategory.SCARED: 0.3},
            "وحشتني": {EmotionCategory.LOVE: 0.8, EmotionCategory.SAD: 0.2},
        },
        "en": {
            "oh my god": {EmotionCategory.SURPRISE: 0.8, EmotionCategory.SCARED: 0.2},
            "no way": {EmotionCategory.SURPRISE: 0.7, EmotionCategory.CONFUSED: 0.3},
            "awesome": {EmotionCategory.EXCITED: 0.9, EmotionCategory.HAPPY: 0.1},
        }
    }
