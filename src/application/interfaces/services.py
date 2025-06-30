from abc import ABC, abstractmethod

class IAIService(ABC):
    @abstractmethod
    async def generate_response(self, message: str, context: dict) -> str:
        pass 