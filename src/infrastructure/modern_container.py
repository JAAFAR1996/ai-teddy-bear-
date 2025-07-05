from typing import Any, Dict, List, Optional

"""
Enterprise Dependency Injection Container - 2025
Advanced DI container with service lifecycle management, health monitoring, and async capabilities
"""

import asyncio
import importlib
import inspect
import logging
import threading
import weakref
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from contextvars import ContextVar
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Generic,
    List,
    Optional,
    Type,
    TypeVar,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)
from functools import wraps

import structlog
from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject
from tenacity import retry, stop_after_attempt, wait_exponential

logger = structlog.get_logger()

T = TypeVar("T")
ServiceType = TypeVar("ServiceType")


class ServiceLifetime(Enum):
    """Service lifetime management options"""

    SINGLETON = "singleton"
    SCOPED = "scoped"
    TRANSIENT = "transient"
    THREAD_LOCAL = "thread_local"


class ServiceStatus(Enum):
    """Service health status"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    STARTING = "starting"
    STOPPING = "stopping"
    STOPPED = "stopped"


@dataclass
class ServiceRegistration:
    """Service registration metadata"""

    name: str
    service_type: Type
    implementation: Optional[Type] = None
    factory: Optional[Callable] = None
    lifetime: ServiceLifetime = ServiceLifetime.SINGLETON
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    health_check: Optional[Callable[[], Awaitable[bool]]] = None
    initialization_timeout: float = 30.0
    shutdown_timeout: float = 10.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ServiceInstance:
    """Service instance wrapper with lifecycle tracking"""

    service: Any
    registration: ServiceRegistration
    created_at: datetime
    status: ServiceStatus = ServiceStatus.HEALTHY
    last_health_check: Optional[datetime] = None
    health_check_failures: int = 0
    access_count: int = 0
    last_accessed: Optional[datetime] = None


class ServiceHealthMonitor:
    """Service health monitoring system"""

    def __init__(self, container: "EnterpriseContainer"):
        self.container = container
        self.monitoring_interval = 30.0  # seconds
        self.health_check_timeout = 5.0  # seconds
        self.max_failures = 3
        self._monitoring_task: Optional[asyncio.Task] = None
        self._health_history: Dict[str, List[bool]] = {}

    async def start_monitoring(self):
        """Start health monitoring"""
        if self._monitoring_task is None or self._monitoring_task.done():
            self._monitoring_task = asyncio.create_task(
                self._monitoring_loop())
            logger.info("Service health monitoring started")

    async def stop_monitoring(self):
        """Stop health monitoring"""
        if self._monitoring_task and not self._monitoring_task.done():
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
            logger.info("Service health monitoring stopped")

    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while True:
            try:
                await asyncio.sleep(self.monitoring_interval)
                await self._check_all_services()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Health monitoring error", error=str(e))

    async def _check_all_services(self):
        """Check health of all registered services"""
        for service_name, instance in self.container._instances.items():
            if instance.registration.health_check:
                await self._check_service_health(service_name, instance)

    async def _check_service_health(
            self,
            service_name: str,
            instance: ServiceInstance):
        """Check health of a specific service"""
        try:
            health_check_result = await asyncio.wait_for(
                instance.registration.health_check(), timeout=self.health_check_timeout
            )
            self._update_health_history(service_name, health_check_result)
            await self._update_service_status(service_name, instance, health_check_result)

        except asyncio.TimeoutError:
            logger.warning("Health check timeout", service=service_name)
            instance.health_check_failures += 1
        except Exception as e:
            logger.error(
                "Health check error",
                service=service_name,
                error=str(e))
            instance.health_check_failures += 1

    def _update_health_history(self, service_name: str, result: bool):
        """Updates the health history for a service."""
        if service_name not in self._health_history:
            self._health_history[service_name] = []
        self._health_history[service_name].append(result)
        if len(self._health_history[service_name]) > 10:
            self._health_history[service_name] = self._health_history[service_name][-10:]

    async def _update_service_status(self, service_name: str, instance: ServiceInstance, result: bool):
        """Updates the service status based on health check result."""
        instance.last_health_check = datetime.utcnow()
        if result:
            self._handle_healthy_service(service_name, instance)
        else:
            await self._handle_unhealthy_service(service_name, instance)

    def _handle_healthy_service(self, service_name: str, instance: ServiceInstance):
        """Handles a healthy service."""
        instance.health_check_failures = 0
        if instance.status == ServiceStatus.DEGRADED:
            instance.status = ServiceStatus.HEALTHY
            logger.info("Service recovered", service=service_name)

    async def _handle_unhealthy_service(self, service_name: str, instance: ServiceInstance):
        """Handles an unhealthy service."""
        instance.health_check_failures += 1
        if instance.health_check_failures >= self.max_failures:
            if instance.status != ServiceStatus.UNHEALTHY:
                instance.status = ServiceStatus.UNHEALTHY
                logger.error(
                    "Service marked as unhealthy",
                    service=service_name,
                    failures=instance.health_check_failures,
                )
                await self._attempt_service_recovery(service_name, instance)
        elif instance.status == ServiceStatus.HEALTHY:
            instance.status = ServiceStatus.DEGRADED
            logger.warning("Service degraded", service=service_name)

    async def _attempt_service_recovery(
        self, service_name: str, instance: ServiceInstance
    ):
        """Attempt to recover an unhealthy service"""
        logger.info("Attempting service recovery", service=service_name)

        try:
            # Mark as stopping
            instance.status = ServiceStatus.STOPPING

            # Call cleanup if available
            if hasattr(instance.service, "cleanup"):
                await instance.service.cleanup()

            # Remove from instances
            del self.container._instances[service_name]

            # Mark as starting
            instance.status = ServiceStatus.STARTING

            # Recreate service
            new_instance = await self.container._create_service_instance(
                service_name, instance.registration
            )

            logger.info("Service recovered successfully", service=service_name)

        except Exception as e:
            logger.error(
                "Service recovery failed",
                service=service_name,
                error=str(e))
            instance.status = ServiceStatus.UNHEALTHY

    def get_health_status(self, service_name: str) -> Dict[str, Any]:
        """Get detailed health status for a service"""
        if service_name in self.container._instances:
            instance = self.container._instances[service_name]
            history = self._health_history.get(service_name, [])

            success_rate = (
                sum(history) /
                len(history) *
                100) if history else 0

            return {
                "service": service_name,
                "status": instance.status.value,
                "last_check": (
                    instance.last_health_check.isoformat()
                    if instance.last_health_check
                    else None
                ),
                "failures": instance.health_check_failures,
                "success_rate": round(success_rate, 2),
                "uptime": (datetime.utcnow() - instance.created_at).total_seconds(),
                "access_count": instance.access_count,
                "last_accessed": (
                    instance.last_accessed.isoformat()
                    if instance.last_accessed
                    else None
                ),
            }

        return {"service": service_name, "status": "not_found"}


class AsyncServiceResolver:
    """Async service resolution with caching and lazy loading"""

    def __init__(self, container: "EnterpriseContainer"):
        self.container = container
        self._resolution_cache: Dict[str, Any] = {}
        self._resolution_locks: Dict[str, asyncio.Lock] = {}
        self._cache_ttl = timedelta(minutes=5)
        self._cache_timestamps: Dict[str, datetime] = {}

    async def resolve(
        self, service_name: str, context: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Resolve service asynchronously with caching"""
        # Check cache first
        if self._is_cached(service_name):
            return self._resolution_cache[service_name]

        # Get or create lock for this service
        if service_name not in self._resolution_locks:
            self._resolution_locks[service_name] = asyncio.Lock()

        async with self._resolution_locks[service_name]:
            # Double-check cache after acquiring lock
            if self._is_cached(service_name):
                return self._resolution_cache[service_name]

            # Resolve service
            service = await self._resolve_service(service_name, context)

            # Cache if singleton
            registration = self.container._registrations.get(service_name)
            if registration and registration.lifetime == ServiceLifetime.SINGLETON:
                self._resolution_cache[service_name] = service
                self._cache_timestamps[service_name] = datetime.utcnow()

            return service

    def _is_cached(self, service_name: str) -> bool:
        """Check if service is cached and not expired"""
        if service_name not in self._resolution_cache:
            return False

        timestamp = self._cache_timestamps.get(service_name)
        if not timestamp:
            return False

        return datetime.utcnow() - timestamp < self._cache_ttl

    async def _resolve_service(
        self, service_name: str, context: Optional[Dict[str, Any]]
    ) -> Any:
        """Resolve service implementation"""
        registration = self.container._registrations.get(service_name)
        if not registration:
            raise ValueError(f"Service '{service_name}' not registered")

        # Check if instance already exists (for singletons)
        if registration.lifetime == ServiceLifetime.SINGLETON:
            if service_name in self.container._instances:
                instance = self.container._instances[service_name]
                instance.access_count += 1
                instance.last_accessed = datetime.utcnow()
                return instance.service

        # Create new instance
        return await self.container._create_service_instance(service_name, registration)

    def clear_cache(self, service_name: Optional[str] = None) -> None:
        """Clear resolution cache for a specific service or the entire cache."""
        if service_name:
            self._resolution_cache.pop(service_name, None)
            self._cache_timestamps.pop(service_name, None)
        else:
            self._resolution_cache.clear()
            self._cache_timestamps.clear()


