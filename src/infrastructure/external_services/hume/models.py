"""
Data models for the Enhanced Hume Integration.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict


class Language(Enum):
    ARABIC = "ar"
    ENGLISH = "en"
    AUTO_DETECT = "auto"


@dataclass
class CalibrationConfig:
    confidence_threshold: float = 0.7
    language_weights: Dict[str, float] = field(
        default_factory=lambda: {"ar": 1.0, "en": 0.9, "auto": 0.8}
    )
