"""
Base interface for all secret providers.
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from ..models import SecretMetadata, SecretValue


class ISecretsProvider(ABC):
    """Interface for secret providers"""

    @abstractmethod
    async def get_secret(
        self, name: str, version: Optional[str] = None
    ) -> Optional[SecretValue]:
        """Retrieve a secret"""
        pass

    @abstractmethod
    async def set_secret(
            self,
            name: str,
            value: str,
            metadata: SecretMetadata) -> bool:
        """Store a secret"""
        pass

    @abstractmethod
    async def delete_secret(self, name: str) -> bool:
        """Delete a secret"""
        pass

    @abstractmethod
    async def rotate_secret(self, name: str, new_value: str) -> bool:
        """Rotate a secret"""
        pass

    @abstractmethod
    async def list_secrets(self) -> List[SecretMetadata]:
        """List all secrets"""
        pass
