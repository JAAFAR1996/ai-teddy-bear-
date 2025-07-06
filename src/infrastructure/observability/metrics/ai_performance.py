"""
AI-specific performance metrics for the teddy bear system.
"""
import logging
from typing import Any, Dict

from opentelemetry import metrics, trace

from .models import AIInteractionMetrics

logger = logging.getLogger(__name__)


class AIPerformanceMetrics:
    """
    AI-specific performance metrics for the teddy bear system.
    Tracks AI model performance, response quality, and resource usage.
    """

    def __init__(self):
        self.meter = metrics.get_meter("ai.teddy.performance", "1.0.0")
        self.tracer = trace.get_tracer("ai.teddy.performance", "1.0.0")
        self._initialize_metrics()

    def _initialize_metrics(self):
        """Initializes all the Prometheus metrics for AI performance."""
        self.ai_response_time = self.meter.create_histogram(
            name="ai_response_time_ms",
            description="AI model response time in milliseconds",
            unit="ms",
            boundaries=[50, 100, 200, 300, 500,
                        750, 1000, 1500, 2000, 3000, 5000],
        )
        self.ai_accuracy = self.meter.create_histogram(
            name="ai_accuracy_score",
            description="AI model accuracy score",
            unit="1",
            boundaries=[0.7, 0.8, 0.85, 0.9, 0.92,
                        0.95, 0.97, 0.98, 0.99, 1.0],
        )
        self.token_usage = self.meter.create_counter(
            name="ai_tokens_used_total",
            description="Total AI tokens consumed",
            unit="1",
        )
        self.inference_cost = self.meter.create_counter(
            name="ai_inference_cost_total",
            description="Total AI inference cost",
            unit="usd",
        )
        self.context_utilization = self.meter.create_histogram(
            name="ai_context_utilization",
            description="AI context window utilization percentage",
            unit="1",
            boundaries=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
        )
        self.hallucination_rate = self.meter.create_gauge(
            name="ai_hallucination_rate",
            description="AI hallucination detection rate",
            unit="1",
        )
        self.response_quality = self.meter.create_histogram(
            name="ai_response_quality_score",
            description="Quality score of AI responses",
            unit="1",
            boundaries=[0.5, 0.6, 0.7, 0.75, 0.8,
                        0.85, 0.9, 0.93, 0.95, 0.97, 1.0],
        )
        self.temperature_effectiveness = self.meter.create_histogram(
            name="ai_temperature_effectiveness",
            description="Effectiveness of different temperature settings",
            unit="1",
            boundaries=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
        )

    def _create_ai_interaction_span_attributes(
        self, metrics_data: AIInteractionMetrics
    ) -> Dict[str, Any]:
        """Creates a dictionary of span attributes for AI interaction tracing."""
        return {
            "ai.model": metrics_data.model_name,
            "ai.temperature": metrics_data.temperature,
            "ai.tokens_used": metrics_data.tokens_used,
            "ai.response_time_ms": metrics_data.response_time_ms,
            "ai.accuracy": metrics_data.accuracy_score,
            "ai.quality": metrics_data.quality_score,
            "ai.context_utilization": metrics_data.context_utilization,
            "ai.cost_usd": metrics_data.cost_usd,
            "child.age_group": metrics_data.child_context.get("age_group", "unknown"),
        }

    def _record_all_ai_metrics(self, metrics_data: AIInteractionMetrics):
        """Records all AI performance metrics."""
        child_context = metrics_data.child_context
        self.ai_response_time.record(
            metrics_data.response_time_ms,
            attributes={
                "model": metrics_data.model_name,
                "age_group": child_context.get("age_group", "unknown"),
                "temperature_range": self._categorize_temperature(metrics_data.temperature),
            },
        )
        self.ai_accuracy.record(
            metrics_data.accuracy_score,
            attributes={
                "model": metrics_data.model_name,
                "age_group": child_context.get("age_group", "unknown"),
            },
        )
        self.token_usage.add(
            metrics_data.tokens_used,
            attributes={
                "model": metrics_data.model_name,
                "interaction_type": child_context.get("interaction_type", "chat"),
                "age_group": child_context.get("age_group", "unknown"),
            },
        )
        self.inference_cost.add(
            metrics_data.cost_usd,
            attributes={
                "model": metrics_data.model_name,
                "cost_tier": self._categorize_cost(metrics_data.cost_usd),
            },
        )
        self.context_utilization.record(
            metrics_data.context_utilization,
            attributes={
                "model": metrics_data.model_name,
                "utilization_level": self._categorize_utilization(
                    metrics_data.context_utilization
                ),
            },
        )
        self.response_quality.record(
            metrics_data.quality_score,
            attributes={
                "model": metrics_data.model_name,
                "age_group": child_context.get("age_group", "unknown"),
                "quality_tier": self._categorize_quality(metrics_data.quality_score),
            },
        )

    def record_ai_interaction(self, metrics_data: AIInteractionMetrics):
        """Record comprehensive AI interaction metrics"""
        with self.tracer.start_as_current_span("ai_interaction") as span:
            attributes = self._create_ai_interaction_span_attributes(
                metrics_data)
            span.set_attributes(attributes)
            self._record_all_ai_metrics(metrics_data)

    def _categorize_temperature(self, temperature: float) -> str:
        """Categorize AI temperature settings"""
        if temperature < 0.3:
            return "conservative"
        elif temperature < 0.7:
            return "balanced"
        else:
            return "creative"

    def _categorize_cost(self, cost_usd: float) -> str:
        """Categorize inference costs"""
        if cost_usd < 0.001:
            return "low"
        elif cost_usd < 0.01:
            return "medium"
        else:
            return "high"

    def _categorize_utilization(self, utilization: float) -> str:
        """Categorize context utilization"""
        if utilization < 0.5:
            return "low"
        elif utilization < 0.8:
            return "optimal"
        else:
            return "high"

    def _categorize_quality(self, quality: float) -> str:
        """Categorize response quality"""
        if quality < 0.7:
            return "poor"
        elif quality < 0.85:
            return "good"
        elif quality < 0.95:
            return "excellent"
        else:
            return "exceptional"
