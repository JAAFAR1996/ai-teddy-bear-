from datetime import datetime
from typing import Optional

from sqlmodel import Field, Index, SQLModel


class EmotionLog(SQLModel, table=True):
    __tablename__ = "emotions_log"
    __table_args__ = (
        Index("idx_emotionlog_userid", "user_id"),
        Index("idx_emotionlog_timestamp", "timestamp"),
        Index("idx_emotionlog_emotiontype", "emotion_type"),
    )
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    timestamp: datetime = Field(index=True)
    emotion_type: str = Field(index=True)
    source: str  # 'audio', 'text', or 'both'
    score: float

    def to_dict(self) -> Any:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "timestamp": self.timestamp.isoformat(),
            "emotion_type": self.emotion_type,
            "source": self.source,
            "score": self.score,
        }
