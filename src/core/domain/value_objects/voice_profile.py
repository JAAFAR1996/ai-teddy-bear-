"""
🎙️ Voice Profile Value Object
============================

Voice profile represents the unique vocal characteristics and preferences
for a child's interaction with the AI Teddy Bear.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from enum import Enum


class VoiceGender(Enum):
    """Voice gender options"""
    MALE = "male"
    FEMALE = "female"
    NEUTRAL = "neutral"


class EmotionBaseline(Enum):
    """Baseline emotional tone options"""
    CHEERFUL = "cheerful"
    CALM = "calm"
    ENERGETIC = "energetic"
    GENTLE = "gentle"
    PLAYFUL = "playful"


@dataclass(frozen=True)
class VoiceProfile:
    """
    Value Object representing child's voice interaction preferences.
    
    This encapsulates all voice-related settings and characteristics
    that affect how the AI responds to and interacts with the child.
    """
    
    # Voice characteristics
    pitch: float  # Range: 0.5-2.0 (normal = 1.0)
    speed: float  # Range: 0.5-2.0 (normal = 1.0)
    volume: float  # Range: 0.1-1.0
    
    # Emotional settings
    emotion_baseline: EmotionBaseline
    emotion_sensitivity: float  # Range: 0.1-1.0
    
    # Voice identity
    voice_gender: VoiceGender
    language_accent: str  # e.g., "en-US", "en-GB"
    
    # Advanced settings
    response_style: str  # "educational", "playful", "storytelling"
    complexity_level: int  # 1-5 based on child's age/comprehension
    
    # Metadata
    voice_model_version: str
    last_calibrated: Optional[str] = None

    def __post_init__(self):
        """Validate voice profile parameters"""
        if not 0.5 <= self.pitch <= 2.0:
            raise ValueError("Pitch must be between 0.5 and 2.0")
        
        if not 0.5 <= self.speed <= 2.0:
            raise ValueError("Speed must be between 0.5 and 2.0")
        
        if not 0.1 <= self.volume <= 1.0:
            raise ValueError("Volume must be between 0.1 and 1.0")
        
        if not 0.1 <= self.emotion_sensitivity <= 1.0:
            raise ValueError("Emotion sensitivity must be between 0.1 and 1.0")
        
        if not 1 <= self.complexity_level <= 5:
            raise ValueError("Complexity level must be between 1 and 5")

    @classmethod
    def create_default(cls, child_age: int, language: str = "en-US") -> 'VoiceProfile':
        """Create default voice profile based on child's age"""
        
        # Age-appropriate complexity mapping
        complexity_map = {
            (3, 4): 1,   # Simple words, short sentences
            (5, 6): 2,   # Basic vocabulary expansion
            (7, 8): 3,   # More complex concepts
            (9, 10): 4,  # Advanced vocabulary
            (11, 12): 5  # Full complexity
        }
        
        complexity = 3  # Default
        for age_range, level in complexity_map.items():
            if age_range[0] <= child_age <= age_range[1]:
                complexity = level
                break
        
        return cls(
            pitch=1.0,
            speed=0.9,  # Slightly slower for children
            volume=0.8,
            emotion_baseline=EmotionBaseline.CHEERFUL,
            emotion_sensitivity=0.7,
            voice_gender=VoiceGender.NEUTRAL,
            language_accent=language,
            response_style="playful",
            complexity_level=complexity,
            voice_model_version="v2025.1",
            last_calibrated=None
        )

    @classmethod
    def create_custom(
        cls,
        pitch: float = 1.0,
        speed: float = 1.0,
        volume: float = 0.8,
        emotion_baseline: EmotionBaseline = EmotionBaseline.CHEERFUL,
        emotion_sensitivity: float = 0.7,
        voice_gender: VoiceGender = VoiceGender.NEUTRAL,
        language_accent: str = "en-US",
        response_style: str = "playful",
        complexity_level: int = 3
    ) -> 'VoiceProfile':
        """Create custom voice profile with specified parameters"""
        
        return cls(
            pitch=pitch,
            speed=speed,
            volume=volume,
            emotion_baseline=emotion_baseline,
            emotion_sensitivity=emotion_sensitivity,
            voice_gender=voice_gender,
            language_accent=language_accent,
            response_style=response_style,
            complexity_level=complexity_level,
            voice_model_version="v2025.1",
            last_calibrated=None
        )

    def adjust_for_emotion(self, detected_emotion: str, intensity: float) -> 'VoiceProfile':
        """Create adjusted voice profile based on detected emotion"""
        
        emotion_adjustments = {
            "happy": {"pitch": 0.1, "speed": 0.1},
            "sad": {"pitch": -0.2, "speed": -0.2},
            "excited": {"pitch": 0.2, "speed": 0.2},
            "tired": {"pitch": -0.1, "speed": -0.3},
            "frustrated": {"pitch": -0.1, "speed": -0.1},
            "calm": {"pitch": 0.0, "speed": -0.1}
        }
        
        adjustment = emotion_adjustments.get(detected_emotion, {"pitch": 0, "speed": 0})
        adjusted_intensity = intensity * self.emotion_sensitivity
        
        new_pitch = max(0.5, min(2.0, 
            self.pitch + (adjustment["pitch"] * adjusted_intensity)))
        new_speed = max(0.5, min(2.0, 
            self.speed + (adjustment["speed"] * adjusted_intensity)))
        
        return self.__class__(
            pitch=new_pitch,
            speed=new_speed,
            volume=self.volume,
            emotion_baseline=self.emotion_baseline,
            emotion_sensitivity=self.emotion_sensitivity,
            voice_gender=self.voice_gender,
            language_accent=self.language_accent,
            response_style=self.response_style,
            complexity_level=self.complexity_level,
            voice_model_version=self.voice_model_version,
            last_calibrated=self.last_calibrated
        )

    def to_synthesis_params(self) -> Dict[str, Any]:
        """Convert voice profile to parameters for speech synthesis"""
        
        return {
            "pitch": self.pitch,
            "speed": self.speed,
            "volume": self.volume,
            "voice_id": f"{self.voice_gender.value}_{self.language_accent}",
            "emotion_baseline": self.emotion_baseline.value,
            "stability": 0.8,  # Voice consistency
            "similarity_boost": 0.7,  # Voice similarity to baseline
            "style": self.response_style,
            "use_speaker_boost": True
        }

    def is_age_appropriate(self, child_age: int) -> bool:
        """Check if voice profile settings are appropriate for child's age"""
        
        age_complexity_map = {
            (3, 4): 1,
            (5, 6): 2,
            (7, 8): 3,
            (9, 10): 4,
            (11, 12): 5
        }
        
        for age_range, expected_complexity in age_complexity_map.items():
            if age_range[0] <= child_age <= age_range[1]:
                return abs(self.complexity_level - expected_complexity) <= 1
        
        return True  # Default to allowing if age not in range

    def __str__(self) -> str:
        return (f"VoiceProfile(pitch={self.pitch}, speed={self.speed}, "
                f"emotion={self.emotion_baseline.value}, "
                f"complexity={self.complexity_level})")

    def __repr__(self) -> str:
        return (f"VoiceProfile(pitch={self.pitch}, speed={self.speed}, "
                f"volume={self.volume}, emotion_baseline={self.emotion_baseline}, "
                f"voice_gender={self.voice_gender}, language={self.language_accent})") 