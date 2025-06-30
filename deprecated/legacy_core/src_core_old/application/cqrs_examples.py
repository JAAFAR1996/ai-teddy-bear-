"""
📚 CQRS Usage Examples
=====================

Comprehensive examples demonstrating CQRS pattern usage
for AI Teddy Bear system operations.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from uuid import uuid4

from .cqrs_service import get_cqrs_service

logger = logging.getLogger(__name__)


async def example_1_child_registration():
    """Example 1: Child registration using CQRS commands"""
    
    print("🔄 Example 1: Child Registration with CQRS")
    print("-" * 50)
    
    cqrs = get_cqrs_service()
    await cqrs.initialize()
    
    # Register a new child
    result = await cqrs.register_child(
        parent_id="parent-123",
        device_id="device-456",
        name="Emma Thompson",
        age=7,
        udid="unique-device-emma-001",
        user_id="admin"
    )
    
    if result.success:
        print(f"✅ Child registered successfully:")
        print(f"   - Child ID: {result.data['child_id']}")
        print(f"   - Name: {result.data['name']}")
        print(f"   - Age: {result.data['age']}")
    else:
        print(f"❌ Registration failed: {result.message}")
    
    return result.data['child_id'] if result.success else None


async def example_2_child_profile_queries():
    """Example 2: Query child profile using CQRS queries"""
    
    print("\n🔍 Example 2: Child Profile Queries")
    print("-" * 50)
    
    cqrs = get_cqrs_service()
    
    # First register a child to query
    child_id = await example_1_child_registration()
    
    if not child_id:
        print("❌ Cannot query profile - no child registered")
        return
    
    # Query child profile
    profile_result = await cqrs.get_child_profile(
        child_id=child_id,
        user_id="parent-123"
    )
    
    if profile_result.data:
        profile = profile_result.data
        print("✅ Child profile retrieved:")
        print(f"   - Name: {profile.get('name', 'N/A')}")
        print(f"   - Age: {profile.get('age', 'N/A')}")
        print(f"   - Conversations: {profile.get('conversation_count', 0)}")
        print(f"   - Safety Status: {profile.get('safety_status', 'N/A')}")
        print(f"   - Profile Completeness: {profile.get('profile_completeness', 0)}%")
    else:
        print(f"❌ Profile not found: {profile_result.metadata.get('message', 'Unknown error')}")


async def example_3_profile_updates():
    """Example 3: Update child profile with commands"""
    
    print("\n📝 Example 3: Profile Updates")
    print("-" * 50)
    
    cqrs = get_cqrs_service()
    
    # Use child from previous example or create new one
    child_id = "child-123"  # Assume exists from previous example
    
    # Update child profile
    update_result = await cqrs.update_child_profile(
        child_id=child_id,
        changes={
            "age": 8,  # Birthday!
            "preferences": {
                "favorite_stories": ["dragons", "princesses"],
                "learning_style": "visual",
                "bedtime": "20:00"
            }
        },
        user_id="parent-123"
    )
    
    if update_result.success:
        print("✅ Profile updated successfully:")
        print(f"   - Changes applied: {update_result.data['changes']}")
        
        # Query updated profile
        updated_profile = await cqrs.get_child_profile(child_id)
        if updated_profile.data:
            print(f"   - New age: {updated_profile.data.get('age', 'N/A')}")
            print(f"   - Updated completeness: {updated_profile.data.get('profile_completeness', 0)}%")
    else:
        print(f"❌ Update failed: {update_result.message}")


async def example_4_safety_violations():
    """Example 4: Safety violation reporting and queries"""
    
    print("\n⚠️ Example 4: Safety Violation Handling")
    print("-" * 50)
    
    cqrs = get_cqrs_service()
    child_id = "child-123"
    
    # Report safety violation
    violation_result = await cqrs.report_safety_violation(
        child_id=child_id,
        violation_type="inappropriate_content",
        details="Child used language not appropriate for their age",
        severity="medium",
        user_id="system"
    )
    
    if violation_result.success:
        print("✅ Safety violation reported:")
        print(f"   - Type: {violation_result.data['violation_type']}")
        print(f"   - Severity: {violation_result.data['severity']}")
        
        # Get safety report
        safety_report = await cqrs.get_child_safety_report(
            child_id=child_id,
            from_date=datetime.utcnow() - timedelta(days=30)
        )
        
        if safety_report.data:
            report = safety_report.data
            print("📊 Safety Report:")
            print(f"   - Total violations: {report['summary']['total_violations']}")
            print(f"   - Safety score: {report['summary']['safety_score']}")
            print(f"   - Status: {report['summary']['status']}")
            print(f"   - Recommendations: {len(report['recommendations'])} items")
    else:
        print(f"❌ Violation reporting failed: {violation_result.message}")


async def example_5_parent_dashboard():
    """Example 5: Parent dashboard with multiple children"""
    
    print("\n👨‍👩‍👧‍👦 Example 5: Parent Dashboard")
    print("-" * 50)
    
    cqrs = get_cqrs_service()
    parent_id = "parent-123"
    
    # Register multiple children for parent
    children_names = ["Emma", "Liam", "Sophie"]
    registered_children = []
    
    for i, name in enumerate(children_names):
        result = await cqrs.register_child(
            parent_id=parent_id,
            device_id=f"device-{i+1}",
            name=name,
            age=5 + i,
            udid=f"unique-device-{name.lower()}-{i+1}",
            user_id=parent_id
        )
        
        if result.success:
            registered_children.append(result.data['child_id'])
            print(f"✅ Registered {name} (ID: {result.data['child_id']})")
    
    # Get children for parent
    children_result = await cqrs.get_children_by_parent(
        parent_id=parent_id,
        page=1,
        page_size=10,
        user_id=parent_id
    )
    
    if children_result.data:
        print(f"\n📋 Parent Dashboard for {parent_id}:")
        print(f"   - Total children: {children_result.total_count}")
        
        for child in children_result.data:
            print(f"   • {child.get('name', 'Unknown')} (Age: {child.get('age', 'N/A')})")
            print(f"     - Conversations: {child.get('recent_conversations_count', 0)}")
            print(f"     - Safety: {child.get('safety_status', 'Unknown')}")
            print(f"     - Last activity: {child.get('last_activity', 'Never')}")


async def example_6_search_and_analytics():
    """Example 6: Search children and system analytics"""
    
    print("\n🔍 Example 6: Search and Analytics")
    print("-" * 50)
    
    cqrs = get_cqrs_service()
    
    # Search children by criteria
    search_results = await cqrs.search_children(
        search_term="Em",  # Find children with "Em" in name
        age_range=(6, 8),   # Ages 6-8
        parent_id=None      # Any parent
    )
    
    print(f"🔍 Search Results (name contains 'Em', age 6-8):")
    for child in search_results:
        print(f"   • {child['name']} (Age: {child['age']}, Parent: {child['parent_id']})")
        print(f"     - Engagement: {child['engagement_level']}")
        print(f"     - Safety: {child['safety_status']}")
    
    # Get system analytics
    analytics = await cqrs.get_system_analytics()
    
    print(f"\n📊 System Analytics:")
    print(f"   - Total children: {analytics['total_children']}")
    print(f"   - Total conversations: {analytics['total_conversations']}")
    print(f"   - Safety violations: {analytics['total_safety_violations']}")
    print(f"   - Average engagement: {analytics['average_engagement']:.2f}")
    print(f"   - Safety distribution: {analytics['safety_status_distribution']}")
    
    # Command bus status
    cmd_status = analytics['command_bus']
    print(f"   - Command handlers: {cmd_status['handlers_count']}")
    
    # Query bus status
    query_status = analytics['query_bus']
    print(f"   - Query handlers: {query_status['handlers_count']}")
    print(f"   - Cache entries: {query_status['cache_stats']['total_entries']}")


async def example_7_cqrs_health_monitoring():
    """Example 7: CQRS health monitoring and administration"""
    
    print("\n🏥 Example 7: CQRS Health Monitoring")
    print("-" * 50)
    
    cqrs = get_cqrs_service()
    
    # Get health status
    health = await cqrs.get_health_status()
    
    print(f"🏥 CQRS Health Status: {health['status'].upper()}")
    print(f"   - Initialized: {health['initialized']}")
    print(f"   - Checked at: {health['checked_at']}")
    
    components = health['components']
    
    # Command bus health
    cmd_health = components['command_bus']
    print(f"\n🚌 Command Bus:")
    print(f"   - Status: {cmd_health['status']}")
    print(f"   - Handlers: {cmd_health['handlers_count']}")
    print(f"   - Middleware: {cmd_health['middleware_count']}")
    
    # Query bus health
    query_health = components['query_bus']
    print(f"\n🔍 Query Bus:")
    print(f"   - Status: {query_health['status']}")
    print(f"   - Handlers: {query_health['handlers_count']}")
    
    cache_stats = query_health['cache_stats']
    print(f"   - Cache entries: {cache_stats['total_entries']}")
    print(f"   - Expired entries: {cache_stats['expired_entries']}")
    print(f"   - Hit rate: {cache_stats['hit_rate']:.2%}")
    
    # Projection manager health
    proj_health = components['projection_manager']
    print(f"\n📊 Projection Manager:")
    print(f"   - Status: {proj_health['status']}")
    print(f"   - Read models: {proj_health['read_models_count']}")
    print(f"   - Conversation summaries: {proj_health['conversation_summaries_count']}")
    
    # Clear caches
    print(f"\n🧹 Clearing all caches...")
    await cqrs.clear_all_caches()
    print("✅ Caches cleared")


async def example_8_error_handling():
    """Example 8: Error handling in CQRS operations"""
    
    print("\n❌ Example 8: Error Handling")
    print("-" * 50)
    
    cqrs = get_cqrs_service()
    
    # Try to register child with invalid data
    print("Testing invalid child registration...")
    invalid_result = await cqrs.register_child(
        parent_id="",  # Invalid parent ID
        device_id="device-test",
        name="",       # Invalid name
        age=15,        # Invalid age (too old)
        udid="short",  # Invalid UDID (too short)
        user_id="test"
    )
    
    if not invalid_result.success:
        print(f"✅ Validation caught invalid data: {invalid_result.message}")
    else:
        print(f"❌ Validation failed - invalid data was accepted")
    
    # Try to query non-existent child
    print("\nTesting query for non-existent child...")
    missing_profile = await cqrs.get_child_profile(
        child_id="non-existent-child",
        user_id="test"
    )
    
    if not missing_profile.data:
        print(f"✅ Query correctly returned no data for missing child")
        print(f"   Message: {missing_profile.metadata.get('message', 'No message')}")
    else:
        print(f"❌ Query returned data for non-existent child")
    
    # Try to update non-existent child
    print("\nTesting update for non-existent child...")
    missing_update = await cqrs.update_child_profile(
        child_id="non-existent-child",
        changes={"age": 8},
        user_id="test"
    )
    
    if not missing_update.success:
        print(f"✅ Update correctly failed for missing child: {missing_update.message}")
    else:
        print(f"❌ Update succeeded for non-existent child")


async def run_all_cqrs_examples():
    """Run all CQRS examples"""
    
    print("🚀 Starting CQRS Pattern Examples")
    print("=" * 60)
    
    try:
        await example_1_child_registration()
        await example_2_child_profile_queries()
        await example_3_profile_updates()
        await example_4_safety_violations()
        await example_5_parent_dashboard()
        await example_6_search_and_analytics()
        await example_7_cqrs_health_monitoring()
        await example_8_error_handling()
        
        print("\n" + "=" * 60)
        print("✅ All CQRS examples completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error running CQRS examples: {e}")
        logger.error(f"CQRS examples failed: {e}")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run examples
    asyncio.run(run_all_cqrs_examples()) 