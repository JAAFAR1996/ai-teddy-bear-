# child.py - Enhanced child entity with complete features

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime, date
from enum import Enum
import re
import uuid


class Language(Enum):
    """Supported languages"""
    ENGLISH = "en"
    ARABIC = "ar"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    CHINESE = "zh"
    JAPANESE = "ja"
    KOREAN = "ko"


class VoiceType(Enum):
    """Voice type preferences"""
    CHEERFUL = "cheerful"
    CALM = "calm"
    ENERGETIC = "energetic"
    GENTLE = "gentle"
    PLAYFUL = "playful"


class InteractionStyle(Enum):
    """Interaction style preferences"""
    EDUCATIONAL = "educational"
    PLAYFUL = "playful"
    STORYTELLING = "storytelling"
    CONVERSATIONAL = "conversational"
    MIXED = "mixed"


class LearningLevel(Enum):
    """Learning level categories"""
    PRESCHOOL = "preschool"         # Ages 3-5
    EARLY_ELEMENTARY = "early_elementary"  # Ages 6-7
    ELEMENTARY = "elementary"       # Ages 8-10
    MIDDLE_SCHOOL = "middle_school" # Ages 11-13
    HIGH_SCHOOL = "high_school"     # Ages 14+


class EmotionalSensitivity(Enum):
    """Emotional sensitivity levels"""
    HIGH = "high"       # Very gentle, lots of support
    MODERATE = "moderate"  # Balanced approach
    LOW = "low"         # More direct communication


class ChildPreferences(BaseModel):
    """Child's interaction preferences"""
    
    language: Language = Field(
        default=Language.ENGLISH,
        description="Preferred language"
    )
    
    voice_type: VoiceType = Field(
        default=VoiceType.CHEERFUL,
        description="Preferred voice type"
    )
    
    interaction_style: InteractionStyle = Field(
        default=InteractionStyle.MIXED,
        description="Preferred interaction style"
    )
    
    emotional_sensitivity: EmotionalSensitivity = Field(
        default=EmotionalSensitivity.MODERATE,
        description="Emotional sensitivity level"
    )
    
    favorite_characters: List[str] = Field(
        default_factory=list,
        description="Favorite story characters"
    )
    
    favorite_colors: List[str] = Field(
        default_factory=list,
        description="Favorite colors for visual elements"
    )
    
    learning_interests: List[str] = Field(
        default_factory=lambda: ["science", "math", "reading", "art"],
        description="Specific learning interests"
    )
    
    bedtime_story_themes: List[str] = Field(
        default_factory=lambda: ["adventure", "animals", "space", "fairy_tales"],
        description="Preferred bedtime story themes"
    )
    
    wake_words: List[str] = Field(
        default_factory=lambda: ["hey teddy", "hello teddy"],
        description="Custom wake words"
    )
    
    volume_level: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Preferred volume level"
    )
    
    response_speed: float = Field(
        default=1.0,
        ge=0.5,
        le=1.5,
        description="Speech speed multiplier"
    )


class DevelopmentMilestone(BaseModel):
    """Represents a developmental milestone"""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., description="Milestone name")
    category: str = Field(..., description="Category (cognitive, social, etc)")
    achieved_at: datetime = Field(default_factory=datetime.now)
    description: str = Field(..., description="Milestone description")
    
    
class SafetySettings(BaseModel):
    """Safety and privacy settings"""
    
    block_personal_questions: bool = Field(
        default=True,
        description="Block questions about personal information"
    )
    
    require_parent_approval: bool = Field(
        default=False,
        description="Require parent approval for certain actions"
    )
    
    allowed_external_content: bool = Field(
        default=False,
        description="Allow access to external educational content"
    )
    
    emergency_contacts: List[str] = Field(
        default_factory=list,
        description="Emergency contact information"
    )
    
    restricted_words: List[str] = Field(
        default_factory=list,
        description="Additional restricted words"
    )


