"""
Cache Integration Service for AI Teddy Bear System.

This service provides seamless integration between the multi-layer caching system
and existing AI services for optimal performance.

Performance Team Implementation - Task 12
Author: Performance Team Lead
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Union, Callable, Type
from dataclasses import dataclass
from datetime import datetime, timedelta
import hashlib
import json

try:
    from .multi_layer_cache import (
        MultiLayerCache, CacheConfig, ContentType, CacheLayer, CacheMetrics
    )
    MULTI_LAYER_CACHE_AVAILABLE = True
except ImportError:
    MULTI_LAYER_CACHE_AVAILABLE = False
    MultiLayerCache = None

logger = logging.getLogger(__name__)


@dataclass
class CacheStrategy:
    """Cache strategy configuration for different operations."""
    content_type: ContentType
    ttl_seconds: int
    use_compression: bool = True
    cache_on_miss: bool = True
    invalidate_on_update: bool = True
    warm_cache: bool = False
    

class CacheIntegrationService:
    """Service for integrating caching with AI components."""
    
    def __init__(self, cache_config: Optional[CacheConfig] = None):
        self.cache_config = cache_config or CacheConfig()
        self.cache_system: Optional[MultiLayerCache] = None
        
        # Cache strategies for different operations
        self.strategies = self._setup_cache_strategies()
        
        # Performance tracking
        self.performance_stats = {
            "cache_hits": 0,
            "cache_misses": 0,
            "compute_time_saved_ms": 0.0,
            "operations_cached": 0
        }
        
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def initialize(self):
        """Initialize cache integration service."""
        try:
            if not MULTI_LAYER_CACHE_AVAILABLE:
                self.logger.warning("Multi-layer cache not available")
                return False
            
            self.cache_system = MultiLayerCache(self.cache_config)
            await self.cache_system.initialize()
            
            self.logger.info("Cache integration service initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Cache initialization failed: {e}")
            return False
    
    async def cache_audio_transcription(
        self,
        audio_hash: str,
        transcription_fn: Callable,
        *args,
        **kwargs
    ) -> Optional[str]:
        """Cache audio transcription results."""
        if not self.cache_system:
            return await transcription_fn(*args, **kwargs)
        
        strategy = self.strategies["audio_transcription"]
        cache_key = f"transcription:{audio_hash}"
        
        start_time = time.time()
        
        # Try cache first
        cached_result = await self.cache_system.get_with_fallback(
            cache_key,
            strategy.content_type
        )
        
        if cached_result is not None:
            self.performance_stats["cache_hits"] += 1
            self.logger.debug(f"Transcription cache hit: {audio_hash[:16]}...")
            return cached_result
        
        # Compute transcription
        self.performance_stats["cache_misses"] += 1
        result = await transcription_fn(*args, **kwargs)
        
        # Cache result
        if result and strategy.cache_on_miss:
            await self.cache_system.set_multi_layer(
                cache_key,
                result,
                strategy.content_type
            )
            self.performance_stats["operations_cached"] += 1
        
        compute_time = (time.time() - start_time) * 1000
        self.performance_stats["compute_time_saved_ms"] += compute_time
        
        return result
    
    async def cache_ai_response(
        self,
        conversation_context: Dict[str, Any],
        ai_response_fn: Callable,
        *args,
        **kwargs
    ) -> Optional[str]:
        """Cache AI response results."""
        if not self.cache_system:
            return await ai_response_fn(*args, **kwargs)
        
        strategy = self.strategies["ai_response"]
        
        # Generate context-based cache key
        context_hash = self._hash_conversation_context(conversation_context)
        cache_key = f"ai_response:{context_hash}"
        
        start_time = time.time()
        
        # Try cache first
        cached_result = await self.cache_system.get_with_fallback(
            cache_key,
            strategy.content_type
        )
        
        if cached_result is not None:
            self.performance_stats["cache_hits"] += 1
            self.logger.debug(f"AI response cache hit: {context_hash[:16]}...")
            return cached_result
        
        # Generate AI response
        self.performance_stats["cache_misses"] += 1
        result = await ai_response_fn(*args, **kwargs)
        
        # Cache result
        if result and strategy.cache_on_miss:
            await self.cache_system.set_multi_layer(
                cache_key,
                result,
                strategy.content_type
            )
            self.performance_stats["operations_cached"] += 1
        
        compute_time = (time.time() - start_time) * 1000
        self.performance_stats["compute_time_saved_ms"] += compute_time
        
        return result
    
    async def cache_emotion_analysis(
        self,
        audio_features: Dict[str, Any],
        emotion_analysis_fn: Callable,
        *args,
        **kwargs
    ) -> Optional[Dict[str, float]]:
        """Cache emotion analysis results."""
        if not self.cache_system:
            return await emotion_analysis_fn(*args, **kwargs)
        
        strategy = self.strategies["emotion_analysis"]
        
        # Generate features-based cache key
        features_hash = self._hash_audio_features(audio_features)
        cache_key = f"emotion:{features_hash}"
        
        start_time = time.time()
        
        # Try cache first
        cached_result = await self.cache_system.get_with_fallback(
            cache_key,
            strategy.content_type
        )
        
        if cached_result is not None:
            self.performance_stats["cache_hits"] += 1
            self.logger.debug(f"Emotion analysis cache hit: {features_hash[:16]}...")
            return cached_result
        
        # Perform emotion analysis
        self.performance_stats["cache_misses"] += 1
        result = await emotion_analysis_fn(*args, **kwargs)
        
        # Cache result
        if result and strategy.cache_on_miss:
            await self.cache_system.set_multi_layer(
                cache_key,
                result,
                strategy.content_type
            )
            self.performance_stats["operations_cached"] += 1
        
        compute_time = (time.time() - start_time) * 1000
        self.performance_stats["compute_time_saved_ms"] += compute_time
        
        return result
    
    async def cache_voice_synthesis(
        self,
        text: str,
        voice_config: Dict[str, Any],
        synthesis_fn: Callable,
        *args,
        **kwargs
    ) -> Optional[bytes]:
        """Cache voice synthesis results."""
        if not self.cache_system:
            return await synthesis_fn(*args, **kwargs)
        
        strategy = self.strategies["voice_synthesis"]
        
        # Generate synthesis cache key
        synthesis_hash = self._hash_synthesis_params(text, voice_config)
        cache_key = f"tts:{synthesis_hash}"
        
        start_time = time.time()
        
        # Try cache first
        cached_result = await self.cache_system.get_with_fallback(
            cache_key,
            strategy.content_type
        )
        
        if cached_result is not None:
            self.performance_stats["cache_hits"] += 1
            self.logger.debug(f"Voice synthesis cache hit: {synthesis_hash[:16]}...")
            return cached_result
        
        # Perform voice synthesis
        self.performance_stats["cache_misses"] += 1
        result = await synthesis_fn(*args, **kwargs)
        
        # Cache result
        if result and strategy.cache_on_miss:
            await self.cache_system.set_multi_layer(
                cache_key,
                result,
                strategy.content_type
            )
            self.performance_stats["operations_cached"] += 1
        
        compute_time = (time.time() - start_time) * 1000
        self.performance_stats["compute_time_saved_ms"] += compute_time
        
        return result
    
    async def cache_user_session(
        self,
        user_id: str,
        session_data: Dict[str, Any],
        ttl_override: Optional[int] = None
    ) -> bool:
        """Cache user session data."""
        if not self.cache_system:
            return False
        
        strategy = self.strategies["user_session"]
        cache_key = f"session:{user_id}"
        
        ttl = ttl_override or strategy.ttl_seconds
        
        return await self.cache_system.set_multi_layer(
            cache_key,
            session_data,
            strategy.content_type
        )
    
    async def get_user_session(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get cached user session data."""
        if not self.cache_system:
            return None
        
        strategy = self.strategies["user_session"]
        cache_key = f"session:{user_id}"
        
        return await self.cache_system.get_with_fallback(
            cache_key,
            strategy.content_type
        )
    
    async def cache_configuration(
        self,
        config_key: str,
        config_data: Dict[str, Any]
    ) -> bool:
        """Cache configuration data."""
        if not self.cache_system:
            return False
        
        strategy = self.strategies["configuration"]
        cache_key = f"config:{config_key}"
        
        return await self.cache_system.set_multi_layer(
            cache_key,
            config_data,
            strategy.content_type
        )
    
    async def get_configuration(self, config_key: str) -> Optional[Dict[str, Any]]:
        """Get cached configuration data."""
        if not self.cache_system:
            return None
        
        strategy = self.strategies["configuration"]
        cache_key = f"config:{config_key}"
        
        return await self.cache_system.get_with_fallback(
            cache_key,
            strategy.content_type
        )
    
    async def invalidate_user_cache(self, user_id: str) -> bool:
        """Invalidate all cache entries for a user."""
        if not self.cache_system:
            return False
        
        patterns = [
            f"session:{user_id}",
            f"ai_response:*{user_id}*",
            f"emotion:*{user_id}*"
        ]
        
        success = True
        for pattern in patterns:
            try:
                # For pattern-based invalidation, we need to implement this
                # in the cache system or maintain an index
                await self.cache_system.invalidate(pattern)
            except Exception as e:
                self.logger.error(f"Cache invalidation error for {pattern}: {e}")
                success = False
        
        return success
    
    async def warm_cache_for_user(
        self,
        user_id: str,
        user_data: Dict[str, Any]
    ) -> int:
        """Warm cache with user-specific data."""
        if not self.cache_system:
            return 0
        
        cache_entries = []
        
        # Session data
        if "session" in user_data:
            cache_entries.append((
                f"session:{user_id}",
                user_data["session"],
                ContentType.USER_SESSION
            ))
        
        # Frequently used configurations
        if "preferences" in user_data:
            cache_entries.append((
                f"config:user_preferences:{user_id}",
                user_data["preferences"],
                ContentType.CONFIGURATION
            ))
        
        # Pre-computed responses for common scenarios
        if "common_responses" in user_data:
            for scenario, response in user_data["common_responses"].items():
                cache_entries.append((
                    f"ai_response:common:{user_id}:{scenario}",
                    response,
                    ContentType.AI_RESPONSE
                ))
        
        return await self.cache_system.warm_cache(cache_entries)
    
    def _setup_cache_strategies(self) -> Dict[str, CacheStrategy]:
        """Setup cache strategies for different operations."""
        return {
            "audio_transcription": CacheStrategy(
                content_type=ContentType.AUDIO_TRANSCRIPTION,
                ttl_seconds=3600,  # 1 hour
                use_compression=True,
                cache_on_miss=True,
                invalidate_on_update=False,
                warm_cache=False
            ),
            "ai_response": CacheStrategy(
                content_type=ContentType.AI_RESPONSE,
                ttl_seconds=1800,  # 30 minutes
                use_compression=True,
                cache_on_miss=True,
                invalidate_on_update=True,
                warm_cache=True
            ),
            "emotion_analysis": CacheStrategy(
                content_type=ContentType.EMOTION_ANALYSIS,
                ttl_seconds=900,   # 15 minutes
                use_compression=False,
                cache_on_miss=True,
                invalidate_on_update=False,
                warm_cache=False
            ),
            "voice_synthesis": CacheStrategy(
                content_type=ContentType.VOICE_SYNTHESIS,
                ttl_seconds=86400,  # 24 hours
                use_compression=True,
                cache_on_miss=True,
                invalidate_on_update=False,
                warm_cache=True
            ),
            "user_session": CacheStrategy(
                content_type=ContentType.USER_SESSION,
                ttl_seconds=1800,   # 30 minutes
                use_compression=False,
                cache_on_miss=True,
                invalidate_on_update=True,
                warm_cache=False
            ),
            "configuration": CacheStrategy(
                content_type=ContentType.CONFIGURATION,
                ttl_seconds=3600,   # 1 hour
                use_compression=False,
                cache_on_miss=True,
                invalidate_on_update=True,
                warm_cache=True
            )
        }
    
    def _hash_conversation_context(self, context: Dict[str, Any]) -> str:
        """Generate hash for conversation context."""
        # Extract key elements for cache key generation
        key_elements = {
            "user_message": context.get("user_message", ""),
            "emotion": context.get("emotion", ""),
            "child_age": context.get("child_age", ""),
            "conversation_type": context.get("conversation_type", "")
        }
        
        context_str = json.dumps(key_elements, sort_keys=True)
        return hashlib.sha256(context_str.encode()).hexdigest()
    
    def _hash_audio_features(self, features: Dict[str, Any]) -> str:
        """Generate hash for audio features."""
        # Use key audio features for caching
        key_features = {
            "mfcc": features.get("mfcc", [])[:13],  # First 13 MFCC coefficients
            "spectral_centroid": features.get("spectral_centroid", 0),
            "zero_crossing_rate": features.get("zero_crossing_rate", 0),
            "duration": round(features.get("duration", 0), 1)  # Round to 0.1s
        }
        
        features_str = json.dumps(key_features, sort_keys=True)
        return hashlib.sha256(features_str.encode()).hexdigest()
    
    def _hash_synthesis_params(self, text: str, voice_config: Dict[str, Any]) -> str:
        """Generate hash for voice synthesis parameters."""
        synthesis_params = {
            "text": text,
            "voice": voice_config.get("voice", "default"),
            "speed": voice_config.get("speed", 1.0),
            "pitch": voice_config.get("pitch", 1.0),
            "emotion": voice_config.get("emotion", "neutral")
        }
        
        params_str = json.dumps(synthesis_params, sort_keys=True)
        return hashlib.sha256(params_str.encode()).hexdigest()
    
    async def get_cache_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive cache performance report."""
        if not self.cache_system:
            return {"status": "cache_system_unavailable"}
        
        # Get cache system metrics
        cache_metrics = self.cache_system.get_performance_metrics()
        
        # Calculate integration-specific metrics
        total_operations = self.performance_stats["cache_hits"] + self.performance_stats["cache_misses"]
        integration_hit_rate = (
            self.performance_stats["cache_hits"] / total_operations
            if total_operations > 0 else 0.0
        )
        
        average_time_saved = (
            self.performance_stats["compute_time_saved_ms"] / max(1, self.performance_stats["cache_hits"])
        )
        
        return {
            "integration_stats": {
                "total_operations": total_operations,
                "cache_hits": self.performance_stats["cache_hits"],
                "cache_misses": self.performance_stats["cache_misses"],
                "hit_rate": integration_hit_rate,
                "operations_cached": self.performance_stats["operations_cached"],
                "average_time_saved_ms": average_time_saved,
                "total_time_saved_ms": self.performance_stats["compute_time_saved_ms"]
            },
            "cache_system_metrics": cache_metrics,
            "strategy_summary": {
                strategy_name: {
                    "content_type": strategy.content_type.value,
                    "ttl_seconds": strategy.ttl_seconds,
                    "use_compression": strategy.use_compression,
                    "cache_on_miss": strategy.cache_on_miss
                }
                for strategy_name, strategy in self.strategies.items()
            }
        }
    
    async def optimize_cache_settings(self) -> Dict[str, Any]:
        """Analyze performance and suggest cache optimizations."""
        if not self.cache_system:
            return {"status": "cache_system_unavailable"}
        
        metrics = await self.get_cache_performance_report()
        suggestions = []
        
        # Analyze hit rates
        cache_metrics = metrics.get("cache_system_metrics", {})
        hit_rates = cache_metrics.get("hit_rate_by_layer", {})
        
        if hit_rates.get("l1", 0) < 0.3:
            suggestions.append({
                "type": "l1_size_increase",
                "message": "L1 cache hit rate is low. Consider increasing L1 cache size.",
                "current_rate": hit_rates.get("l1", 0),
                "recommended_action": "Increase l1_max_size_mb"
            })
        
        if hit_rates.get("l2", 0) < 0.5:
            suggestions.append({
                "type": "l2_ttl_optimization",
                "message": "L2 cache hit rate is low. Consider increasing TTL for frequently accessed content.",
                "current_rate": hit_rates.get("l2", 0),
                "recommended_action": "Increase TTL for AI responses and transcriptions"
            })
        
        # Analyze latency
        latencies = cache_metrics.get("latency_by_layer", {})
        if latencies.get("l2_avg_ms", 0) > 50:
            suggestions.append({
                "type": "redis_optimization",
                "message": "L2 Redis latency is high. Consider Redis optimization or clustering.",
                "current_latency": latencies.get("l2_avg_ms", 0),
                "recommended_action": "Optimize Redis configuration or add Redis cluster"
            })
        
        # Analyze integration hit rate
        integration_hit_rate = metrics.get("integration_stats", {}).get("hit_rate", 0)
        if integration_hit_rate < 0.4:
            suggestions.append({
                "type": "cache_warming",
                "message": "Integration hit rate is low. Consider implementing cache warming.",
                "current_rate": integration_hit_rate,
                "recommended_action": "Enable cache warming for frequently accessed content"
            })
        
        return {
            "analysis_timestamp": datetime.now().isoformat(),
            "performance_metrics": metrics,
            "optimization_suggestions": suggestions,
            "recommended_config_changes": self._generate_config_recommendations(suggestions)
        }
    
    def _generate_config_recommendations(self, suggestions: List[Dict]) -> Dict[str, Any]:
        """Generate specific configuration recommendations."""
        recommendations = {}
        
        for suggestion in suggestions:
            if suggestion["type"] == "l1_size_increase":
                recommendations["l1_max_size_mb"] = self.cache_config.l1_max_size_mb * 2
                
            elif suggestion["type"] == "l2_ttl_optimization":
                recommendations["ai_response_ttl"] = 3600  # Increase to 1 hour
                recommendations["transcription_ttl"] = 7200  # Increase to 2 hours
                
            elif suggestion["type"] == "redis_optimization":
                recommendations["l2_max_connections"] = min(200, self.cache_config.l2_max_connections * 2)
                recommendations["enable_redis_cluster"] = True
                
            elif suggestion["type"] == "cache_warming":
                recommendations["cache_warming_enabled"] = True
                recommendations["cache_warming_interval"] = 300  # 5 minutes
        
        return recommendations
    
    async def cleanup(self):
        """Cleanup cache integration service."""
        if self.cache_system:
            await self.cache_system.cleanup()
        
        self.logger.info("Cache integration service cleanup completed")


# Factory function for easy integration
async def create_cache_integration_service(
    config: Optional[CacheConfig] = None
) -> CacheIntegrationService:
    """Factory function to create and initialize cache integration service."""
    service = CacheIntegrationService(config)
    await service.initialize()
    return service 