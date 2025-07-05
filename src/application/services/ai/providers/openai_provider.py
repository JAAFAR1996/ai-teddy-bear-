"""
🤖 OpenAI Provider - Enterprise 2025
Complete OpenAI implementation with all features from existing OpenAI service
"""

import asyncio
import logging
import openai
from datetime import datetime
from typing import Any, Dict, List, Optional

from .base_provider import BaseAIProvider
from ..core import (
    AIProvider,
    AIRequest,
    AIResponse,
    EmotionResult,
    EmotionType,
    MessageCategory,
    ResponseSafety,
    ErrorType,
)

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseAIProvider):
    """
    OpenAI Provider implementation
    
    Features from original openai_service.py:
    - Multiple model support (GPT-4, GPT-3.5-turbo)
    - Advanced safety checking
    - Context-aware responses
    - Child-specific prompting
    - Token optimization
    - Rate limiting handling
    """
    
    def __init__(
        self,
        config: Dict[str, Any],
        max_retries: int = 3,
        timeout: float = 30.0,
        **kwargs
    ):
        super().__init__(
            provider_name="openai",
            config=config,
            max_retries=max_retries,
            timeout=timeout,
            **kwargs
        )
    
    def _initialize_provider(self, **kwargs) -> None:
        """Initialize OpenAI-specific settings"""
        self.api_key = self.config.get("api_key")
        self.organization = self.config.get("organization")
        self.default_model = self.config.get("model", "gpt-4")
        self.max_tokens = self.config.get("max_tokens", 150)
        self.temperature = self.config.get("temperature", 0.7)
        
        # Initialize OpenAI client
        openai.api_key = self.api_key
        if self.organization:
            openai.organization = self.organization
        
        # Model configurations
        self.model_configs = {
            "gpt-4": {
                "max_tokens": 8192,
                "cost_per_token": 0.00003,
                "safety_level": "high"
            },
            "gpt-3.5-turbo": {
                "max_tokens": 4096,
                "cost_per_token": 0.000002,
                "safety_level": "medium"
            }
        }
        
        # Child-specific prompting
        self.child_prompts = {
            "base_prompt": """
You are Teddy, a friendly AI companion for children. Always respond with:
- Age-appropriate language
- Encouraging and positive tone
- Educational value when possible
- Safety-first approach
- Empathy and understanding

Remember: You're talking to a child, so keep responses simple, fun, and safe.
""",
            "safety_rules": [
                "Never discuss adult topics",
                "Always redirect dangerous questions",
                "Encourage learning and curiosity",
                "Support emotional well-being",
                "Promote positive behavior"
            ]
        }
        
        logger.info(f"OpenAI provider initialized with model: {self.default_model}")
    
    async def _make_request(self, request: AIRequest) -> AIResponse:
        """Make request to OpenAI API"""
        try:
            # Prepare messages with child-specific context
            messages = self._prepare_messages(request)
            
            # Select appropriate model
            model = self._select_model(request)
            
            # Make the API call
            response = await self._call_openai_api(
                messages=messages,
                model=model,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                child_id=request.child_id
            )
            
            # Process response
            return self._process_openai_response(response, request, model)
            
        except Exception as e:
            logger.error(f"OpenAI request failed: {e}")
            raise
    
    def _prepare_messages(self, request: AIRequest) -> List[Dict[str, str]]:
        """Prepare messages for OpenAI API with child-specific context"""
        messages = []
        
        # System prompt with child context
        system_prompt = self._create_system_prompt(request)
        messages.append({"role": "system", "content": system_prompt})
        
        # Add conversation history if available
        if request.conversation_history:
            for msg in request.conversation_history[-5:]:  # Last 5 messages
                messages.append({"role": "user", "content": msg.get("user", "")})
                messages.append({"role": "assistant", "content": msg.get("assistant", "")})
        
        # Add current message
        messages.append({"role": "user", "content": request.message})
        
        return messages
    
    def _create_system_prompt(self, request: AIRequest) -> str:
        """Create child-specific system prompt"""
        base_prompt = self.child_prompts["base_prompt"]
        
        # Add child-specific context
        child_context = []
        if request.child_age:
            child_context.append(f"Child age: {request.child_age} years old")
        if request.child_name:
            child_context.append(f"Child name: {request.child_name}")
        if request.learning_level:
            child_context.append(f"Learning level: {request.learning_level}")
        if request.emotional_state:
            child_context.append(f"Emotional state: {request.emotional_state}")
        
        if child_context:
            context_str = "\\n".join(child_context)
            base_prompt += f"\\n\\nChild Context:\\n{context_str}"
        
        # Add safety rules
        safety_rules = "\\n".join(f"- {rule}" for rule in self.child_prompts["safety_rules"])
        base_prompt += f"\\n\\nSafety Rules:\\n{safety_rules}"
        
        return base_prompt
    
    def _select_model(self, request: AIRequest) -> str:
        """Select appropriate model based on request"""
        # Default to configured model
        model = self.default_model
        
        # Use GPT-4 for complex requests
        if len(request.message) > 100 or request.context.get("complexity", "normal") == "high":
            model = "gpt-4"
        
        # Use GPT-3.5 for simple requests to save costs
        elif len(request.message) < 50 and request.context.get("complexity", "normal") == "low":
            model = "gpt-3.5-turbo"
        
        return model
    
    async def _call_openai_api(
        self,
        messages: List[Dict[str, str]],
        model: str,
        max_tokens: int,
        temperature: float,
        child_id: str
    ) -> Dict[str, Any]:
        """Make async call to OpenAI API"""
        try:
            response = await openai.ChatCompletion.acreate(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                presence_penalty=0.1,
                frequency_penalty=0.1,
                user=child_id  # For tracking and safety
            )
            return response
            
        except openai.error.RateLimitError as e:
            logger.warning(f"Rate limit exceeded for child {child_id}")
            raise Exception(f"Rate limit exceeded: {e}")
        
        except openai.error.AuthenticationError as e:
            logger.error(f"Authentication failed: {e}")
            raise Exception(f"Authentication error: {e}")
        
        except openai.error.InvalidRequestError as e:
            logger.error(f"Invalid request: {e}")
            raise Exception(f"Invalid request: {e}")
        
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            raise Exception(f"API call failed: {e}")
    
    def _process_openai_response(
        self,
        response: Dict[str, Any],
        request: AIRequest,
        model: str
    ) -> AIResponse:
        """Process OpenAI response into AIResponse"""
        try:
            # Extract response text
            message = response["choices"][0]["message"]["content"].strip()
            
            # Extract usage information
            usage = response.get("usage", {})
            tokens_used = usage.get("total_tokens", 0)
            
            # Calculate confidence based on response quality
            confidence = self._calculate_confidence(message, response)
            
            # Create AIResponse
            ai_response = AIResponse(
                text=message,
                child_id=request.child_id,
                session_id=request.session_id or "session",
                confidence=confidence,
                provider=AIProvider.OPENAI,
                model=model,
                tokens_used=tokens_used,
                processing_time_ms=0,  # Will be set by base class
                created_at=datetime.utcnow()
            )
            
            return ai_response
            
        except Exception as e:
            logger.error(f"Failed to process OpenAI response: {e}")
            raise
    
    def _calculate_confidence(self, message: str, response: Dict[str, Any]) -> float:
        """Calculate confidence score based on response quality"""
        confidence = 0.8  # Base confidence
        
        # Adjust based on response length
        if len(message) < 10:
            confidence -= 0.2
        elif len(message) > 100:
            confidence += 0.1
        
        # Adjust based on finish reason
        finish_reason = response.get("choices", [{}])[0].get("finish_reason")
        if finish_reason == "stop":
            confidence += 0.1
        elif finish_reason == "length":
            confidence -= 0.1
        
        return min(1.0, max(0.0, confidence))
    
    async def _check_provider_health(self) -> bool:
        """Check OpenAI API health"""
        try:
            # Simple health check request
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            return True
            
        except Exception as e:
            logger.error(f"OpenAI health check failed: {e}")
            return False
    
    async def _check_response_safety(self, text: str) -> Dict[str, Any]:
        """Enhanced safety checking using OpenAI moderation"""
        try:
            # Use OpenAI's moderation endpoint
            moderation_response = await openai.Moderation.acreate(input=text)
            
            results = moderation_response["results"][0]
            
            # Check if content is flagged
            is_flagged = results["flagged"]
            
            # Get detailed categories
            categories = results.get("categories", {})
            flagged_categories = [cat for cat, flagged in categories.items() if flagged]
            
            # Calculate safety score
            category_scores = results.get("category_scores", {})
            max_score = max(category_scores.values()) if category_scores else 0.0
            safety_score = 1.0 - max_score
            
            return {
                "is_safe": not is_flagged,
                "safety_score": safety_score,
                "flagged_categories": flagged_categories,
                "risk_level": "high" if is_flagged else "low",
                "explanation": f"OpenAI moderation flagged: {', '.join(flagged_categories)}" if flagged_categories else "Content is safe",
                "recommendations": ["Review content"] if is_flagged else []
            }
            
        except Exception as e:
            logger.warning(f"OpenAI moderation check failed: {e}")
            # Fallback to base safety check
            return await super()._check_response_safety(text)
    
    async def _analyze_emotion(self, text: str) -> EmotionResult:
        """Enhanced emotion analysis using OpenAI"""
        try:
            # Use a quick OpenAI call for emotion analysis
            emotion_prompt = f"""
Analyze the emotion in this text from a child's perspective.
Text: "{text}"

Respond with ONLY the primary emotion from this list:
happy, sad, angry, fearful, surprised, curious, neutral, excited, anxious, confused

Primary emotion:"""
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": emotion_prompt}],
                max_tokens=10,
                temperature=0.1
            )
            
            emotion_text = response["choices"][0]["message"]["content"].strip().lower()
            
            # Map to EmotionType
            emotion_mapping = {
                "happy": EmotionType.HAPPY,
                "sad": EmotionType.SAD,
                "angry": EmotionType.ANGRY,
                "fearful": EmotionType.FEARFUL,
                "surprised": EmotionType.SURPRISED,
                "curious": EmotionType.CURIOUS,
                "neutral": EmotionType.NEUTRAL,
                "excited": EmotionType.EXCITED,
                "anxious": EmotionType.ANXIOUS,
                "confused": EmotionType.CONFUSED
            }
            
            primary_emotion = emotion_mapping.get(emotion_text, EmotionType.NEUTRAL)
            
            return EmotionResult(
                primary_emotion=primary_emotion,
                confidence=0.85,
                emotions_detected={emotion_text: 0.85},
                analysis_method="openai"
            )
            
        except Exception as e:
            logger.warning(f"OpenAI emotion analysis failed: {e}")
            # Fallback to base emotion analysis
            return await super()._analyze_emotion(text)
    
    async def _categorize_message(self, text: str) -> MessageCategory:
        """Enhanced message categorization using OpenAI"""
        try:
            category_prompt = f"""
Categorize this message from a child's conversation.
Text: "{text}"

Respond with ONLY one category:
general_conversation, educational, emotional_support, storytelling, play_activity, 
safety_concern, behavioral_guidance, learning_assessment, social_skills, 
creative_expression, problem_solving, daily_routine

Category:"""
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": category_prompt}],
                max_tokens=10,
                temperature=0.1
            )
            
            category_text = response["choices"][0]["message"]["content"].strip().lower()
            
            # Map to MessageCategory
            try:
                return MessageCategory(category_text)
            except ValueError:
                return MessageCategory.GENERAL_CONVERSATION
            
        except Exception as e:
            logger.warning(f"OpenAI categorization failed: {e}")
            # Fallback to base categorization
            return await super()._categorize_message(text)
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get provider-specific information"""
        return {
            "provider": "OpenAI",
            "default_model": self.default_model,
            "available_models": list(self.model_configs.keys()),
            "features": [
                "Multiple models",
                "Content moderation",
                "Child-safe prompting",
                "Conversation context",
                "Emotion analysis",
                "Safety checking",
                "Token optimization"
            ],
            "limits": {
                "max_tokens": self.model_configs[self.default_model]["max_tokens"],
                "rate_limit": "3500 requests/minute",
                "context_window": self.model_configs[self.default_model]["max_tokens"]
            }
        }
    
    def estimate_cost(self, request: AIRequest) -> float:
        """Estimate cost for request"""
        model = self._select_model(request)
        config = self.model_configs.get(model, self.model_configs["gpt-3.5-turbo"])
        
        # Estimate tokens (rough approximation)
        estimated_tokens = len(request.message.split()) * 1.3  # Words to tokens ratio
        estimated_tokens += request.max_tokens  # Response tokens
        
        return estimated_tokens * config["cost_per_token"] 