class EnterpriseContainer:
    """
    Enterprise-grade dependency injection container with:
    - Async service resolution
    - Service lifecycle management
    - Health monitoring
    - Thread-safe operations
    - Scoped service support
    - Service discovery and registration
    """

    def __init__(self, name: str = "default"):
        self.name = name
        self._registrations: Dict[str, ServiceRegistration] = {}
        self._instances: Dict[str, ServiceInstance] = {}
        self._scoped_instances: Dict[str, Dict[str, Any]] = {}
        self._thread_local = threading.local()
        self._lock = asyncio.Lock()
        self._executor = ThreadPoolExecutor(
            max_workers=4, thread_name_prefix="container"
        )

        # Advanced features
        self.health_monitor = ServiceHealthMonitor(self)
        self.resolver = AsyncServiceResolver(self)

        # Container state
        self._initialized = False
        self._disposed = False

        logger.info("Enterprise container created", name=name)

    async def initialize(self, settings: Any = None):
        """Initialize container with configuration"""
        if self._initialized:
            return

        async with self._lock:
            if self._initialized:
                return

            logger.info("Initializing enterprise container", name=self.name)

            try:
                # Start health monitoring
                await self.health_monitor.start_monitoring()

                # Initialize core services
                await self._initialize_core_services(settings)

                self._initialized = True
                logger.info("Enterprise container initialized successfully")

            except Exception as e:
                logger.error("Container initialization failed", error=str(e))
                raise

    async def _initialize_core_services(self, settings: Any):
        """Initialize core infrastructure services"""
        # Register session manager
        if settings:
            # Register Redis session manager if configured
            if hasattr(settings, "redis_url"):
                await self.register_service(
                    "session_manager",
                    "src.infrastructure.session_manager",
                    "RedisSessionManager",
                    lifetime=ServiceLifetime.SINGLETON,
                    health_check=self._session_manager_health_check,
                )

            # Register other core services based on settings
            pass

    async def register_service(self, registration: ServiceRegistration):
        """Register a service with the container using a registration object."""
        try:
            # Ensure implementation is set if not already
            if not registration.implementation:
                module = importlib.import_module(registration.module_path)
                registration.implementation = getattr(
                    module, registration.class_name)

            async with self._lock:
                self._registrations[registration.name] = registration

            logger.info(
                "Service registered",
                name=registration.name,
                type=registration.class_name,
                lifetime=registration.lifetime.value,
            )

        except Exception as e:
            logger.error(
                "Service registration failed",
                name=registration.name,
                module=registration.module_path,
                class_name=registration.class_name,
                error=str(e),
            )
            raise

    async def get_service(
        self,
        service_name_or_type: Union[str, Type[T]],
        context: Optional[Dict[str, Any]] = None,
    ) -> T:
        """Get service instance asynchronously"""
        if not self._initialized:
            await self.initialize()

        if self._disposed:
            raise RuntimeError("Container has been disposed")

        # Handle type-based resolution
        if not isinstance(service_name_or_type, str):
            service_name = self._find_service_by_type(service_name_or_type)
        else:
            service_name = service_name_or_type

        return await self.resolver.resolve(service_name, context)

    def _find_service_by_type(self, service_type: Type) -> str:
        """Find service name by type"""
        for name, registration in self._registrations.items():
            if registration.service_type == service_type:
                return name

        raise ValueError(
            f"No service registered for type '{service_type.__name__}'")

    async def _create_service_instance(
        self, service_name: str, registration: ServiceRegistration
    ) -> Any:
        """Create service instance with dependency injection"""
        try:
            logger.debug("Creating service instance", service=service_name)

            # Resolve dependencies first
            dependencies = {}
            for dep_name in registration.dependencies:
                dependencies[dep_name] = await self.get_service(dep_name)

            # Get constructor parameters
            constructor = registration.implementation.__init__
            sig = inspect.signature(constructor)
            constructor_params = {}

            # Map dependencies to constructor parameters
            for param_name, param in sig.parameters.items():
                if param_name == "self":
                    continue

                # Try to find dependency by name or type annotation
                if param_name in dependencies:
                    constructor_params[param_name] = dependencies[param_name]
                elif param.annotation != inspect.Parameter.empty:
                    try:
                        dep_service = await self.get_service(param.annotation)
                        constructor_params[param_name] = dep_service
                    except ValueError:
                        # Parameter not available, use default if provided
                        if param.default != inspect.Parameter.empty:
                            constructor_params[param_name] = param.default

            # Create instance
            if asyncio.iscoroutinefunction(registration.implementation):
                service = await registration.implementation(**constructor_params)
            else:
                # Run in thread pool for CPU-intensive initialization
                service = await asyncio.get_event_loop().run_in_executor(
                    self._executor,
                    lambda: registration.implementation(**constructor_params),
                )

            # Initialize if has async initialization
            if hasattr(service, "initialize") and asyncio.iscoroutinefunction(
                service.initialize
            ):
                await asyncio.wait_for(
                    service.initialize(), timeout=registration.initialization_timeout
                )

            # Create service instance wrapper
            instance = ServiceInstance(
                service=service,
                registration=registration,
                created_at=datetime.utcnow(),
                status=ServiceStatus.HEALTHY,
            )

            # Store instance based on lifetime
            if registration.lifetime == ServiceLifetime.SINGLETON:
                self._instances[service_name] = instance
            elif registration.lifetime == ServiceLifetime.THREAD_LOCAL:
                if not hasattr(self._thread_local, "instances"):
                    self._thread_local.instances = {}
                self._thread_local.instances[service_name] = instance

            logger.info("Service instance created", service=service_name)
            return service

        except Exception as e:
            logger.error(
                "Service creation failed",
                service=service_name,
                error=str(e))
            raise

    async def get_services_by_tag(self, tag: str) -> List[Any]:
        """Get all services with a specific tag"""
        services = []
        for name, registration in self._registrations.items():
            if tag in registration.tags:
                service = await self.get_service(name)
                services.append(service)
        return services

    async def health_check(
            self, service_name: Optional[str] = None) -> Dict[str, Any]:
        """Get health status of services"""
        if service_name:
            return self.health_monitor.get_health_status(service_name)

        # Get all service health statuses
        health_statuses = {}
        for name in self._registrations:
            health_statuses[name] = self.health_monitor.get_health_status(name)

        # Calculate overall health
        total_services = len(health_statuses)
        healthy_services = sum(
            1
            for status in health_statuses.values()
            if status.get("status") == "healthy"
        )

        overall_health = "healthy" if healthy_services == total_services else "degraded"
        if healthy_services < total_services * 0.5:
            overall_health = "unhealthy"

        return {
            "overall_status": overall_health,
            "healthy_services": healthy_services,
            "total_services": total_services,
            "services": health_statuses,
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def cleanup(self):
        """Cleanup container resources"""
        if self._disposed:
            return

        logger.info("Cleaning up enterprise container", name=self.name)

        async with self._lock:
            try:
                # Stop health monitoring
                await self.health_monitor.stop_monitoring()

                # Dispose all service instances
                for service_name, instance in list(self._instances.items()):
                    await self._dispose_service_instance(service_name, instance)

                # Clear registrations
                self._registrations.clear()
                self._instances.clear()

                # Shutdown executor
                self._executor.shutdown(wait=True)

                self._disposed = True
                logger.info("Enterprise container cleaned up successfully")

            except Exception as e:
                logger.error("Container cleanup error", error=str(e))
                raise

    async def _dispose_service_instance(
        self, service_name: str, instance: ServiceInstance
    ):
        """Dispose a service instance"""
        try:
            instance.status = ServiceStatus.STOPPING

            # Call cleanup if available
            if hasattr(instance.service, "cleanup"):
                if asyncio.iscoroutinefunction(instance.service.cleanup):
                    await asyncio.wait_for(
                        instance.service.cleanup(),
                        timeout=instance.registration.shutdown_timeout,
                    )
                else:
                    await asyncio.get_event_loop().run_in_executor(
                        self._executor, instance.service.cleanup
                    )

            instance.status = ServiceStatus.STOPPED
            logger.debug("Service instance disposed", service=service_name)

        except Exception as e:
            logger.error(
                "Service disposal error",
                service=service_name,
                error=str(e))

    # Health check implementations for core services
    async def _session_manager_health_check(self) -> bool:
        """Health check for session manager"""
        try:
            session_manager = await self.get_service("session_manager")
            # Perform simple health check
            return (
                hasattr(session_manager, "redis_client")
                and session_manager.redis_client is not None
            )
        except Exception as e:
            logger.error(f"Session manager health check failed: {e}")
            return False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        asyncio.create_task(self.cleanup())

    async def __aenter__(self):
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()


# Global container instance
_global_container: Optional[EnterpriseContainer] = None


def get_container() -> EnterpriseContainer:
    """Get global container instance"""
    global _global_container
    if _global_container is None:
        _global_container = EnterpriseContainer("global")
    return _global_container


def set_container(container: EnterpriseContainer) -> None:
    """Set global container instance"""
    global _global_container
    _global_container = container


# Dependency injection decorators
def injectable(
        lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT) -> Callable:
    """Mark class as injectable service"""

    def decorator(cls: Type[T]) -> Type[T]:
        cls._injectable_lifetime = lifetime
        return cls

    return decorator


def inject_service(service_name: str) -> Callable:
    """Inject service dependency"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            container = get_container()
            service = await container.get_service(service_name)
            return await func(service, *args, **kwargs)

        return wrapper

    return decorator
