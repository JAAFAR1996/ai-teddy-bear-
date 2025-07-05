"""
Application State Manager
Clean state management system to replace global variables with context managers and thread-safe patterns
"""

import asyncio
import logging
import threading
import weakref
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Type, TypeVar, Union

import redis.asyncio as redis
from pydantic import BaseModel, Field
from typing_extensions import Protocol

logger = logging.getLogger(__name__)

T = TypeVar('T')


class StateScope(Enum):
    """State scope enumeration"""
    REQUEST = "request"
    SESSION = "session"
    APPLICATION = "application"
    GLOBAL = "global"


class StateEventType(Enum):
    """State event types"""
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    EXPIRED = "expired"


@dataclass
class StateMetadata:
    """State metadata"""
    key: str
    scope: StateScope
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime] = None
    tags: Set[str] = field(default_factory=set)
    version: int = 1
    checksum: Optional[str] = None


class StateEvent(BaseModel):
    """State change event"""
    event_type: StateEventType
    key: str
    scope: StateScope
    timestamp: datetime
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
    metadata: StateMetadata


class IStateStore(ABC):
    """State store interface"""
    
    @abstractmethod
    async def get(self, key: str, scope: StateScope) -> Optional[Any]:
        """Get state value"""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, scope: StateScope, **kwargs) -> None:
        """Set state value"""
        pass
    
    @abstractmethod
    async def delete(self, key: str, scope: StateScope) -> None:
        """Delete state value"""
        pass
    
    @abstractmethod
    async def exists(self, key: str, scope: StateScope) -> bool:
        """Check if key exists"""
        pass
    
    @abstractmethod
    async def clear_scope(self, scope: StateScope) -> None:
        """Clear all values in scope"""
        pass


class IStateObserver(ABC):
    """State observer interface"""
    
    @abstractmethod
    async def on_state_changed(self, event: StateEvent) -> None:
        """Handle state change event"""
        pass


class ThreadSafeStateStore(IStateStore):
    """Thread-safe in-memory state store"""
    
    def __init__(self):
        self.storage: Dict[StateScope, Dict[str, Any]] = {
            scope: {} for scope in StateScope
        }
        self.metadata: Dict[StateScope, Dict[str, StateMetadata]] = {
            scope: {} for scope in StateScope
        }
        self._lock = threading.RLock()
        self.observers: List[IStateObserver] = []
    
    async def get(self, key: str, scope: StateScope) -> Optional[Any]:
        """Get state value"""
        with self._lock:
            if key in self.storage[scope]:
                # Check expiration
                metadata = self.metadata[scope].get(key)
                if metadata and metadata.expires_at:
                    if datetime.now(timezone.utc) > metadata.expires_at:
                        await self.delete(key, scope)
                        return None
                
                return self.storage[scope][key]
            return None
    
    async def set(self, key: str, value: Any, scope: StateScope, **kwargs) -> None:
        """Set state value"""
        with self._lock:
            old_value = self.storage[scope].get(key)
            
            # Create or update metadata
            if key in self.metadata[scope]:
                metadata = self.metadata[scope][key]
                metadata.updated_at = datetime.now(timezone.utc)
                metadata.version += 1
            else:
                metadata = StateMetadata(
                    key=key,
                    scope=scope,
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                    tags=set(kwargs.get("tags", [])),
                    expires_at=kwargs.get("expires_at")
                )
            
            # Store value and metadata
            self.storage[scope][key] = value
            self.metadata[scope][key] = metadata
            
            # Notify observers
            event = StateEvent(
                event_type=StateEventType.UPDATED if old_value is not None else StateEventType.CREATED,
                key=key,
                scope=scope,
                timestamp=datetime.now(timezone.utc),
                old_value=old_value,
                new_value=value,
                metadata=metadata
            )
            
            await self._notify_observers(event)
    
    async def delete(self, key: str, scope: StateScope) -> None:
        """Delete state value"""
        with self._lock:
            if key in self.storage[scope]:
                old_value = self.storage[scope][key]
                metadata = self.metadata[scope].get(key)
                
                del self.storage[scope][key]
                if key in self.metadata[scope]:
                    del self.metadata[scope][key]
                
                # Notify observers
                event = StateEvent(
                    event_type=StateEventType.DELETED,
                    key=key,
                    scope=scope,
                    timestamp=datetime.now(timezone.utc),
                    old_value=old_value,
                    new_value=None,
                    metadata=metadata
                )
                
                await self._notify_observers(event)
    
    async def exists(self, key: str, scope: StateScope) -> bool:
        """Check if key exists"""
        with self._lock:
            return key in self.storage[scope]
    
    async def clear_scope(self, scope: StateScope) -> None:
        """Clear all values in scope"""
        with self._lock:
            for key in list(self.storage[scope].keys()):
                await self.delete(key, scope)
    
    def add_observer(self, observer: IStateObserver) -> None:
        """Add state observer"""
        self.observers.append(observer)
    
    def remove_observer(self, observer: IStateObserver) -> None:
        """Remove state observer"""
        if observer in self.observers:
            self.observers.remove(observer)
    
    async def _notify_observers(self, event: StateEvent) -> None:
        """Notify all observers"""
        for observer in self.observers:
            try:
                await observer.on_state_changed(event)
            except Exception as e:
                logger.error(f"❌ Observer notification failed: {e}")


