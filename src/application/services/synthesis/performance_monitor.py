#!/usr/bin/env python3
"""
📊 Performance Monitoring Service
خدمة مراقبة الأداء والإحصائيات
"""

import logging
import time
from typing import Any, Dict, Optional

from .models import VoiceProvider

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Service for tracking performance metrics and health monitoring"""
    
    def __init__(self):
        """Initialize the performance monitor"""
        self.stats = {
            "total_syntheses": 0,
            "total_processing_time": 0.0,
            "total_audio_duration": 0.0,
            "error_count": 0,
            "provider_usage": {},
            "provider_errors": {},
            "provider_response_times": {}
        }
        
        self.start_time = time.time()
        
        logger.debug("Performance monitor initialized")
    
    def update_synthesis_stats(
        self,
        provider: VoiceProvider,
        processing_time: float,
        audio_duration: Optional[float] = None,
        success: bool = True
    ) -> None:
        """Update performance statistics for a synthesis operation"""
        try:
            # Update general stats
            self.stats["total_syntheses"] += 1
            self.stats["total_processing_time"] += processing_time
            
            if audio_duration:
                self.stats["total_audio_duration"] += audio_duration
            
            # Update provider-specific stats
            provider_name = provider.value
            
            # Usage count
            if provider_name not in self.stats["provider_usage"]:
                self.stats["provider_usage"][provider_name] = 0
            self.stats["provider_usage"][provider_name] += 1
            
            # Error tracking
            if not success:
                self.stats["error_count"] += 1
                if provider_name not in self.stats["provider_errors"]:
                    self.stats["provider_errors"][provider_name] = 0
                self.stats["provider_errors"][provider_name] += 1
            
            # Response time tracking
            if provider_name not in self.stats["provider_response_times"]:
                self.stats["provider_response_times"][provider_name] = []
            
            self.stats["provider_response_times"][provider_name].append(processing_time)
            
            # Keep only last 100 response times per provider
            if len(self.stats["provider_response_times"][provider_name]) > 100:
                self.stats["provider_response_times"][provider_name] = \
                    self.stats["provider_response_times"][provider_name][-100:]
            
            logger.debug(f"Updated stats for provider {provider_name}: {processing_time:.3f}s")
            
        except Exception as e:
            logger.error(f"Failed to update synthesis stats: {e}")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        try:
            uptime = time.time() - self.start_time
            
            # Calculate averages
            avg_processing_time = (
                self.stats["total_processing_time"] / self.stats["total_syntheses"]
                if self.stats["total_syntheses"] > 0 else 0
            )
            
            error_rate = (
                self.stats["error_count"] / self.stats["total_syntheses"]
                if self.stats["total_syntheses"] > 0 else 0
            )
            
            # Calculate provider-specific metrics
            provider_metrics = {}
            for provider, usage_count in self.stats["provider_usage"].items():
                response_times = self.stats["provider_response_times"].get(provider, [])
                error_count = self.stats["provider_errors"].get(provider, 0)
                
                provider_metrics[provider] = {
                    "usage_count": usage_count,
                    "error_count": error_count,
                    "error_rate": error_count / usage_count if usage_count > 0 else 0,
                    "avg_response_time": sum(response_times) / len(response_times) if response_times else 0,
                    "min_response_time": min(response_times) if response_times else 0,
                    "max_response_time": max(response_times) if response_times else 0
                }
            
            return {
                "uptime_seconds": uptime,
                "total_syntheses": self.stats["total_syntheses"],
                "average_processing_time_s": avg_processing_time,
                "total_audio_duration_s": self.stats["total_audio_duration"],
                "error_count": self.stats["error_count"],
                "error_rate": error_rate,
                "syntheses_per_minute": self.stats["total_syntheses"] / (uptime / 60) if uptime > 0 else 0,
                "provider_metrics": provider_metrics,
                "system_health": self._calculate_system_health()
            }
            
        except Exception as e:
            logger.error(f"Failed to get performance metrics: {e}")
            return {"error": str(e)}
    
    def _calculate_system_health(self) -> Dict[str, Any]:
        """Calculate overall system health score"""
        try:
            if self.stats["total_syntheses"] == 0:
                return {
                    "score": 1.0,
                    "status": "healthy",
                    "reason": "No operations yet"
                }
            
            error_rate = self.stats["error_count"] / self.stats["total_syntheses"]
            
            # Health score based on error rate
            if error_rate == 0:
                health_score = 1.0
                status = "healthy"
            elif error_rate < 0.1:  # Less than 10% errors
                health_score = 0.8
                status = "healthy"
            elif error_rate < 0.3:  # Less than 30% errors
                health_score = 0.6
                status = "degraded"
            else:
                health_score = 0.3
                status = "unhealthy"
            
            return {
                "score": health_score,
                "status": status,
                "error_rate": error_rate,
                "total_operations": self.stats["total_syntheses"]
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate system health: {e}")
            return {
                "score": 0.0,
                "status": "unknown",
                "error": str(e)
            }
    
    def get_provider_health(self, provider: VoiceProvider) -> Dict[str, Any]:
        """Get health metrics for a specific provider"""
        try:
            provider_name = provider.value
            
            usage_count = self.stats["provider_usage"].get(provider_name, 0)
            error_count = self.stats["provider_errors"].get(provider_name, 0)
            response_times = self.stats["provider_response_times"].get(provider_name, [])
            
            if usage_count == 0:
                return {
                    "status": "unused",
                    "usage_count": 0,
                    "error_rate": 0,
                    "avg_response_time": 0
                }
            
            error_rate = error_count / usage_count
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            
            # Determine status
            if error_rate == 0 and avg_response_time < 5.0:
                status = "healthy"
            elif error_rate < 0.1 and avg_response_time < 10.0:
                status = "good"
            elif error_rate < 0.3 and avg_response_time < 30.0:
                status = "degraded"
            else:
                status = "unhealthy"
            
            return {
                "status": status,
                "usage_count": usage_count,
                "error_count": error_count,
                "error_rate": error_rate,
                "avg_response_time": avg_response_time,
                "recent_response_times": response_times[-10:] if response_times else []
            }
            
        except Exception as e:
            logger.error(f"Failed to get provider health for {provider.value}: {e}")
            return {"status": "error", "error": str(e)}
    
    def reset_stats(self) -> None:
        """Reset all performance statistics"""
        try:
            self.stats = {
                "total_syntheses": 0,
                "total_processing_time": 0.0,
                "total_audio_duration": 0.0,
                "error_count": 0,
                "provider_usage": {},
                "provider_errors": {},
                "provider_response_times": {}
            }
            
            self.start_time = time.time()
            logger.info("Performance statistics reset")
            
        except Exception as e:
            logger.error(f"Failed to reset stats: {e}")
    
    def get_stats_summary(self) -> str:
        """Get a brief summary of performance stats"""
        try:
            metrics = self.get_performance_metrics()
            
            return (
                f"Syntheses: {metrics['total_syntheses']}, "
                f"Errors: {metrics['error_count']} ({metrics['error_rate']:.1%}), "
                f"Avg Time: {metrics['average_processing_time_s']:.2f}s, "
                f"Health: {metrics['system_health']['status']}"
            )
            
        except Exception as e:
            return f"Stats unavailable: {e}"
    
    def log_performance_summary(self) -> None:
        """Log a performance summary"""
        try:
            summary = self.get_stats_summary()
            health = self._calculate_system_health()
            
            if health["status"] == "healthy":
                logger.info(f"📊 Performance: {summary}")
            elif health["status"] == "degraded":
                logger.warning(f"⚠️ Performance degraded: {summary}")
            else:
                logger.error(f"❌ Performance issues: {summary}")
                
        except Exception as e:
            logger.error(f"Failed to log performance summary: {e}")
    
    def track_operation_start(self, operation_id: str) -> float:
        """Start tracking an operation and return start time"""
        start_time = time.time()
        logger.debug(f"Started tracking operation: {operation_id}")
        return start_time
    
    def track_operation_end(
        self,
        operation_id: str,
        start_time: float,
        provider: VoiceProvider,
        success: bool = True,
        audio_duration: Optional[float] = None
    ) -> float:
        """End tracking an operation and update stats"""
        end_time = time.time()
        processing_time = end_time - start_time
        
        self.update_synthesis_stats(provider, processing_time, audio_duration, success)
        
        logger.debug(f"Completed tracking operation: {operation_id} ({processing_time:.3f}s)")
        return processing_time 