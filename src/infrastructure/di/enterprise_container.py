"""
Enterprise-Grade Dependency Injection Container
Advanced DI system with async support, lifecycle management, and circular dependency detection
"""

import asyncio
import inspect
import logging
import threading
import weakref
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Type, TypeVar, Union

from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

T = TypeVar('T')


class LifecycleScope(Enum):
    """Dependency lifecycle scopes"""
    SINGLETON = "singleton"
    REQUEST = "request"
    SESSION = "session"
    TRANSIENT = "transient"


class ContainerState(Enum):
    """Container state management"""
    INITIALIZING = "initializing"
    READY = "ready"
    SHUTTING_DOWN = "shutting_down"
    SHUTDOWN = "shutdown"


@dataclass
class DependencyMetadata:
    """Metadata for dependency registration"""
    interface: Type
    implementation: Type
    scope: LifecycleScope
    factory: Optional[Callable] = None
    dependencies: List[str] = field(default_factory=list)
    async_init: bool = False
    cleanup_method: Optional[str] = None
    health_check: Optional[Callable] = None
    tags: Set[str] = field(default_factory=set)


class IDependencyProvider(ABC):
    """Interface for dependency providers"""
    
    @abstractmethod
    async def get(self, interface: Type[T]) -> T:
        """Get dependency instance"""
        pass
    
    @abstractmethod
    async def register(self, interface: Type, implementation: Type, **kwargs) -> None:
        """Register dependency"""
        pass
    
    @abstractmethod
    async def unregister(self, interface: Type) -> None:
        """Unregister dependency"""
        pass


class CircularDependencyError(Exception):
    """Raised when circular dependency is detected"""
    pass


class DependencyNotFoundError(Exception):
    """Raised when dependency is not found"""
    pass


class LifecycleError(Exception):
    """Raised when lifecycle operation fails"""
    pass


class DependencyGraph:
    """Dependency graph for cycle detection"""
    
    def __init__(self):
        self.graph: Dict[str, Set[str]] = {}
        self.metadata: Dict[str, DependencyMetadata] = {}
    
    def add_dependency(self, interface: str, dependencies: List[str], metadata: DependencyMetadata):
        """Add dependency to graph"""
        self.graph[interface] = set(dependencies)
        self.metadata[interface] = metadata
    
    def detect_cycles(self) -> List[List[str]]:
        """Detect circular dependencies using DFS"""
        visited = set()
        rec_stack = set()
        cycles = []
        
        def dfs(node: str, path: List[str]):
            if node in rec_stack:
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:] + [node])
                return
            
            if node in visited:
                return
            
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in self.graph.get(node, []):
                dfs(neighbor, path.copy())
            
            rec_stack.remove(node)
        
        for node in self.graph:
            if node not in visited:
                dfs(node, [])
        
        return cycles


class AsyncProvider(providers.Provider):
    """Async provider for dependency injection"""
    
    def __init__(self, factory: Callable, *args, **kwargs):
        super().__init__(factory, *args, **kwargs)
        self._async_factory = asyncio.iscoroutinefunction(factory)
    
    async def async_call(self, *args, **kwargs) -> Any:
        """Call provider asynchronously"""
        if self._async_factory:
            return await self._factory(*args, **kwargs)
        else:
            return self._factory(*args, **kwargs)


