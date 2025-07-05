from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)


class PerformanceTracker:
    """Tracks performance metrics for the transcription service."""

    def __init__(self):
        self.stats = {
            "total_transcriptions": 0,
            "total_processing_time": 0.0,
            "average_confidence": 0.0,
            "error_count": 0,
            "fallback_usage": 0,
        }

    def update_stats(self, result: Dict[str, Any], processing_time: float) -> None:
        """Update performance statistics"""
        self.stats["total_transcriptions"] += 1
        self.stats["total_processing_time"] += processing_time

        current_avg = self.stats["average_confidence"]
        count = self.stats["total_transcriptions"]
        new_confidence = result.get("confidence", 0.0)

        if count > 0:
            self.stats["average_confidence"] = (
                current_avg * (count - 1) + new_confidence
            ) / count
        else:
            self.stats["average_confidence"] = new_confidence

    def increment_error_count(self):
        self.stats["error_count"] += 1

    def increment_fallback_usage(self):
        self.stats["fallback_usage"] += 1

    def get_metrics(self, config) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        total_transcriptions = self.stats["total_transcriptions"]
        avg_processing_time = (
            self.stats["total_processing_time"] / total_transcriptions
            if total_transcriptions > 0
            else 0
        )
        error_rate = (
            self.stats["error_count"] / total_transcriptions
            if total_transcriptions > 0
            else 0
        )
        fallback_rate = (
            self.stats["fallback_usage"] / total_transcriptions
            if total_transcriptions > 0
            else 0
        )

        return {
            "total_transcriptions": total_transcriptions,
            "average_processing_time_s": round(avg_processing_time, 3),
            "average_confidence": round(self.stats["average_confidence"], 3),
            "error_count": self.stats["error_count"],
            "error_rate": round(error_rate, 3),
            "fallback_usage": self.stats["fallback_usage"],
            "fallback_rate": round(fallback_rate, 3),
            "is_child_friendly": error_rate < 0.05 and avg_processing_time < 2.0,
            "response_quality": (
                "excellent"
                if error_rate < 0.02
                else "good" if error_rate < 0.05 else "needs_improvement"
            ),
            "processing_speed": (
                "fast"
                if avg_processing_time < 1.0
                else "acceptable" if avg_processing_time < 2.0 else "slow"
            ),
            "model": config.whisper_model,
            "device": config.device,
            "sample_rate": config.sample_rate,
            "confidence_threshold": config.confidence_threshold,
        }
