# [AI-Generated]: This code was added automatically according to the project guide.
from dataclasses import dataclass
from typing import List

@dataclass
class EmotionConfig:
    """إعدادات تحليل المشاعر"""
    api_key: str
    supported_emotions: List[str] = None
    alert_threshold: float = 0.7  # عتبة التنبيه للمشاعر السلبية
    history_limit: int = 1000     # حد السجل
    
    def __post_init__(self):
        if self.supported_emotions is None:
            self.supported_emotions = [
                'happy', 'sad', 'angry', 'fear', 
                'surprise', 'disgust', 'neutral'
            ]