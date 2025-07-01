"""Core Use Cases"""

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict


class UseCase(ABC):
    @abstractmethod
    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        pass


@dataclass
class VoiceInteractionRequest:
    child_id: str
    audio_data: bytes
    language: str = "ar"


class VoiceInteractionUseCase(UseCase):
    async def execute(self, request: VoiceInteractionRequest) -> Dict[str, Any]:
        await asyncio.sleep(0.1)  # Mock processing
        return {
            "success": True,
            "transcribed_text": "مرحبا",
            "response_text": "مرحبا! كيف حالك؟",
            "safety_score": 0.95,
        }


@dataclass
class ChildRegistrationRequest:
    name: str
    age: int
    language: str = "ar"


class ChildRegistrationUseCase(UseCase):
    async def execute(self, request: ChildRegistrationRequest) -> Dict[str, Any]:
        import uuid

        await asyncio.sleep(0.1)  # Mock processing
        return {
            "success": True,
            "child_id": str(uuid.uuid4()),
            "message": f"تم تسجيل {request.name} بنجاح",
        }


class UseCaseFactory:
    @staticmethod
    def create_voice_interaction():
        return VoiceInteractionUseCase()

    @staticmethod
    def create_child_registration():
        return ChildRegistrationUseCase()
