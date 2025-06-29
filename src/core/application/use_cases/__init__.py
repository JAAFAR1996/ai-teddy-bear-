"""
🎯 Application Use Cases - AI Teddy Bear Core
============================================

Use cases represent the application-specific business rules.
They orchestrate the flow of data to and from the entities,
and direct those entities to use their business rules to achieve
the goals of the use case.

Following Clean Architecture principles:
- Independent of UI, database, and external concerns
- Testable business logic
- Clear application boundaries
- Single responsibility per use case
"""

from .child_use_cases import (
    RegisterChildUseCase,
    UpdateChildProfileUseCase,
    GetChildProfileUseCase,
    ActivateChildUseCase,
    DeactivateChildUseCase
)

from .conversation_use_cases import (
    StartConversationUseCase,
    ProcessChildInputUseCase,
    GenerateResponseUseCase,
    EndConversationUseCase,
    GetConversationHistoryUseCase
)

from .learning_use_cases import (
    SetLearningGoalUseCase,
    TrackProgressUseCase,
    GeneratePersonalizedContentUseCase,
    EvaluateLearningOutcomesUseCase
)

from .safety_use_cases import (
    ValidateContentSafetyUseCase,
    ApplyParentalControlsUseCase,
    MonitorInteractionSafetyUseCase,
    GenerateSafetyReportUseCase
)

__all__ = [
    # Child Use Cases
    'RegisterChildUseCase',
    'UpdateChildProfileUseCase', 
    'GetChildProfileUseCase',
    'ActivateChildUseCase',
    'DeactivateChildUseCase',
    
    # Conversation Use Cases
    'StartConversationUseCase',
    'ProcessChildInputUseCase',
    'GenerateResponseUseCase',
    'EndConversationUseCase',
    'GetConversationHistoryUseCase',
    
    # Learning Use Cases
    'SetLearningGoalUseCase',
    'TrackProgressUseCase',
    'GeneratePersonalizedContentUseCase',
    'EvaluateLearningOutcomesUseCase',
    
    # Safety Use Cases
    'ValidateContentSafetyUseCase',
    'ApplyParentalControlsUseCase',
    'MonitorInteractionSafetyUseCase',
    'GenerateSafetyReportUseCase'
] 