#!/usr/bin/env python3
"""
🚀 Simple Usage Examples for LLM Services
أمثلة بسيطة لاستخدام خدمات LLM

This file demonstrates the new simplified interface for easy LLM usage.
"""

import asyncio
from src.application.services.ai import generate_simple, LLMServiceFactory, GenerationRequest


async def example_super_simple():
    """مثال فائق البساطة - سطر واحد فقط"""
    print("🚀 Super Simple Example:")
    
    response = await generate_simple("What is the capital of France?")
    print(f"Response: {response}")


async def example_simple_with_options():
    """مثال بسيط مع خيارات إضافية"""
    print("\n🎯 Simple with Options Example:")
    
    response = await generate_simple(
        "Explain quantum computing in simple terms",
        provider="anthropic",
        temperature=0.8,
        max_tokens=200
    )
    print(f"Response: {response}")


async def example_comparison():
    """مقارنة بين الواجهات المختلفة"""
    print("\n🆚 Interface Comparison:")
    
    prompt = "What is Python programming?"
    
    # 1. Super Simple Interface
    print("1. Super Simple:")
    simple_response = await generate_simple(prompt)
    print(f"   Result: {simple_response[:100]}...")
    
    # 2. Production Interface (using the existing factory)
    print("\n2. Production Interface:")
    from src.core.domain.entities.conversation import Conversation, Message
    
    message = Message(content=prompt, role="user")
    conversation = Conversation(messages=[message])
    
    factory = await LLMServiceFactory().initialize()
    request = GenerationRequest(conversation=conversation)
    production_response = await factory.generate_response(request)
    print(f"   Result: {production_response[:100]}...")


async def main():
    """تشغيل جميع الأمثلة"""
    print("🧪 Testing LLM Simplified Interface\n")
    
    try:
        await example_super_simple()
        await example_simple_with_options() 
        await example_comparison()
        
        print("\n✅ All examples completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 