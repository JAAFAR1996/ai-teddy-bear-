"""
Microservices Orchestrator
This module provides the main ServiceOrchestrator class that integrates
service discovery, load balancing, health monitoring, and circuit breaking.
"""

import logging
from typing import Any, Dict, Optional

import aiohttp

from .orchestration import (
    CircuitBreaker,
    IHealthChecker,
    ILoadBalancer,
    IServiceDiscovery,
    IServiceRegistry,
    ServiceDefinition,
    ServiceStatus,
)

logger = logging.getLogger(__name__)


class ServiceOrchestrator:
    """Main service orchestrator, tying all components together."""

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
        """
        Registers a new service with the orchestrator, starts health monitoring,
        and sets up a circuit breaker for it.
        """
        await self.registry.register_service(service)
        self.services[service.name] = service

        # Start health monitoring
        await self.health_checker.start_monitoring(service)

        # Create circuit breaker
        self.circuit_breakers[service.name] = CircuitBreaker(
            threshold=service.circuit_breaker_threshold,
            timeout=service.circuit_breaker_timeout,
        )
        logger.info(
            f"Successfully registered and configured service: {service.name}")

    async def call_service(
        self,
        service_name: str,
        method: str,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        client_ip: Optional[str] = None,
    ) -> Any:
        """
        Calls a service using the configured load balancer and circuit breaker.
        Retries the call if it fails, up to the configured number of attempts.
        """
        service = self.services.get(service_name)
        if not service:
            logger.error(
                f"Attempted to call non-existent service: {service_name}")
            raise ValueError(f"Service {service_name} not found")

        circuit_breaker = self.circuit_breakers[service_name]

        last_exception = None
        for attempt in range(service.retry_attempts + 1):
            try:
                instance = await self.load_balancer.select_instance(
                    service_name, service.load_balancing_strategy, client_ip=client_ip
                )
                if not instance:
                    raise Exception(
                        f"No healthy instances available for {service_name}")

                async def make_request():
                    url = f"{instance.protocol}://{instance.host}:{instance.port}{path}"
                    timeout = aiohttp.ClientTimeout(total=service.timeout)
                    async with aiohttp.ClientSession() as session:
                        async with session.request(
                            method.upper(), url, json=data, headers=headers, timeout=timeout
                        ) as response:
                            response.raise_for_status()
                            return await response.json()

                return await circuit_breaker.call(make_request)

            except Exception as e:
                last_exception = e
                logger.warning(
                    f"Attempt {attempt + 1} failed for service {service_name}: {e}. Retrying..."
                )

        logger.error(
            f"All {service.retry_attempts + 1} attempts to call service {service_name} failed.")
        raise last_exception

    async def get_service_health(self, service_name: str) -> Dict[str, Any]:
        """Get detailed health status for a specific service."""
        service = self.services.get(service_name)
        if not service:
            return {"status": "not_found", "message": f"Service {service_name} not found."}

        healthy_instances = [
            i for i in service.instances if i.status == ServiceStatus.HEALTHY]
        unhealthy_instances = [
            i for i in service.instances if i.status == ServiceStatus.UNHEALTHY]

        circuit_breaker_state = self.circuit_breakers.get(service_name)

        health_status = {
            "service_name": service_name,
            "total_instances": len(service.instances),
            "healthy_instances": len(healthy_instances),
            "unhealthy_instances": len(unhealthy_instances),
            "circuit_breaker_state": circuit_breaker_state.state.value if circuit_breaker_state else "unknown",
            "instances": [
                {
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
                for instance in service.instances
            ],
        }

        return health_status


def create_service_orchestrator(
    registry: IServiceRegistry,
    discovery: IServiceDiscovery,
    load_balancer: ILoadBalancer,
    health_checker: IHealthChecker,
) -> ServiceOrchestrator:
    """Factory function to create a fully configured ServiceOrchestrator."""
    return ServiceOrchestrator(
        registry,
        discovery,
        load_balancer,
        health_checker)
