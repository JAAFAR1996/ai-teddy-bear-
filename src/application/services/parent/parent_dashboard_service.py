# parent_dashboard_service.py - REFACTORED VERSION
"""
Parent Dashboard Service - Clean Architecture
============================================

Main service coordinator for Parent Dashboard functionality.
This service now delegates to specialized components following Clean Architecture principles.

Migrated from 1295-line God Class to organized, maintainable architecture.
"""

import logging
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

# Application imports
from src.application.services.parentdashboard import (
    DashboardAlertService,
    DashboardAnalyticsService,
    DashboardOrchestrator,
    DashboardSessionService,
)

# Domain imports
from src.domain.parentdashboard import (
    AccessControlService,
    AlertSeverity,
    AlertType,
    AnalyticsDomainService,
    ChildProfile,
    ContentAnalysisService,
    ParentalControl,
    ParentUser,
)
from src.infrastructure.config import get_config

# Infrastructure imports
from src.infrastructure.parentdashboard import (
    CacheService,
    ChartGenerationService,
    ExportService,
    NotificationService,
)

# Repository imports
from src.infrastructure.persistence.child_repository import ChildRepository
from src.infrastructure.persistence.conversation_repository import (
    ConversationRepository,
)


# Import high-cohesion components
from .dashboard_components import (
    ProfileManagementService,
    ConversationSessionService,
    AnalyticsReportingService,
    AccessControlAlertsService,
    ChildProfileData,
    InteractionLogData,
    AnalyticsRequest,
    ExportRequest,
    AlertRequest,
)


