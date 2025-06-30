from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any

@dataclass
class Transcription:
    id: Optional[int] = None
    audio_file_path: Optional[str] = None
    text: Optional[str] = None
    language: Optional[str] = None
    confidence: Optional[float] = None
    created_at: Optional[datetime] = None
    user_id: Optional[int] = None
    conversation_id: Optional[int] = None
    duration: Optional[float] = None  # Audio duration in seconds
    model_used: Optional[str] = None  # Which STT model was used
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary for database operations."""
        return {
            "id": self.id,
            "audio_file_path": self.audio_file_path,
            "text": self.text,
            "language": self.language,
            "confidence": self.confidence,
            "created_at": self.created_at,
            "user_id": self.user_id,
            "conversation_id": self.conversation_id,
            "duration": self.duration,
            "model_used": self.model_used
        }