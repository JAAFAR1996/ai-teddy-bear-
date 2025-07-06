"""
FastAPI middleware for the API Gateway.
"""
import time
from typing import TYPE_CHECKING, Callable

from fastapi import Request
from fastapi.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse

if TYPE_CHECKING:
    from .gateway import SecurityAPIGateway


class APIGatewayMiddleware(BaseHTTPMiddleware):
    """
    The FastAPI middleware that integrates all the gateway's security and
    management features into the request/response cycle.
    """

    def __init__(self, app, gateway_instance: "SecurityAPIGateway"):
        super().__init__(app)
        self.gateway = gateway_instance

    async def dispatch(self, request: Request, call_next: Callable):
        """The main entry point for processing all incoming requests."""
        start_time = time.monotonic()

        # 1. Run all security checks (threats, IP blocks)
        security_result = await self.gateway.run_security_checks(request)
        if not security_result["allowed"]:
            return self._build_error_response(
                security_result["status_code"], security_result["message"]
            )

        # 2. Check rate limiting
        rate_limit_result = await self.gateway.check_rate_limit(request)
        if not rate_limit_result["allowed"]:
            headers = {
                "Retry-After": str(rate_limit_result.get("retry_after", 60))}
            return self._build_error_response(429, "Rate limit exceeded.", headers)

        # 3. Check circuit breaker
        if not await self.gateway.check_circuit_breaker(request):
            return self._build_error_response(503, "Service temporarily unavailable.")

        try:
            # 4. If all checks pass, process the request
            response = await call_next(request)
            await self.gateway.on_request_success(request)

        except Exception as e:
            # 5. Handle upstream errors and record failure
            await self.gateway.on_request_failure(request)
            # Re-raise the exception to be handled by FastAPI's exception handlers
            raise e

        finally:
            # 6. Record analytics for the request
            response_time = time.monotonic() - start_time
            # This is a simplification; a real implementation would need the response object
            # to get the status code. This can be handled by a separate middleware
            # or by adapting the gateway logic.
            # await self.gateway.record_request_analytics(...)

        # 7. Add security headers to the response
        if 'response' in locals():
            return await self.gateway.add_security_headers(response)

        # Fallback for errors before response is generated
        return self._build_error_response(500, "An internal error occurred.")

    def _build_error_response(self, status_code: int, message: str, headers: dict = None) -> JSONResponse:
        """Helper to create a standardized JSON error response."""
        return JSONResponse(
            status_code=status_code,
            content={"error": message},
            headers=headers or {},
        )
