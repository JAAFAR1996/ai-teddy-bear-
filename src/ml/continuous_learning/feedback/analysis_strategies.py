# ===================================================================
# 🧸 AI Teddy Bear - Feedback Analysis Strategies
# Enterprise ML Feedback Analysis Strategy Implementations
# ML Team Lead: Senior ML Engineer
# Date: January 2025
# ===================================================================

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import numpy as np


class FeedbackAnalysisStrategy(ABC):
    """
    Abstract base class for a feedback analysis strategy.
    Defines the interface for analyzing a collection of feedback items.
    """

    @abstractmethod
    def analyze(self, feedback_items: List[Dict]) -> Optional[str]:
        """
        Analyzes the feedback items and returns a string key if the
        condition is met, otherwise None.

        Args:
            feedback_items: A list of feedback data dictionaries.

        Returns:
            An optional string representing the identified trend or area.
        """
        pass


# --- Improvement Area Strategies ---


class LowQualityStrategy(FeedbackAnalysisStrategy):
    """Identifies if the overall response quality is an area for improvement."""

    def analyze(self, feedback_items: List[Dict]) -> Optional[str]:
        low_quality_items = [
            item for item in feedback_items if item.get(
                "quality_score", 1.0) < 0.7]
        if (
            len(feedback_items) > 0
            and (len(low_quality_items) / len(feedback_items)) > 0.1
        ):
            return "response_quality"
        return None


class SafetyIssueStrategy(FeedbackAnalysisStrategy):
    """Identifies if there are significant safety issues."""

    def analyze(self, feedback_items: List[Dict]) -> Optional[str]:
        safety_issues = [
            item for item in feedback_items if item.get(
                "safety_score", 1.0) < 0.95]
        if safety_issues:
            return "safety_enhancement"
        return None


class LowSatisfactionStrategy(FeedbackAnalysisStrategy):
    """Identifies if user satisfaction is low."""

    def analyze(self, feedback_items: List[Dict]) -> Optional[str]:
        low_satisfaction = [
            item for item in feedback_items if item.get(
                "satisfaction", 1.0) < 0.7]
        if (
            len(feedback_items) > 0
            and (len(low_satisfaction) / len(feedback_items)) > 0.15
        ):
            return "user_satisfaction"
        return None


class ParentExperienceStrategy(FeedbackAnalysisStrategy):
    """Identifies if the parent experience needs improvement."""

    def analyze(self, feedback_items: List[Dict]) -> Optional[str]:
        parent_items = [item for item in feedback_items if item.get(
            "type") == "parent_feedback"]
        if parent_items:
            avg_parent_satisfaction = np.mean(
                [item.get("satisfaction", 1.0) for item in parent_items]
            )
            if avg_parent_satisfaction < 0.8:
                return "parent_experience"
        return None


# --- Positive Trend Strategies ---


class HighQualityStrategy(FeedbackAnalysisStrategy):
    """Identifies if the response quality is consistently high."""

    def analyze(self, feedback_items: List[Dict]) -> Optional[str]:
        if not feedback_items:
            return None
        high_quality_rate = sum(
            1 for item in feedback_items if item.get(
                "quality_score",
                0.0) > 0.8) / len(feedback_items)
        if high_quality_rate > 0.8:
            return "high_response_quality"
        return None


class ExcellentSafetyStrategy(FeedbackAnalysisStrategy):
    """Identifies if safety compliance is excellent."""

    def analyze(self, feedback_items: List[Dict]) -> Optional[str]:
        if not feedback_items:
            return None
        high_safety_rate = sum(
            1 for item in feedback_items if item.get(
                "safety_score",
                0.0) > 0.95) / len(feedback_items)
        if high_safety_rate > 0.98:
            return "excellent_safety_compliance"
        return None


class HighSatisfactionStrategy(FeedbackAnalysisStrategy):
    """Identifies if user satisfaction is high."""

    def analyze(self, feedback_items: List[Dict]) -> Optional[str]:
        if not feedback_items:
            return None
        high_satisfaction_rate = sum(
            1 for item in feedback_items if item.get("satisfaction", 0.0) > 0.8
        ) / len(feedback_items)
        if high_satisfaction_rate > 0.85:
            return "high_user_satisfaction"
        return None


class EffectiveLearningStrategy(FeedbackAnalysisStrategy):
    """Identifies if learning outcomes are effective."""

    def analyze(self, feedback_items: List[Dict]) -> Optional[str]:
        learning_items = [item for item in feedback_items if item.get(
            "type") == "learning_outcome"]
        if learning_items:
            avg_learning_effectiveness = np.mean(
                [item.get("quality_score", 0.0) for item in learning_items]
            )
            if avg_learning_effectiveness > 0.75:
                return "effective_learning_outcomes"
        return None
