#!/usr/bin/env python3
"""
🔬 AI Teddy Bear - Advanced Analysis Script
"""

import ast
import json
import os
import sys
import time
import psutil
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict, Counter
import re

class AdvancedAnalyzer:
    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        self.results = {
            "performance": {},
            "dependencies": {},
            "security": {},
            "ai_effectiveness": {}
        }
        
    def analyze_performance(self) -> Dict[str, Any]:
        """Analyze performance metrics"""
        perf_data = {
            "memory_usage": {},
            "large_files": [],
            "cpu_info": {}
        }
        
        # CPU and memory info
        perf_data["cpu_info"] = {
            "cpu_count": psutil.cpu_count(),
            "memory_total_gb": psutil.virtual_memory().total / (1024**3),
            "memory_available_gb": psutil.virtual_memory().available / (1024**3)
        }
        
        # Large files analysis
        large_files = []
        for py_file in self.project_path.rglob("*.py"):
            try:
                size = py_file.stat().st_size
                if size > 10000:  # Files > 10KB
                    lines = len(py_file.read_text(encoding='utf-8', errors='ignore').splitlines())
                    large_files.append({
                        "file": str(py_file.relative_to(self.project_path)),
                        "size_kb": size / 1024,
                        "lines": lines
                    })
            except Exception:
                continue
                
        perf_data["large_files"] = sorted(large_files, key=lambda x: x["size_kb"], reverse=True)[:10]
        return perf_data
    
    def analyze_dependencies(self) -> Dict[str, Any]:
        """Analyze dependencies"""
        deps_data = {
            "import_graph": {},
            "high_coupling": [],
            "dependency_metrics": {}
        }
        
        import_graph = defaultdict(set)
        
        for py_file in self.project_path.rglob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                tree = ast.parse(content)
                
                file_imports = set()
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            file_imports.add(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            file_imports.add(node.module)
                
                import_graph[str(py_file.relative_to(self.project_path))] = file_imports
                
            except Exception:
                continue
        
        deps_data["import_graph"] = {k: list(v) for k, v in import_graph.items()}
        
        # High coupling detection
        coupling_scores = {}
        for file, imports in import_graph.items():
            internal_imports = len([imp for imp in imports if not imp.startswith(('os', 'sys', 'json', 'typing', 'datetime'))])
            coupling_scores[file] = internal_imports
        
        high_coupling = sorted(coupling_scores.items(), key=lambda x: x[1], reverse=True)[:10]
        deps_data["high_coupling"] = [{"file": f, "import_count": c} for f, c in high_coupling]
        
        return deps_data
    
    def analyze_security(self) -> Dict[str, Any]:
        """Analyze security from bandit report"""
        security_data = {"bandit_summary": {}}
        
        bandit_file = self.project_path / "bandit_report.json"
        if bandit_file.exists():
            try:
                with open(bandit_file, 'r') as f:
                    bandit_data = json.load(f)
                
                total_issues = len(bandit_data.get("results", []))
                severity_counts = Counter(result.get("issue_severity", "UNKNOWN") for result in bandit_data.get("results", []))
                
                security_data["bandit_summary"] = {
                    "total_issues": total_issues,
                    "severity_breakdown": dict(severity_counts),
                    "top_issues": bandit_data.get("results", [])[:5]
                }
                
            except Exception as e:
                security_data["bandit_summary"]["error"] = str(e)
        
        return security_data
    
    def analyze_ai_effectiveness(self) -> Dict[str, Any]:
        """Analyze AI services effectiveness"""
        ai_data = {
            "ai_services_used": [],
            "performance_kpis": {}
        }
        
        ai_patterns = {
            "openai": r"openai|gpt-|chatcompletion",
            "hume": r"hume|emotion.*analysis", 
            "elevenlabs": r"elevenlabs|text.*to.*speech"
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
        
        # Performance KPIs
        ai_data["performance_kpis"] = {
            "estimated_response_time_ms": 2500,
            "concurrent_requests_capacity": 50,
            "ai_accuracy_target": 85
        }
        
        return ai_data
    
    def analyze_all(self) -> Dict[str, Any]:
        """Run all analyses"""
        print("🔬 Starting Analysis...")
        
        self.results["performance"] = self.analyze_performance()
        self.results["dependencies"] = self.analyze_dependencies()
        self.results["security"] = self.analyze_security()
        self.results["ai_effectiveness"] = self.analyze_ai_effectiveness()
        
        return self.results

def main():
    analyzer = AdvancedAnalyzer()
    results = analyzer.analyze_all()
    
    with open("analysis_report.json", 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print("✅ Analysis complete!")

if __name__ == "__main__":
    main() 