class LifecycleManager:
    """Manages dependency lifecycles"""
    
    def __init__(self):
        self.singletons: Dict[str, Any] = {}
        self.request_scoped: Dict[str, Any] = {}
        self.session_scoped: Dict[str, Any] = {}
        self._lock = threading.RLock()
    
    def get_instance(self, interface: str, scope: LifecycleScope, factory: Callable, *args, **kwargs) -> Any:
        """Get or create instance based on scope"""
        with self._lock:
            if scope == LifecycleScope.SINGLETON:
                if interface not in self.singletons:
                    self.singletons[interface] = factory(*args, **kwargs)
                return self.singletons[interface]
            
            elif scope == LifecycleScope.REQUEST:
                if interface not in self.request_scoped:
                    self.request_scoped[interface] = factory(*args, **kwargs)
                return self.request_scoped[interface]
            
            elif scope == LifecycleScope.SESSION:
                if interface not in self.session_scoped:
                    self.session_scoped[interface] = factory(*args, **kwargs)
                return self.session_scoped[interface]
            
            else:  # TRANSIENT
                return factory(*args, **kwargs)
    
    def clear_request_scope(self):
        """Clear request-scoped instances"""
        with self._lock:
            self.request_scoped.clear()
    
    def clear_session_scope(self):
        """Clear session-scoped instances"""
        with self._lock:
            self.session_scoped.clear()
    
    async def cleanup(self):
        """Cleanup all instances"""
        with self._lock:
            # Cleanup singletons
            for interface, instance in self.singletons.items():
                if hasattr(instance, 'cleanup'):
                    if asyncio.iscoroutinefunction(instance.cleanup):
                        await instance.cleanup()
                    else:
                        instance.cleanup()
            
            # Cleanup request-scoped
            for interface, instance in self.request_scoped.items():
                if hasattr(instance, 'cleanup'):
                    if asyncio.iscoroutinefunction(instance.cleanup):
                        await instance.cleanup()
                    else:
                        instance.cleanup()
            
            # Cleanup session-scoped
            for interface, instance in self.session_scoped.items():
                if hasattr(instance, 'cleanup'):
                    if asyncio.iscoroutinefunction(instance.cleanup):
                        await instance.cleanup()
                    else:
                        instance.cleanup()
            
            self.singletons.clear()
            self.request_scoped.clear()
            self.session_scoped.clear()


