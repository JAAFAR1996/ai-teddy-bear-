#!/usr/bin/env python3
"""
🚀 Enterprise GraphQL Server with DataLoader Pattern
Lead Architect: جعفر أديب (Jaafar Adeeb)
High-performance GraphQL server with advanced optimization
"""

import asyncio
from typing import Dict, Any
import structlog
from strawberry.fastapi import GraphQLRouter
from src.infrastructure.graphql.context import create_graphql_context_manager
from src.presentation.api.graphql.schema import create_optimized_schema
from src.infrastructure.graphql.performance import performance_monitor

logger = structlog.get_logger()


class EnterpriseGraphQLServer:
    """
    🏗️ Enterprise GraphQL Server
    Features:
    - DataLoader pattern for N+1 prevention
    - Cursor-based pagination
    - Performance monitoring
    - Query complexity analysis
    - Redis caching integration
    """
    
    def __init__(self, container):
        self.container = container
        self.context_manager = None
        self.schema = None
        self.router = None
        self._running = False
        logger.info("🚀 Enterprise GraphQL Server initialized")
    
    async def initialize(self):
        """Initialize GraphQL server components"""
        try:
            # Create and initialize context manager
            self.context_manager = create_graphql_context_manager(self.container)
            await self.context_manager.initialize()
            
            # Create optimized schema
            self.schema = create_optimized_schema()
            
            # Create GraphQL router
            self.router = GraphQLRouter(
                schema=self.schema,
                context_getter=self._get_context,
                graphiql=True,  # Enable GraphiQL in development
            )
            
            logger.info("✅ GraphQL Server initialized successfully")
            
        except Exception as e:
            logger.error("❌ Failed to initialize GraphQL Server", error=str(e))
            raise
    
    async def _get_context(self, request) -> Dict[str, Any]:
        """Create GraphQL context for each request"""
        try:
            # Extract auth info from request
            auth_header = request.headers.get("Authorization")
            user_id = None  # Extract from token if needed
            
            # Create context
            context = await self.context_manager.create_context(
                request=request,
                user_id=user_id,
                auth_token=auth_header
            )
            
            return context.__dict__
            
        except Exception as e:
            logger.error("❌ Failed to create GraphQL context", error=str(e))
            # Return minimal context to prevent crashes
            return {
                "dataloaders": {},
                "paginators": {},
                "repositories": {}
            }
    
    async def start(self, port: int = 8080):
        """Start GraphQL server"""
        if self._running:
            return
        
        logger.info("📊 Starting GraphQL server", port=port)
        
        try:
            # Initialize if not already done
            if not self.context_manager:
                await self.initialize()
            
            self._running = True
            logger.info("✅ GraphQL server started successfully")
            
            # Keep server running
            await self._wait_for_termination()
            
        except Exception as e:
            logger.error("❌ Failed to start GraphQL server", error=str(e))
            raise
    
    async def stop(self):
        """Stop GraphQL server"""
        if not self._running:
            return
        
        logger.info("🛑 Stopping GraphQL server...")
        
        try:
            self._running = False
            logger.info("✅ GraphQL server stopped")
            
        except Exception as e:
            logger.error("❌ Error stopping GraphQL server", error=str(e))
    
    async def _wait_for_termination(self):
        """Wait for server termination"""
        try:
            while self._running:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass
    
    def get_router(self):
        """Get FastAPI router for GraphQL"""
        return self.router
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get GraphQL performance metrics"""
        try:
            # Get DataLoader metrics
            dataloader_metrics = await self.context_manager.get_performance_metrics()
            
            # Get query performance metrics
            query_metrics = performance_monitor.get_performance_summary()
            
            return {
                "dataloader_metrics": dataloader_metrics,
                "query_metrics": query_metrics,
                "server_status": "running" if self._running else "stopped"
            }
            
        except Exception as e:
            logger.error("❌ Failed to get performance metrics", error=str(e))
            return {"error": str(e)}
    
    async def warm_cache(self):
        """Pre-warm DataLoader caches"""
        if self.context_manager:
            await self.context_manager.warm_cache()
    
    def reset_metrics(self):
        """Reset performance metrics"""
        if self.context_manager:
            self.context_manager.reset_metrics()
        performance_monitor.reset_stats()


# Factory function
def create_graphql_server(container) -> EnterpriseGraphQLServer:
    """Create and configure GraphQL server"""
    return EnterpriseGraphQLServer(container) 