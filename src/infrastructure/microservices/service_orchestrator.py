"""
Microservices Orchestrator
Advanced service orchestration with discovery, load balancing, health monitoring, and circuit breakers
"""

import asyncio
import json
import logging
import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Type, TypeVar, Union

import aiohttp
import consul
import kubernetes
from kubernetes import client, config
from pydantic import BaseModel, Field
from typing_extensions import Protocol

logger = logging.getLogger(__name__)

T = TypeVar("T")


class ServiceStatus(Enum):
    """Service status enumeration"""

    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    STARTING = "starting"
    STOPPING = "stopping"
    UNKNOWN = "unknown"


class LoadBalancingStrategy(Enum):
    """Load balancing strategies"""

    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    IP_HASH = "ip_hash"
    RANDOM = "random"


class CircuitBreakerState(Enum):
    """Circuit breaker states"""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class ServiceInstance:
    """Service instance information"""

    id: str
    name: str
    host: str
    port: int
    protocol: str = "http"
    health_check_url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: ServiceStatus = ServiceStatus.UNKNOWN
    last_health_check: Optional[datetime] = None
    response_time: Optional[float] = None
    error_count: int = 0
    success_count: int = 0
    weight: int = 1
    tags: Set[str] = field(default_factory=set)


@dataclass
class ServiceDefinition:
    """Service definition"""

    name: str
    version: str
    instances: List[ServiceInstance] = field(default_factory=list)
    load_balancing_strategy: LoadBalancingStrategy = LoadBalancingStrategy.ROUND_ROBIN
    health_check_interval: int = 30
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 60
    retry_attempts: int = 3
    timeout: int = 30
    max_connections: int = 100
    tags: Set[str] = field(default_factory=set)


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
    async def get_service(
            self,
            service_name: str) -> Optional[ServiceDefinition]:
        """Get service"""
        pass

    @abstractmethod
    async def list_services(self) -> List[ServiceDefinition]:
        """List all services"""
        pass


class IServiceDiscovery(ABC):
    """Service discovery interface"""

    @abstractmethod
    async def discover_services(
            self, service_name: str) -> List[ServiceInstance]:
        """Discover service instances"""
        pass

    @abstractmethod
    async def watch_service(
            self,
            service_name: str,
            callback: Callable) -> None:
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
    async def update_instance_status(
        self, instance_id: str, status: ServiceStatus
    ) -> None:
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


class ConsulServiceRegistry(IServiceRegistry):
    """Consul-based service registry"""

    def __init__(
            self,
            consul_host: str = "localhost",
            consul_port: int = 8500):
        self.consul = consul.Consul(host=consul_host, port=consul_port)
        self.services: Dict[str, ServiceDefinition] = {}

    async def register_service(self, service: ServiceDefinition) -> None:
        """Register service with Consul"""
        # Register each instance
        for instance in service.instances:
            service_id = f"{service.name}-{instance.id}"

            # Prepare service registration
            registration = {
                "ID": service_id,
                "Name": service.name,
                "Address": instance.host,
                "Port": instance.port,
                "Tags": list(instance.tags),
                "Meta": instance.metadata,
                "Check": {
                    "HTTP": instance.health_check_url
                    or f"http://{instance.host}:{instance.port}/health",
                    "Interval": f"{service.health_check_interval}s",
                    "Timeout": "5s",
                },
            }

            # Register with Consul
            self.consul.agent.service.register(**registration)

        # Store locally
        self.services[service.name] = service
        logger.info(
            f"📝 Registered service {service.name} with {len(service.instances)} instances"
        )

    async def deregister_service(self, service_name: str) -> None:
        """Deregister service from Consul"""
        if service_name not in self.services:
            return

        service = self.services[service_name]

        # Deregister each instance
        for instance in service.instances:
            service_id = f"{service.name}-{instance.id}"
            self.consul.agent.service.deregister(service_id)

        # Remove from local storage
        del self.services[service_name]
        logger.info(f"🗑️ Deregistered service {service_name}")

    async def get_service(
            self,
            service_name: str) -> Optional[ServiceDefinition]:
        """Get service from Consul"""
        # Try local cache first
        if service_name in self.services:
            return self.services[service_name]

        # Query Consul
        _, services = self.consul.health.service(service_name, passing=True)

        if not services:
            return None

        # Convert Consul response to ServiceDefinition
        instances = []
        for service in services:
            service_info = service["Service"]
            instance = ServiceInstance(
                id=service_info["ID"],
                name=service_info["Service"],
                host=service_info["Address"],
                port=service_info["Port"],
                tags=set(service_info.get("Tags", [])),
                metadata=service_info.get("Meta", {}),
            )
            instances.append(instance)

        return ServiceDefinition(name=service_name, instances=instances)

    async def list_services(self) -> List[ServiceDefinition]:
        """List all services from Consul"""
        _, services = self.consul.catalog.services()

        service_definitions = []
        for service_name in services:
            service = await self.get_service(service_name)
            if service:
                service_definitions.append(service)

        return service_definitions


