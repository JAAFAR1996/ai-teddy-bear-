"""
Load balancer implementation with multiple strategies.
"""
import hashlib
import logging
import random
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .interfaces import ILoadBalancer, IServiceDiscovery
from .models import LoadBalancingStrategy, ServiceInstance, ServiceStatus

logger = logging.getLogger(__name__)


class LoadBalancer(ILoadBalancer):
    """Load balancer implementation"""

    def __init__(self, discovery: IServiceDiscovery):
        self.discovery = discovery
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
        self, service_name: str, strategy: LoadBalancingStrategy, client_ip: Optional[str] = None
    ) -> Optional[ServiceInstance]:
        """Select service instance based on strategy"""
        instances = await self.discovery.discover_services(service_name)
        if not instances:
            logger.warning(f"No instances found for service: {service_name}")
            return None

        healthy_instances = [
            i for i in instances if i.status == ServiceStatus.HEALTHY]
        if not healthy_instances:
            logger.warning(
                f"No healthy instances available for service: {service_name}")
            return None

        balancing_func = self._strategy_map.get(strategy)
        if not balancing_func:
            logger.warning(
                f"Unknown load balancing strategy: {strategy}. Falling back to random.")
            return self._random(healthy_instances)

        if strategy == LoadBalancingStrategy.IP_HASH:
            return balancing_func(healthy_instances, client_ip=client_ip)
        elif strategy in [LoadBalancingStrategy.ROUND_ROBIN, LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN]:
            return balancing_func(service_name, healthy_instances)

        return balancing_func(healthy_instances)

    async def update_instance_status(self, instance_id: str, status: ServiceStatus) -> None:
        """Update instance status"""
        if instance_id not in self.instance_states:
            self.instance_states[instance_id] = {}

        self.instance_states[instance_id]["status"] = status
        self.instance_states[instance_id]["last_updated"] = datetime.now(
            timezone.utc)
        logger.debug(
            f"Updated status for instance {instance_id} to {status.name}")

    def _round_robin(self, service_name: str, instances: List[ServiceInstance]) -> ServiceInstance:
        """Round robin selection"""
        if service_name not in self.round_robin_indexes:
            self.round_robin_indexes[service_name] = 0

        index = self.round_robin_indexes[service_name] % len(instances)
        instance = instances[index]
        self.round_robin_indexes[service_name] += 1

        return instance

    def _least_connections(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Least connections selection"""
        return min(instances, key=lambda i: i.metadata.get("active_connections", 0))

    def _weighted_round_robin(
        self, service_name: str, instances: List[ServiceInstance]
    ) -> ServiceInstance:
        """Weighted round robin selection"""
        weighted_instances = []
        for instance in instances:
            weight = instance.weight if instance.weight > 0 else 1
            weighted_instances.extend([instance] * weight)

        if not weighted_instances:
            return self._random(instances)

        return self._round_robin(service_name, weighted_instances)

    def _ip_hash(self, instances: List[ServiceInstance], client_ip: Optional[str] = None) -> ServiceInstance:
        """IP hash selection"""
        if not client_ip:
            logger.warning(
                "IP Hash strategy requires client_ip, falling back to random.")
            return self._random(instances)

        hash_value = int(hashlib.md5(client_ip.encode()).hexdigest(), 16)
        return instances[hash_value % len(instances)]

    def _random(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Random selection"""
        return random.choice(instances)
