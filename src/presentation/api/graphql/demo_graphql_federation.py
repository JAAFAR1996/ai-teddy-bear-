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
            print("❌ Federation system not available")
            return False
        
        try:
            print("🚀 Initializing GraphQL Federation Demo...")
            
            # Create authentication service
            auth_config = create_auth_config()
            self.auth_service = await create_auth_service(auth_config)
            print("✅ Authentication service initialized")
            
            # Create federation gateway
            federation_config = create_default_federation_config()
            self.gateway = await create_federation_gateway(federation_config)
            print("✅ Federation gateway initialized")
            
            return True
            
        except Exception as e:
    logger.error(f"Error: {e}")f"❌ Initialization failed: {e}")
            return False
    
    async def demo_basic_queries(self):
        """Demonstrate basic GraphQL queries."""
        print("\n" + "="*50)
        print("🔍 DEMO: Basic GraphQL Queries")
        print("="*50)
        
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
            print(f"\n📝 {query_info['name']}:")
            print(f"Query: {query_info['query'].strip()}")
            
            try:
                result = await self.gateway._execute_federated_query(
                    query_info['query'],
                    query_info['variables']
                )
                print(f"✅ Result: {json.dumps(result, indent=2, default=str)}")
            except Exception as e:
    logger.error(f"Error: {e}")f"❌ Error: {e}")
    
    async def demo_federated_queries(self):
        """Demonstrate federated queries across services."""
        print("\n" + "="*50)
        print("🌐 DEMO: Federated Queries")
        print("="*50)
        
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
        
        print(f"📝 Federated Query:")
        print(federated_query.strip())
        
        # Analyze which services are needed
        services = self.gateway._analyze_query_services(federated_query)
        print(f"🔧 Services involved: {services}")
        
        try:
            result = await self.gateway._execute_federated_query(federated_query, {})
            print(f"✅ Federated Result: {json.dumps(result, indent=2, default=str)}")
        except Exception as e:
    logger.error(f"Error: {e}")f"❌ Error: {e}")
    
    async def demo_authentication(self):
        """Demonstrate authentication features."""
        print("\n" + "="*50)
        print("🔐 DEMO: Authentication & Authorization")
        print("="*50)
        
        # Create test user
        print("👤 Creating test user...")
        user = await self.auth_service.create_user(
            username="demo_parent",
            email="demo@teddy-bear.ai",
            password="demo123",
            role="parent"
        )
        print(f"✅ Created user: {user.username} with role: {user.role}")
        
        # Generate JWT token
        print("🎟️ Generating JWT token...")
        token = await self.auth_service.create_access_token(user)
        print(f"✅ Token generated: {token[:20]}...")
        
        # Verify token
        print("🔍 Verifying token...")
        verified_user = await self.auth_service.verify_token(token)
        print(f"✅ Token verified for user: {verified_user.username}")
        
        # Create API key
        print("🔑 Creating API key...")
        api_key = await self.auth_service.create_api_key(
            user.id,
            "Demo API Key",
            user.permissions
        )
        print(f"✅ API key created: {api_key.name}")
    
    async def demo_performance_metrics(self):
        """Demonstrate performance monitoring."""
        print("\n" + "="*50)
        print("📊 DEMO: Performance Monitoring")
        print("="*50)
        
        # Get gateway metrics
        print("📈 Gateway Performance Metrics:")
        metrics = self.gateway.metrics
        
        print(f"   Total Requests: {metrics['requests_total']}")
        print(f"   Successful Requests: {metrics['requests_success']}")
        print(f"   Error Requests: {metrics['requests_error']}")
        print(f"   Average Latency: {metrics['average_latency']:.2f}ms")
        print(f"   Cache Hits: {metrics['cache_hits']}")
        print(f"   Cache Misses: {metrics['cache_misses']}")
        
        # Calculate hit rate
        total_cache = metrics['cache_hits'] + metrics['cache_misses']
        if total_cache > 0:
            hit_rate = metrics['cache_hits'] / total_cache
            print(f"   Cache Hit Rate: {hit_rate:.2%}")
        
        print(f"   Last Updated: {datetime.now()}")
    
    async def cleanup(self):
        """Cleanup demo resources."""
        if self.gateway:
            await self.gateway.cleanup()
        print("🧹 Demo cleanup completed")


async def run_interactive_demo():
    """Run interactive GraphQL Federation demo."""
    print("🎯 AI Teddy Bear - GraphQL Federation Demo")
    print("=" * 60)
    print("API Team Implementation - Task 13")
    print("=" * 60)
    
    demo = FederationDemoSystem()
    
    if not await demo.initialize():
        return
    
    try:
        while True:
            print("\n🎮 Demo Options:")
            print("1. Basic GraphQL Queries")
            print("2. Federated Queries") 
            print("3. Authentication & Authorization")
            print("4. Performance Monitoring")
            print("5. Run All Demos")
            print("0. Exit")
            
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
                print("\n🚀 Running all demos...")
                await demo.demo_basic_queries()
                await demo.demo_federated_queries()
                await demo.demo_authentication()
                await demo.demo_performance_metrics()
                print("\n✅ All demos completed!")
            else:
                print("❌ Invalid choice. Please select 0-5.")
            
            if choice != "0":
                input("\nPress Enter to continue...")
    
    finally:
        await demo.cleanup()
        print("\n👋 Demo completed. Thank you!")


async def run_automated_demo():
    """Run automated demo without user interaction."""
    print("🤖 Running Automated GraphQL Federation Demo...")
    
    demo = FederationDemoSystem()
    
    if not await demo.initialize():
        return
    
    try:
        await demo.demo_basic_queries()
        await demo.demo_federated_queries()
        await demo.demo_authentication()
        await demo.demo_performance_metrics()
        
        print("\n✅ Automated demo completed successfully!")
        
    finally:
        await demo.cleanup()


if __name__ == "__main__":
    import sys
    
    if "--automated" in sys.argv:
        asyncio.run(run_automated_demo())
    else:
        asyncio.run(run_interactive_demo()) 