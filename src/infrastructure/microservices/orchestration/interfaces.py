"""
Interfaces for the service orchestration layer, defining the contracts for
service registry, discovery, load balancing, and health checking.
"""
from abc import ABC, abstractmethod
from typing import Callable, List, Optional

from .models import (
    LoadBalancingStrategy,
    ServiceDefinition,
    ServiceInstance,
    ServiceStatus,
)


class IServiceRegistry(ABC):
    """Service registry interface"""

    @abstractmethod
    async def register_service(self, service: ServiceDefinition) -> None:
        """Register service"""
        pass

    @abstractmethod
    async def deregister_service(self, service_name: str) -> None:
        """Deregister service"""
        pass

    @abstractmethod
    async def get_service(self, service_name: str) -> Optional[ServiceDefinition]:
        """Get service"""
        pass

    @abstractmethod
    async def list_services(self) -> List[ServiceDefinition]:
        """List all services"""
        pass


class IServiceDiscovery(ABC):
    """Service discovery interface"""

    @abstractmethod
    async def discover_services(self, service_name: str) -> List[ServiceInstance]:
        """Discover service instances"""
        pass

    @abstractmethod
    async def watch_service(self, service_name: str, callback: Callable) -> None:
        """Watch service changes"""
        pass


class ILoadBalancer(ABC):
    """Load balancer interface"""

    @abstractmethod
    async def select_instance(
        self, service_name: str, strategy: LoadBalancingStrategy
    ) -> Optional[ServiceInstance]:
        """Select service instance"""
        pass

    @abstractmethod
    async def update_instance_status(self, instance_id: str, status: ServiceStatus) -> None:
        """Update instance status"""
        pass


class IHealthChecker(ABC):
    """Health checker interface"""

    @abstractmethod
    async def check_health(self, instance: ServiceInstance) -> ServiceStatus:
        """Check instance health"""
        pass

    @abstractmethod
    async def start_monitoring(self, service: ServiceDefinition) -> None:
        """Start health monitoring"""
        pass

    @abstractmethod
    async def stop_monitoring(self, service_name: str) -> None:
        """Stop health monitoring"""
        pass
