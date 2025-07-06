"""
Factory and configuration functions for the API Gateway.
"""
from typing import Optional

import redis.asyncio as redis
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from .gateway import SecurityAPIGateway

_api_gateway: Optional[SecurityAPIGateway] = None


def get_api_gateway(redis_client: Optional[redis.Redis] = None) -> SecurityAPIGateway:
    """
    Factory function to create and return a singleton instance of the SecurityAPIGateway.
    """
    global _api_gateway
    if _api_gateway is None:
        _api_gateway = SecurityAPIGateway(redis_client=redis_client)
    elif redis_client and not _api_gateway.redis_client:
        _api_gateway.redis_client = redis_client
    return _api_gateway


def configure_app_security(app: FastAPI, redis_client: Optional[redis.Redis] = None):
    """
    Configures a FastAPI application with the necessary security middleware,
    including CORS and the main API Gateway middleware.
    """
    gateway = get_api_gateway(redis_client=redis_client)

    # Add CORS middleware first
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure this more securely for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add the main API Gateway middleware
    gateway_middleware = gateway.create_middleware()
    app.add_middleware(gateway_middleware.__class__, gateway_instance=gateway)

    return app
