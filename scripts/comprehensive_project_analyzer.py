#!/usr/bin/env python3
"""
🔍 Comprehensive Project File Analyzer
Analyzes every Python file in the project and generates detailed reports
"""

import os
import hashlib
import ast
import re
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Set, Any, Optional
import inspect

class ProjectFileAnalyzer:
    """Comprehensive analyzer for project files"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.analysis_results = {}
        self.file_hashes = {}
        self.duplicate_files = defaultdict(list)
        
        # File type patterns
        self.file_patterns = {
            'test': ['test_', '_test', 'tests/', 'testing/'],
            'config': ['config', 'settings', 'constants'],
            'service': ['service', 'services/'],
            'repository': ['repository', 'repositories/', 'repo'],
            'model': ['model', 'models/', 'entity', 'entities/'],
            'controller': ['controller', 'controllers/', 'handler', 'handlers/'],
            'utility': ['util', 'utils/', 'helper', 'helpers/'],
            'domain': ['domain/'],
            'application': ['application/'],
            'infrastructure': ['infrastructure/'],
            'presentation': ['presentation/', 'api/', 'web/'],
            'dto': ['dto/', 'schemas/'],
            'exception': ['exception', 'error'],
            'middleware': ['middleware/'],
            'decorator': ['decorator'],
            'factory': ['factory'],
            'builder': ['builder'],
            'observer': ['observer'],
            'strategy': ['strategy'],
            'command': ['command'],
            'query': ['query']
        }

    def analyze_ast(self, file_path: str, content: str) -> Dict[str, Any]:
        """Analyze Python file using AST"""
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            return {
                'error': f'Syntax error: {e}',
                'classes': [],
                'functions': [],
                'imports': [],
                'async_functions': [],
                'decorators': []
            }
        
        classes = []
        functions = []
        imports = []
        async_functions = []
        decorators = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                base_classes = [base.id if isinstance(base, ast.Name) else str(base) for base in node.bases]
                class_decorators = [dec.id if isinstance(dec, ast.Name) else str(dec) for dec in node.decorator_list]
                classes.append({
                    'name': node.name,
                    'line': node.lineno,
                    'bases': base_classes,
                    'decorators': class_decorators,
                    'methods': len([n for n in node.body if isinstance(n, ast.FunctionDef)])
                })
            
            elif isinstance(node, ast.FunctionDef):
                func_decorators = [dec.id if isinstance(dec, ast.Name) else str(dec) for dec in node.decorator_list]
                functions.append({
                    'name': node.name,
                    'line': node.lineno,
                    'decorators': func_decorators,
                    'args': len(node.args.args),
                    'is_async': False
                })
            
            elif isinstance(node, ast.AsyncFunctionDef):
                func_decorators = [dec.id if isinstance(dec, ast.Name) else str(dec) for dec in node.decorator_list]
                async_functions.append({
                    'name': node.name,
                    'line': node.lineno,
                    'decorators': func_decorators,
                    'args': len(node.args.args)
                })
            
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append({
                        'module': alias.name,
                        'alias': alias.asname,
                        'type': 'import'
                    })
            
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    imports.append({
                        'module': f"{module}.{alias.name}" if module else alias.name,
                        'alias': alias.asname,
                        'type': 'from_import',
                        'from_module': module
                    })
        
        return {
            'classes': classes,
            'functions': functions,
            'imports': imports,
            'async_functions': async_functions,
            'total_classes': len(classes),
            'total_functions': len(functions) + len(async_functions),
            'total_imports': len(imports)
        }

    def analyze_content_patterns(self, content: str) -> Dict[str, Any]:
        """Analyze content for specific patterns"""
        patterns = {
            'todo_fixme': len(re.findall(r'(TODO|FIXME|XXX|HACK)', content, re.IGNORECASE)),
            'print_statements': len(re.findall(r'\bprint\s*\(', content)),
            'console_log': len(re.findall(r'console\.log', content)),
            'hardcoded_urls': len(re.findall(r'https?://[^\s"\']+', content)),
            'hardcoded_passwords': len(re.findall(r'(password|pwd|pass)\s*=\s*["\'][^"\']+["\']', content, re.IGNORECASE)),
            'sql_queries': len(re.findall(r'(SELECT|INSERT|UPDATE|DELETE|CREATE|DROP)\s+', content, re.IGNORECASE)),
            'api_keys': len(re.findall(r'(api_key|apikey|secret_key|token)\s*=\s*["\'][^"\']+["\']', content, re.IGNORECASE)),
            'has_main': '__name__ == "__main__"' in content,
            'has_async': 'async def' in content or 'await ' in content,
            'has_decorators': '@' in content,
            'has_type_hints': '->' in content or ': ' in content,
            'has_docstrings': '"""' in content or "'''" in content
        }
        return patterns

    def determine_file_type(self, file_path: str, content: str, ast_info: Dict) -> str:
        """Determine the type of the file based on path and content"""
        file_path_lower = file_path.lower()
        
        # Check patterns in order of specificity
        for file_type, patterns in self.file_patterns.items():
            for pattern in patterns:
                if pattern in file_path_lower:
                    return file_type
        
        # Check content-based classification
        if ast_info.get('total_classes', 0) > 0:
            # Check if it's a model/entity
            class_names = [cls['name'].lower() for cls in ast_info.get('classes', [])]
            if any('entity' in name or 'model' in name for name in class_names):
                return 'model'
            
            # Check for service pattern
            if any('service' in name for name in class_names):
                return 'service'
            
            # Check for repository pattern
            if any('repository' in name or 'repo' in name for name in class_names):
                return 'repository'
        
        # Default classification
        if file_path_lower.endswith('__init__.py'):
            return 'module_init'
        
        return 'utility'

    def determine_importance(self, file_path: str, ast_info: Dict, patterns: Dict) -> str:
        """Determine the importance level of the file"""
        file_path_lower = file_path.lower()
        
        # Critical files
        critical_indicators = [
            'main.py', 'app.py', '__init__.py' in file_path and 'src/' in file_path,
            ast_info.get('total_classes', 0) > 3,
            ast_info.get('total_imports', 0) > 10,
            'domain/' in file_path_lower and 'entities/' in file_path_lower,
            'security' in file_path_lower,
            'auth' in file_path_lower
        ]
        
        if any(critical_indicators):
            return 'critical'
        
        # High importance
        high_indicators = [
            'service' in file_path_lower,
            'repository' in file_path_lower,
            'controller' in file_path_lower,
            ast_info.get('total_classes', 0) > 1,
            patterns.get('has_async', False),
            'infrastructure/' in file_path_lower
        ]
        
        if any(high_indicators):
            return 'high'
        
        # Low importance (likely to be trash or deprecated)
        low_indicators = [
            'test' in file_path_lower and patterns.get('todo_fixme', 0) > 3,
            patterns.get('print_statements', 0) > 5,
            'old' in file_path_lower,
            'deprecated' in file_path_lower,
            'backup' in file_path_lower,
            'temp' in file_path_lower
        ]
        
        if any(low_indicators):
            return 'low'
        
        return 'medium'

    def suggest_new_location(self, file_path: str, file_type: str, ast_info: Dict) -> tuple:
        """Suggest a new location based on DDD architecture"""
        current_path = Path(file_path)
        
        # DDD-based suggestions
        if file_type == 'model' or file_type == 'entity':
            if 'entities' not in file_path:
                return 'src/domain/entities/', 'Domain entities should be in domain layer'
        
        elif file_type == 'service':
            # Check if it's domain service or application service
            if any('domain' in cls['name'].lower() for cls in ast_info.get('classes', [])):
                return 'src/domain/services/', 'Domain services belong in domain layer'
            else:
                return 'src/application/services/', 'Application services belong in application layer'
        
        elif file_type == 'repository':
            if 'infrastructure' not in file_path:
                return 'src/infrastructure/persistence/', 'Repositories are infrastructure concerns'
        
        elif file_type == 'controller':
            if 'presentation' not in file_path:
                return 'src/presentation/api/', 'Controllers are presentation layer concerns'
        
        elif file_type == 'dto':
            if 'application' not in file_path:
                return 'src/application/dto/', 'DTOs belong in application layer'
        
        elif file_type == 'exception':
            if 'domain' not in file_path:
                return 'src/domain/exceptions/', 'Domain exceptions belong in domain layer'
        
        return str(current_path.parent) + '/', 'Current location is appropriate'

    def find_similar_files(self, file_path: str, content_hash: str) -> List[str]:
        """Find files with similar names or content"""
        similar = []
        file_name = Path(file_path).stem
        
        for other_path, other_hash in self.file_hashes.items():
            if other_path == file_path:
                continue
            
            other_name = Path(other_path).stem
            
            # Check for similar names
            if (file_name in other_name or other_name in file_name) and file_name != other_name:
                similar.append(other_path)
            
            # Check for identical content
            if content_hash == other_hash:
                similar.append(f"{other_path} (identical content)")
        
        return similar

    def identify_issues(self, file_path: str, ast_info: Dict, patterns: Dict, file_type: str) -> List[str]:
        """Identify potential issues with the file"""
        issues = []
        
        # Security issues
        if patterns.get('hardcoded_passwords', 0) > 0:
            issues.append("Contains hardcoded passwords - SECURITY RISK")
        
        if patterns.get('api_keys', 0) > 0:
            issues.append("Contains hardcoded API keys - SECURITY RISK")
        
        # Code quality issues
        if patterns.get('todo_fixme', 0) > 5:
            issues.append("Too many TODO/FIXME comments")
        
        if patterns.get('print_statements', 0) > 3:
            issues.append("Contains debug print statements")
        
        if ast_info.get('total_functions', 0) > 15:
            issues.append("File too large - consider splitting")
        
        if not patterns.get('has_docstrings', False) and ast_info.get('total_classes', 0) > 0:
            issues.append("Missing docstrings")
        
        if not patterns.get('has_type_hints', False) and ast_info.get('total_functions', 0) > 0:
            issues.append("Missing type hints")
        
        # Architecture issues
        if file_type == 'service' and 'domain' in file_path and patterns.get('sql_queries', 0) > 0:
            issues.append("Domain service contains SQL queries - violates clean architecture")
        
        # Test-related issues
        if file_type != 'test' and 'test' not in file_path.lower():
            test_file_expected = file_path.replace('src/', 'tests/').replace('.py', '_test.py')
            if not os.path.exists(test_file_expected):
                issues.append("No corresponding test file found")
        
        return issues

    def calculate_content_hash(self, content: str) -> str:
        """Calculate hash of file content for duplicate detection"""
        # Normalize content by removing comments and whitespace
        lines = [line.strip() for line in content.split('\n') if line.strip() and not line.strip().startswith('#')]
        normalized = '\n'.join(lines)
        return hashlib.md5(normalized.encode()).hexdigest()[:8]

    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze a single Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            return {'error': f'Could not read file: {e}'}
        
        # Get file stats
        file_stat = os.stat(file_path)
        
        # Calculate content hash
        content_hash = self.calculate_content_hash(content)
        self.file_hashes[file_path] = content_hash
        
        # AST analysis
        ast_info = self.analyze_ast(file_path, content)
        
        # Pattern analysis
        patterns = self.analyze_content_patterns(content)
        
        # Determine file characteristics
        file_type = self.determine_file_type(file_path, content, ast_info)
        importance = self.determine_importance(file_path, ast_info, patterns)
        
        # Suggest new location
        suggested_location, move_reason = self.suggest_new_location(file_path, file_type, ast_info)
        
        # Find similar files
        similar_files = self.find_similar_files(file_path, content_hash)
        
        # Identify issues
        issues = self.identify_issues(file_path, ast_info, patterns, file_type)
        
        # Extract dependencies
        dependencies = list(set([imp['module'].split('.')[0] for imp in ast_info.get('imports', [])]))
        
        return {
            'file_path': file_path,
            'analysis': {
                'type': file_type,
                'importance': importance,
                'current_location': str(Path(file_path).parent) + '/',
                'suggested_location': suggested_location,
                'reason_for_move': move_reason,
                'file_stats': {
                    'lines': len(content.split('\n')),
                    'size_bytes': len(content.encode()),
                    'classes': ast_info.get('total_classes', 0),
                    'functions': ast_info.get('total_functions', 0),
                    'imports': ast_info.get('total_imports', 0),
                    'has_tests': 'test' in file_path.lower() or any('test' in similar for similar in similar_files),
                    'last_modified': datetime.fromtimestamp(file_stat.st_mtime, tz=timezone.utc).isoformat()
                },
                'dependencies': dependencies,
                'similar_files': similar_files,
                'issues': issues,
                'content_hash': content_hash,
                'main_purpose': self.extract_main_purpose(content, ast_info),
                'patterns': patterns,
                'ast_details': {
                    'classes': ast_info.get('classes', []),
                    'functions': ast_info.get('functions', []),
                    'async_functions': ast_info.get('async_functions', [])
                }
            }
        }

    def extract_main_purpose(self, content: str, ast_info: Dict) -> str:
        """Extract the main purpose of the file"""
        # Try to get from docstring
        lines = content.strip().split('\n')
        
        # Check for module docstring
        if len(lines) > 0 and ('"""' in lines[0] or "'''" in lines[0]):
            for i, line in enumerate(lines[1:], 1):
                if '"""' in line or "'''" in line:
                    docstring = ' '.join(lines[:i+1])
                    # Clean and extract first meaningful sentence
                    clean_doc = re.sub(r'["""\']+', '', docstring).strip()
                    if clean_doc:
                        return clean_doc.split('.')[0][:100] + ('...' if len(clean_doc) > 100 else '')
        
        # Infer from classes and functions
        classes = ast_info.get('classes', [])
        functions = ast_info.get('functions', [])
        
        if classes:
            class_names = [cls['name'] for cls in classes]
            return f"Defines classes: {', '.join(class_names[:3])}" + ('...' if len(class_names) > 3 else '')
        
        if functions:
            func_names = [func['name'] for func in functions if not func['name'].startswith('_')][:3]
            if func_names:
                return f"Provides functions: {', '.join(func_names)}" + ('...' if len(functions) > 3 else '')
        
        return "Utility module"

    def analyze_project(self) -> Dict[str, Any]:
        """Analyze all Python files in the project"""
        python_files = []
        
        # Find all Python files
        for root, dirs, files in os.walk(self.project_root):
            # Skip common ignore directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', 'venv', 'env']]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    # Make path relative to project root
                    rel_path = os.path.relpath(file_path, self.project_root)
                    python_files.append(rel_path)
        
        print(f"🔍 Found {len(python_files)} Python files to analyze...")
        
        # Analyze each file
        results = {}
        for i, file_path in enumerate(python_files, 1):
            print(f"📄 Analyzing {i}/{len(python_files)}: {file_path}")
            try:
                results[file_path] = self.analyze_file(file_path)
            except Exception as e:
                print(f"❌ Error analyzing {file_path}: {e}")
                results[file_path] = {'error': str(e)}
        
        # Generate summary statistics
        summary = self.generate_summary(results)
        
        return {
            'summary': summary,
            'files': results,
            'analysis_timestamp': datetime.now(timezone.utc).isoformat(),
            'total_files_analyzed': len(results)
        }

    def generate_summary(self, results: Dict) -> Dict[str, Any]:
        """Generate summary statistics"""
        valid_results = [r for r in results.values() if 'error' not in r]
        
        # Count by type and importance
        type_counts = defaultdict(int)
        importance_counts = defaultdict(int)
        issue_counts = defaultdict(int)
        
        total_lines = 0
        total_classes = 0
        total_functions = 0
        files_with_issues = 0
        
        for result in valid_results:
            analysis = result.get('analysis', {})
            
            type_counts[analysis.get('type', 'unknown')] += 1
            importance_counts[analysis.get('importance', 'unknown')] += 1
            
            stats = analysis.get('file_stats', {})
            total_lines += stats.get('lines', 0)
            total_classes += stats.get('classes', 0)
            total_functions += stats.get('functions', 0)
            
            issues = analysis.get('issues', [])
            if issues:
                files_with_issues += 1
            
            for issue in issues:
                issue_counts[issue] += 1
        
        return {
            'total_valid_files': len(valid_results),
            'total_lines_of_code': total_lines,
            'total_classes': total_classes,
            'total_functions': total_functions,
            'files_with_issues': files_with_issues,
            'file_types': dict(type_counts),
            'importance_levels': dict(importance_counts),
            'common_issues': dict(sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:10])
        }

