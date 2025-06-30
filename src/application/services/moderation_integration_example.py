import logging

logger = logging.getLogger(__name__)

"""
🔗 Moderation Service Integration Example
How to integrate the new modern moderation service into existing codebase
"""

import asyncio
from typing import Optional
from openai import AsyncOpenAI

from application.services.moderation_service_modern import (
    ModernModerationService,
    ModerationConfig,
    create_moderation_service
)

# ================== INTEGRATION WITH DI CONTAINER ==================

async def setup_moderation_in_container():
    """Example: Add moderation service to DI container"""
    
    # Method 1: Using factory function
    moderation_service = await create_moderation_service(
        openai_api_key="your-openai-api-key-here",  # From environment
        config=ModerationConfig(
            enable_ai_fallback=True,
            ai_threshold_chars=25,
            strict_mode_age=13
        )
    )
    
    # Method 2: Manual initialization
    openai_client = AsyncOpenAI(api_key="your-openai-api-key")
    moderation_service = ModernModerationService(
        openai_client=openai_client,
        config=ModerationConfig()
    )
    
    return moderation_service

# ================== INTEGRATION WITH API ENDPOINTS ==================

async def api_endpoint_example(content: str, user_age: int):
    """Example: Use in API endpoint"""
    
    # Get moderation service from container
    moderation_service = await setup_moderation_in_container()
    
    # Moderate content
    result = await moderation_service.moderate_content(
        text=content,
        user_age=user_age,
        use_ai=True  # Force AI check for this endpoint
    )
    
    if not result['safe']:
        return {
            "error": "Content not allowed",
            "reason": f"Flagged for: {', '.join(result['flags'])}",
            "confidence": result['confidence']
        }
    
    # Content is safe, proceed with normal processing
    return {"message": "Content approved", "processed": content}

# ================== INTEGRATION WITH VOICE SERVICE ==================

async def voice_interaction_moderation(text: str, child_age: int):
    """Example: Integrate with voice interaction service"""
    
    moderation_service = await setup_moderation_in_container()
    
    # Quick safety check
    is_safe = await moderation_service.is_content_safe(text, child_age)
    
    if not is_safe:
        # Generate safe fallback response
        return {
            "response": f"I didn't understand that. Let's talk about something fun instead!",
            "moderated": True
        }
    
    # Process normally
    return {"response": text, "moderated": False}

# ================== CUSTOM PATTERNS EXAMPLE ==================

async def add_custom_moderation_rules():
    """Example: Add custom moderation patterns"""
    
    moderation_service = await setup_moderation_in_container()
    
    # Add custom patterns for specific use cases
    custom_patterns = [
        ("credit_card", r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b"),
        ("social_security", r"\b\d{3}-\d{2}-\d{4}\b"),
        ("custom_profanity", r"\b(custom|bad|words)\b")
    ]
    
    for name, pattern in custom_patterns:
        success = moderation_service.add_custom_pattern(name, pattern)
        logger.error(f"Added pattern '{name}': {'✅' if success else '❌'}")

# ================== MONITORING AND STATS ==================

async def moderation_monitoring():
    """Example: Monitor moderation service performance"""
    
    moderation_service = await setup_moderation_in_container()
    
    # Get performance stats
    stats = await moderation_service.get_moderation_stats()
    logger.info(f"📊 Moderation Stats: {stats}")
    
    # Health check
    health = await moderation_service.health_check()
    logger.info(f"💚 Health Status: {health}")
    
    # Example: Log to monitoring system
    if health['service'] != 'healthy':
        logger.info("🚨 Alert: Moderation service degraded!")

# ================== BATCH PROCESSING EXAMPLE ==================

async def batch_moderate_content(content_list, user_age: int = 10):
    """Example: Batch moderation for multiple content items"""
    
    moderation_service = await setup_moderation_in_container()
    
    results = []
    for content in content_list:
        result = await moderation_service.moderate_content(content, user_age)
        results.append({
            "content": content[:50] + "..." if len(content) > 50 else content,
            "safe": result['safe'],
            "flags": result['flags'],
            "method": result['method']
        })
    
    return results

# ================== MAIN DEMO ==================

async def main_demo():
    """Complete integration demo"""
    
    logger.info("🚀 Modern Moderation Service Integration Demo")
    
    # Test API endpoint integration
    logger.info("\n1️⃣ API Endpoint Test:")
    api_result = await api_endpoint_example("Hello, my friend!", 10)
    logger.info(f"   Result: {api_result}")
    
    # Test voice integration
    logger.info("\n2️⃣ Voice Integration Test:")
    voice_result = await voice_interaction_moderation("I hate you!", 8)
    logger.info(f"   Result: {voice_result}")
    
    # Test custom patterns
    logger.info("\n3️⃣ Custom Patterns:")
    await add_custom_moderation_rules()
    
    # Test monitoring
    logger.info("\n4️⃣ Monitoring:")
    await moderation_monitoring()
    
    # Test batch processing
    logger.info("\n5️⃣ Batch Processing:")
    test_content = [
        "Hello world!",
        "I hate you stupid",
        "Call me at 555-123-4567",
        "Let's play a game!"
    ]
    batch_results = await batch_moderate_content(test_content)
    for result in batch_results:
        status = "✅" if result['safe'] else "❌"
        logger.info(f"   {status} {result['content']}: {result['flags']}")

if __name__ == "__main__":
    # Run the demo (without actual API keys)
    logger.info("📋 Integration example created successfully!")
    logger.info("💡 To run demo: python moderation_integration_example.py")