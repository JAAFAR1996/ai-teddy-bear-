"""
Code Analyzer for AI Test Generation
===================================

Analyzes Python code to extract structure, dependencies,
complexity metrics, and security patterns for intelligent
test generation.
"""

import ast
import inspect
import importlib.util
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class FunctionAnalysis:
    """Analysis of a single function"""
    name: str
    line_number: int
    parameters: List[str]
    return_type: Optional[str]
    docstring: Optional[str]
    complexity: int
    has_async: bool
    raises_exceptions: List[str]
    calls_functions: List[str]
    security_concerns: List[str]
    child_safety_relevance: int  # 0-5 scale


@dataclass
class ClassAnalysis:
    """Analysis of a single class"""
    name: str
    line_number: int
    methods: List[FunctionAnalysis]
    parent_classes: List[str]
    docstring: Optional[str]
    complexity: int
    security_concerns: List[str]
    child_safety_relevance: int


@dataclass
class ModuleAnalysis:
    """Complete analysis of a Python module"""
    file_path: str
    imports: List[str]
    functions: List[FunctionAnalysis]
    classes: List[ClassAnalysis]
    global_variables: List[str]
    total_complexity: int
    security_score: int  # 0-100
    child_safety_score: int  # 0-100
    test_coverage_recommendations: List[str]
    code: str  # The actual source code


