#!/usr/bin/env python3
"""
🎯 GraphQL Context Manager
Lead Architect: جعفر أديب (Jaafar Adeeb)
Enterprise context management with DataLoader and pagination
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, field
import structlog
from .dataloaders import DataLoaderRegistry, create_dataloader_registry
from .pagination import CursorPaginator

logger = structlog.get_logger()


@dataclass
class GraphQLContext:
    """
    🏗️ GraphQL Request Context
    Contains DataLoaders, paginators, repositories, and auth info
    """
    dataloaders: Dict[str, Any] = field(default_factory=dict)
    paginators: Dict[str, Any] = field(default_factory=dict)
    repositories: Dict[str, Any] = field(default_factory=dict)
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    auth_token: Optional[str] = None
    
    def get_dataloader(self, name -> Any: str) -> Any:
        """Get DataLoader by name"""
        return self.dataloaders.get(name)
    
    def get_paginator(self, name -> Any: str) -> Any:
        """Get paginator by name"""
        return self.paginators.get(name)
    
    def get_repository(self, name -> Any: str) -> Any:
        """Get repository by name"""
        return self.repositories.get(name)


class GraphQLContextManager:
    """
    🎮 GraphQL Context Manager
    Creates and manages context for each GraphQL request
    """
    
    def __init__(self, container):
        self.container = container
        self._dataloader_registry: Optional[DataLoaderRegistry] = None
        self._repositories = {}
        logger.info("🎮 GraphQL Context Manager initialized")
    
    async def initialize(self):
        """Initialize context manager with dependencies"""
        try:
            # Get dependencies from container
            self._repositories = {
                "child": self.container.child_repository(),
                "conversation": self.container.conversation_repository(),
                "message": self.container.message_repository() if hasattr(self.container, 'message_repository') else None
            }
            
            # Create DataLoader registry
            cache_client = self.container.redis_client()
            self._dataloader_registry = create_dataloader_registry(
                cache_client=cache_client,
                **{k: v for k, v in self._repositories.items() if v is not None}
            )
            
            logger.info("✅ GraphQL Context Manager initialized successfully")
            
        except Exception as e:
            logger.error("❌ Failed to initialize GraphQL Context Manager", error=str(e))
            raise
    
    async def create_context(
        self,
        request: Any = None,
        user_id: Optional[str] = None,
        auth_token: Optional[str] = None
    ) -> GraphQLContext:
        """
        Create GraphQL context for request
        """
        try:
            # Extract request information
            request_id = getattr(request, 'id', None) if request else None
            
            # Create DataLoaders for this request
            dataloaders = await self._create_dataloaders()
            
            # Create paginators for this request
            paginators = await self._create_paginators()
            
            # Create context
            context = GraphQLContext(
                dataloaders=dataloaders,
                paginators=paginators,
                repositories=self._repositories,
                user_id=user_id,
                request_id=request_id,
                auth_token=auth_token
            )
            
            logger.debug("🎯 GraphQL context created", 
                        request_id=request_id,
                        user_id=user_id,
                        dataloaders=list(dataloaders.keys()),
                        paginators=list(paginators.keys()))
            
            return context
            
        except Exception as e:
            logger.error("❌ Failed to create GraphQL context", error=str(e))
            raise
    
    async def _create_dataloaders(self) -> Dict[str, Any]:
        """Create DataLoaders for request"""
        dataloaders = {}
        
        try:
            # Get DataLoaders from registry
            if self._dataloader_registry:
                # Core entity loaders
                dataloaders["child"] = self._dataloader_registry.get_loader("child")
                dataloaders["conversation"] = self._dataloader_registry.get_loader("conversation")
                
                # Relationship loaders
                dataloaders["conversation_by_child"] = self._dataloader_registry.get_loader("conversation_by_child")
                
                # Aggregate loaders (for counts, stats)
                dataloaders["conversation_count"] = await self._create_conversation_count_loader()
                dataloaders["message_count"] = await self._create_message_count_loader()
            
            return dataloaders
            
        except Exception as e:
            logger.error("❌ Failed to create DataLoaders", error=str(e))
            return {}
    
    async def _create_paginators(self) -> Dict[str, Any]:
        """Create paginators for request"""
        paginators = {}
        
        try:
            cache_client = self.container.redis_client()
            
            # Child paginator
            if "child" in self._repositories:
                paginators["child"] = CursorPaginator(
                    repository=self._repositories["child"],
                    cache_client=cache_client
                )
            
            # Conversation paginator
            if "conversation" in self._repositories:
                paginators["conversation"] = CursorPaginator(
                    repository=self._repositories["conversation"],
                    cache_client=cache_client
                )
            
            # Message paginator
            if "message" in self._repositories:
                paginators["message"] = CursorPaginator(
                    repository=self._repositories["message"],
                    cache_client=cache_client
                )
            
            return paginators
            
        except Exception as e:
            logger.error("❌ Failed to create paginators", error=str(e))
            return {}
    
    async def _create_conversation_count_loader(self):
        """Create DataLoader for conversation counts by child"""
        from .dataloaders import BaseDataLoader
        
        class ConversationCountLoader(BaseDataLoader[str, int]):
            def __init__(self, conversation_repository, cache_client):
                super().__init__(
                    repository=conversation_repository,
                    cache_client=cache_client,
                    name="conversation_count_loader"
                )
            
            async def _fetch_from_repository(self, child_ids: list) -> list:
                """Fetch conversation counts for child IDs"""
                try:
                    counts = []
                    for child_id in child_ids:
                        count = await self.repository.count({"child_id": child_id})
                        counts.append(count)
                    return counts
                except Exception as e:
                    logger.error("Failed to fetch conversation counts", error=str(e))
                    return [0] * len(child_ids)
        
        cache_client = self.container.redis_client()
        return ConversationCountLoader(
            self._repositories["conversation"],
            cache_client
        )
    
    async def _create_message_count_loader(self):
        """Create DataLoader for message counts by conversation"""
        from .dataloaders import BaseDataLoader
        
        class MessageCountLoader(BaseDataLoader[str, int]):
            def __init__(self, message_repository, cache_client):
                super().__init__(
                    repository=message_repository,
                    cache_client=cache_client,
                    name="message_count_loader"
                )
            
            async def _fetch_from_repository(self, conversation_ids: list) -> list:
                """Fetch message counts for conversation IDs"""
                try:
                    counts = []
                    for conversation_id in conversation_ids:
                        count = await self.repository.count({"conversation_id": conversation_id})
                        counts.append(count)
                    return counts
                except Exception as e:
                    logger.error("Failed to fetch message counts", error=str(e))
                    return [0] * len(conversation_ids)
        
        if "message" in self._repositories and self._repositories["message"]:
            cache_client = self.container.redis_client()
            return MessageCountLoader(
                self._repositories["message"],
                cache_client
            )
        return None
    
    async def warm_cache(self, warmup_data: Dict[str, list] = None):
        """Pre-warm DataLoader caches"""
        if not warmup_data:
            # Default warmup data
            warmup_data = {
                "child": [],  # Will be populated from recent queries
                "conversation": []
            }
        
        if self._dataloader_registry:
            await self._dataloader_registry.warm_cache(warmup_data)
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics from DataLoaders"""
        if self._dataloader_registry:
            return await self._dataloader_registry.get_all_metrics()
        return {}
    
    def reset_metrics(self) -> Any:
        """Reset all DataLoader metrics"""
        if self._dataloader_registry:
            self._dataloader_registry.reset_all_metrics()


# Factory function for creating context manager
def create_graphql_context_manager(container) -> GraphQLContextManager:
    """Create and initialize GraphQL context manager"""
    context_manager = GraphQLContextManager(container)
    logger.info("🏭 GraphQL Context Manager created")
    return context_manager 