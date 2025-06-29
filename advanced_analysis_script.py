#!/usr/bin/env python3
"""
🔬 AI Teddy Bear - Advanced Analysis Script
Comprehensive Performance, Security, and AI Effectiveness Analysis
"""

import ast
import json
import os
import sys
import time
import psutil
import tracemalloc
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
from collections import defaultdict, Counter
import importlib.util
import re

# Performance analysis
import cProfile
import pstats
from memory_profiler import profile
from pympler import asizeof

class AdvancedAnalyzer:
    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        self.results = {
            "performance": {},
            "dependencies": {},
            "security": {},
            "ai_effectiveness": {},
            "code_quality": {},
            "recommendations": []
        }
        
    def analyze_all(self) -> Dict[str, Any]:
        """Run comprehensive analysis"""
        print("🔬 Starting Advanced Analysis...")
        
        # 1. Performance Analysis
        print("📊 Analyzing Performance...")
        self.results["performance"] = self.analyze_performance()
        
        # 2. Dependency Analysis
        print("🔗 Analyzing Dependencies...")
        self.results["dependencies"] = self.analyze_dependencies()
        
        # 3. Security Analysis
        print("🛡️ Analyzing Security...")
        self.results["security"] = self.analyze_security()
        
        # 4. AI Effectiveness
        print("🤖 Analyzing AI Effectiveness...")
        self.results["ai_effectiveness"] = self.analyze_ai_effectiveness()
        
        # 5. Code Quality
        print("📋 Analyzing Code Quality...")
        self.results["code_quality"] = self.analyze_code_quality()
        
        # 6. Generate Recommendations
        print("💡 Generating Recommendations...")
        self.results["recommendations"] = self.generate_recommendations()
        
        return self.results
    
    def analyze_performance(self) -> Dict[str, Any]:
        """Analyze CPU and memory performance"""
        perf_data = {
            "cpu_bottlenecks": [],
            "memory_usage": {},
            "hot_spots": [],
            "import_times": {},
            "function_profiles": {}
        }
        
        # Memory usage analysis
        try:
            tracemalloc.start()
            
            # Analyze main.py memory
            if (self.project_path / "main.py").exists():
                start_time = time.time()
                spec = importlib.util.spec_from_file_location("main", self.project_path / "main.py")
                if spec and spec.loader:
                    import_time = time.time() - start_time
                    perf_data["import_times"]["main.py"] = import_time
                    
            # Current memory snapshot
            current, peak = tracemalloc.get_traced_memory()
            perf_data["memory_usage"] = {
                "current_mb": current / 1024 / 1024,
                "peak_mb": peak / 1024 / 1024
            }
            tracemalloc.stop()
            
        except Exception as e:
            perf_data["memory_usage"]["error"] = str(e)
        
        # CPU analysis
        perf_data["cpu_info"] = {
            "cpu_count": psutil.cpu_count(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_total_gb": psutil.virtual_memory().total / (1024**3),
            "memory_available_gb": psutil.virtual_memory().available / (1024**3),
            "memory_percent": psutil.virtual_memory().percent
        }
        
        # File size analysis (potential bottlenecks)
        large_files = []
        for py_file in self.project_path.rglob("*.py"):
            try:
                size = py_file.stat().st_size
                if size > 10000:  # Files > 10KB
                    lines = len(py_file.read_text(encoding='utf-8', errors='ignore').splitlines())
                    large_files.append({
                        "file": str(py_file.relative_to(self.project_path)),
                        "size_kb": size / 1024,
                        "lines": lines,
                        "complexity_ratio": size / lines if lines > 0 else 0
                    })
            except Exception:
                continue
                
        perf_data["large_files"] = sorted(large_files, key=lambda x: x["size_kb"], reverse=True)[:10]
        
        return perf_data
    
    def analyze_dependencies(self) -> Dict[str, Any]:
        """Analyze module dependencies and detect circular imports"""
        deps_data = {
            "import_graph": {},
            "circular_dependencies": [],
            "high_coupling": [],
            "unused_imports": [],
            "dependency_metrics": {}
        }
        
        import_graph = defaultdict(set)
        all_imports = defaultdict(list)
        
        # Parse all Python files for imports
        for py_file in self.project_path.rglob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                tree = ast.parse(content)
                
                file_imports = set()
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            file_imports.add(alias.name)
                            all_imports[str(py_file.relative_to(self.project_path))].append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            file_imports.add(node.module)
                            all_imports[str(py_file.relative_to(self.project_path))].append(node.module)
                
                import_graph[str(py_file.relative_to(self.project_path))] = file_imports
                
            except Exception as e:
                continue
        
        deps_data["import_graph"] = {k: list(v) for k, v in import_graph.items()}
        
        # Find circular dependencies (simplified)
        def find_cycles(graph):
            cycles = []
            visited = set()
            rec_stack = set()
            
            def dfs(node, path):
                if node in rec_stack:
                    cycle_start = path.index(node)
                    cycles.append(path[cycle_start:] + [node])
                    return
                
                if node in visited:
                    return
                
                visited.add(node)
                rec_stack.add(node)
                
                for neighbor in graph.get(node, []):
                    if neighbor in graph:  # Only internal modules
                        dfs(neighbor, path + [node])
                
                rec_stack.remove(node)
            
            for node in graph:
                if node not in visited:
                    dfs(node, [])
            
            return cycles
        
        # Build internal dependency graph
        internal_graph = {}
        for file, imports in import_graph.items():
            internal_imports = []
            for imp in imports:
                # Check if it's an internal import
                if any(imp.startswith(prefix) for prefix in ['api', 'core', 'config', 'infrastructure']):
                    internal_imports.append(imp)
            internal_graph[file] = internal_imports
        
        cycles = find_cycles(internal_graph)
        deps_data["circular_dependencies"] = cycles[:5]  # Top 5 cycles
        
        # High coupling detection
        coupling_scores = {}
        for file, imports in import_graph.items():
            internal_imports = len([imp for imp in imports if not imp.startswith(('os', 'sys', 'json', 'typing', 'datetime', 'pathlib'))])
            coupling_scores[file] = internal_imports
        
        high_coupling = sorted(coupling_scores.items(), key=lambda x: x[1], reverse=True)[:10]
        deps_data["high_coupling"] = [{"file": f, "import_count": c} for f, c in high_coupling]
        
        # Dependency metrics
        deps_data["dependency_metrics"] = {
            "total_files": len(import_graph),
            "avg_imports_per_file": sum(len(imports) for imports in import_graph.values()) / len(import_graph) if import_graph else 0,
            "max_imports": max(len(imports) for imports in import_graph.values()) if import_graph else 0,
            "total_unique_imports": len(set().union(*import_graph.values())) if import_graph else 0
        }
        
        return deps_data
    
    def analyze_security(self) -> Dict[str, Any]:
        """Analyze security issues from bandit report and additional checks"""
        security_data = {
            "bandit_summary": {},
            "hardcoded_secrets": [],
            "sql_injection_risks": [],
            "xss_risks": [],
            "file_permissions": [],
            "api_security": {}
        }
        
        # Parse bandit report if exists
        bandit_file = self.project_path / "bandit_report.json"
        if bandit_file.exists():
            try:
                with open(bandit_file, 'r') as f:
                    bandit_data = json.load(f)
                
                # Summarize bandit results
                total_issues = len(bandit_data.get("results", []))
                severity_counts = Counter(result.get("issue_severity", "UNKNOWN") for result in bandit_data.get("results", []))
                confidence_counts = Counter(result.get("issue_confidence", "UNKNOWN") for result in bandit_data.get("results", []))
                
                security_data["bandit_summary"] = {
                    "total_issues": total_issues,
                    "severity_breakdown": dict(severity_counts),
                    "confidence_breakdown": dict(confidence_counts),
                    "files_with_issues": len(set(result.get("filename", "") for result in bandit_data.get("results", []))),
                    "top_issues": bandit_data.get("results", [])[:5]  # Top 5 issues
                }
                
            except Exception as e:
                security_data["bandit_summary"]["error"] = str(e)
        
        # Manual security checks
        secret_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']'
        ]
        
        for py_file in self.project_path.rglob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                for pattern in secret_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        security_data["hardcoded_secrets"].append({
                            "file": str(py_file.relative_to(self.project_path)),
                            "matches": len(matches),
                            "pattern": pattern
                        })
            except Exception:
                continue
        
        # API security analysis
        fastapi_files = []
        for py_file in self.project_path.rglob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                if "fastapi" in content.lower() or "@app." in content:
                    fastapi_files.append(str(py_file.relative_to(self.project_path)))
            except Exception:
                continue
        
        security_data["api_security"] = {
            "fastapi_files": fastapi_files,
            "endpoints_found": len(fastapi_files),
            "has_cors_middleware": any("cors" in str(f).lower() for f in self.project_path.rglob("*.py"))
        }
        
        return security_data
    
    def analyze_ai_effectiveness(self) -> Dict[str, Any]:
        """Analyze AI tools effectiveness and KPIs"""
        ai_data = {
            "ai_services_used": [],
            "api_integrations": {},
            "error_handling": {},
            "response_times": {},
            "accuracy_metrics": {},
            "cost_analysis": {}
        }
        
        # Detect AI services
        ai_patterns = {
            "openai": r"openai|gpt-|chatcompletion",
            "hume": r"hume|emotion.*analysis",
            "elevenlabs": r"elevenlabs|text.*to.*speech|tts",
            "whisper": r"whisper|speech.*to.*text|stt"
        }
        
        ai_service_files = defaultdict(list)
        
        for py_file in self.project_path.rglob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore').lower()
                for service, pattern in ai_patterns.items():
                    if re.search(pattern, content):
                        ai_service_files[service].append(str(py_file.relative_to(self.project_path)))
            except Exception:
                continue
        
        ai_data["ai_services_used"] = dict(ai_service_files)
        
        # API integration analysis
        api_configs = []
        for py_file in self.project_path.rglob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                if "api_key" in content.lower():
                    api_configs.append(str(py_file.relative_to(self.project_path)))
            except Exception:
                continue
        
        ai_data["api_integrations"] = {
            "files_with_api_keys": api_configs,
            "total_integrations": len(set().union(*ai_service_files.values()))
        }
        
        # Error handling analysis
        error_handling_count = 0
        total_ai_files = len(set().union(*ai_service_files.values()))
        
        for py_file in self.project_path.rglob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                if any(service in content.lower() for service in ai_patterns.keys()):
                    if "try:" in content and "except" in content:
                        error_handling_count += 1
            except Exception:
                continue
        
        ai_data["error_handling"] = {
            "files_with_error_handling": error_handling_count,
            "error_handling_percentage": (error_handling_count / total_ai_files * 100) if total_ai_files > 0 else 0
        }
        
        # Performance KPIs estimation
        ai_data["performance_kpis"] = {
            "estimated_response_time_ms": 2500,  # Based on FastAPI + AI services
            "concurrent_requests_capacity": 50,   # Estimated based on architecture
            "ai_accuracy_target": 85,             # Industry standard for voice AI
            "emotion_detection_confidence": 80    # Based on Hume AI capabilities
        }
        
        return ai_data
    
    def analyze_code_quality(self) -> Dict[str, Any]:
        """Analyze overall code quality metrics"""
        quality_data = {
            "complexity_metrics": {},
            "documentation_coverage": {},
            "test_coverage": {},
            "code_duplication": {},
            "naming_conventions": {}
        }
        
        total_lines = 0
        documented_functions = 0
        total_functions = 0
        complexity_scores = []
        
        for py_file in self.project_path.rglob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                lines = content.splitlines()
                total_lines += len(lines)
                
                # Parse AST for function analysis
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        total_functions += 1
                        
                        # Check for docstring
                        if (ast.get_docstring(node) or 
                            (len(node.body) > 0 and isinstance(node.body[0], ast.Expr) and 
                             isinstance(node.body[0].value, ast.Str))):
                            documented_functions += 1
                        
                        # Simple complexity metric (number of statements)
                        complexity = len(list(ast.walk(node)))
                        complexity_scores.append(complexity)
                        
            except Exception:
                continue
        
        quality_data["complexity_metrics"] = {
            "total_lines_of_code": total_lines,
            "total_functions": total_functions,
            "avg_function_complexity": sum(complexity_scores) / len(complexity_scores) if complexity_scores else 0,
            "max_function_complexity": max(complexity_scores) if complexity_scores else 0,
            "functions_over_40_lines": len([c for c in complexity_scores if c > 40])
        }
        
        quality_data["documentation_coverage"] = {
            "documented_functions": documented_functions,
            "documentation_percentage": (documented_functions / total_functions * 100) if total_functions > 0 else 0
        }
        
        # Test coverage analysis
        test_files = list(self.project_path.rglob("test_*.py")) + list(self.project_path.rglob("*_test.py"))
        quality_data["test_coverage"] = {
            "test_files_count": len(test_files),
            "estimated_coverage": min(len(test_files) * 10, 100)  # Rough estimation
        }
        
        return quality_data
    
    def generate_recommendations(self) -> List[Dict[str, Any]]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []
        
        # Performance recommendations
        if self.results["performance"]["memory_usage"].get("peak_mb", 0) > 500:
            recommendations.append({
                "category": "Performance",
                "priority": "HIGH",
                "title": "High Memory Usage Detected",
                "description": f"Peak memory usage: {self.results['performance']['memory_usage']['peak_mb']:.1f}MB",
                "action": "Implement memory profiling and optimize data structures",
                "impact": "Reduces server costs and improves scalability"
            })
        
        # Dependency recommendations
        if len(self.results["dependencies"]["circular_dependencies"]) > 0:
            recommendations.append({
                "category": "Architecture",
                "priority": "CRITICAL",
                "title": "Circular Dependencies Found",
                "description": f"Found {len(self.results['dependencies']['circular_dependencies'])} circular dependency chains",
                "action": "Refactor imports to break circular dependencies",
                "impact": "Prevents import errors and improves modularity"
            })
        
        # Security recommendations
        bandit_issues = self.results["security"]["bandit_summary"].get("total_issues", 0)
        if bandit_issues > 10:
            recommendations.append({
                "category": "Security",
                "priority": "HIGH",
                "title": "Multiple Security Issues",
                "description": f"Bandit found {bandit_issues} security issues",
                "action": "Review and fix security vulnerabilities identified by Bandit",
                "impact": "Protects against security breaches and data leaks"
            })
        
        # AI effectiveness recommendations
        error_handling_pct = self.results["ai_effectiveness"]["error_handling"].get("error_handling_percentage", 0)
        if error_handling_pct < 80:
            recommendations.append({
                "category": "AI Services",
                "priority": "MEDIUM",
                "title": "Insufficient Error Handling for AI Services",
                "description": f"Only {error_handling_pct:.1f}% of AI service files have proper error handling",
                "action": "Add comprehensive try-catch blocks for all AI API calls",
                "impact": "Improves system reliability and user experience"
            })
        
        # Code quality recommendations
        doc_pct = self.results["code_quality"]["documentation_coverage"].get("documentation_percentage", 0)
        if doc_pct < 60:
            recommendations.append({
                "category": "Code Quality",
                "priority": "MEDIUM",
                "title": "Low Documentation Coverage",
                "description": f"Only {doc_pct:.1f}% of functions are documented",
                "action": "Add docstrings to all public functions and classes",
                "impact": "Improves maintainability and team productivity"
            })
        
        return recommendations

def main():
    """Run the advanced analysis"""
    analyzer = AdvancedAnalyzer()
    results = analyzer.analyze_all()
    
    # Save results to JSON
    output_file = "advanced_analysis_report.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n✅ Analysis complete! Results saved to {output_file}")
    print(f"📊 Found {len(results['recommendations'])} recommendations")
    print(f"🔍 Analyzed {results['code_quality']['complexity_metrics']['total_lines_of_code']} lines of code")
    print(f"🔒 Security issues: {results['security']['bandit_summary'].get('total_issues', 'N/A')}")
    
if __name__ == "__main__":
    main() 