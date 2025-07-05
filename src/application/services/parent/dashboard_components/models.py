"""
📋 Shared Dashboard Models
Common data structures used across dashboard components
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


# =============================================================================
# VALIDATION SERVICES (EXTRACT FUNCTION REFACTORING)
# =============================================================================

class ValidationService:
    """
    Extracted validation logic to reduce cyclomatic complexity.
    Each validation method has a single responsibility.
    """
    
    @staticmethod
    def validate_non_empty_string(value: str, field_name: str) -> None:
        """Validate that a field is a non-empty string"""
        if not value or not isinstance(value, str):
            raise ValueError(f"{field_name} must be a non-empty string")
    
    @staticmethod
    def validate_positive_integer(value: int, field_name: str) -> None:
        """Validate that a field is a positive integer"""
        if not isinstance(value, int) or value <= 0:
            raise ValueError(f"{field_name} must be a positive integer")
    
    @staticmethod
    def validate_list_type(value: List[Any], field_name: str) -> None:
        """Validate that a field is a list"""
        if not isinstance(value, list):
            raise ValueError(f"{field_name} must be a list")
    
    @staticmethod
    def validate_age_range(age: int) -> None:
        """Validate age is within reasonable bounds"""
        if age < 3 or age > 18:
            raise ValueError("age must be between 3 and 18 years")
    
    @staticmethod
    def validate_language_code(language: str) -> None:
        """Validate language code format"""
        valid_languages = ["en", "ar", "es", "fr", "de", "it", "ja", "ko", "zh"]
        if language not in valid_languages:
            raise ValueError(f"language must be one of: {', '.join(valid_languages)}")


class ChildProfileValidator:
    """
    Specialized validator for child profile data.
    Decomposed from complex __post_init__ method.
    """
    
    def __init__(self, validation_service: ValidationService):
        self.validator = validation_service
    
    def validate_basic_fields(self, parent_id: str, name: str, age: int) -> None:
        """Validate basic required fields"""
        self.validator.validate_non_empty_string(parent_id, "parent_id")
        self.validator.validate_non_empty_string(name, "name")
        self.validator.validate_positive_integer(age, "age")
    
    def validate_age_constraints(self, age: int) -> None:
        """Validate age-specific constraints"""
        self.validator.validate_age_range(age)
    
    def validate_interests_and_language(self, interests: List[str], language: str) -> None:
        """Validate interests and language fields"""
        self.validator.validate_list_type(interests, "interests")
        self.validator.validate_non_empty_string(language, "language")
        self.validator.validate_language_code(language)


class InteractionLogValidator:
    """
    Specialized validator for interaction log data.
    Decomposed from complex __post_init__ method.
    """
    
    def __init__(self, validation_service: ValidationService):
        self.validator = validation_service
    
    def validate_required_fields(self, user_id: str, child_message: str, assistant_message: str) -> None:
        """Validate required string fields"""
        self.validator.validate_non_empty_string(user_id, "user_id")
        self.validator.validate_non_empty_string(child_message, "child_message")
        self.validator.validate_non_empty_string(assistant_message, "assistant_message")
    
    def validate_message_length(self, child_message: str, assistant_message: str) -> None:
        """Validate message length constraints"""
        if len(child_message) > 5000:
            raise ValueError("child_message cannot exceed 5000 characters")
        if len(assistant_message) > 10000:
            raise ValueError("assistant_message cannot exceed 10000 characters")
    
    def set_default_timestamp(self, timestamp: Optional[datetime]) -> datetime:
        """Set default timestamp if not provided"""
        return timestamp if timestamp is not None else datetime.now()


# =============================================================================
# PARAMETER OBJECTS (IMPROVED WITH LOW COMPLEXITY VALIDATION)
# =============================================================================

@dataclass
class ChildProfileData:
    """
    Parameter object for child profile creation.
    Encapsulates all data needed to create a child profile.
    """
    parent_id: str
    name: str
    age: int
    interests: List[str]
    language: str = "en"
    
    def __post_init__(self):
        """
        Validate child profile data with extracted validation methods.
        Cyclomatic complexity reduced from 15 to 3.
        """
        validator_service = ValidationService()
        profile_validator = ChildProfileValidator(validator_service)
        
        # Decomposed validation calls (low complexity)
        profile_validator.validate_basic_fields(self.parent_id, self.name, self.age)
        profile_validator.validate_age_constraints(self.age)
        profile_validator.validate_interests_and_language(self.interests, self.language)


@dataclass
class InteractionLogData:
    """
    Parameter object for interaction logging.
    Encapsulates all data needed to log an interaction.
    """
    user_id: str
    child_message: str
    assistant_message: str
    timestamp: Optional[datetime] = None
    session_id: Optional[str] = None
    audio_url: Optional[str] = None
    
    def __post_init__(self):
        """
        Validate interaction log data with extracted validation methods.
        Cyclomatic complexity reduced from 11 to 2.
        """
        validator_service = ValidationService()
        interaction_validator = InteractionLogValidator(validator_service)
        
        # Decomposed validation calls (low complexity)
        interaction_validator.validate_required_fields(
            self.user_id, self.child_message, self.assistant_message
        )
        interaction_validator.validate_message_length(
            self.child_message, self.assistant_message
        )
        
        # Set default timestamp
        self.timestamp = interaction_validator.set_default_timestamp(self.timestamp)


@dataclass
class AnalyticsRequest:
    """Parameter object for analytics requests to reduce argument count"""
    child_id: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    include_charts: bool = False
    period_days: Optional[int] = None
    
    def __post_init__(self):
        """Set calculated period_days if not provided"""
        if self.period_days is None and self.start_date:
            self.period_days = (datetime.now() - self.start_date).days
        elif self.period_days is None:
            self.period_days = 30


@dataclass
class ExportRequest:
    """Parameter object for export requests to reduce argument count"""
    child_id: str
    format: str = "pdf"
    data_type: str = "conversations"
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate export request parameters"""
        ValidationService.validate_non_empty_string(self.child_id, "child_id")
        
        valid_formats = ["pdf", "json", "excel"]
        if self.format not in valid_formats:
            raise ValueError(f"format must be one of: {', '.join(valid_formats)}")
        
        valid_data_types = ["conversations", "analytics"]
        if self.data_type not in valid_data_types:
            raise ValueError(f"data_type must be one of: {', '.join(valid_data_types)}")


@dataclass
class AlertRequest:
    """Parameter object for alert creation"""
    parent_id: str
    child_id: str
    alert_type: str
    severity: str
    title: str
    message: str
    details: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Validate alert request parameters"""
        ValidationService.validate_non_empty_string(self.parent_id, "parent_id")
        ValidationService.validate_non_empty_string(self.child_id, "child_id")
        ValidationService.validate_non_empty_string(self.alert_type, "alert_type")
        ValidationService.validate_non_empty_string(self.severity, "severity")
        ValidationService.validate_non_empty_string(self.title, "title")
        ValidationService.validate_non_empty_string(self.message, "message") 