class CodeAnalyzer:
    """
    Analyzes Python code to extract structural and semantic
    information for intelligent test generation.
    """
    
    def __init__(self):
        # Child safety keywords
        self.child_safety_keywords = {
            'high_relevance': [
                'child', 'kid', 'age', 'content', 'safety', 'appropriate',
                'filter', 'moderate', 'toxic', 'harmful', 'emergency'
            ],
            'medium_relevance': [
                'user', 'input', 'response', 'message', 'conversation',
                'validate', 'check', 'process', 'analyze'
            ],
            'security_related': [
                'auth', 'permission', 'access', 'validate', 'sanitize',
                'encrypt', 'decrypt', 'secure', 'privacy', 'personal'
            ]
        }
        
        # Security vulnerability patterns
        self.security_patterns = {
            'injection': ['sql', 'query', 'execute', 'eval', 'exec'],
            'authentication': ['login', 'auth', 'token', 'session', 'password'],
            'authorization': ['permission', 'access', 'role', 'privilege'],
            'data_exposure': ['personal', 'private', 'sensitive', 'confidential'],
            'input_validation': ['input', 'validate', 'sanitize', 'filter'],
            'crypto': ['encrypt', 'decrypt', 'hash', 'secret', 'key']
        }
    
    async def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze a Python file and return comprehensive analysis
        
        Args:
            file_path: Path to the Python file to analyze
            
        Returns:
            Dictionary containing complete analysis results
        """
        try:
            # Read the source code
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            # Parse the AST
            tree = ast.parse(source_code)
            
            # Perform analysis
            analysis = ModuleAnalysis(
                file_path=file_path,
                imports=self._extract_imports(tree),
                functions=self._analyze_functions(tree, source_code),
                classes=self._analyze_classes(tree, source_code),
                global_variables=self._extract_global_variables(tree),
                total_complexity=0,  # Will be calculated
                security_score=0,    # Will be calculated
                child_safety_score=0, # Will be calculated
                test_coverage_recommendations=[],
                code=source_code
            )
            
            # Calculate metrics
            analysis.total_complexity = self._calculate_total_complexity(analysis)
            analysis.security_score = self._calculate_security_score(analysis)
            analysis.child_safety_score = self._calculate_child_safety_score(analysis)
            analysis.test_coverage_recommendations = self._generate_coverage_recommendations(analysis)
            
            logger.info(f"Analyzed {file_path}: complexity={analysis.total_complexity}, "
                       f"security={analysis.security_score}, safety={analysis.child_safety_score}")
            
            return asdict(analysis)
            
        except Exception as e:
            logger.error(f"Code analysis failed for {file_path}: {e}")
            raise
    
    def _extract_imports(self, tree: ast.AST) -> List[str]:
        """Extract all import statements"""
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")
        
        return imports
    
    def _analyze_functions(self, tree: ast.AST, source_code: str) -> List[FunctionAnalysis]:
        """Analyze all functions in the module"""
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                analysis = self._analyze_single_function(node, source_code)
                functions.append(analysis)
        
        return functions
    
    def _analyze_single_function(self, node: ast.FunctionDef, source_code: str) -> FunctionAnalysis:
        """Analyze a single function"""
        # Extract parameters
        parameters = [arg.arg for arg in node.args.args]
        
        # Extract return type annotation
        return_type = None
        if node.returns:
            return_type = ast.unparse(node.returns) if hasattr(ast, 'unparse') else str(node.returns)
        
        # Extract docstring
        docstring = ast.get_docstring(node)
        
        # Calculate complexity
        complexity = self._calculate_function_complexity(node)
        
        # Check if async
        has_async = isinstance(node, ast.AsyncFunctionDef)
        
        # Find exceptions raised
        exceptions = self._find_raised_exceptions(node)
        
        # Find function calls
        function_calls = self._find_function_calls(node)
        
        # Find security concerns
        security_concerns = self._find_security_concerns(node, source_code)
        
        # Calculate child safety relevance
        child_safety_relevance = self._calculate_child_safety_relevance(node, docstring or "")
        
        return FunctionAnalysis(
            name=node.name,
            line_number=node.lineno,
            parameters=parameters,
            return_type=return_type,
            docstring=docstring,
            complexity=complexity,
            has_async=has_async,
            raises_exceptions=exceptions,
            calls_functions=function_calls,
            security_concerns=security_concerns,
            child_safety_relevance=child_safety_relevance
        )
    
    def _analyze_classes(self, tree: ast.AST, source_code: str) -> List[ClassAnalysis]:
        """Analyze all classes in the module"""
        classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                analysis = self._analyze_single_class(node, source_code)
                classes.append(analysis)
        
        return classes
    
    def _analyze_single_class(self, node: ast.ClassDef, source_code: str) -> ClassAnalysis:
        """Analyze a single class"""
        # Analyze methods
        methods = []
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method_analysis = self._analyze_single_function(item, source_code)
                methods.append(method_analysis)
        
        # Extract parent classes
        parent_classes = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                parent_classes.append(base.id)
            elif isinstance(base, ast.Attribute):
                parent_classes.append(ast.unparse(base) if hasattr(ast, 'unparse') else str(base))
        
        # Extract docstring
        docstring = ast.get_docstring(node)
        
        # Calculate complexity
        complexity = sum(method.complexity for method in methods)
        
        # Find security concerns
        security_concerns = []
        for method in methods:
            security_concerns.extend(method.security_concerns)
        
        # Calculate child safety relevance
        child_safety_relevance = max(
            (method.child_safety_relevance for method in methods), 
            default=0
        )
        
        return ClassAnalysis(
            name=node.name,
            line_number=node.lineno,
            methods=methods,
            parent_classes=parent_classes,
            docstring=docstring,
            complexity=complexity,
            security_concerns=list(set(security_concerns)),
            child_safety_relevance=child_safety_relevance
        )
    
    def _extract_global_variables(self, tree: ast.AST) -> List[str]:
        """Extract global variable assignments"""
        variables = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        variables.append(target.id)
        
        return variables
    
    def _calculate_function_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of a function"""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            # Control flow statements increase complexity
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 1
            elif isinstance(child, ast.Lambda):
                complexity += 1
        
        return complexity
    
    def _find_raised_exceptions(self, node: ast.FunctionDef) -> List[str]:
        """Find exceptions that can be raised by the function"""
        exceptions = []
        
        for child in ast.walk(node):
            if isinstance(child, ast.Raise):
                if child.exc:
                    if isinstance(child.exc, ast.Name):
                        exceptions.append(child.exc.id)
                    elif isinstance(child.exc, ast.Call) and isinstance(child.exc.func, ast.Name):
                        exceptions.append(child.exc.func.id)
        
        return exceptions
    
    def _find_function_calls(self, node: ast.FunctionDef) -> List[str]:
        """Find function calls within the function"""
        calls = []
        
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    calls.append(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    calls.append(child.func.attr)
        
        return calls
    
    def _find_security_concerns(self, node: ast.FunctionDef, source_code: str) -> List[str]:
        """Find potential security concerns in the function"""
        concerns = []
        
        # Get function source
        function_source = ast.get_source_segment(source_code, node) or ""
        function_source_lower = function_source.lower()
        
        # Check for security patterns
        for concern_type, keywords in self.security_patterns.items():
            if any(keyword in function_source_lower for keyword in keywords):
                concerns.append(concern_type)
        
        # Check for dangerous function calls
        dangerous_calls = ['eval', 'exec', 'compile', '__import__']
        for child in ast.walk(node):
            if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                if child.func.id in dangerous_calls:
                    concerns.append("dangerous_execution")
        
        return concerns
    
    def _calculate_child_safety_relevance(self, node: ast.FunctionDef, docstring: str) -> int:
        """Calculate child safety relevance score (0-5)"""
        content = f"{node.name} {docstring}".lower()
        
        score = 0
        
        # High relevance keywords
        for keyword in self.child_safety_keywords['high_relevance']:
            if keyword in content:
                score += 2
        
        # Medium relevance keywords
        for keyword in self.child_safety_keywords['medium_relevance']:
            if keyword in content:
                score += 1
        
        # Security related keywords (important for child safety)
        for keyword in self.child_safety_keywords['security_related']:
            if keyword in content:
                score += 1
        
        # Cap at 5
        return min(score, 5)
    
    def _calculate_total_complexity(self, analysis: ModuleAnalysis) -> int:
        """Calculate total module complexity"""
        total = 0
        
        # Add function complexities
        for func in analysis.functions:
            total += func.complexity
        
        # Add class complexities
        for cls in analysis.classes:
            total += cls.complexity
        
        return total
    
    def _calculate_security_score(self, analysis: ModuleAnalysis) -> int:
        """Calculate security score (0-100, higher is better)"""
        base_score = 100
        
        # Deduct points for security concerns
        all_concerns = []
        
        for func in analysis.functions:
            all_concerns.extend(func.security_concerns)
        
        for cls in analysis.classes:
            all_concerns.extend(cls.security_concerns)
        
        # Deduct points based on concern types
        concern_penalties = {
            'injection': 20,
            'dangerous_execution': 15,
            'authentication': 10,
            'authorization': 10,
            'data_exposure': 15,
            'input_validation': 5,
            'crypto': 5
        }
        
        for concern in set(all_concerns):
            penalty = concern_penalties.get(concern, 5)
            base_score -= penalty
        
        return max(base_score, 0)
    
    def _calculate_child_safety_score(self, analysis: ModuleAnalysis) -> int:
        """Calculate child safety score (0-100, higher is better)"""
        total_relevance = 0
        max_possible = 0
        
        # Calculate based on function relevance
        for func in analysis.functions:
            total_relevance += func.child_safety_relevance
            max_possible += 5  # Max relevance per function
        
        # Calculate based on class relevance
        for cls in analysis.classes:
            total_relevance += cls.child_safety_relevance
            max_possible += 5  # Max relevance per class
        
        if max_possible == 0:
            return 50  # Neutral score if no functions/classes
        
        # Convert to 0-100 scale
        score = (total_relevance / max_possible) * 100
        return int(score)
    
    def _generate_coverage_recommendations(self, analysis: ModuleAnalysis) -> List[str]:
        """Generate test coverage recommendations"""
        recommendations = []
        
        # Check for high complexity functions
        for func in analysis.functions:
            if func.complexity > 5:
                recommendations.append(
                    f"High complexity function '{func.name}' (complexity: {func.complexity}) "
                    "needs comprehensive testing including edge cases"
                )
        
        # Check for security-sensitive functions
        for func in analysis.functions:
            if func.security_concerns:
                recommendations.append(
                    f"Security-sensitive function '{func.name}' needs penetration testing "
                    f"for: {', '.join(func.security_concerns)}"
                )
        
        # Check for child safety critical functions
        for func in analysis.functions:
            if func.child_safety_relevance >= 3:
                recommendations.append(
                    f"Child safety critical function '{func.name}' needs extensive "
                    "age-appropriateness and content filtering tests"
                )
        
        # Check for async functions
        async_functions = [f for f in analysis.functions if f.has_async]
        if async_functions:
            recommendations.append(
                f"Async functions need concurrency and performance testing: "
                f"{', '.join(f.name for f in async_functions)}"
            )
        
        # Check for exception handling
        functions_with_exceptions = [f for f in analysis.functions if f.raises_exceptions]
        if functions_with_exceptions:
            recommendations.append(
                "Functions that raise exceptions need error handling tests: "
                f"{', '.join(f.name for f in functions_with_exceptions)}"
            )
        
        return recommendations 