class KubernetesServiceDiscovery(IServiceDiscovery):
    """Kubernetes-based service discovery"""

    def __init__(self, namespace: str = "default"):
        try:
            config.load_incluster_config()
        except config.ConfigException:
            config.load_kube_config()

        self.namespace = namespace
        self.v1 = client.CoreV1Api()
        self.watchers: Dict[str, client.Watch] = {}

    async def discover_services(
            self, service_name: str) -> List[ServiceInstance]:
        """Discover service instances in Kubernetes"""
        try:
            # Get service
            service = self.v1.read_namespaced_service(
                service_name, self.namespace)

            # Get endpoints
            endpoints = self.v1.read_namespaced_endpoints(
                service_name, self.namespace)

            instances = []
            for subset in endpoints.subsets:
                for address in subset.addresses:
                    for port in subset.ports:
                        instance = ServiceInstance(
                            id=f"{service_name}-{address.ip}",
                            name=service_name,
                            host=address.ip,
                            port=port.port,
                            protocol="http" if port.name == "http" else "https",
                        )
                        instances.append(instance)

            return instances

        except client.ApiException as e:
            logger.error(f"❌ Kubernetes API error: {e}")
            return []

    async def watch_service(
            self,
            service_name: str,
            callback: Callable) -> None:
        """Watch service changes in Kubernetes"""
        if service_name in self.watchers:
            return

        def watch_callback(event):
            asyncio.create_task(callback(event))

        watcher = client.Watch()
        self.watchers[service_name] = watcher

        # Start watching
        for event in watcher.stream(
            self.v1.list_namespaced_endpoints,
            namespace=self.namespace,
            field_selector=f"metadata.name={service_name}",
        ):
            watch_callback(event)


