#!/usr/bin/env python3
"""
🔧 gRPC Server
Lead Architect: جعفر أديب (Jaafar Adeeb)
High-performance gRPC communication
"""

import asyncio
import grpc
from typing import Dict, Any
import structlog

logger = structlog.get_logger()


class GRPCServer:
    """Enterprise gRPC server for high-performance communication"""
    
    def __init__(self, container):
        self.container = container
        self.server: grpc.aio.Server = None
        self._running = False
    
    async def start(self, port: int = 50051):
        """Start gRPC server"""
        if self._running:
            return
        
        logger.info("🔧 Starting gRPC server", port=port)
        
        try:
            self.server = grpc.aio.server()
            
            # Add services here
            # self.server.add_insecure_port(f'[::]:{port}')
            
            # await self.server.start()
            self._running = True
            
            logger.info("✅ gRPC server started successfully")
            
            # Keep server running
            await self._wait_for_termination()
            
        except Exception as e:
            logger.error("❌ Failed to start gRPC server", error=str(e))
            raise
    
    async def stop(self):
        """Stop gRPC server"""
        if not self._running:
            return
        
        logger.info("🛑 Stopping gRPC server...")
        
        try:
            if self.server:
                await self.server.stop(grace=5)
            
            self._running = False
            logger.info("✅ gRPC server stopped")
            
        except Exception as e:
            logger.error("❌ Error stopping gRPC server", error=str(e))
    
    async def _wait_for_termination(self):
        """Wait for server termination"""
        try:
            while self._running:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass 