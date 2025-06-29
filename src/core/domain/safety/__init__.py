"""
AI Safety Module for Teddy Bear Content Filtering

This module provides advanced multi-layer content filtering specifically designed
for child safety in AI-powered toys and educational systems.

Features:
- Multi-layer toxicity detection
- Age-appropriate content validation
- Context-aware analysis
- Emotional impact assessment
- Educational value evaluation
"""

from .content_filter import AdvancedContentFilter
from .models import (
    ContentAnalysisResult,
    EmotionalImpactResult,
    SafetyConfig,
    FilterResult
)
from .keyword_filter import KeywordFilter
from .context_analyzer import ContextAnalyzer
from .emotional_impact_analyzer import EmotionalImpactAnalyzer
from .educational_value_evaluator import EducationalValueEvaluator

__all__ = [
    'AdvancedContentFilter',
    'ContentAnalysisResult',
    'EmotionalImpactResult',
    'SafetyConfig',
    'FilterResult',
    'KeywordFilter',
    'ContextAnalyzer',
    'EmotionalImpactAnalyzer',
    'EducationalValueEvaluator'
]

__version__ = "1.0.0"
__author__ = "AI Safety Team" 