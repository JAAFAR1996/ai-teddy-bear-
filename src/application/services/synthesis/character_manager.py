#!/usr/bin/env python3
"""
🎭 Voice Character Management Service
خدمة إدارة شخصيات الصوت
"""

import logging
from typing import Any, Dict, List, Optional

from .models import VoiceCharacter, VoiceProvider, SynthesisConfig, VoiceSettings
from src.domain.value_objects.value_objects import EmotionalTone

logger = logging.getLogger(__name__)


class VoiceCharacterManager:
    """Manager for voice characters with emotional settings"""

    def __init__(self, config: SynthesisConfig):
        """Initialize the character manager"""
        self.config = config
        self.voice_characters: Dict[str, VoiceCharacter] = {}
        self.current_character: Optional[VoiceCharacter] = None

        logger.debug("Voice character manager initialized")

    async def load_default_characters(self) -> None:
        """Load default voice characters"""
        try:
            # Create emotional settings for teddy bear characters
            teddy_emotional_settings = self._create_teddy_emotional_settings()

            # English Teddy Character
            self.voice_characters["teddy_en"] = VoiceCharacter(
                id="teddy_en",
                name="Friendly Teddy (English)",
                provider=VoiceProvider.ELEVENLABS,
                voice_id="josh",  # Default ElevenLabs voice
                language="en",
                description="Warm, friendly teddy bear voice for children",
                emotional_settings=teddy_emotional_settings,
                pitch_adjustment=2.0,  # Higher pitch for child-friendly voice
                speed_adjustment=0.95,  # Slightly slower for clarity
                volume_adjustment=1.0
            )

            # Arabic Teddy Character
            self.voice_characters["teddy_ar"] = VoiceCharacter(
                id="teddy_ar",
                name="دبدوب الودود (Arabic)",
                provider=VoiceProvider.AZURE,  # Better Arabic support
                voice_id="ar-SA-ZariyahNeural",
                language="ar",
                description="صوت دبدوب ودود للأطفال باللغة العربية",
                emotional_settings=teddy_emotional_settings,
                pitch_adjustment=1.5,
                speed_adjustment=0.9,
                volume_adjustment=1.0
            )

            # Set default character
            self.current_character = self.voice_characters["teddy_en"]

            logger.info(
                f"✅ Loaded {len(self.voice_characters)} voice characters")

        except Exception as e:
            logger.error(f"❌ Failed to load default characters: {e}")
            raise

    def _create_teddy_emotional_settings(self) -> Dict[EmotionalTone, VoiceSettings]:
        """Create emotional voice settings for teddy bear characters"""
        return {
            EmotionalTone.HAPPY: VoiceSettings(
                stability=0.3,
                similarity_boost=0.7,
                style=0.4
            ),
            EmotionalTone.CALM: VoiceSettings(
                stability=0.6,
                similarity_boost=0.5,
                style=0.2
            ),
            EmotionalTone.EXCITED: VoiceSettings(
                stability=0.2,
                similarity_boost=0.8,
                style=0.7
            ),
            EmotionalTone.CURIOUS: VoiceSettings(
                stability=0.4,
                similarity_boost=0.6,
                style=0.5
            ),
            EmotionalTone.LOVE: VoiceSettings(
                stability=0.7,
                similarity_boost=0.4,
                style=0.3
            ),
            EmotionalTone.ENCOURAGING: VoiceSettings(
                stability=0.5,
                similarity_boost=0.6,
                style=0.4
            ),
            EmotionalTone.FRIENDLY: VoiceSettings(
                stability=0.4,
                similarity_boost=0.7,
                style=0.5
            )
        }

    async def select_character(
        self,
        character_id: Optional[str],
        language: Optional[str]
    ) -> VoiceCharacter:
        """Select appropriate voice character"""
        if character_id and character_id in self.voice_characters:
            logger.debug(f"Selected character by ID: {character_id}")
            return self.voice_characters[character_id]

        # Auto-select based on language
        if language:
            for character in self.voice_characters.values():
                if character.language == language:
                    logger.debug(
                        f"Selected character by language: {character.id}")
                    return character

        # Return current or default character
        default_character = self.current_character or self.voice_characters.get(
            "teddy_en")
        if default_character:
            logger.debug(f"Using default character: {default_character.id}")
            return default_character

        # Last resort - create a basic character
        return self._create_fallback_character()

    def _create_fallback_character(self) -> VoiceCharacter:
        """Create a basic fallback character"""
        basic_settings = {
            EmotionalTone.FRIENDLY: VoiceSettings(
                stability=0.5, similarity_boost=0.5, style=0.5)
        }

        return VoiceCharacter(
            id="fallback",
            name="Basic Voice",
            provider=VoiceProvider.SYSTEM,
            voice_id="default",
            language="en",
            description="Basic fallback voice",
            emotional_settings=basic_settings
        )

    def set_current_character(self, character_id: str) -> bool:
        """Set current voice character"""
        if character_id in self.voice_characters:
            self.current_character = self.voice_characters[character_id]
            logger.info(
                f"🎭 Voice character set to: {self.current_character.name}")
            return True
        else:
            logger.warning(f"Character ID not found: {character_id}")
            return False

    def get_current_character(self) -> Optional[VoiceCharacter]:
        """Get current voice character"""
        return self.current_character

    def get_available_characters(self) -> List[Dict[str, Any]]:
        """Get list of available voice characters"""
        return [
            {
                "id": char.id,
                "name": char.name,
                "language": char.language,
                "provider": char.provider.value,
                "description": char.description
            }
            for char in self.voice_characters.values()
        ]

    def add_character(self, character: VoiceCharacter) -> bool:
        """Add a new voice character"""
        try:
            self.voice_characters[character.id] = character
            logger.info(f"✅ Added voice character: {character.name}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to add character: {e}")
            return False

    def remove_character(self, character_id: str) -> bool:
        """Remove a voice character"""
        if character_id in self.voice_characters:
            if self.current_character and self.current_character.id == character_id:
                # Reset to default if removing current character
                self.current_character = self.voice_characters.get("teddy_en")

            del self.voice_characters[character_id]
            logger.info(f"🗑️ Removed voice character: {character_id}")
            return True
        else:
            logger.warning(
                f"Character ID not found for removal: {character_id}")
            return False

    def get_character_by_language(self, language: str) -> Optional[VoiceCharacter]:
        """Get first character matching the language"""
        for character in self.voice_characters.values():
            if character.language == language:
                return character
        return None

    def get_characters_by_provider(self, provider: VoiceProvider) -> List[VoiceCharacter]:
        """Get all characters for a specific provider"""
        return [
            char for char in self.voice_characters.values()
            if char.provider == provider
        ]

    def get_character_stats(self) -> Dict[str, Any]:
        """Get statistics about loaded characters"""
        provider_counts = {}
        language_counts = {}

        for character in self.voice_characters.values():
            # Count by provider
            provider = character.provider.value
            provider_counts[provider] = provider_counts.get(provider, 0) + 1

            # Count by language
            language = character.language
            language_counts[language] = language_counts.get(language, 0) + 1

        return {
            "total_characters": len(self.voice_characters),
            "current_character": self.current_character.id if self.current_character else None,
            "provider_distribution": provider_counts,
            "language_distribution": language_counts,
            "available_character_ids": list(self.voice_characters.keys())
        }