class EnterpriseContainer(containers.DeclarativeContainer):
    """Enterprise-grade dependency injection container"""
    
    def __init__(self, name: str = "enterprise_container"):
        super().__init__()
        self.name = name
        self.state = ContainerState.INITIALIZING
        self.lifecycle_manager = LifecycleManager()
        self.dependency_graph = DependencyGraph()
        self.registrations: Dict[str, DependencyMetadata] = {}
        self._lock = threading.RLock()
        self._initialized = False
        
        logger.info(f"🔧 Enterprise container '{name}' initialized")
    
    def register(
        self,
        interface: Type[T],
        implementation: Type[T],
        scope: LifecycleScope = LifecycleScope.SINGLETON,
        factory: Optional[Callable] = None,
        dependencies: Optional[List[str]] = None,
        async_init: bool = False,
        cleanup_method: Optional[str] = None,
        health_check: Optional[Callable] = None,
        tags: Optional[Set[str]] = None,
    ) -> None:
        """Register dependency with metadata"""
        with self._lock:
            interface_name = interface.__name__
            
            metadata = DependencyMetadata(
                interface=interface,
                implementation=implementation,
                scope=scope,
                factory=factory,
                dependencies=dependencies or [],
                async_init=async_init,
                cleanup_method=cleanup_method,
                health_check=health_check,
                tags=tags or set(),
            )
            
            self.registrations[interface_name] = metadata
            self.dependency_graph.add_dependency(interface_name, metadata.dependencies, metadata)
            
            # Create provider
            if factory:
                provider = AsyncProvider(factory)
            else:
                provider = providers.Factory(implementation)
            
            setattr(self, interface_name.lower(), provider)
            
            logger.info(f"📦 Registered {interface_name} with scope {scope.value}")
    
    def register_singleton(
        self,
        interface: Type[T],
        implementation: Type[T],
        **kwargs
    ) -> None:
        """Register singleton dependency"""
        self.register(interface, implementation, LifecycleScope.SINGLETON, **kwargs)
    
    def register_request_scoped(
        self,
        interface: Type[T],
        implementation: Type[T],
        **kwargs
    ) -> None:
        """Register request-scoped dependency"""
        self.register(interface, implementation, LifecycleScope.REQUEST, **kwargs)
    
    def register_transient(
        self,
        interface: Type[T],
        implementation: Type[T],
        **kwargs
    ) -> None:
        """Register transient dependency"""
        self.register(interface, implementation, LifecycleScope.TRANSIENT, **kwargs)
    
    def detect_circular_dependencies(self) -> List[List[str]]:
        """Detect circular dependencies"""
        cycles = self.dependency_graph.detect_cycles()
        if cycles:
            logger.error(f"🚨 Circular dependencies detected: {cycles}")
        return cycles
    
    async def initialize(self) -> None:
        """Initialize container and all dependencies"""
        with self._lock:
            if self._initialized:
                return
            
            # Detect circular dependencies
            cycles = self.detect_circular_dependencies()
            if cycles:
                raise CircularDependencyError(f"Circular dependencies detected: {cycles}")
            
            # Initialize all singletons
            for interface_name, metadata in self.registrations.items():
                if metadata.scope == LifecycleScope.SINGLETON:
                    try:
                        await self._initialize_dependency(interface_name, metadata)
                    except Exception as e:
                        logger.error(f"❌ Failed to initialize {interface_name}: {e}")
                        raise LifecycleError(f"Failed to initialize {interface_name}: {e}")
            
            self.state = ContainerState.READY
            self._initialized = True
            logger.info(f"✅ Container '{self.name}' initialized successfully")
    
    async def _initialize_dependency(self, interface_name: str, metadata: DependencyMetadata):
        """Initialize a single dependency"""
        if metadata.async_init:
            # For async initialization
            if metadata.factory:
                instance = await metadata.factory()
            else:
                instance = metadata.implementation()
                if hasattr(instance, 'initialize') and asyncio.iscoroutinefunction(instance.initialize):
                    await instance.initialize()
        else:
            # For sync initialization
            if metadata.factory:
                instance = metadata.factory()
            else:
                instance = metadata.implementation()
                if hasattr(instance, 'initialize'):
                    instance.initialize()
        
        # Store in lifecycle manager
        self.lifecycle_manager.singletons[interface_name] = instance
    
    async def get(self, interface: Type[T]) -> T:
        """Get dependency instance"""
        if not self._initialized:
            await self.initialize()
        
        interface_name = interface.__name__
        
        if interface_name not in self.registrations:
            raise DependencyNotFoundError(f"Dependency {interface_name} not registered")
        
        metadata = self.registrations[interface_name]
        
        # Get from lifecycle manager
        if metadata.factory:
            instance = self.lifecycle_manager.get_instance(
                interface_name, metadata.scope, metadata.factory
            )
        else:
            instance = self.lifecycle_manager.get_instance(
                interface_name, metadata.scope, metadata.implementation
            )
        
        return instance
    
    def get_sync(self, interface: Type[T]) -> T:
        """Get dependency instance synchronously"""
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If we're in an async context, use async version
            return asyncio.create_task(self.get(interface))
        else:
            # If we're in a sync context, run async code
            return asyncio.run(self.get(interface))
    
    def resolve_dependencies(self, target_class: Type) -> Dict[str, Any]:
        """Resolve dependencies for a class"""
        dependencies = {}
        
        # Get constructor parameters
        sig = inspect.signature(target_class.__init__)
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
            
            param_type = param.annotation
            if param_type != inspect.Parameter.empty:
                try:
                    dependencies[param_name] = self.get_sync(param_type)
                except Exception as e:
                    logger.warning(f"⚠️ Could not resolve dependency {param_name}: {e}")
        
        return dependencies
    
    @contextmanager
    def request_scope(self):
        """Context manager for request scope"""
        try:
            yield self
        finally:
            self.lifecycle_manager.clear_request_scope()
    
    @asynccontextmanager
    async def async_request_scope(self):
        """Async context manager for request scope"""
        try:
            yield self
        finally:
            self.lifecycle_manager.clear_request_scope()
    
    def get_by_tag(self, tag: str) -> List[Any]:
        """Get all dependencies with specific tag"""
        instances = []
        
        for interface_name, metadata in self.registrations.items():
            if tag in metadata.tags:
                try:
                    instance = self.get_sync(metadata.interface)
                    instances.append(instance)
                except Exception as e:
                    logger.warning(f"⚠️ Could not get {interface_name} with tag {tag}: {e}")
        
        return instances
    
    async def health_check(self) -> Dict[str, bool]:
        """Perform health check on all dependencies"""
        health_status = {}
        
        for interface_name, metadata in self.registrations.items():
            try:
                instance = await self.get(metadata.interface)
                
                if metadata.health_check:
                    health_status[interface_name] = metadata.health_check(instance)
                elif hasattr(instance, 'health_check'):
                    if asyncio.iscoroutinefunction(instance.health_check):
                        health_status[interface_name] = await instance.health_check()
                    else:
                        health_status[interface_name] = instance.health_check()
                else:
                    health_status[interface_name] = True
                    
            except Exception as e:
                logger.error(f"❌ Health check failed for {interface_name}: {e}")
                health_status[interface_name] = False
        
        return health_status
    
    async def shutdown(self) -> None:
        """Shutdown container and cleanup all dependencies"""
        with self._lock:
            if self.state == ContainerState.SHUTDOWN:
                return
            
            self.state = ContainerState.SHUTTING_DOWN
            logger.info(f"🔄 Shutting down container '{self.name}'")
            
            try:
                await self.lifecycle_manager.cleanup()
                self.state = ContainerState.SHUTDOWN
                logger.info(f"✅ Container '{self.name}' shut down successfully")
            except Exception as e:
                logger.error(f"❌ Error during container shutdown: {e}")
                raise LifecycleError(f"Container shutdown failed: {e}")


