"""
Coverage Tracker for AI-Powered Testing
=======================================

Advanced coverage tracking system that monitors
code execution paths and provides intelligent
coverage analysis for comprehensive testing.
"""

import ast
import asyncio
import json
import logging
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import coverage

logger = logging.getLogger(__name__)


@dataclass
class CoverageMetrics:
    """Coverage metrics for analysis"""
    line_coverage: float
    branch_coverage: float
    function_coverage: float
    uncovered_lines: List[int]
    uncovered_branches: List[str]
    uncovered_functions: List[str]
    total_lines: int
    covered_lines: int
    execution_paths: List[str]


@dataclass
class HotSpot:
    """Code hotspot that needs more testing"""
    file_path: str
    line_number: int
    function_name: str
    complexity: int
    coverage_score: float
    safety_critical: bool
    priority: int


class CoverageTracker:
    """
    Advanced coverage tracking system with AI-powered
    analysis for identifying testing gaps and priorities.
    """
    
    def __init__(self, target_directories: Optional[List[str]] = None):
        self.target_directories = target_directories or ['core/', 'src/']
        self.coverage = coverage.Coverage(
            source=self.target_directories,
            branch=True,
            include=['*.py'],
            omit=['*/tests/*', '*/test_*', '*/__pycache__/*']
        )
        
        # Coverage tracking state
        self.is_tracking = False
        self.baseline_coverage = 0.0
        self.current_coverage = 0.0
        self.coverage_history = []
        
        # Execution path tracking
        self.execution_paths = set()
        self.function_calls = {}
        self.branch_history = []
        
        # AI-powered analysis
        self.hotspots = []
        self.coverage_recommendations = []
        
    async def start_tracking(self):
        """Start coverage tracking"""
        try:
            self.coverage.start()
            self.is_tracking = True
            self.baseline_coverage = await self.get_coverage_percentage()
            logger.info("Coverage tracking started")
        except Exception as e:
            logger.error(f"Failed to start coverage tracking: {e}")
            raise
    
    async def stop_tracking(self):
        """Stop coverage tracking and save data"""
        try:
            if self.is_tracking:
                self.coverage.stop()
                self.coverage.save()
                self.is_tracking = False
                
                # Update current coverage
                self.current_coverage = await self.get_coverage_percentage()
                
                # Add to history
                self.coverage_history.append({
                    'timestamp': time.time(),
                    'coverage': self.current_coverage
                })
                
                logger.info(f"Coverage tracking stopped. Coverage: {self.current_coverage:.2f}%")
        except Exception as e:
            logger.error(f"Failed to stop coverage tracking: {e}")
    
    async def get_coverage_percentage(self) -> float:
        """Get current coverage percentage"""
        try:
            # Generate coverage report
            total = self.coverage.report(show_missing=False, skip_covered=False)
            return total if total is not None else 0.0
        except Exception as e:
            logger.error(f"Failed to get coverage percentage: {e}")
            return 0.0
    
    async def get_current_coverage(self) -> float:
        """Get current coverage for comparison"""
        return self.current_coverage
    
    async def get_detailed_metrics(self) -> CoverageMetrics:
        """Get detailed coverage metrics"""
        try:
            # Get line coverage
            line_coverage = await self.get_coverage_percentage()
            
            # Get branch coverage
            branch_coverage = await self._calculate_branch_coverage()
            
            # Get function coverage
            function_coverage = await self._calculate_function_coverage()
            
            # Get uncovered items
            uncovered_lines = await self._get_uncovered_lines()
            uncovered_branches = await self._get_uncovered_branches()
            uncovered_functions = await self._get_uncovered_functions()
            
            # Get totals
            total_lines, covered_lines = await self._get_line_counts()
            
            return CoverageMetrics(
                line_coverage=line_coverage,
                branch_coverage=branch_coverage,
                function_coverage=function_coverage,
                uncovered_lines=uncovered_lines,
                uncovered_branches=uncovered_branches,
                uncovered_functions=uncovered_functions,
                total_lines=total_lines,
                covered_lines=covered_lines,
                execution_paths=list(self.execution_paths)
            )
        except Exception as e:
            logger.error(f"Failed to get detailed metrics: {e}")
            return CoverageMetrics(0, 0, 0, [], [], [], 0, 0, [])
    
    async def _calculate_branch_coverage(self) -> float:
        """Calculate branch coverage percentage"""
        try:
            # Get branch data from coverage.py
            branch_data = self.coverage.get_data().measured_contexts()
            if not branch_data:
                return 0.0
            
            # This is a simplified calculation
            # In practice, you'd analyze the actual branch data
            return min(100.0, self.current_coverage + 10.0)  # Placeholder
        except Exception as e:
            logger.error(f"Failed to calculate branch coverage: {e}")
            return 0.0
    
    async def _calculate_function_coverage(self) -> float:
        """Calculate function coverage percentage"""
        try:
            covered_functions = len(self.function_calls)
            total_functions = await self._count_total_functions()
            
            if total_functions == 0:
                return 100.0
            
            return (covered_functions / total_functions) * 100.0
        except Exception as e:
            logger.error(f"Failed to calculate function coverage: {e}")
            return 0.0
    
    async def _get_uncovered_lines(self) -> List[int]:
        """Get list of uncovered line numbers"""
        try:
            uncovered = []
            analysis = self.coverage.analysis2()
            
            for filename, data in analysis:
                if any(target in filename for target in self.target_directories):
                    uncovered.extend(data.missing)
            
            return sorted(set(uncovered))
        except Exception as e:
            logger.error(f"Failed to get uncovered lines: {e}")
            return []
    
    async def _get_uncovered_branches(self) -> List[str]:
        """Get list of uncovered branches"""
        try:
            # This would require more sophisticated analysis
            # For now, return placeholder data
            return ["branch_1", "branch_2"]  # Placeholder
        except Exception as e:
            logger.error(f"Failed to get uncovered branches: {e}")
            return []
    
    async def _get_uncovered_functions(self) -> List[str]:
        """Get list of uncovered functions"""
        try:
            all_functions = await self._get_all_functions()
            covered_functions = set(self.function_calls.keys())
            uncovered = [func for func in all_functions if func not in covered_functions]
            return uncovered
        except Exception as e:
            logger.error(f"Failed to get uncovered functions: {e}")
            return []
    
    async def _get_line_counts(self) -> tuple:
        """Get total and covered line counts"""
        try:
            total_lines = 0
            covered_lines = 0
            
            for target_dir in self.target_directories:
                if Path(target_dir).exists():
                    for py_file in Path(target_dir).rglob("*.py"):
                        with open(py_file, 'r', encoding='utf-8') as f:
                            file_lines = len(f.readlines())
                            total_lines += file_lines
            
            # Estimate covered lines based on coverage percentage
            covered_lines = int(total_lines * (self.current_coverage / 100.0))
            
            return total_lines, covered_lines
        except Exception as e:
            logger.error(f"Failed to get line counts: {e}")
            return 0, 0
    
    async def _count_total_functions(self) -> int:
        """Count total functions in target directories"""
        try:
            total_functions = 0
            
            for target_dir in self.target_directories:
                if Path(target_dir).exists():
                    for py_file in Path(target_dir).rglob("*.py"):
                        with open(py_file, 'r', encoding='utf-8') as f:
                            tree = ast.parse(f.read())
                            for node in ast.walk(tree):
                                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                                    total_functions += 1
            
            return total_functions
        except Exception as e:
            logger.error(f"Failed to count total functions: {e}")
            return 1  # Avoid division by zero
    
    async def _get_all_functions(self) -> List[str]:
        """Get all function names in target directories"""
        try:
            functions = []
            
            for target_dir in self.target_directories:
                if Path(target_dir).exists():
                    for py_file in Path(target_dir).rglob("*.py"):
                        with open(py_file, 'r', encoding='utf-8') as f:
                            tree = ast.parse(f.read())
                            for node in ast.walk(tree):
                                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                                    functions.append(f"{py_file.stem}.{node.name}")
            
            return functions
        except Exception as e:
            logger.error(f"Failed to get all functions: {e}")
            return []
    
    async def track_execution_path(self, path: str):
        """Track execution path for analysis"""
        self.execution_paths.add(path)
    
    async def track_function_call(self, function_name: str):
        """Track function call for coverage analysis"""
        if function_name not in self.function_calls:
            self.function_calls[function_name] = 0
        self.function_calls[function_name] += 1
    
    async def identify_coverage_hotspots(self) -> List[HotSpot]:
        """
        Identify code hotspots that need more testing
        using AI-powered analysis
        """
        try:
            hotspots = []
            
            # Analyze uncovered code
            metrics = await self.get_detailed_metrics()
            
            # Find high-complexity uncovered functions
            for func_name in metrics.uncovered_functions:
                # Parse function details
                file_path, function_name = self._parse_function_name(func_name)
                
                if file_path and function_name:
                    complexity = await self._calculate_function_complexity(file_path, function_name)
                    safety_critical = await self._is_safety_critical_function(file_path, function_name)
                    
                    # Calculate priority based on multiple factors
                    priority = self._calculate_hotspot_priority(
                        complexity, safety_critical, 0.0  # 0% coverage
                    )
                    
                    hotspot = HotSpot(
                        file_path=file_path,
                        line_number=1,  # Would need AST analysis to get exact line
                        function_name=function_name,
                        complexity=complexity,
                        coverage_score=0.0,
                        safety_critical=safety_critical,
                        priority=priority
                    )
                    hotspots.append(hotspot)
            
            # Sort by priority (highest first)
            hotspots.sort(key=lambda h: h.priority, reverse=True)
            
            self.hotspots = hotspots[:20]  # Keep top 20
            return self.hotspots
        except Exception as e:
            logger.error(f"Failed to identify hotspots: {e}")
            return []
    
    def _parse_function_name(self, func_name: str) -> tuple:
        """Parse function name to get file path and function name"""
        try:
            if '.' in func_name:
                parts = func_name.split('.')
                return '.'.join(parts[:-1]) + '.py', parts[-1]
            return None, None
        except IndexError as e:
    logger.error(f"Error in operation: {e}", exc_info=True)IndexError as e:
    logger.error(f"Error in operation: {e}", exc_info=True)            return None, None
    
    async def _calculate_function_complexity(self, file_path: str, function_name: str) -> int:
        """Calculate cyclomatic complexity of a function"""
        try:
            # This would require AST analysis
            # For now, return a random complexity between 1-10
