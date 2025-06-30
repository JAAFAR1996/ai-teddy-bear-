"""
Domain Exceptions Package
تنظيم وتصدير جميع exception classes
"""

# Base exceptions
from .base import (
    ErrorSeverity,
    ErrorCategory,
    ErrorContext,
    AITeddyBearException
)

# Child safety exceptions
from .child_safety import (
    ChildSafetyException,
    InappropriateContentException,
    ParentalConsentRequiredException,
    AgeInappropriateException
)

# Validation exceptions
from .validation import (
    ValidationException,
    InvalidInputException,
    MissingRequiredFieldException
)

# Security exceptions
from .security import (
    SecurityException,
    AuthenticationException,
    AuthorizationException,
    TokenExpiredException
)

# Infrastructure exceptions
from .infrastructure import (
    InfrastructureException,
    DatabaseException,
    ExternalServiceException,
    CircuitBreakerOpenException
)

# Business logic exceptions
from .business_logic import (
    BusinessLogicException,
    ResourceNotFoundException,
    DuplicateResourceException,
    QuotaExceededException
)

# Performance exceptions
from .performance import (
    PerformanceException,
    TimeoutException,
    RateLimitException
)

__all__ = [
    # Base
    "ErrorSeverity",
    "ErrorCategory",
    "ErrorContext",
    "AITeddyBearException",
    
    # Child safety
    "ChildSafetyException",
    "InappropriateContentException",
    "ParentalConsentRequiredException",
    "AgeInappropriateException",
    
    # Validation
    "ValidationException",
    "InvalidInputException",
    "MissingRequiredFieldException",
    
    # Security
    "SecurityException",
    "AuthenticationException",
    "AuthorizationException",
    "TokenExpiredException",
    
    # Infrastructure
    "InfrastructureException",
    "DatabaseException",
    "ExternalServiceException",
    "CircuitBreakerOpenException",
    
    # Business logic
    "BusinessLogicException",
    "ResourceNotFoundException",
    "DuplicateResourceException",
    "QuotaExceededException",
    
    # Performance
    "PerformanceException",
    "TimeoutException",
    "RateLimitException"
] 