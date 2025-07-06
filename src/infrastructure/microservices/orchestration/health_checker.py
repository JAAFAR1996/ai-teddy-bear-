"""
Health checker implementation for monitoring service instances.
"""
import asyncio
import logging
import time
from datetime import datetime, timezone
from typing import Dict

import aiohttp

from .interfaces import IHealthChecker
from .models import ServiceDefinition, ServiceInstance, ServiceStatus

logger = logging.getLogger(__name__)


class HealthChecker(IHealthChecker):
    """Health checker implementation"""

    def __init__(self, load_balancer):
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}
        self.health_results: Dict[str, Dict[str, ServiceStatus]] = {}
        self.load_balancer = load_balancer

    async def check_health(self, instance: ServiceInstance) -> ServiceStatus:
        """Check instance health via its health check URL."""
        if not instance.health_check_url:
            logger.debug(
                f"Instance {instance.id} has no health check URL. Status is UNKNOWN.")
            return ServiceStatus.UNKNOWN

        try:
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                timeout = aiohttp.ClientTimeout(total=5)

                async with session.get(instance.health_check_url, timeout=timeout) as response:
                    response_time = time.time() - start_time

                    if response.status >= 200 and response.status < 300:
                        new_status = ServiceStatus.HEALTHY
                        instance.success_count += 1
                    else:
                        new_status = ServiceStatus.UNHEALTHY
                        instance.error_count += 1

                    instance.status = new_status
                    instance.response_time = response_time
                    await self.load_balancer.update_instance_status(instance.id, new_status)

                    return new_status

        except asyncio.TimeoutError:
            logger.warning(f"⚠️ Health check timed out for {instance.id}")
            instance.status = ServiceStatus.UNHEALTHY
            instance.error_count += 1
            await self.load_balancer.update_instance_status(instance.id, ServiceStatus.UNHEALTHY)
            return ServiceStatus.UNHEALTHY
        except aiohttp.ClientError as e:
            logger.warning(
                f"⚠️ Health check client error for {instance.id}: {e}")
            instance.status = ServiceStatus.UNHEALTHY
            instance.error_count += 1
            await self.load_balancer.update_instance_status(instance.id, ServiceStatus.UNHEALTHY)
            return ServiceStatus.UNHEALTHY
        except Exception as e:
            logger.error(
                f"❌ Unexpected health check error for {instance.id}: {e}", exc_info=True)
            instance.status = ServiceStatus.UNHEALTHY
            instance.error_count += 1
            await self.load_balancer.update_instance_status(instance.id, ServiceStatus.UNHEALTHY)
            return ServiceStatus.UNHEALTHY

    async def start_monitoring(self, service: ServiceDefinition) -> None:
        """Start periodic health monitoring for all instances of a service."""
        if service.name in self.monitoring_tasks:
            logger.info(
                f"Health monitoring for {service.name} is already running.")
            return

        async def monitor_health():
            logger.info(
                f"🔍 Starting health monitoring loop for {service.name}")
            while True:
                try:
                    tasks = [self.check_health(instance)
                             for instance in service.instances]
                    results = await asyncio.gather(*tasks, return_exceptions=True)

                    for i, result in enumerate(results):
                        instance_id = service.instances[i].id
                        if isinstance(result, ServiceStatus):
                            if service.name not in self.health_results:
                                self.health_results[service.name] = {}
                            self.health_results[service.name][instance_id] = result
                            service.instances[i].last_health_check = datetime.now(
                                timezone.utc)
                        else:
                            logger.error(
                                f"Error checking health for {instance_id}: {result}", exc_info=result)

                    await asyncio.sleep(service.health_check_interval)

                except asyncio.CancelledError:
                    logger.info(
                        f"Health monitoring for {service.name} was cancelled.")
                    break
                except Exception as e:
                    logger.error(
                        f"❌ Unhandled error in health monitoring for {service.name}: {e}", exc_info=True)
                    # Wait before retrying
                    await asyncio.sleep(service.health_check_interval)

        task = asyncio.create_task(monitor_health())
        self.monitoring_tasks[service.name] = task
        logger.info(f"Registered health monitoring task for {service.name}")

    async def stop_monitoring(self, service_name: str) -> None:
        """Stop health monitoring for a service."""
        if service_name in self.monitoring_tasks:
            task = self.monitoring_tasks[service_name]
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass  # Expected

            del self.monitoring_tasks[service_name]
            logger.info(f"🛑 Stopped health monitoring for {service_name}")
        else:
            logger.warning(
                f"No health monitoring task found for service {service_name} to stop.")