class LoadBalancer(ILoadBalancer):
    """Load balancer implementation"""

    def __init__(self):
        self.instance_states: Dict[str, Dict[str, Any]] = {}
        self.round_robin_indexes: Dict[str, int] = {}
        self._strategy_map = {
            LoadBalancingStrategy.ROUND_ROBIN: self._round_robin,
            LoadBalancingStrategy.LEAST_CONNECTIONS: self._least_connections,
            LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN: self._weighted_round_robin,
            LoadBalancingStrategy.IP_HASH: self._ip_hash,
            LoadBalancingStrategy.RANDOM: self._random,
        }

    async def select_instance(
        self, service_name: str, strategy: LoadBalancingStrategy
    ) -> Optional[ServiceInstance]:
        """Select service instance based on strategy"""
        # Get service instances
        service = await self._get_service_instances(service_name)
        if not service or not service.instances:
            logger.warning(f"No instances found for service: {service_name}")
            return None

        healthy_instances = [
            i for i in service.instances if i.status == ServiceStatus.HEALTHY
        ]
        if not healthy_instances:
            logger.warning(
                f"No healthy instances available for service: {service_name}"
            )
            return None

        balancing_func = self._strategy_map.get(strategy)

        if balancing_func:
            if strategy in [
                LoadBalancingStrategy.ROUND_ROBIN,
                LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN,
            ]:
                return balancing_func(service_name, healthy_instances)
            return balancing_func(healthy_instances)

        # Fallback for unknown strategies
        logger.warning(
            f"Unknown load balancing strategy: {strategy}. Falling back to default."
        )
        return healthy_instances[0]

    async def update_instance_status(
        self, instance_id: str, status: ServiceStatus
    ) -> None:
        """Update instance status"""
        if instance_id not in self.instance_states:
            self.instance_states[instance_id] = {}

        self.instance_states[instance_id]["status"] = status
        self.instance_states[instance_id]["last_updated"] = datetime.now(
            timezone.utc)

    def _round_robin(
        self, service_name: str, instances: List[ServiceInstance]
    ) -> ServiceInstance:
        """Round robin selection"""
        if service_name not in self.round_robin_indexes:
            self.round_robin_indexes[service_name] = 0

        instance = instances[self.round_robin_indexes[service_name] % len(
            instances)]
        self.round_robin_indexes[service_name] += 1

        return instance

    def _least_connections(
            self,
            instances: List[ServiceInstance]) -> ServiceInstance:
        """Least connections selection"""
        return min(
            instances,
            key=lambda i: i.metadata.get(
                "active_connections",
                0))

    def _weighted_round_robin(
        self, service_name: str, instances: List[ServiceInstance]
    ) -> ServiceInstance:
        """Weighted round robin selection"""
        # Create weighted list
        weighted_instances = []
        for instance in instances:
            weight = instance.weight
            weighted_instances.extend([instance] * weight)

        if not weighted_instances:
            return instances[0]

        # Round robin on weighted list
        if service_name not in self.round_robin_indexes:
            self.round_robin_indexes[service_name] = 0

        instance = weighted_instances[
            self.round_robin_indexes[service_name] % len(weighted_instances)
        ]
        self.round_robin_indexes[service_name] += 1

        return instance

    def _ip_hash(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """IP hash selection"""
        # This would use the client IP, for now use random
        import hashlib

        client_ip = "127.0.0.1"  # Get from request context
        hash_value = int(hashlib.md5(client_ip.encode()).hexdigest(), 16)
        return instances[hash_value % len(instances)]

    def _random(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Random selection"""
        return random.choice(instances)

    async def _get_service_instances(
        self, service_name: str
    ) -> Optional[ServiceDefinition]:
        """Get service instances (to be implemented with service discovery)"""
        # This would integrate with service discovery
        return None


class HealthChecker(IHealthChecker):
    """Health checker implementation"""

    def __init__(self):
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}
        self.health_results: Dict[str, Dict[str, ServiceStatus]] = {}

    async def check_health(self, instance: ServiceInstance) -> ServiceStatus:
        """Check instance health"""
        if not instance.health_check_url:
            return ServiceStatus.UNKNOWN

        try:
            async with aiohttp.ClientSession() as session:
                start_time = time.time()

                async with session.get(
                    instance.health_check_url, timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    response_time = time.time() - start_time

                    if response.status == 200:
                        instance.status = ServiceStatus.HEALTHY
                        instance.response_time = response_time
                        instance.success_count += 1
                        return ServiceStatus.HEALTHY
                    else:
                        instance.status = ServiceStatus.UNHEALTHY
                        instance.error_count += 1
                        return ServiceStatus.UNHEALTHY

        except Exception as e:
            instance.status = ServiceStatus.UNHEALTHY
            instance.error_count += 1
            logger.warning(f"⚠️ Health check failed for {instance.id}: {e}")
            return ServiceStatus.UNHEALTHY

    async def start_monitoring(self, service: ServiceDefinition) -> None:
        """Start health monitoring"""
        if service.name in self.monitoring_tasks:
            return

        async def monitor_health():
            while True:
                try:
                    for instance in service.instances:
                        status = await self.check_health(instance)

                        # Store result
                        if service.name not in self.health_results:
                            self.health_results[service.name] = {}
                        self.health_results[service.name][instance.id] = status

                        instance.last_health_check = datetime.now(timezone.utc)

                    await asyncio.sleep(service.health_check_interval)

                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(
                        f"❌ Health monitoring error for {service.name}: {e}")
                    await asyncio.sleep(service.health_check_interval)

        task = asyncio.create_task(monitor_health())
        self.monitoring_tasks[service.name] = task
        logger.info(f"🔍 Started health monitoring for {service.name}")

    async def stop_monitoring(self, service_name: str) -> None:
        """Stop health monitoring"""
        if service_name in self.monitoring_tasks:
            task = self.monitoring_tasks[service_name]
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

            del self.monitoring_tasks[service_name]
            logger.info(f"🛑 Stopped health monitoring for {service_name}")


class CircuitBreaker:
    """Circuit breaker implementation"""

    def __init__(self, threshold: int = 5, timeout: int = 60):
        self.threshold = threshold
        self.timeout = timeout
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker"""
        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e

    def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0
        self.state = CircuitBreakerState.CLOSED

    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.now(timezone.utc)

        if self.failure_count >= self.threshold:
            self.state = CircuitBreakerState.OPEN

    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt reset"""
        if not self.last_failure_time:
            return True

        time_since_failure = (
            datetime.now(timezone.utc) - self.last_failure_time
        ).total_seconds()
        return time_since_failure >= self.timeout


class ServiceOrchestrator:
    """Main service orchestrator"""

    def __init__(
        self,
        registry: IServiceRegistry,
        discovery: IServiceDiscovery,
        load_balancer: ILoadBalancer,
        health_checker: IHealthChecker,
    ):
        self.registry = registry
        self.discovery = discovery
        self.load_balancer = load_balancer
        self.health_checker = health_checker
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.services: Dict[str, ServiceDefinition] = {}

    async def register_service(self, service: ServiceDefinition) -> None:
        """Register service"""
        await self.registry.register_service(service)
        self.services[service.name] = service

        # Start health monitoring
        await self.health_checker.start_monitoring(service)

        # Create circuit breaker
        self.circuit_breakers[service.name] = CircuitBreaker(
            threshold=service.circuit_breaker_threshold,
            timeout=service.circuit_breaker_timeout,
        )

    async def call_service(
        self,
        service_name: str,
        method: str,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        """Call service with load balancing and circuit breaker"""
        # Get service instance
        service = self.services.get(service_name)
        if not service:
            raise ValueError(f"Service {service_name} not found")

        # Select instance
        instance = await self.load_balancer.select_instance(
            service_name, service.load_balancing_strategy
        )
        if not instance:
            raise Exception(
                f"No healthy instances available for {service_name}")

        # Get circuit breaker
        circuit_breaker = self.circuit_breakers[service_name]

        # Make request
        async def make_request():
            url = f"{instance.protocol}://{instance.host}:{instance.port}{path}"

            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method, url, json=data, headers=headers, timeout=service.timeout
                ) as response:
                    response.raise_for_status()
                    return await response.json()

        return await circuit_breaker.call(make_request)

    async def get_service_health(self, service_name: str) -> Dict[str, Any]:
        """Get service health status"""
        service = self.services.get(service_name)
        if not service:
            return {"status": "not_found"}

        health_status = {
            "service_name": service_name,
            "total_instances": len(service.instances),
            "healthy_instances": len(
                [i for i in service.instances if i.status == ServiceStatus.HEALTHY]
            ),
            "unhealthy_instances": len(
                [i for i in service.instances if i.status == ServiceStatus.UNHEALTHY]
            ),
            "circuit_breaker_state": self.circuit_breakers[service_name].state.value,
            "instances": [],
        }

        for instance in service.instances:
            instance_status = {
                "id": instance.id,
                "host": instance.host,
                "port": instance.port,
                "status": instance.status.value,
                "response_time": instance.response_time,
                "error_count": instance.error_count,
                "success_count": instance.success_count,
                "last_health_check": (
                    instance.last_health_check.isoformat()
                    if instance.last_health_check
                    else None
                ),
            }
            health_status["instances"].append(instance_status)

        return health_status


# Factory functions
def create_consul_registry(
    consul_host: str = "localhost", consul_port: int = 8500
) -> IServiceRegistry:
    """Create Consul service registry"""
    return ConsulServiceRegistry(consul_host, consul_port)


def create_kubernetes_discovery(
        namespace: str = "default") -> IServiceDiscovery:
    """Create Kubernetes service discovery"""
    return KubernetesServiceDiscovery(namespace)


def create_load_balancer() -> ILoadBalancer:
    """Create load balancer"""
    return LoadBalancer()


def create_health_checker() -> IHealthChecker:
    """Create health checker"""
    return HealthChecker()


def create_service_orchestrator(
    registry: IServiceRegistry,
    discovery: IServiceDiscovery,
    load_balancer: ILoadBalancer,
    health_checker: IHealthChecker,
) -> ServiceOrchestrator:
    """Create service orchestrator"""
    return ServiceOrchestrator(
        registry,
        discovery,
        load_balancer,
        health_checker)


# Utility functions
def create_service_instance(
    id: str, name: str, host: str, port: int, protocol: str = "http", **kwargs
) -> ServiceInstance:
    """Create service instance"""
    return ServiceInstance(
        id=id, name=name, host=host, port=port, protocol=protocol, **kwargs
    )


def create_service_definition(
    name: str, version: str, instances: List[ServiceInstance], **kwargs
) -> ServiceDefinition:
    """Create service definition"""
    return ServiceDefinition(
        name=name,
        version=version,
        instances=instances,
        **kwargs)
