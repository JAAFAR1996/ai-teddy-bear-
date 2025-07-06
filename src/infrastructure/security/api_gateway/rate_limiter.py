"""
Rate limiting component for the API Gateway.
"""
import asyncio
import re
import time
from typing import Dict, List, Optional, Tuple

import redis.asyncio as redis

from .models import RateLimitRule, RequestType


class RateLimiterMixin:
    """A mixin providing rate limiting functionality using Redis or in-memory storage."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rate_limit_rules: List[RateLimitRule] = self._initialize_default_rules(
        )
        self._memory_store: Dict[str, List[float]] = {}
        self.redis_client: Optional[redis.Redis] = kwargs.get("redis_client")

    def _initialize_default_rules(self) -> List[RateLimitRule]:
        """Initializes a default set of rate limiting rules."""
        return [
            RateLimitRule("general_api", 100, 60, RequestType.API_CALL),
            RateLimitRule("auth_login", 10, 300, RequestType.AUTHENTICATION),
            RateLimitRule("audio_upload", 30, 60, RequestType.AUDIO_UPLOAD),
            RateLimitRule("websocket", 15, 60,
                          RequestType.WEBSOCKET_CONNECTION),
            RateLimitRule("file_upload", 20, 300, RequestType.FILE_UPLOAD),
            RateLimitRule("bulk_ops", 5, 600, RequestType.BULK_OPERATION),
            RateLimitRule("parent_api", 200, 60, user_role="parent"),
            RateLimitRule("child_api", 50, 60, user_role="child"),
        ]

    async def check_rate_limit(self, request) -> Dict[str, any]:
        """Checks if a request is within the defined rate limits."""
        client_ip = self._get_client_ip(request)
        user_id = await self._extract_user_id(request)
        user_role = await self._extract_user_role(request)
        endpoint = str(request.url.path)
        request_type = self._classify_request(request)

        rules = self._find_applicable_rules(request_type, user_role, endpoint)

        for rule in rules:
            key_base = f"user:{user_id}" if user_id else f"ip:{client_ip}"
            rate_limit_key = f"rate_limit:{rule.name}:{key_base}"

            is_allowed, retry_after = await self._is_request_allowed(
                rate_limit_key, rule.requests, rule.window_seconds
            )
            if not is_allowed:
                return {"allowed": False, "retry_after": retry_after, "rule": rule.name}

        return {"allowed": True}

    async def _is_request_allowed(self, key: str, limit: int, window: int) -> Tuple[bool, int]:
        """Determines if a request is allowed based on the given key, limit, and window."""
        if self.redis_client:
            return await self._redis_sliding_window_check(key, limit, window)
        return self._memory_sliding_window_check(key, limit, window)

    async def _redis_sliding_window_check(self, key: str, limit: int, window: int) -> Tuple[bool, int]:
        """Performs a rate limit check using Redis with the sliding window algorithm."""
        now = time.time()
        window_start = now - window

        async with self.redis_client.pipeline(transaction=True) as pipe:
            pipe.zremrangebyscore(key, 0, window_start)
            pipe.zcard(key)
            pipe.zadd(key, {str(now): now})
            pipe.expire(key, window)
            results = await pipe.execute()

        current_count = results[1]

        if current_count >= limit:
            return False, window  # Simplified retry_after for now
        return True, 0

    def _memory_sliding_window_check(self, key: str, limit: int, window: int) -> Tuple[bool, int]:
        """Performs a rate limit check using in-memory storage."""
        now = time.time()
        window_start = now - window

        if key not in self._memory_store:
            self._memory_store[key] = []

        # Remove timestamps outside the window
        self._memory_store[key] = [
            ts for ts in self._memory_store[key] if ts > window_start]

        if len(self._memory_store[key]) >= limit:
            retry_after = int((self._memory_store[key][0] + window) - now)
            return False, max(1, retry_after)

        self._memory_store[key].append(now)
        return True, 0

    def _find_applicable_rules(
        self, request_type: RequestType, user_role: Optional[str], endpoint: str
    ) -> List[RateLimitRule]:
        """Finds all rate limit rules that apply to the current request."""
        return [
            rule for rule in self.rate_limit_rules
            if (not rule.request_type or rule.request_type == request_type) and
            (not rule.user_role or rule.user_role == user_role) and
            (not rule.endpoint_pattern or re.search(
                rule.endpoint_pattern, endpoint))
        ]

    def _classify_request(self, request) -> RequestType:
        """Classifies the request into a RequestType for rate limiting purposes."""
        path = str(request.url.path)
        method = request.method.upper()

        if "/auth/" in path or "/login" in path:
            return RequestType.AUTHENTICATION
        if "/audio/" in path and method == 'POST':
            return RequestType.AUDIO_UPLOAD
        if "/ws" in path or "/websocket" in path:
            return RequestType.WEBSOCKET_CONNECTION
        if "/upload" in path and method == 'POST':
            return RequestType.FILE_UPLOAD
        if "/bulk/" in path:
            return RequestType.BULK_OPERATION

        return RequestType.API_CALL

    # These are placeholders that the main gateway class will implement
    def _get_client_ip(self, request) -> str: raise NotImplementedError

    async def _extract_user_id(
        self, request) -> Optional[str]: raise NotImplementedError

    async def _extract_user_role(
        self, request) -> Optional[str]: raise NotImplementedError
