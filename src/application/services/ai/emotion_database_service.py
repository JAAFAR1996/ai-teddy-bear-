"""Database service for emotion management."""

from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import structlog
from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import sessionmaker

from ....domain.emotion.models import (EmotionAnalytics, EmotionResult)

logger = structlog.get_logger(__name__)


class EmotionDatabaseService:
    """Service for managing emotion data in database."""

    def __init__(
        self,
        database_url: str = "sqlite:///teddy_emotions.db",
        retention_days: int = 365,
    ):
        self.database_url = database_url
        self.retention_days = retention_days
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self._initialize_database()

    def _initialize_database(self) -> None:
        """Initialize database tables."""
        try:
            # Create tables if they don't exist
            metadata = MetaData()
            metadata.create_all(self.engine)
            logger.info(" Database initialized successfully")
        except Exception as e:
            logger.error(f" Database initialization failed: {e}")

    @contextmanager
    def get_db_session(self):
        """Get database session with automatic cleanup."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()

    async def save_emotion_result(
        self,
        emotion_result: EmotionResult,
        child_id: str,
        session_id: Optional[str] = None,
        device_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Save emotion analysis result to database.

        Returns:
            Database record ID
        """
        try:
            with self.get_db_session() as session:
                # Create emotion record
                emotion_record = {
                    "id": self._generate_id(),
                    "child_id": child_id,
                    "session_id": session_id or self._generate_session_id(),
                    "device_id": device_id,
                    "primary_emotion": emotion_result.primary_emotion,
                    "confidence": emotion_result.confidence,
                    "all_emotions": emotion_result.all_emotions,
                    "source": emotion_result.source,
                    "behavioral_indicators": emotion_result.behavioral_indicators,
                    "recommendations": emotion_result.recommendations,
                    "context": context,
                    "created_at": datetime.now(),
                    "updated_at": datetime.now(),
                }

                # Mock save (implement with actual ORM models)
                record_id = emotion_record["id"]
                logger.info(f" Emotion saved: {record_id}")

                return record_id

        except Exception as e:
            logger.error(f" Failed to save emotion: {e}")
            raise

    async def get_child_emotions(
        self, child_id: str, hours: int = 24, limit: int = 100
    ) -> List[EmotionResult]:
        """Get emotion history for a child."""
        try:
            with self.get_db_session() as session:
                # Mock query (implement with actual ORM)
                start_time = datetime.now() - timedelta(hours=hours)

                # This would be actual database query
                mock_emotions = [
                    EmotionResult(
                        primary_emotion="happy",
                        confidence=0.85,
                        all_emotions={"happy": 0.85, "curious": 0.15},
                        source="text",
                        timestamp=datetime.now().isoformat(),
                        behavioral_indicators=["positive words"],
                        recommendations=["Continue positive engagement"],
                    )
                ]

                return mock_emotions[:limit]

        except Exception as e:
            logger.error(f" Failed to get emotions: {e}")
            return []

    async def get_emotion_analytics(
        self, child_id: str, days: int = 7
    ) -> Optional[EmotionAnalytics]:
        """Generate emotion analytics for a child."""
        try:
            with self.get_db_session() as session:
                # Mock analytics generation
                analytics = EmotionAnalytics(
                    child_id=child_id,
                    analysis_period=f"{days} days",
                    total_interactions=45,
                    emotion_distribution={
                        "happy": 20,
                        "curious": 15,
                        "calm": 8,
                        "sad": 2,
                    },
                    dominant_emotion="happy",
                    emotional_stability_score=0.82,
                    behavioral_patterns=[
                        "Consistent positive engagement",
                        "High curiosity levels",
                        "Good emotional regulation",
                    ],
                    risk_assessment="low",
                    trends={"happiness": 0.15, "stability": 0.08},
                    recommendations=[
                        "Continue current supportive approach",
                        "Encourage creative activities",
                    ],
                    analysis_date=datetime.now(),
                )

                return analytics

        except Exception as e:
            logger.error(f" Failed to generate analytics: {e}")
            return None

    async def cleanup_old_data(self, days_to_keep: Optional[int] = None) -> int:
        """Clean up old emotion data."""
        try:
            cleanup_days = days_to_keep or self.retention_days
            cutoff_date = datetime.now() - timedelta(days=cleanup_days)

            with self.get_db_session() as session:
                # Mock cleanup (implement with actual ORM)
                deleted_count = 0  # Would be actual deletion count

                logger.info(f" Cleaned up {deleted_count} old records")
                return deleted_count

        except Exception as e:
            logger.error(f" Cleanup failed: {e}")
            return 0

    async def get_child_profile(self, child_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive child emotion profile."""
        try:
            with self.get_db_session() as session:
                # Mock profile (implement with actual queries)
                profile = {
                    "child_id": child_id,
                    "total_interactions": 150,
                    "dominant_emotions": {
                        "happy": 0.45,
                        "curious": 0.30,
                        "calm": 0.20,
                        "sad": 0.05,
                    },
                    "behavioral_patterns": [
                        "High engagement with stories",
                        "Positive response to encouragement",
                        "Questions frequently",
                    ],
                    "risk_factors": [],
                    "last_interaction": datetime.now() - timedelta(hours=2),
                    "emotional_stability": 0.85,
                }

                return profile

        except Exception as e:
            logger.error(f" Failed to get profile: {e}")
            return None

    def _generate_id(self) -> str:
        """Generate unique ID for records."""
        import uuid

        return str(uuid.uuid4())

    def _generate_session_id(self) -> str:
        """Generate session ID."""
        return f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
