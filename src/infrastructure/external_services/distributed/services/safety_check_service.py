"""
Distributed safety check service deployment.
"""

import logging
import time
from typing import Any, Dict

try:
    from ray import serve
    AI_SERVICES_AVAILABLE = True
except ImportError:
    AI_SERVICES_AVAILABLE = False
    serve = None

from ..mocks import MockAIServices

logger = logging.getLogger(__name__)

if AI_SERVICES_AVAILABLE:
    @serve.deployment(
        name="safety-service",
        num_replicas=3,
        ray_actor_options={
            "num_cpus": 0.5,
            "memory": 500 *
            1024 *
            1024},
        # 500MB
    )
    class SafetyCheckService:
        """Distributed safety checking service."""

        def __init__(self):
            self.safety_keywords = {
                "inappropriate": ["سيء", "غبي", "أكره", "اقتل", "ايذي"],
                "distress": ["ساعدني", "خائف", "طوارئ", "خطر", "توقف"],
                "violence": ["قتال", "ضرب", "دم", "سلاح"],
            }
            self.service_stats = {"requests": 0, "total_time": 0.0}

        async def check_safety(
            self, text: str, audio_data: bytes = None
        ) -> Dict[str, Any]:
            """Perform comprehensive safety check."""
            start_time = time.time()
            self.service_stats["requests"] += 1

            try:
                # Text-based safety check
                text_result = self._check_text_safety(text)

                # Audio-based safety check (if implemented)
                audio_result = (
                    self._check_audio_safety(audio_data)
                    if audio_data
                    else {"safe": True}
                )

                # Combine results
                is_safe = text_result["safe"] and audio_result["safe"]
                risk_level = "high" if not is_safe else "low"

                processing_time = (time.time() - start_time) * 1000
                self.service_stats["total_time"] += processing_time

                return {
                    "is_safe": is_safe, "risk_level": risk_level, "confidence": min(
                        text_result["confidence"], audio_result.get(
                            "confidence", 1.0)), "detected_issues": text_result.get(
                        "issues", []), "processing_time_ms": processing_time, }

            except Exception as e:
                logger.error(f"❌ Safety check failed: {e}")
                return await MockAIServices.check_safety(text, audio_data)

        def _check_text_safety(self, text: str) -> Dict[str, Any]:
            """Check text content for safety issues."""
            if not text:
                return {"safe": True, "confidence": 1.0, "issues": []}

            text_lower = text.lower()
            detected_issues = []

            for category, keywords in self.safety_keywords.items():
                for keyword in keywords:
                    if keyword in text_lower:
                        detected_issues.append(f"{category}: {keyword}")

            is_safe = len(detected_issues) == 0
            confidence = 0.95 if is_safe else 0.8

            return {
                "safe": is_safe,
                "confidence": confidence,
                "issues": detected_issues,
            }

        def _check_audio_safety(self, audio_data: bytes) -> Dict[str, Any]:
            """Check audio content for safety issues (placeholder)."""
            # Placeholder for audio-based safety analysis
            # Could include volume analysis, speech pattern analysis, etc.
            return {"safe": True, "confidence": 0.9}
else:
    SafetyCheckService = MockAIServices
