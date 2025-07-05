"""Dependency Injection (DI) helper – 2025
Provides a very small, thread-safe singleton container so we can migrate تدريجيًا
بعيدًا عن المتغيّرات global. يجنّب الاعتماد على مكتبات خارجية بقدر الإمكان.
"""

from __future__ import annotations

import threading
from typing import Any, Callable, Dict, Type, TypeVar

T = TypeVar("T")

# Internal state (protected via `_lock`).
_instances: Dict[Type[Any], Any] = {}
_lock = threading.Lock()


def provide(cls: Type[T], factory: Callable[[], T]) -> T:  # noqa: D401
    """Return a *singleton* instance for *cls*.

    Args:
        cls: Key type to identify the singleton.
        factory: Zero-argument callable to build the instance lazily.

    Returns:
        Cached instance created by *factory* exactly once.
    """
    if cls in _instances:
        return _instances[cls]

    # Double-checked locking to guarantee thread safety without heavy locking.
    with _lock:
        if cls not in _instances:
            _instances[cls] = factory()
        return _instances[cls]


def clear() -> None:  # pragma: no cover
    """❎ *Testing only*: clear the container so tests remain isolated."""
    with _lock:
        _instances.clear() 