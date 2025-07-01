from typing import Any, Dict, List, Optional

"""
Service Registry Pattern
Solves circular dependencies and provides centralized service management
"""

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Type, TypeVar

import structlog

logger = structlog.get_logger()

T = TypeVar("T", bound="ServiceBase")


class ServiceState(Enum):
    """Service lifecycle states"""

    CREATED = "created"
    INITIALIZING = "initializing"
    READY = "ready"
    DEGRADED = "degraded"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"


class ServicePriority(Enum):
    """Service initialization priority"""

    CRITICAL = 1  # Must start first (database, cache)
    HIGH = 2  # Core services (auth, config)
    NORMAL = 3  # Business services
    LOW = 4  # Optional services


@dataclass
class ServiceInfo:
    """Service metadata"""

    name: str
    service_class: Type
    instance: Optional[Any] = None
    state: ServiceState = ServiceState.CREATED
    priority: ServicePriority = ServicePriority.NORMAL
    dependencies: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    initialized_at: Optional[datetime] = None
    error: Optional[str] = None
    health_check_interval: float = 60.0
    _health_check_task: Optional[asyncio.Task] = None


class ServiceBase(ABC):
    """Base class for all services"""

    def __init__(self, registry: "ServiceRegistry", config: Dict[str, Any]):
        self.registry = registry
        self.config = config
        self._state = ServiceState.CREATED
        self.logger = structlog.get_logger(self.__class__.__name__)

    @property
    def state(self) -> ServiceState:
        """Get service state"""
        return self._state

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the service"""
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        """Shutdown the service"""
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        pass

    def get_service(self, service_name: str) -> Any:
        """Get another service from registry (avoids circular imports)"""
        return self.registry.get_service(service_name)

    async def wait_for_service(self, service_name: str, timeout: float = 30.0) -> Any:
        """Wait for a service to be ready"""
        return await self.registry.wait_for_service(service_name, timeout)


class ServiceRegistry:
    """
    Central service registry and lifecycle manager
    Solves circular dependencies by lazy loading and dependency injection
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._services: Dict[str, ServiceInfo] = {}
        self._lock = asyncio.Lock()
        self._initialization_order: List[str] = []
        self._shutdown_order: List[str] = []

    def register_service(
        self,
        name: str,
        service_class: Type[ServiceBase],
        priority: ServicePriority = ServicePriority.NORMAL,
        dependencies: Optional[List[str]] = None,
    ) -> None:
        """Register a service class"""
        if name in self._services:
            raise ValueError(f"Service '{name}' already registered")

        self._services[name] = ServiceInfo(
            name=name,
            service_class=service_class,
            priority=priority,
            dependencies=dependencies or [],
        )

        logger.info(
            "Service registered",
            name=name,
            class_name=service_class.__name__,
            priority=priority.name,
        )

    async def initialize(self) -> None:
        """Initialize all services in dependency order"""
        async with self._lock:
            # Calculate initialization order
            self._initialization_order = self._calculate_init_order()

            logger.info(
                "Starting service initialization", order=self._initialization_order
            )

            # Initialize services
            for service_name in self._initialization_order:
                await self._initialize_service(service_name)

            # Start health checks
            for service_name, info in self._services.items():
                if info.state == ServiceState.READY:
                    info._health_check_task = asyncio.create_task(
                        self._health_check_loop(service_name)
                    )

            logger.info("All services initialized")

    async def _initialize_service(self, name: str) -> None:
        """Initialize a single service"""
        info = self._services[name]

        if info.state != ServiceState.CREATED:
            return  # Already initialized

        try:
            info.state = ServiceState.INITIALIZING
            logger.info(f"Initializing service: {name}")

            # Check dependencies
            for dep in info.dependencies:
                dep_info = self._services.get(dep)
                if not dep_info or dep_info.state != ServiceState.READY:
                    raise Exception(f"Dependency '{dep}' not ready")

            # Create instance
            info.instance = info.service_class(self, self.config)

            # Initialize
            await info.instance.initialize()

            # Update state
            info.state = ServiceState.READY
            info.initialized_at = datetime.utcnow()

            logger.info(f"Service initialized successfully: {name}")

        except Exception as e:
            info.state = ServiceState.FAILED
            info.error = str(e)
            logger.error(f"Service initialization failed: {name}", error=str(e))
            raise

    def get_service(self, name: str) -> Any:
        """Get a service instance"""
        if name not in self._services:
            raise ValueError(f"Service '{name}' not registered")

        info = self._services[name]

        if info.state != ServiceState.READY:
            raise RuntimeError(f"Service '{name}' not ready (state: {info.state})")

        return info.instance

    async def wait_for_service(self, name: str, timeout: float = 30.0) -> Any:
        """Wait for a service to be ready"""
        if name not in self._services:
            raise ValueError(f"Service '{name}' not registered")

        start_time = asyncio.get_event_loop().time()

        while True:
            info = self._services[name]

            if info.state == ServiceState.READY:
                return info.instance

            if info.state == ServiceState.FAILED:
                raise RuntimeError(f"Service '{name}' failed: {info.error}")

            if asyncio.get_event_loop().time() - start_time > timeout:
                raise TimeoutError(f"Timeout waiting for service '{name}'")

            await asyncio.sleep(0.1)

    async def shutdown(self) -> None:
        """Shutdown all services in reverse order"""
        async with self._lock:
            # Calculate shutdown order (reverse of init)
            self._shutdown_order = list(reversed(self._initialization_order))

            logger.info("Starting service shutdown", order=self._shutdown_order)

            # Stop health checks
            for info in self._services.values():
                if info._health_check_task:
                    info._health_check_task.cancel()
                    try:
                        await info._health_check_task
                    except asyncio.CancelledError:
                        pass

            # Shutdown services
            for service_name in self._shutdown_order:
                await self._shutdown_service(service_name)

            logger.info("All services shut down")

    async def _shutdown_service(self, name: str) -> None:
        """Shutdown a single service"""
        info = self._services[name]

        if info.state != ServiceState.READY:
            return

        try:
            info.state = ServiceState.STOPPING
            logger.info(f"Shutting down service: {name}")

            await info.instance.shutdown()

            info.state = ServiceState.STOPPED
            logger.info(f"Service shut down successfully: {name}")

        except Exception as e:
            logger.error(f"Service shutdown failed: {name}", error=str(e))

    def _calculate_init_order(self) -> List[str]:
        """Calculate service initialization order based on dependencies"""
        # Group by priority
        priority_groups = {}
        for name, info in self._services.items():
            priority = info.priority.value
            if priority not in priority_groups:
                priority_groups[priority] = []
            priority_groups[priority].append(name)

        # Sort each group by dependencies
        order = []
        for priority in sorted(priority_groups.keys()):
            group = priority_groups[priority]
            sorted_group = self._topological_sort(group)
            order.extend(sorted_group)

        return order

    def _topological_sort(self, services: List[str]) -> List[str]:
        """Topological sort for dependency resolution"""
        # Build dependency graph
        graph = {s: set() for s in services}
        for service in services:
            info = self._services[service]
            for dep in info.dependencies:
                if dep in graph:
                    graph[service].add(dep)

        # Kahn's algorithm
        in_degree = {s: 0 for s in services}
        for deps in graph.values():
            for dep in deps:
                in_degree[dep] += 1

        queue = [s for s in services if in_degree[s] == 0]
        result = []

        while queue:
            service = queue.pop(0)
            result.append(service)

            for dep in graph[service]:
                in_degree[dep] -= 1
                if in_degree[dep] == 0:
                    queue.append(dep)

        # Check for cycles
        if len(result) != len(services):
            raise ValueError("Circular dependency detected")

        return result

    async def _health_check_loop(self, service_name: str) -> None:
        """Periodic health check for a service"""
        info = self._services[service_name]

        while True:
            try:
                await asyncio.sleep(info.health_check_interval)

                # Perform health check
                health = await info.instance.health_check()

                # Update state based on health
                if health.get("healthy", True):
                    if info.state == ServiceState.DEGRADED:
                        info.state = ServiceState.READY
                        logger.info(f"Service recovered: {service_name}")
                else:
                    if info.state == ServiceState.READY:
                        info.state = ServiceState.DEGRADED
                        logger.warning(
                            f"Service degraded: {service_name}", health=health
                        )

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(
                    f"Health check failed for service: {service_name}", error=str(e)
                )

    def get_status(self) -> Dict[str, Any]:
        """Get status of all services"""
        return {
            name: {
                "state": info.state.value,
                "initialized_at": (
                    info.initialized_at.isoformat() if info.initialized_at else None
                ),
                "error": info.error,
                "dependencies": info.dependencies,
                "priority": info.priority.name,
            }
            for name, info in self._services.items()
        }

    def get_service_info(self, name: str) -> ServiceInfo:
        """Get service information"""
        if name not in self._services:
            raise ValueError(f"Service '{name}' not registered")
        return self._services[name]


