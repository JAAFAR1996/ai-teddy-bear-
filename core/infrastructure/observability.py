"""
Infrastructure observability module with optional OpenTelemetry support
"""

import logging
import time
from functools import wraps
from typing import Optional, Any, Dict
import structlog

# Try to import OpenTelemetry components - make them optional
try:
    from opentelemetry import trace
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.exporter.prometheus import PrometheusMetricReader
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.instrumentation.logging import LoggingInstrumentor
    OPENTELEMETRY_AVAILABLE = True
except ImportError as e:
    OPENTELEMETRY_AVAILABLE = False
    print(f"⚠️ OpenTelemetry not available: {e}")
    # Define dummy classes for compatibility
    class DummyTracer:
        def start_span(self, name, **kwargs):
            return DummySpan()
    
    class DummySpan:
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
        def set_attribute(self, key, value):
            pass

logger = structlog.get_logger(__name__)

def get_tracer(name: str = "teddy-bear") -> Any:
    """Get OpenTelemetry tracer or dummy tracer"""
    if OPENTELEMETRY_AVAILABLE:
        return trace.get_tracer(name)
    return DummyTracer()

def trace_async(span_name: str):
    """Async tracing decorator with fallback"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if OPENTELEMETRY_AVAILABLE:
                tracer = get_tracer()
                with tracer.start_span(span_name) as span:
                    span.set_attribute("function", func.__name__)
                    start_time = time.time()
                    try:
                        result = await func(*args, **kwargs)
                        span.set_attribute("success", True)
                        return result
                    except Exception as e:
                        span.set_attribute("error", str(e))
                        span.set_attribute("success", False)
                        raise
                    finally:
                        span.set_attribute("duration", time.time() - start_time)
            else:
                # Simple timing without OpenTelemetry
                start_time = time.time()
                logger.info(f"Starting {span_name}")
                try:
                    result = await func(*args, **kwargs)
                    logger.info(f"Completed {span_name}", duration=time.time() - start_time)
                    return result
                except Exception as e:
                    logger.error(f"Error in {span_name}", error=str(e), duration=time.time() - start_time)
                    raise
        return wrapper
    return decorator

def trace_sync(span_name: str):
    """Sync tracing decorator with fallback"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if OPENTELEMETRY_AVAILABLE:
                tracer = get_tracer()
                with tracer.start_span(span_name) as span:
                    span.set_attribute("function", func.__name__)
                    start_time = time.time()
                    try:
                        result = func(*args, **kwargs)
                        span.set_attribute("success", True)
                        return result
                    except Exception as e:
                        span.set_attribute("error", str(e))
                        span.set_attribute("success", False)
                        raise
                    finally:
                        span.set_attribute("duration", time.time() - start_time)
            else:
                # Simple timing without OpenTelemetry
                start_time = time.time()
                logger.info(f"Starting {span_name}")
                try:
                    result = func(*args, **kwargs)
                    logger.info(f"Completed {span_name}", duration=time.time() - start_time)
                    return result
                except Exception as e:
                    logger.error(f"Error in {span_name}", error=str(e), duration=time.time() - start_time)
                    raise
        return wrapper
    return decorator

def setup_observability(app_name: str = "teddy-bear") -> bool:
    """Setup observability stack with fallback"""
    try:
        if not OPENTELEMETRY_AVAILABLE:
            logger.warning("OpenTelemetry not available, using basic logging only")
            return False
            
        # Setup tracing
        trace.set_tracer_provider(TracerProvider())
        tracer = trace.get_tracer(app_name)
        
        # Configure exporters (optional)
        try:
            # Jaeger exporter (optional)
            jaeger_exporter = JaegerExporter(
                agent_host_name="localhost",
                agent_port=6831,
            )
            span_processor = BatchSpanProcessor(jaeger_exporter)
            trace.get_tracer_provider().add_span_processor(span_processor)
        except Exception as e:
            logger.warning(f"Jaeger not available: {e}")
        
        logger.info("✅ Observability setup complete")
        return True
        
    except Exception as e:
        logger.error(f"Failed to setup observability: {e}")
        return False

# Performance monitoring utilities
class PerformanceMonitor:
    """Simple performance monitoring"""
    
    def __init__(self):
        self.metrics: Dict[str, list] = {}
    
    def record_timing(self, operation: str, duration: float):
        """Record operation timing"""
        if operation not in self.metrics:
            self.metrics[operation] = []
        self.metrics[operation].append(duration)
    
    def get_stats(self, operation: str) -> Dict[str, float]:
        """Get statistics for operation"""
        if operation not in self.metrics:
            return {}
        
        times = self.metrics[operation]
        return {
            "count": len(times),
            "avg": sum(times) / len(times),
            "min": min(times),
            "max": max(times)
        }

# Global performance monitor instance
performance_monitor = PerformanceMonitor()

# Alias functions for compatibility
def setup_tracing(app_name: str = "teddy-bear") -> bool:
    """Alias for setup_observability"""
    return setup_observability(app_name) 