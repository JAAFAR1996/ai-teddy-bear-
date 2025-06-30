"""
🧸 AI Teddy Bear - Domain Models
نماذج البيانات الأساسية للنظام
"""

from datetime import datetime
from typing import Dict, Any, Optional, List, Literal
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, ConfigDict, validator
from enum import Enum


class Language(str, Enum):
    """Supported languages"""
    ARABIC = "ar"
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"


class LearningLevel(str, Enum):
    """Learning levels based on age"""
    PRESCHOOL = "preschool"  # 3-5 years
    EARLY_ELEMENTARY = "early_elementary"  # 6-7 years
    ELEMENTARY = "elementary"  # 8-10 years
    MIDDLE_SCHOOL = "middle_school"  # 11-13 years


class EmotionType(str, Enum):
    """Emotion types"""
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    SCARED = "scared"
    EXCITED = "excited"
    NEUTRAL = "neutral"
    LOVE = "love"


class MessageCategory(str, Enum):
    """Message categories"""
    GREETING = "greeting"
    STORY_REQUEST = "story_request"
    PLAY_REQUEST = "play_request"
    LEARNING = "learning"
    MUSIC = "music"
    QUESTION = "question"
    CONVERSATION = "conversation"
    EMOTION = "emotion"


class BaseEntity(BaseModel):
    """Base entity with common fields"""
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }
    )
    
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


class DeviceInfo(BaseEntity):
    """ESP32 device information"""
    device_id: str = Field(..., description="Unique device identifier (UDID)")
    firmware_version: str = Field(default="2.0.0")
    status: Literal["online", "offline", "maintenance"] = "offline"
    last_seen: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @validator("device_id")
    def validate_device_id(cls, v):
        if not v or len(v) < 5:
            raise ValueError("Invalid device ID")
        return v.upper()


class ChildProfile(BaseEntity):
    """Child profile with preferences and settings"""
    device_id: str = Field(..., description="Associated device UDID")
    name: str = Field(..., min_length=1, max_length=50)
    age: int = Field(..., ge=2, le=15)
    language: Language = Language.ARABIC
    learning_level: Optional[LearningLevel] = None
    preferences: Dict[str, Any] = Field(default_factory=dict)
    special_needs: Optional[List[str]] = Field(default_factory=list)
    parent_email: Optional[str] = None
    
    @validator("learning_level", always=True)
    def set_learning_level(cls, v, values):
        if v is None and "age" in values:
            age = values["age"]
            if age <= 5:
                return LearningLevel.PRESCHOOL
            elif age <= 7:
                return LearningLevel.EARLY_ELEMENTARY
            elif age <= 10:
                return LearningLevel.ELEMENTARY
            else:
                return LearningLevel.MIDDLE_SCHOOL
        return v


class AudioData(BaseModel):
    """Audio data model"""
    audio_base64: str = Field(..., description="Base64 encoded audio data")
    format: Literal["mp3", "wav", "opus", "webm"] = "mp3"
    sample_rate: int = Field(default=16000)
    duration_seconds: Optional[float] = None
    size_bytes: Optional[int] = None


class VoiceMessage(BaseEntity):
    """Voice message from child"""
    device_id: str
    child_id: UUID
    audio_data: Optional[AudioData] = None
    transcribed_text: Optional[str] = None
    language: Language = Language.ARABIC
    emotion: Optional[EmotionType] = None
    category: Optional[MessageCategory] = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class AIResponse(BaseEntity):
    """AI-generated response"""
    message_id: UUID = Field(..., description="Original message ID")
    text: str = Field(..., min_length=1)
    emotion: EmotionType = EmotionType.NEUTRAL
    category: MessageCategory = MessageCategory.CONVERSATION
    learning_points: List[str] = Field(default_factory=list)
    voice_settings: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Conversation(BaseEntity):
    """Complete conversation record"""
    device_id: str
    child_id: UUID
    session_id: UUID = Field(default_factory=uuid4)
    message: VoiceMessage
    response: AIResponse
    processing_time_ms: int = Field(default=0, ge=0)
    success: bool = True
    error_message: Optional[str] = None


class EmotionAnalysis(BaseModel):
    """Emotion analysis result"""
    primary_emotion: EmotionType
    confidence: float = Field(ge=0.0, le=1.0)
    secondary_emotions: Dict[EmotionType, float] = Field(default_factory=dict)
    voice_features: Dict[str, float] = Field(default_factory=dict)
    recommendations: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Analytics(BaseEntity):
    """Analytics data for dashboard"""
    device_id: str
    child_id: UUID
    total_interactions: int = Field(default=0, ge=0)
    daily_usage: Dict[str, int] = Field(default_factory=dict)
    emotion_distribution: Dict[EmotionType, int] = Field(default_factory=dict)
    learning_progress: Dict[str, float] = Field(default_factory=dict)
    favorite_topics: List[str] = Field(default_factory=list)
    average_session_duration_minutes: float = Field(default=0.0, ge=0.0)


class ParentNotification(BaseEntity):
    """Notification for parents"""
    device_id: str
    child_id: UUID
    type: Literal["emotion_alert", "milestone", "daily_summary", "system"] 
    title: str
    message: str
    priority: Literal["low", "medium", "high", "urgent"] = "medium"
    read: bool = False
    action_required: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)


# Request/Response models for API
class RegisterDeviceRequest(BaseModel):
    """Device registration request"""
    device_id: str
    firmware_version: str = "2.0.0"
    capabilities: List[str] = Field(default_factory=list)


class ProcessAudioRequest(BaseModel):
    """Audio processing request"""
    audio: str = Field(..., description="Base64 encoded audio")
    device_id: str
    session_id: Optional[str] = None
    format: Literal["mp3", "wav", "opus"] = "mp3"


class CreateChildProfileRequest(BaseModel):
    """Create child profile request"""
    name: str = Field(..., min_length=1, max_length=50)
    age: int = Field(..., ge=2, le=15)
    device_id: str
    language: Language = Language.ARABIC
    parent_email: Optional[str] = None
    special_needs: Optional[List[str]] = None


class DashboardData(BaseModel):
    """Dashboard data response"""
    total_devices: int
    active_devices: int
    total_children: int
    total_conversations: int
    recent_activity: List[Dict[str, Any]]
    emotion_summary: Dict[EmotionType, int]
    system_health: Dict[str, Any] 