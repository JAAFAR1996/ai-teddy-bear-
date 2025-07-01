"""
Domain Exceptions Package
تنظيم وتصدير جميع exception classes
"""

# Base exceptions
from .base import (AITeddyBearException, ErrorCategory, ErrorContext,
                   ErrorSeverity)
# Business logic exceptions
from .business_logic import (BusinessLogicException,
                             DuplicateResourceException,
                             QuotaExceededException, ResourceNotFoundException)
# Child safety exceptions
from .child_safety import (AgeInappropriateException, ChildSafetyException,
                           InappropriateContentException,
                           ParentalConsentRequiredException)
# Infrastructure exceptions
from .infrastructure import (CircuitBreakerOpenException, DatabaseException,
                             ExternalServiceException, InfrastructureException)
# Performance exceptions
from .performance import (PerformanceException, RateLimitException,
                          TimeoutException)
# Security exceptions
from .security import (AuthenticationException, AuthorizationException,
                       SecurityException, TokenExpiredException)
# Validation exceptions
from .validation import (InvalidInputException, MissingRequiredFieldException,
                         ValidationException)

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
    "RateLimitException",
]
