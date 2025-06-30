#!/usr/bin/env python3
"""
Interactive Demo for GraphQL Federation System.

API Team Implementation - Task 13
Author: API Team Lead
"""

import asyncio
import logging
import json
from datetime import datetime

# Demo imports
try:
    from src.infrastructure.graphql.federation_gateway import (
        create_federation_gateway, create_default_federation_config
    )
    from src.infrastructure.graphql.authentication import create_auth_service, create_auth_config
    FEDERATION_AVAILABLE = True
except Exception as e:
    logger.error(f"Error: {e}")f"⚠️  GraphQL Federation not available: {e}")
    FEDERATION_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FederationDemoSystem:
    """Demo system for GraphQL Federation."""
    
    def __init__(self):
        self.gateway = None
        self.auth_service = None
        
    async def initialize(self):
        """Initialize demo system."""
        if not FEDERATION_AVAILABLE:
            logger.error("❌ Federation system not available")
            return False
        
        try:
            logger.info("🚀 Initializing GraphQL Federation Demo...")
            
            # Create authentication service
            auth_config = create_auth_config()
            self.auth_service = await create_auth_service(auth_config)
            logger.info("✅ Authentication service initialized")
            
            # Create federation gateway
            federation_config = create_default_federation_config()
            self.gateway = await create_federation_gateway(federation_config)
            logger.info("✅ Federation gateway initialized")
            
            return True
            
        except Exception as e:
    logger.error(f"Error: {e}")f"❌ Initialization failed: {e}")
            return False
    
    async def demo_basic_queries(self):
        """Demonstrate basic GraphQL queries."""
        logger.info("\n" + "="*50)
        logger.debug("🔍 DEMO: Basic GraphQL Queries")
        logger.info("="*50)
        
        # Sample queries
        queries = [
            {
                "name": "Get Child",
                "query": """
                query {
                    child(id: "child-001") {
                        id
                        name
                        age
                        language
                    }
                }
                """,
                "variables": {}
            },
            {
                "name": "Get Children for Parent",
                "query": """
                query {
                    children(parentId: "parent-001") {
                        id
                        name
                        age
                        preferences {
                            favoriteTopics
                            difficultyLevel
                        }
                    }
                }
                """,
                "variables": {}
            }
        ]
        
        for query_info in queries:
            logger.info(f"\n📝 {query_info['name']}:")
            logger.info(f"Query: {query_info['query'].strip()}")
            
            try:
                result = await self.gateway._execute_federated_query(
                    query_info['query'],
                    query_info['variables']
                )
                logger.info(f"✅ Result: {json.dumps(result, indent=2, default=str)}")
            except Exception as e:
    logger.error(f"Error: {e}")f"❌ Error: {e}")
    
    async def demo_federated_queries(self):
        """Demonstrate federated queries across services."""
        logger.info("\n" + "="*50)
        logger.info("🌐 DEMO: Federated Queries")
        logger.info("="*50)
        
        federated_query = """
        query {
            child(id: "child-001") {
                id
                name
                age
                aiProfile {
                    personalityTraits {
                        name
                        score
                    }
                    learningStyle
                }
                usage {
                    totalSessionTime
                    dailyUsage
                }
                safetyProfile {
                    riskLevel
                    safetyScore
                }
            }
        }
        """
        
        logger.info(f"📝 Federated Query:")
        logger.info(federated_query.strip())
        
        # Analyze which services are needed
        services = self.gateway._analyze_query_services(federated_query)
        logger.info(f"🔧 Services involved: {services}")
        
        try:
            result = await self.gateway._execute_federated_query(federated_query, {})
            logger.info(f"✅ Federated Result: {json.dumps(result, indent=2, default=str)}")
        except Exception as e:
    logger.error(f"Error: {e}")f"❌ Error: {e}")
    
    async def demo_authentication(self):
        """Demonstrate authentication features."""
        logger.info("\n" + "="*50)
        logger.info("🔐 DEMO: Authentication & Authorization")
        logger.info("="*50)
        
        # Create test user
        logger.info("👤 Creating test user...")
        user = await self.auth_service.create_user(
            username="demo_parent",
            email="demo@teddy-bear.ai",
            password="demo123",
            role="parent"
        )
        logger.info(f"✅ Created user: {user.username} with role: {user.role}")
        
        # Generate JWT token
        logger.info("🎟️ Generating JWT token...")
        token = await self.auth_service.create_access_token(user)
        logger.info(f"✅ Token generated: {token[:20]}...")
        
        # Verify token
        logger.debug("🔍 Verifying token...")
        verified_user = await self.auth_service.verify_token(token)
        logger.info(f"✅ Token verified for user: {verified_user.username}")
        
        # Create API key
        logger.info("🔑 Creating API key...")
        api_key = await self.auth_service.create_api_key(
            user.id,
            "Demo API Key",
            user.permissions
        )
        logger.info(f"✅ API key created: {api_key.name}")
    
    async def demo_performance_metrics(self):
        """Demonstrate performance monitoring."""
        logger.info("\n" + "="*50)
        logger.info("📊 DEMO: Performance Monitoring")
        logger.info("="*50)
        
        # Get gateway metrics
        logger.info("📈 Gateway Performance Metrics:")
        metrics = self.gateway.metrics
        
        logger.info(f"   Total Requests: {metrics['requests_total']}")
        logger.info(f"   Successful Requests: {metrics['requests_success']}")
        logger.error(f"   Error Requests: {metrics['requests_error']}")
        logger.info(f"   Average Latency: {metrics['average_latency']:.2f}ms")
        logger.info(f"   Cache Hits: {metrics['cache_hits']}")
        logger.info(f"   Cache Misses: {metrics['cache_misses']}")
        
        # Calculate hit rate
        total_cache = metrics['cache_hits'] + metrics['cache_misses']
        if total_cache > 0:
            hit_rate = metrics['cache_hits'] / total_cache
            logger.info(f"   Cache Hit Rate: {hit_rate:.2%}")
        
        logger.info(f"   Last Updated: {datetime.now()}")
    
    async def cleanup(self):
        """Cleanup demo resources."""
        if self.gateway:
            await self.gateway.cleanup()
        logger.info("🧹 Demo cleanup completed")


