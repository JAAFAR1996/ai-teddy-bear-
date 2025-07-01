"""
Report Generation Application Service
Orchestrates the generation of comprehensive reports
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from src.domain.reporting.models import (
    ChildProgress,
    EmotionDistribution,
    InteractionAnalysis,
    ReportPeriod,
    SkillAnalysis,
)
from src.domain.reporting.services import BehaviorAnalyzer, EmotionAnalyzerService, ProgressAnalyzer, SkillAnalyzer


class ReportGenerationService:
    """Application service for generating comprehensive reports"""

    def __init__(self, database_service=None, analytics_service=None):
        self.db = database_service
        self.analytics = analytics_service
        self.logger = logging.getLogger(self.__class__.__name__)

        # Initialize domain services
        self.progress_analyzer = ProgressAnalyzer()
        self.emotion_analyzer = EmotionAnalyzerService()
        self.skill_analyzer = SkillAnalyzer()
        self.behavior_analyzer = BehaviorAnalyzer()

    async def generate_weekly_report(self, child_id: str, week_offset: int = 0) -> ChildProgress:
        """
        Generate comprehensive weekly report for a child

        Args:
            child_id: Child's unique identifier
            week_offset: 0 = current week, 1 = last week, etc.

        Returns:
            ChildProgress object with all metrics
        """
        try:
            # Calculate date range
            end_date = datetime.now() - timedelta(weeks=week_offset)
            start_date = end_date - timedelta(days=7)
            period = ReportPeriod(start_date=start_date, end_date=end_date)

            # Get child info
            child_info = await self._get_child_info(child_id)

            # Get interaction data
            interactions = await self._get_interactions(child_id, start_date, end_date)

            # Analyze all metrics using domain services
            emotion_analysis = self.emotion_analyzer.analyze_emotion_distribution(interactions)
            skill_analysis = self.skill_analyzer.analyze_skills_practiced(interactions)

            # Build comprehensive progress report
            progress = ChildProgress(
                child_id=child_id,
                child_name=child_info.get("name", "Unknown"),
                age=child_info.get("age", 5),
                period=period,
                # Basic interaction metrics
                total_interactions=len(interactions),
                avg_daily_interactions=len(interactions) / 7,
                longest_conversation=self.progress_analyzer.calculate_longest_conversation(interactions),
                favorite_topics=self.progress_analyzer.extract_favorite_topics(interactions),
                # Emotional analysis
                emotion_analysis=emotion_analysis,
                mood_trends=self.progress_analyzer.analyze_mood_trends(interactions, start_date, end_date),
                # Behavioral analysis
                attention_span=self.progress_analyzer.calculate_attention_span(interactions),
                response_time=self.progress_analyzer.calculate_response_time(interactions),
                vocabulary_growth=self.progress_analyzer.estimate_vocabulary_growth(interactions),
                question_frequency=self.progress_analyzer.calculate_question_frequency(interactions),
                # Learning analysis
                skill_analysis=skill_analysis,
                learning_achievements=self.skill_analyzer.identify_achievements(interactions),
                recommended_activities=self.skill_analyzer.generate_activity_recommendations(interactions),
                # Social analysis
                empathy_indicators=self.emotion_analyzer.count_empathy_indicators(interactions),
                sharing_behavior=self.emotion_analyzer.analyze_sharing_behavior(interactions),
                cooperation_level=self.emotion_analyzer.calculate_cooperation_level(interactions),
                # Sleep analysis (if data available)
                sleep_pattern_quality=self.emotion_analyzer.analyze_sleep_patterns(interactions),
                bedtime_conversations=self.emotion_analyzer.count_bedtime_conversations(interactions),
                # Red flags
                concerning_patterns=self.emotion_analyzer.identify_concerning_patterns(interactions),
                urgent_recommendations=self.emotion_analyzer.generate_urgent_recommendations(interactions),
            )

            self.logger.info(f"Generated weekly report for child {child_id}")
            return progress

        except Exception as e:
            self.logger.error(f"Weekly report generation failed for child {child_id}: {e}")
            raise

    async def generate_monthly_report(self, child_id: str) -> Dict[str, Any]:
        """Generate comprehensive monthly report"""
        try:
            # Get 4 weekly reports
            weekly_reports = []
            for week in range(4):
                weekly_report = await self.generate_weekly_report(child_id, week)
                weekly_reports.append(weekly_report)

            # Analyze trends across weeks
            monthly_trends = self._analyze_monthly_trends(weekly_reports)
            long_term_recommendations = self._generate_long_term_recommendations(weekly_reports)
            developmental_milestones = self._check_developmental_milestones(weekly_reports)

            report = {
                "child_id": child_id,
                "report_period": "monthly",
                "generated_at": datetime.now(),
                "weekly_reports": weekly_reports,
                "monthly_trends": monthly_trends,
                "long_term_recommendations": long_term_recommendations,
                "developmental_milestones": developmental_milestones,
            }

            self.logger.info(f"Generated monthly report for child {child_id}")
            return report

        except Exception as e:
            self.logger.error(f"Monthly report generation failed for child {child_id}: {e}")
            raise

    async def _get_child_info(self, child_id: str) -> Dict[str, Any]:
        """Get child information from database"""
        try:
            if self.db:
                # Real database query would go here
                return await self.db.get_child_info(child_id)

            # Fallback mock data
            return {"name": f"Child_{child_id}", "age": 5, "preferences": [], "special_needs": []}

        except Exception as e:
            self.logger.error(f"Failed to get child info for {child_id}: {e}")
            return {"name": "Unknown", "age": 5}

    async def _get_interactions(
        self, child_id: str, start_date: datetime, end_date: datetime
    ) -> List[InteractionAnalysis]:
        """Get interaction data from database"""
        try:
            if self.db:
                # Real database query would go here
                return await self.db.get_interactions(child_id, start_date, end_date)

            # Fallback mock data for testing
            mock_interactions = []
            for i in range(5):  # Mock 5 interactions
                interaction = InteractionAnalysis(
                    timestamp=start_date + timedelta(days=i),
                    duration=120 + i * 30,  # 2-5 minutes
                    primary_emotion="happy",
                    emotions={"happy": 0.7, "curious": 0.3},
                    topics_discussed=["stories", "games"],
                    skills_used=["listening", "speaking"],
                    behavioral_indicators=["engaged", "attentive"],
                    quality_score=0.8,
                )
                mock_interactions.append(interaction)

            return mock_interactions

        except Exception as e:
            self.logger.error(f"Failed to get interactions for {child_id}: {e}")
            return []

    def _analyze_monthly_trends(self, weekly_reports: List[ChildProgress]) -> Dict[str, Any]:
        """Analyze trends across weekly reports"""
        try:
            if not weekly_reports:
                return {}

            trends = {
                "interaction_trend": "stable",
                "emotion_stability_trend": "improving",
                "skill_development_trend": "positive",
                "attention_span_trend": "stable",
                "overall_progress": "good",
            }

            # Analyze interaction trends
            interaction_counts = [report.total_interactions for report in weekly_reports]
            if len(interaction_counts) >= 2:
                if interaction_counts[-1] > interaction_counts[0]:
                    trends["interaction_trend"] = "increasing"
                elif interaction_counts[-1] < interaction_counts[0]:
                    trends["interaction_trend"] = "decreasing"

            # Analyze emotion stability trends
            stability_scores = [report.emotion_analysis.stability_score for report in weekly_reports]
            if len(stability_scores) >= 2:
                if stability_scores[-1] > stability_scores[0]:
                    trends["emotion_stability_trend"] = "improving"
                elif stability_scores[-1] < stability_scores[0]:
                    trends["emotion_stability_trend"] = "declining"

            # Analyze skill development
            skill_counts = [report.skill_analysis.get_total_practice_sessions() for report in weekly_reports]
            if len(skill_counts) >= 2:
                if skill_counts[-1] > skill_counts[0]:
                    trends["skill_development_trend"] = "positive"
                elif skill_counts[-1] < skill_counts[0]:
                    trends["skill_development_trend"] = "needs_attention"

            return trends

        except Exception as e:
            self.logger.error(f"Monthly trends analysis error: {e}")
            return {}

    def _generate_long_term_recommendations(self, weekly_reports: List[ChildProgress]) -> List[str]:
        """Generate long-term recommendations based on monthly data"""
        try:
            recommendations = []

            if not weekly_reports:
                return recommendations

            # Analyze consistent patterns
            all_concerning_patterns = []
            for report in weekly_reports:
                all_concerning_patterns.extend(report.concerning_patterns)

            # If consistent concerns across weeks
            if len(all_concerning_patterns) >= len(weekly_reports):
                recommendations.append("مراجعة شاملة مع أخصائي تطوير الطفل")

            # Check for skill plateau
            recent_achievements = weekly_reports[-1].learning_achievements if weekly_reports else []
            if len(recent_achievements) < 2:
                recommendations.append("تنويع الأنشطة التعليمية لتحفيز التطور")

            # Check for interaction consistency
            avg_interactions = sum(report.total_interactions for report in weekly_reports) / len(weekly_reports)

            if avg_interactions < 10:
                recommendations.append("زيادة تكرار جلسات التفاعل اليومية")

            return recommendations

        except Exception as e:
            self.logger.error(f"Long-term recommendations generation error: {e}")
            return []

    def _check_developmental_milestones(self, weekly_reports: List[ChildProgress]) -> Dict[str, Any]:
        """Check developmental milestones based on monthly data"""
        try:
            if not weekly_reports:
                return {}

            latest_report = weekly_reports[-1]
            age = latest_report.age

            milestones = {
                "age_appropriate_development": True,
                "areas_on_track": [],
                "areas_needing_attention": [],
                "next_milestones": [],
            }

            # Age-appropriate checks
            if age >= 4:
                # Check social skills
                if latest_report.empathy_indicators >= 3:
                    milestones["areas_on_track"].append("التطور الاجتماعي والعاطفي")
                else:
                    milestones["areas_needing_attention"].append("التطور الاجتماعي")

                # Check attention span
                if latest_report.attention_span >= 5:
                    milestones["areas_on_track"].append("التركيز والانتباه")
                else:
                    milestones["areas_needing_attention"].append("تطوير فترة التركيز")

            if age >= 5:
                # Check vocabulary growth
                if latest_report.vocabulary_growth >= 10:
                    milestones["areas_on_track"].append("تطوير المفردات")
                else:
                    milestones["areas_needing_attention"].append("تطوير المفردات")

            # Suggest next milestones
            if age < 6:
                milestones["next_milestones"].append("تطوير مهارات القراءة البسيطة")
                milestones["next_milestones"].append("تحسين مهارات التعبير")

            return milestones

        except Exception as e:
            self.logger.error(f"Developmental milestones check error: {e}")
            return {}
