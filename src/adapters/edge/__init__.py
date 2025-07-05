"""
Edge Computing Adapters for AI Teddy Bear Project.

This module provides edge computing capabilities for real-time processing
on embedded devices like ESP32-S3, enabling instant response and reduced
cloud dependency.

AI Team Implementation - Task 10
"""

from .edge_ai_manager import (
    EdgeAIManager,
    EdgeAudioFeatures,
    EdgeEmotionResult,
    EdgeModelConfig,
    EdgeProcessingMode,
    EdgeProcessingResult,
    EdgeSafetyResult,
    SafetyLevel,
    WakeWordModel,
)

__all__ = [
    "EdgeAIManager",
    "EdgeModelConfig",
    "EdgeProcessingMode",
    "WakeWordModel",
    "SafetyLevel",
    "EdgeProcessingResult",
    "EdgeEmotionResult",
    "EdgeSafetyResult",
    "EdgeAudioFeatures",
]
