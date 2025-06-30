from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any

class IChildRepository(ABC):
    @abstractmethod
    async def get(self, child_id: str) -> Optional[Any]:
        pass
    
    @abstractmethod
    async def save(self, child: Any) -> None:
        pass
    
    @abstractmethod
    async def find_by_parent(self, parent_id: str) -> List[Any]:
        pass

class IConversationRepository(ABC):
    @abstractmethod
    async def save_message(self, session_id: str, message: Dict[str, Any]) -> None:
        pass
    
    @abstractmethod
    async def get_conversation(self, session_id: str) -> List[Dict[str, Any]]:
        pass 