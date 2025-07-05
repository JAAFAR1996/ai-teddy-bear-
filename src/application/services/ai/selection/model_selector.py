"""
🎯 LLM Model Selection Service
خدمة اختيار نماذج LLM - مستخرجة من الملف الأساسي

✅ Single Responsibility: Model selection only
✅ Task-based model selection
✅ Performance history tracking
✅ Easy to extend and maintain
"""

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum


# Mock classes for standalone operation
class LLMProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"


class ModelConfig:
    """Mock model config for selection"""

    def __init__(
            self,
            provider=None,
            model_name="",
            max_tokens=150,
            temperature=0.7,
            **kwargs):
        self.provider = provider
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        for k, v in kwargs.items():
            setattr(self, k, v)


@dataclass
class ModelSelectionRequest:
    """Parameter object for model selection"""

    task_type: str
    context_length: int = 0
    required_features: List[str] = field(default_factory=list)
    budget_constraint: Optional[float] = None
    latency_requirement: Optional[int] = None


class LLMModelSelector:
    """
    مسؤولية واحدة: اختيار النموذج المناسب للمهمة
    Extracted from main factory to achieve High Cohesion
    """

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.performance_history = defaultdict(list)

    def select_model(self, request: ModelSelectionRequest) -> ModelConfig:
        """Select best model for the given request"""
        return self._select_by_task_type(request.task_type)

    def _select_by_task_type(self, task_type: str) -> ModelConfig:
        """Select model based on task type"""
        task_configs = {
            "creative_writing": ModelConfig(
                provider=LLMProvider.ANTHROPIC,
                model_name="claude-3-sonnet",
                max_tokens=2048,
                temperature=0.8,
            ),
            "analysis": ModelConfig(
                provider=LLMProvider.OPENAI,
                model_name="gpt-4",
                max_tokens=1024,
                temperature=0.3,
            ),
        }

        return task_configs.get(
            task_type,
            ModelConfig(
                provider=LLMProvider.OPENAI,
                model_name="gpt-3.5-turbo",
                max_tokens=1024,
                temperature=0.7,
            ),
        )

    def get_default_model_config(
        self, provider: LLMProvider = LLMProvider.OPENAI, task: str = "general"
    ) -> ModelConfig:
        """Get default model configuration for provider and task"""
        configs = {
            LLMProvider.OPENAI: {
                "general": ModelConfig(
                    provider=LLMProvider.OPENAI,
                    model_name="gpt-3.5-turbo",
                    max_tokens=150,
                    temperature=0.7,
                ),
                "creative": ModelConfig(
                    provider=LLMProvider.OPENAI,
                    model_name="gpt-4",
                    max_tokens=500,
                    temperature=0.9,
                ),
            },
            LLMProvider.ANTHROPIC: {
                "general": ModelConfig(
                    provider=LLMProvider.ANTHROPIC,
                    model_name="claude-3-sonnet",
                    max_tokens=150,
                    temperature=0.7,
                )
            },
        }

        return configs.get(provider, {}).get(
            task, configs[LLMProvider.OPENAI]["general"]
        )