def main():
    """Main execution function"""
    analyzer = ProjectFileAnalyzer()
    
    print("🚀 Starting comprehensive project analysis...")
    results = analyzer.analyze_project()
    
    # Save full results
    output_file = 'project_analysis_complete.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Analysis complete! Results saved to {output_file}")
    
    # Print summary
    summary = results['summary']
    print(f"\n📊 SUMMARY:")
    print(f"   📄 Total files analyzed: {summary['total_valid_files']}")
    print(f"   📝 Total lines of code: {summary['total_lines_of_code']:,}")
    print(f"   🏗️  Total classes: {summary['total_classes']}")
    print(f"   ⚙️  Total functions: {summary['total_functions']}")
    print(f"   ⚠️  Files with issues: {summary['files_with_issues']}")
    
    print(f"\n📋 File Types:")
    for file_type, count in summary['file_types'].items():
        print(f"   {file_type}: {count}")
    
    print(f"\n🎯 Importance Levels:")
    for level, count in summary['importance_levels'].items():
        print(f"   {level}: {count}")
    
    print(f"\n⚠️  Top Issues:")
    for issue, count in summary['common_issues'].items():
        print(f"   {issue}: {count} files")
    
    # Generate specific reports for critical and high importance files
    critical_files = []
    high_files = []
    
    for file_path, result in results['files'].items():
        if 'error' in result:
            continue
        
        importance = result['analysis']['importance']
        if importance == 'critical':
            critical_files.append((file_path, result))
        elif importance == 'high':
            high_files.append((file_path, result))
    
    # Save critical files report
    if critical_files:
        critical_report = {
            'critical_files': {path: result for path, result in critical_files},
            'count': len(critical_files)
        }
        
        with open('critical_files_report.json', 'w', encoding='utf-8') as f:
            json.dump(critical_report, f, indent=2, ensure_ascii=False)
        
        print(f"\n🔴 Critical files report saved to critical_files_report.json ({len(critical_files)} files)")
    
    # Save high importance files report
    if high_files:
        high_report = {
            'high_importance_files': {path: result for path, result in high_files},
            'count': len(high_files)
        }
        
        with open('high_importance_files_report.json', 'w', encoding='utf-8') as f:
            json.dump(high_report, f, indent=2, ensure_ascii=False)
        
        print(f"🟡 High importance files report saved to high_importance_files_report.json ({len(high_files)} files)")

if __name__ == "__main__":
    main() 