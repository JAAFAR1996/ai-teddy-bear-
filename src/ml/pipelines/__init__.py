# ===================================================================
# 🤖 AI Teddy Bear - ML Pipelines Module
# Enterprise-Grade AI Pipeline Components
# AI Team Lead: Senior AI Engineer
# Date: January 2025
# ===================================================================

from .child_interaction_pipeline import (ChildSafetyChecker, SafetyResult,
                                         child_interaction_pipeline,
                                         deploy_child_interaction_pipeline,
                                         generate_safe_response,
                                         preprocess_child_audio)

__all__ = [
    "child_interaction_pipeline",
    "deploy_child_interaction_pipeline",
    "preprocess_child_audio",
    "generate_safe_response",
    "ChildSafetyChecker",
    "SafetyResult",
]

__version__ = "1.0.0"