# Example of how to use the registry to avoid circular dependencies
class ExampleAIService(ServiceBase):
    """Example AI service that depends on other services"""

    async def initialize(self) -> None:
        """Initialize without direct imports"""
        self.logger.info("Initializing AI service")

        # Get dependencies from registry instead of importing
        self.llm_service = await self.wait_for_service("llm")
        self.moderation_service = await self.wait_for_service("moderation")
        self.memory_service = await self.wait_for_service("memory")

        self._state = ServiceState.READY

    async def shutdown(self) -> None:
        """Cleanup"""
        self._state = ServiceState.STOPPED

    async def health_check(self) -> Dict[str, Any]:
        """Check health"""
        return {
            "healthy": True,
            "services_available": {
                "llm": self.llm_service is not None,
                "moderation": self.moderation_service is not None,
                "memory": self.memory_service is not None,
            },
        }

    async def generate_response(self, message: str) -> str:
        """Generate response using other services"""
        # Moderation check
        if not await self.moderation_service.is_appropriate(message):
            return "عذراً، لا أستطيع الرد على هذا المحتوى"

        # Get context from memory
        context = await self.memory_service.get_context(message)

        # Generate with LLM
        response = await self.llm_service.generate(message, context)

        # Store in memory
        await self.memory_service.store(message, response)

        return response