class Child(BaseModel):
    """
    Enhanced child profile for the AI Teddy Bear system
    """
    
    # Basic Information
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier"
    )
    
    name: str = Field(
        ...,
        description="Child's name",
        min_length=2,
        max_length=50
    )
    
    age: int = Field(
        ...,
        gt=0,
        lt=18,
        description="Child's age"
    )
    
    date_of_birth: Optional[date] = Field(
        None,
        description="Child's date of birth"
    )
    
    gender: Optional[str] = Field(
        None,
        description="Child's gender (optional)"
    )
    
    # Interests and Preferences
    interests: List[str] = Field(
        default_factory=list,
        description="Child's interests"
    )
    
    preferences: ChildPreferences = Field(
        default_factory=ChildPreferences,
        description="Interaction preferences"
    )
    
    # Educational Information
    learning_level: LearningLevel = Field(
        default=LearningLevel.ELEMENTARY,
        description="Current learning level"
    )
    
    known_concepts: List[str] = Field(
        default_factory=list,
        description="Concepts the child has learned"
    )
    
    learning_goals: List[str] = Field(
        default_factory=list,
        description="Current learning goals"
    )
    
    milestones: List[DevelopmentMilestone] = Field(
        default_factory=list,
        description="Achieved developmental milestones"
    )
    
    # Interaction Settings
    max_daily_interaction_time: int = Field(
        default=3600,  # 1 hour default
        ge=0,
        description="Maximum daily interaction time in seconds"
    )
    
    allowed_topics: List[str] = Field(
        default_factory=lambda: [
            'education', 'games', 'science', 'art',
            'nature', 'animals', 'history', 'music',
            'stories', 'math', 'creativity', 'friendship'
        ],
        description="List of allowed conversation topics"
    )
    
    blocked_topics: List[str] = Field(
        default_factory=lambda: [
            'violence', 'scary_content', 'adult_themes'
        ],
        description="List of blocked conversation topics"
    )
    
    # Safety Settings
    safety_settings: SafetySettings = Field(
        default_factory=SafetySettings,
        description="Safety and privacy settings"
    )
    
    # Usage Statistics
    total_interaction_time: int = Field(
        default=0,
        description="Total interaction time in seconds"
    )
    
    total_sessions: int = Field(
        default=0,
        description="Total number of sessions"
    )
    
    favorite_activities: Dict[str, int] = Field(
        default_factory=dict,
        description="Favorite activities and their frequency"
    )
    
    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Profile creation timestamp"
    )
    
    last_interaction: Optional[datetime] = Field(
        None,
        description="Timestamp of last interaction"
    )
    
    updated_at: datetime = Field(
        default_factory=datetime.now,
        description="Last update timestamp"
    )
    
    # Parent Information
    parent_id: Optional[str] = Field(
        None,
        description="Parent account ID"
    )
    
    parent_email: Optional[str] = Field(
        None,
        description="Parent email for notifications"
    )
    
    # Validators
    
    @validator('interests')
    def validate_interests(cls, interests):
        """Validate child's interests"""
        if len(interests) > 10:
            raise ValueError("Maximum of 10 interests allowed")
        
        # Sanitize and normalize interests
        validated = []
        for interest in interests:
            if interest and isinstance(interest, str):
                clean_interest = interest.lower().strip()
                if clean_interest and len(clean_interest) <= 50:
                    validated.append(clean_interest)
                    
        return validated
    
    @validator('name')
    def validate_name(cls, name):
        """Validate child's name"""
        # Remove any potential HTML or script tags
        name = re.sub(r'<[^>]+>', '', name)
        
        # Allow letters, spaces, and common name characters
        if not re.match(r'^[A-Za-z\s\'\-\.]+$', name):
            raise ValueError("Name contains invalid characters")
        
        return name.strip()
    
    @validator('learning_level')
    def validate_learning_level(cls, level, values):
        """Ensure learning level matches age"""
        age = values.get('age')
        if age:
            if age < 5 and level != LearningLevel.PRESCHOOL:
                return LearningLevel.PRESCHOOL
            elif 5 <= age < 8 and level not in [LearningLevel.PRESCHOOL, LearningLevel.EARLY_ELEMENTARY]:
                return LearningLevel.EARLY_ELEMENTARY
            elif 8 <= age < 11 and level not in [LearningLevel.ELEMENTARY]:
                return LearningLevel.ELEMENTARY
            elif 11 <= age < 14 and level not in [LearningLevel.MIDDLE_SCHOOL]:
                return LearningLevel.MIDDLE_SCHOOL
            elif age >= 14 and level not in [LearningLevel.HIGH_SCHOOL]:
                return LearningLevel.HIGH_SCHOOL
        return level
    
    @validator('parent_email')
    def validate_email(cls, email):
        """Validate parent email"""
        if email:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                raise ValueError("Invalid email format")
        return email
    
    # Methods
    
    def update_last_interaction(self):
        """Update the last interaction timestamp"""
        self.last_interaction = datetime.now()
        self.updated_at = datetime.now()
    
    def is_interaction_allowed(self, topic: str) -> bool:
        """Check if a conversation topic is allowed"""
        topic_lower = topic.lower()
        
        # Check if explicitly blocked
        if any(blocked in topic_lower for blocked in self.blocked_topics):
            return False
            
        # Check if in allowed topics
        return any(allowed in topic_lower for allowed in self.allowed_topics)
    
    def add_milestone(self, name: str, category: str, description: str):
        """Add a developmental milestone"""
        milestone = DevelopmentMilestone(
            name=name,
            category=category,
            description=description
        )
        self.milestones.append(milestone)
        self.updated_at = datetime.now()
    
    def update_learning_progress(self, concept: str):
        """Update learning progress"""
        if concept not in self.known_concepts:
            self.known_concepts.append(concept)
            self.updated_at = datetime.now()
    
    def track_activity(self, activity: str):
        """Track favorite activities"""
        if activity not in self.favorite_activities:
            self.favorite_activities[activity] = 0
        self.favorite_activities[activity] += 1
        self.updated_at = datetime.now()
    
    def get_age_appropriate_content(self) -> Dict[str, Any]:
        """Get age-appropriate content settings"""
        return {
            'max_session_duration': min(30 * 60, self.max_daily_interaction_time),  # 30 min max per session
            'complexity_level': self.learning_level.value,
            'content_filters': {
                'violence': self.age < 10,
                'scary_content': self.age < 8,
                'complex_topics': self.age < 12
            },
            'recommended_activities': self._get_recommended_activities()
        }
    
    def _get_recommended_activities(self) -> List[str]:
        """Get age-appropriate recommended activities"""
        activities = {
            LearningLevel.PRESCHOOL: [
                "counting_games", "color_recognition", "animal_sounds",
                "simple_stories", "nursery_rhymes"
            ],
            LearningLevel.EARLY_ELEMENTARY: [
                "basic_math", "word_games", "simple_science",
                "creative_stories", "music_exploration"
            ],
            LearningLevel.ELEMENTARY: [
                "math_puzzles", "science_experiments", "geography_games",
                "creative_writing", "coding_basics"
            ],
            LearningLevel.MIDDLE_SCHOOL: [
                "advanced_math", "science_projects", "history_exploration",
                "debate_topics", "programming"
            ],
            LearningLevel.HIGH_SCHOOL: [
                "complex_problems", "research_topics", "career_exploration",
                "advanced_coding", "philosophy"
            ]
        }
        
        return activities.get(self.learning_level, [])
    
    def calculate_age(self) -> int:
        """Calculate current age from date of birth"""
        if self.date_of_birth:
            today = date.today()
            age = today.year - self.date_of_birth.year
            
            # Adjust if birthday hasn't occurred this year
            if (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day):
                age -= 1
                
            # Update age field
            self.age = age
            
        return self.age
    
    def to_dict(self) -> dict:
        """Convert child profile to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'gender': self.gender,
            'interests': self.interests,
            'preferences': self.preferences.dict(),
            'learning_level': self.learning_level.value,
            'known_concepts': self.known_concepts,
            'learning_goals': self.learning_goals,
            'milestones': [m.dict() for m in self.milestones],
            'max_daily_interaction_time': self.max_daily_interaction_time,
            'allowed_topics': self.allowed_topics,
            'blocked_topics': self.blocked_topics,
            'safety_settings': self.safety_settings.dict(),
            'total_interaction_time': self.total_interaction_time,
            'total_sessions': self.total_sessions,
            'favorite_activities': self.favorite_activities,
            'created_at': self.created_at.isoformat(),
            'last_interaction': self.last_interaction.isoformat() if self.last_interaction else None,
            'updated_at': self.updated_at.isoformat(),
            'parent_id': self.parent_id,
            'parent_email': self.parent_email
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Child':
        """Create Child instance from dictionary"""
        # Parse dates
        if 'date_of_birth' in data and data['date_of_birth']:
            data['date_of_birth'] = date.fromisoformat(data['date_of_birth'])
            
        if 'created_at' in data:
            data['created_at'] = datetime.fromisoformat(data['created_at'])
            
        if 'last_interaction' in data and data['last_interaction']:
            data['last_interaction'] = datetime.fromisoformat(data['last_interaction'])
            
        if 'updated_at' in data:
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
            
        # Parse nested objects
        if 'preferences' in data and isinstance(data['preferences'], dict):
            data['preferences'] = ChildPreferences(**data['preferences'])
            
        if 'safety_settings' in data and isinstance(data['safety_settings'], dict):
            data['safety_settings'] = SafetySettings(**data['safety_settings'])
            
        if 'milestones' in data:
            data['milestones'] = [
                DevelopmentMilestone(**m) if isinstance(m, dict) else m
                for m in data['milestones']
            ]
            
        return cls(**data)
    
    class Config:
        """Pydantic configuration"""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }