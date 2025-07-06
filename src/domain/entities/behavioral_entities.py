from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List


class VoicePattern(Enum):
    """أنماط الصوت المختلفة"""

    CONFIDENT = "واثق"
    HESITANT = "متردد"
    EXCITED = "متحمس"
    ANXIOUS = "قلق"
    CALM = "هادئ"
    TIRED = "متعب"
    HAPPY = "سعيد"
    SAD = "حزين"


class BehavioralConcern(Enum):
    """المخاوف السلوكية التي تحتاج تنبيه الوالدين"""

    REPEATED_ANXIETY = "قلق_متكرر"
    SOCIAL_WITHDRAWAL = "انسحاب_اجتماعي"
    LOW_CONFIDENCE = "ثقة_منخفضة"
    AGGRESSIVE_PATTERNS = "أنماط_عدوانية"
    REGRESSION_SIGNS = "علامات_تراجع"
    EMOTIONAL_INSTABILITY = "عدم_استقرار_عاطفي"


@dataclass
class VoiceAnalysis:
    """تحليل مفصل للصوت"""

    speed_wpm: float  # كلمات في الدقيقة
    pause_frequency: float  # تكرار التوقفات
    pause_duration_avg: float  # متوسط مدة التوقفات
    pitch_variation: float  # تنوع طبقة الصوت
    volume_consistency: float  # ثبات الصوت
    confidence_score: float  # نقاط الثقة (0-1)
    emotional_tone: str  # النبرة العاطفية
    detected_patterns: List[VoicePattern]
    analysis_timestamp: datetime


@dataclass
class BehavioralAlert:
    """تنبيه سلوكي للوالدين"""

    id: str
    child_name: str
    device_id: str
    concern_type: BehavioralConcern
    severity_level: str  # "منخفض", "متوسط", "عالي"
    description: str
    evidence: List[str]  # الأدلة المؤدية للتنبيه
    recommendations: List[str]
    created_at: datetime
    parent_notified: bool = False


@dataclass
class PsychologicalProfile:
    """الملف النفسي للطفل"""

    child_name: str
    device_id: str
    personality_traits: Dict[str, float]  # الصفات الشخصية مع نقاطها
    emotional_patterns: Dict[str, List[float]]  # أنماط المشاعر عبر الوقت
    stress_indicators: List[str]  # مؤشرات التوتر
    strengths: List[str]  # نقاط القوة
    areas_of_concern: List[str]  # مناطق الاهتمام
    social_skills_level: float  # مستوى المهارات الاجتماعية
    confidence_trend: List[float]  # اتجاه الثقة بالنفس
    last_updated: datetime