class RedisStateStore(IStateStore):
    """Redis-based state store"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.key_prefix = "state:"
    
    def _get_key(self, key: str, scope: StateScope) -> str:
        """Get full Redis key"""
        return f"{self.key_prefix}{scope.value}:{key}"
    
    async def get(self, key: str, scope: StateScope) -> Optional[Any]:
        """Get state value from Redis"""
        redis_key = self._get_key(key, scope)
        
        # Get value and metadata
        value_data = await self.redis.hgetall(redis_key)
        if not value_data:
            return None
        
        # Check expiration
        expires_at_str = value_data.get(b"expires_at", b"").decode()
        if expires_at_str:
            expires_at = datetime.fromisoformat(expires_at_str)
            if datetime.now(timezone.utc) > expires_at:
                await self.delete(key, scope)
                return None
        
        # Return value
        import json
        value_json = value_data.get(b"value", b"null").decode()
        return json.loads(value_json)
    
    async def set(self, key: str, value: Any, scope: StateScope, **kwargs) -> None:
        """Set state value in Redis"""
        redis_key = self._get_key(key, scope)
        
        import json
        value_json = json.dumps(value)
        
        # Prepare metadata
        metadata = {
            "value": value_json,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "scope": scope.value,
            "version": 1
        }
        
        if "expires_at" in kwargs:
            metadata["expires_at"] = kwargs["expires_at"].isoformat()
        
        if "tags" in kwargs:
            metadata["tags"] = json.dumps(list(kwargs["tags"]))
        
        # Store in Redis
        await self.redis.hmset(redis_key, metadata)
        
        # Set expiration if specified
        if "expires_at" in kwargs:
            ttl = int((kwargs["expires_at"] - datetime.now(timezone.utc)).total_seconds())
            if ttl > 0:
                await self.redis.expire(redis_key, ttl)
    
    async def delete(self, key: str, scope: StateScope) -> None:
        """Delete state value from Redis"""
        redis_key = self._get_key(key, scope)
        await self.redis.delete(redis_key)
    
    async def exists(self, key: str, scope: StateScope) -> bool:
        """Check if key exists in Redis"""
        redis_key = self._get_key(key, scope)
        return await self.redis.exists(redis_key) > 0
    
    async def clear_scope(self, scope: StateScope) -> None:
        """Clear all values in scope from Redis"""
        pattern = f"{self.key_prefix}{scope.value}:*"
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)


class ApplicationStateManager:
    """Main application state manager"""
    
    def __init__(self, state_store: IStateStore):
        self.state_store = state_store
        self.request_contexts: Dict[str, Dict[str, Any]] = {}
        self.session_contexts: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()
    
    @contextmanager
    def request_context(self, request_id: str):
        """Context manager for request-scoped state"""
        try:
            with self._lock:
                self.request_contexts[request_id] = {}
            yield self
        finally:
            with self._lock:
                if request_id in self.request_contexts:
                    del self.request_contexts[request_id]
                # Clear request-scoped state
                asyncio.create_task(self.state_store.clear_scope(StateScope.REQUEST))
    
    @asynccontextmanager
    async def async_request_context(self, request_id: str):
        """Async context manager for request-scoped state"""
        try:
            with self._lock:
                self.request_contexts[request_id] = {}
            yield self
        finally:
            with self._lock:
                if request_id in self.request_contexts:
                    del self.request_contexts[request_id]
                # Clear request-scoped state
                await self.state_store.clear_scope(StateScope.REQUEST)
    
    @contextmanager
    def session_context(self, session_id: str):
        """Context manager for session-scoped state"""
        try:
            with self._lock:
                self.session_contexts[session_id] = {}
            yield self
        finally:
            with self._lock:
                if session_id in self.session_contexts:
                    del self.session_contexts[session_id]
    
    async def get_state(self, key: str, scope: StateScope = StateScope.REQUEST) -> Optional[Any]:
        """Get state value"""
        return await self.state_store.get(key, scope)
    
    async def set_state(
        self,
        key: str,
        value: Any,
        scope: StateScope = StateScope.REQUEST,
        **kwargs
    ) -> None:
        """Set state value"""
        await self.state_store.set(key, value, scope, **kwargs)
    
    async def delete_state(self, key: str, scope: StateScope = StateScope.REQUEST) -> None:
        """Delete state value"""
        await self.state_store.delete(key, scope)
    
    async def has_state(self, key: str, scope: StateScope = StateScope.REQUEST) -> bool:
        """Check if state exists"""
        return await self.state_store.exists(key, scope)
    
    async def clear_scope(self, scope: StateScope) -> None:
        """Clear all state in scope"""
        await self.state_store.clear_scope(scope)


class ThreadSafeSingleton:
    """Thread-safe singleton pattern"""
    
    def __init__(self, cls: Type[T]):
        self.cls = cls
        self._instance: Optional[T] = None
        self._lock = threading.RLock()
    
    def __call__(self, *args, **kwargs) -> T:
        if self._instance is None:
            with self._lock:
                if self._instance is None:
                    self._instance = self.cls(*args, **kwargs)
        return self._instance


class ContextVarManager:
    """Context variable manager for request context"""
    
    def __init__(self):
        self.context_vars: Dict[str, Any] = {}
        self._lock = threading.RLock()
    
    def set_context_var(self, name: str, value: Any) -> None:
        """Set context variable"""
        with self._lock:
            self.context_vars[name] = value
    
    def get_context_var(self, name: str, default: Any = None) -> Any:
        """Get context variable"""
        with self._lock:
            return self.context_vars.get(name, default)
    
    def clear_context_vars(self) -> None:
        """Clear all context variables"""
        with self._lock:
            self.context_vars.clear()


class StateObserver(IStateObserver):
    """Default state observer implementation"""
    
    async def on_state_changed(self, event: StateEvent) -> None:
        """Handle state change event"""
        logger.info(
            f"📊 State {event.event_type.value}: {event.key} "
            f"({event.scope.value}) at {event.timestamp}"
        )


class CleanupManager:
    """Resource cleanup manager"""
    
    def __init__(self):
        self.cleanup_handlers: List[Callable] = []
        self._lock = threading.RLock()
    
    def register_cleanup(self, handler: Callable) -> None:
        """Register cleanup handler"""
        with self._lock:
            self.cleanup_handlers.append(handler)
    
    async def cleanup(self) -> None:
        """Execute all cleanup handlers"""
        with self._lock:
            handlers = self.cleanup_handlers.copy()
        
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler()
                else:
                    handler()
            except Exception as e:
                logger.error(f"❌ Cleanup handler failed: {e}")


# Global state manager instance (thread-safe singleton)
_state_manager: Optional[ApplicationStateManager] = None
_state_manager_lock = threading.RLock()


def get_state_manager() -> ApplicationStateManager:
    """Get global state manager instance"""
    global _state_manager
    if _state_manager is None:
        with _state_manager_lock:
            if _state_manager is None:
                state_store = ThreadSafeStateStore()
                _state_manager = ApplicationStateManager(state_store)
    return _state_manager


def set_state_manager(manager: ApplicationStateManager) -> None:
    """Set global state manager instance"""
    global _state_manager
    with _state_manager_lock:
        _state_manager = manager


# Context managers for different scopes
@contextmanager
def request_scope(request_id: str):
    """Request scope context manager"""
    manager = get_state_manager()
    with manager.request_context(request_id):
        yield manager


@asynccontextmanager
async def async_request_scope(request_id: str):
    """Async request scope context manager"""
    manager = get_state_manager()
    async with manager.async_request_context(request_id):
        yield manager


@contextmanager
def session_scope(session_id: str):
    """Session scope context manager"""
    manager = get_state_manager()
    with manager.session_context(session_id):
        yield manager


# Decorators for state management
def with_state(scope: StateScope = StateScope.REQUEST):
    """Decorator to inject state manager"""
    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs):
            manager = get_state_manager()
            # Inject state manager as first argument
            return await func(manager, *args, **kwargs)
        return wrapper
    return decorator


def stateful(scope: StateScope = StateScope.REQUEST):
    """Decorator for stateful functions"""
    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs):
            manager = get_state_manager()
            # Store function result in state
            result = await func(*args, **kwargs)
            await manager.set_state(f"{func.__name__}_result", result, scope)
            return result
        return wrapper
    return decorator


# Factory functions
def create_state_manager(use_redis: bool = False, redis_url: str = "redis://localhost:6379") -> ApplicationStateManager:
    """Create state manager"""
    if use_redis:
        redis_client = redis.from_url(redis_url)
        state_store = RedisStateStore(redis_client)
    else:
        state_store = ThreadSafeStateStore()
    
    return ApplicationStateManager(state_store)


def create_context_var_manager() -> ContextVarManager:
    """Create context variable manager"""
    return ContextVarManager()


def create_cleanup_manager() -> CleanupManager:
    """Create cleanup manager"""
    return CleanupManager()


# Utility functions
def create_state_metadata(
    key: str,
    scope: StateScope,
    **kwargs
) -> StateMetadata:
    """Create state metadata"""
    return StateMetadata(
        key=key,
        scope=scope,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        **kwargs
    )


def singleton(cls: Type[T]) -> Type[T]:
    """Singleton decorator"""
    return ThreadSafeSingleton(cls) 