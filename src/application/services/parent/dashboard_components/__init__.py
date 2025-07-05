"""
📊 Parent Dashboard Components - High Cohesion Architecture
Refactored dashboard service components following EXTRACT CLASS pattern
"""

from .profile_management import ProfileManagementService
from .conversation_session import ConversationSessionService
from .analytics_reporting import AnalyticsReportingService
from .access_control_alerts import AccessControlAlertsService
from .models import (
    ChildProfileData,
    InteractionLogData,
    AnalyticsRequest,
    ExportRequest,
    AlertRequest
)

__all__ = [
    # Core Components
    "ProfileManagementService",
    "ConversationSessionService", 
    "AnalyticsReportingService",
    "AccessControlAlertsService",
    
    # Data Models
    "ChildProfileData",
    "InteractionLogData",
    "AnalyticsRequest",
    "ExportRequest",
    "AlertRequest"
]

# Version info
__version__ = "2.0.0"
__author__ = "AI Teddy Bear Team"
__description__ = "High-cohesion parent dashboard components with EXTRACT CLASS refactoring" 