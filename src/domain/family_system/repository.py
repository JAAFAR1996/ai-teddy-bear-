from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from .models import FamilyProfile, ScheduledMessage, TimeRestriction


class FamilyRepository(ABC):
    """Abstract interface for storing and retrieving family data."""

    @abstractmethod
    async def save_family_profile(self, profile: FamilyProfile) -> None:
        pass

    @abstractmethod
    async def get_family_profile(self, family_id: str) -> Optional[FamilyProfile]:
        pass

    @abstractmethod
    async def get_all_family_profiles(self) -> List[FamilyProfile]:
        pass

    @abstractmethod
    async def save_scheduled_message(self, message: ScheduledMessage) -> None:
        pass

    @abstractmethod
    async def get_scheduled_messages(self, family_id: str) -> List[ScheduledMessage]:
        pass

    @abstractmethod
    async def save_time_restriction(self, restriction: TimeRestriction) -> None:
        pass

    @abstractmethod
    async def get_time_restrictions(self, family_id: str) -> List[TimeRestriction]:
        pass
