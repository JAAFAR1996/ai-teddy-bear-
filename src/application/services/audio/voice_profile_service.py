"""
Voice Profile Management Application Service
Handles voice profile storage, loading and management
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

from elevenlabs import VoiceSettings

from src.domain.audio.models.voice_models import (EmotionalTone, Language,
                                                  VoiceProfile)


class VoiceProfileService:
    """Application service for voice profile management"""

    def __init__(self, storage_path: str = "data/voice_profiles", config=None):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self._profiles_cache: Dict[str, VoiceProfile] = {}

    async def save_profile(self, profile: VoiceProfile) -> bool:
        """Save voice profile to storage"""
        try:
            if not profile.is_valid():
                self.logger.error(f"Invalid voice profile: {profile.id}")
                return False

            # Serialize profile
            profile_data = self._serialize_profile(profile)

            # Save to file
            profile_file = self.storage_path / f"{profile.id}.json"
            with open(profile_file, "w", encoding="utf-8") as f:
                json.dump(profile_data, f, indent=2, ensure_ascii=False)

            # Update cache
            self._profiles_cache[profile.id] = profile

            self.logger.info(f"Saved voice profile: {profile.id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to save profile {profile.id}: {e}")
            return False

    async def load_profile(self, profile_id: str) -> Optional[VoiceProfile]:
        """Load voice profile from storage"""
        try:
            # Check cache first
            if profile_id in self._profiles_cache:
                return self._profiles_cache[profile_id]

            # Load from file
            profile_file = self.storage_path / f"{profile_id}.json"
            if not profile_file.exists():
                self.logger.warning(f"Profile file not found: {profile_id}")
                return None

            with open(profile_file, "r", encoding="utf-8") as f:
                profile_data = json.load(f)

            # Deserialize profile
            profile = self._deserialize_profile(profile_data)

            if profile and profile.is_valid():
                # Cache the profile
                self._profiles_cache[profile_id] = profile
                return profile
            else:
                self.logger.error(f"Invalid profile data: {profile_id}")
                return None

        except Exception as e:
            self.logger.error(f"Failed to load profile {profile_id}: {e}")
            return None

    async def get_all_profiles(self) -> List[VoiceProfile]:
        """Get all available voice profiles"""
        try:
            profiles = []

            # Load from files
            for profile_file in self.storage_path.glob("*.json"):
                profile_id = profile_file.stem
                profile = await self.load_profile(profile_id)
                if profile:
                    profiles.append(profile)

            return profiles

        except Exception as e:
            self.logger.error(f"Failed to get all profiles: {e}")
            return []

    async def delete_profile(self, profile_id: str) -> bool:
        """Delete voice profile"""
        try:
            # Remove from cache
            self._profiles_cache.pop(profile_id, None)

            # Remove file
            profile_file = self.storage_path / f"{profile_id}.json"
            if profile_file.exists():
                profile_file.unlink()
                self.logger.info(f"Deleted voice profile: {profile_id}")
                return True
            else:
                self.logger.warning(f"Profile file not found: {profile_id}")
                return False

        except Exception as e:
            self.logger.error(f"Failed to delete profile {profile_id}: {e}")
            return False

    async def create_default_profiles(self) -> Dict[str, VoiceProfile]:
        """Create and save default voice profiles"""
        try:
            profiles = {}

            # Default teddy bear profile (English)
            teddy_settings = self._create_emotional_settings()

            teddy_profile = VoiceProfile(
                id="teddy_bear",
                name="Friendly Teddy",
                voice_id=getattr(self.config, "DEFAULT_VOICE_ID", "josh"),
                language=Language.ENGLISH,
                emotional_settings=teddy_settings,
                pitch_adjustment=2.0,
                speed_adjustment=0.95,
                personality_prompt="You are a warm, friendly teddy bear who loves children.",
            )

            # Arabic teddy bear profile
            teddy_profile_ar = VoiceProfile(
                id="teddy_bear_ar",
                name="دبدوب الودود",
                voice_id=getattr(self.config, "ARABIC_VOICE_ID", "josh"),
                language=Language.ARABIC,
                emotional_settings=teddy_settings,
                pitch_adjustment=1.5,
                speed_adjustment=0.9,
                personality_prompt="أنت دبدوب ودود يحب الأطفال ويتحدث بلطف.",
            )

            # Save profiles
            profiles["teddy_bear"] = teddy_profile
            profiles["teddy_bear_ar"] = teddy_profile_ar

            for profile in profiles.values():
                await self.save_profile(profile)

            self.logger.info("Created default voice profiles")
            return profiles

        except Exception as e:
            self.logger.error(f"Failed to create default profiles: {e}")
            return {}

    def _create_emotional_settings(self) -> Dict[EmotionalTone, VoiceSettings]:
        """Create emotional voice settings"""
        return {
            EmotionalTone.HAPPY: VoiceSettings(
                stability=0.3, similarity_boost=0.7, style=0.4
            ),
            EmotionalTone.CALM: VoiceSettings(
                stability=0.5, similarity_boost=0.5, style=0.2
            ),
            EmotionalTone.CURIOUS: VoiceSettings(
                stability=0.4, similarity_boost=0.6, style=0.5
            ),
            EmotionalTone.SUPPORTIVE: VoiceSettings(
                stability=0.6, similarity_boost=0.4, style=0.3
            ),
            EmotionalTone.PLAYFUL: VoiceSettings(
                stability=0.2, similarity_boost=0.8, style=0.6
            ),
            EmotionalTone.SLEEPY: VoiceSettings(
                stability=0.7, similarity_boost=0.3, style=0.1
            ),
            EmotionalTone.EXCITED: VoiceSettings(
                stability=0.1, similarity_boost=0.9, style=0.8
            ),
            EmotionalTone.STORYTELLING: VoiceSettings(
                stability=0.4, similarity_boost=0.5, style=0.4
            ),
            EmotionalTone.EDUCATIONAL: VoiceSettings(
                stability=0.6, similarity_boost=0.5, style=0.3
            ),
            EmotionalTone.COMFORTING: VoiceSettings(
                stability=0.7, similarity_boost=0.4, style=0.2
            ),
        }

    def _serialize_profile(self, profile: VoiceProfile) -> Dict:
        """Serialize voice profile to dictionary"""
        return {
            "id": profile.id,
            "name": profile.name,
            "voice_id": profile.voice_id,
            "language": profile.language.value,
            "pitch_adjustment": profile.pitch_adjustment,
            "speed_adjustment": profile.speed_adjustment,
            "personality_prompt": profile.personality_prompt,
            "emotional_settings": {
                emotion.value: {
                    "stability": settings.stability,
                    "similarity_boost": settings.similarity_boost,
                    "style": settings.style,
                }
                for emotion, settings in profile.emotional_settings.items()
            },
        }

    def _deserialize_profile(self, data: Dict) -> Optional[VoiceProfile]:
        """Deserialize voice profile from dictionary"""
        try:
            # Reconstruct emotional settings
            emotional_settings = {}
            for emotion_str, settings_data in data.get(
                "emotional_settings", {}
            ).items():
                emotion = EmotionalTone(emotion_str)
                settings = VoiceSettings(
                    stability=settings_data["stability"],
                    similarity_boost=settings_data["similarity_boost"],
                    style=settings_data["style"],
                )
                emotional_settings[emotion] = settings

            # Create profile
            profile = VoiceProfile(
                id=data["id"],
                name=data["name"],
                voice_id=data["voice_id"],
                language=Language(data["language"]),
                emotional_settings=emotional_settings,
                pitch_adjustment=data.get("pitch_adjustment", 0.0),
                speed_adjustment=data.get("speed_adjustment", 1.0),
                personality_prompt=data.get("personality_prompt", ""),
            )

            return profile

        except Exception as e:
            self.logger.error(f"Profile deserialization error: {e}")
            return None
