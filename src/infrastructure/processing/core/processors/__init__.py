"""
Expose all task processors.
"""

from .ai import process_ai_response, process_emotion_analysis
from .audio import process_audio_enhancement, process_audio_transcription
from .custom import process_custom
from .data import process_data_analytics
from .db import process_database_operation
from .image import process_image_generation, process_image_processing
from .notification import process_notification
from .text import process_text_analysis

__all__ = [
    "process_ai_response",
    "process_emotion_analysis",
    "process_audio_enhancement",
    "process_audio_transcription",
    "process_custom",
    "process_data_analytics",
    "process_database_operation",
    "process_image_generation",
    "process_image_processing",
    "process_notification",
    "process_text_analysis",
]