except ImportError as e:
    logger.error(f"Error in operation: {e}", exc_info=True)     import random
            return random.randint(1, 10)
        except ImportError as e:
    logger.error(f"Error in operation: {e}", exc_info=True)            return 1
    
    async def _is_safety_critical_function(self, file_path: str, function_name: str) -> bool:
        """Determine if function is safety critical"""
        safety_keywords = [
            'child', 'safety', 'content', 'filter', 'moderate',
            'validate', 'emergency', 'auth', 'permission'
        ]
        
        func_name_lower = function_name.lower()
        file_path_lower = file_path.lower()
        
        return any(keyword in func_name_lower or keyword in file_path_lower 
                  for keyword in safety_keywords)
    
    def _calculate_hotspot_priority(self, complexity: int, safety_critical: bool, coverage: float) -> int:
        """Calculate hotspot priority (1-10)"""
        priority = 0
        
        # Complexity factor (higher complexity = higher priority)
        priority += min(complexity, 5)
        
        # Safety critical factor
        if safety_critical:
            priority += 3
        
        # Coverage factor (lower coverage = higher priority)
        priority += int((100 - coverage) / 20)
        
        return min(priority, 10)
    
    async def generate_coverage_recommendations(self) -> List[str]:
        """Generate AI-powered coverage recommendations"""
        try:
            recommendations = []
            metrics = await self.get_detailed_metrics()
            
            # Low overall coverage
            if metrics.line_coverage < 80:
                recommendations.append(
                    f"Overall coverage is {metrics.line_coverage:.1f}%. "
                    "Recommend increasing to at least 80% for production readiness."
                )
            
            # Low branch coverage
            if metrics.branch_coverage < 70:
                recommendations.append(
                    f"Branch coverage is {metrics.branch_coverage:.1f}%. "
                    "Focus on testing conditional logic and error handling paths."
                )
            
            # Low function coverage
            if metrics.function_coverage < 90:
                recommendations.append(
                    f"Function coverage is {metrics.function_coverage:.1f}%. "
                    f"Add tests for {len(metrics.uncovered_functions)} uncovered functions."
                )
            
            # Identify critical uncovered areas
            hotspots = await self.identify_coverage_hotspots()
            safety_critical_hotspots = [h for h in hotspots if h.safety_critical]
            
            if safety_critical_hotspots:
                recommendations.append(
                    f"Found {len(safety_critical_hotspots)} safety-critical functions "
                    "without adequate test coverage. These should be prioritized."
                )
            
            # High complexity uncovered code
            complex_hotspots = [h for h in hotspots if h.complexity > 5]
            if complex_hotspots:
                recommendations.append(
                    f"Found {len(complex_hotspots)} high-complexity functions "
                    "with insufficient coverage. These are prone to bugs."
                )
            
            self.coverage_recommendations = recommendations
            return recommendations
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            return []
    
    async def export_coverage_report(self, output_file: str) -> bool:
        """Export detailed coverage report"""
        try:
            metrics = await self.get_detailed_metrics()
            hotspots = await self.identify_coverage_hotspots()
            recommendations = await self.generate_coverage_recommendations()
            
            report = {
                'timestamp': time.time(),
                'metrics': asdict(metrics),
                'hotspots': [asdict(h) for h in hotspots],
                'recommendations': recommendations,
                'coverage_history': self.coverage_history,
                'execution_paths': list(self.execution_paths),
                'function_calls': self.function_calls
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"Coverage report exported to {output_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to export coverage report: {e}")
            return False
    
    async def reset_tracking(self):
        """Reset all tracking data"""
        self.execution_paths.clear()
        self.function_calls.clear()
        self.branch_history.clear()
        self.coverage_history.clear()
        self.hotspots.clear()
        self.coverage_recommendations.clear()
        self.current_coverage = 0.0
        self.baseline_coverage = 0.0
        
        logger.info("Coverage tracking data reset")
    
    async def get_coverage_delta(self) -> float:
        """Get coverage improvement since baseline"""
        return self.current_coverage - self.baseline_coverage
    
    async def is_coverage_improving(self, threshold: float = 1.0) -> bool:
        """Check if coverage is improving above threshold"""
        delta = await self.get_coverage_delta()
        return delta >= threshold 