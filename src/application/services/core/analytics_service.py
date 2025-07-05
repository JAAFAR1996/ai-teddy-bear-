"""
Dashboard Analytics Service
==========================

Application service for analytics processing and reporting.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List

from src.domain.parentdashboard.services.analytics_domain_service import \
    AnalyticsDomainService
from src.infrastructure.persistence.conversation_repository import \
    ConversationRepository


class DashboardAnalyticsService:
    """Application service for dashboard analytics"""

    def __init__(
        self,
        conversation_repository: ConversationRepository,
        analytics_domain_service: AnalyticsDomainService,
    ):
        self.conversation_repository = conversation_repository
        self.analytics_service = analytics_domain_service
        self.logger = logging.getLogger(self.__class__.__name__)

    async def get_child_analytics(
        self, child_id: str, period_days: int = 30, include_charts: bool = False
    ) -> Dict[str, Any]:
        """Get comprehensive analytics for a child"""

        try:
            start_date = datetime.now() - timedelta(days=period_days)
            end_date = datetime.now()

            # Get conversation logs
            logs = await self.conversation_repository.get_by_child_id(
                child_id, start_date=start_date, end_date=end_date
            )

            # Calculate analytics
            analytics = self.analytics_service.calculate_analytics(logs)

            result = {
                "analytics": analytics.__dict__,
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": period_days,
                },
                "insights": analytics.get_insights(),
                "recommendations": analytics.get_recommendations(),
            }

            # Add charts if requested
            if include_charts:
                # Would integrate with chart generation service
                result["charts"] = await self._generate_charts(analytics)

            return result

        except Exception as e:
            self.logger.error(f"Error getting analytics for child {child_id}: {e}")
            return {}

    async def get_comparative_analytics(
        self, child_ids: List[str], period_days: int = 30
    ) -> Dict[str, Any]:
        """Get comparative analytics across multiple children"""

        try:
            comparative_data = {
                "children": {},
                "comparisons": {},
                "period_days": period_days,
            }

            all_analytics = []

            for child_id in child_ids:
                analytics_data = await self.get_child_analytics(
                    child_id, period_days, include_charts=False
                )

                if analytics_data:
                    comparative_data["children"][child_id] = analytics_data
                    all_analytics.append(analytics_data["analytics"])

            # Calculate comparisons
            if len(all_analytics) > 1:
                comparative_data["comparisons"] = self._calculate_comparisons(
                    all_analytics
                )

            return comparative_data

        except Exception as e:
            self.logger.error(f"Error getting comparative analytics: {e}")
            return {}

    async def get_trend_analysis(self, child_id: str, weeks: int = 4) -> Dict[str, Any]:
        """Get trend analysis over specified weeks"""

        try:
            trends = {"weekly_data": [], "overall_trends": {}, "insights": []}

            # Get data for each week
            for week in range(weeks):
                week_end = datetime.now() - timedelta(weeks=week)
                week_start = week_end - timedelta(weeks=1)

                logs = await self.conversation_repository.get_by_child_id(
                    child_id, start_date=week_start, end_date=week_end
                )

                weekly_analytics = self.analytics_service.calculate_analytics(logs)
                trends["weekly_data"].append(
                    {
                        "week_start": week_start.isoformat(),
                        "week_end": week_end.isoformat(),
                        "analytics": weekly_analytics.__dict__,
                    }
                )

            # Calculate overall trends
            trends["overall_trends"] = self._calculate_trends(trends["weekly_data"])

            # Generate insights
            trends["insights"] = self._generate_trend_insights(trends["overall_trends"])

            return trends

        except Exception as e:
            self.logger.error(f"Error getting trend analysis for child {child_id}: {e}")
            return {}

    async def _generate_charts(self, analytics) -> Dict[str, str]:
        """Generate charts for analytics data"""
        # Placeholder - would integrate with chart generation service
        return {
            "usage_trend": "base64_chart_data",
            "topic_distribution": "base64_chart_data",
            "sentiment_overview": "base64_chart_data",
        }

    def _calculate_comparisons(self, analytics_list: List[Dict]) -> Dict[str, Any]:
        """Calculate comparative metrics"""

        if not analytics_list:
            return {}

        # Calculate averages
        avg_conversations = sum(a["total_conversations"] for a in analytics_list) / len(
            analytics_list
        )
        avg_duration = sum(a["total_duration_minutes"] for a in analytics_list) / len(
            analytics_list
        )
        avg_quality = sum(a["interaction_quality_score"] for a in analytics_list) / len(
            analytics_list
        )

        return {
            "averages": {
                "conversations": avg_conversations,
                "duration_minutes": avg_duration,
                "quality_score": avg_quality,
            },
            "variations": {
                "highest_usage": max(a["total_conversations"] for a in analytics_list),
                "lowest_usage": min(a["total_conversations"] for a in analytics_list),
                "highest_quality": max(
                    a["interaction_quality_score"] for a in analytics_list
                ),
                "lowest_quality": min(
                    a["interaction_quality_score"] for a in analytics_list
                ),
            },
        }

    def _calculate_trends(self, weekly_data: List[Dict]) -> Dict[str, Any]:
        """Calculate trend directions"""

        if len(weekly_data) < 2:
            return {}

        # Sort by week (newest first, so reverse for trend calculation)
        sorted_data = sorted(weekly_data, key=lambda x: x["week_start"])

        # Calculate trends for key metrics
        conversations_trend = self._calculate_metric_trend(
            [w["analytics"]["total_conversations"] for w in sorted_data]
        )

        quality_trend = self._calculate_metric_trend(
            [w["analytics"]["interaction_quality_score"] for w in sorted_data]
        )

        sentiment_trend = self._calculate_metric_trend(
            [
                w["analytics"]["sentiment_breakdown"].get("positive", 0)
                for w in sorted_data
            ]
        )

        return {
            "conversations": conversations_trend,
            "quality": quality_trend,
            "positive_sentiment": sentiment_trend,
        }

    def _calculate_metric_trend(self, values: List[float]) -> Dict[str, Any]:
        """Calculate trend for a specific metric"""

        if len(values) < 2:
            return {"direction": "stable", "change_percent": 0}

        start_value = values[0]
        end_value = values[-1]

        if start_value == 0:
            change_percent = 100 if end_value > 0 else 0
        else:
            change_percent = ((end_value - start_value) / start_value) * 100

        if change_percent > 5:
            direction = "increasing"
        elif change_percent < -5:
            direction = "decreasing"
        else:
            direction = "stable"

        return {
            "direction": direction,
            "change_percent": round(change_percent, 2),
            "start_value": start_value,
            "end_value": end_value,
        }

    def _generate_trend_insights(self, trends: Dict[str, Any]) -> List[str]:
        """Generate insights from trend data"""

        insights = []

        # Conversation trends
        conv_trend = trends.get("conversations", {})
        if conv_trend.get("direction") == "increasing":
            insights.append("Child engagement is increasing over time")
        elif conv_trend.get("direction") == "decreasing":
            insights.append("Child engagement has been declining")

        # Quality trends
        quality_trend = trends.get("quality", {})
        if quality_trend.get("direction") == "increasing":
            insights.append("Conversation quality is improving")
        elif quality_trend.get("direction") == "decreasing":
            insights.append("Conversation quality may need attention")

        # Sentiment trends
        sentiment_trend = trends.get("positive_sentiment", {})
        if sentiment_trend.get("direction") == "decreasing":
            insights.append("Child's emotional state may need monitoring")
        elif sentiment_trend.get("direction") == "increasing":
            insights.append("Child shows improving emotional well-being")

        return insights
