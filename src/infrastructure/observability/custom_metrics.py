"""
Custom Metrics for AI Teddy Bear Observability
==============================================

Comprehensive metrics collection focusing on child safety,
AI performance, and system reliability with OpenTelemetry.
"""

import time
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging

from opentelemetry import metrics, trace
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.asyncio import AsyncioInstrumentor
from prometheus_client import start_http_server, CollectorRegistry

logger = logging.getLogger(__name__)


class SafetyViolationType(Enum):
    """Types of child safety violations"""
    INAPPROPRIATE_CONTENT = "inappropriate_content"
    PERSONAL_INFO_REQUEST = "personal_info_request" 
    TOXIC_LANGUAGE = "toxic_language"
    AGE_INAPPROPRIATE = "age_inappropriate"
    EMERGENCY_TRIGGER = "emergency_trigger"
    PARENTAL_BYPASS_ATTEMPT = "parental_bypass_attempt"
    UNKNOWN_ADULT_CONTACT = "unknown_adult_contact"


class SeverityLevel(Enum):
    """Severity levels for violations and alerts"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class ChildInteractionMetrics:
    """Metrics for a single child interaction"""
    child_id: str
    age_group: str
    interaction_type: str
    duration_ms: float
    safety_score: float
    toxicity_score: float
    sentiment_score: float
    response_time_ms: float
    success: bool
    violations: List[SafetyViolationType]


class ChildSafetyMetrics:
    """
    Comprehensive child safety metrics collection and monitoring.
    Focuses on real-time safety validation and compliance tracking.
    """
    
    def __init__(self):
        # Initialize OpenTelemetry
        self._setup_telemetry()
        
        # Start Prometheus metrics server
        start_http_server(port=8000)
        
        # Initialize metrics
        self.meter = metrics.get_meter("ai.teddy.safety", "1.0.0")
        self.tracer = trace.get_tracer("ai.teddy.safety", "1.0.0")
        
        # Safety violation tracking
        self.safety_violations = self.meter.create_counter(
            name="child_safety_violations_total",
            description="Total child safety violations detected",
            unit="1"
        )
        
        # Content toxicity monitoring
        self.content_toxicity = self.meter.create_histogram(
            name="content_toxicity_score",
            description="Toxicity scores of AI responses",
            unit="1",
            boundaries=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        )
        
        # Real-time conversation sentiment
        self.conversation_sentiment = self.meter.create_gauge(
            name="conversation_sentiment",
            description="Real-time sentiment of conversation (-1 to +1)",
            unit="1"
        )
        
        # Child engagement duration
        self.child_engagement = self.meter.create_histogram(
            name="child_engagement_duration_seconds",
            description="Duration of child engagement sessions",
            unit="seconds",
            boundaries=[1, 5, 10, 30, 60, 120, 300, 600, 1200, 1800]
        )
        
        # Age appropriateness score
        self.age_appropriateness = self.meter.create_histogram(
            name="age_appropriateness_score",
            description="Age appropriateness score of responses",
            unit="1",
            boundaries=[0.0, 0.2, 0.4, 0.6, 0.7, 0.8, 0.85, 0.9, 0.95, 1.0]
        )
        
        # Emergency protocol activations
        self.emergency_activations = self.meter.create_counter(
            name="emergency_protocol_activations_total",
            description="Total emergency protocol activations",
            unit="1"
        )
        
        # Parental control events
        self.parental_control_events = self.meter.create_counter(
            name="parental_control_events_total",
            description="Parental control related events",
            unit="1"
        )
        
        # Child safety compliance rate
        self.safety_compliance_rate = self.meter.create_gauge(
            name="child_safety_compliance_rate",
            description="Overall child safety compliance rate",
            unit="1"
        )
        
        # COPPA compliance tracking
        self.coppa_compliance = self.meter.create_gauge(
            name="coppa_compliance_score",
            description="COPPA compliance score",
            unit="1"
        )
        
        # Content filter effectiveness
        self.content_filter_effectiveness = self.meter.create_histogram(
            name="content_filter_effectiveness",
            description="Effectiveness of content filtering",
            unit="1",
            boundaries=[0.7, 0.8, 0.85, 0.9, 0.95, 0.97, 0.98, 0.99, 0.995, 1.0]
        )
        
    def _setup_telemetry(self):
        """Setup OpenTelemetry providers and exporters"""
        # Metrics setup
        registry = CollectorRegistry()
        reader = PrometheusMetricReader()
        provider = MeterProvider(metric_readers=[reader])
        metrics.set_meter_provider(provider)
        
        # Tracing setup
        jaeger_exporter = JaegerExporter(
            agent_host_name="jaeger-agent",
            agent_port=6831,
        )
        
        span_processor = BatchSpanProcessor(jaeger_exporter)
        trace_provider = TracerProvider()
        trace_provider.add_span_processor(span_processor)
        trace.set_tracer_provider(trace_provider)
        
        # Instrument frameworks
        FastAPIInstrumentor.instrument()
        AsyncioInstrumentor.instrument()
    
    def record_safety_violation(
        self, 
        violation_type: SafetyViolationType, 
        severity: SeverityLevel,
        child_context: Dict[str, Any],
        details: Optional[str] = None
    ):
        """Record a child safety violation with full context"""
        with self.tracer.start_as_current_span("safety_violation") as span:
            span.set_attributes({
                "violation.type": violation_type.value,
                "violation.severity": severity.value,
                "child.age_group": child_context.get("age_group", "unknown"),
                "child.id": child_context.get("child_id", "anonymous"),
                "violation.details": details or "No details provided",
                "timestamp": datetime.utcnow().isoformat()
            })
            
            self.safety_violations.add(
                1,
                attributes={
                    "violation_type": violation_type.value,
                    "severity": severity.value,
                    "age_group": child_context.get("age_group", "unknown"),
                    "session_id": child_context.get("session_id", "unknown")
                }
            )
            
            # Log critical violations
            if severity in [SeverityLevel.CRITICAL, SeverityLevel.HIGH]:
                logger.critical(
                    f"Child safety violation: {violation_type.value} "
                    f"(severity: {severity.value}) for child {child_context.get('child_id', 'unknown')}"
                )
    
    def record_content_toxicity(
        self, 
        toxicity_score: float, 
        content_type: str,
        child_context: Dict[str, Any]
    ):
        """Record content toxicity score"""
        with self.tracer.start_as_current_span("content_toxicity_check") as span:
            span.set_attributes({
                "toxicity.score": toxicity_score,
                "content.type": content_type,
                "child.age_group": child_context.get("age_group", "unknown")
            })
            
            self.content_toxicity.record(
                toxicity_score,
                attributes={
                    "content_type": content_type,
                    "age_group": child_context.get("age_group", "unknown"),
                    "is_toxic": "true" if toxicity_score > 0.5 else "false"
                }
            )
    
    def record_child_interaction(self, metrics: ChildInteractionMetrics):
        """Record comprehensive child interaction metrics"""
        with self.tracer.start_as_current_span("child_interaction") as span:
            span.set_attributes({
                "child.id": metrics.child_id,
                "child.age_group": metrics.age_group,
                "interaction.type": metrics.interaction_type,
                "interaction.duration_ms": metrics.duration_ms,
                "safety.score": metrics.safety_score,
                "toxicity.score": metrics.toxicity_score,
                "sentiment.score": metrics.sentiment_score,
                "response.time_ms": metrics.response_time_ms,
                "interaction.success": metrics.success,
                "violations.count": len(metrics.violations)
            })
            
            # Record engagement duration
            self.child_engagement.record(
                metrics.duration_ms / 1000,  # Convert to seconds
                attributes={
                    "age_group": metrics.age_group,
                    "interaction_type": metrics.interaction_type,
                    "success": str(metrics.success).lower()
                }
            )
            
            # Record sentiment
            self.conversation_sentiment.set(
                metrics.sentiment_score,
                attributes={
                    "age_group": metrics.age_group,
                    "interaction_type": metrics.interaction_type
                }
            )
            
            # Record safety violations if any
            for violation in metrics.violations:
                self.record_safety_violation(
                    violation,
                    SeverityLevel.MEDIUM,
                    {"child_id": metrics.child_id, "age_group": metrics.age_group}
                )
    
    def record_emergency_activation(
        self, 
        trigger_type: str, 
        response_time_ms: float,
        child_context: Dict[str, Any]
    ):
        """Record emergency protocol activation"""
        with self.tracer.start_as_current_span("emergency_activation") as span:
            span.set_attributes({
                "emergency.trigger_type": trigger_type,
                "emergency.response_time_ms": response_time_ms,
                "child.id": child_context.get("child_id", "unknown"),
                "child.age_group": child_context.get("age_group", "unknown")
            })
            
            self.emergency_activations.add(
                1,
                attributes={
                    "trigger_type": trigger_type,
                    "age_group": child_context.get("age_group", "unknown"),
                    "response_time_category": self._categorize_response_time(response_time_ms)
                }
            )
            
            # Critical alert for slow emergency response
            if response_time_ms > 30000:  # 30 seconds
                logger.critical(
                    f"Slow emergency response: {response_time_ms}ms for trigger {trigger_type}"
                )
    
    def record_parental_control_event(
        self, 
        event_type: str, 
        action: str,
        parent_context: Dict[str, Any]
    ):
        """Record parental control events"""
        with self.tracer.start_as_current_span("parental_control_event") as span:
            span.set_attributes({
                "parental.event_type": event_type,
                "parental.action": action,
                "parent.id": parent_context.get("parent_id", "unknown")
            })
            
            self.parental_control_events.add(
                1,
                attributes={
                    "event_type": event_type,
                    "action": action,
                    "verification_method": parent_context.get("verification_method", "unknown")
                }
            )
    
    def update_compliance_metrics(self):
        """Update compliance metrics based on recent data"""
        # This would typically query recent metrics to calculate compliance rates
        # For demo purposes, using simulated values
        
        safety_compliance = 0.985  # 98.5% compliance rate
        coppa_compliance = 0.995   # 99.5% COPPA compliance
        filter_effectiveness = 0.973  # 97.3% filter effectiveness
        
        self.safety_compliance_rate.set(
            safety_compliance,
            attributes={"measurement_window": "1h"}
        )
        
        self.coppa_compliance.set(
            coppa_compliance,
            attributes={"regulation": "COPPA", "region": "US"}
        )
        
        self.content_filter_effectiveness.record(
            filter_effectiveness,
            attributes={"filter_type": "comprehensive", "ai_model": "gpt-4"}
        )
    
    def _categorize_response_time(self, response_time_ms: float) -> str:
        """Categorize response times for metrics"""
        if response_time_ms < 1000:
            return "excellent"
        elif response_time_ms < 5000:
            return "good"
        elif response_time_ms < 15000:
            return "acceptable"
        elif response_time_ms < 30000:
            return "poor"
        else:
            return "critical"


class AIPerformanceMetrics:
    """
    AI-specific performance metrics for the teddy bear system.
    Tracks AI model performance, response quality, and resource usage.
    """
    
    def __init__(self):
        self.meter = metrics.get_meter("ai.teddy.performance", "1.0.0")
        self.tracer = trace.get_tracer("ai.teddy.performance", "1.0.0")
        
        # AI response time tracking
        self.ai_response_time = self.meter.create_histogram(
            name="ai_response_time_ms",
            description="AI model response time in milliseconds",
            unit="ms",
            boundaries=[50, 100, 200, 300, 500, 750, 1000, 1500, 2000, 3000, 5000]
        )
        
        # AI model accuracy
        self.ai_accuracy = self.meter.create_histogram(
            name="ai_accuracy_score",
            description="AI model accuracy score",
            unit="1",
            boundaries=[0.7, 0.8, 0.85, 0.9, 0.92, 0.95, 0.97, 0.98, 0.99, 1.0]
        )
        
        # Token usage tracking
        self.token_usage = self.meter.create_counter(
            name="ai_tokens_used_total",
            description="Total AI tokens consumed",
            unit="1"
        )
        
        # Model inference cost
        self.inference_cost = self.meter.create_counter(
            name="ai_inference_cost_total",
            description="Total AI inference cost",
            unit="usd"
        )
        
        # Context window utilization
        self.context_utilization = self.meter.create_histogram(
            name="ai_context_utilization",
            description="AI context window utilization percentage",
            unit="1",
            boundaries=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        )
        
        # AI hallucination detection
        self.hallucination_rate = self.meter.create_gauge(
            name="ai_hallucination_rate",
            description="AI hallucination detection rate",
            unit="1"
        )
        
        # Response quality score
        self.response_quality = self.meter.create_histogram(
            name="ai_response_quality_score",
            description="Quality score of AI responses",
            unit="1",
            boundaries=[0.5, 0.6, 0.7, 0.75, 0.8, 0.85, 0.9, 0.93, 0.95, 0.97, 1.0]
        )
        
        # Model temperature effectiveness
        self.temperature_effectiveness = self.meter.create_histogram(
            name="ai_temperature_effectiveness",
            description="Effectiveness of different temperature settings",
            unit="1",
            boundaries=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        )
    
    def record_ai_interaction(
        self,
        response_time_ms: float,
        tokens_used: int,
        model_name: str,
        temperature: float,
        accuracy_score: float,
        quality_score: float,
        context_utilization: float,
        cost_usd: float,
        child_context: Dict[str, Any]
    ):
        """Record comprehensive AI interaction metrics"""
        with self.tracer.start_as_current_span("ai_interaction") as span:
            span.set_attributes({
                "ai.model": model_name,
                "ai.temperature": temperature,
                "ai.tokens_used": tokens_used,
                "ai.response_time_ms": response_time_ms,
                "ai.accuracy": accuracy_score,
                "ai.quality": quality_score,
                "ai.context_utilization": context_utilization,
                "ai.cost_usd": cost_usd,
                "child.age_group": child_context.get("age_group", "unknown")
            })
            
            # Record all metrics
            self.ai_response_time.record(
                response_time_ms,
                attributes={
                    "model": model_name,
                    "age_group": child_context.get("age_group", "unknown"),
                    "temperature_range": self._categorize_temperature(temperature)
                }
            )
            
            self.ai_accuracy.record(
                accuracy_score,
                attributes={
                    "model": model_name,
                    "age_group": child_context.get("age_group", "unknown")
                }
            )
            
            self.token_usage.add(
                tokens_used,
                attributes={
                    "model": model_name,
                    "interaction_type": child_context.get("interaction_type", "chat"),
                    "age_group": child_context.get("age_group", "unknown")
                }
            )
            
            self.inference_cost.add(
                cost_usd,
                attributes={
                    "model": model_name,
                    "cost_tier": self._categorize_cost(cost_usd)
                }
            )
            
            self.context_utilization.record(
                context_utilization,
                attributes={
                    "model": model_name,
                    "utilization_level": self._categorize_utilization(context_utilization)
                }
            )
            
            self.response_quality.record(
                quality_score,
                attributes={
                    "model": model_name,
                    "age_group": child_context.get("age_group", "unknown"),
                    "quality_tier": self._categorize_quality(quality_score)
                }
            )
    
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


class SystemHealthMetrics:
    """
    System-wide health and reliability metrics.
    Tracks infrastructure health, SLIs/SLOs, and error budgets.
    """
    
    def __init__(self):
        self.meter = metrics.get_meter("ai.teddy.system", "1.0.0")
        self.tracer = trace.get_tracer("ai.teddy.system", "1.0.0")
        
        # Service availability
        self.service_availability = self.meter.create_gauge(
            name="service_availability",
            description="Service availability percentage",
            unit="1"
        )
        
        # Error rate tracking
        self.error_rate = self.meter.create_gauge(
            name="service_error_rate",
            description="Service error rate",
            unit="1"
        )
        
        # Request latency
        self.request_latency = self.meter.create_histogram(
            name="request_latency_ms",
            description="Request latency in milliseconds",
            unit="ms",
            boundaries=[1, 5, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000]
        )
        
        # Throughput tracking
        self.request_throughput = self.meter.create_counter(
            name="requests_total",
            description="Total number of requests",
            unit="1"
        )
        
        # Error budget consumption
        self.error_budget_consumption = self.meter.create_gauge(
            name="error_budget_consumption",
            description="Error budget consumption rate",
            unit="1"
        )
        
        # SLO compliance
        self.slo_compliance = self.meter.create_gauge(
            name="slo_compliance",
            description="SLO compliance percentage",
            unit="1"
        )
        
        # Database connection health
        self.db_connection_health = self.meter.create_gauge(
            name="database_connection_health",
            description="Database connection health score",
            unit="1"
        )
        
        # Cache hit rate
        self.cache_hit_rate = self.meter.create_gauge(
            name="cache_hit_rate",
            description="Cache hit rate percentage",
            unit="1"
        )
        
        # Memory usage
        self.memory_usage = self.meter.create_gauge(
            name="memory_usage_bytes",
            description="Memory usage in bytes",
            unit="bytes"
        )
        
        # CPU utilization
        self.cpu_utilization = self.meter.create_gauge(
            name="cpu_utilization",
            description="CPU utilization percentage",
            unit="1"
        )
    
    def record_request(
        self,
        latency_ms: float,
        status_code: int,
        service_name: str,
        endpoint: str,
        method: str
    ):
        """Record request metrics"""
        with self.tracer.start_as_current_span("request") as span:
            span.set_attributes({
                "http.method": method,
                "http.status_code": status_code,
                "service.name": service_name,
                "endpoint": endpoint,
                "latency_ms": latency_ms
            })
            
            # Record latency
            self.request_latency.record(
                latency_ms,
                attributes={
                    "service": service_name,
                    "endpoint": endpoint,
                    "method": method,
                    "status_code": str(status_code),
                    "status_class": f"{status_code // 100}xx"
                }
            )
            
            # Record throughput
            self.request_throughput.add(
                1,
                attributes={
                    "service": service_name,
                    "endpoint": endpoint,
                    "method": method,
                    "status_code": str(status_code)
                }
            )
    
    def update_slo_metrics(self, service_name: str):
        """Update SLO compliance metrics"""
        # This would typically calculate from actual metrics
        # For demo purposes, using simulated values
        
        availability = 0.9995  # 99.95% availability
        error_rate = 0.0005    # 0.05% error rate
        error_budget_used = 0.25  # 25% of error budget consumed
        slo_compliance = 0.998    # 99.8% SLO compliance
        
        self.service_availability.set(
            availability,
            attributes={"service": service_name}
        )
        
        self.error_rate.set(
            error_rate,
            attributes={"service": service_name}
        )
        
        self.error_budget_consumption.set(
            error_budget_used,
            attributes={"service": service_name, "slo_type": "availability"}
        )
        
        self.slo_compliance.set(
            slo_compliance,
            attributes={"service": service_name}
        )


class ObservabilityAggregator:
    """
    Central aggregator for all observability metrics.
    Provides unified interface for metric collection and analysis.
    """
    
    def __init__(self):
        self.child_safety_metrics = ChildSafetyMetrics()
        self.ai_performance_metrics = AIPerformanceMetrics()
        self.system_health_metrics = SystemHealthMetrics()
        
        # Start background tasks
        asyncio.create_task(self._periodic_compliance_update())
        asyncio.create_task(self._periodic_health_check())
    
    async def _periodic_compliance_update(self):
        """Periodically update compliance metrics"""
        while True:
            try:
                self.child_safety_metrics.update_compliance_metrics()
                await asyncio.sleep(60)  # Update every minute
            except Exception as e:
                logger.error(f"Error updating compliance metrics: {e}")
                await asyncio.sleep(60)
    
    async def _periodic_health_check(self):
        """Periodically update system health metrics"""
        while True:
            try:
                self.system_health_metrics.update_slo_metrics("ai-teddy-core")
                await asyncio.sleep(30)  # Update every 30 seconds
            except Exception as e:
                logger.error(f"Error updating health metrics: {e}")
                await asyncio.sleep(30)
    
    def get_safety_metrics(self) -> ChildSafetyMetrics:
        """Get child safety metrics instance"""
        return self.child_safety_metrics
    
    def get_performance_metrics(self) -> AIPerformanceMetrics:
        """Get AI performance metrics instance"""
        return self.ai_performance_metrics
    
    def get_health_metrics(self) -> SystemHealthMetrics:
        """Get system health metrics instance"""
        return self.system_health_metrics


# Global metrics instance
observability = ObservabilityAggregator() 