class ParentDashboardService:
    """ """

    def __init__(
        self,
        child_repo: ChildRepository,
        conversation_repo: ConversationRepository,
        config=None,
    ):
        """Initialize with high-cohesion components"""
        self.config = config or get_config()
        self.logger = logging.getLogger(self.__class__.__name__)

        # Initialize domain services (unchanged)
        self.analytics_domain_service = AnalyticsDomainService()
        self.access_control_service = AccessControlService()
        self.content_analysis_service = ContentAnalysisService()

        # Initialize application services (unchanged)
        self.orchestrator = DashboardOrchestrator(
            child_repository=child_repo,
            conversation_repository=conversation_repo,
            analytics_service=self.analytics_domain_service,
            access_service=self.access_control_service,
            content_service=self.content_analysis_service,
        )

        self.analytics_service = DashboardAnalyticsService(
            conversation_repository=conversation_repo,
            analytics_domain_service=self.analytics_domain_service,
        )

        self.alert_service = DashboardAlertService(
            content_analysis_service=self.content_analysis_service
        )

        self.session_service = DashboardSessionService(
            content_service=self.content_analysis_service,
            access_service=self.access_control_service,
        )

        # Initialize infrastructure services (unchanged)
        redis_url = self._get_redis_url()
        self.cache_service = CacheService(redis_url)
        self.chart_service = ChartGenerationService()
        self.notification_service = NotificationService(
            self._get_config_dict())
        self.export_service = ExportService()

        # Initialize HIGH-COHESION COMPONENTS
        self.profile_manager = ProfileManagementService(
            orchestrator=self.orchestrator, child_repository=child_repo
        )

        self.conversation_manager = ConversationSessionService(
            session_service=self.session_service,
            content_analysis_service=self.content_analysis_service,
            cache_service=self.cache_service,
        )

        self.analytics_reporter = AnalyticsReportingService(
            analytics_service=self.analytics_service,
            cache_service=self.cache_service,
            chart_service=self.chart_service,
            export_service=self.export_service,
        )

        self.access_control_manager = AccessControlAlertsService(
            orchestrator=self.orchestrator,
            alert_service=self.alert_service,
            notification_service=self.notification_service,
            access_control_service=self.access_control_service,
        )

        self.logger.info(
            "🚀 Parent Dashboard Service initialized with High Cohesion Architecture"
        )

    # =============================================================================
    # PARENT & CHILD MANAGEMENT (Delegates to ProfileManagementService)
    # =============================================================================

    async def create_parent_account(
            self,
            email: str,
            name: str,
            phone: Optional[str] = None,
            timezone: str = "UTC") -> ParentUser:
        """Create a new parent account - delegated to profile manager"""
        return await self.profile_manager.create_parent_account(
            email, name, phone, timezone
        )

    async def create_child_profile(
        self, profile_data: ChildProfileData
    ) -> ChildProfile:
        """
        Create child profile - delegated to profile manager.
        Uses parameter object pattern (1 argument only).
        """
        return await self.profile_manager.create_child_profile(profile_data)

    # =============================================================================
    # SESSION MANAGEMENT (Delegates to ConversationSessionService)
    # =============================================================================

    async def log_interaction(self, interaction_data: InteractionLogData):
        """
        Log a conversation interaction - delegated to conversation manager.
        Uses parameter object pattern (1 argument only).
        """
        return await self.conversation_manager.log_interaction(interaction_data)

    async def end_conversation_session(self, session_id: str):
        """End a conversation session - delegated to conversation manager"""
        return await self.conversation_manager.end_conversation_session(session_id)

    # =============================================================================
    # ANALYTICS (Delegates to AnalyticsReportingService)
    # =============================================================================

    async def get_analytics(
        self, analytics_request: AnalyticsRequest
    ) -> Dict[str, Any]:
        """Get comprehensive analytics - delegated to analytics reporter"""
        return await self.analytics_reporter.get_analytics(analytics_request)

    async def get_comparative_analytics(
        self, child_ids: List[str], period_days: int = 30
    ) -> Dict[str, Any]:
        """Get comparative analytics - delegated to analytics reporter"""
        return await self.analytics_reporter.get_comparative_analytics(
            child_ids, period_days
        )

    async def get_trend_analysis(
            self, child_id: str, weeks: int = 4) -> Dict[str, Any]:
        """Get trend analysis - delegated to analytics reporter"""
        return await self.analytics_reporter.get_trend_analysis(child_id, weeks)

    # =============================================================================
    # ACCESS CONTROL & ALERTS (Delegates to AccessControlAlertsService)
    # =============================================================================

    async def check_access_allowed(
            self, child_id: str) -> tuple[bool, Optional[str]]:
        """Check if child can access the system - delegated to access control manager"""
        return await self.access_control_manager.check_access_allowed(child_id)

    async def update_parental_controls(
        self, child_id: str, controls: Dict[str, Any]
    ) -> bool:
        """Update parental control settings - delegated to access control manager"""
        return await self.access_control_manager.update_parental_controls(
            child_id, controls
        )

    async def set_access_schedule(self,
                                  child_id: str,
                                  schedule_type,
                                  custom_schedule: Optional[List[Dict]] = None):
        """Set access schedule - delegated to access control manager"""
        return await self.access_control_manager.set_access_schedule(
            child_id, schedule_type, custom_schedule
        )

    async def send_moderation_alert(
        self, user_id: str, alert_type: str, severity: str, details: Dict[str, Any]
    ):
        """Send moderation alert - delegated to access control manager"""
        return await self.access_control_manager.send_moderation_alert(
            user_id, alert_type, severity, details
        )

    # =============================================================================
    # DATA EXPORT (Delegates to AnalyticsReportingService)
    # =============================================================================

    async def export_data(self, export_request: ExportRequest) -> bytes:
        """Export data - delegated to analytics reporter"""
        return await self.analytics_reporter.export_data(export_request)

    # =============================================================================
    # DASHBOARD DATA (Delegates to Orchestrator)
    # =============================================================================

    async def get_dashboard_data(self, parent_id: str) -> Dict[str, Any]:
        """Get comprehensive dashboard data - delegated to orchestrator"""
        return await self.orchestrator.get_dashboard_data(
            parent_id, include_analytics=True
        )

    # =============================================================================
    # LEGACY COMPATIBILITY METHODS (Reduced Argument Count)
    # =============================================================================

    async def create_child_profile_legacy(
        self, profile_data: ChildProfileData
    ) -> ChildProfile:
        """
        Legacy method REFACTORED using Parameter Object pattern.
        ✅ Reduced from 5 arguments to 1 argument (under threshold)

        Args:
            profile_data: ChildProfileData containing all profile information

        Returns:
            ChildProfile: Created child profile
        """
        return await self.create_child_profile(profile_data)

    async def log_interaction_legacy(
            self, interaction_data: InteractionLogData):
        """
        Legacy method REFACTORED using Parameter Object pattern.
        ✅ Reduced from 6 arguments to 1 argument (under threshold)

        Args:
            interaction_data: InteractionLogData containing all interaction information

        Returns:
            Log result from session service
        """
        return await self.log_interaction(interaction_data)

    async def get_analytics_legacy(
        self,
        child_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        include_charts: bool = False,
    ) -> Dict[str, Any]:
        """
        Legacy method for backward compatibility.
        ⚠️ DEPRECATED: Use get_analytics with AnalyticsRequest instead.
        """
        analytics_request = AnalyticsRequest(
            child_id=child_id,
            start_date=start_date,
            end_date=end_date,
            include_charts=include_charts,
        )
        return await self.get_analytics(analytics_request)

    async def export_conversation_history_legacy(
        self,
        child_id: str,
        format: str = "pdf",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> bytes:
        """
        Legacy method for backward compatibility.
        ⚠️ DEPRECATED: Use export_data with ExportRequest instead.
        """
        export_request = ExportRequest(
            child_id=child_id,
            format=format,
            data_type="conversations",
            start_date=start_date,
            end_date=end_date,
        )
        return await self.export_data(export_request)

    # =============================================================================
    # HELPER METHODS (Minimal implementations)
    # =============================================================================

    def _get_redis_url(self) -> Optional[str]:
        """Get Redis URL from config"""
        if isinstance(self.config, dict):
            return self.config.get("REDIS_URL")
        return getattr(
            self.config,
            "REDIS_URL",
            None) or os.getenv("REDIS_URL")

    def _get_config_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary for infrastructure services"""
        if isinstance(self.config, dict):
            return self.config

        return {
            "EMAIL_FROM": getattr(
                self.config,
                "EMAIL_FROM",
                "noreply@ai-teddy.com"),
            "SMTP_HOST": getattr(
                self.config,
                "SMTP_HOST",
                "localhost"),
            "SMTP_PORT": getattr(
                self.config,
                "SMTP_PORT",
                587),
            "SMTP_USER": getattr(
                self.config,
                "SMTP_USER",
                None),
            "SMTP_PASS": getattr(
                self.config,
                "SMTP_PASS",
                None),
        }

    async def get_parent_by_id(self, parent_id: str) -> Optional[Any]:
        """Get parent user - delegated to profile manager"""
        return await self.profile_manager.get_parent_by_id(parent_id)


# =============================================================================
# API ENDPOINTS CLASS (Refactored to use new service)
# =============================================================================


class ParentDashboardAPI:
    """
    🌐 REST API for parent dashboard - High Cohesion Edition
    Uses high-cohesion components for better maintainability
    """

    def __init__(self, dashboard_service: ParentDashboardService):
        self.service = dashboard_service
        self.logger = logging.getLogger(self.__class__.__name__)

    async def get_dashboard_data(self, parent_id: str) -> Dict[str, Any]:
        """Get dashboard data for parent"""
        return await self.service.get_dashboard_data(parent_id)

    async def update_settings(
        self, child_id: str, settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update child settings using access control manager"""
        success = await self.service.update_parental_controls(child_id, settings)
        return {"success": success}

    async def get_real_time_status(self, child_id: str) -> Dict[str, Any]:
        """Get real-time status using conversation manager"""
        return await self.service.conversation_manager.get_real_time_session_status(
            child_id
        )

    async def get_analytics(
        self, child_id: str, period_days: int = 30
    ) -> Dict[str, Any]:
        """Get analytics using parameter object and analytics reporter"""
        analytics_request = AnalyticsRequest(
            child_id=child_id, period_days=period_days, include_charts=True
        )
        return await self.service.get_analytics(analytics_request)

    async def export_data(
            self,
            child_id: str,
            format: str = "pdf",
            data_type: str = "conversations") -> bytes:
        """Export data using parameter object and analytics reporter"""
        export_request = ExportRequest(
            child_id=child_id, format=format, data_type=data_type
        )
        return await self.service.export_data(export_request)
