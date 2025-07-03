"""
🔍 LLM Parameter Validation Services
خدمات التحقق من صحة معاملات LLM - مستخرجة من الملف الأساسي

✅ Single Responsibility: Parameter validation only
✅ Low Cyclomatic Complexity: Each method has 1-2 branches max
✅ High Cohesion: All methods related to validation
✅ Easy to test and maintain
"""

from dataclasses import dataclass
from typing import Optional
from enum import Enum


# Mock classes for standalone operation
class LLMProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"


class Conversation:
    """Mock conversation class for validation"""
    def __init__(self, messages=None):
        self.messages = messages or []


class LLMParameterValidationService:
    """
    مسؤولية واحدة: التحقق من صحة parameters الخاصة بـ LLM
    Extracted from main factory to achieve High Cohesion
    """
    
    @staticmethod
    def validate_required_conversation(conversation) -> None:
        """Validate that conversation is provided and valid"""
        if not conversation:
            raise ValueError("Conversation is required")
    
    @staticmethod
    def validate_max_tokens_range(max_tokens: int) -> None:
        """Validate max_tokens parameter is within acceptable range"""
        if max_tokens < 1 or max_tokens > 8192:
            raise ValueError("max_tokens must be between 1 and 8192")
    
    @staticmethod
    def validate_temperature_range(temperature: float) -> None:
        """Validate temperature parameter is within acceptable range"""
        if temperature < 0.0 or temperature > 2.0:
            raise ValueError("temperature must be between 0.0 and 2.0")
    
    @staticmethod
    def validate_provider_type(provider: Optional[LLMProvider]) -> None:
        """Validate provider parameter if provided"""
        if provider is not None and not isinstance(provider, LLMProvider):
            raise ValueError("provider must be a valid LLMProvider enum value")
    
    @staticmethod
    def validate_model_name(model: Optional[str]) -> None:
        """Validate model name if provided"""
        if model is None:
            return
            
        # Refactoring: Extract complex conditions to improve readability
        is_not_string = not isinstance(model, str)
        is_empty_string = isinstance(model, str) and len(model.strip()) == 0
        
        if is_not_string or is_empty_string:
            raise ValueError("model must be a non-empty string if provided")


class LLMParameterValidator:
    """Specialized validator for LLM parameter objects"""
    
    @dataclass
    class ValidationParameters:
        """Parameter object for validation parameters"""
        conversation: Conversation
        provider: Optional[LLMProvider]
        model: Optional[str]
        max_tokens: int
        temperature: float
    
    def __init__(self, validation_service: LLMParameterValidationService):
        self.validator = validation_service
    
    def validate_core_parameters(self, conversation: Conversation, max_tokens: int, temperature: float) -> None:
        """Validate core required parameters"""
        self.validator.validate_required_conversation(conversation)
        self.validator.validate_max_tokens_range(max_tokens)
        self.validator.validate_temperature_range(temperature)
    
    def validate_optional_parameters(self, provider: Optional[LLMProvider], model: Optional[str]) -> None:
        """Validate optional parameters"""
        self.validator.validate_provider_type(provider)
        self.validator.validate_model_name(model)
    
    def validate_all_parameters(self, params: 'LLMParameterValidator.ValidationParameters') -> None:
        """Validate all parameters - single entry point"""
        # Refactoring: Using parameter object to reduce arguments
        self.validate_core_parameters(params.conversation, params.max_tokens, params.temperature)
        self.validate_optional_parameters(params.provider, params.model) 