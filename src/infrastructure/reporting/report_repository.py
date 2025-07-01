"""
Report Repository Infrastructure
Handles data persistence and retrieval for reporting
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.domain.reporting.models import InteractionAnalysis, ProgressMetrics


class ReportRepository:
    """Infrastructure component for report data persistence"""

    def __init__(self, database_service=None):
        self.db = database_service
        self.logger = logging.getLogger(self.__class__.__name__)

    async def store_in_parent_reports(self, metrics: ProgressMetrics, recommendations: List[Dict]) -> str:
        """Store analysis results in parent_reports table"""
        try:
            report_id = f"report_{metrics.child_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            if self.db:
                query = """
                INSERT INTO parent_reports (
                    report_id, child_id, analysis_date, 
                    vocabulary_score, emotional_score, cognitive_score,
                    developmental_concerns, recommendations, urgency_level
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """

                await self.db.execute(
                    query,
                    (
                        report_id,
                        metrics.child_id,
                        metrics.analysis_date,
                        metrics.vocabulary_complexity_score,
                        metrics.emotional_intelligence_score,
                        metrics.cognitive_development_score,
                        str(metrics.developmental_concerns),
                        str(recommendations),
                        metrics.urgency_level.value,
                    ),
                )

                self.logger.info(f"Stored report {report_id} in database")
            else:
                self.logger.warning("No database service available, report not stored")

            return report_id

        except Exception as e:
            self.logger.error(f"Report storage error: {e}")
            raise

    async def get_child_info(self, child_id: int) -> Dict[str, Any]:
        """Get child information from database"""
        try:
            if self.db:
                query = """
                SELECT name, age, preferences, special_needs, learning_style
                FROM children 
                WHERE child_id = %s
                """
                result = await self.db.fetch_one(query, (child_id,))

                if result:
                    return {
                        "name": result["name"],
                        "age": result["age"],
                        "preferences": result.get("preferences", []),
                        "special_needs": result.get("special_needs", []),
                        "learning_style": result.get("learning_style", "visual"),
                    }

            # Fallback data
            return {
                "name": f"Child_{child_id}",
                "age": 5,
                "preferences": [],
                "special_needs": [],
                "learning_style": "visual",
            }

        except Exception as e:
            self.logger.error(f"Get child info error for {child_id}: {e}")
            return {"name": "Unknown", "age": 5}

    async def get_interactions(
        self, child_id: str, start_date: datetime, end_date: datetime
    ) -> List[InteractionAnalysis]:
        """Get interaction data from database"""
        try:
            if self.db:
                query = """
                SELECT timestamp, duration, primary_emotion, emotions, 
                       topics_discussed, skills_used, behavioral_indicators, quality_score
                FROM interactions 
                WHERE child_id = %s AND timestamp BETWEEN %s AND %s
                ORDER BY timestamp
                """

                results = await self.db.fetch_all(query, (child_id, start_date, end_date))

                interactions = []
                for row in results:
                    interaction = InteractionAnalysis(
                        timestamp=row["timestamp"],
                        duration=row["duration"],
                        primary_emotion=row["primary_emotion"],
                        emotions=row["emotions"] or {},
                        topics_discussed=row["topics_discussed"] or [],
                        skills_used=row["skills_used"] or [],
                        behavioral_indicators=row["behavioral_indicators"] or [],
                        quality_score=row["quality_score"] or 0.5,
                    )
                    interactions.append(interaction)

                return interactions

            # Fallback mock data
            return self._generate_mock_interactions(start_date, end_date)

        except Exception as e:
            self.logger.error(f"Get interactions error for {child_id}: {e}")
            return []

    async def get_recent_interactions(self, child_id: int, limit: int = 20) -> List[InteractionAnalysis]:
        """Get recent interactions for analysis"""
        try:
            if self.db:
                query = """
                SELECT timestamp, duration, primary_emotion, emotions, 
                       topics_discussed, skills_used, behavioral_indicators, quality_score
                FROM interactions 
                WHERE child_id = %s 
                ORDER BY timestamp DESC 
                LIMIT %s
                """

                results = await self.db.fetch_all(query, (child_id, limit))

                interactions = []
                for row in results:
                    interaction = InteractionAnalysis(
                        timestamp=row["timestamp"],
                        duration=row["duration"],
                        primary_emotion=row["primary_emotion"],
                        emotions=row["emotions"] or {},
                        topics_discussed=row["topics_discussed"] or [],
                        skills_used=row["skills_used"] or [],
                        behavioral_indicators=row["behavioral_indicators"] or [],
                        quality_score=row["quality_score"] or 0.5,
                    )
                    interactions.append(interaction)

                return interactions

            return []

        except Exception as e:
            self.logger.error(f"Get recent interactions error for {child_id}: {e}")
            return []

    def _generate_mock_interactions(self, start_date: datetime, end_date: datetime) -> List[InteractionAnalysis]:
        """Generate mock interaction data for testing"""
        try:
            import random
            from datetime import timedelta

            interactions = []
            current_date = start_date

            while current_date <= end_date:
                # Generate 1-3 interactions per day
                daily_interactions = random.randint(1, 3)

                for i in range(daily_interactions):
                    interaction = InteractionAnalysis(
                        timestamp=current_date + timedelta(hours=random.randint(9, 20)),
                        duration=random.randint(60, 300),  # 1-5 minutes
                        primary_emotion=random.choice(["happy", "curious", "calm", "excited"]),
                        emotions={
                            "happy": random.uniform(0.3, 0.8),
                            "curious": random.uniform(0.2, 0.7),
                            "calm": random.uniform(0.1, 0.5),
                        },
                        topics_discussed=random.sample(
                            [
                                "stories",
                                "games",
                                "animals",
                                "colors",
                                "numbers",
                                "family",
                                "friends",
                                "school",
                                "food",
                                "toys",
                            ],
                            random.randint(1, 3),
                        ),
                        skills_used=random.sample(
                            [
                                "listening",
                                "speaking",
                                "counting",
                                "reading",
                                "problem_solving",
                                "creativity",
                                "social_skills",
                            ],
                            random.randint(1, 4),
                        ),
                        behavioral_indicators=random.sample(
                            ["engaged", "attentive", "cooperative", "responsive", "creative", "patient", "curious"],
                            random.randint(1, 3),
                        ),
                        quality_score=random.uniform(0.5, 1.0),
                    )
                    interactions.append(interaction)

                current_date += timedelta(days=1)

            return interactions

        except Exception as e:
            self.logger.error(f"Mock interactions generation error: {e}")
            return []

    async def store_report_metadata(self, report_data: Dict[str, Any]) -> str:
        """Store report metadata for tracking"""
        try:
            report_id = report_data.get("report_id", f"meta_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

            if self.db:
                query = """
                INSERT INTO report_metadata (
                    report_id, child_id, report_type, generated_at,
                    file_path, format, status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """

                await self.db.execute(
                    query,
                    (
                        report_id,
                        report_data.get("child_id"),
                        report_data.get("report_type", "weekly"),
                        report_data.get("generated_at", datetime.now()),
                        report_data.get("file_path", ""),
                        report_data.get("format", "pdf"),
                        "completed",
                    ),
                )

                self.logger.info(f"Stored report metadata {report_id}")

            return report_id

        except Exception as e:
            self.logger.error(f"Report metadata storage error: {e}")
            return ""

    async def get_report_history(self, child_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get report generation history for a child"""
        try:
            if self.db:
                query = """
                SELECT report_id, report_type, generated_at, format, status
                FROM report_metadata 
                WHERE child_id = %s 
                ORDER BY generated_at DESC 
                LIMIT %s
                """

                results = await self.db.fetch_all(query, (child_id, limit))
                return [dict(row) for row in results]

            return []

        except Exception as e:
            self.logger.error(f"Get report history error for {child_id}: {e}")
            return []
