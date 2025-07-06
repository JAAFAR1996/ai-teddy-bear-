"""
Factory functions for creating components of the service orchestration layer.
"""
from typing import List

from .consul_registry import ConsulServiceRegistry
from .health_checker import HealthChecker
from .interfaces import (
    IHealthChecker,
    ILoadBalancer,
    IServiceDiscovery,
    IServiceRegistry,
)
from .k8s_discovery import KubernetesServiceDiscovery
from .load_balancer import LoadBalancer
from .models import ServiceDefinition, ServiceInstance


def create_consul_registry(
    consul_host: str = "localhost", consul_port: int = 8500
) -> IServiceRegistry:
    """Create Consul service registry"""
    return ConsulServiceRegistry(consul_host, consul_port)


def create_kubernetes_discovery(namespace: str = "default") -> IServiceDiscovery:
    """Create Kubernetes service discovery"""
    return KubernetesServiceDiscovery(namespace)


def create_load_balancer(discovery: IServiceDiscovery) -> ILoadBalancer:
    """Create load balancer"""
    return LoadBalancer(discovery)


def create_health_checker(load_balancer: ILoadBalancer) -> IHealthChecker:
    """Create health checker"""
    return HealthChecker(load_balancer)


# Utility functions
def create_service_instance(
    id: str, name: str, host: str, port: int, protocol: str = "http", **kwargs
) -> ServiceInstance:
    """Create a service instance object."""
    return ServiceInstance(
        id=id, name=name, host=host, port=port, protocol=protocol, **kwargs
    )


def create_service_definition(
    name: str, version: str, instances: List[ServiceInstance], **kwargs
) -> ServiceDefinition:
    """Create a service definition object."""
    return ServiceDefinition(name=name, version=version, instances=instances, **kwargs)
