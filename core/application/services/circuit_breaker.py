"""
Circuit Breaker Pattern Implementation
Provides fault tolerance and prevents cascading failures
"""

import asyncio
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, List, Optional

import structlog

logger = structlog.get_logger()


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject calls
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""
    failure_threshold: int = 5
    success_threshold: int = 2
    recovery_timeout: float = 60.0  # seconds
    half_open_max_calls: int = 3
    excluded_exceptions: tuple = ()
    name: Optional[str] = None


@dataclass
class CircuitBreakerStats:
    """Circuit breaker statistics"""
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[float] = None
    last_success_time: Optional[float] = None
    total_calls: int = 0
    total_failures: int = 0
    total_successes: int = 0
    state_changes: List[Dict[str, Any]] = field(default_factory=list)


class CircuitBreakerError(Exception):
    """Raised when circuit breaker is open"""
    pass


class CircuitBreaker:
    """
    Circuit breaker implementation with async support
    
    Example:
        cb = CircuitBreaker(failure_threshold=5, recovery_timeout=60)
        
        @cb
        async def risky_operation():
            return await external_service.call()
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        success_threshold: int = 2,
        recovery_timeout: float = 60.0,
        half_open_max_calls: int = 3,
        excluded_exceptions: tuple = (),
        name: Optional[str] = None
    ):
        self.config = CircuitBreakerConfig(
            failure_threshold=failure_threshold,
            success_threshold=success_threshold,
            recovery_timeout=recovery_timeout,
            half_open_max_calls=half_open_max_calls,
            excluded_exceptions=excluded_exceptions,
            name=name
        )
        
        self._state = CircuitState.CLOSED
        self._stats = CircuitBreakerStats()
        self._half_open_calls = 0
        self._lock = asyncio.Lock()
        self._state_change_callbacks: List[Callable] = []
    
    @property
    def state(self) -> CircuitState:
        """Current circuit state"""
        return self._state
    
    @property
    def stats(self) -> CircuitBreakerStats:
        """Circuit breaker statistics"""
        return self._stats
    
    @property
    def is_closed(self) -> bool:
        """Check if circuit is closed (normal operation)"""
        return self._state == CircuitState.CLOSED
    
    @property
    def is_open(self) -> bool:
        """Check if circuit is open (rejecting calls)"""
        return self._state == CircuitState.OPEN
    
    @property
    def is_half_open(self) -> bool:
        """Check if circuit is half-open (testing recovery)"""
        return self._state == CircuitState.HALF_OPEN
    
    def add_state_change_callback(self, callback: Callable) -> None:
        """Add callback for state changes"""
        self._state_change_callbacks.append(callback)
    
    async def _change_state(self, new_state: CircuitState) -> None:
        """Change circuit state and notify callbacks"""
        if self._state == new_state:
            return
        
        old_state = self._state
        self._state = new_state
        
        # Record state change
        self._stats.state_changes.append({
            "from": old_state.value,
            "to": new_state.value,
            "timestamp": datetime.utcnow().isoformat(),
            "stats": {
                "failures": self._stats.failure_count,
                "successes": self._stats.success_count,
                "total_calls": self._stats.total_calls
            }
        })
        
        logger.info(
            "Circuit breaker state changed",
            name=self.config.name,
            from_state=old_state.value,
            to_state=new_state.value
        )
        
        # Notify callbacks
        for callback in self._state_change_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(old_state, new_state)
                else:
                    callback(old_state, new_state)
            except Exception as e:
                logger.error("State change callback failed", error=str(e))
    
    async def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self._stats.last_failure_time is None:
            return False
        
        return time.time() - self._stats.last_failure_time >= self.config.recovery_timeout
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection
        """
        async with self._lock:
            # Check if we should transition from OPEN to HALF_OPEN
            if self.is_open and await self._should_attempt_reset():
                await self._change_state(CircuitState.HALF_OPEN)
                self._half_open_calls = 0
                self._stats.success_count = 0
                self._stats.failure_count = 0
            
            # Reject if circuit is open
            if self.is_open:
                raise CircuitBreakerError(
                    f"Circuit breaker is OPEN (name={self.config.name})"
                )
            
            # Check half-open call limit
            if self.is_half_open and self._half_open_calls >= self.config.half_open_max_calls:
                raise CircuitBreakerError(
                    f"Circuit breaker half-open call limit reached (name={self.config.name})"
                )
        
        # Execute function
        start_time = time.time()
        try:
            if self.is_half_open:
                self._half_open_calls += 1
            
            # Call function
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            # Record success
            await self._on_success()
            
            return result
            
        except Exception as e:
            # Check if exception should be ignored
            if isinstance(e, self.config.excluded_exceptions):
                raise
            
            # Record failure
            await self._on_failure(e)
            
            raise
        
        finally:
            # Update stats
            self._stats.total_calls += 1
            duration = time.time() - start_time
            
            if hasattr(self, '_metrics_recorder'):
                self._metrics_recorder.record_call(
                    self.config.name,
                    self._state.value,
                    duration
                )
    
    async def _on_success(self) -> None:
        """Handle successful call"""
        async with self._lock:
            self._stats.success_count += 1
            self._stats.total_successes += 1
            self._stats.last_success_time = time.time()
            
            if self.is_half_open:
                # Check if we should close the circuit
                if self._stats.success_count >= self.config.success_threshold:
                    await self._change_state(CircuitState.CLOSED)
                    self._stats.failure_count = 0
            
            elif self.is_closed:
                # Reset failure count on success in closed state
                self._stats.failure_count = 0
    
    async def _on_failure(self, error: Exception) -> None:
        """Handle failed call"""
        async with self._lock:
            self._stats.failure_count += 1
            self._stats.total_failures += 1
            self._stats.last_failure_time = time.time()
            
            logger.warning(
                "Circuit breaker recorded failure",
                name=self.config.name,
                error=str(error),
                failure_count=self._stats.failure_count
            )
            
            if self.is_half_open:
                # Immediately open on failure in half-open state
                await self._change_state(CircuitState.OPEN)
            
            elif self.is_closed:
                # Check if we should open the circuit
                if self._stats.failure_count >= self.config.failure_threshold:
                    await self._change_state(CircuitState.OPEN)
    
    def __call__(self, func: Callable) -> Callable:
        """Decorator usage"""
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await self.call(func, *args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Run in event loop if needed
            try:
                loop = asyncio.get_running_loop()
                return loop.run_until_complete(self.call(func, *args, **kwargs))
            except RuntimeError:
                # No event loop, create one
                return asyncio.run(self.call(func, *args, **kwargs))
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    async def reset(self) -> None:
        """Manually reset the circuit breaker"""
        async with self._lock:
            await self._change_state(CircuitState.CLOSED)
            self._stats.failure_count = 0
            self._stats.success_count = 0
            self._half_open_calls = 0
    
    def get_status(self) -> Dict[str, Any]:
        """Get circuit breaker status"""
        return {
            "name": self.config.name,
            "state": self._state.value,
            "stats": {
                "failure_count": self._stats.failure_count,
                "success_count": self._stats.success_count,
                "total_calls": self._stats.total_calls,
                "total_failures": self._stats.total_failures,
                "total_successes": self._stats.total_successes,
                "last_failure_time": self._stats.last_failure_time,
                "last_success_time": self._stats.last_success_time,
            },
            "config": {
                "failure_threshold": self.config.failure_threshold,
                "success_threshold": self.config.success_threshold,
                "recovery_timeout": self.config.recovery_timeout,
                "half_open_max_calls": self.config.half_open_max_calls,
            }
        }


class CircuitBreakerManager:
    """Manage multiple circuit breakers"""
    
    def __init__(self):
        self._breakers: Dict[str, CircuitBreaker] = {}
    
    def add_breaker(self, name: str, breaker: CircuitBreaker) -> None:
        """Add a circuit breaker"""
        breaker.config.name = name
        self._breakers[name] = breaker
    
    def get_breaker(self, name: str) -> Optional[CircuitBreaker]:
        """Get a circuit breaker by name"""
        return self._breakers.get(name)
    
    def create_breaker(self, name: str, **kwargs) -> CircuitBreaker:
        """Create and register a new circuit breaker"""
        breaker = CircuitBreaker(name=name, **kwargs)
        self._breakers[name] = breaker
        return breaker
    
    def get_all_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all circuit breakers"""
        return {
            name: breaker.get_status()
            for name, breaker in self._breakers.items()
        }
    
    async def reset_all(self) -> None:
        """Reset all circuit breakers"""
        for breaker in self._breakers.values():
            await breaker.reset()


# Global circuit breaker manager
circuit_breaker_manager = CircuitBreakerManager()


# Convenience decorator
def circuit_breaker(name: str, **kwargs):
    """
    Decorator to apply circuit breaker to a function
    
    Example:
        @circuit_breaker("external_api", failure_threshold=3)
        async def call_external_api():
            return await external_api.request()
    """
    def decorator(func):
        breaker = circuit_breaker_manager.get_breaker(name)
        if not breaker:
            breaker = circuit_breaker_manager.create_breaker(name, **kwargs)
        return breaker(func)
    
    return decorator 