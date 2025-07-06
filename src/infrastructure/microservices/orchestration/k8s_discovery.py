"""
Kubernetes-based service discovery implementation.
"""
import asyncio
import logging
from typing import Callable, Dict, List

from kubernetes import client, config

from .interfaces import IServiceDiscovery
from .models import ServiceInstance

logger = logging.getLogger(__name__)


class KubernetesServiceDiscovery(IServiceDiscovery):
    """Kubernetes-based service discovery"""

    def __init__(self, namespace: str = "default"):
        try:
            config.load_incluster_config()
            logger.info("Loaded in-cluster Kubernetes config.")
        except config.ConfigException:
            try:
                config.load_kube_config()
                logger.info("Loaded local Kubernetes config.")
            except config.ConfigException as e:
                logger.error(
                    f"Could not configure Kubernetes client: {e}", exc_info=True)
                raise

        self.namespace = namespace
        self.v1 = client.CoreV1Api()
        self.watchers: Dict[str, client.Watch] = {}

    async def discover_services(self, service_name: str) -> List[ServiceInstance]:
        """Discover service instances in Kubernetes"""
        try:
            endpoints = self.v1.read_namespaced_endpoints(
                service_name, self.namespace)

            instances = []
            if endpoints.subsets:
                for subset in endpoints.subsets:
                    for address in subset.addresses:
                        for port in subset.ports:
                            instance = ServiceInstance(
                                id=f"{service_name}-{address.ip}-{port.port}",
                                name=service_name,
                                host=address.ip,
                                port=port.port,
                                protocol="https" if port.name == "https" else "http",
                            )
                            instances.append(instance)

            logger.info(
                f"Discovered {len(instances)} instances for service '{service_name}' in namespace '{self.namespace}'.")
            return instances

        except client.ApiException as e:
            logger.error(
                f"❌ Kubernetes API error while discovering '{service_name}': {e}",
                exc_info=True
            )
            return []

    async def watch_service(self, service_name: str, callback: Callable) -> None:
        """Watch service changes in Kubernetes"""
        if service_name in self.watchers:
            logger.warning(
                f"Watcher for service '{service_name}' already exists.")
            return

        def watch_task():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            watcher = client.Watch()
            self.watchers[service_name] = watcher
            logger.info(f"Starting to watch service '{service_name}'.")

            try:
                for event in watcher.stream(
                    self.v1.list_namespaced_endpoints,
                    namespace=self.namespace,
                    field_selector=f"metadata.name={service_name}",
                ):
                    asyncio.run_coroutine_threadsafe(
                        callback(event), asyncio.get_event_loop())
            except client.ApiException as e:
                logger.error(
                    f"Watcher for '{service_name}' failed: {e}", exc_info=True)
            except Exception as e:
                logger.error(
                    f"Unexpected error in watcher for '{service_name}': {e}", exc_info=True)
            finally:
                if service_name in self.watchers:
                    del self.watchers[service_name]
                logger.info(f"Stopped watching service '{service_name}'.")

        # Running the watcher in a separate thread to avoid blocking
        asyncio.to_thread(watch_task)
