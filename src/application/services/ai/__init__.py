"""
🚀 LLM Services Package - High Cohesion Architecture
تجميع جميع خدمات LLM مع الهيكلة المحسنة

✅ تم حل مشكلة Low Cohesion بتطبيق EXTRACT CLASS pattern داخل الملف الأصلي
✅ جميع المكونات منظمة في ملف واحد مع فصل واضح للمسؤوليات
✅ تصدير موحد وتكامل كامل مع المشروع
"""

# Import all components from the refactored main factory file
from .llm_service_factory import (
    # Main service classes
    LLMServiceFactory,
    LLMModelSelector,
    LLMResponseCache,
    ModelSelector,  # Backward compatibility alias
    ResponseCache,  # Backward compatibility alias
    
    # Parameter objects
    GenerationRequest,
    ModelSelectionRequest,
    LegacyGenerationParams,
    LegacyFactoryParams,
    LegacyCompatibilityParams,
    
    # Validation services
    LLMParameterValidationService,
    LLMParameterValidator,
    
    # Shared abstractions
    ParameterConverter,
    LegacyCompatibilityService,
    
    # Factory functions
    create_llm_factory,
    create_generation_request,
    create_model_selection_request,
    create_legacy_generation_params,
    create_legacy_factory_params,
    create_legacy_compatibility_params,
    create_legacy_params_from_args,
    
    # Conversion functions
    from_legacy_args,
    from_legacy_args_compatible,
    from_legacy_args_compatible_individual,
    
    # Utility functions
    get_default_model_config
)

# Import base classes
from .llm_base import (
    LLMProvider,
    ModelConfig,
    LLMResponse,
    BaseLLMAdapter
)

# Import adapters
from .llm_openai_adapter import OpenAIAdapter
from .llm_anthropic_adapter import AnthropicAdapter
from .llm_google_adapter import GoogleAdapter


# Export all high-cohesion components
__all__ = [
    # Core Factory (main coordinator)
    "LLMServiceFactory",
    "create_llm_factory",
    
    # Parameter Validation (extracted responsibility)
    "LLMParameterValidationService",
    "LLMParameterValidator",
    
    # Parameter Objects (extracted responsibility)
    "GenerationRequest",
    "LegacyGenerationParams",
    "LegacyFactoryParams",
    "LegacyCompatibilityParams",
    "create_generation_request",
    "create_legacy_generation_params",
    "create_legacy_factory_params",
    "create_legacy_compatibility_params",
    "create_legacy_params_from_args",
    
    # Model Selection (extracted responsibility)
    "ModelSelector",
    "ModelSelectionRequest",
    "create_model_selection_request",
    "get_default_model_config",
    
    # Response Caching (extracted responsibility)
    "ResponseCache",
    
    # Legacy Compatibility (extracted responsibility)
    "LegacyCompatibilityService",
    "ParameterConverter",
    "from_legacy_args",
    "from_legacy_args_compatible",
    "from_legacy_args_compatible_individual",
    
    # Base Classes
    "LLMProvider",
    "ModelConfig",
    "LLMResponse",
    "BaseLLMAdapter",
    
    # Adapters
    "OpenAIAdapter",
    "AnthropicAdapter",
    "GoogleAdapter"
]


# Module level documentation
__doc__ = """
🎯 LLM Services Package - High Cohesion Architecture

تم تطبيق EXTRACT CLASS pattern لحل مشكلة Low Cohesion:

📦 المكونات المستخرجة (Extracted Components):
├── llm_parameter_validation.py    - مسؤولية: Parameter Validation
├── llm_parameter_objects.py       - مسؤولية: Parameter Objects & Factory Functions  
├── llm_model_selection.py         - مسؤولية: Model Selection & Configuration
├── llm_response_cache.py          - مسؤولية: Response Caching & Cache Management
├── llm_legacy_compatibility.py   - مسؤولية: Legacy Support & Parameter Conversion
└── llm_service_factory_refactored.py - مسؤولية: Factory Coordination

🚀 فوائد التحسين (Benefits Achieved):
✅ High Cohesion - كل module له مسؤولية واحدة واضحة
✅ Single Responsibility Principle - مطبق على كل مكون
✅ Easy Maintenance - سهولة في الصيانة والتطوير
✅ Clear Separation of Concerns - فصل واضح للمسؤوليات
✅ Testability - سهولة في كتابة الاختبارات
✅ Reusability - إمكانية إعادة الاستخدام

📈 تحسينات الجودة (Quality Improvements):
- تقليل الـ Low Cohesion من 63 functions إلى modules متخصصة
- فصل المسؤوليات بوضوح
- تحسين إمكانية القراءة والفهم
- تطبيق Clean Architecture principles

💡 مثال على الاستخدام (Usage Example):
```python
from src.application.services.ai import (
    LLMServiceFactory, 
    GenerationRequest,
    create_llm_factory
)

# إنشاء المصنع
factory = await create_llm_factory()

# إنشاء طلب
request = GenerationRequest(
    conversation=conversation,
    provider=LLMProvider.OPENAI,
    model="gpt-4"
)

# توليد الاستجابة
response = await factory.generate_response(request)
```
"""