# Global container instance
_global_container: Optional[EnterpriseContainer] = None


def get_container() -> EnterpriseContainer:
    """Get global container instance"""
    global _global_container
    if _global_container is None:
        _global_container = EnterpriseContainer()
    return _global_container


def set_container(container: EnterpriseContainer) -> None:
    """Set global container instance"""
    global _global_container
    _global_container = container


# Decorators for dependency injection
def inject_dependency(interface: Type[T]):
    """Decorator to inject dependency"""
    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs):
            container = get_container()
            dependency = await container.get(interface)
            return await func(dependency, *args, **kwargs)
        return wrapper
    return decorator


def inject_dependencies(*interfaces: Type):
    """Decorator to inject multiple dependencies"""
    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs):
            container = get_container()
            dependencies = [await container.get(interface) for interface in interfaces]
            return await func(*dependencies, *args, **kwargs)
        return wrapper
    return decorator


# Factory functions
def create_container(name: str = "default") -> EnterpriseContainer:
    """Create new container instance"""
    return EnterpriseContainer(name)


def create_singleton_container() -> EnterpriseContainer:
    """Create container with singleton scope by default"""
    container = EnterpriseContainer("singleton_container")
    return container


def create_request_scoped_container() -> EnterpriseContainer:
    """Create container with request scope by default"""
    container = EnterpriseContainer("request_container")
    return container


# Utility functions
def register_services(container: EnterpriseContainer, services: Dict[Type, Type]) -> None:
    """Register multiple services at once"""
    for interface, implementation in services.items():
        container.register_singleton(interface, implementation)


def auto_wire(container: EnterpriseContainer, target_class: Type) -> Type:
    """Auto-wire dependencies for a class"""
    def wrapper(*args, **kwargs):
        dependencies = container.resolve_dependencies(target_class)
        return target_class(*dependencies, *args, **kwargs)
    
    return wrapper


# Context managers for scoped operations
@contextmanager
def container_scope(container: EnterpriseContainer):
    """Context manager for container operations"""
    try:
        yield container
    finally:
        pass  # Container cleanup handled by lifecycle manager


@asynccontextmanager
async def async_container_scope(container: EnterpriseContainer):
    """Async context manager for container operations"""
    try:
        yield container
    finally:
        pass  # Container cleanup handled by lifecycle manager 