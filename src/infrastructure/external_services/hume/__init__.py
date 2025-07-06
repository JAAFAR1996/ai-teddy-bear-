"""
This package contains the Enhanced Hume Integration.
"""

from .calibration import calibrate_hume
from .enhanced_hume_2025 import EnhancedHumeIntegration
from .historical import merge_historical_data
from .models import CalibrationConfig, Language
from .multilang import analyze_emotion_multilang

__all__ = [
    "EnhancedHumeIntegration",
    "calibrate_hume",
    "merge_historical_data",
    "analyze_emotion_multilang",
    "CalibrationConfig",
    "Language",
]
