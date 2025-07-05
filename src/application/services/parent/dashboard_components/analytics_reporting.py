"""
📊 Analytics & Reporting Service
High cohesion component for analytics, insights, and data export operations
"""

import logging
from typing import Dict, Any, List
from .models import AnalyticsRequest, ExportRequest


class AnalyticsReportingService:
    """
    Dedicated service for analytics and reporting operations.
    High cohesion: all methods work with analytics data and reports.
    """

    def __init__(
            self,
            analytics_service,
            cache_service,
            chart_service,
            export_service):
        """Initialize analytics and reporting service"""
        self.analytics_service = analytics_service
        self.cache_service = cache_service
        self.chart_service = chart_service
        self.export_service = export_service
        self.logger = logging.getLogger(__name__)

    async def get_analytics(
        self, analytics_request: AnalyticsRequest
    ) -> Dict[str, Any]:
        """Get comprehensive analytics for a child using parameter object"""
        try:
            # Check cache first
            cached_analytics = self.cache_service.get_cached_analytics(
                analytics_request.child_id, analytics_request.period_days
            )

            if cached_analytics and not analytics_request.include_charts:
                self.logger.debug(
                    f"Returning cached analytics for child {analytics_request.child_id}"
                )
                return cached_analytics

            # Get fresh analytics
            analytics = await self.analytics_service.get_child_analytics(
                analytics_request.child_id,
                analytics_request.period_days,
                analytics_request.include_charts,
            )

            # Cache results (without charts for size efficiency)
            if analytics and not analytics_request.include_charts:
                self.cache_service.cache_analytics(
                    analytics_request.child_id, analytics_request.period_days, analytics)

            self.logger.info(
                f"Successfully generated analytics for child {analytics_request.child_id}"
            )
            return analytics

        except Exception as e:
            self.logger.error(
                f"Failed to get analytics for child {analytics_request.child_id}: {e}"
            )
            return {"error": str(e), "analytics": {}}

    async def get_comparative_analytics(
        self, child_ids: List[str], period_days: int = 30
    ) -> Dict[str, Any]:
        """Get comparative analytics across multiple children"""
        try:
            return await self.analytics_service.get_comparative_analytics(
                child_ids, period_days
            )
        except Exception as e:
            self.logger.error(f"Failed to get comparative analytics: {e}")
            return {"error": str(e), "comparison": {}}

    async def get_trend_analysis(
            self, child_id: str, weeks: int = 4) -> Dict[str, Any]:
        """Get trend analysis over specified weeks"""
        try:
            return await self.analytics_service.get_trend_analysis(child_id, weeks)
        except Exception as e:
            self.logger.error(
                f"Failed to get trend analysis for child {child_id}: {e}")
            return {"error": str(e), "trends": {}}

    async def export_data(self, export_request: ExportRequest) -> bytes:
        """Export data based on export request with proper formatting"""
        try:
            if export_request.data_type == "conversations":
                return await self._export_conversations(export_request)
            elif export_request.data_type == "analytics":
                return await self._export_analytics(export_request)
            else:
                raise ValueError(
                    f"Unsupported data type: {export_request.data_type}")

        except Exception as e:
            self.logger.error(f"Failed to export data: {e}")
            return b""

    async def _export_analytics(self, export_request: ExportRequest) -> bytes:
        """Export analytics data in requested format"""
        try:
            analytics_request = AnalyticsRequest(
                child_id=export_request.child_id,
                start_date=export_request.start_date,
                end_date=export_request.end_date,
                include_charts=True,
            )

            analytics = await self.get_analytics(analytics_request)

            if analytics and "analytics" in analytics:
                return await self.export_service.export_analytics_report(
                    analytics["analytics"],
                    child_name="Child Name",
                    format_type=export_request.format,
                )

            return b""

        except Exception as e:
            self.logger.error(f"Failed to export analytics: {e}")
            return b""

    async def _export_conversations(
            self, export_request: ExportRequest) -> bytes:
        """Export conversation history in requested format"""
        try:
            conversations = []  # Would fetch from database

            if export_request.format == "json":
                return await self.export_service.export_conversation_history_as_json(
                    conversations
                )
            elif export_request.format == "excel":
                return await self.export_service.export_conversation_history_as_excel(
                    conversations
                )
            else:  # PDF
                return await self.export_service.export_conversation_history_as_pdf(
                    conversations, child_name="Child Name"
                )

        except Exception as e:
            self.logger.error(f"Failed to export conversations: {e}")
            return b""

    def get_analytics_stats(self) -> Dict[str, Any]:
        """Get analytics service statistics"""
        return {
            "service_name": "AnalyticsReportingService",
            "operations": [
                "get_analytics",
                "export_data"],
            "high_cohesion": True,
            "responsibility": "Analytics, insights, and data export operations",
        }
