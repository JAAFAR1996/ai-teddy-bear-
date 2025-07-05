from datetime import datetime
from typing import List, Optional

from sqlmodel import Session, func, select

from src.core.domain.entities.emotion_log import EmotionLog


class EmotionLogRepository:
    def __init__(self, session: Session):
        self.session = session

    def add_many(self, logs: List[EmotionLog]) -> None:
        """Batch insert for high performance."""
        self.session.add_all(logs)
        self.session.commit()

    def list(
        self,
        user_id: str,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
        emotion_type: Optional[str] = None,
    ) -> List[EmotionLog]:
        q = select(EmotionLog).where(EmotionLog.user_id == user_id)
        if start:
            q = q.where(EmotionLog.timestamp >= start)
        if end:
            q = q.where(EmotionLog.timestamp <= end)
        if emotion_type:
            q = q.where(EmotionLog.emotion_type == emotion_type)
        q = q.order_by(EmotionLog.timestamp.desc()).limit(limit).offset(offset)
        return self.session.exec(q).all()

    def aggregate_stats(str="day") -> None:
        """Aggregation: avg score & count per emotion_type per period (day/week)."""
        fmt = "%Y-%m-%d" if period == "day" else "%Y-%W"
        q = (
            select(
                func.strftime(fmt, EmotionLog.timestamp).label("period"),
                EmotionLog.emotion_type,
                func.avg(EmotionLog.score).label("avg_score"),
                func.count().label("count"),
            )
            .where(EmotionLog.user_id == user_id)
            .group_by("period", EmotionLog.emotion_type)
            .order_by("period")
        )
        return self.session.exec(q).all()


# مثال استخدام:
# repo = EmotionLogRepository(session)
# repo.add_many([EmotionLog(user_id=..., ...), ...])
# logs = repo.list(user_id, limit=20, offset=0, emotion_type="happy")
# stats = repo.aggregate_stats(user_id, period="week")
