"""
AI-Powered Testing Framework for AI Teddy Bear Project
====================================================

This package provides comprehensive AI-powered testing capabilities:
- AI test generation using GPT-4
- Smart fuzzing for security vulnerabilities
- Property-based testing with Hypothesis
- Child safety validation
- Performance regression detection
- Security penetration testing

Usage:
    from src.testing import AITestGenerator, SmartFuzzer
    
    generator = AITestGenerator()
    tests = await generator.generate_tests_for_module("core/ai/service.py")
"""

from .ai_test_generator import AITestGenerator
from .smart_fuzzer import SmartFuzzer
from .code_analyzer import CodeAnalyzer
from .coverage_tracker import CoverageTracker
from .test_validator import TestValidator
from .mutation_engine import MutationEngine
from .security_tester import SecurityTester
from .performance_tester import PerformanceTester

__all__ = [
    'AITestGenerator',
    'SmartFuzzer', 
    'CodeAnalyzer',
    'CoverageTracker',
    'TestValidator',
    'MutationEngine',
    'SecurityTester',
    'PerformanceTester'
]

__version__ = "1.0.0" 