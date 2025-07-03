"""
🏗️ Base AI Provider - Enterprise 2025
Base class combining all common features from existing providers
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..core import (
    AIProvider,
    AIRequest,
    AIResponse,
    EmotionResult,
    PerformanceMetrics,
    SafetyCheck,
    ErrorType,
    HealthStatus,
    ResponseSafety,
    MessageCategory,
    IAIProvider,
)

logger = logging.getLogger(__name__)


class BaseAIProvider(ABC):
    """
    Base AI Provider with enterprise features
    
    Combines all common functionality from existing providers:
    - OpenAI service features
    - Modern AI service capabilities
    - Refactored AI service patterns
    - LLM service utilities
    - Factory pattern support
    """
    
    def __init__(
        self,
        provider_name: str,
        config: Dict[str, Any],
        max_retries: int = 3,
        timeout: float = 30.0,
        **kwargs
    ):
        self.provider_name = provider_name
        self.config = config
        self.max_retries = max_retries
        self.timeout = timeout
        self.metrics = PerformanceMetrics()
        self.is_healthy = True
        self.last_health_check = datetime.utcnow()
        
        # Initialize provider-specific settings
        self._initialize_provider(**kwargs)
        
        logger.info(f"Initialized {provider_name} provider")
    
    @abstractmethod
    def _initialize_provider(self, **kwargs) -> None:
        """Initialize provider-specific settings"""
        pass
    
    @abstractmethod
    async def _make_request(self, request: AIRequest) -> AIResponse:
        """Make actual API request to the provider"""
        pass
    
    @abstractmethod
    async def _check_provider_health(self) -> bool:
        """Check provider-specific health"""
        pass
    
    async def generate_response(self, request: AIRequest) -> AIResponse:
        """
        Generate AI response with comprehensive error handling
        
        Features from all existing implementations:
        - Retry logic (from modern_ai_service)
        - Safety checking (from openai_service)
        - Performance metrics (from refactored_ai_service)
        - Error handling (from all services)
        """
        start_time = time.time()
        
        try:
            self.metrics.total_requests += 1
            
            # Pre-processing validations
            await self._validate_request(request)
            
            # Execute request with retry logic
            response = await self._execute_with_retry(request)
            
            # Post-processing
            response = await self._post_process_response(response, request)
            
            # Update metrics
            processing_time = (time.time() - start_time) * 1000
            self._update_success_metrics(processing_time, response)
            
            return response
            
        except Exception as e:
            # Update error metrics
            processing_time = (time.time() - start_time) * 1000
            self._update_error_metrics(processing_time, str(e))
            
            # Create fallback response
            return await self._create_error_response(request, str(e))
    
    async def _validate_request(self, request: AIRequest) -> None:
        """Validate request before processing"""
        if not request.message.strip():
            raise ValueError("Message cannot be empty")
        
        if not request.child_id:
            raise ValueError("Child ID is required")
        
        if len(request.message) > 5000:
            raise ValueError("Message too long")
    
    async def _execute_with_retry(self, request: AIRequest) -> AIResponse:
        """Execute request with retry logic"""
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                # Add timeout to the request
                return await asyncio.wait_for(
                    self._make_request(request),
                    timeout=self.timeout
                )
            except asyncio.TimeoutError:
                last_exception = TimeoutError(f"Request timed out after {self.timeout}s")
                logger.warning(f"Attempt {attempt + 1} timed out")
            except Exception as e:
                last_exception = e
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                
                # Exponential backoff
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
        
        # All retries failed
        raise last_exception
    
    async def _post_process_response(
        self, 
        response: AIResponse, 
        request: AIRequest
    ) -> AIResponse:
        """Post-process response with safety checks and enhancements"""
        
        # Safety checking
        if request.require_safety_check:
            safety_check = await self._check_response_safety(response.text)
            response.safety_score = safety_check.safety_score
            response.safety_level = self._get_safety_level(safety_check)
        
        # Emotion analysis
        emotion_result = await self._analyze_emotion(response.text)
        response.emotion = emotion_result.primary_emotion.value
        
        # Message categorization
        response.category = await self._categorize_message(response.text)
        
        return response
    
    async def _check_response_safety(self, text: str) -> SafetyCheck:
        """Check response safety (basic implementation)"""
        # Basic safety keywords check
        unsafe_keywords = [
            "violence", "harmful", "dangerous", "inappropriate",
            "scary", "frightening", "adult content"
        ]
        
        flagged = []
        for keyword in unsafe_keywords:
            if keyword.lower() in text.lower():
                flagged.append(keyword)
        
        safety_score = 1.0 - (len(flagged) * 0.2)
        
        return SafetyCheck(
            is_safe=len(flagged) == 0,
            safety_score=max(0.0, safety_score),
            flagged_categories=flagged,
            risk_level="high" if flagged else "low"
        )
    
    async def _analyze_emotion(self, text: str) -> EmotionResult:
        """Basic emotion analysis"""
        # Simple emotion detection
        emotion_keywords = {
            "happy": ["happy", "joy", "excited", "glad", "wonderful"],
            "sad": ["sad", "unhappy", "disappointed", "upset"],
            "angry": ["angry", "mad", "frustrated", "annoyed"],
            "curious": ["curious", "wonder", "why", "how", "what"],
            "neutral": []
        }
        
        detected = {}
        for emotion, keywords in emotion_keywords.items():
            count = sum(1 for keyword in keywords if keyword in text.lower())
            if count > 0:
                detected[emotion] = count / len(keywords)
        
        if not detected:
            detected["neutral"] = 1.0
        
        primary_emotion = max(detected, key=detected.get)
        
        from ..core.enums import EmotionType
        return EmotionResult(
            primary_emotion=EmotionType(primary_emotion),
            confidence=detected[primary_emotion],
            emotions_detected=detected
        )
    
    async def _categorize_message(self, text: str) -> MessageCategory:
        """Basic message categorization"""
        # Simple categorization based on content
        if any(word in text.lower() for word in ["learn", "teach", "explain"]):
            return MessageCategory.EDUCATIONAL
        elif any(word in text.lower() for word in ["story", "once upon", "tale"]):
            return MessageCategory.STORYTELLING
        elif any(word in text.lower() for word in ["play", "game", "fun"]):
            return MessageCategory.PLAY_ACTIVITY
        elif any(word in text.lower() for word in ["feel", "emotion", "upset"]):
            return MessageCategory.EMOTIONAL_SUPPORT
        else:
            return MessageCategory.GENERAL_CONVERSATION
    
    def _get_safety_level(self, safety_check: SafetyCheck) -> ResponseSafety:
        """Convert safety check to safety level"""
        if safety_check.safety_score >= 0.8:
            return ResponseSafety.SAFE
        elif safety_check.safety_score >= 0.5:
            return ResponseSafety.CAUTION
        else:
            return ResponseSafety.UNSAFE
    
    async def _create_error_response(self, request: AIRequest, error: str) -> AIResponse:
        """Create error fallback response"""
        return AIResponse(
            text="I'm sorry, I'm having trouble right now. Let's try again later!",
            child_id=request.child_id,
            session_id=request.session_id or "error",
            provider=AIProvider(self.provider_name),
            error=error,
            safety_level=ResponseSafety.SAFE,
            category=MessageCategory.GENERAL_CONVERSATION
        )
    
    def _update_success_metrics(self, processing_time: float, response: AIResponse) -> None:
        """Update success metrics"""
        self.metrics.successful_requests += 1
        self.metrics.total_processing_time_ms += processing_time
        
        # Update timing metrics
        if self.metrics.min_response_time_ms == 0:
            self.metrics.min_response_time_ms = processing_time
        else:
            self.metrics.min_response_time_ms = min(
                self.metrics.min_response_time_ms, processing_time
            )
        
        self.metrics.max_response_time_ms = max(
            self.metrics.max_response_time_ms, processing_time
        )
        
        # Calculate average
        if self.metrics.successful_requests > 0:
            self.metrics.average_response_time_ms = (
                self.metrics.total_processing_time_ms / self.metrics.successful_requests
            )
        
        # Update provider usage
        provider_key = self.provider_name
        self.metrics.provider_usage[provider_key] = (
            self.metrics.provider_usage.get(provider_key, 0) + 1
        )
        
        # Update token usage
        self.metrics.total_tokens_used += response.tokens_used
        if self.metrics.total_requests > 0:
            self.metrics.average_tokens_per_request = (
                self.metrics.total_tokens_used / self.metrics.total_requests
            )
        
        # Update safety metrics
        self.metrics.safety_checks_performed += 1
        if response.safety_level == ResponseSafety.UNSAFE:
            self.metrics.unsafe_content_blocked += 1
    
    def _update_error_metrics(self, processing_time: float, error: str) -> None:
        """Update error metrics"""
        self.metrics.failed_requests += 1
        
        # Update provider errors
        provider_key = self.provider_name
        self.metrics.provider_errors[provider_key] = (
            self.metrics.provider_errors.get(provider_key, 0) + 1
        )
        
        # Update error breakdown
        error_type = self._classify_error(error)
        self.metrics.error_breakdown[error_type] = (
            self.metrics.error_breakdown.get(error_type, 0) + 1
        )
        
        # Check for rate limiting
        if "rate limit" in error.lower():
            self.metrics.rate_limit_incidents += 1
    
    def _classify_error(self, error: str) -> str:
        """Classify error type"""
        error_lower = error.lower()
        
        if "timeout" in error_lower:
            return ErrorType.TIMEOUT.value
        elif "rate limit" in error_lower:
            return ErrorType.RATE_LIMIT.value
        elif "network" in error_lower:
            return ErrorType.NETWORK_ERROR.value
        elif "authentication" in error_lower:
            return ErrorType.AUTHENTICATION_ERROR.value
        elif "permission" in error_lower:
            return ErrorType.PERMISSION_DENIED.value
        else:
            return ErrorType.INTERNAL_ERROR.value
    
    async def check_safety(self, content: str) -> str:
        """Check content safety - interface implementation"""
        safety_check = await self._check_response_safety(content)
        return "safe" if safety_check.is_safe else "unsafe"
    
    async def health_check(self) -> bool:
        """Comprehensive health check"""
        try:
            # Check provider-specific health
            provider_healthy = await self._check_provider_health()
            
            # Update health status
            self.is_healthy = provider_healthy
            self.last_health_check = datetime.utcnow()
            
            return provider_healthy
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            self.is_healthy = False
            return False
    
    async def get_usage_metrics(self) -> Dict[str, Any]:
        """Get usage metrics - interface implementation"""
        return self.metrics.to_dict()
    
    def get_health_status(self) -> HealthStatus:
        """Get current health status"""
        if not self.is_healthy:
            return HealthStatus.UNHEALTHY
        
        # Check if health check is recent
        time_since_check = (datetime.utcnow() - self.last_health_check).total_seconds()
        if time_since_check > 300:  # 5 minutes
            return HealthStatus.UNKNOWN
        
        # Check error rate
        error_rate = self.metrics.error_rate
        if error_rate > 50:
            return HealthStatus.CRITICAL
        elif error_rate > 20:
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.HEALTHY
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        return {
            "provider": self.provider_name,
            "health_status": self.get_health_status().value,
            "total_requests": self.metrics.total_requests,
            "success_rate": self.metrics.success_rate,
            "average_response_time": self.metrics.average_response_time_ms,
            "last_health_check": self.last_health_check.isoformat(),
            "is_healthy": self.is_healthy
        } 