#!/usr/bin/env python3
"""
🏥 Health Checker System
Lead Architect: جعفر أديب (Jaafar Adeeb)
Comprehensive health monitoring for all application services
"""

import asyncio
import time
from typing import Dict, Any, List, Optional
import structlog
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = structlog.get_logger()


@dataclass
class HealthStatus:
    """Health status result"""
    healthy: bool
    service: str
    response_time: float
    details: Dict[str, Any]
    timestamp: datetime
    error: Optional[str] = None


class HealthChecker:
    """
    🏗️ Enterprise Health Checker
    Features:
    - Multi-service health monitoring
    - Async health checks with timeouts
    - Dependency health validation
    - Health history tracking
    - Circuit breaker pattern
    """
    
    def __init__(self, container):
        self.container = container
        self.health_history: Dict[str, List[HealthStatus]] = {}
        self.circuit_breakers: Dict[str, Dict[str, Any]] = {}
        self.timeout = 10.0  # Default timeout in seconds
        
        # Health check registry
        self.health_checks = {
            "database": self._check_database_health,
            "vault": self._check_vault_health,
            "redis": self._check_redis_health,
            "messaging": self._check_messaging_health,
            "ai_services": self._check_ai_services_health,
        }
    
    async def check_all(self) -> Dict[str, Dict[str, Any]]:
        """Check health of all registered services"""
        logger.info("🏥 Starting comprehensive health checks...")
        
        results = {}
        
        # Run all health checks concurrently
        tasks = []
        for service_name in self.health_checks:
            task = asyncio.create_task(
                self._run_single_health_check(service_name),
                name=f"health_check_{service_name}"
            )
            tasks.append((service_name, task))
        
        # Wait for all health checks to complete
        for service_name, task in tasks:
            try:
                health_status = await task
                results[service_name] = {
                    "healthy": health_status.healthy,
                    "response_time": health_status.response_time,
                    "details": health_status.details,
                    "timestamp": health_status.timestamp.isoformat(),
                    "error": health_status.error
                }
                
                # Update health history
                self._update_health_history(service_name, health_status)
                
            except Exception as e:
                logger.error(f"Health check failed for {service_name}", error=str(e))
                results[service_name] = {
                    "healthy": False,
                    "response_time": 0.0,
                    "details": {},
                    "timestamp": datetime.utcnow().isoformat(),
                    "error": str(e)
                }
        
        # Calculate overall health
        overall_healthy = all(
            result["healthy"] for result in results.values()
        )
        
        results["overall"] = {
            "healthy": overall_healthy,
            "services_checked": len(results) - 1,
            "healthy_services": sum(1 for r in results.values() if r.get("healthy", False)),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info("✅ Health checks completed", overall_healthy=overall_healthy)
        return results
    
    async def _run_single_health_check(self, service_name: str) -> HealthStatus:
        """Run a single health check with timeout and circuit breaker"""
        
        # Check circuit breaker
        if self._is_circuit_open(service_name):
            return HealthStatus(
                healthy=False,
                service=service_name,
                response_time=0.0,
                details={"circuit_breaker": "open"},
                timestamp=datetime.utcnow(),
                error="Circuit breaker is open"
            )
        
        start_time = time.time()
        
        try:
            # Run health check with timeout
            health_check_func = self.health_checks[service_name]
            health_result = await asyncio.wait_for(
                health_check_func(),
                timeout=self.timeout
            )
            
            response_time = time.time() - start_time
            
            # Reset circuit breaker on success
            self._reset_circuit_breaker(service_name)
            
            return HealthStatus(
                healthy=health_result.get("healthy", False),
                service=service_name,
                response_time=response_time,
                details=health_result,
                timestamp=datetime.utcnow()
            )
            
        except asyncio.TimeoutError:
            response_time = time.time() - start_time
            self._trip_circuit_breaker(service_name)
            
            return HealthStatus(
                healthy=False,
                service=service_name,
                response_time=response_time,
                details={},
                timestamp=datetime.utcnow(),
                error=f"Health check timeout after {self.timeout}s"
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            self._trip_circuit_breaker(service_name)
            
            return HealthStatus(
                healthy=False,
                service=service_name,
                response_time=response_time,
                details={},
                timestamp=datetime.utcnow(),
                error=str(e)
            )
    
    async def _check_database_health(self) -> Dict[str, Any]:
        """Check database health"""
        try:
            database = self.container.database()
            return await database.health_check()
        except Exception as e:
            return {"healthy": False, "error": str(e)}
    
    async def _check_vault_health(self) -> Dict[str, Any]:
        """Check Vault health"""
        try:
            vault_client = self.container.vault_client()
            return await vault_client.health_check()
        except Exception as e:
            return {"healthy": False, "error": str(e)}
    
    async def _check_redis_health(self) -> Dict[str, Any]:
        """Check Redis health"""
        try:
            redis_client = self.container.redis_client()
            return await redis_client.health_check()
        except Exception as e:
            return {"healthy": False, "error": str(e)}
    
    async def _check_messaging_health(self) -> Dict[str, Any]:
        """Check message broker health"""
        try:
            message_broker = self.container.message_broker()
            return await message_broker.health_check()
        except Exception as e:
            return {"healthy": False, "error": str(e)}
    
    async def _check_ai_services_health(self) -> Dict[str, Any]:
        """Check AI services health"""
        try:
            ai_service = self.container.ai_service()
            return await ai_service.health_check()
        except Exception as e:
            return {"healthy": False, "error": str(e)}
    
    def _is_circuit_open(self, service_name: str) -> bool:
        """Check if circuit breaker is open"""
        if service_name not in self.circuit_breakers:
            return False
        
        circuit = self.circuit_breakers[service_name]
        if circuit.get("state") != "open":
            return False
        
        # Check if circuit should be half-open
        if datetime.utcnow() > circuit.get("next_attempt", datetime.min):
            circuit["state"] = "half_open"
            return False
        
        return True
    
    def _trip_circuit_breaker(self, service_name: str):
        """Trip circuit breaker for a service"""
        if service_name not in self.circuit_breakers:
            self.circuit_breakers[service_name] = {
                "failure_count": 0,
                "state": "closed"
            }
        
        circuit = self.circuit_breakers[service_name]
        circuit["failure_count"] += 1
        
        # Trip circuit after 3 failures
        if circuit["failure_count"] >= 3:
            circuit["state"] = "open"
            circuit["next_attempt"] = datetime.utcnow() + timedelta(minutes=5)
            logger.warning(f"Circuit breaker opened for {service_name}")
    
    def _reset_circuit_breaker(self, service_name: str):
        """Reset circuit breaker for a service"""
        if service_name in self.circuit_breakers:
            self.circuit_breakers[service_name] = {
                "failure_count": 0,
                "state": "closed"
            }
    
    def _update_health_history(self, service_name: str, health_status: HealthStatus):
        """Update health history for a service"""
        if service_name not in self.health_history:
            self.health_history[service_name] = []
        
        self.health_history[service_name].append(health_status)
        
        # Keep only last 100 health checks
        if len(self.health_history[service_name]) > 100:
            self.health_history[service_name] = self.health_history[service_name][-100:]
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get health summary and statistics"""
        summary = {
            "total_services": len(self.health_checks),
            "circuit_breakers": {},
            "health_trends": {}
        }
        
        # Circuit breaker status
        for service_name, circuit in self.circuit_breakers.items():
            summary["circuit_breakers"][service_name] = {
                "state": circuit.get("state", "closed"),
                "failure_count": circuit.get("failure_count", 0)
            }
        
        # Health trends
        for service_name, history in self.health_history.items():
            if history:
                recent_checks = history[-10:]  # Last 10 checks
                healthy_count = sum(1 for check in recent_checks if check.healthy)
                
                summary["health_trends"][service_name] = {
                    "recent_success_rate": healthy_count / len(recent_checks),
                    "average_response_time": sum(check.response_time for check in recent_checks) / len(recent_checks),
                    "last_check": recent_checks[-1].timestamp.isoformat()
                }
        
        return summary 