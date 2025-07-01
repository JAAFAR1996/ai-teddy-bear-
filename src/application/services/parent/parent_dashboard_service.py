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
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

# Application imports
from src.application.services.parentdashboard import (
    DashboardAlertService, DashboardAnalyticsService, DashboardOrchestrator,
    DashboardSessionService)
# Domain imports
from src.domain.parentdashboard import (AccessControlService, AlertSeverity, AlertType,
                                        AnalyticsDomainService, ChildProfile,
                                        ContentAnalysisService,
                                        ParentalControl, ParentUser)
from src.infrastructure.config import get_config
# Infrastructure imports
from src.infrastructure.parentdashboard import (CacheService,
                                                ChartGenerationService,
                                                ExportService,
                                                NotificationService)
# Repository imports
from src.infrastructure.persistence.child_repository import ChildRepository
from src.infrastructure.persistence.conversation_repository import \
    ConversationRepository


class ParentDashboardService:
    """
    Refactored Parent Dashboard Service - Clean Architecture Coordinator

    This service now acts as a facade that coordinates between:
    - Domain services (business logic)
    - Application services (use cases)
    - Infrastructure services (external concerns)

    All heavy lifting is delegated to specialized services.
    """

    def __init__(
        self,
        child_repo: ChildRepository,
        conversation_repo: ConversationRepository,
        config=None,
    ):
        """Initialize parent dashboard service with dependency injection"""
        self.config = config or get_config()
        self.logger = logging.getLogger(self.__class__.__name__)

        # Initialize domain services
        self.analytics_domain_service = AnalyticsDomainService()
        self.access_control_service = AccessControlService()
        self.content_analysis_service = ContentAnalysisService()

        # Initialize application services
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

        # Initialize infrastructure services
        redis_url = self._get_redis_url()
        self.cache_service = CacheService(redis_url)
        self.chart_service = ChartGenerationService()
        self.notification_service = NotificationService(self._get_config_dict())
        self.export_service = ExportService()

        self.logger.info("Parent Dashboard Service initialized with Clean Architecture")

    # =============================================================================
    # PARENT & CHILD MANAGEMENT (Delegates to Orchestrator)
    # =============================================================================

    async def create_parent_account(
        self, email: str, name: str, phone: Optional[str] = None, timezone: str = "UTC"
    ) -> ParentUser:
        """Create a new parent account"""
        return await self.orchestrator.create_parent_account(
            email, name, phone, timezone
        )

    async def create_child_profile(
        self,
        parent_id: str,
        name: str,
        age: int,
        interests: List[str],
        language: str = "en",
    ) -> ChildProfile:
        """Create child profile with age-appropriate defaults"""
        return await self.orchestrator.create_child_profile(
            parent_id, name, age, interests, language
        )

    async def update_parental_controls(
        self, child_id: str, controls: Dict[str, Any]
    ) -> bool:
        """Update parental control settings"""
        success = await self.orchestrator.update_parental_controls(child_id, controls)

        if success:
            # Invalidate related cache
            self.cache_service.invalidate_child_cache(child_id)

        return success

    # =============================================================================
    # SESSION MANAGEMENT (Delegates to SessionService)
    # =============================================================================

    async def log_interaction(
        self,
        user_id: str,
        child_message: str,
        assistant_message: str,
        timestamp: datetime = None,
        session_id: Optional[str] = None,
        audio_url: Optional[str] = None,
    ):
        """Log a conversation interaction"""
        if not session_id:
            # Start new session if needed
            session_result = await self.session_service.start_session(user_id)
            session_id = session_result.get("session_id")

        return await self.session_service.log_interaction(
            session_id, child_message, assistant_message, audio_url
        )

    async def end_conversation_session(self, session_id: str):
        """End a conversation session"""
        conversation_log = await self.session_service.end_session(session_id)

        if conversation_log:
            # Invalidate analytics cache since new data is available
            self.cache_service.invalidate_child_cache(conversation_log.child_id)

            # Check for alerts
            await self._process_conversation_alerts(conversation_log)

        return conversation_log

    # =============================================================================
    # ANALYTICS (Delegates to AnalyticsService with Caching)
    # =============================================================================

    async def get_analytics(
        self,
        child_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        include_charts: bool = False,
    ) -> Dict[str, Any]:
        """Get comprehensive analytics for a child"""

        # Calculate period for caching
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        period_days = (datetime.now() - start_date).days

        # Check cache first
        cached_analytics = self.cache_service.get_cached_analytics(
            child_id, period_days
        )
        if cached_analytics and not include_charts:
            return cached_analytics

        # Get fresh analytics
        analytics = await self.analytics_service.get_child_analytics(
            child_id, period_days, include_charts
        )

        # Cache results (without charts for size)
        if analytics and not include_charts:
            self.cache_service.cache_analytics(child_id, period_days, analytics)

        return analytics

    async def get_comparative_analytics(
        self, child_ids: List[str], period_days: int = 30
    ) -> Dict[str, Any]:
        """Get comparative analytics across children"""
        return await self.analytics_service.get_comparative_analytics(
            child_ids, period_days
        )

    async def get_trend_analysis(self, child_id: str, weeks: int = 4) -> Dict[str, Any]:
        """Get trend analysis over specified weeks"""
        return await self.analytics_service.get_trend_analysis(child_id, weeks)

    # =============================================================================
    # ACCESS CONTROL (Delegates to Orchestrator)
    # =============================================================================

    async def check_access_allowed(self, child_id: str) -> tuple[bool, Optional[str]]:
        """Check if child can access the system"""
        access_result = await self.orchestrator.check_child_access(child_id)
        return access_result.get("allowed", False), access_result.get("reason")

    async def set_access_schedule(
        self, child_id: str, schedule_type, custom_schedule: Optional[List[Dict]] = None
    ):
        """Set access schedule for a child"""
        # This would be implemented by creating schedules using AccessControlService
        schedules = self.access_control_service.create_default_schedule(
            child_id, schedule_type
        )
        # In real implementation, would save to database
        self.logger.info(f"Set access schedule for child {child_id}")

    # =============================================================================
    # ALERTS & NOTIFICATIONS (Delegates to AlertService)
    # =============================================================================

    async def send_moderation_alert(
        self, user_id: str, alert_type: str, severity: str, details: Dict[str, Any]
    ):
        """Send moderation alert to parent"""

        # Get parent info (simplified)
        parent_id = "parent_id"  # Would get from child repository

        alert = await self.alert_service.create_alert(
            parent_id=parent_id,
            child_id=user_id,
            alert_type=AlertType(alert_type),
            severity=AlertSeverity(severity),
            title=f"Moderation Alert - {severity.upper()}",
            message="Content moderation issue detected",
            details=details,
        )

        # Send notification
        await self.notification_service.send_email_alert(
            recipient_email="parent@example.com",  # Would get from parent data
            alert_title=alert.title,
            alert_message=alert.message,
            child_name="Child Name",  # Would get from child data
            alert_details=details,
        )

    # =============================================================================
    # DATA EXPORT (Delegates to ExportService)
    # =============================================================================

    async def export_conversation_history(
        self,
        child_id: str,
        format: str = "pdf",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> bytes:
        """Export conversation history in specified format"""

        try:
            # Get conversation data (simplified - would use repository)
            conversations = []  # Would fetch from database

            if format.lower() == "json":
                return await self.export_service.export_conversation_history_as_json(
                    conversations
                )
            elif format.lower() == "excel":
                return await self.export_service.export_conversation_history_as_excel(
                    conversations
                )
            else:  # PDF
                return await self.export_service.export_conversation_history_as_pdf(
                    conversations, child_name="Child Name"
                )

        except Exception as e:
            self.logger.error(f"Error exporting conversation history: {e}")
            return b""

    # =============================================================================
    # DASHBOARD DATA (Delegates to Orchestrator)
    # =============================================================================

    async def get_dashboard_data(self, parent_id: str) -> Dict[str, Any]:
        """Get comprehensive dashboard data"""
        return await self.orchestrator.get_dashboard_data(
            parent_id, include_analytics=True
        )

    async def get_recommendations(self, child_id: str) -> Dict[str, Any]:
        """Get AI-powered recommendations for the child"""

        # Get recent analytics
        analytics = await self.get_analytics(child_id)

        if not analytics:
            return {"recommendations": [], "insights": []}

        # Extract recommendations from analytics
        analytics_data = analytics.get("analytics", {})
        recommendations = analytics.get("recommendations", [])
        insights = analytics.get("insights", [])

        return {
            "content_suggestions": self._generate_content_suggestions(analytics_data),
            "time_management": self._generate_time_suggestions(analytics_data),
            "learning_activities": self._generate_learning_suggestions(analytics_data),
            "safety_tips": self._generate_safety_suggestions(analytics_data),
            "insights": insights,
            "recommendations": recommendations,
        }

    # =============================================================================
    # PRIVATE HELPER METHODS
    # =============================================================================

    async def _process_conversation_alerts(self, conversation_log):
        """Process potential alerts from conversation"""

        # Analyze conversation for issues
        controls = ParentalControl(
            child_id=conversation_log.child_id
        )  # Would get from DB

        analysis = self.content_analysis_service.analyze_conversation_content(
            conversation_log, controls
        )

        # Process any alerts that were flagged
        for alert_info in analysis.get("alerts_needed", []):
            await self.alert_service.create_alert(
                parent_id="parent_id",  # Would get from child
                child_id=conversation_log.child_id,
                alert_type=alert_info["type"],
                severity=alert_info["severity"],
                title=alert_info.get("title", "Content Alert"),
                message=alert_info["message"],
            )

    def _get_redis_url(self) -> Optional[str]:
        """Get Redis URL from config"""
        if isinstance(self.config, dict):
            return self.config.get("REDIS_URL")
        return getattr(self.config, "REDIS_URL", None) or os.getenv("REDIS_URL")

    def _get_config_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary for infrastructure services"""
        if isinstance(self.config, dict):
            return self.config

        # Convert config object to dict
        return {
            "EMAIL_FROM": getattr(self.config, "EMAIL_FROM", "noreply@ai-teddy.com"),
            "SMTP_HOST": getattr(self.config, "SMTP_HOST", "localhost"),
            "SMTP_PORT": getattr(self.config, "SMTP_PORT", 587),
            "SMTP_USER": getattr(self.config, "SMTP_USER", None),
            "SMTP_PASS": getattr(self.config, "SMTP_PASS", None),
        }

    def _generate_content_suggestions(
        self, analytics_data: Dict[str, Any]
    ) -> List[str]:
        """Generate content suggestions based on analytics"""
        suggestions = []

        topics_freq = analytics_data.get("topics_frequency", {})
        if "education" in topics_freq:
            suggestions.append("Continue educational conversations - great engagement!")
        if "games" in topics_freq:
            suggestions.append("Try educational games to combine fun with learning")

        return suggestions

    def _generate_time_suggestions(self, analytics_data: Dict[str, Any]) -> List[str]:
        """Generate time management suggestions"""
        suggestions = []

        avg_session = analytics_data.get("average_session_minutes", 0)
        if avg_session > 30:
            suggestions.append("Consider shorter sessions with breaks")
        elif avg_session < 5:
            suggestions.append("Encourage longer, more engaged conversations")

        return suggestions

    def _generate_learning_suggestions(
        self, analytics_data: Dict[str, Any]
    ) -> List[str]:
        """Generate learning activity suggestions"""
        suggestions = []

        learning_progress = analytics_data.get("learning_progress", {})
        if isinstance(learning_progress, dict):
            engagement = learning_progress.get("educational_engagement", 0)
            if engagement < 0.3:
                suggestions.append("Introduce more educational topics and activities")

        return suggestions

    def _generate_safety_suggestions(self, analytics_data: Dict[str, Any]) -> List[str]:
        """Generate safety-related suggestions"""
        suggestions = []

        sentiment = analytics_data.get("sentiment_breakdown", {})
        if sentiment.get("negative", 0) > 0.3:
            suggestions.append(
                "Monitor emotional well-being - consider professional guidance if needed"
            )

        return suggestions

    # =============================================================================
    # LEGACY COMPATIBILITY (Minimal implementations for backward compatibility)
    # =============================================================================

    async def get_parent_by_id(self, parent_id: str) -> Optional[Any]:
        """Get parent user from DB with input validation"""
        if not isinstance(parent_id, str) or not parent_id:
            self.logger.error("Invalid parent_id for get_parent_by_id")
            return None

        # Would delegate to parent repository
        self.logger.info(f"Getting parent {parent_id}")
        return None


# =============================================================================
# API ENDPOINTS CLASS (Refactored to use new service)
# =============================================================================


class ParentDashboardAPI:
    """REST API for parent dashboard - now uses refactored service"""

    def __init__(self, dashboard_service: ParentDashboardService):
        self.service = dashboard_service
        self.logger = logging.getLogger(self.__class__.__name__)

    async def get_dashboard_data(self, parent_id: str) -> Dict[str, Any]:
        """Get dashboard data for parent"""
        return await self.service.get_dashboard_data(parent_id)

    async def update_settings(
        self, child_id: str, settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update child settings"""
        success = await self.service.update_parental_controls(child_id, settings)
        return {"success": success}

    async def get_real_time_status(self, child_id: str) -> Dict[str, Any]:
        """Get real-time status for a child"""
        active_sessions = await self.service.session_service.get_active_sessions(
            child_id
        )

        if active_sessions:
            session = active_sessions[0]
            return {
                "is_active": True,
                "session_duration": session["duration_seconds"],
                "current_topics": session["current_topics"],
                "message_count": session["message_count"],
            }

        return {
            "is_active": False,
            "session_duration": 0,
            "current_topics": [],
            "message_count": 0,
        }

    async def get_analytics(
        self, child_id: str, period_days: int = 30
    ) -> Dict[str, Any]:
        """Get analytics for child"""
        return await self.service.get_analytics(child_id, include_charts=True)

    async def export_data(
        self, child_id: str, format: str = "pdf", data_type: str = "conversations"
    ) -> bytes:
        """Export child data"""
        if data_type == "conversations":
            return await self.service.export_conversation_history(child_id, format)
        else:
            # Export analytics
            analytics = await self.service.get_analytics(child_id)
            if analytics:
                return await self.service.export_service.export_analytics_report(
                    analytics["analytics"],
                    child_name="Child Name",
                    format_type=format,  # Would get from database
                )
            return b""
