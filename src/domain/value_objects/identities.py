"""
🆔 Identity Value Objects
========================

Strong-typed identifiers for domain entities following DDD principles.
These provide type safety and prevent mixing up different types of IDs.
"""

from dataclasses import dataclass
from typing import Union
from uuid import UUID, uuid4


@dataclass(frozen=True)
class ChildId:
    """Strongly-typed Child identifier"""

    value: UUID

    def __init__(self, value: Union[str, UUID]):
        if isinstance(value, str):
            object.__setattr__(self, "value", UUID(value))
        elif isinstance(value, UUID):
            object.__setattr__(self, "value", value)
        else:
            raise TypeError("ChildId must be created from str or UUID")

    def __str__(self) -> str:
        return str(self.value)

    @classmethod
    def generate(cls) -> "ChildId":
        """Generate a new random ChildId"""
        return cls(uuid4())


@dataclass(frozen=True)
class ParentId:
    """Strongly-typed Parent identifier"""

    value: UUID

    def __init__(self, value: Union[str, UUID]):
        if isinstance(value, str):
            object.__setattr__(self, "value", UUID(value))
        elif isinstance(value, UUID):
            object.__setattr__(self, "value", value)
        else:
            raise TypeError("ParentId must be created from str or UUID")

    def __str__(self) -> str:
        return str(self.value)

    @classmethod
    def generate(cls) -> "ParentId":
        """Generate a new random ParentId"""
        return cls(uuid4())


@dataclass(frozen=True)
class ConversationId:
    """Strongly-typed Conversation identifier"""

    value: UUID

    def __init__(self, value: Union[str, UUID]):
        if isinstance(value, str):
            object.__setattr__(self, "value", UUID(value))
        elif isinstance(value, UUID):
            object.__setattr__(self, "value", value)
        else:
            raise TypeError("ConversationId must be created from str or UUID")

    def __str__(self) -> str:
        return str(self.value)

    @classmethod
    def generate(cls) -> "ConversationId":
        """Generate a new random ConversationId"""
        return cls(uuid4())


@dataclass(frozen=True)
class AudioSessionId:
    """Strongly-typed Audio Session identifier"""

    value: UUID

    def __init__(self, value: Union[str, UUID]):
        if isinstance(value, str):
            object.__setattr__(self, "value", UUID(value))
        elif isinstance(value, UUID):
            object.__setattr__(self, "value", value)
        else:
            raise TypeError("AudioSessionId must be created from str or UUID")

    def __str__(self) -> str:
        return str(self.value)

    @classmethod
    def generate(cls) -> "AudioSessionId":
        """Generate a new random AudioSessionId"""
        return cls(uuid4())


@dataclass(frozen=True)
class MessageId:
    """Strongly-typed Message identifier"""

    value: UUID

    def __init__(self, value: Union[str, UUID]):
        if isinstance(value, str):
            object.__setattr__(self, "value", UUID(value))
        elif isinstance(value, UUID):
            object.__setattr__(self, "value", value)
        else:
            raise TypeError("MessageId must be created from str or UUID")

    def __str__(self) -> str:
        return str(self.value)

    @classmethod
    def generate(cls) -> "MessageId":
        """Generate a new random MessageId"""
        return cls(uuid4())
