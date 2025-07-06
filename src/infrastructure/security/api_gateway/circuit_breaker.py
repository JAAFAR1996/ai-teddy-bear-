"""
Circuit breaker component for the API Gateway.
"""
import logging
import time
from typing import Any, Dict

logger = logging.getLogger(__name__)


class CircuitBreakerMixin:
    """
    A mixin providing circuit breaker functionality to prevent repeated calls
    to failing upstream services.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.circuit_breakers: Dict[str, Dict[str, Any]] = {}

    async def check_circuit_breaker(self, request) -> bool:
        """
        Checks the status of the circuit breaker for the requested service.
        Returns False if the circuit is open, True otherwise.
        """
        service_key = self._get_service_key(request)
        breaker = self.circuit_breakers.setdefault(service_key, {
            "state": "closed",  # closed, open, half_open
            "failure_count": 0,
            "success_count": 0,
            "last_failure_time": None,
        })

        if breaker["state"] == "open":
            if time.time() - breaker["last_failure_time"] > 60:  # 60-second timeout
                breaker["state"] = "half_open"
                breaker["success_count"] = 0
                logger.info(
                    f"Circuit breaker for '{service_key}' is now half-open.")
                return True
            return False
        return True

    async def on_request_success(self, request):
        """Records a successful request for the circuit breaker."""
        service_key = self._get_service_key(request)
        if service_key in self.circuit_breakers:
            breaker = self.circuit_breakers[service_key]
            if breaker["state"] == "half_open":
                breaker["success_count"] += 1
                if breaker["success_count"] >= 3:  # Require 3 successes to close
                    breaker["state"] = "closed"
                    breaker["failure_count"] = 0
                    logger.info(
                        f"Circuit breaker for '{service_key}' has been closed.")

    async def on_request_failure(self, request):
        """Records a failed request and updates the circuit breaker state if necessary."""
        service_key = self._get_service_key(request)
        if service_key in self.circuit_breakers:
            breaker = self.circuit_breakers[service_key]
            breaker["failure_count"] += 1
            breaker["last_failure_time"] = time.time()

            if breaker["state"] == "half_open" or breaker["failure_count"] >= 5:
                breaker["state"] = "open"
                logger.warning(
                    f"Circuit breaker for '{service_key}' has been opened.")

    # Placeholder that the main gateway class will implement
    def _get_service_key(self, request) -> str: raise NotImplementedError
