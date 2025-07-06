"""
Consul-based service registry implementation.
"""
import logging
from typing import Dict, List, Optional

import consul

from .interfaces import IServiceRegistry
from .models import ServiceDefinition, ServiceInstance

logger = logging.getLogger(__name__)


class ConsulServiceRegistry(IServiceRegistry):
    """Consul-based service registry"""

    def __init__(self, consul_host: str = "localhost", consul_port: int = 8500):
        self.consul = consul.Consul(host=consul_host, port=consul_port)
        self.services: Dict[str, ServiceDefinition] = {}

    async def register_service(self, service: ServiceDefinition) -> None:
        """Register service with Consul"""
        for instance in service.instances:
            service_id = f"{service.name}-{instance.id}"

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

            self.consul.agent.service.register(**registration)

        self.services[service.name] = service
        logger.info(
            f"📝 Registered service {service.name} with {len(service.instances)} instances"
        )

    async def deregister_service(self, service_name: str) -> None:
        """Deregister service from Consul"""
        if service_name not in self.services:
            logger.warning(
                f"Attempted to deregister non-existent service: {service_name}")
            return

        service = self.services[service_name]

        for instance in service.instances:
            service_id = f"{service.name}-{instance.id}"
            self.consul.agent.service.deregister(service_id)

        del self.services[service_name]
        logger.info(f"🗑️ Deregistered service {service_name}")

    async def get_service(self, service_name: str) -> Optional[ServiceDefinition]:
        """Get service from Consul"""
        if service_name in self.services:
            return self.services[service_name]

        _, services = self.consul.health.service(service_name, passing=True)

        if not services:
            return None

        instances = []
        for service_info in services:
            service_data = service_info["Service"]
            instance = ServiceInstance(
                id=service_data["ID"],
                name=service_data["Service"],
                host=service_data["Address"],
                port=service_data["Port"],
                tags=set(service_data.get("Tags", [])),
                metadata=service_data.get("Meta", {}),
            )
            instances.append(instance)

        service_def = ServiceDefinition(
            name=service_name, version="v1", instances=instances)  # Assuming version
        self.services[service_name] = service_def
        return service_def

    async def list_services(self) -> List[ServiceDefinition]:
        """List all services from Consul"""
        _, services_dict = self.consul.catalog.services()

        service_definitions = []
        for service_name in services_dict:
            service = await self.get_service(service_name)
            if service:
                service_definitions.append(service)

        return service_definitions
