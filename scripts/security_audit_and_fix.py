#!/usr/bin/env python3
"""
Security Audit and Auto-Fix Script
Scans the codebase for security issues and applies fixes
"""

import os
import re
import ast
import json
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
import logging
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SecurityIssueType(Enum):
    """Types of security issues"""
    HARDCODED_SECRET = "hardcoded_secret"
    EVAL_EXEC_USAGE = "eval_exec_usage"
    WEAK_EXCEPTION_HANDLING = "weak_exception_handling"
    MISSING_INPUT_VALIDATION = "missing_input_validation"
    INSECURE_CONFIG = "insecure_config"
    MISSING_ENCRYPTION = "missing_encryption"
    SQL_INJECTION_RISK = "sql_injection_risk"
    PATH_TRAVERSAL_RISK = "path_traversal_risk"


@dataclass
class SecurityIssue:
    """Represents a security issue found in the code"""
    issue_type: SecurityIssueType
    file_path: Path
    line_number: int
    severity: str  # "critical", "high", "medium", "low"
    description: str
    code_snippet: str
    suggested_fix: str
    can_auto_fix: bool = False
    

class SecurityAuditor:
    """Main security auditor class"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.issues: List[SecurityIssue] = []
        self.fixed_count = 0
        self.patterns = self._load_security_patterns()
        
    def _load_security_patterns(self) -> Dict[str, Any]:
        """Load security patterns to check"""
        return {
            # API Keys and Secrets
            "api_keys": [
                r'api[_-]?key\s*[:=]\s*["\']([^"\']+)["\']',
                r'secret[_-]?key\s*[:=]\s*["\']([^"\']+)["\']',
                r'password\s*[:=]\s*["\']([^"\']+)["\']',
                r'token\s*[:=]\s*["\']([^"\']+)["\']',
            ],
            
            # Specific API key patterns
            "specific_keys": {
                "openai": r'sk-[a-zA-Z0-9]{48}',
                "aws": r'AKIA[0-9A-Z]{16}',
                "google": r'AIza[0-9A-Za-z\-_]{35}',
                "github": r'ghp_[a-zA-Z0-9]{36}',
                "slack": r'xoxb-[0-9]{12}-[0-9]{12}-[a-zA-Z0-9]{24}',
            },
            
            # Dangerous functions
            "dangerous_functions": [
                r'\beval\s*\(',
                r'\bexec\s*\(',
                r'\b__import__\s*\(',
                r'compile\s*\(',
            ],
            
            # SQL Injection risks
            "sql_injection": [
                r'\.execute\s*\(\s*["\'].*%s.*["\'].*%',
                r'\.execute\s*\(\s*f["\']',
                r'\.execute\s*\(\s*[^"\']*\+',
            ],
            
            # Path traversal
            "path_traversal": [
                r'open\s*\([^)]*\.\.[/\\]',
                r'Path\s*\([^)]*\.\.[/\\]',
            ],
            
            # Weak exception handling
            "weak_exceptions": [
                r'except\s*:',
                r'except\s+Exception\s*:',
                r'except.*pass',
            ],
        }
    
    async def audit_project(self) -> List[SecurityIssue]:
        """Audit the entire project for security issues"""
        logger.info(f"Starting security audit of {self.project_root}")
        
        # Get all Python files
        python_files = list(self.project_root.rglob("*.py"))
        
        # Exclude virtual environments and hidden directories
        python_files = [
            f for f in python_files 
            if not any(part.startswith('.') or part in ['venv', 'env', '__pycache__'] 
                      for part in f.parts)
        ]
        
        logger.info(f"Found {len(python_files)} Python files to audit")
        
        # Audit each file
        for file_path in python_files:
            await self._audit_file(file_path)
        
        # Sort issues by severity
        self.issues.sort(key=lambda x: self._severity_score(x.severity), reverse=True)
        
        logger.info(f"Audit complete. Found {len(self.issues)} security issues")
        return self.issues
    
    async def _audit_file(self, file_path: Path):
        """Audit a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.splitlines()
            
            # Check for hardcoded secrets
            await self._check_hardcoded_secrets(file_path, content, lines)
            
            # Check for dangerous functions
            await self._check_dangerous_functions(file_path, content, lines)
            
            # Check for SQL injection risks
            await self._check_sql_injection(file_path, content, lines)
            
            # Check for path traversal
            await self._check_path_traversal(file_path, content, lines)
            
            # Check exception handling
            await self._check_exception_handling(file_path, content, lines)
            
            # AST-based checks
            try:
                tree = ast.parse(content)
                await self._ast_based_checks(file_path, tree, lines)
            except SyntaxError:
                logger.warning(f"Could not parse {file_path} with AST")
                
        except Exception as e:
            logger.error(f"Error auditing {file_path}: {e}")
    
    async def _check_hardcoded_secrets(self, file_path: Path, content: str, lines: List[str]):
        """Check for hardcoded secrets"""
        # Skip test files and examples
        if 'test' in str(file_path).lower() or 'example' in str(file_path).lower():
            return
        
        # Check general patterns
        for pattern in self.patterns["api_keys"]:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                line_num = content[:match.start()].count('\n') + 1
                secret_value = match.group(1)
                
                # Check if it's a real secret (not placeholder)
                if len(secret_value) > 10 and not secret_value.startswith('${'):
                    self.issues.append(SecurityIssue(
                        issue_type=SecurityIssueType.HARDCODED_SECRET,
                        file_path=file_path,
                        line_number=line_num,
                        severity="critical",
                        description=f"Hardcoded secret found: {match.group(0)[:50]}...",
                        code_snippet=lines[line_num - 1].strip() if line_num <= len(lines) else "",
                        suggested_fix="Use secrets manager: await secrets_manager.get_secret('key_name')",
                        can_auto_fix=True
                    ))
        
        # Check specific API key patterns
        for key_type, pattern in self.patterns["specific_keys"].items():
            for match in re.finditer(pattern, content):
                line_num = content[:match.start()].count('\n') + 1
                self.issues.append(SecurityIssue(
                    issue_type=SecurityIssueType.HARDCODED_SECRET,
                    file_path=file_path,
                    line_number=line_num,
                    severity="critical",
                    description=f"Hardcoded {key_type} API key found",
                    code_snippet=lines[line_num - 1].strip() if line_num <= len(lines) else "",
                    suggested_fix=f"Use secrets manager: await secrets_manager.get_secret('{key_type}_api_key')",
                    can_auto_fix=True
                ))
    
    async def _check_dangerous_functions(self, file_path: Path, content: str, lines: List[str]):
        """Check for eval/exec usage"""
        for pattern in self.patterns["dangerous_functions"]:
            for match in re.finditer(pattern, content):
                line_num = content[:match.start()].count('\n') + 1
                func_name = match.group(0).replace('(', '').strip()
                
                self.issues.append(SecurityIssue(
                    issue_type=SecurityIssueType.EVAL_EXEC_USAGE,
                    file_path=file_path,
                    line_number=line_num,
                    severity="high",
                    description=f"Dangerous function '{func_name}' usage detected",
                    code_snippet=lines[line_num - 1].strip() if line_num <= len(lines) else "",
                    suggested_fix="Use safe_expression_parser.parse() instead",
                    can_auto_fix=True
                ))
    
    async def _check_sql_injection(self, file_path: Path, content: str, lines: List[str]):
        """Check for SQL injection vulnerabilities"""
        for pattern in self.patterns["sql_injection"]:
            for match in re.finditer(pattern, content):
                line_num = content[:match.start()].count('\n') + 1
                
                self.issues.append(SecurityIssue(
                    issue_type=SecurityIssueType.SQL_INJECTION_RISK,
                    file_path=file_path,
                    line_number=line_num,
                    severity="high",
                    description="Potential SQL injection vulnerability",
                    code_snippet=lines[line_num - 1].strip() if line_num <= len(lines) else "",
                    suggested_fix="Use parameterized queries with placeholders",
                    can_auto_fix=False
                ))
    
    async def _check_path_traversal(self, file_path: Path, content: str, lines: List[str]):
        """Check for path traversal vulnerabilities"""
        for pattern in self.patterns["path_traversal"]:
            for match in re.finditer(pattern, content):
                line_num = content[:match.start()].count('\n') + 1
                
                self.issues.append(SecurityIssue(
                    issue_type=SecurityIssueType.PATH_TRAVERSAL_RISK,
                    file_path=file_path,
                    line_number=line_num,
                    severity="high",
                    description="Potential path traversal vulnerability",
                    code_snippet=lines[line_num - 1].strip() if line_num <= len(lines) else "",
                    suggested_fix="Validate and sanitize file paths, use Path.resolve()",
                    can_auto_fix=False
                ))
    
    async def _check_exception_handling(self, file_path: Path, content: str, lines: List[str]):
        """Check for weak exception handling"""
        for pattern in self.patterns["weak_exceptions"]:
            for match in re.finditer(pattern, content):
                line_num = content[:match.start()].count('\n') + 1
                
                self.issues.append(SecurityIssue(
                    issue_type=SecurityIssueType.WEAK_EXCEPTION_HANDLING,
                    file_path=file_path,
                    line_number=line_num,
                    severity="medium",
                    description="Weak exception handling detected",
                    code_snippet=lines[line_num - 1].strip() if line_num <= len(lines) else "",
                    suggested_fix="Use specific exception types from the exception hierarchy",
                    can_auto_fix=True
                ))
    
    async def _ast_based_checks(self, file_path: Path, tree: ast.AST, lines: List[str]):
        """Perform AST-based security checks"""
        class SecurityVisitor(ast.NodeVisitor):
            def __init__(self, auditor, file_path, lines):
                self.auditor = auditor
                self.file_path = file_path
                self.lines = lines
                self.issues = []
            
            def visit_Call(self, node):
                # Check for eval/exec
                if isinstance(node.func, ast.Name):
                    if node.func.id in ['eval', 'exec', '__import__']:
                        self.issues.append(SecurityIssue(
                            issue_type=SecurityIssueType.EVAL_EXEC_USAGE,
                            file_path=self.file_path,
                            line_number=node.lineno,
                            severity="high",
                            description=f"AST: Dangerous function '{node.func.id}' detected",
                            code_snippet=self.lines[node.lineno - 1].strip() if node.lineno <= len(self.lines) else "",
                            suggested_fix="Use safe alternatives from safe_expression_parser",
                            can_auto_fix=True
                        ))
                
                self.generic_visit(node)
        
        visitor = SecurityVisitor(self, file_path, lines)
        visitor.visit(tree)
        self.issues.extend(visitor.issues)
    
    def _severity_score(self, severity: str) -> int:
        """Convert severity to numeric score for sorting"""
        return {"critical": 4, "high": 3, "medium": 2, "low": 1}.get(severity, 0)
    
    async def auto_fix_issues(self, dry_run: bool = True) -> int:
        """Automatically fix security issues where possible"""
        logger.info(f"Starting auto-fix process (dry_run={dry_run})")
        
        # Group issues by file
        issues_by_file = {}
        for issue in self.issues:
            if issue.can_auto_fix:
                if issue.file_path not in issues_by_file:
                    issues_by_file[issue.file_path] = []
                issues_by_file[issue.file_path].append(issue)
        
        # Fix issues file by file
        for file_path, file_issues in issues_by_file.items():
            await self._fix_file_issues(file_path, file_issues, dry_run)
        
        logger.info(f"Auto-fix complete. Fixed {self.fixed_count} issues")
        return self.fixed_count
    
    async def _fix_file_issues(self, file_path: Path, issues: List[SecurityIssue], dry_run: bool):
        """Fix issues in a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Sort issues by line number in reverse order to avoid offset issues
            issues.sort(key=lambda x: x.line_number, reverse=True)
            
            for issue in issues:
                if issue.issue_type == SecurityIssueType.HARDCODED_SECRET:
                    lines = self._fix_hardcoded_secret(lines, issue)
                    self.fixed_count += 1
                elif issue.issue_type == SecurityIssueType.EVAL_EXEC_USAGE:
                    lines = self._fix_eval_exec(lines, issue)
                    self.fixed_count += 1
                elif issue.issue_type == SecurityIssueType.WEAK_EXCEPTION_HANDLING:
                    lines = self._fix_weak_exception(lines, issue)
                    self.fixed_count += 1
            
            if not dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                logger.info(f"Fixed {len(issues)} issues in {file_path}")
            else:
                logger.info(f"Would fix {len(issues)} issues in {file_path}")
                
        except Exception as e:
            logger.error(f"Error fixing issues in {file_path}: {e}")
    
    def _fix_hardcoded_secret(self, lines: List[str], issue: SecurityIssue) -> List[str]:
        """Fix hardcoded secret by replacing with secrets manager call"""
        line_idx = issue.line_number - 1
        if line_idx < len(lines):
            line = lines[line_idx]
            
            # Extract variable name and secret key
            match = re.search(r'(\w+)\s*=\s*["\']([^"\']+)["\']', line)
            if match:
                var_name = match.group(1)
                secret_key = self._generate_secret_key(var_name)
                
                # Replace with secrets manager call
                indent = len(line) - len(line.lstrip())
                new_line = f"{' ' * indent}{var_name} = await secrets_manager.get_secret('{secret_key}')\n"
                lines[line_idx] = new_line
                
                # Add import if needed
                self._ensure_import(lines, "from infrastructure.security.secrets_manager import secrets_manager")
        
        return lines
    
    def _fix_eval_exec(self, lines: List[str], issue: SecurityIssue) -> List[str]:
        """Fix eval/exec usage with safe parser"""
        line_idx = issue.line_number - 1
        if line_idx < len(lines):
            line = lines[line_idx]
            
            # Replace eval
            if 'eval(' in line:
                line = line.replace('eval(', 'safe_eval(')
                lines[line_idx] = line
                self._ensure_import(lines, "from infrastructure.security.safe_expression_parser import safe_eval")
            
            # Replace exec
            elif 'exec(' in line:
                indent = len(line) - len(line.lstrip())
                lines[line_idx] = f"{' ' * indent}# SECURITY: exec() removed - needs manual refactoring\n"
                lines.insert(line_idx + 1, f"{' ' * indent}# Original: {line.strip()}\n")
        
        return lines
    
    def _fix_weak_exception(self, lines: List[str], issue: SecurityIssue) -> List[str]:
        """Fix weak exception handling"""
        line_idx = issue.line_number - 1
        if line_idx < len(lines):
            line = lines[line_idx]
            
            # Replace bare except
            if 'except:' in line:
                line = line.replace('except:', 'except Exception as e:')
                lines[line_idx] = line
                
                # Add logging
                indent = len(line) - len(line.lstrip()) + 4
                lines.insert(line_idx + 1, f"{' ' * indent}logger.error(f'Unexpected error: {{e}}')\n")
                self._ensure_import(lines, "import logging")
                self._ensure_import(lines, "logger = logging.getLogger(__name__)")
            
            # Replace broad except Exception
            elif 'except Exception:' in line:
                line = line.replace('except Exception:', 'except Exception as e:')
                lines[line_idx] = line
                
                # Add specific handling comment
                indent = len(line) - len(line.lstrip()) + 4
                lines.insert(line_idx + 1, f"{' ' * indent}# TODO: Use specific exception types\n")
        
        return lines
    
    def _generate_secret_key(self, var_name: str) -> str:
        """Generate a secret key name from variable name"""
        # Convert common patterns
        key_mappings = {
            'api_key': 'api_key',
            'apikey': 'api_key',
            'secret': 'secret_key',
            'password': 'password',
            'token': 'token',
        }
        
        var_lower = var_name.lower()
        for pattern, key_suffix in key_mappings.items():
            if pattern in var_lower:
                # Extract prefix if any
                prefix = var_lower.replace(pattern, '').strip('_')
                if prefix:
                    return f"{prefix}_{key_suffix}"
                return key_suffix
        
        return var_name
    
    def _ensure_import(self, lines: List[str], import_statement: str):
        """Ensure an import statement exists in the file"""
        # Check if import already exists
        for line in lines:
            if import_statement in line:
                return
        
        # Find the best place to add import
        import_idx = 0
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                import_idx = i + 1
            elif line.strip() and not line.startswith('#'):
                break
        
        lines.insert(import_idx, f"{import_statement}\n")
    
    def generate_report(self, output_file: Optional[Path] = None) -> str:
        """Generate a security audit report"""
        report = []
        report.append("=" * 80)
        report.append("SECURITY AUDIT REPORT")
        report.append("=" * 80)
        report.append(f"Audit Date: {datetime.now().isoformat()}")
        report.append(f"Project: {self.project_root}")
        report.append(f"Total Issues Found: {len(self.issues)}")
        report.append("")
        
        # Summary by severity
        severity_counts = {}
        for issue in self.issues:
            severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1
        
        report.append("Summary by Severity:")
        for severity in ["critical", "high", "medium", "low"]:
            count = severity_counts.get(severity, 0)
            report.append(f"  {severity.upper()}: {count}")
        report.append("")
        
        # Summary by type
        type_counts = {}
        for issue in self.issues:
            type_counts[issue.issue_type.value] = type_counts.get(issue.issue_type.value, 0) + 1
        
        report.append("Summary by Type:")
        for issue_type, count in type_counts.items():
            report.append(f"  {issue_type}: {count}")
        report.append("")
        
        # Detailed issues
        report.append("Detailed Issues:")
        report.append("-" * 80)
        
        for i, issue in enumerate(self.issues, 1):
            report.append(f"\nIssue #{i}")
            report.append(f"Type: {issue.issue_type.value}")
            report.append(f"Severity: {issue.severity.upper()}")
            report.append(f"File: {issue.file_path}")
            report.append(f"Line: {issue.line_number}")
            report.append(f"Description: {issue.description}")
            report.append(f"Code: {issue.code_snippet}")
            report.append(f"Fix: {issue.suggested_fix}")
            report.append(f"Auto-fixable: {'Yes' if issue.can_auto_fix else 'No'}")
            report.append("-" * 40)
        
        # Recommendations
        report.append("\nRecommendations:")
        report.append("1. Address all CRITICAL issues immediately")
        report.append("2. Use the auto-fix feature for supported issues")
        report.append("3. Implement secrets management for all API keys")
        report.append("4. Replace all eval/exec with safe alternatives")
        report.append("5. Improve exception handling throughout the codebase")
        report.append("6. Enable pre-commit hooks to prevent future issues")
        
        report_text = "\n".join(report)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report_text)
            logger.info(f"Report saved to {output_file}")
        
        return report_text


async def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Security Audit and Fix Tool")
    parser.add_argument("--project-root", type=Path, default=Path.cwd(),
                       help="Project root directory")
    parser.add_argument("--auto-fix", action="store_true",
                       help="Automatically fix issues where possible")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be fixed without making changes")
    parser.add_argument("--report", type=Path,
                       help="Output report file path")
    
    args = parser.parse_args()
    
    # Create auditor
    auditor = SecurityAuditor(args.project_root)
    
    # Run audit
    issues = await auditor.audit_project()
    
    # Generate report
    report = auditor.generate_report(args.report)
    print(report)
    
    # Auto-fix if requested
    if args.auto_fix:
        fixed = await auditor.auto_fix_issues(dry_run=args.dry_run)
        print(f"\nFixed {fixed} issues")
    
    # Exit with error code if critical issues found
    critical_count = sum(1 for issue in issues if issue.severity == "critical")
    if critical_count > 0:
        logger.error(f"Found {critical_count} critical security issues!")
        exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 