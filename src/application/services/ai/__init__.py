"""
🏭 LLM Service Factory Package
حزمة مصنع خدمات LLM

This package provides a complete solution for LLM service management.
"""

# Import main components
try:
    from .llm_service_factory import (
        LLMServiceFactory,
        GenerationRequest,
        LegacyGenerationParams,
        create_generation_request,
        create_legacy_generation_params,
        generate_simple,
        get_factory,
    )

    # Import specialized services
    from .validation.parameter_validation import (
        LLMParameterValidationService,
        LLMParameterValidator,
    )

    from .caching.response_cache import LLMResponseCache

    from .selection.model_selector import LLMModelSelector, ModelSelectionRequest

    # Export public API
    __all__ = [
        # Main factory
        "LLMServiceFactory",
        # Simplified interface
        "generate_simple",
        "get_factory",
        # Parameter objects
        "GenerationRequest",
        "LegacyGenerationParams",
        "ModelSelectionRequest",
        # Factory helpers
        "create_generation_request",
        "create_legacy_generation_params",
        # Specialized services
        "LLMParameterValidationService",
        "LLMParameterValidator",
        "LLMResponseCache",
        "LLMModelSelector",
    ]

except ImportError as e:
    # If imports fail, provide minimal interface
    __all__ = []
    print(f"Warning: Could not import all LLM services: {e}")

# Package metadata
__version__ = "2.0.0"
__author__ = "AI Teddy Bear Team"
__description__ = "Complete LLM service management solution"
