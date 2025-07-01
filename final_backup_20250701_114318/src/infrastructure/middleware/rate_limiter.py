import time
from collections import defaultdict
from typing import Callable

from fastapi import HTTPException, Request


class RateLimiter:
    """Token bucket rate limiter with sliding window"""

    def __init__(self, requests_per_minute: int = 60, burst_size: int = 10):
        self.rate = requests_per_minute / 60.0  # requests per second
        self.burst_size = burst_size
        self.buckets = defaultdict(lambda: {"tokens": burst_size, "last_update": time.time()})

    async def __call__(self, request: Request, call_next: Callable):
        # Get client identifier
        client_id = self._get_client_id(request)

        # Check rate limit
        if not self._is_allowed(client_id):
            raise HTTPException(status_code=429, detail="Rate limit exceeded", headers={"Retry-After": "60"})

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        bucket = self.buckets[client_id]
        response.headers["X-RateLimit-Limit"] = str(self.burst_size)
        response.headers["X-RateLimit-Remaining"] = str(int(bucket["tokens"]))
        response.headers["X-RateLimit-Reset"] = str(int(time.time() + (self.burst_size - bucket["tokens"]) / self.rate))

        return response

    def _is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed"""
        bucket = self.buckets[client_id]
        current_time = time.time()

        # Refill tokens based on time elapsed
        time_elapsed = current_time - bucket["last_update"]
        bucket["tokens"] = min(self.burst_size, bucket["tokens"] + time_elapsed * self.rate)
        bucket["last_update"] = current_time

        # Check if we have tokens
        if bucket["tokens"] >= 1:
            bucket["tokens"] -= 1
            return True
        return False

    def _get_client_id(self, request: Request) -> str:
        """Get unique client identifier"""
        # Try to get from authenticated user
        if hasattr(request.state, "user") and request.state.user:
            return f"user:{request.state.user.id}"

        # Fall back to IP address
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return f"ip:{forwarded.split(',')[0].strip()}"
        return f"ip:{request.client.host}"
