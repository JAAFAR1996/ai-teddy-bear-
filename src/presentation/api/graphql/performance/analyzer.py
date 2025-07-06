import logging
from typing import Any, Dict, List

try:
    from graphql import parse
    GRAPHQL_AVAILABLE = True
except ImportError:
    GRAPHQL_AVAILABLE = False

logger = logging.getLogger(__name__)


class QueryComplexityAnalyzer:
    """Analyze GraphQL query complexity for performance optimization."""

    def __init__(self, max_complexity: int = 1000):
        self.max_complexity = max_complexity
        self.field_costs = self._initialize_field_costs()
        self.logger = logging.getLogger(
            f"{__name__}.{self.__class__.__name__}")

    def _initialize_field_costs(self) -> Dict[str, int]:
        """Initialize field cost mapping."""
        return {
            # Basic fields
            "id": 1,
            "name": 1,
            "email": 1,
            "createdAt": 1,
            # Complex fields
            "conversations": 10,
            "aiProfile": 15,
            "emotionHistory": 20,
            "usage": 25,
            "parentalReports": 30,
            # Very expensive fields
            "aiAnalysis": 50,
            "safetyCheck": 40,
            "performance": 35,
        }

    def analyze_complexity(self, query: str) -> Dict[str, Any]:
        """Analyze query complexity."""
        if not GRAPHQL_AVAILABLE:
            return {
                "complexity": 0,
                "analysis": "GraphQL library not available"}

        try:
            # Parse query
            document = parse(query)

            # Calculate complexity
            complexity = self._calculate_complexity(document)

            # Generate analysis
            analysis = {
                "total_complexity": complexity,
                "max_allowed": self.max_complexity,
                "is_allowed": complexity <= self.max_complexity,
                "complexity_ratio": complexity / self.max_complexity,
                "recommendations": self._generate_complexity_recommendations(
                    complexity
                ),
            }

            return analysis

        except Exception as e:
            self.logger.error(f"Query complexity analysis failed: {e}")
            return {"complexity": float("inf"), "error": str(e)}

    def _calculate_complexity(self, document) -> int:
        """Calculate query complexity score."""
        # Simplified complexity calculation
        # In production, use a proper GraphQL complexity analyzer

        complexity = 0

        # Count field selections and apply costs
        for definition in document.definitions:
            if hasattr(definition, "selection_set"):
                complexity += self._calculate_selection_complexity(
                    definition.selection_set
                )

        return complexity

    def _calculate_selection_complexity(
            self, selection_set, depth: int = 0) -> int:
        """Calculate complexity for selection set."""
        if not selection_set or depth > 10:  # Prevent infinite recursion
            return 0

        complexity = 0
        depth_multiplier = 1 + (depth * 0.5)  # Increase cost with depth

        for selection in selection_set.selections:
            field_name = getattr(selection, "name", {}).get("value", "unknown")
            field_cost = self.field_costs.get(field_name, 5)  # Default cost

            complexity += field_cost * depth_multiplier

            # Add nested selection complexity
            if hasattr(selection, "selection_set") and selection.selection_set:
                complexity += self._calculate_selection_complexity(
                    selection.selection_set, depth + 1
                )

        return int(complexity)

    def _generate_complexity_recommendations(
            self, complexity: int) -> List[str]:
        """Generate recommendations for complex queries."""
        recommendations = []

        if complexity > self.max_complexity:
            recommendations.append(
                f"Query complexity ({complexity}) exceeds limit ({self.max_complexity})"
            )
            recommendations.append(
                "Consider breaking the query into smaller parts")
            recommendations.append("Use pagination for list fields")
            recommendations.append("Remove unnecessary fields from selection")

        elif complexity > self.max_complexity * 0.8:
            recommendations.append("Query is approaching complexity limit")
            recommendations.append("Consider optimizing field selections")

        return recommendations
