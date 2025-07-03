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
    
    def __init__(self, analytics_service, cache_service, chart_service, export_service):
        """Initialize analytics and reporting service"""
        self.analytics_service = analytics_service
        self.cache_service = cache_service
        self.chart_service = chart_service
        self.export_service = export_service
        self.logger = logging.getLogger(__name__)
    
    async def get_analytics(self, analytics_request: AnalyticsRequest) -> Dict[str, Any]:
        """Get comprehensive analytics for a child using parameter object"""
        try:
            # Check cache first
            cached_analytics = self.cache_service.get_cached_analytics(
                analytics_request.child_id, analytics_request.period_days
            )
            
            if cached_analytics and not analytics_request.include_charts:
                self.logger.debug(f"Returning cached analytics for child {analytics_request.child_id}")
                return cached_analytics
            
            # Get fresh analytics
            analytics = await self.analytics_service.get_child_analytics(
                analytics_request.child_id,
                analytics_request.period_days,
                analytics_request.include_charts
            )
            
            # Cache results (without charts for size efficiency)
            if analytics and not analytics_request.include_charts:
                self.cache_service.cache_analytics(
                    analytics_request.child_id,
                    analytics_request.period_days,
                    analytics
                )
            
            self.logger.info(f"Successfully generated analytics for child {analytics_request.child_id}")
            return analytics
            
        except Exception as e:
            self.logger.error(f"Failed to get analytics for child {analytics_request.child_id}: {e}")
            return {"error": str(e), "analytics": {}}
    
    async def get_comparative_analytics(
        self, 
        child_ids: List[str], 
        period_days: int = 30
    ) -> Dict[str, Any]:
        """Get comparative analytics across multiple children"""
        try:
            return await self.analytics_service.get_comparative_analytics(child_ids, period_days)
        except Exception as e:
            self.logger.error(f"Failed to get comparative analytics: {e}")
            return {"error": str(e), "comparison": {}}
    
    async def get_trend_analysis(self, child_id: str, weeks: int = 4) -> Dict[str, Any]:
        """Get trend analysis over specified weeks"""
        try:
            return await self.analytics_service.get_trend_analysis(child_id, weeks)
        except Exception as e:
            self.logger.error(f"Failed to get trend analysis for child {child_id}: {e}")
            return {"error": str(e), "trends": {}}
    
    async def export_data(self, export_request: ExportRequest) -> bytes:
        """Export data based on export request with proper formatting"""
        try:
            if export_request.data_type == "conversations":
                return await self._export_conversations(export_request)
            elif export_request.data_type == "analytics":
                return await self._export_analytics(export_request)
            else:
                raise ValueError(f"Unsupported data type: {export_request.data_type}")
            
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
                include_charts=True
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
    
    async def _export_conversations(self, export_request: ExportRequest) -> bytes:
        """Export conversation history in requested format"""
        try:
            conversations = []  # Would fetch from database
            
            if export_request.format == "json":
                return await self.export_service.export_conversation_history_as_json(conversations)
            elif export_request.format == "excel":
                return await self.export_service.export_conversation_history_as_excel(conversations)
            else:  # PDF
                return await self.export_service.export_conversation_history_as_pdf(
                    conversations, child_name="Child Name"
                )
            
        except Exception as e:
            self.logger.error(f"Failed to export conversations: {e}")
            return b""
    
    async def _enrich_analytics_with_insights(self, analytics: Dict[str, Any]) -> Dict[str, Any]:
        """Add AI-generated insights to analytics data"""
        try:
            analytics_data = analytics.get("analytics", {})
            
            # Generate insights
            insights = []
            
            # Engagement insights
            engagement = analytics_data.get("engagement_score", 0)
            if engagement > 0.8:
                insights.append("High engagement levels - child is actively participating!")
            elif engagement < 0.4:
                insights.append("Low engagement detected - consider new activities")
            
            # Learning progress insights
            learning = analytics_data.get("learning_progress", {})
            if learning.get("improvement_rate", 0) > 0.1:
                insights.append("Strong learning progress - great job!")
            
            # Safety insights
            safety_score = analytics_data.get("safety_score", 1.0)
            if safety_score < 0.9:
                insights.append("Some content concerns detected - review recommended")
            
            analytics["insights"] = insights
            return analytics
            
        except Exception as e:
            self.logger.error(f"Failed to enrich analytics with insights: {e}")
            return analytics
    
    def _generate_content_suggestions(self, analytics_data: Dict[str, Any]) -> List[str]:
        """Generate content suggestions based on analytics"""
        suggestions = []
        
        topics_freq = analytics_data.get("topics_frequency", {})
        if "education" in topics_freq and topics_freq["education"] > 5:
            suggestions.append("Continue educational conversations - great engagement!")
        
        if "games" in topics_freq and topics_freq["games"] > 3:
            suggestions.append("Try educational games to combine fun with learning")
        
        # Add more content suggestions based on patterns
        engagement = analytics_data.get("engagement_score", 0)
        if engagement < 0.5:
            suggestions.append("Try interactive storytelling to boost engagement")
        
        return suggestions
    
    def _generate_time_suggestions(self, analytics_data: Dict[str, Any]) -> List[str]:
        """Generate time management suggestions"""
        suggestions = []
        
        avg_session = analytics_data.get("average_session_minutes", 0)
        if avg_session > 30:
            suggestions.append("Consider shorter sessions with breaks for better focus")
        elif avg_session < 5:
            suggestions.append("Encourage longer, more engaged conversations")
        
        # Usage patterns
        peak_hours = analytics_data.get("peak_usage_hours", [])
        if peak_hours:
            suggestions.append(f"Peak engagement at {peak_hours[0]}:00 - great time for learning!")
        
        return suggestions
    
    def _generate_learning_suggestions(self, analytics_data: Dict[str, Any]) -> List[str]:
        """Generate learning activity suggestions"""
        suggestions = []
        
        learning_progress = analytics_data.get("learning_progress", {})
        if isinstance(learning_progress, dict):
            engagement = learning_progress.get("educational_engagement", 0)
            if engagement < 0.3:
                suggestions.append("Introduce more educational topics and activities")
            elif engagement > 0.7:
                suggestions.append("Advanced learning activities could be beneficial")
        
        # Skill development
        skills = analytics_data.get("skills_development", {})
        if skills.get("creativity", 0) < 0.5:
            suggestions.append("Encourage creative activities like storytelling and art")
        
        return suggestions
    
    def _generate_safety_suggestions(self, analytics_data: Dict[str, Any]) -> List[str]:
        """Generate safety-related suggestions"""
        suggestions = []
        
        sentiment = analytics_data.get("sentiment_breakdown", {})
        negative_ratio = sentiment.get("negative", 0)
        
        if negative_ratio > 0.3:
            suggestions.append(
                "High negative sentiment detected - consider professional guidance"
            )
        elif negative_ratio > 0.1:
            suggestions.append("Monitor emotional well-being closely")
        
        safety_score = analytics_data.get("safety_score", 1.0)
        if safety_score < 0.9:
            suggestions.append("Review recent conversations for safety concerns")
        
        return suggestions
    
    def _generate_engagement_suggestions(self, analytics_data: Dict[str, Any]) -> List[str]:
        """Generate engagement improvement suggestions"""
        suggestions = []
        
        engagement = analytics_data.get("engagement_score", 0)
        response_time = analytics_data.get("average_response_time", 0)
        
        if engagement < 0.6:
            suggestions.append("Try more interactive content to boost engagement")
        
        if response_time > 10:
            suggestions.append("Child takes time to respond - allow for thinking time")
        
        return suggestions
    
    def _generate_summary_insights(self, analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate high-level summary insights"""
        return {
            "overall_health": self._calculate_overall_health(analytics_data),
            "key_strengths": self._identify_key_strengths(analytics_data),
            "areas_for_improvement": self._identify_improvement_areas(analytics_data),
            "progress_trajectory": self._analyze_progress_trajectory(analytics_data)
        }
    
    def _calculate_overall_health(self, analytics_data: Dict[str, Any]) -> str:
        """Calculate overall interaction health score"""
        engagement = analytics_data.get("engagement_score", 0)
        safety = analytics_data.get("safety_score", 1.0)
        learning = analytics_data.get("learning_progress", {}).get("overall_score", 0)
        
        overall_score = (engagement + safety + learning) / 3
        
        if overall_score > 0.8:
            return "excellent"
        elif overall_score > 0.6:
            return "good"
        elif overall_score > 0.4:
            return "fair"
        else:
            return "needs_attention"
    
    def _identify_key_strengths(self, analytics_data: Dict[str, Any]) -> List[str]:
        """Identify key strengths from analytics"""
        strengths = []
        
        if analytics_data.get("engagement_score", 0) > 0.7:
            strengths.append("High engagement and participation")
        
        if analytics_data.get("safety_score", 1.0) > 0.95:
            strengths.append("Excellent safety awareness")
        
        learning = analytics_data.get("learning_progress", {})
        if learning.get("educational_engagement", 0) > 0.6:
            strengths.append("Strong learning motivation")
        
        return strengths
    
    def _identify_improvement_areas(self, analytics_data: Dict[str, Any]) -> List[str]:
        """Identify areas that need improvement"""
        areas = []
        
        if analytics_data.get("engagement_score", 0) < 0.4:
            areas.append("Increase interaction engagement")
        
        if analytics_data.get("safety_score", 1.0) < 0.9:
            areas.append("Address safety concerns")
        
        negative_sentiment = analytics_data.get("sentiment_breakdown", {}).get("negative", 0)
        if negative_sentiment > 0.2:
            areas.append("Improve emotional well-being")
        
        return areas
    
    def _analyze_progress_trajectory(self, analytics_data: Dict[str, Any]) -> str:
        """Analyze the trajectory of progress"""
        learning = analytics_data.get("learning_progress", {})
        improvement_rate = learning.get("improvement_rate", 0)
        
        if improvement_rate > 0.1:
            return "improving"
        elif improvement_rate > -0.05:
            return "stable"
        else:
            return "declining"
    
    async def _generate_comparison_charts(self, comparative_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate charts for comparative analytics"""
        try:
            charts = {}
            
            # Generate comparison charts using chart service
            if self.chart_service:
                charts["engagement_comparison"] = await self.chart_service.create_comparison_chart(
                    comparative_data.get("engagement_data", {})
                )
                
                charts["learning_comparison"] = await self.chart_service.create_comparison_chart(
                    comparative_data.get("learning_data", {})
                )
            
            return charts
            
        except Exception as e:
            self.logger.error(f"Failed to generate comparison charts: {e}")
            return {}
    
    async def _generate_trend_charts(self, trend_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate charts for trend analysis"""
        try:
            charts = {}
            
            if self.chart_service:
                charts["trend_line"] = await self.chart_service.create_trend_chart(
                    trend_data.get("trend_points", [])
                )
            
            return charts
            
        except Exception as e:
            self.logger.error(f"Failed to generate trend charts: {e}")
            return {}
    
    def _analyze_trends(self, trend_data: Dict[str, Any]) -> List[str]:
        """Analyze trends and provide insights"""
        insights = []
        
        trend_direction = trend_data.get("overall_trend", "stable")
        if trend_direction == "improving":
            insights.append("Positive trend detected - child is progressing well!")
        elif trend_direction == "declining":
            insights.append("Declining trend detected - may need intervention")
        
        return insights
    
    def get_analytics_stats(self) -> Dict[str, Any]:
        """Get analytics service statistics"""
        return {
            "service_name": "AnalyticsReportingService",
            "operations": ["get_analytics", "export_data"],
            "high_cohesion": True,
            "responsibility": "Analytics, insights, and data export operations"
        } 