async def run_interactive_demo():
    """Run interactive GraphQL Federation demo."""
    logger.info("🎯 AI Teddy Bear - GraphQL Federation Demo")
    logger.info("=" * 60)
    logger.info("API Team Implementation - Task 13")
    logger.info("=" * 60)
    
    demo = FederationDemoSystem()
    
    if not await demo.initialize():
        return
    
    try:
        while True:
            logger.info("\n🎮 Demo Options:")
            logger.info("1. Basic GraphQL Queries")
            logger.info("2. Federated Queries")
            logger.info("3. Authentication & Authorization")
            logger.info("4. Performance Monitoring")
            logger.info("5. Run All Demos")
            logger.info("0. Exit")
            
            choice = input("\nSelect demo (0-5): ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                await demo.demo_basic_queries()
            elif choice == "2":
                await demo.demo_federated_queries()
            elif choice == "3":
                await demo.demo_authentication()
            elif choice == "4":
                await demo.demo_performance_metrics()
            elif choice == "5":
                logger.info("\n🚀 Running all demos...")
                await demo.demo_basic_queries()
                await demo.demo_federated_queries()
                await demo.demo_authentication()
                await demo.demo_performance_metrics()
                logger.info("\n✅ All demos completed!")
            else:
                logger.error("❌ Invalid choice. Please select 0-5.")
            
            if choice != "0":
                input("\nPress Enter to continue...")
    
    finally:
        await demo.cleanup()
        logger.info("\n👋 Demo completed. Thank you!")


async def run_automated_demo():
    """Run automated demo without user interaction."""
    logger.info("🤖 Running Automated GraphQL Federation Demo...")
    
    demo = FederationDemoSystem()
    
    if not await demo.initialize():
        return
    
    try:
        await demo.demo_basic_queries()
        await demo.demo_federated_queries()
        await demo.demo_authentication()
        await demo.demo_performance_metrics()
        
        logger.info("\n✅ Automated demo completed successfully!")
        
    finally:
        await demo.cleanup()


if __name__ == "__main__":
    import sys
    
    if "--automated" in sys.argv:
        asyncio.run(run_automated_demo())
    else:
        asyncio.run(run_interactive_demo()) 