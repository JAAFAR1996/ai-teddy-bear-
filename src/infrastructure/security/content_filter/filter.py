"""
The main AdvancedContentFilter class.
"""
import asyncio
import hashlib
import time
from typing import Any, Dict, List, Optional, Tuple

import structlog
from cachetools import TTLCache

from .age_checker import AgeAppropriatenessChecker
from .models import (
    ContentAnalysisResult,
    ContentCategory,
    RiskLevel,
    SafetyViolation,
)
from .toxicity_detector import ToxicityDetector

logger = structlog.get_logger(__name__)


class AdvancedContentFilter:
    """
    A sophisticated, multi-layered content filter that combines toxicity
    detection and age-appropriateness checks to ensure child safety.
    """

    def __init__(self):
        self.toxicity_detector = ToxicityDetector()
        self.age_checker = AgeAppropriatenessChecker()
        self.analysis_cache = TTLCache(maxsize=1000, ttl=1800)
        self.filter_stats = {
            "total_requests": 0,
            "blocked_content": 0,
            "modified_content": 0,
            "safe_content": 0,
            "cache_hits": 0,
        }

    async def comprehensive_safety_check(
        self, content: str, child_age: int, context: Optional[Dict[str, Any]] = None
    ) -> ContentAnalysisResult:
        """Performs a comprehensive, multi-layered safety check on the given content."""
        start_time = time.monotonic()
        self.filter_stats["total_requests"] += 1

        cache_key = self._generate_cache_key(content, child_age, context)
        if (cached_result := self.analysis_cache.get(cache_key)):
            self.filter_stats["cache_hits"] += 1
            return cached_result

        try:
            toxicity_result, age_result = await asyncio.gather(
                self.toxicity_detector.analyze_toxicity(content, child_age),
                self.age_checker.check_age_appropriateness(content, child_age),
            )
            analysis_result = await self._combine_analysis_results(
                content, child_age, toxicity_result, age_result, start_time
            )
            self.analysis_cache[cache_key] = analysis_result
            self._update_filter_stats(analysis_result)
            return analysis_result
        except Exception as e:
            logger.error("Content analysis pipeline failed", exc_info=e)
            return self._generate_safe_fallback_result(content, start_time)

    async def _combine_analysis_results(
        self, content: str, child_age: int, toxicity_result, age_result, start_time
    ) -> ContentAnalysisResult:
        """Combines the results of all analysis components into a single result."""
        is_safe = not toxicity_result["is_toxic"] and age_result["is_age_appropriate"]
        risk_level = self._calculate_overall_risk(toxicity_result, age_result)

        modifications, safe_alternative = [], content
        if not is_safe:
            modifications, safe_alternative = await self._generate_safe_modifications(
                content, toxicity_result, age_result, child_age
            )

        return ContentAnalysisResult(
            is_safe=is_safe,
            risk_level=risk_level,
            confidence_score=self._calculate_confidence(
                toxicity_result, age_result),
            content_category=self._categorize_content(content),
            violations=toxicity_result["violations"],
            modifications=modifications,
            safe_alternative=safe_alternative,
            safety_recommendations=self._generate_safety_recommendations(
                toxicity_result, age_result),
            parent_notification_required=self._requires_parent_notification(
                risk_level, child_age),
            processing_time_ms=(time.monotonic() - start_time) * 1000,
        )

    def _calculate_overall_risk(self, toxicity_result, age_result) -> RiskLevel:
        """Calculates the overall risk level based on all analysis scores."""
        max_risk_value = 0
        if toxicity_result["is_toxic"]:
            max_risk_value = max(
                max_risk_value, toxicity_result["violations"][0].severity.value)
        if not age_result["is_age_appropriate"]:
            appropriateness_risk = 2  # Medium risk default for age inappropriateness
            if age_result["appropriateness_score"] < 0.3:
                appropriateness_risk = 3  # High risk
            max_risk_value = max(max_risk_value, appropriateness_risk)

        risk_map = {0: RiskLevel.SAFE, 1: RiskLevel.LOW_RISK,
                    2: RiskLevel.MEDIUM_RISK, 3: RiskLevel.HIGH_RISK, 4: RiskLevel.CRITICAL}
        return risk_map.get(max_risk_value, RiskLevel.MEDIUM_RISK)

    def _calculate_confidence(self, toxicity_result, age_result) -> float:
        """Calculates a confidence score for the overall analysis."""
        return (toxicity_result.get("confidence", 0.8) + age_result.get("appropriateness_score", 0.5)) / 2

    def _categorize_content(self, content: str) -> ContentCategory:
        """Categorizes the content based on keywords."""
        if any(keyword in content for keyword in ["learn", "teach", "explain"]):
            return ContentCategory.EDUCATIONAL
        return ContentCategory.ENTERTAINMENT

    async def _generate_safe_modifications(
        self, content: str, toxicity_result, age_result, child_age: int
    ) -> Tuple[List[str], Optional[str]]:
        """Generates safe modifications to the content if it's deemed unsafe."""
        modifications, safe_alternative = [], content

        if toxicity_result["is_toxic"]:
            safe_alternative = await self._remove_toxic_content(safe_alternative, toxicity_result)
            modifications.append("Removed toxic content")

        if not age_result["is_age_appropriate"]:
            safe_alternative = await self._simplify_for_age(safe_alternative, child_age)
            modifications.append("Simplified content for age-appropriateness")

        if not safe_alternative.strip() or len(safe_alternative.strip()) < len(content.strip()) / 2:
            safe_alternative = self._get_safe_fallback_text(child_age)
            modifications.append("Replaced content with a safe alternative")

        return modifications, safe_alternative

    async def _remove_toxic_content(self, content: str, toxicity_result) -> str:
        """Removes detected toxic patterns from the content."""
        for category_info in toxicity_result["detected_categories"].values():
            for pattern in category_info["patterns"]:
                content = content.replace(pattern, "***")
        return content

    async def _simplify_for_age(self, content: str, age: int) -> str:
        """Simplifies content to be more age-appropriate."""
        # This is a mock simplification. A real implementation would be much more complex.
        if age < 7:
            return "Let's talk about something else! How about a fun story?"
        return "Let me say that in a simpler way. " + content

    def _get_safe_fallback_text(self, age: int) -> str:
        """Provides a generic, safe fallback response."""
        if age < 6:
            return "That's an interesting thought! What is your favorite color?"
        if age < 10:
            return "Hmm, let's talk about something different. Do you like drawing?"
        return "I'm not sure about that. Let's try a different topic."

    def _generate_safety_recommendations(self, toxicity_result, age_result) -> List[str]:
        """Generates safety recommendations based on the analysis."""
        recs = []
        if toxicity_result["is_toxic"]:
            recs.append("Content contains potentially toxic language.")
        if not age_result["is_age_appropriate"]:
            recs.extend(age_result["recommendations"])
        if not recs:
            recs.append("Content appears safe and appropriate.")
        return recs

    def _requires_parent_notification(self, risk_level: RiskLevel, child_age: int) -> bool:
        """Determines if a parent should be notified based on risk and age."""
        return risk_level in [RiskLevel.HIGH_RISK, RiskLevel.CRITICAL] or \
            (child_age <= 6 and risk_level == RiskLevel.MEDIUM_RISK)

    def _generate_cache_key(self, content: str, child_age: int, context: dict) -> str:
        """Generates a consistent cache key for a given analysis request."""
        ctx_str = str(sorted(context.items())) if context else ""
        return hashlib.md5(f"{content[:200]}:{child_age}:{ctx_str}".encode()).hexdigest()

    def _update_filter_stats(self, result: ContentAnalysisResult) -> None:
        """Updates internal statistics based on an analysis result."""
        if not result.is_safe:
            self.filter_stats["blocked_content"] += 1
        elif result.modifications:
            self.filter_stats["modified_content"] += 1
        else:
            self.filter_stats["safe_content"] += 1

    def _generate_safe_fallback_result(self, content: str, start_time: float) -> ContentAnalysisResult:
        """Generates a safe, default result in case of an internal processing error."""
        return ContentAnalysisResult(
            is_safe=False,
            risk_level=RiskLevel.HIGH_RISK,
            confidence_score=0.0,
            content_category=ContentCategory.HARMFUL,
            violations=[SafetyViolation(
                "processing_error", RiskLevel.HIGH_RISK, "Filter failed", content[:50])],
            modifications=["Filter pipeline error"],
            safe_alternative=self._get_safe_fallback_text(8),
            safety_recommendations=["System error, manual review recommended"],
            parent_notification_required=True,
            processing_time_ms=(time.monotonic() - start_time) * 1000,
        )

    def get_filter_statistics(self) -> Dict[str, Any]:
        """Returns a dictionary of the filter's performance statistics."""
        total = self.filter_stats["total_requests"]
        stats = self.filter_stats.copy()
        stats["cache_hit_rate"] = (
            stats["cache_hits"] / total * 100) if total > 0 else 0
        return stats

    async def cleanup(self):
        self.analysis_cache.clear()
        logger.info("AdvancedContentFilter resources cleaned up.")
