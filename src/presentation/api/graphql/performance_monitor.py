from typing import Any, Dict, List, Optional

"""
Performance Monitoring for GraphQL Federation.

This module provides comprehensive performance monitoring, metrics collection,
and query optimization for the federated GraphQL system.

API Team Implementation - Task 13
Author: API Team Lead
"""

from .performance import GraphQLPerformanceMonitor, QueryComplexityAnalyzer


# Factory function
def create_performance_monitor(
    enable_prometheus: bool = True,
) -> GraphQLPerformanceMonitor:
    """Create GraphQL performance monitor."""
    return GraphQLPerformanceMonitor(enable_prometheus)
