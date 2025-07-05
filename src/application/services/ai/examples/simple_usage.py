#!/usr/bin/env python3
"""
🚀 Simple Usage Examples for LLM Services
أمثلة بسيطة لاستخدام خدمات LLM

This file demonstrates the new simplified interface for easy LLM usage.
"""

import asyncio
import sys
import os

# Add parent directory to path for standalone operation
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from src.application.services.ai import generate_simple, LLMServiceFactory, GenerationRequest
except ImportError:
    # If running standalone, import directly
    from llm_service_factory import generate_simple, LLMServiceFactory, GenerationRequest


async def example_super_simple():
    """مثال فائق البساطة - سطر واحد فقط"""
    print("🚀 Super Simple Example:")
    
    # Note: This would work with real LLM providers
    print("  This would call: await generate_simple('What is the capital of France?')")
    print("  Response: Paris (simulated)")


async def example_simple_with_options():
    """مثال بسيط مع خيارات إضافية"""
    print("\n🎯 Simple with Options Example:")
    
    # Note: This would work with real LLM providers
    print("  This would call: await generate_simple(...)")
    print("  Response: Quantum computing explanation (simulated)")


async def example_comparison():
    """مقارنة بين الواجهات المختلفة"""
    print("\n🆚 Interface Comparison:")
    
    # 1. Super Simple Interface (simulated)
    print("1. Super Simple:")
    print("   Result: Simulated response about Python...")
    
    # 2. Production Interface (simulated)
    print("\n2. Production Interface:")
    print("   Result: Simulated production response...")


async def main():
    """تشغيل جميع الأمثلة"""
    print("🧪 Testing LLM Simplified Interface\n")
    
    try:
        await example_super_simple()
        await example_simple_with_options() 
        await example_comparison()
        
        print("\n✅ All examples completed successfully!")
        print("Note: These are simulated responses.")
        print("With real LLM providers, you would get actual AI responses.")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 